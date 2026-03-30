import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Busca a URL do .env; se não achar, usa uma string vazia (evita erro de None)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "use_pure": True,
            "connect_timeout": 5
        },
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 0
    }
    
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_COOKIE_NAME = 'projeto_univesp_session'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    
    # Uploads
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'comprovantes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


