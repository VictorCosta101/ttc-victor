import os
import json
from pathlib import Path

import fitz
from db import get_catalogacao_db
from models import CatalogacaoErro, Julgamento
from sqlalchemy.orm import Session
from gpt_client import GPTClient
import logging
from dotenv import load_dotenv


CACHE_DIR = Path("cache")

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API OpenAI (pode ser diferente do agente varredor)
API_KEY = os.getenv("LLM_JUIZ_API_KEY2")
gpt_client = GPTClient(api_key=API_KEY)

def julgar_erros(db: Session):
    """
    Consulta erros não julgados, reavalia com LLM e registra julgamentos.
    Acessa os PDFs originais no diretório de cache para análise.
    """
    print("api juiz key")
    print(API_KEY)
    try:
        # 1. Busca erros não julgados
        erros_nao_julgados = db.query(CatalogacaoErro).filter(
            CatalogacaoErro.julgado == False
        ).all()

        if not erros_nao_julgados:
            logger.info("Nenhum erro pendente para julgamento")
            return

        logger.info(f"Iniciando julgamento de {len(erros_nao_julgados)} erros")

        # 2. Processa cada erro
        for erro in erros_nao_julgados:
            try:
                # 2.1 Verifica se o PDF existe no cache
                pdf_path = CACHE_DIR / f"{erro.reference}.pdf"
                if not pdf_path.exists():
                    logger.warning(f"PDF não encontrado para {erro.reference}")
                    continue

                # 2.2 Extrai texto do PDF
                with open(pdf_path, "rb") as f:
                    pdf_document = fitz.open(stream=f.read())
                    texto_carta = ""
                    for pagina in pdf_document:
                        texto_carta += pagina.get_text("text") + "\n"

                # 2.3 Prepara prompt para o Juiz (GPT)
                prompt = f"""
                Reavalie este possível erro de catalogação:

                **Dados do Erro**:
                - Reference: {erro.reference}
                - Campo: {erro.campo}
                - Valor Catalogado: {erro.conteudo_errado}
                - Sugestão de Correção: {erro.resposta_correta}
                - Motivo: {erro.motivo}

                **Conteúdo Original da Carta**:
                {texto_carta}...  # Limita o tamanho para o prompt

                **Sua Tarefa**:
                1. Verifique se a correção sugerida está correta
                2. Caso não esteja, indique o valor correto
                3. Atribua um grau de certeza (0.0 a 1.0)

                **Formato de Resposta**:
                {{
                    "analise": "Explicação detalhada",
                    "valor_correto_final": "valor corrigido ou confirmado",
                    "grau_certeza": 0.95,
                    "correcao_necessaria": true/false
                }}
                """

                # 2.4 Chama o GPT para julgamento
                response = gpt_client.generate_content(
                    assistant_prompt="Você é um especialista em documentos históricos da América portuguesa.",
                    user_prompt=prompt
                )
                print("Resposta original do llm")
                print(response)

                resposta_gpt = response.get("response", "{}").strip("```json").strip("```").strip()
                resultado = json.loads(resposta_gpt)
                print("resultado do juiz")
                print(resultado)

                # 2.5 Registra o julgamento
                julgamento = Julgamento(
                    erro_id=erro.id,
                    reference=erro.reference,
                    resultado_analise=resultado["analise"],
                    resposta_correta=resultado["valor_correto_final"],
                    grau_certeza=resultado.get("grau_certeza", 0.9)
                )
                db.add(julgamento)

                # 2.6 Marca o erro como julgado
                erro.julgado = True
                erro.resposta_correta = resultado["valor_correto_final"]
                db.commit()

                logger.info(f"Erro {erro.id} julgado com sucesso")

            except Exception as e:
                logger.error(f"Erro ao processar {erro.reference}: {str(e)}")
                db.rollback()

        logger.info("Processo de julgamento concluído")

    except Exception as e:
        logger.error(f"Falha crítica no julgamento: {str(e)}")
        raise