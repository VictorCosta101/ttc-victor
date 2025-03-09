from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Configuração do banco de dados
DATABASE_URL = "postgresql://user:password@localhost:5432/catalogacao"

# Criando o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Criando a sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM
Base = declarative_base()

# Dependência para injetar sessão do banco no FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
