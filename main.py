# ~~~~~~~~~~~~~~~~~~~ Start do FastAPI ~~~~~~~~~~~~~~~~~~~ #

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

# ~~~~~~~~~~~~~~~~~~~ DOCS ~~~~~~~~~~~~~~~~~~~ #
app = FastAPI(
    title="Biblioteca",
    description="API de Biblioteca",
    version="1.0.0",
    contact= {"name": "Igor", "email": "igormoser@outlook.com"}
)

# ~~~~~~~~~~~~~~~~~~~ Security ~~~~~~~~~~~~~~~~~~~ #

LOGIN = "admin"
PASSWORD = "admin"

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    login_correct = secrets.compare_digest(credentials.username, LOGIN)
    password_correct = secrets.compare_digest(credentials.password, PASSWORD)
    if not (login_correct and password_correct):
        raise HTTPException(status_code=401,
                            detail="Credenciais inválidas.",
                            headers={"WWW-Authenticate": "Basic"}
                            )
    return credentials.username

# ~~~~~~~~~~~~~~~~~~~ Classes ~~~~~~~~~~~~~~~~~~~ #

biblioteca_livros: dict[int, dict] = {}

class CriarLivro(BaseModel):
    id: int
    nome: str
    autor: str
    ano: int

class AtualizarLivro(BaseModel):
    nome: str
    autor: str
    ano: int

# ~~~~~~~~~~~~~~~~~~~ Paginação ~~~~~~~~~~~~~~~~~~~ #

@app.get("/livros", dependencies=[Depends(authenticate_user)])
def get_livros(skip: int = 0, limit: int = 10):

    livros_lista = list(biblioteca_livros.values())
    livros_lista.sort(key=lambda livro: livro["id"])

    livros_paginados = livros_lista[skip: skip + limit]

    mensagem = "Biblioteca vazia!" if not biblioteca_livros else "Livros cadastrados."
    return {
        "mensagem": mensagem,
        "livros": livros_paginados,
        "total": len(livros_lista),
        "skip": skip,
        "limit": limit
    }

# ~~~~~~~~~~~~~~~~~~~ CRUD ~~~~~~~~~~~~~~~~~~~ #
@app.get("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def get_livro(id_livro: int):
    if id_livro not in biblioteca_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    return biblioteca_livros[id_livro]

@app.post("/livros", dependencies=[Depends(authenticate_user)])
def post_livros(livro: CriarLivro):
    if livro.id in biblioteca_livros:
        raise HTTPException(status_code=409, detail="Já existe um livro com este ID.")

    biblioteca_livros[livro.id] = livro.model_dump()

    return biblioteca_livros[livro.id]

@app.put("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def put_livro(id_livro: int, livro: AtualizarLivro):
    if id_livro not in biblioteca_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    livro_atual = biblioteca_livros[id_livro]
    livro_atual['nome'] = livro.nome
    livro_atual['autor'] = livro.autor
    livro_atual['ano'] = livro.ano

    return {
        "mensagem": "Livro atualizado com sucesso!",
        "livro": livro_atual
    }

@app.delete("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def delete_livro(id_livro: int):
    if id_livro not in biblioteca_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    livro_removido = biblioteca_livros.pop(id_livro)

    return {
        "mensagem": "Livro deletado com sucesso!",
        "livro": livro_removido
    }
