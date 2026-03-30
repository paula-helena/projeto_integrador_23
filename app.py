import os
from datetime import datetime
from decimal import Decimal
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Bloco, Clube, Responsavel, Pagamento30, Repasse70, Destinatario, Usuario
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/listagem")
@login_required
def listagem():
    termo = request.args.get('busca', '').strip()
    status_filtro = request.args.get('status', '')
    entrega_filtro = request.args.get('entrega', '')
    
    # Pega a página atual da URL, padrão é 1
    page = request.args.get('page', 1, type=int)

    # Subquery para somar repasses de cada bloco
    subquery_repasses = db.session.query(
        Repasse70.bloco_id, 
        func.sum(Repasse70.repasse70_valor).label('total')
    ).group_by(Repasse70.bloco_id).subquery()

    from sqlalchemy.orm import joinedload
    query = Bloco.query.options(
        joinedload(Bloco.responsavel).joinedload(Responsavel.clube)
    ).join(Responsavel, isouter=True).join(Clube, isouter=True)\
     .outerjoin(Pagamento30)\
     .outerjoin(subquery_repasses, Bloco.bloco_id == subquery_repasses.c.bloco_id)

    # Use .asc() para ascendente (1, 2, 3...) ou .desc() se quisesse o inverso
    query = query.order_by(Bloco.bloco_id.asc())

    # --- FILTROS (Mantidos como estavam) ---
    if termo:
        if termo.isdigit():
            num = int(termo)
            query = query.filter(
                (Bloco.bloco_id == num) |
                ((Bloco.bloco_numero_inicial <= num) & (Bloco.bloco_numero_final >= num))
            )
        else:
            query = query.filter(
                (Responsavel.responsavel_nome.like(f'%{termo}%')) |
                (Responsavel.responsavel_contato.like(f'%{termo}%')) |
                (Clube.clube_nome.like(f'%{termo}%'))
            )

    if entrega_filtro:
        query = query.filter(Bloco.bloco_forma_entrega == entrega_filtro)

    if status_filtro == 'disponivel':
        query = query.filter(Bloco.responsavel_id == None)\
                    .filter((~Bloco.pagamento30.has()) | (Pagamento30.pagamento30_pago == False))\
                    .filter(func.coalesce(subquery_repasses.c.total, 0) == 0)
    elif status_filtro == 'reservado':
        query = query.filter(Bloco.responsavel_id != None)\
                     .filter(Pagamento30.pagamento30_pago != True)\
                     .filter(func.coalesce(subquery_repasses.c.total, 0) == 0)
    elif status_filtro == 'pago':
        query = query.filter(Pagamento30.pagamento30_pago == True)\
                     .filter(func.coalesce(subquery_repasses.c.total, 0) < 700)
    elif status_filtro == 'repassado':
        query = query.filter(subquery_repasses.c.total >= 700)

    # --- A MÁGICA DA PAGINAÇÃO ---
    # per_page=20 define quantos blocos aparecem por vez
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    blocos = pagination.items 

    return render_template("listagem.html", 
                           blocos=blocos, 
                           pagination=pagination, # Objeto para criar os botões no HTML
                           termo=termo, 
                           status_filtro=status_filtro, 
                           entrega_filtro=entrega_filtro)

@app.route("/bloco/<int:id_bloco>")
def gerenciar_bloco(id_bloco):
    bloco = Bloco.query.get_or_404(id_bloco)
    responsaveis = Responsavel.query.all()
    destinatarios = Destinatario.query.all()
    clubes = Clube.query.order_by(Clube.clube_nome).all()
    
    total_repassado = sum(float(r.repasse70_valor or 0) for r in bloco.repasses)
    atingiu_70 = total_repassado >= (float(bloco.bloco_valor_total) * 0.7)
    
    return render_template("gerenciar_bloco.html", bloco=bloco, responsaveis=responsaveis, 
                           destinatarios=destinatarios, clubes=clubes, 
                           atingiu_70=atingiu_70, total_repassado=total_repassado)

