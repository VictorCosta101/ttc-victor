import logging
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data_comparator import analyze_data
from db import get_db

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class CartaInput(BaseModel):
    reference: str
    carta_texto: str

@app.post("/verificar/")
def verificar_carta(input_data: CartaInput, db: Session = Depends(get_db)):
    logger.info(f" Recebendo request para referência {input_data.reference}")

    try:
        resultado = analyze_data(input_data.reference, input_data.carta_texto, db)

        if not resultado:
            logger.error(" analyze_data retornou None")
            return {"error": "Erro interno: analyze_data falhou"}

        logger.info(f" analyze_data processou referência {input_data.reference}")
        return resultado
    
    except Exception as e:
        logger.exception(" Erro ao processar carta")
        return {"error": f"Erro interno: {str(e)}"}
