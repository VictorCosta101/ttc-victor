import openai
import requests
import PyPDF2
import json

# Configuração da API do ChatGPT
openai.api_key = "sua-chave-api-da-openai"

# URL do servidor Ollama
OLLAMA_URL = "http://seu-servidor-ollama:port/api/generate"

# Função para ler texto de um PDF
def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Erro ao ler o PDF: {str(e)}"

# Função para consultar o modelo GPT da OpenAI
def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Ou outro modelo compatível
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro com ChatGPT: {str(e)}"

# Função para consultar o modelo Mistral rodando no Ollama
def ask_mistral(prompt):
    try:
        payload = {"prompt": prompt}
        headers = {"Content-Type": "application/json"}
        response = requests.post(OLLAMA_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("response", "Sem resposta do modelo.")
    except Exception as e:
        return f"Erro com Mistral: {str(e)}"

# Função para comparar os modelos
def compare_models(text, questions):
    results = {"chatgpt": [], "mistral": []}
    
    for question in questions:
        prompt = f"{text}\nPergunta: {question}"
        '''
        # Consultar ChatGPT
        chatgpt_response = ask_chatgpt(prompt)
        results["chatgpt"].append({"question": question, "response": chatgpt_response})
        '''
        # Consultar Mistral
        mistral_response = ask_mistral(prompt)
        results["mistral"].append({"question": question, "response": mistral_response})
    
    return results

# Função para salvar os resultados
def save_results(results, filename="results.json"):
    with open(filename, "w") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

# Fluxo principal do programa
if __name__ == "__main__":
    # Caminho do arquivo PDF
    pdf_path = "carta_sesmarias.pdf"  # Substitua pelo caminho do seu arquivo PDF
    
    # Extrair texto do PDF
    carta_texto = extract_text_from_pdf(pdf_path)
    if "Erro" in carta_texto:
        print(carta_texto)  # Exibe erro se não conseguir ler o PDF
    else:
        print("Texto extraído com sucesso.")
        
        # Perguntas para os modelos
        perguntas = [
            "Qual o ano da concessão da carta?",
            "Para que finalidade foi concedida a sesmaria?",
            "Onde está localizada a região mencionada?"
        ]
        
        # Comparar os modelos
        resultados = compare_models(carta_texto, perguntas)
        
        # Salvar os resultados
        save_results(resultados)
        print("Resultados salvos em 'results.json'")
