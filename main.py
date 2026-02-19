# ~~~~~~~~~~~~~~~~~~~ Start do FastAPI (-Imports-) ~~~~~~~~~~~~~~~~~~~ #

import secrets

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# region ~~~~~~~~~~~~~~~~~~~ Database ( SQLite / SQLAlchemy ~~~~~~~~~~~~~~~~~~~ #

DATABASE_URL = "sqlite:///./biblioteca.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# endregion

# ~~~~~~~~~~~~~~~~~~~ Session (-Dependency-) ~~~~~~~~~~~~~~~~~~~ #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ~~~~~~~~~~~~~~~~~~~ FastAPI (-Docs-) ~~~~~~~~~~~~~~~~~~~ #
app = FastAPI(
    title="Biblioteca",
    description="API de Biblioteca",
    version="1.0.0",
    contact= {"name": "Igor", "email": "igormoser@outlook.com"}
)

# ~~~~~~~~~~~~~~~~~~~ Security (-HTTP Basic-) ~~~~~~~~~~~~~~~~~~~ #

LOGIN = "admin"
PASSWORD = "admin"

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    login_correct = secrets.compare_digest(credentials.username, LOGIN)
    password_correct = secrets.compare_digest(credentials.password, PASSWORD)

    if not (login_correct and password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username

# ~~~~~~~~~~~~~~~~~~~ ORM Models ~~~~~~~~~~~~~~~~~~~ #

class Livro(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True)
    titulo = Column(String, index=True)
    autor = Column(String, index=True)
    ano = Column(Integer)

Base.metadata.create_all(bind=engine)

# ~~~~~~~~~~~~~~~~~~~ Schemas (-Pydantic-) ~~~~~~~~~~~~~~~~~~~ #

class CriarLivro(BaseModel):
    titulo: str
    autor: str
    ano: int

class AtualizarLivro(BaseModel):
    titulo: str
    autor: str
    ano: int

# ~~~~~~~~~~~~~~~~~~~ Paginação ~~~~~~~~~~~~~~~~~~~ #

@app.get("/livros", dependencies=[Depends(authenticate_user)])
def get_livros(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    total = db.query(Livro).count()

    livros_db = (
        db.query(Livro)
        .order_by(Livro.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    livros_paginados = [
        {"id": livro.id, "titulo": livro.titulo, "autor": livro.autor, "ano": livro.ano}
        for livro in livros_db
    ]

    mensagem = "Biblioteca vazia!" if total == 0 else "Livros cadastrados."
    return {
        "mensagem": mensagem,
        "livros": livros_paginados,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# ~~~~~~~~~~~~~~~~~~~ CRUD ~~~~~~~~~~~~~~~~~~~ #

@app.get("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def get_livro(id_livro: int, db: Session = Depends(get_db)):
    livro_db = db.query(Livro).filter(Livro.id == id_livro).first()

    if livro_db is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    return {
        "id": livro_db.id,
        "titulo": livro_db.titulo,
        "autor": livro_db.autor,
        "ano": livro_db.ano,
    }

@app.post("/livros", dependencies=[Depends(authenticate_user)])
def post_livros(livro: CriarLivro, db: Session = Depends(get_db)):
    novo_livro = Livro(
        titulo=livro.titulo,
        autor=livro.autor,
        ano=livro.ano,
    )
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    return {
        "mensagem": "Livro criado com sucesso!",
        "livro": {
            "id": novo_livro.id,
            "titulo": novo_livro.titulo,
            "autor": novo_livro.autor,
            "ano": novo_livro.ano,
        },
    }

@app.put("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def put_livro(id_livro: int, livro: AtualizarLivro, db: Session = Depends(get_db)):

    livro_db = db.query(Livro).filter(Livro.id == id_livro).first()

    if livro_db is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    livro_db.titulo = livro.titulo
    livro_db.autor = livro.autor
    livro_db.ano = livro.ano

    db.commit()
    db.refresh(livro_db)

    return {
        "mensagem": "Livro atualizado com sucesso!",
        "livro": {
            "id": livro_db.id,
            "titulo": livro_db.titulo,
            "autor": livro_db.autor,
            "ano": livro_db.ano,
        },
    }

@app.delete("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def delete_livro(id_livro: int, db: Session = Depends(get_db)):
    livro_db = db.query(Livro).filter(Livro.id == id_livro).first()

    if livro_db is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    livro_removido = {
        "id": livro_db.id,
        "titulo": livro_db.titulo,
        "autor": livro_db.autor,
        "ano": livro_db.ano,
    }

    db.delete(livro_db)
    db.commit()

    return {
        "mensagem": "Livro deletado com sucesso!",
        "livro": livro_removido,
    }
