from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from data_comparator import analyze_data
from db import get_catalogacao_db, get_silb_db
from models import Base, CatalogacaoErro
from juiz import julgar_erros
from pathlib import Path
import fitz  # PyMuPDF
import logging
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de diretórios (adicionar no início do arquivo)
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# Cria as tabelas no banco de dados catalogacao (se não existirem)
Base.metadata.create_all(bind=get_catalogacao_db().__next__().bind)

app = FastAPI()
@app.post("/verificar/")
async def verificar_carta(
    reference: str = Query(...),
    file: UploadFile = File(...),
    catalogacao_db: Session = Depends(get_catalogacao_db),
    silb_db: Session = Depends(get_silb_db)
):
    # 1. Configuração inicial
    cache_path = CACHE_DIR / f"{reference}.pdf"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)  # Garante que o diretório existe
    
    try:
        # 2. Validação e salvamento do arquivo
        try:
            # Lê e valida o conteúdo do arquivo
            contents = await file.read()
            if not contents:
                raise HTTPException(
                    status_code=400,
                    detail="O arquivo enviado está vazio"
                )
            
            # Salva no cache com verificação
            with open(cache_path, "wb") as f:
                f.write(contents)
            
            # Verifica se o arquivo foi salvo corretamente
            if not cache_path.exists() or os.path.getsize(cache_path) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Falha ao salvar arquivo temporário no cache"
                )
                
        except HTTPException:
            raise
        except Exception as file_error:
            '''
            if cache_path.exists():
                cache_path.unlink()
            '''
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar arquivo: {str(file_error)}"
            )

        # 3. Processamento do PDF
        try:
            # Abre e valida o PDF
            pdf_document = fitz.open(cache_path)
            if pdf_document.is_closed or pdf_document.page_count == 0:
                raise ValueError("PDF inválido ou vazio")
            
            # Extrai o texto com verificação
            carta_texto = "\n".join(
                pagina.get_text("text") 
                for pagina in pdf_document 
                if pagina.get_text("text").strip()
            )
            
            if not carta_texto.strip():
                raise ValueError("PDF não contém texto legível")
            
            pdf_document.close()
            
        except Exception as pdf_error:
            if cache_path.exists():
                cache_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar PDF: {str(pdf_error)}"
            )

        # 4. Análise dos dados
        try:
            
            resultado = analyze_data(
                reference=reference,
                carta_texto=carta_texto,
                catalogacao_db=catalogacao_db,
                silb_db=silb_db
            )
           
            # Limpeza final
            '''
            if cache_path.exists():
                cache_path.unlink()   
            return resultado
            '''
        except Exception as analysis_error:
            # Mantém o arquivo para debug em caso de erro na análise
            logger.error(f"Arquivo mantido em {cache_path} para análise do erro")
            
            # Registra erro no banco
            erro = CatalogacaoErro(
                reference=reference,
                campo="sistema",
                conteudo_errado="N/A",
                motivo=f"Erro na análise: {str(analysis_error)}",
                resposta_correta="Revisar processamento"
            )
            catalogacao_db.add(erro)
            catalogacao_db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=f"Erro na análise do documento: {str(analysis_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Falha crítica ao processar {reference}")
        '''
        # Limpeza em caso de erro não tratado
        if cache_path.exists():
            cache_path.unlink()
          '''
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no servidor: {str(e)}"
        )

@app.post("/julgar/")
def julgar_erros_endpoint(
    catalogacao_db: Session = Depends(get_catalogacao_db)  # Sessão do banco catalogacao
):
    try:
        # Chama a função de julgamento
        julgar_erros(catalogacao_db)
        return {"message": "Julgamento concluído!"}

    except Exception as e:
        logger.exception("Erro ao julgar erros")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/erros/")
def listar_erros(
    catalogacao_db: Session = Depends(get_catalogacao_db)  # Sessão do banco catalogacao
):
    try:
        # Retorna todos os erros registrados
        erros = catalogacao_db.query(CatalogacaoErro).all()
        return {"erros": erros}

    except Exception as e:
        logger.exception("Erro ao listar erros")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/julgamentos/")
def listar_julgamentos(
    catalogacao_db: Session = Depends(get_catalogacao_db)  # Sessão do banco catalogacao
):
    try:
        # Retorna todos os julgamentos registrados
        julgamentos = catalogacao_db.query(Julgamento).all()
        return {"julgamentos": julgamentos}

    except Exception as e:
        logger.exception("Erro ao listar julgamentos")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")