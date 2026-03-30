SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://laisguer_univespadmin:univespadmin@laisguerra.com.br/laisguer_projeto_integrador_23"

# Esta é a configuração que força o modo "Pure Python" (para não gerar erro de conexão do MySQL Connector)
SQLALCHEMY_ENGINE_OPTIONS = {
    "connect_args": {
        "use_pure": True,
        "connect_timeout": 10
    },
    "pool_pre_ping": True,
    "pool_recycle": 280
}

SQLALCHEMY_TRACK_MODIFICATIONS = False
