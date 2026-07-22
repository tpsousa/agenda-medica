# Agenda Médica

Desafio técnico da TimeSaver: aplicação web de login e consulta de agendamentos médicos.

## Descrição da solução

A aplicação segue o padrão **application factory** do Flask, organizada em blueprints:

- **`auth`** — tela de login (usuário/e-mail + senha), validação contra o SQLite e sessão do usuário.
- **`agenda`** — tela principal, endpoint interno que busca os agendamentos via HTTP em um serviço de API separado (mockado) e endpoint de busca/filtro.
- **`services/api_client.py`** — toda a comunicação HTTP e o tratamento de falhas da API ficam isolados aqui, com exceções específicas (`ApiUnavailableError`, `ApiInvalidResponseError`) capturadas nas rotas.

A tabela de agendamentos é renderizada com **Tabulator** no front-end, que consome o endpoint interno `/agenda/api/agendamentos` via `fetch`. A busca por paciente, CPF ou médico é feita no servidor (parâmetro `?q=`), mantendo a lógica de negócio fora do front-end.

O projeto inclui um **serviço de API mockado** (`mock_api/`), rodando como um segundo container, que simula o sistema de agendamentos com dados fixos e endpoints auxiliares para reproduzir cenários de falha (veja a seção Testes manuais dos cenários de falha).

## Tecnologias utilizadas

- Python 3.12 + Flask (aplicação principal e API mockada)
- Flask-SQLAlchemy + SQLite (persistência de usuários)
- Werkzeug (hash de senha)
- `requests` (integração HTTP com a API de agendamentos)
- Tabulator.js (tabela interativa no front-end, via CDN)
- Docker + Docker Compose
- Pytest (testes automatizados)

## Estrutura do projeto

```
agenda-medica/
├── app/
│   ├── auth/            # blueprint de login/logout
│   ├── agenda/           # blueprint da tela principal e endpoint de agendamentos
│   ├── services/          # cliente HTTP da API (com tratamento de falhas)
│   ├── templates/         # login.html, agenda.html, base.html
│   ├── static/css/        # estilos
│   ├── config.py, extensions.py, models.py, __init__.py
├── mock_api/              # serviço HTTP separado com os dados mockados
├── tests/                 # testes automatizados (pytest)
├── seed.py                # cria o banco e o usuário de teste
├── run.py                 # ponto de entrada da aplicação
├── entrypoint.sh           # seed + start, usado pelo container
├── Dockerfile, docker-compose.yml
└── requirements.txt
```

## Como executar com Docker (recomendado)

Pré-requisitos: Docker e Docker Compose instalados.

```bash
docker compose up --build
```

Este único comando sobe dois serviços:

- `web` — aplicação principal em **http://localhost:5000** (cria o banco e o usuário de teste automaticamente na inicialização, via `entrypoint.sh`)
- `mock-api` — API de agendamentos em **http://localhost:5001**

Acesse **http://localhost:5000** no navegador.

## Como executar sem Docker (terminal)

```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Em um terminal, suba a API mockada:
cd mock_api && pip install -r requirements.txt && python app.py

# Em outro terminal, na raiz do projeto:
python seed.py        # cria o banco e o usuário de teste
python run.py          # inicia a aplicação em http://localhost:5000
```

Por padrão a aplicação espera a API mockada em `http://localhost:5001` (configurável via variável de ambiente `API_BASE_URL`).

## Credenciais do usuário de teste

| Usuário | E-mail                     | Senha     |
|---------|-----------------------------|-----------|
| `admin` | `admin@timesaver.com.br`   | `admin123` |

Criado automaticamente por `seed.py` (executado pelo `entrypoint.sh` no Docker, ou manualmente fora dele).

## Exemplos de uso

1. Acesse `http://localhost:5000`, será redirecionado para o login.
2. Entre com `admin` / `admin123`.
3. A tela principal exibe a tabela de agendamentos, carregada automaticamente.
4. Digite um nome, CPF ou médico na busca para filtrar; se não houver correspondência, a tabela informa que nenhum registro foi encontrado.

## Testes manuais dos cenários de falha

A API mockada aceita o parâmetro `?simulate=` para reproduzir os cenários da Parte 2 do desafio sem precisar derrubar containers:

```bash
curl "http://localhost:5001/api/agendamentos?simulate=empty"    # nenhum agendamento
curl "http://localhost:5001/api/agendamentos?simulate=invalid"  # corpo não é JSON válido
curl "http://localhost:5001/api/agendamentos?simulate=missing"  # campos obrigatórios ausentes (descartados com aviso)
curl "http://localhost:5001/api/agendamentos?simulate=error"    # HTTP 500 (indisponibilidade)
```

Para testar via a aplicação principal, ajuste temporariamente `API_BASE_URL` do serviço `web` (ou pare o container `mock-api`) e recarregue a tela principal — a aplicação exibe uma mensagem amigável em vez de quebrar.

Credenciais inválidas: basta digitar uma senha incorreta na tela de login.

## Testes automatizados

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -v
```

Cobrem: login válido/inválido, campos vazios no login, listagem normal de agendamentos, indisponibilidade da API, busca sem correspondência e redirecionamento de usuário não autenticado.

## Decisões técnicas

- **SQLAlchemy** em vez de `sqlite3` puro, para manter o modelo de usuário organizado e facilitar testes com banco em memória.
- **Serviço de API separado** (em vez de dados mockados no mesmo processo), para refletir de forma mais realista uma integração HTTP de verdade — inclusive permitindo simular timeout, erro de conexão e respostas malformadas.
- **Busca no servidor**, não apenas no cliente: o endpoint `/agenda/api/agendamentos?q=` já filtra os dados, então a mesma lógica vale tanto para o carregamento inicial quanto para buscas subsequentes.
- **Registros incompletos são descartados, não travam a aplicação**: quando a API retorna um item sem algum campo obrigatório, ele é ignorado e logado, e o usuário recebe um aviso informativo em vez de um erro técnico.
- **Logging estruturado** em todos os pontos de falha (login inválido, erro de banco, indisponibilidade da API, resposta inválida, registros descartados), para facilitar o diagnóstico sem expor detalhes técnicos ao usuário final.

## Limitações conhecidas

- O usuário de teste é único; não há tela de cadastro (fora do escopo do desafio).
- A busca é por correspondência simples (substring), sem acentuação normalizada.
- O servidor de desenvolvimento do Flask é usado no container por simplicidade; para produção real, o recomendado seria um servidor WSGI como Gunicorn.
