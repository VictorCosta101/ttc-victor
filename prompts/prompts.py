import json

def prompt_0(reference: str, 
                            catalog_data: dict, 
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

def prompt_1(reference: str, 
                            catalog_data: dict, 
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
            ## PAPEL
            Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

            ## TAREFA
            Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

            ## DADOS
            Texto original da carta:
            {document_text}

            Dados catalogados:
            {json.dumps(catalog_data, indent=2, ensure_ascii=False)}

            ## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

            Se não houver divergências, retorne uma lista vazia para "erros".           
            """
def prompt_2(reference: str, 
                            catalog_data: dict, 
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

        ## PAPEL
        Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

        ## TAREFA
        Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

        ## EXEMPLOS
        Aqui estão alguns exemplos de análises anteriores:

        Exemplo 1:
        Texto original: "Aos vinte dias do mês de março de 1732, na cidade de Olinda, capitania de Pernambuco, foi concedida sesmaria a João da Silva..."
        Dados catalogados: "owner_name": "João Silva", "dateConcession": "20-03-1733", "captaincy_name": "Pernambuco"
        Análise:
        
            "erros": 
                
                    "campo": "owner_name",
                    "valor_incorreto": "João Silva",
                    "valor_correto": "João da Silva",
                    "motivo": "O texto original menciona 'João da Silva' com a preposição 'da' que está ausente na catalogação"
                
                    "campo": "dateConcession",
                    "valor_incorreto": "20-03-1733",
                    "valor_correto": "20-03-1732",
                    "motivo": "O texto original indica o ano de 1732, não 1733 como catalogado"
              


        Exemplo 2:
        Texto original: "...terras devolutas nunca povoadas na Ribeira do Açu..."
        Dados catalogados: "landhistory_history": "Devoluta por abandono", "landrecord_river": "Açu"
        Análise:
       
                    "campo": "landhistory_history",
                    "valor_incorreto": "Devoluta por abandono",
                    "valor_correto": "Devoluta nunca povoada",
                    "motivo": "O texto especifica 'terras devolutas nunca povoadas', indicando que nunca foram ocupadas, não que foram abandonadas"
           


        ## DADOS
        Texto original da carta:
        
        {document_text}
        

        Dados catalogados:
        
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}
        

        CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

        ## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

        Se não houver divergências, retorne uma lista vazia para "erros".         
            """

def prompt_3(reference: str, 
                            catalog_data: dict, 
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

        ## PAPEL
Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

## TAREFA
Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

## PROCESSO DE ANÁLISE
Para realizar esta tarefa com precisão, siga este processo de raciocínio:

1. Primeiro, identifique no texto original todas as informações relevantes para catalogação:
   - Nomes de pessoas (sesmeiros, autoridades)
   - Datas (concessão, confirmação)
   - Localizações (capitania, localidade, rios)
   - Características da terra (histórico, confrontantes)
   - Processo administrativo (tipo de petição, deferimento)

2. Em seguida, compare cada informação identificada com o campo correspondente nos dados catalogados:
   - Verifique a grafia exata dos nomes
   - Confirme se as datas estão corretas (dia, mês e ano)
   - Valide se as categorias selecionadas correspondem ao texto
   - Certifique-se de que não há omissões de informações presentes no texto

3. Para cada divergência encontrada:
   - Identifique o campo específico
   - Registre o valor atual catalogado
   - Determine o valor correto conforme o texto original
   - Explique brevemente a natureza da divergência

4. Finalmente, avalie o impacto geral das divergências na qualidade da catalogação.

## DADOS
Texto original da carta:
        
        {document_text}
        

        Dados catalogados:
        
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}


        CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

Se não houver divergências, retorne uma lista vazia para "erros".         
            """
def prompt_4(reference: str, 
                            catalog_data: dict, 
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
        ## PAPEL    ## PAPEL
Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

## TAREFA
Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

## CONHECIMENTO CONTEXTUAL
Para auxiliar na análise, considere estas informações contextuais relevantes:

### Terminologia Histórica
- "Datas de terra" e "sesmarias" referem-se ao mesmo tipo de concessão
- "Devoluta" significa terra não ocupada ou retornada à Coroa
- "Confirmação" é o processo de validação de uma concessão anterior
- "Medição" refere-se ao processo de demarcação dos limites da terra

### Estrutura Administrativa Colonial
- Capitanias eram as principais divisões administrativas
- A hierarquia incluía: Rei > Governador > Provedor > Sesmeiro
- Documentos podiam ser emitidos por diferentes autoridades

### Formatos de Data
- Datas eram frequentemente escritas por extenso ("aos vinte dias do mês de março")
- Anos eram frequentemente escritos com "anno de" ou "era de"
- O calendário usado é o gregoriano após 1582

### Categorias de Terras
- "Primordial": primeira ocupação de terra virgem
- "Devoluta nunca povoada": terra não ocupada anteriormente
- "Devoluta por abandono": terra que voltou à Coroa por falta de uso
- "Comprada": adquirida de proprietário anterior
- "Herdada": recebida por herança
### CRITÉRIOS PARA ERROS:
            REPORTAR SOMENTE SE:
            - Datas com dia/mês/ano diferentes
            - Localidades geográficas distintas
            - Nomes de proprietários radicalmente diferentes

            IGNORAR:
            - Variações de formato de data
            - Grafias alternativas
            - Ordem de elementos em listas
## DADOS
Texto original da carta:
        
        {document_text}
        
        Dados catalogados:
        
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}
        

        CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

Se não houver divergências, retorne uma lista vazia para "erros".        
            """
        

def prompt_5(reference: str, 
                            catalog_data: dict, 
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
            ## PAPEL
Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

## TAREFA
Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

## ABORDAGEM DE VERIFICAÇÃO DUPLA
Para garantir a máxima precisão, você deve:

1. Realizar uma primeira análise completa, identificando possíveis divergências
2. Realizar uma segunda análise independente, sem considerar os resultados da primeira
3. Comparar os resultados das duas análises e resolver quaisquer discrepâncias
4. Verificar a consistência interna dos dados catalogados
5. Verificar a consistência entre os dados catalogados e o texto original
6. Avaliar a qualidade geral da catalogação, considerando a clareza e a precisão dos dados definidos em criterio para erros
## DADOS
Texto original da carta:
        
        {document_text}
        

        Dados catalogados:
        
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}


        CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

##INSTRUÇÕES ADICIONAIS
### CRITÉRIOS PARA ERROS:
            REPORTAR SOMENTE SE:
            - Datas com dia/mês/ano diferentes
            - Localidades geográficas distintas
            - Nomes de proprietários radicalmente diferentes

            IGNORAR:
            - Variações de formato de data
            - Grafias alternativas
            - Ordem de elementos em listas

## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

Se não houver divergências, retorne uma lista vazia para "erros".         
            """
def prompt_6(reference: str, 
                            catalog_data: dict, 
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

        ## PAPEL
Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

## TAREFA
Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

## PROCESSO DE ANÁLISE
Para realizar esta tarefa com precisão, siga este processo de raciocínio:

1. Primeiro, identifique no texto original todas as informações relevantes para catalogação:
   - Nomes de pessoas (sesmeiros, autoridades)
   - Datas (concessão, confirmação)
   - Localizações (capitania, localidade, rios)
   - Características da terra (histórico, confrontantes)
   - Processo administrativo (tipo de petição, deferimento)

2. Em seguida, compare cada informação identificada com o campo correspondente nos dados catalogados:
   - Verifique a grafia exata dos nomes
   - Confirme se as datas estão corretas (dia, mês e ano)
   - Valide se as categorias selecionadas correspondem ao texto
   - Certifique-se de que não há omissões de informações presentes no texto

3. Para cada divergência encontrada:
   - Identifique o campo específico
   - Registre o valor atual catalogado
   - Determine o valor correto conforme o texto original
   - Explique brevemente a natureza da divergência

4. Finalmente, avalie o impacto geral das divergências na qualidade da catalogação.

## DADOS
Texto original da carta:
        
        {document_text}
        

        Dados catalogados:
        
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}


        CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

Se não houver divergências, retorne uma lista vazia para "erros".         
            """
def prompt_7(reference: str, 
                            catalog_data: dict, 
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
## PAPEL
Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

## TAREFA
Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados.

## EXEMPLOS
Aqui está um exemplo de análise anterior:

Texto original: "Aos vinte dias do mês de março de 1732, na cidade de Olinda, capitania de Pernambuco, foi concedida sesmaria a João da Silva..."
Dados catalogados: {{"owner_name": "João Silva", "dateConcession": "20-03-1733", "captaincy_name": "Pernambuco"}}

Processo de raciocínio:
1. Analisando o nome do proprietário:
   - No texto original: "João da Silva"
   - Nos dados catalogados: "João Silva"
   - Há divergência: falta o "da" no sobrenome

2. Analisando a data de concessão:
   - No texto original: "vinte dias do mês de março de 1732"
   - Nos dados catalogados: "20-03-1733"
   - Há divergência: o ano está incorreto (1733 vs. 1732)

3. Analisando a capitania:
   - No texto original: "capitania de Pernambuco"
   - Nos dados catalogados: "Pernambuco"
   - Não há divergência: o valor está correto

Resultado:
json
{{
    "erros": [
        {{
            "campo": "owner_name",
            "valor_incorreto": "João Silva",
            "valor_correto": "João da Silva",
            "motivo": "O texto original menciona 'João da Silva' com a preposição 'da' que está ausente na catalogação"
        }},
        {{
            "campo": "dateConcession",
            "valor_incorreto": "20-03-1733",
            "valor_correto": "20-03-1732",
            "motivo": "O texto original indica o ano de 1732, não 1733 como catalogado"
        }}
    ]
}}


## PROCESSO DE ANÁLISE
Para realizar esta tarefa com precisão, siga este processo de raciocínio:

1. Primeiro, identifique no texto original todas as informações relevantes para catalogação:
   - Nomes de pessoas (sesmeiros, autoridades)
   - Datas (concessão, confirmação)
   - Localizações (capitania, localidade, rios)
   - Características da terra (histórico, confrontantes)
   - Processo administrativo (tipo de petição, deferimento)

2. Em seguida, compare cada informação identificada com o campo correspondente nos dados catalogados:
   - Verifique a grafia exata dos nomes
   - Confirme se as datas estão corretas (dia, mês e ano)
   - Valide se as categorias selecionadas correspondem ao texto
   - Certifique-se de que não há omissões de informações presentes no texto

3. Para cada divergência encontrada:
   - Identifique o campo específico
   - Registre o valor atual catalogado
   - Determine o valor correto conforme o texto original
   - Explique brevemente a natureza da divergência

4. Finalmente, avalie o impacto geral das divergências na qualidade da catalogação.

## DADOS
Texto original da carta:
            {document_text}

Dados catalogados:
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}

        

        CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

##INSTRUÇÕES ADICIONAIS
### CRITÉRIOS PARA ERROS:
            REPORTAR SOMENTE SE:
            - Datas com dia/mês/ano diferentes
            - Localidades geográficas distintas
            - Nomes de proprietários radicalmente diferentes

            IGNORAR:
            - Variações de formato de data
            - Grafias alternativas
            - Ordem de elementos em listas

## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

Se não houver divergências, retorne uma lista vazia para "erros".        
            """




def prompt_8(reference: str, 
                            catalog_data: dict, 
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
## PAPEL
Você é um especialista em análise de documentos históricos do período colonial brasileiro, com profundo conhecimento sobre cartas de sesmaria e seus processos de catalogação.

## TAREFA
Analise cuidadosamente o texto original da carta de sesmaria e os dados catalogados na plataforma. Identifique e liste todas as divergências encontradas entre o conteúdo original e os dados catalogados, indicando seu nível de confiança para cada divergência identificada.

## DADOS
Texto original da carta:
        
        {document_text}
        

        Dados catalogados:
        
        {json.dumps(catalog_data, indent=2, ensure_ascii=False)}



## NÍVEIS DE CONFIANÇA
Para cada divergência identificada, considere internamente um nível de confiança:
- **Alta**: Evidência clara e inequívoca no texto original
- **Média**: Evidência presente, mas com alguma ambiguidade
- **Baixa**: Evidência indireta ou baseada em inferência


CAMPOS CATEGÓRICOS (valores exatos):
                    - "tipo de petição": ["concessão", "Não encontrado"]
                    - "Solicitaram repartição da terra": ["sim", "não", "true", "false"]
                    - "Capitania onde mora": {capitanias_str}
                    - "Histórico da terra": {historico_terra}
                    - "Despacho favorável": ["Sim", "Não", "Parcial", "NC", "NA"]
                    - "Forma de Deferimento": {deferimento}

##INSTRUÇÕES ADICIONAIS
### CRITÉRIOS PARA ERROS:
            REPORTAR SOMENTE SE:
            - Datas com dia/mês/ano diferentes
            - Localidades geográficas distintas
            - Nomes de proprietários radicalmente diferentes

            IGNORAR:
            - Variações de formato de data
            - Grafias alternativas
            - Ordem de elementos em listas
## FORMATO DE RESPOSTA (OBRIGATÓRIO):
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

Se não houver divergências, retorne uma lista vazia para "erros".       
            """

# Exporta os prompts como um dicionário
PROMPTS = {
    "prompt_0": prompt_0,
    "prompt_1": prompt_1,
    "prompt_2": prompt_2,
    "prompt_3": prompt_3,
    "prompt_4": prompt_4,
    "prompt_5": prompt_5,
    "prompt_6": prompt_6,
    "prompt_7": prompt_7,
    "prompt_8": prompt_8,
}