@app.route("/bloco/<int:id_bloco>/salvar", methods=['POST'])
def salvar_bloco(id_bloco):
    bloco = Bloco.query.get_or_404(id_bloco)
    
    # --- 1. RESPONSÁVEL E CLUBE ---
    nome_novo_resp = request.form.get('novo_responsavel_nome')
    if nome_novo_resp:
        id_clube_sel = request.form.get('clube_id_selecionado')
        nome_novo_clube = request.form.get('novo_responsavel_clube')
        id_clube_final = None
        
        if nome_novo_clube:
            clube = Clube.query.filter_by(clube_nome=nome_novo_clube).first()
            if not clube:
                clube = Clube(clube_nome=nome_novo_clube)
                db.session.add(clube); db.session.flush()
            id_clube_final = clube.clube_id
        elif id_clube_sel:
            id_clube_final = int(id_clube_sel)
            
        if id_clube_final:
            novo_resp = Responsavel(responsavel_nome=nome_novo_resp, 
                                   responsavel_contato=request.form.get('novo_responsavel_contato'), 
                                   clube_id=id_clube_final)
            db.session.add(novo_resp); db.session.flush()
            bloco.responsavel_id = novo_resp.responsavel_id
    else:
        resp_id = request.form.get('responsavel_id')
        bloco.responsavel_id = int(resp_id) if resp_id else None

    # --- 2. ENTREGA E OBSERVAÇÃO (Onde estava o erro de persistência) ---
    bloco.bloco_forma_entrega = request.form.get('forma_entrega') or None
    bloco.bloco_observacoes = request.form.get('bloco_observacoes') # Agora captura corretamente

    # --- 3. CUSTAS 30% ---
    if not bloco.pagamento30:
        bloco.pagamento30 = Pagamento30(bloco_id=bloco.bloco_id)
        db.session.add(bloco.pagamento30)
    
    bloco.pagamento30.pagamento30_pago = (request.form.get('pagamento_pago') == 'sim')
    data_30 = request.form.get('pagamento_data')
    if data_30:
        bloco.pagamento30.pagamento30_data = datetime.strptime(data_30, '%Y-%m-%d').date()

    f30 = request.files.get('comprovante_30')
    if f30 and f30.filename != '':
        fname = secure_filename(f"bloco_{bloco.bloco_id}_30pct_{f30.filename}")
        f30.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        bloco.pagamento30.pagamento30_comprovante = fname

    # --- 4. REPASSES 70% ---
    v70_input = request.form.get('novo_repasse_valor')
    if v70_input:
        v_novo = float(v70_input)
        total_at = sum(float(r.repasse70_valor or 0) for r in bloco.repasses)
        limite = float(bloco.bloco_valor_total) * 0.7
        
        if (total_at + v_novo) > (limite + 0.01):
            flash(f"Erro: Limite de 70% excedido (Máx: R$ {limite:.2f}).")
        else:
            nome_nova_ent = request.form.get('novo_destinatario_nome')
            id_dest_final = None
            if nome_nova_ent:
                nova_ent = Destinatario(destinatario_nome=nome_nova_ent, 
                                        destinatario_tipo=request.form.get('novo_destinatario_tipo'))
                db.session.add(nova_ent); db.session.flush()
                id_dest_final = nova_ent.destinatario_id
            else:
                d_id = request.form.get('novo_repasse_destinatario')
                id_dest_final = int(d_id) if d_id else None
            
            if id_dest_final:
                nr = Repasse70(bloco_id=bloco.bloco_id, destinatario_id=id_dest_final, 
                               repasse70_valor=v_novo, repasse70_data=datetime.utcnow().date())
                f70 = request.files.get('comprovante_70')
                if f70 and f70.filename != '':
                    fn70 = secure_filename(f"bloco_{bloco.bloco_id}_70pct_{f70.filename}")
                    f70.save(os.path.join(app.config['UPLOAD_FOLDER'], fn70))
                    nr.repasse70_comprovante = fn70
                db.session.add(nr)

    db.session.commit()
    return redirect(url_for('gerenciar_bloco', id_bloco=bloco.bloco_id))

@app.route("/bloco/<int:id_bloco>/cancelar_30")
def cancelar_30(id_bloco):
    bloco = Bloco.query.get_or_404(id_bloco)
    if bloco.pagamento30 and bloco.pagamento30.pagamento30_comprovante:
        path = os.path.join(app.config['UPLOAD_FOLDER'], bloco.pagamento30.pagamento30_comprovante)
        if os.path.exists(path): os.remove(path)
        bloco.pagamento30.pagamento30_comprovante = None
        db.session.commit()
    return redirect(url_for('gerenciar_bloco', id_bloco=id_bloco))

@app.route("/bloco/<int:id_bloco>/remover_repasse/<int:id_repasse>")
def remover_repasse(id_bloco, id_repasse):
    rep = Repasse70.query.get_or_404(id_repasse)
    if rep.repasse70_comprovante:
        path = os.path.join(app.config['UPLOAD_FOLDER'], rep.repasse70_comprovante)
        if os.path.exists(path): os.remove(path)
    db.session.delete(rep)
    db.session.commit()
    return redirect(url_for('gerenciar_bloco', id_bloco=id_bloco))

