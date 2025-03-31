import os
import requests
from db import get_silb_db
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from sqlalchemy import text
import time as time_module 

# Carrega as variáveis do arquivo .env
load_dotenv()


# Configuração da API
API_BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{API_BASE_URL}/verificar/"
JULGAR_URL = f"{API_BASE_URL}/julgar/"

def buscar_references_e_arquivos(silb_db: Session):
    """
    Busca os 10 primeiros references e nomes dos arquivos no banco SILB.
    """
    query = text("""
    SELECT r.reference, f.file 
    FROM Request r
    JOIN FileRequests fr ON fr.request_id = r.id
    JOIN File f ON f.id = fr.file_id
    LIMIT 10;
    """)
    result = silb_db.execute(query)
    return result.fetchall()

def enviar_para_api(reference: str, filename: str):
    """
    Envia o arquivo PDF para a API.
    Modificado para buscar os PDFs no diretório original do SILB (/uploads)
    """
    # Caminho onde o SILB original armazena os PDFs
    caminho_silb = "./uploads"  # Ajuste para o caminho real
    filepath = os.path.join(caminho_silb, filename)
    
    if not os.path.exists(filepath):
        print(f"Arquivo não encontrado no SILB: {filepath}")
        return

    with open(filepath, "rb") as file:
        files = {"file": (filename, file, "application/pdf")}
        response = requests.post(API_URL, files=files, params={"reference": reference})
        
        if response.status_code == 200:
            print(f"Arquivo {filename} processado! Reference: {reference}")
        else:
            print(f"Erro ao processar {filename}: {response.text}")

def executar_julgamento():
    """
    Aciona o endpoint de julgamento para analisar os erros encontrados.
    """
    try:
        print("\n Iniciando processo de julgamento dos erros...")
        start_time = 0
        
        response = requests.post(JULGAR_URL, timeout=120)
        
        if response.status_code == 200:
            elapsed = 1 - start_time
            print(f" Julgamento concluído em {elapsed:.2f}s!")
            return response.json()
        print(f" Falha no julgamento: {response.text}")
        return None
    except requests.exceptions.Timeout:
        print(" Tempo excedido no julgamento (o processo pode estar em andamento)")
        return None
    except Exception as e:
        print(f" Erro inesperado no julgamento: {str(e)}")
        return None

def main():
    fluxo = 2
    if(fluxo == 1):
        # Obtém uma sessão do banco SILB
        silb_db = next(get_silb_db())

        # Busca os references e nomes dos arquivos
        references_e_arquivos = buscar_references_e_arquivos(silb_db)

        # Envia cada arquivo para a API
        for reference, filename in references_e_arquivos:
         enviar_para_api(reference, filename)
    else:
        executar_julgamento()

if __name__ == "__main__":
    main()