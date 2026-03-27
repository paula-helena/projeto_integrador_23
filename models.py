from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Clube(db.Model):
    __tablename__ = 'Clube'
    clube_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clube_nome = db.Column(db.String(150), nullable=False)
    
    # Relação com Responsável
    responsaveis = db.relationship('Responsavel', backref='clube', lazy=True)

class Responsavel(db.Model):
    __tablename__ = 'Responsavel'
    responsavel_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    responsavel_nome = db.Column(db.String(150), nullable=False)
    responsavel_contato = db.Column(db.String(150))
    responsavel_ativo = db.Column(db.Boolean, default=True)
    clube_id = db.Column(db.Integer, db.ForeignKey('Clube.clube_id'))

class Bloco(db.Model):
    __tablename__ = 'Bloco'
    bloco_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bloco_numero_inicial = db.Column(db.Integer, nullable=False)
    bloco_numero_final = db.Column(db.Integer, nullable=False)
    
    bloco_valor_numero = db.Column(db.Numeric(10, 2))
    bloco_quantidade_numeros = db.Column(db.Integer)
    bloco_valor_total = db.Column(db.Numeric(10, 2))
    
    bloco_forma_entrega = db.Column(db.Enum('em_maos', 'correios'))
    bloco_data_entrega = db.Column(db.Date)
    bloco_observacoes = db.Column(db.Text, nullable=True)

    responsavel_id = db.Column(db.Integer, db.ForeignKey('Responsavel.responsavel_id'))

    # --- DEFINIÇÃO DOS RELACIONAMENTOS (O segredo para o erro parar) ---
    # Alterado para 'responsavel' para bater com o que usamos no app.py e no HTML
    responsavel = db.relationship('Responsavel', backref='blocos', lazy=True)
    
    pagamento30 = db.relationship('Pagamento30', backref='bloco', uselist=False, lazy=True)
    repasses = db.relationship('Repasse70', backref='bloco', lazy=True)
    transferencias = db.relationship('TransferenciaBloco', backref='bloco', lazy=True)

class Destinatario(db.Model):
    __tablename__ = 'Destinatario'
    destinatario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destinatario_nome = db.Column(db.String(150), nullable=False)
    destinatario_tipo = db.Column(db.Enum('fundacao', 'clube', 'entidade', 'outro'))

    repasses = db.relationship('Repasse70', backref='destinatario', lazy=True)

class Pagamento30(db.Model):
    __tablename__ = 'Pagamento30'
    pagamento30_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey('Bloco.bloco_id'), nullable=False)
    
    pagamento30_valor = db.Column(db.Numeric(10, 2))
    pagamento30_data = db.Column(db.Date)
    pagamento30_pago = db.Column(db.Boolean, default=False)
    pagamento30_comprovante = db.Column(db.String(255))
    pagamento30_observacao = db.Column(db.Text)

class Repasse70(db.Model):
    __tablename__ = 'Repasse70'
    repasse70_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey('Bloco.bloco_id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('Destinatario.destinatario_id'), nullable=False)
    
    repasse70_valor = db.Column(db.Numeric(10, 2))
    repasse70_data = db.Column(db.Date)
    repasse70_comprovante = db.Column(db.String(255))
    repasse70_observacao = db.Column(db.Text)

class TransferenciaBloco(db.Model):
    __tablename__ = 'TransferenciaBloco'
    transferencia_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey('Bloco.bloco_id'), nullable=False)
    responsavel_origem_id = db.Column(db.Integer, db.ForeignKey('Responsavel.responsavel_id'))
    responsavel_destino_id = db.Column(db.Integer, db.ForeignKey('Responsavel.responsavel_id'))
    
    transferencia_data = db.Column(db.Date)
    transferencia_observacao = db.Column(db.Text)
    
class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuario'
    usuario_id = db.Column(db.Integer, primary_key=True)
    usuario_nome = db.Column(db.String(100), nullable=False)
    usuario_email = db.Column(db.String(120), unique=True, nullable=False)
    usuario_senha_hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.usuario_id)

    def set_senha(self, senha):
        self.usuario_senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.usuario_senha_hash, senha)