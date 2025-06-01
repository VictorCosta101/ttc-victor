from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class File(Base):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, index=True)
    file = Column(String(512))  # Ajustado para permitir nulo e tamanho máximo
    
    requests = relationship("FileRequests", back_populates="file")

class FileRequests(Base):
    __tablename__ = "file_requests"

    file_id = Column(Integer, ForeignKey("file.id"), primary_key=True)
    request_id = Column(Integer, ForeignKey("request.id"), primary_key=True)

    file = relationship("File", back_populates="requests")
    request = relationship("Request", back_populates="files")

class Request(Base):
    __tablename__ = "request"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(11), unique=True)
    oldReference = Column(String(11))
    date_request = Column(Date)
    dateConcession = Column(Date)
    same_measure = Column(Boolean)
    request_type = Column(Integer)  # int(10) unsigned
    link = Column(String(512))
    comments = Column(Text)  # mediumtext
    privileged_observations = Column(Text)  # mediumtext
    show = Column(Boolean, default=True)
    landRecord_id = Column(Integer)  # int(10) unsigned
    deferment_id = Column(Integer)  # int(10) unsigned
    comments_demands = Column(Text)
    owner_count = Column(Integer)
    comments_justification = Column(Text)
    petition_type = Column(Integer)  # tinyint(1)

    files = relationship("FileRequests", back_populates="request")

# Modelos para o banco 'catalogacao' (mantidos como estão)
class CatalogacaoErro(Base):
    __tablename__ = "catalogacao_erros"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, nullable=False)
    campo = Column(String, nullable=False)
    conteudo_errado = Column(Text, nullable=False)
    data_registro = Column(DateTime, default=datetime.utcnow)
    motivo = Column(String, nullable=False)
    julgado = Column(Boolean, default=False)
    resposta_correta = Column(Text)
    prompt_name = Column(String(50),nullable=True)
    erro_positivo = Column(Boolean, nullable=True)

class Julgamento(Base):
    __tablename__ = "julgamentos"

    id = Column(Integer, primary_key=True, index=True)
    erro_id = Column(Integer, ForeignKey("catalogacao_erros.id"), nullable=False)
    reference = Column(String, nullable=False)
    resultado_analise = Column(Text, nullable=False)
    resposta_correta = Column(Text, nullable=False)
    grau_certeza = Column(Float)
    data_julgamento = Column(DateTime, default=datetime.utcnow)
    correcao = Column(Boolean, default=False)