from datetime import time
import os
from pathlib import Path
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
EXTRAIR_DADOS_URL = f"{API_BASE_URL}/extrair_dados/"
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
    LIMIT 30;
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

def testar_extrair_dados_api(filename: str):
    """
    Testa a extração de dados enviando um PDF do cache para a API
    """
    # Configura caminhos
    cache_path = Path("cache") / filename
    
    if not cache_path.exists():
        print(f"Arquivo não encontrado no cache: {cache_path}")
        return None

    try:
        print(f"\nEnviando arquivo {filename} para extração de dados...")
        
        # Envia o arquivo para a API
        with open(cache_path, 'rb') as file:
            files = {'file': (filename, file, 'application/pdf')}
            #start_time = time.time()
            response = requests.post(EXTRAIR_DADOS_URL, files=files)
            #elapsed_time = time.time() - start_time

        if response.status_code != 200:
            print(f"Erro na API: {response.status_code} - {response.text}")
            return None

        resultado = response.json()
        
        # Exibe os resultados formatados
        print("\nRESULTADO DA EXTRAÇÃO:")
        print("=" * 60)
        print(f"Status: {resultado.get('status', 'N/A')}")
        print(f"Reference: {resultado.get('reference', 'Não identificado')}")
       # print(f"Tempo de processamento: {elapsed_time:.2f}s")
        print("\nDADOS CATALOGADOS:")
        
        dados = resultado.get('dados_extraidos', {})
        for campo, valor in dados.items():
            if valor:  # Mostra apenas campos com valores
                print(f"{campo}: {valor}")
        
        print("\nRESUMO:")
        campos_preenchidos = len([v for v in dados.values() if v])
        print(f"Total de campos identificados: {campos_preenchidos}/{len(dados)}")
        
        return resultado

    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")
        return None


def main():
    fluxo = 1
    if(fluxo == 1):
        # Obtém uma sessão do banco SILB
        silb_db = next(get_silb_db())

        # Busca os references e nomes dos arquivos
        references_e_arquivos = buscar_references_e_arquivos(silb_db)

        # Envia cada arquivo para a API
        count = 0
        for reference, filename in references_e_arquivos:
         enviar_para_api(reference, filename)
         count += 1
         print(f"Total de arquivos processados: {count}")
    elif fluxo == 3:
        # Novo fluxo: teste de API com arquivo do cache
        import sys
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            
            # Verifica se o arquivo existe no cache
            if not (Path("cache") / filename).exists():
                print(f"Arquivo {filename} não encontrado no diretório cache/")
                print("Certifique-se de que o arquivo PDF está na pasta cache/")
                return
            
            testar_extrair_dados_api(filename)
        else:
            print("Uso: python teste.py <nome_do_arquivo_no_cache>")
            print("Exemplo: python teste.py PE-AL0001.pdf")
            print("\nArquivos disponíveis no cache:")
            for f in Path("cache").glob("*.pdf"):
                print(f" - {f.name}")
    
if __name__ == "__main__":
    main()