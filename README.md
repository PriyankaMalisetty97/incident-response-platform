# Incident Response Platform

AI-powered incident response & root-cause assistant (backend).
**Status: Phase 1 – core incident management backend (in progress).**

## Done so far
- FastAPI app with `/health`
- PostgreSQL via SQLAlchemy (config from `.env`)
- `User` and `Incident` models, `Severity`/`Status` enums
- Incident CRUD: `POST/GET/PATCH/DELETE /incidents`
- Filtering (`severity`, `status`, `service`), pagination, validation, 404 handling
- Automated tests (pytest, in-memory SQLite)

## Next
Authentication (register/login/JWT) → Alembic migrations → error-handling polish → docs.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d          # starts PostgreSQL
uvicorn app.main:app --reload # http://localhost:8000/docs
pytest
```
