from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CatalogacaoErro(Base):
    __tablename__ = "catalogacao_erros"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, nullable=False)
    campo = Column(String, nullable=False)
    conteudo_errado = Column(Text, nullable=False)
    data_registro = Column(DateTime, default=datetime.utcnow)
    motivo = Column(String, nullable=False)
