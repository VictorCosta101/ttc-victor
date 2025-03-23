from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from data_comparator import analyze_data
from db import get_db, Base, engine
from models import CatalogacaoErro
import fitz  # PyMuPDF
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def detectar_reference(texto: str) -> str:
    """
    Extrai o reference da primeira linha do texto.
    """
    primeira_linha = texto.split("\n")[0].strip()
    return primeira_linha

@app.post("/verificar/")
async def verificar_carta(
    file: UploadFile = File(...),  # Recebe o arquivo PDF
    db: Session = Depends(get_db)  # Sessão do banco de dados
):
    try:
        # Lê o conteúdo do arquivo PDF
        pdf_content = await file.read()

        # Converte o PDF para texto
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        carta_texto = ""
        for pagina in pdf_document:
            carta_texto += pagina.get_text("text") + "\n"

        # Detecta o reference da primeira linha
        reference = detectar_reference(carta_texto)
        if not reference:
            raise HTTPException(status_code=400, detail="Reference não detectado no PDF.")

        logger.info(f"Processando carta com reference: {reference}")

        # Chama a função de análise
        resultado = analyze_data(reference, carta_texto, db)

        if not resultado:
            raise HTTPException(status_code=500, detail="Erro ao processar a carta.")

        return resultado

    except Exception as e:
        logger.exception("Erro ao processar carta")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")