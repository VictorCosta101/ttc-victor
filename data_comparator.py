import os
import json
from typing import Dict, Optional
import requests
from gpt_client import GPTClient
from db import get_catalogacao_db, get_silb_db
from models import CatalogacaoErro, Request, File, FileRequests
from sqlalchemy.orm import Session
import logging
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações da API
SILB_API_BASE_URL =  (
        f"http://plataformasilb.cchla.ufrn.br/api/get/tabela?")
GPT_CLIENT = GPTClient(api_key=os.getenv("LLM_VARREDOR_API_KEY"))

class SILBDataFetcher:
    @staticmethod
    def fetch_catalog_data(reference: str) -> Optional[Dict]:
        """Busca dados catalogados na API do SILB"""
        url = (
        f"http://plataformasilb.cchla.ufrn.br/api/get/tabela?"
        f"reference={reference}"
        f"&captaincy_name="
        f"&owner="
        f"&date_request="
        f"&date_request_fim="
        f"&dateConcession="
        f"&dateConcession_fim="
        f"&location="
        f"&marcos="
        f"&typeArea="
        f"&landrecord_comments="
        f"&comments="
        f"&limitant="
        f"&comments_justification="
        f"&sources="
        f"&comments_deferment="
        f"&comments_demands="
        )
        try:
            params = {
                "reference": reference,
                # Outros parâmetros podem ser adicionados conforme necessidade
            }
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # A API retorna uma lista, pegamos o primeiro item
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar dados do SILB para {reference}: {str(e)}")
            return None

class DataParser:
    """Responsável por processar e traduzir os dados da API do SILB"""
    
    FIELD_MAPPING = {
        "request_petition_type": "Tipo de petição",
        "request_old_reference": "Referência da antiga plataforma SILB",
        "owner_name": "Nome",
        "request_same_measure":"Solicitaram repartição da terra em mesma medida",
        "captaincy_name" : "Capitania onde mora",
        "landhistory_history" : "Histórico da terra",
        "requesttype_type" : "Tipo de petição",
        "request_date_request": "Data da petição",
        "dateConcession": "Data da concessão",
        "landrecord_comments": "Observações da sesmaria",
        "landrecord_location": "Localidade",
        "landrecord_marcos" : "Marcos Geográficos",
        "landrecord_river" : "Ribeira",
        "landrecord_limitant" : "Confrontantes",
        "landrecord_hectare_area": "Área",
        "landrecord_width_area": "Largura",
        "landrecord_height_area": "Comprimento",
        "request_comments" : "Observações da petição",
        "justifications" : "Justificativas",
        "demands": "Exigências do Deferimento",
        "countOwners" : "Total de sesmeiros que solicitaram a sesmaria",
        "comments":"Observações da petição",
        "limitant": "Confrontantes",
        "comments_justification": "Observações das Justificativas",
        "soucers":"Fonte",
        "comments_deferment":"Observações do deferimento e da concessão" ,
        "comments_demands":"Observações das exigências"  ,
        "defermentFavorable": "Despacho favorável",
        "defermentForm": "Forma de Deferimento",
        "providerName": "Nome do provedor",
        "procuradorName": "Nome do procurador"

        
    }
    
    ESSENTIAL_FIELDS = [
        "tipo_peticao",
        "referencia_antiga",
        "nome_proprietario",
        "mesma_medida",
        "capitania",
        "historico_terra",
        "data_peticao",
        "data_concessao",
        "observacoes_sesmaria",
        "localidade",
        "marcos_geograficos",
        "ribeira",
        "confrontantes",
        "area_hectares",
        "largura",
        "comprimento",
        "observacoes_peticao",
        "justificativas",
        "exigencias_deferimento",
        "total_sesmeiros",
        "observacoes_gerais",
        "observacoes_justificativas",
        "fontes",
        "observacoes_deferimento",
        "observacoes_exigencias",
        "despacho_favoravel",
        "forma_deferimento",
        "nome_provedor",
        "nome_procurador"
    ]

    
    @classmethod
    def parse_and_filter(cls, api_data: Dict) -> Dict:
        """Filtra e traduz os campos relevantes para análise"""
        if not api_data:
            return {}
            
        parsed_data = {}
        
        # Primeiro verifica todas as chaves disponíveis no response
        available_keys = set(api_data.keys())
        logger.debug(f"Chaves disponíveis na resposta: {available_keys}")
        
        for original_field, translated_field in cls.FIELD_MAPPING.items():
            # Verifica se a chave existe no response (case insensitive)
            matching_keys = [k for k in available_keys if k.lower() == original_field.lower()]
            
            if matching_keys:
                actual_key = matching_keys[0]
                value = api_data[actual_key]
                
                # Trata valores "NC" como vazios
                if value and str(value).strip().upper() != "NC":
                    parsed_data[translated_field] = value
        
        # Adiciona o reference se não estiver presente
        if 'reference' in api_data and 'referencia' not in parsed_data:
            parsed_data['referencia'] = api_data['reference']
            
        logger.debug(f"Dados parseados: {parsed_data}")
        return parsed_data

