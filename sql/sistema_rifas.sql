USE sistema_rifas;

CREATE TABLE Clube (
    clube_id INT AUTO_INCREMENT PRIMARY KEY,
    clube_nome VARCHAR(150) NOT NULL
);

CREATE TABLE Responsavel (
    responsavel_id INT AUTO_INCREMENT PRIMARY KEY,
    responsavel_nome VARCHAR(150) NOT NULL,
    responsavel_contato VARCHAR(150),
    responsavel_ativo BOOLEAN DEFAULT TRUE,

    clube_id INT,

    CONSTRAINT fk_responsavel_clube
        FOREIGN KEY (clube_id)
        REFERENCES Clube(clube_id)
);

CREATE TABLE BlocoRifa (

    bloco_id INT AUTO_INCREMENT PRIMARY KEY,

    bloco_numero_inicial INT NOT NULL,
    bloco_numero_final INT NOT NULL,

    bloco_valor_rifa DECIMAL(10,2),
    bloco_quantidade_rifas INT,
    bloco_valor_total DECIMAL(10,2),

    bloco_forma_entrega ENUM('em_maos','correios'),
    bloco_data_entrega DATE,

    responsavel_id INT,

    CONSTRAINT fk_bloco_responsavel
        FOREIGN KEY (responsavel_id)
        REFERENCES Responsavel(responsavel_id)

);

CREATE TABLE Destinatario (

    destinatario_id INT AUTO_INCREMENT PRIMARY KEY,

    destinatario_nome VARCHAR(150) NOT NULL,

    destinatario_tipo ENUM(
        'fundacao',
        'clube',
        'entidade',
        'outro'
    )
);

CREATE TABLE Pagamento30 (

    pagamento30_id INT AUTO_INCREMENT PRIMARY KEY,

    bloco_id INT NOT NULL,

    pagamento30_valor DECIMAL(10,2),

    pagamento30_data DATE,

    pagamento30_pago BOOLEAN DEFAULT FALSE,

    pagamento30_comprovante VARCHAR(255),

    pagamento30_observacao TEXT,

    CONSTRAINT fk_pagamento_bloco
        FOREIGN KEY (bloco_id)
        REFERENCES BlocoRifa(bloco_id)
);

CREATE TABLE Repasse70 (

    repasse70_id INT AUTO_INCREMENT PRIMARY KEY,

    bloco_id INT NOT NULL,

    destinatario_id INT NOT NULL,

    repasse70_valor DECIMAL(10,2),

    repasse70_data DATE,

    repasse70_comprovante VARCHAR(255),

    repasse70_observacao TEXT,

    CONSTRAINT fk_repasse_bloco
        FOREIGN KEY (bloco_id)
        REFERENCES BlocoRifa(bloco_id),

    CONSTRAINT fk_repasse_destinatario
        FOREIGN KEY (destinatario_id)
        REFERENCES Destinatario(destinatario_id)

);

CREATE TABLE TransferenciaBloco (

    transferencia_id INT AUTO_INCREMENT PRIMARY KEY,

    bloco_id INT NOT NULL,

    responsavel_origem_id INT,

    responsavel_destino_id INT,

    transferencia_data DATE,

    transferencia_observacao TEXT,

    CONSTRAINT fk_transferencia_bloco
        FOREIGN KEY (bloco_id)
        REFERENCES BlocoRifa(bloco_id),

    CONSTRAINT fk_transferencia_origem
        FOREIGN KEY (responsavel_origem_id)
        REFERENCES Responsavel(responsavel_id),

    CONSTRAINT fk_transferencia_destino
        FOREIGN KEY (responsavel_destino_id)
        REFERENCES Responsavel(responsavel_id)

);

ALTER TABLE BlocoRifa ADD COLUMN bloco_observacoes TEXT;


