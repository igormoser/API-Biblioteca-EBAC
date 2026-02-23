# API Biblioteca (FastAPI + Compose + Poetry) — EBAC

Este repositório contém uma aplicação **FastAPI** empacotada com **Compose** (compatível com **Docker Compose** e **Podman Compose**), usando **Poetry** para gerenciar dependências.

A API sobe com **hot reload** (modo desenvolvimento) e usa **SQLite** como banco local.

---

## Stack
- FastAPI
- Uvicorn (server ASGI)
- Poetry (dependências)
- Compose (Docker Compose **ou** Podman Compose)
- Engine de containers (Docker **ou** Podman)
- SQLite (arquivo local)

---

## Requisitos (escolha UMA opção)

### Opção A — Podman (Windows + WSL2) — foco do módulo de containers
- Windows com **WSL2**
- **Podman** instalado (Podman Desktop é opcional)
- **podman machine** funcionando (ambiente Linux/VM para executar containers)
- **Podman Compose** disponível via comando `podman compose`

> **Importante (Windows/Podman):** antes de rodar o projeto, garanta que a máquina do Podman está iniciada (veja a seção “Podman (Windows) — primeiro uso”).

### Opção B — Docker
- Docker Desktop no Windows
- Docker Compose (comando `docker compose`)

> **Windows/Docker:** recomenda-se Docker Desktop com backend **WSL2** habilitado.

---

## Como clonar
```bash
git clone https://github.com/igormoser/API-Biblioteca-EBAC.git
cd API-Biblioteca-EBAC
```

---

## Podman (Windows) — primeiro uso

### 1) Criar e iniciar a máquina do Podman
> Execute no PowerShell (ou terminal do PyCharm), uma única vez:

```bash
podman machine init
podman machine start
```

Verificar status:
```bash
podman machine ls
podman info
```

> Se `podman info` falhar, normalmente é porque a machine não está iniciada.

---

## Como executar com Compose (modo desenvolvimento)

### Usando Podman Compose
Subir a aplicação:
```bash
podman compose up --build -d
```

Acompanhar logs:
```bash
podman compose logs -f
```

Parar e remover containers:
```bash
podman compose down
```

### Usando Docker Compose
Subir a aplicação:
```bash
docker compose up --build -d
```

Acompanhar logs:
```bash
docker compose logs -f
```

Parar e remover containers:
```bash
docker compose down
```

---

## Como acessar
- Documentação Swagger: http://localhost:8000/docs  
- Documentação Redoc: http://localhost:8000/redoc (se habilitado)

---

## Autenticação
A aplicação usa credenciais definidas por variáveis de ambiente no `docker-compose.yml`:

- `LOGIN=admin`
- `PASSWORD=admin`

> **Importante:** essas credenciais são apenas para desenvolvimento. Em produção, altere para valores fortes.

---

## Variáveis de ambiente
As variáveis necessárias já estão definidas no `docker-compose.yml` (não é necessário `.env` para rodar):
| Variável | Padrão | Para que serve |
|---|---:|---|
| `LOGIN` | `admin` | Usuário para autenticação |
| `PASSWORD` | `admin` | Senha para autenticação |
| `DATABASE_URL` | `sqlite:///./biblioteca.db` | URL de conexão do banco |
| `PYTHONUNBUFFERED` | `1` | Logs sem buffer (melhor para containers) |

### Como alterar as variáveis
Você pode editar diretamente o `docker-compose.yml` e subir novamente:

**Podman:**
```bash
podman compose up --build -d
```

**Docker:**
```bash
docker compose up --build -d
```

Opcionalmente, você pode criar um `.env` para sobrescrever (se preferir esse padrão), mas **não é obrigatório**.

---

## Banco de dados e persistência (SQLite)
O banco é um arquivo SQLite definido por:
- `DATABASE_URL=sqlite:///./biblioteca.db`

Como existe este volume no compose:
- `.:/app`

…o arquivo `biblioteca.db` **fica dentro do diretório do projeto** e tende a **persistir no seu host** (Windows/Linux/macOS) como um arquivo local.

### Resetar o banco (se necessário)
Se quiser “zerar” o banco, pare os containers e apague o arquivo:

**Podman:**
```bash
podman compose down
# apague o arquivo biblioteca.db (na raiz do projeto)
podman compose up --build -d
```

**Docker:**
```bash
docker compose down
# apague o arquivo biblioteca.db (na raiz do projeto)
docker compose up --build -d
```

---

## Observações de desenvolvimento
O container executa o Uvicorn com:
- `--reload` (hot reload)
- volume montado `.:/app`

Isso é ideal para desenvolvimento: qualquer alteração no código reflete automaticamente.

> **Produção:** normalmente você removeria `--reload` e não montaria o volume do projeto no container.

---

## Troubleshooting (erros comuns)

### Podman: “Cannot connect” / machine não iniciada
Garanta que a machine está rodando:
```bash
podman machine start
podman info
```

### Podman Compose não encontrado
Se `podman compose` não existir no seu ambiente, verifique sua instalação do Podman/Podman Desktop e atualize.

> Em alguns setups antigos, o comando alternativo pode ser `podman-compose`, mas o padrão recomendado no módulo é `podman compose`.

### Porta 8000 já está em uso
Troque a porta do host no `docker-compose.yml`:
```yml
ports:
  - "8001:8000"
```
Acesse: http://localhost:8001/docs

### Docker não inicia / WSL não instalado (Windows)
- Garanta que o WSL2 está habilitado
- No Docker Desktop, confirme backend WSL2

### API sobe mas dá erro
Veja logs detalhados:

**Podman:**
```bash
podman compose logs -f
```

**Docker:**
```bash
docker compose logs -f
```

---

## Comandos úteis

### Podman
Ver status dos containers:
```bash
podman compose ps
```

Rebuild completo (quando mudar dependências):
```bash
podman compose up --build -d
```

Parar e limpar:
```bash
podman compose down
```

### Docker
Ver status dos containers:
```bash
docker compose ps
```

Rebuild completo (quando mudar dependências):
```bash
docker compose up --build -d
```

Parar e limpar:
```bash
docker compose down
```