class HistoricalDocumentAnalyzer:
    """Coordena todo o processo de análise documental"""
    
    @staticmethod
    def build_analysis_prompt(reference: str, 
                            catalog_data: Dict, 
                            document_text: str) -> str:
        """Constroi o prompt para análise histórica"""
        return f"""
        Você é um especialista em documentos históricos do período colonial brasileiro.
        Analise a carta de sesmaria abaixo comparando com os dados catalogados:

        **Dados Catalogados**:
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}

        **Conteúdo Original da Carta (Reference: {reference})**:
        {document_text[:10000]}... [texto truncado para economia]

        **Sua Tarefa**:
        1. Identifique discrepâncias entre o conteúdo e os dados catalogados
        2. Para cada erro encontrado, forneça:
           - Campo com erro 
           - Valor catalogado incorreto
           - Valor correto baseado no texto
           - Justificativa histórica para a correção
    

        **Formato de Resposta JSON**:
        {{
            "erros": [
                {{
                    "campo": "nome_do_campo",
                    "valor_incorreto": "valor_atual",
                    "valor_correto": "valor_sugerido",
                    "motivo": "explicacao_historica",
                }}
            ],
            "analise_geral": "Resumo breve da análise"
        }}
        """

    @classmethod
    def analyze_document(cls,
                       reference: str,
                       document_text: str,
                       db_session: Session) -> Dict:
        """Executa o pipeline completo de análise"""
        try:
            # 1. Busca dados catalogados
            raw_data = SILBDataFetcher.fetch_catalog_data(reference)
            print("===============================")
            print("Dados encontrados")
            
            if not raw_data:
                raise ValueError(f"Dados não encontrados para {reference}")
            
            # 2. Parseia e filtra os dados
            print(raw_data)
            catalog_data = DataParser.parse_and_filter(raw_data)
            if not catalog_data:
                raise ValueError("Nenhum dado relevante encontrado para análise")
            
            # 3. Prepara e envia para análise do GPT
            prompt = cls.build_analysis_prompt(reference, catalog_data, document_text)
            
            response = GPT_CLIENT.generate_content(
                assistant_prompt="Você é um historiador especializado em documentos coloniais.",
                user_prompt=prompt
            )
            
            # 4. Processa a resposta
            result = cls._process_gpt_response(response, reference, db_session)
            
            return {
                "status": "success",
                "reference": reference,
                "erros_identificados": result["erros"],
                "analise_geral": result["analise_geral"]
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de {reference}: {str(e)}")
            raise

    @staticmethod
    def _process_gpt_response(response: Dict, 
                            reference: str,
                            db_session: Session) -> Dict:
        """Processa a resposta do GPT e persiste os erros"""
        try:
            # Extrai a resposta JSON
            raw_response = response.get("response", "{}")
            clean_response = raw_response.strip("```json").strip("```").strip()
            analysis_result = json.loads(clean_response)
            
            # Persiste cada erro encontrado
            for erro in analysis_result.get("erros", []):
                db_session.add(CatalogacaoErro(
                    reference=reference,
                    campo=erro["campo"],
                    conteudo_errado=erro["valor_incorreto"],
                    resposta_correta=erro["valor_correto"],
                    motivo=erro["motivo"],
                    julgado=False,
                ))
            
            db_session.commit()
            return analysis_result
            
        except json.JSONDecodeError:
            logger.error("Resposta do GPT em formato inválido")
            raise ValueError("Resposta da análise em formato inválido")
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao processar resposta: {str(e)}")
            raise

def analyze_data(reference: str, 
                carta_texto: str, 
                catalogacao_db: Session, 
                silb_db: Session) -> Dict:
    """Função principal para integração com o FastAPI"""
    try:
       
        analyzer = HistoricalDocumentAnalyzer()
        return analyzer.analyze_document(reference, carta_texto, catalogacao_db)
    
    except Exception as e:
        logger.error(f"Falha na análise de {reference}: {str(e)}")
        
        # Registra erro genérico no banco
        catalogacao_db.add(CatalogacaoErro(
            reference=reference,
            campo="sistema",
            conteudo_errado="N/A",
            motivo=f"Erro na análise: {str(e)}",
            resposta_correta="Revisar processamento",
            julgado=False
        ))
        catalogacao_db.commit()
        
        return {
            "status": "error",
            "reference": reference,
            "message": str(e),
            "erros_identificados": []
        }