@app.route("/dashboard")
@login_required
def dashboard():
    # 1. Captura os filtros da URL
    clube_id = request.args.get('clube_id')
    data_ini = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # 2. Subquery de Repasses (Calcula a soma de repasses por bloco no MySQL)
    subquery_rep = db.session.query(
        Repasse70.bloco_id, 
        func.sum(Repasse70.repasse70_valor).label('total')
    ).group_by(Repasse70.bloco_id).subquery()

    # 3. Query Base para Contagens (Aplicando seus filtros de Clube e Data)
    query_base = db.session.query(Bloco).join(Responsavel, isouter=True)
    
    if clube_id:
        query_base = query_base.filter(Responsavel.clube_id == clube_id)
    
    if data_ini and data_fim:
        # Se filtrar por data, precisamos garantir o join com Pagamento30
        query_base = query_base.join(Pagamento30).filter(
            Pagamento30.pagamento30_data.between(data_ini, data_fim)
        )

    # --- EXECUÇÃO DAS CONTAGENS DIRETAMENTE NO BANCO ---
    
    # Total de blocos (dentro do filtro aplicado)
    total_count = query_base.count()

    # Repassados (Soma de repasses >= 700)
    repassados = query_base.join(subquery_rep, Bloco.bloco_id == subquery_rep.c.bloco_id)\
                           .filter(subquery_rep.c.total >= 700).count()

    # Pagos 30% (Tem pagamento OK e repasse < 700)
    # Usamos outerjoin para garantir que pegamos quem tem pagamento mesmo sem repasse ainda
    pagos = query_base.join(Pagamento30)\
                      .filter(Pagamento30.pagamento30_pago == True)\
                      .outerjoin(subquery_rep, Bloco.bloco_id == subquery_rep.c.bloco_id)\
                      .filter(func.coalesce(subquery_rep.c.total, 0) < 700).count()

    # Reservados (Tem responsável, mas pagamento30 não está como 'pago')
    reservados = query_base.filter(Bloco.responsavel_id != None)\
                           .filter(~Bloco.pagamento30.has(Pagamento30.pagamento30_pago == True))\
                           .count()

    # Disponíveis (O que sobrar da conta)
    disponiveis = total_count - (repassados + pagos + reservados)

    # 4. Dados para o Select de Clubes (Ordenados como você gosta)
    clubes = Clube.query.order_by(Clube.clube_nome).all()

    return render_template("dashboard.html", 
                           labels_status=['Disponível', 'Reservado', 'Pago 30%', 'Repassado'],
                           data_status=[disponiveis, reservados, pagos, repassados],
                           clubes=clubes,
                           clube_sel=int(clube_id) if clube_id else None)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Usuario, int(user_id))
    except:
        return None

# --- ROTA RAIZ: LOGIN ---
@app.route("/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listagem'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        print(f"--- Tentando login para: {email} ---") # DEBUG
        
        try:
            user = Usuario.query.filter_by(usuario_email=email).first()
            print(f"--- Busca no banco finalizada. Usuário encontrado? {user is not None} ---") # DEBUG
            
            if user and user.checar_senha(senha):
                print("--- Senha correta. Iniciando sessão... ---") # DEBUG
                login_user(user)
                print("--- Redirecionando para listagem... ---") # DEBUG
                return redirect(url_for('listagem'))
            
            print("--- Falha: E-mail ou senha incorretos ---") # DEBUG
            flash("E-mail ou senha incorretos.")
        except Exception as e:
            print(f"--- ERRO NO LOGIN: {e} ---") # DEBUG
            flash("Erro de conexão com o servidor.")
            
    return render_template("index.html")

# --- ROTA DE REGISTRO (PÚBLICA) ---
@app.route("/registrar", methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if Usuario.query.filter_by(usuario_email=email).first():
            flash("E-mail já cadastrado.")
        else:
            novo_u = Usuario(usuario_nome=nome, usuario_email=email)
            novo_u.set_senha(senha)
            db.session.add(novo_u)
            db.session.commit()
            flash("Conta criada! Faça login.")
            return redirect(url_for('login'))
    return render_template("registrar.html")

# --- ROTA DE LOGOUT ---
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))








if __name__ == "__main__":
    app.run(debug=True)