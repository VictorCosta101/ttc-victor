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

def fetch_data_from_silb(reference: str) -> dict:
    """
    Busca dados da API do SILB com base no reference.
    """

    # Formata o reference
    reference_formatado = formatar_reference(reference)
    
    url = (
        f"http://plataformasilb.cchla.ufrn.br/api/get/tabela?"
        f"reference={reference_formatado}"
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
    print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[0] if isinstance(data, list) and data else data if isinstance(data, dict) else None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar dados da API do SILB para {reference}: {e}")
        return None

def analyze_data(reference: str, carta_texto: str, db: Session):
    """
    Compara os dados da carta com os dados da API do SILB usando GPT.
    """
    logger.info(f"Processando reference: {reference}")

    # Busca os dados da API do SILB
    api_data = fetch_data_from_silb(reference)
    if not api_data:
        return {"error": "Erro ao buscar dados da API do SILB"}

    # Cria o prompt para o GPT
    prompt = f"""
   Você é um especialista em análise de documentos históricos. Compare os dados extraídos de um documento (API) com o conteúdo original da carta e identifique quaisquer erros. 
   Considere sinônimos, variações de escrita e equivalências numéricas ao fazer a comparação.

    **Dados extraídos da API**:
    {json.dumps(api_data, indent=2)}

    **Conteúdo original da carta**:
    {carta_texto}

    **Regras para comparação**:
    1. Valores numéricos escritos por extenso (ex: "quatro léguas") devem ser considerados equivalentes aos seus correspondentes em algarismos (ex: "4.00").
    2. Sinônimos e variações de escrita (ex: "terras" vs. "propriedades") devem ser considerados equivalentes, a menos que haja uma diferença clara de significado.
    3. Ignore diferenças de pontuação, maiúsculas/minúsculas e espaçamento, a menos que alterem o significado.
    4. Apenas identifique erros quando houver uma discrepância clara e significativa entre os dados.

    **Formato de resposta**:
    Retorne apenas os campos incorretos no seguinte formato JSON:
    {{
        "erros_identificados": [
            {{
                "campo": "nome_do_campo",
                "valor_incorreto": "valor_extraído",
                "motivo": "explicação_do_erro"
            }}
        ]
    }}
    """

    try:
        # Chama o GPT para análise
        response = gpt_client.generate_content(
            assistant_prompt="Você é um especialista em documentos históricos.",
            user_prompt=prompt
        )
        resposta_gpt = response.get("response", "{}").strip("```json").strip("```").strip()
        resultado = json.loads(resposta_gpt)

        # Salva os erros no banco de dados
        for erro in resultado.get("erros_identificados", []):
            novo_erro = CatalogacaoErro(
                reference=reference,
                campo=erro["campo"],
                conteudo_errado=erro["valor_incorreto"],
                motivo=erro["motivo"]
            )
            db.add(novo_erro)
        db.commit()

        return {"message": "Verificação concluída!", "erros_identificados": resultado.get("erros_identificados", [])}

    except Exception as e:
        logger.error(f"Erro ao processar dados com GPT: {e}")
        return {"error": "Erro ao processar dados com GPT"}
    

def formatar_reference(reference: str) -> str:
    """
    Formata o reference para o padrão esperado pela API do SILB.
    Remove espaços e garante que o formato seja consistente (ex: PE-AL0001).

    Args:
        reference (str): O reference extraído do PDF.

    Returns:
        str: O reference formatado.
    """
    # Remove espaços em branco
    reference = reference.replace(" ", "")

    # Verifica se o reference está no formato esperado (ex: PE-AL0001)
    if not reference.replace("-", "").isalnum():
        raise ValueError(f"Reference inválido: {reference}. O formato esperado é 'PE-AL0001'.")

    return reference    