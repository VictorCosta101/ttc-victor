import requests
import json
from gpt_client import GPTClient
from db import get_db
from models import CatalogacaoErro
from sqlalchemy.orm import Session
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API OpenAI
API_KEY = "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"
gpt_client = GPTClient(api_key=API_KEY)

# Verifica se já temos erros armazenados para essa carta
def verificar_carta_analisada(reference: str, db: Session):
    return db.query(CatalogacaoErro).filter(CatalogacaoErro.reference == reference).first()

# Busca dados da API
def fetch_data_from_api(reference: str) -> dict:
    url = (
        f"http://plataformasilb.cchla.ufrn.br/api/get/tabela?"
        f"reference={reference}"
        f"&captaincy_name=Pernambuco"
        f"&owner="
        f"&date_request="
        f"&date_request_fim="
        f"&dateConcession="
        f"&dateConcession_fim="
        f"&location="
        f"&marcos="
        f"&typeArea=1"
        f"&landrecord_comments="
        f"&comments="
        f"&limitant="
        f"&comments_justification="
        f"&sources="
        f"&comments_deferment="
        f"&comments_demands="
        )
    
    logger.info(f"Buscando dados na URL: {url}")  

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Resposta da API para {reference}: {data}")  

        return data[0] if isinstance(data, list) and data else data if isinstance(data, dict) else None

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar dados da API para {reference}: {e}")
        return None

# Envia todos os dados para análise do GPT
def analyze_data(reference: str, carta_texto: str, db: Session):
    logger.info(f"Recebendo request para referência {reference}")

    #  Busca os dados da API
    api_data = fetch_data_from_api(reference)
    if not api_data:
        logger.error(f" Erro ao buscar dados da API para {reference}")
        return {"error": "Erro ao buscar dados da API"}

    # Criando um prompt consolidado para o GPT
    prompt = f"""
    Você é um especialista em análise de documentos históricos. Compare os seguintes dados extraídos de um documento (API) com o conteúdo original da carta e identifique quaisquer erros.

    **Dados extraídos da API**:
    {json.dumps(api_data, indent=2)}

    **Conteúdo original da carta**:
    {carta_texto}

     Retorne apenas os campos incorretos no seguinte formato JSON:
    {{
        "erros_identificados": [
            {{
                "campo": "nome_do_campo",
                "valor_incorreto": "valor_extraído",
                "motivo": "explicação do erro"
            }},
            ...
        ]
    }}
    """

    try:
        response = gpt_client.generate_content(
            assistant_prompt="Você é um especialista em documentos históricos.",
            user_prompt=prompt
        )
        
        resposta_gpt = response.get("response", "{}").strip("```json").strip("```").strip()
        resultado = json.loads(resposta_gpt)  
        print("response: " + str(resultado))
       

    except Exception as e:
        logger.error(f"Erro na chamada do GPT para {reference}: {e}")
        return {"error": "Erro ao processar dados com GPT"}

    erros_identificados = resultado.get("erros_identificados", [])

    # Salvar erros no banco de dados
    for erro in erros_identificados:
        novo_erro = CatalogacaoErro(
            reference=reference, 
            campo=erro["campo"], 
            conteudo_errado=erro["valor_incorreto"],
            motivo=erro["motivo"]
        )
        db.add(novo_erro)

    db.commit()

    logger.info(f"Processamento concluído para referência {reference}")
    return {"message": "Verificação concluída!", "erros_identificados": erros_identificados}
