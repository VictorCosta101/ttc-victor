from datetime import datetime
from dateutil.parser import parse
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
from prompts.prompts import PROMPTS
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
       "Tipo de petição",
        "Referência da antiga plataforma SILB",
        "Nome",
        "Solicitaram repartição da terra em mesma medida",
        "Capitania onde mora",
        "Histórico da terra",
        "Data da petição",
        "Data da concessão",
        "Observações da sesmaria",
        "Localidade",
        "Marcos Geográficos",
        "Ribeira",
        "Confrontantes",
        "Observações da petição",
        "Justificativas",
        "Exigências do Deferimento",
        "Total de sesmeiros que solicitaram a sesmaria",
        "Observações das Justificativas",
        "Fonte",
        "Observações do deferimento e da concessão",
        "Observações das exigências",
        "Despacho favorável",
        "Forma de Deferimento",
        "Nome do provedor",
        "Nome do procurador"
    ]


    @classmethod
    def parse_extracted_data(cls, extracted_data: Dict) -> Dict:
        """
        Formata os dados extraídos para o mesmo padrão usado na API
        """
        parsed_data = {}
        
        for original_field, translated_field in cls.FIELD_MAPPING.items():
            value = extracted_data.get(original_field, "NC")
            
            # Trata valores vazios ou "NC"
            if value and str(value).strip().upper() not in ("", "NC"):
                parsed_data[translated_field] = value
            else:
                parsed_data[translated_field] = None
                
        return parsed_data
    
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
        """Constroi o prompt para análise histórica
        
        Args:
            reference: Identificador único do documento
            catalog_data: Dados catalogados no sistema SILB
            document_text: Texto extraído da carta de sesmaria
            
        Returns:
            str: Prompt formatado para análise pelo LLM
        """
        # Lista de capitanias pré-definidas
        capitanias_validas = [
            "Alagoas", "Bahia", "Ceará", "Colonia do Sacramento", 
            "Espírito Santo", "Goias", "Itamaracá", "Maranhão",
            "Mato Grosso do Sul", "Minas Gerais", "NA", "Pará",
            "Paraíba", "Pernambuco", "Pernambuco/Alagoas", 
            "Pernambuco/Piauí", "Piauí", "Rio de Janeiro",
            "Rio Grande do Norte", "Rio Grande do Sul", "Rio Negro",
            "Santa Catarina", "São Paulo", "São Paulo/Rio de Janeiro", 
            "Sergipe"
        ]

        # Formatando as listas para exibição
        capitanias_str = json.dumps(capitanias_validas, ensure_ascii=False)
        historico_terra = '["Comprada", "Devoluta nunca povoada", "Devoluta por abandono", "Herdada", "NA", "Primordial"]'
        deferimento = '["provisão", "Carta Régia", "NC", "NA", "Carta de doação", "Alvará", "Ordem Régia"]'

        return f"""
            ## ANÁLISE DOCUMENTAL - SESMARIAS COLONIAIS
            Você é um especialista em documentos coloniais brasileiros (séculos XVI-XIX). 

            ### DADOS PARA ANÁLISE
            **Referência**: {reference}

            **Dados Catalogados**:
            {json.dumps(catalog_data, indent=2, ensure_ascii=False)}

            **Conteúdo Original** (extrato):
            {document_text}...

            ## REGRAS DE ANÁLISE

            1. CAMPOS CATEGÓRICOS (valores exatos):
            - "tipo de petição": ["concessão", "Não encontrado"]
            - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
            - "Capitania onde mora": {capitanias_str}
            - "Histórico da terra": {historico_terra}
            - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
            - "Forma de Deferimento": {deferimento}

            2. CRITÉRIOS PARA ERROS:
            REPORTAR SOMENTE SE:
            - Datas com dia/mês/ano diferentes
            - Localidades geográficas distintas
            - Nomes de proprietários radicalmente diferentes

            IGNORAR:
            - Variações de formato de data
            - Grafias alternativas
            - Ordem de elementos em listas

            3. FORMATO DE RESPOSTA (OBRIGATÓRIO):
            {{
                "erros": [
                    {{
                        "campo": "nome_do_campo",
                        "valor_incorreto": "valor_atual",
                        "valor_correto": "valor_sugerido",
                        "motivo": "explicacao_historica"
                    }}
                ]
            }}            
            """



    
    @staticmethod
    def save_prompt_to_txt(reference: str, prompt: str, output_dir: str = "prompt_logs"):
        """
        Salva o prompt em um arquivo TXT para análise posterior
        
        Args:
            reference: Identificador do documento
            prompt: Texto completo do prompt
            output_dir: Pasta onde os logs serão salvos
        """
        try:
            # Cria o diretório se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/prompt_{reference}_{timestamp}.txt"
            
            # Salva o conteúdo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(prompt)
                
            
        except Exception as e:
            print(f"Erro ao salvar prompt: {str(e)}")

    @classmethod
    def analyze_document(cls,
                       reference: str,
                       document_text: str,
                       db_session: Session, 
                       prompt_name: str) -> Dict:
        """Executa o pipeline completo de análise"""
        try:
            # 1. Busca dados catalogados
            raw_data = SILBDataFetcher.fetch_catalog_data(reference)
            print("===============================")
            
            
            if not raw_data:
                raise ValueError(f"Dados não encontrados para {reference}")
            
            # 2. Parseia e filtra os dados
        
            catalog_data = DataParser.parse_and_filter(raw_data)
            if not catalog_data:
                raise ValueError("Nenhum dado relevante encontrado para análise")
            
            prompt_func = PROMPTS.get(prompt_name)
            if not prompt_func:
                raise ValueError(f"Prompt '{prompt_name}' não encontrado")

            
            # 3. Prepara e envia para análise do GPT
            prompt = prompt_func(reference, catalog_data, document_text)
        
            cls.save_prompt_to_txt(reference, prompt)
           
            response = GPT_CLIENT.generate_content(
                assistant_prompt="Você é um historiador especializado em documentos coloniais da america portuguesa.",
                user_prompt=prompt
            )
            
           
            # 4. Processa a resposta
            result = cls._process_gpt_response(response, reference, db_session,prompt_name)
            
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
                            db_session: Session, prompt_name:str) -> Dict:
        """Processa a resposta do GPT e persiste os erros"""
        try:
            # Extrai a resposta JSON
            raw_response = response.get("response", "{}")
            clean_response = raw_response.strip("```json").strip("```").strip()
            analysis_result = json.loads(clean_response)
            DATE_FIELDS = ["Data da concessão", "Data da petição"]
            
            # Persiste cada erro encontrado
            for erro in analysis_result.get("erros", []):
               
               ''' if erro["campo"] in DATE_FIELDS:
                    if is_same_date(erro["valor_incorreto"], erro["valor_correto"]):
                     continue 
                else:'''
              
               db_session.add(CatalogacaoErro(
                        reference=reference,
                        campo=erro["campo"],
                        conteudo_errado=erro["valor_incorreto"],
                        resposta_correta=erro["valor_correto"],
                        motivo=erro["motivo"],
                        julgado=False,
                        prompt_name=prompt_name,
                        erro_positivo = False,
                    ))
            print(db_session)   
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
        prompt_name = "prompt_0"
        return analyzer.analyze_document(reference, carta_texto, catalogacao_db, prompt_name)
    
    except Exception as e:
        logger.error(f"Falha na análise de {reference}: {str(e)}")
        
        # Registra erro genérico no banco
        catalogacao_db.add(CatalogacaoErro(
            reference=reference,
            campo="sistema",
            conteudo_errado="N/A",
            motivo=f"Erro na análise: {str(e)}",
            resposta_correta="Revisar processamento",
            julgado=False,
        ))
        ##catalogacao_db.commit()
        
        return {
            "status": "error",
            "reference": reference,
            "message": str(e),
            "erros_identificados": []
        }
