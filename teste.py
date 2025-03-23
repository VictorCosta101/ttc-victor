import os
import json
import requests

# 🔹 Configuração da API
API_URL = "http://127.0.0.1:8000/verificar/"

# 🔹 Lista de cartas com caminho do PDF
cartas = [
    {"path": "pe-al0010.pdf"},
]

# 🔹 Array para armazenar os resultados
resultados = []

# Processa todas as cartas
for carta in cartas:
    path = carta["path"]

    # Verifica se o arquivo PDF existe
    if not os.path.exists(path):
        print(f" Arquivo não encontrado: {path}")
        continue

    # Prepara o arquivo para envio
    files = {"file": (path, open(path, "rb"), "application/pdf")}

    # Envia para a API FastAPI
    response = requests.post(API_URL, files=files)

    # Verifica a resposta da API
    if response.status_code == 200:
        resultado = response.json()
        resultados.append(resultado)
        print(f" Arquivo {path} processado com sucesso!")
    else:
        print(f" Erro ao processar {path}: {response.text}")

# 🔹 Mostra os resultados finais
print("\nResultados Finais:")
print(json.dumps(resultados, indent=4, ensure_ascii=False))