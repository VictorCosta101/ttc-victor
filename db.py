from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Configuração SILB (MariaDB) - Apenas para consulta de arquivos
SILB_DATABASE_URL = os.getenv("SILB_DATABASE_URL")
silb_engine = create_engine(
    SILB_DATABASE_URL,
    pool_recycle=3600,
    connect_args={"connect_timeout": 5}  # Timeout reduzido para consultas rápidas
)

# Configuração Catalogação (PostgreSQL) - Para operações principais
CATALOGACAO_DATABASE_URL = os.getenv("CATALOGACAO_DATABASE_URL")
catalogacao_engine = create_engine(CATALOGACAO_DATABASE_URL)

# Sessões
SilbSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=silb_engine,
    expire_on_commit=False  # Importante para consultas rápidas
)

CatalogacaoSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=catalogacao_engine
)

Base = declarative_base()

# Dependências FastAPI
def get_silb_db():
    """Fornece conexão rápida e descartável apenas para consulta de arquivos"""
    db = SilbSessionLocal()
    try:
        yield db
    finally:
        db.close()  # Fecha imediatamente após uso

def get_catalogacao_db():
    """Conexão principal para operações de catalogação"""
    db = CatalogacaoSessionLocal()
    try:
        yield db
    finally:
        db.close()