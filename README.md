# Incident Response Platform

A backend API for reporting and managing software incidents. This is **Phase 1** of a larger project: an AI-powered incident response and root-cause assistant that will later search historical incidents and recent code changes, suggest likely root causes, and keep humans in control of important actions.

**Status:** Phase 1 (core incident management backend), nearly complete.

## Features

- **Incident management:** create, list, read, update and delete incidents
- **Controlled values:** severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and status (`OPEN`, `INVESTIGATING`, `RESOLVED`, `CLOSED`)
- **Filtering and pagination:** `GET /incidents?severity=CRITICAL&service=payment-service&limit=20`
- **Authentication:** user registration, login with JWT access tokens, bcrypt password hashing
- **Authorization:** all incident routes require login; only the creator can delete an incident
- **Validation and error handling:** invalid input returns 422, missing items 404, database outage 503, and unexpected errors return a safe 500 without leaking internals
- **Automated tests:** 26 pytest tests running against an in-memory database

## Architecture

```text
Client
  |  HTTP + JWT
  v
FastAPI
  routes/     HTTP only: parse request, return status codes
  services/   business logic and database queries
  schemas/    request/response validation (Pydantic)
  models/     database tables (SQLAlchemy)
  |
  v
PostgreSQL   (users, incidents)
```

## API overview

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | no | Health check |
| POST | `/auth/register` | no | Create an account |
| POST | `/auth/login` | no | Get an access token |
| GET | `/auth/me` | yes | Current user |
| POST | `/incidents` | yes | Create an incident |
| GET | `/incidents` | yes | List incidents (filters: `severity`, `status`, `service`; paging: `limit`, `offset`) |
| GET | `/incidents/{id}` | yes | Get one incident |
| PATCH | `/incidents/{id}` | yes | Update fields |
| DELETE | `/incidents/{id}` | yes (creator only) | Delete an incident |

Interactive docs are available at `/docs` once the server is running.

## Run locally

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --reload-dir app
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --reload-dir app
```

Then open http://127.0.0.1:8000/docs.

**Database.** The default is PostgreSQL (`docker compose up -d` starts one). Set `DATABASE_URL` in `.env` to match your setup. For a quick local try-out, `DATABASE_URL=sqlite:///./dev.db` also works.

**Secret key.** Replace `SECRET_KEY` in `.env` with a random value:
```
python -c "import secrets; print(secrets.token_hex(32))"
```

**Tests**
```
pytest
```

## Roadmap

1. Core incident management backend (this phase): Alembic migrations still to do
2. Event-driven workflow automation (n8n)
3. AI incident analysis (LangChain + LLM)
4. RAG and historical incident search
5. GitHub and Slack integrations
6. Human-in-the-loop approval
7. Docker and AWS deployment
8. Agents and MCP
