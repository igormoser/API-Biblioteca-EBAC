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

- Redis (cache e broker do Celery)
- Celery (filas/background jobs)
---

## Redis (Cache)

Este projeto usa **Redis** como **cache** para o endpoint `GET /livros`.

### Como funciona o cache
- A API tenta buscar a resposta no Redis antes de consultar o banco.
- A chave do cache é baseada na paginação:
  - `livros:skip=<skip>&limit=<limit>`
- O cache tem **TTL** (expiração) para evitar dados “eternos”.
- Após alterações (POST/PUT/DELETE), o cache é **invalidado** (apagamos as chaves `livros:*`) para evitar dados desatualizados.

### Endpoint de debug
Existe um endpoint para inspeção do cache e TTL:
- `GET /debug/redis`

> Dica: use este endpoint para confirmar que o TTL está diminuindo e que o cache é limpo após criar/atualizar/deletar um livro.

### Observação sobre o host do Redis
- Rodando **tudo via Compose**, o host do Redis normalmente é o nome do serviço: `redis`.
- Rodando a API **localmente** (PyCharm/Poetry) com Redis exposto na porta 6379, use `localhost`.

---

## Celery (Filas com Redis)

Este projeto também suporta **Celery** para executar tarefas em background usando o **Redis** como broker (fila) e, opcionalmente, como backend de resultados.

### Arquivos principais
- `celery_app.py`: cria o `celery_app` e configura broker/backend.
- `tasks.py`: define tarefas (tasks) do Celery.

### Rodando com Compose (Redis + API + Worker)
Para usar Celery, o compose deve subir **três serviços**:
- `redis`
- `app` (FastAPI)
- `worker` (Celery worker)

O worker é iniciado com um comando semelhante a:
```bash
poetry run celery -A celery_app:celery_app worker --loglevel=info
```

### Sobre tasks de exemplo
Durante o aprendizado, é comum existir `tasks.py` com exemplos (ex.: `somar`, `fatorial`) apenas para validar que o worker está executando tarefas. No projeto final, a ideia é substituir por tarefas úteis ao domínio (ex.: gerar relatórios, importações, notificações).

---

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

Acompanhar logs (todos os serviços):
```bash
podman compose logs -f
```

Acompanhar logs apenas do worker (Celery):
```bash
podman compose logs -f worker
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

Acompanhar logs (todos os serviços):
```bash
docker compose logs -f
```

Acompanhar logs apenas do worker (Celery):
```bash
docker compose logs -f worker
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


### Poetry: erro ao instalar `celery[redis]`
Em alguns ambientes, o Celery/Kombu impõe limite superior para a versão do pacote Python `redis`.
Se `poetry add "celery[redis]"` falhar por conflito de dependências, fixe o `redis` (biblioteca Python) em uma versão compatível e tente novamente:
```bash
poetry add "redis>=4.5.2,<6.5"
poetry add "celery[redis]"
```

### Podman Compose: “compose provider failed” (Windows)
Se o comando `podman compose` não estiver disponível e aparecer erro de provider, uma alternativa é instalar `podman-compose` via pip e rodar o executável instalado no seu usuário.

Exemplo (instalação):
```bash
python -m pip install --user podman-compose
```

Se o executável não estiver no PATH, use o caminho completo (ajuste o seu usuário/versão do Python):
```bash
%APPDATA%\Python\Python314\Scripts\podman-compose.exe up --build -d
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