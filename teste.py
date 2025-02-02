import requests
import json  # Importar o módulo correto para lidar com JSON

# URL pública do servidor ngrok
ollama_host = "https://7b60-35-187-254-206.ngrok-free.app"

def ask_mistral(prompt):
    url = f"{ollama_host}/api/generate"  # Endpoint para interagir com o modelo
    payload = {
        "model": "mistral",  # Nome do modelo
        "prompt": prompt     # Entrada do usuário
    }
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        # Enviar a requisição POST
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            if response.status_code == 200:
                # Processar o streaming da resposta
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            # Decodificar cada linha como JSON
                            partial_response = json.loads(line.decode("utf-8"))
                            full_response += partial_response.get("response", "")
                        except ValueError:
                            continue
                return full_response
            else:
                return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao conectar ao servidor: {str(e)}"

# Testar o modelo com uma pergunta simples
if __name__ == "__main__":
    prompt = "Qual é a capital da França?"
    resposta = ask_mistral(prompt)
    print("Resposta do Mistral:", resposta)
