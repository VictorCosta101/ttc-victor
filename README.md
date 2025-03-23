# Plataforma SILB - Detecção de Erros de Catalogação com IA

## Introdução

Este projeto tem como objetivo identificar erros de catalogação na **Plataforma SILB** () utilizando **Inteligência Artificial (IA)**. A plataforma SILB é uma base de dados que contém informações sobre as sesmarias concedidas pela Coroa portuguesa no mundo atlântico, incluindo quase 16 mil cartas de sesmarias concedidas na América portuguesa.

### Propósito do Projeto

A catalogação de documentos históricos é um processo complexo e propenso a erros. Este projeto visa:
1. **Automatizar a detecção de erros** de catalogação nas cartas de sesmarias.
2. **Melhorar a qualidade dos dados** disponíveis para pesquisadores e historiadores.
3. **Facilitar a correção de inconsistências** nos registros da plataforma SILB.
4. **Integrar IA** para comparar os dados catalogados com o conteúdo original das cartas.

---

## Sobre a Plataforma SILB

A **Plataforma SILB** é uma iniciativa que facilita o acesso às informações de cartas de sesmarias concedidas pela Coroa portuguesa no mundo atlântico. Ela inclui dados sobre:
- **Petições**: Justificativas dos requerentes para obter sesmarias.
- **Concessões**: Obrigações dos beneficiários, como cultivo, demarcação e confirmação real.
- **Cartas de Sesmarias**: Documentos históricos que registram a concessão de terras.

Para mais informações, visite o site oficial da [Plataforma SILB](http://plataformasilb.cchla.ufrn.br/).

---

## Como Funciona o Projeto

O projeto utiliza **FastAPI** para criar uma API que:
1. Recebe arquivos PDF de cartas de sesmarias.
2. Extrai o texto do PDF e detecta o **reference** (identificador único) da carta.
3. Consulta a API do SILB para obter os dados catalogados.
4. Usa **IA (GPT)** para comparar os dados catalogados com o conteúdo original da carta.
5. Identifica e registra erros de catalogação em um banco de dados **PostgreSQL**.

---

## Requisitos do Projeto

Para executar o projeto, você precisará dos seguintes requisitos:

### Software
- **Python 3.8 ou superior**
- **PostgreSQL** (banco de dados)
- **Docker** (opcional, para containerização)
- **Git** (para clonar o repositório)

### Dependências do Python
- **FastAPI**: Framework para criar a API.
- **PyMuPDF (fitz)**: Biblioteca para extrair texto de PDFs.
- **SQLAlchemy**: ORM para interagir com o banco de dados PostgreSQL.
- **Requests**: Biblioteca para fazer requisições HTTP à API do SILB.
- **python-multipart**: Para lidar com uploads de arquivos no FastAPI.

---

## Passo a Passo para Configurar e Executar o Projeto

### 1. Clone o Repositório

bash
git clone https://github.com/seu-usuario/tcc-victor.git
cd tcc-victor

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

### 3. Instale as Dependências
pip install -r requirements.txt


### 4. Configure o Banco de Dados PostgreSQL
1 - Crie um banco de dados no PostgreSQL.
2 - Atualize a variável DATABASE_URL no arquivo db.py com as credenciais do banco:
DATABASE_URL = "postgresql://usuario:senha@localhost:5432/nome_do_banco"

### 5. Execute o Servidor FastAPI
uvicorn main:app --reload
O servidor estará disponível em http://127.0.0.1:8000.

### 6. Envie Requisições para a API
python teste.py


## Detalhes da API
Endpoint: /verificar/

    Método: POST

    Descrição: Recebe um arquivo PDF de uma carta de sesmaria e retorna os erros de catalogação identificados.

    Parâmetros:

        file (obrigatório): Arquivo PDF da carta.

    Resposta:

        reference: Identificador único da carta.

        erros_identificados: Lista de erros de catalogação.

        message: Mensagem de sucesso ou erro.

Exemplo de requisição:

curl -X POST -F "file=@pe-al0001.pdf" http://127.0.0.1:8000/verificar/

{
    "reference": "PE-AL0001",
    "erros_identificados": [
        {
            "campo": "localização",
            "valor_incorreto": "Recife",
            "valor_correto": "Olinda",
            "motivo": "A localização correta é Olinda, conforme o texto da carta."
        }
    ],
    "message": "Verificação concluída!"
}