INSERT INTO clube (clube_nome) VALUES 
('Rotary Club do Rio de Janeiro-Rocha Miranda'),
('Rotary Club do Rio de Janeiro-Tijuca'),
('Rotary Club Satélite de Angra dos Reis - Mangaratiba'),
('Rotary Club Satélite de Angra dos Reis-Paraty'),
('Rotary Club Satélite de Copacabana - Empreendedores do Amanhã'),
('Rotary Club Satélite de Duque de Caxias-Nilo Peçanha-Xerém'),
('Rotary Club Satélite de Nova Iguaçu-Centro'),
('Rotary Club Satélite de Nova Iguaçu-Luz de Escol'),
('Rotary Club Satélite de Piquete Lorena - MC2'),
('Rotary Club de Volta Redonda'),
('Rotary Club de Volta Redonda-Leste'),
('Rotary Club do Rio de Janeiro'),
('Rotary Club do Rio de Janeiro-Grajaú'),
('Rotary Club do Rio de Janeiro-Guanabara-Galeão'),
('Rotary Club do Rio de Janeiro-Ilha do Governador'),
('Rotary Club do Rio de Janeiro-Lagoa'),
('Rotary Club do Rio de Janeiro-Leblon Gávea'),
('Rotary Club do Rio de Janeiro-Maracanã'),
('Rotary Club do Rio de Janeiro-Rio Comprido'),
('Rotary Club de São José dos Campos-Oeste'),
('Rotary Club de São José dos Campos-Satélite'),
('Rotary Club de São José dos Campos-Sul'),
('Rotary Club de São Sebastião'),
('Rotary Club de Taubaté'),
('Rotary Club de Taubaté-União'),
('Rotary Club de Três Rios'),
('Rotary Club de Ubatuba'),
('Rotary Club de Valença-Centenário'),
('Rotary Club de Vassouras'),
('Rotary Club de Pindamonhangaba'),
('Rotary Club de Pinheiral'),
('Rotary Club de Piquete'),
('Rotary Club de Resende'),
('Rotary Club de Resende-Campos Eliseos'),
('Rotary Club de Rio de Janeiro-Imperial'),
('Rotary Club de Roseira'),
('Rotary Club de São João de Meriti'),
('Rotary Club de São José dos Campos-Leste'),
('Rotary Club de São José dos Campos-Norte'),
('Rotary Club de Jacareí'),
('Rotary Club de Jacareí-Flórida 3 de Abril'),
('Rotary Club de Jacareí-Oeste'),
('Rotary Club de Lorena'),
('Rotary Club de Nilópolis'),
('Rotary Club de Nova Iguaçu'),
('Rotary Club de Nova Iguaçu-Leste'),
('Rotary Club de Nova Iguaçu-Prata'),
('Rotary Club de Petrópolis'),
('Rotary Club de Petrópolis-Cidade Imperial'),
('Rotary Club de Campos do Jordão'),
('Rotary Club de Caraguatatuba'),
('Rotary Club de Caraguatatuba-Poiares'),
('Rotary Club de Cruzeiro'),
('Rotary Club de Cruzeiro-Mantiqueira'),
('Rotary Club de Cunha'),
('Rotary Club de Duque de Caxias-Jardim Primavera'),
('Rotary Club de Engenheiro Paulo de Frontin'),
('Rotary Club de Guararema'),
('Rotary Club de Ilhabela'),
('Casa da Amizade da Família Rotária da Cidade do Rio de Janeiro'),
('Rotary Club Barra da Tijuca'),
('Rotary Club de Angra dos Reis'),
('Rotary Club de Aparecida'),
('Rotary Club de Bangu'),
('Rotary Club de Barra do Piraí'),
('Rotary Club de Barra Mansa-Alvorada'),
('Rotary Club de Caçapava-Jequitibá'),
('Rotary Club de Cachoeira Paulista-Centenário'),
('Rotary Club de Campo Grande');


SET SQL_SAFE_UPDATES = 0;

SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM responsavel WHERE responsavel_nome = 'teste1';
DELETE FROM clube WHERE clube_nome = 'clubeteste';

SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;


RENAME TABLE BlocoRifa TO Bloco;

ALTER TABLE BLOCO 
RENAME COLUMN bloco_valor_rifa TO bloco_valor_numero;

ALTER TABLE BLOCO 
RENAME COLUMN bloco_quantidade_rifas TO bloco_quantidade_numeros;

CREATE TABLE Usuario (
usuario_id INT AUTO_INCREMENT PRIMARY KEY, 
usuario_nome VARCHAR(100) NOT NULL, 
usuario_email VARCHAR(120) UNIQUE NOT NULL, 
usuario_senha_hash VARCHAR(255) NOT NULL 
);