def is_same_date(date1: str, date2: str) -> bool:
    """
    Compara duas datas em formatos diferentes de forma robusta.
    Retorna True apenas se as datas representam o mesmo dia histórico.
    
    Exemplos:
    >>> is_same_date("18-12-1671", "1671-12-18")  # True
    >>> is_same_date("18/12/1671", "18 de dezembro de 1671")  # True
    >>> is_same_date("18-12-1671", "19-12-1671")  # False
    >>> is_same_date("data inválida", "18-12-1671")  # False
    """
    try:
        # Configuração para priorizar formato dia-mês-ano
        dt1 = parse(date1, dayfirst=True, fuzzy=True)
        dt2 = parse(date2, dayfirst=True, fuzzy=True)
        
        # Comparação dos componentes de data
        return (dt1.day == dt2.day and 
                dt1.month == dt2.month and 
                dt1.year == dt2.year)
    except (ValueError, TypeError, AttributeError):
        # Se qualquer data for inválida ou não puder ser parseada
        return False
    

class PDFDataExtractor:
    """Extrai dados estruturados diretamente do texto do PDF com validações categóricas"""
    
    @staticmethod
    def build_extraction_prompt(text: str) -> str:

        """Prompt otimizado para extração com validação categórica estrita e formato frontend-friendly"""
    
    # Listas de valores permitidos (atualizadas com seus campos)
        CATEGORIAS_SESMARIA = ["Petição Individual", "Petição Coletiva"]
        CAPITANIAS = [
        "Alagoas", "Bahia", "Ceará", "Colonia do Sacramento", "Espírito Santo", 
        "Goias", "Itamaracá", "Maranhão", "Mato Grosso do Sul", "Minas Gerais", 
        "NA", "Pará", "Paraíba", "Pernambuco", "Pernambuco/Alagoas", 
        "Pernambuco/Piauí", "Piauí", "Rio de Janeiro", "Rio Grande do Norte", 
        "Rio Grande do Sul", "Rio Negro", "Santa Catarina", "São Paulo", 
        "São Paulo/Rio de Janeiro", "Sergipe"
    ]
        HISTORICO_TERRA = ["Comprada", "Devoluta nunca povoada", "Devoluta por abandono", 
                      "Herdada", "NA", "Primordial"]
        TIPOS_PETICAO = ["concessão", "não encontrado"]
    
        return f"""
    ## INSTRUÇÕES PARA EXTRAÇÃO DE DADOS DE SESMARIAS
    
    **Objetivo**: Analisar documentos históricos de sesmarias e extrair dados estruturados 
    com validação categórica rigorosa para preenchimento automático de formulário.
    
    ### TEXTO PARA ANÁLISE:
    ```text
        {text}...
    ```
    
    ### REGRAS DE EXTRAÇÃO:
    1. **Campos categóricos**: 
       - Use SOMENTE os valores permitidos fornecidos
       - Se não encontrar correspondência exata, use "NA"
       - Nunca invente valores ou faça aproximações
    
    2. **Campos de texto livre**:
       - Mantenha a grafia original do documento
       - Preserve nomes próprios e termos técnicos
       - Para campos vazios: retorne string vazia ("")
    
    3. **Datas**:
       - Formato: "dd/mm/aaaa"
       - Se incompleta: "dd/mm/NA" ou "NA/NA/aaaa"
       - Nunca inventar datas
    
    4. **Nomes próprios**:
       - Conservar maiúsculas originais (ex: "João da Silva")
       - Não normalizar (ex: manter "Joam" em vez de "João")
    
    ### FORMATO DE SAÍDA (JSON):
    {{
        "categoria": "{CATEGORIAS_SESMARIA}",  // OBRIGATÓRIO validar
        "sesmeiro": "Texto livre (nome completo)",
        "capitania": "{CAPITANIAS}",  // OBRIGATÓRIO validar
        "estadoAtual": "{CAPITANIAS}",  // OBRIGATÓRIO validar
        "historicoTerra": "{HISTORICO_TERRA}",  // OBRIGATÓRIO validar
        "tipoPeticao": "{TIPOS_PETICAO}",  // OBRIGATÓRIO validar
        "dataPeticao": "dd/mm/aaaa",  // Formato fixo
        "localidade": "Texto livre",
        "marcosGeograficos": "Texto livre",
        "ribeira": "Texto livre",
        "confrontantes": "Texto livre",
        "observacoesPeticao": "Texto livre",
        "justificativa": "Texto livre",
        "observacoesJustificativas": "Texto livre"
    }}
    
    ### EXEMPLO DE RESPOSTA VÁLIDA:
    {{
        "categoria": "Petição Individual",
        "sesmeiro": "Antônio Rodrigues",
        "capitania": "Pernambuco",
        "estadoAtual": "Pernambuco",
        "historicoTerra": "Devoluta nunca povoada",
        "tipoPeticao": "concessão",
        "dataPeticao": "15/03/1789",
        "localidade": "Engenho São Bento",
        "marcosGeograficos": "Rio Capibaribe; Serra dos Três Irmãos",
        "ribeira": "Capibaribe",
        "confrontantes": "Com terras de João da Silva; com o rio",
        "observacoesPeticao": "O requerente alega posse há 10 anos",
        "justificativa": "Para plantio de cana-de-açúcar",
        "observacoesJustificativas": "Terras devolutas da Coroa"
    }}
    
    ### PROCESSO DE ANÁLISE:
    1. Para CADA campo:
       a) Identificar no texto informações relevantes
       b) Para campos categóricos: VERIFICAR LISTA PERMITIDA
       c) Aplicar formatação exigida
       d) Se não encontrado: usar "NA" ou string vazia conforme o caso
    
    2. Priorizar:
       - Precisão sobre completude
       - Conservar informações originais
       - Não extrapolar dados não explícitos
    
    3. Validar especialmente:
       - Datas (formato correto)
       - Nomes próprios (grafia original)
       - Campos categóricos (valores permitidos)
    """

    @staticmethod
    def extract_data_from_text(text: str) -> Dict:
        """Extrai informações com validação categórica"""
        try:
            prompt = PDFDataExtractor.build_extraction_prompt(text)
            print('Prompt:', prompt)
            response = GPT_CLIENT.generate_content(
                assistant_prompt="Você é um especialista em extração de dados de documentos históricos com validação rigorosa.",
                user_prompt=prompt
            )
            print('Response:', response)
            
            # Processa a resposta para garantir o formato correto
            raw_response = response["response"].strip()
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:-3].strip()
            
              # Converte para dicionário
            extracted_data = json.loads(raw_response)
            # Mapeia para a estrutura esperada pelo sistema
            mapped_data = {
            "categoria": extracted_data.get("categoria", "NC"),
            "request_petition_type": extracted_data.get("tipoPeticao", "NC"),
            "owner_name": extracted_data.get("sesmeiro", "NC"),
            "captaincy_name": extracted_data.get("capitania", "NC"),
            "landhistory_history": extracted_data.get("historicoTerra", "NC"),
            "request_date_request": extracted_data.get("dataPeticao", "NC"),
            "landrecord_location": extracted_data.get("localidade", "NC"),
            "landrecord_marcos": extracted_data.get("marcosGeograficos", "NC"),
            "landrecord_river": extracted_data.get("ribeira", "NC"),
            "landrecord_limitant": extracted_data.get("confrontantes", "NC"),
            "request_comments": extracted_data.get("observacoesPeticao", "NC"),
            "justifications": extracted_data.get("justificativa", "NC"),
            "comments_justification": extracted_data.get("observacoesJustificativas", "NC"),
            # Adicione outros mapeamentos conforme necessário
                }
        
            # Preenche campos não mapeados com "NC"
            final_data = {field: "NC" for field in DataParser.FIELD_MAPPING.keys()}
            final_data.update(mapped_data)
        
            logger.info(f'Final Structured Data: {final_data}')
            return final_data
            
        except Exception as e:
            logger.error(f"Erro na extração de dados do PDF: {str(e)}")
            return {field: "NC" for field in DataParser.FIELD_MAPPING.keys()}