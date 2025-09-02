# VidaPlus

## Descrição

VidaPlus é uma API para sistema de gestão de saúde construída com **Python**, **FastAPI** e **SQLAlchemy**. Ela fornece endpoints para gerenciar usuários, agendamentos, unidades, leitos, suprimentos e internações, com controle de acesso baseado em *roles*.

## Funcionalidades

* **Gerenciamento de Usuários:** Criação e administração de contas com diferentes perfis (ADMIN, PACIENTE, PROFISSIONAL\_DE\_SAÚDE).
* **Gerenciamento de Agendamentos:** Agendamento, cancelamento e gerenciamento de consultas e exames.
* **Gerenciamento de Unidades:** Administração de unidades de saúde (hospitais, clínicas, etc).
* **Gerenciamento de Leitos:** Controle de leitos por tipo e status.
* **Gerenciamento de Suprimentos:** Controle de estoque de materiais e insumos médicos.
* **Gerenciamento de Internações:** Registro de admissões e altas de pacientes.
* **Controle de Acesso Baseado em Roles:** Restrições de acesso aos endpoints conforme o perfil do usuário.

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* Alembic (migrações de banco)
* PostgreSQL (padrão, mas configurável para outros bancos)
* pytest (testes)
* **uv** (recomendado para instalação, execução e gerenciamento do projeto)
* Docker / Docker Compose

## Pré-requisitos

* **Python 3.12+**

* **uv**: Gerenciador recomendado para ambiente virtual, instalação e execução.
  Instale com:

  ```bash
  pip install uv
  ```

* (Opcional) **Docker e Docker Compose** para execução via containers.

## Configuração e Instalação

### Local (sem Docker)

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/araujogusta/vidaplus.git
   cd vidaplus
   ```

2. **Crie e ative um ambiente virtual com uv:**

   ```bash
   uv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**

   ```bash
   uv pip install .
   ```

4. **Configure o banco de dados:**

   * Crie um banco PostgreSQL (ou outro de sua escolha).
   * Ajuste o arquivo `.env` com a URL de conexão:

   ```
   DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
   ```

5. **Execute as migrações:**

   ```bash
   alembic upgrade head
   ```

### Com Docker

O projeto já inclui um arquivo `docker-compose.yml` para facilitar a execução da aplicação e do banco de dados.

1. **Suba os containers:**

   ```bash
   docker-compose up --build
   ```

2. O serviço estará disponível em `http://localhost:8000`.

> **Observação:** O Docker Compose já cuida da criação do banco e da aplicação, simplificando a configuração inicial.

## Executando a Aplicação

* **Local (desenvolvimento com uv):**

  ```bash
  uv pip install -r requirements.txt  # Se necessário
  fastapi dev vidaplus/run.py
  ```

* **Docker:**

  ```bash
  docker compose up
  ```

## Autenticação

A API usa autenticação via token Bearer. Exemplo de cabeçalho:

```
Authorization: Bearer <seu_token>
```

## Endpoints da API

* `/api/usuarios`: Gestão de usuários (ADMIN necessário para criação).
* `/api/profissionais`: Gestão de profissionais de saúde.
* `/api/agendamentos`: Gestão de agendamentos.
* `/api/unidades`: Gestão de unidades (ADMIN necessário para criação).
* `/api/leitos`: Gestão de leitos (ADMIN necessário para criação).
* `/api/estoque`: Gestão de suprimentos (ADMIN necessário para criação).
* `/api/internacoes`: Gestão de internações (ADMIN necessário para criação).

## Testes

Execute com:

```bash
uv run task test
```

## Migrações do Banco

* **Criar nova migração:**

  ```bash
  alembic revision -m "descrição"
  ```
* **Aplicar migração:**

  ```bash
  alembic upgrade head
  ```
* **Reverter:**

  ```bash
  alembic downgrade <id_da_revisao>
  ```

## Modelos Principais

* **Usuário:** `id`, `name`, `email`, `password`, `role`, `created_at`
* **Agendamento:** `id`, `date_time`, `type`, `status`, `estimated_duration`, `location`, `notes`, `patient_id`, `professional_id`, `created_at`, `updated_at`
* **Unidade:** `id`, `name`, `address`
* **Leito:** `id`, `type`, `status`, `unit_id`
* **Suprimento:** `id`, `name`, `quantity`, `min_level`, `unit_id`
* **Internação:** `id`, `admitted_at`, `discharged_at`, `bed_id`, `patient_id`

