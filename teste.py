import os
import json
import requests
import fitz  # PyMuPDF

# 🔹 Configuração da API
API_URL = "http://127.0.0.1:8000/verificar/"

# 🔹 Lista de cartas com referência e caminho do PDF
cartas = [
    {"reference": "PE-AL0001", "path": "pe-al0001.pdf"},
    {"reference": "PE-AL0002", "path": "pe-al0002.pdf"},
]

# 🔹 Array para armazenar os resultados
resultados = []

# 🔹 Função para extrair texto do PDF
def extrair_texto_pdf(caminho_pdf):
    texto = ""
    try:
        with fitz.open(caminho_pdf) as pdf:
            for pagina in pdf:
                texto += pagina.get_text("text") + "\n"
    except Exception as e:
        print(f" Erro ao ler {caminho_pdf}: {e}")
    return texto

#  Processa todas as cartas
for carta in cartas:
    reference = carta["reference"]
    path = carta["path"]

    #  Verifica se o arquivo PDF existe
    if not os.path.exists(path):
        print(f" Arquivo não encontrado: {path}")
        continue

    #  Extrai o texto do PDF
    carta_texto = extrair_texto_pdf(path)

    #  Envia para a API FastAPI
    payload = {"reference": reference, "carta_texto": carta_texto}
    response = requests.post(API_URL, json=payload)

    #  Verifica a resposta da API
    if response.status_code == 200:
        resultado = response.json()
        resultados.append(resultado)
        print(f" {reference} processado com sucesso!")
    else:
        print(f" Erro ao processar {reference}: {response.text}")

# 🔹 Mostra os resultados finais
print("\nResultados Finais:")
print(json.dumps(resultados, indent=4, ensure_ascii=False))
