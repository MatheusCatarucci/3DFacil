# ============================================================
# 1. IMPORTAÇÕES NECESSÁRIAS
# ============================================================

# Bibliotecas nativas do Python
import os
import socket
import subprocess
from pathlib import Path
from fastapi import Query

# Bibliotecas de terceiros
import bcrypt
from pydantic import BaseModel

# Bibliotecas do FastAPI
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Middleware para gerenciamento de sessões
from starlette.middleware.sessions import SessionMiddleware

# Módulos próprios da aplicação
from model import buscarUsuarioPorEmail


# ============================================================
# MODELOS
# ============================================================

# Modelos base de dados de entrada (Pydantic).
class Usuario(BaseModel):
    email: str
    senha: str


# ============================================================
# 2. CONFIGURAÇÕES DA APLICAÇÃO
# ============================================================

# Define o ambiente da aplicação.
# Caso a variável APP_ENV não exista, utiliza "development".
APP_ENV = os.getenv("APP_ENV", "development")

# Chave utilizada para assinar os dados das sessões.
# Deve ser definida através de uma variável de ambiente.
SECRET_KEY = os.getenv("SECRET_KEY", "")

# Obtém o diretório onde este arquivo está localizado.
APP_DIR = Path(__file__).resolve().parent

# Configura o diretório de templates HTML da aplicação.
templates = Jinja2Templates(directory=APP_DIR / "templates")


# ============================================================
# 3. INICIALIZAÇÃO DA APLICAÇÃO FASTAPI
# ============================================================

# Cria a instância principal da API.
app = FastAPI(title="3D Fáil API")


# ============================================================
# 4. MIDDLEWARES
# ============================================================

# Configura o gerenciamento de sessões dos usuários.
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="lax",
    https_only=False,
    max_age=60 * 60 * 8,  # Duração da sessão: 8 horas.
)


# ============================================================
# 5. ARQUIVOS ESTÁTICOS
# ============================================================

# Disponibiliza arquivos CSS, JavaScript e imagens.
# Esses arquivos poderão ser acessados pela rota /static.
app.mount(
    "/static",
    StaticFiles(directory=APP_DIR / "static"),
    name="static"
)


# ============================================================
# 6. ROTAS DA APLICAÇÃO
# ============================================================

# Rota principal: página inicial do sistema.
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    # Dados enviados para o template HTML.
    contexto = {
        "ambiente": APP_ENV,
    }

    # Renderiza o arquivo login.html com os dados do contexto.
    return templates.TemplateResponse(
        request,
        "login.html",
        contexto
    )


@app.post("/login")
async def login(request: Request, usuario_form: Usuario):
    email = usuario_form.email
    senha = usuario_form.senha
    

    usuario_banco = buscarUsuarioPorEmail(email)

    if usuario_banco is None:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    senha_bytes = senha.encode("utf-8")
    hash_bytes = usuario_banco["password_hash"].encode("utf-8")
    
    senha_final = bcrypt.checkpw(senha_bytes, hash_bytes)
    
    #DEBUG    
    if not senha_final:
        print(f"Usuário encontrado: {email}")
        print(f"Senha válida: {senha_final}")
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        
    
    request.session["usuario_id"] = usuario_banco["id"]
    request.session["usuario_nome"] = usuario_banco["name"]

    return Response(status_code=status.HTTP_200_OK)
    
    
@app.get("/dashboard")
async def dashboard(request: Request):
    verificarSessao(request)
    
    if not verificarSessao(request):
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_302_FOUND
        )
    


    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context= contexto
    )


@app.get("/gerenciar")
async def gerenciar(request: Request):
    verificarSessao(request)

    if not verificarSessao(request):
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_302_FOUND
        )

    contexto = {
        "nome": "Matheus",
        "idade": 18
    }
    return templates.TemplateResponse(
        request=request,
        name="gerenciar.html",
        context= contexto
    )


@app.get("/session")
async def verificarSessao(request: Request):
    if request.session.get("usuario_nome") is None:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return Response(status_code=status.HTTP_200_OK)
    
    
#ROTAS DE DEBUG
@app.get("/usuario_banco")
async def buscarUsuario(email: str = Query(...)):
    usuario = buscarUsuarioPorEmail(email)
    
    return {
        "id":usuario["id"],
        "nome":usuario["name"],
        "email":usuario["email"],
        "senha_hash":usuario["password_hash"]
    }


# ============================================================
# 7. FUNÇÕES AUXILIARES
# ============================================================


def gerar_hash(senha_original):
    """Gera um hash bcrypt a partir de uma senha em texto plano."""
    senha_bytes = senha_original.encode("utf-8")
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt)

    # Senha convertida para hash
    return senha_hash.decode("utf-8")


def obter_ip_local():
    """
    Identifica o endereço IP local da máquina.

    Utiliza um socket UDP para identificar qual interface
    de rede seria utilizada para alcançar um endereço externo.
    Não envia dados para esse endereço.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

    except OSError:
        return "Não foi possível identificar o IP"


# ============================================================
# 8. INICIALIZAÇÃO DO SERVIDOR
# ============================================================

# Executa este bloco somente quando o arquivo for iniciado
# diretamente, evitando iniciar outro servidor em importações.
if __name__ == "__main__":

    # Identifica o IP local da máquina.
    ip = obter_ip_local()

    # Exibe as informações de acesso ao sistema.
    print("\n" + "=" * 45)
    print("       SERVIDOR 3D FÁCIL")
    print("=" * 45)
    print(f" Local:  http://localhost:8000")
    print(f" Rede:   http://{ip}:8000")
    print("=" * 45 + "\n", flush=True)

    # Tenta iniciar o servidor Uvicorn.
    try:
        subprocess.run(
            [
                "uvicorn",
                "app:app",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            cwd=APP_DIR,
            check=True
        )

    # Erro quando o executável Uvicorn não é encontrado.
    except FileNotFoundError:
        print("[ERRO] Uvicorn não encontrado.")
        print("Verifique se está instalado no ambiente virtual:")
        print("pip install uvicorn")

    # Erro quando o processo Uvicorn termina com código diferente de zero.
    except subprocess.CalledProcessError as erro:
        print("\n[ERRO] O servidor Uvicorn encerrou com falha.")
        print(f"Código de saída: {erro.returncode}")
        print("Verifique as mensagens acima para identificar a causa.")

    # Permite encerrar o servidor utilizando CTRL + C.
    except KeyboardInterrupt:
        print("\n[INFO] Servidor encerrado pelo usuário.")

    # Captura outros erros inesperados.
    except Exception as erro:
        print(
            f"\n[ERRO INESPERADO] "
            f"{type(erro).__name__}: {erro}"
        )
