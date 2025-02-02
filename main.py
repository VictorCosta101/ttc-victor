import requests
import json
import time
import pdfplumber
import os
import weave
from openai import OpenAI




weave.init('gpt-4-setup')


client = OpenAI(api_key="")


def get_pdf_text(file_path):
    """
    Função para ler o texto do PDF.
    """
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def generate_llm_prompt(extracted_text):
    """
    Função para gerar um prompt para o modelo LLM com base no texto extraído do PDF.
    """
    prompt = f'''
    Texto_fonte: {extracted_text}
    Função: você é um historiador.
    Responda em português.
    Você é um agente de processamento de texto trabalhando com documentos de contrato de arrendamento (sesmarias).
    Extraia os valores especificados do texto tokenizado fonte.

    Retorne a resposta como um objeto JSON com os seguintes campos:
    - "Categoria_da_sesmaria" <string>
    - "Sesmeiros" <string>
    - "Capitania" <string>
    - "Estado_atual" <string>
    - "Historico_da_terra" <string>
    - "Data_de_peticao" <string>
    - "Localidade" <string>
    - "Marcos_geograficos" <string>
    - "Ribeira" <string>
    - "Confrontantes" <string>
    - "Area" <float>
    - "Tipo_de_area" <string>
    - "Largura" <string>
    - "Comprimento" <string>

    Instrução:
    Não infira dados com base no treinamento anterior, use estritamente apenas o texto fonte fornecido como entrada.
    Responda todos os campos. Caso não encontre a informação no texto, retorne o campo com "NA".
    Classifique "Categoria_da_sesmaria" selecionando uma das seguintes opções ["individual"], ["coletiva"].
    Classifique "Capitania" selecionando uma das seguintes opções ["Alagoas"], ["Bahia"], ["Ceará"], ["Colônia do Sacramento"], ["Espírito Santo"], 
    ["Goiás"], ["Itamaracá"], ["Maranhão"], ["Mato Grosso do Sul"], ["Minas Gerais"], ["NA"], ["Pará"], ["Paraíba"], ["Pernambuco"], ["Pernambuco/Alagoas"], 
    ["Pernambuco/Piauí"], ["Piauí"], ["Rio de Janeiro"], ["Rio Grande do Norte"], ["Rio Grande do Sul"], ["Rio Negro"], ["Santa Catarina"], ["São Paulo"], 
    ["São Paulo/Rio de Janeiro"], ["Sergipe"].
    Classifique "Estado_atual" selecionando uma das seguintes opções ["Alagoas"], ["Bahia"], ["Ceará"], ["Colônia do Sacramento"], ["Espírito Santo"], ["Goiás"], ["Itamaracá"], 
    ["Maranhão"], ["Mato Grosso do Sul"], ["Minas Gerais"], ["NA"], ["Pará"], ["Paraíba"], ["Pernambuco"], ["Pernambuco/Alagoas"], ["Pernambuco/Piauí"], ["Piauí"], 
    ["Rio de Janeiro"], ["Rio Grande do Norte"], ["Rio Grande do Sul"], ["Rio Negro"], ["Santa Catarina"], ["São Paulo"], ["São Paulo/Rio de Janeiro"], ["Sergipe"].
    Classifique "Historico_da_terra" selecionando uma das seguintes opções ["Comprada"], ["Devoluta nunca povoada"], ["Devoluta por abandono"], ["Herdada"], ["NA"], ["Primordial"].
    Classifique "Tipo_de_area" selecionando uma das seguintes opções ["Léguas"], ["Braças"], ["NA"].
    '''
    return prompt


@weave.op()
def generate_content(gpt_assistant_prompt: str, gpt_user_prompt: str) -> dict:
    gpt_prompt = f"{gpt_assistant_prompt} {gpt_user_prompt}"
    messages = [
        {"role": "assistant", "content": gpt_assistant_prompt},
        {"role": "user", "content": gpt_user_prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Ensure correct model name is used
        messages=messages,
        temperature=0.2,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    response_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    
    return {"response": response_text, "tokens_used": tokens_used}


def send_to_openai_api(prompt, model="gpt-4o-mini"):
    """
    Envia o prompt para o modelo GPT-4o Mini da OpenAI e retorna a resposta.
    """
    try:
        # Estruturando a mensagem no formato esperado pela API
        messages = [{"role": "user", "content": prompt}]

        # Enviando requisição ao OpenAI via Weave
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=1000,
            frequency_penalty=0.0
        )

        # Extraindo o texto da resposta
        return response.choices[0].message.content

    except Exception as e:
        print(f"Erro ao conectar ao OpenAI: {str(e)}")
        return None


def send_to_llm(model, prompt):
    """
    Envia o prompt para o servidor usando streaming de resposta.
    """
    url = 'https://5b95-35-187-254-206.ngrok-free.app/api/generate'  # Substitua pela URL do ngrok
    headers = {'Content-Type': 'application/json'}
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "options": {"temperature": 0.7}
    }
    
    # Inicia o cronômetro
    inicio = time.time()
    
    try:
        # Enviar requisição POST com streaming
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            if response.status_code == 200:
                # Processar o streaming da resposta
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            partial_response = json.loads(line.decode("utf-8"))
                            full_response += partial_response.get("response", "")
                        except json.JSONDecodeError:
                            continue
                fim = time.time()
                print(f"Tempo de resposta para {model}: {fim - inicio:.2f} segundos")
                return full_response
            else:
                print(f"Erro: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Erro ao conectar ao servidor para o modelo {model}: {str(e)}")
        return None

def save_response_to_file(pdf_name, model_name, response, model_time):
    """
    Função para salvar a resposta de um modelo em um arquivo de texto.
    """
    # Criar diretório para armazenar as respostas, se não existir
    output_dir = "respostas"
    os.makedirs(output_dir, exist_ok=True)
    
    # Nome do arquivo baseado no nome do PDF e no nome do modelo
    file_name = f"{pdf_name}_{model_name}_response.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Salvar a resposta no arquivo
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"Resposta do Modelo: {model_name}\n")
        file.write(f"Tempo de Resposta: {model_time:.2f} segundos\n\n")
        file.write("Resposta do Modelo:\n")
        file.write(response)

    print(f"Resposta salva em: {file_path}")

def compare_responses(pdf_path):
    """
    Compara as respostas dos modelos GPT-4 Mini e Mistral.
    """
    # Passo 1: Obter o texto do PDF
    pdf_text = get_pdf_text(pdf_path)
    
    # Passo 2: Gerar o prompt
    prompt = generate_llm_prompt(pdf_text)
    
    # Passo 3: Enviar para o GPT-4 Mini
    print("Enviando para GPT-4 Mini...")
    gpt4_response = send_to_openai_api(prompt, model="gpt-4o-mini")
    '''
    # Passo 4: Enviar para o Mistral
    print("Enviando para Mistral...")
    mistral_response = send_to_llm("mistral", prompt)
    print(mistral_response)
 
    print("Enviando para Gemma 2...")
    gemma2_response = send_to_llm("gemma2", prompt)
    '''
    save_response_to_file(pdf_path, "gpt-4o-mini",gpt4_response, 0)
    

def main():
    """
    Função principal para executar o experimento.
    """
    lista_pdf_path = ['pe-al0001.pdf','pe-al0002.pdf','pe-al0003.pdf','pe-al0004.pdf','pe-al0005.pdf','pe-al0006.pdf','pe-al0007.pdf','pe-al0008.pdf','pe-al0009.pdf','pe-al0010.pdf']
    for pdf_path in lista_pdf_path:
        compare_responses(pdf_path)

if __name__ == '__main__':
    main()
