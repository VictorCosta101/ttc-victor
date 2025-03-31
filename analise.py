import requests
import psycopg2
import ollama
import json

# Configuração do banco de dados
DB_CONFIG = {
    "dbname": "catalogacao",
    "user": "user",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}

# Lista de referências e caminhos das cartas
documentos = [
    {"reference": "PE-AL0001", "path": "caminho/para/carta1.txt"},
    {"reference": "PE-AL0002", "path": "caminho/para/carta2.txt"},
]

# Função para buscar dados na API
def buscar_dados_api(reference):
    url = f"http://plataformasilb.cchla.ufrn.br/api/get/tabela?reference={reference}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Função para ler o conteúdo da carta
def ler_carta(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {path}")
        return None

# Função para comparar usando GPT-4o Mini
def comparar_com_gpt(api_data, texto_carta):
    prompt = f"""
    Abaixo estão os dados extraídos da API e o conteúdo da carta original.
    Compare os valores e identifique quaisquer inconsistências.

    **Dados da API:** {json.dumps(api_data, indent=2)}

    **Texto da Carta:** {texto_carta}

    Liste os campos inconsistentes no formato JSON: 
    [
      {{"campo": "campo_incorreto", "valor_api": "valor1", "valor_carta": "valor2"}},
      ...
    ]
    """
    resposta = ollama.chat(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    try:
        return json.loads(resposta["message"]["content"])
    except json.JSONDecodeError:
        print("Erro ao interpretar resposta do GPT.")
        return []

# Função para salvar os erros no banco de dados
def salvar_erros(reference, erros):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for erro in erros:
        cur.execute(
            """
            INSERT INTO erros_catalogacao (reference, campo, valor_api, valor_carta)
            VALUES (%s, %s, %s, %s)
            """,
            (reference, erro["campo"], erro["valor_api"], erro["valor_carta"]),
        )
    conn.commit()
    cur.close()
    conn.close()

# Executando o fluxo
for doc in documentos:
    api_data = buscar_dados_api(doc["reference"])
    texto_carta = ler_carta(doc["path"])

    if api_data and texto_carta:
        erros = comparar_com_gpt(api_data, texto_carta)
        if erros:
            salvar_erros(doc["reference"], erros)
            print(f"Erros salvos para referência {doc['reference']}")
        else:
            print(f"Nenhuma inconsistência encontrada para {doc['reference']}")

