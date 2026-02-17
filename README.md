# Online Cinema (FastAPI) — Portfolio Project

A backend API for an online cinema platform: registration & activation, JWT auth, movies catalog, cart, orders, Stripe payments, background tasks, Docker, CI/CD.

## Tech stack (planned)
- FastAPI
- PostgreSQL (later)
- SQLAlchemy + Alembic (later)
- Celery + Redis (later)
- MinIO (later)
- Stripe (later)
- GitHub Actions CI/CD (later)

## Project structure (current)
online-cinema/
app/
main.py
api/
v1/
router.py
core/
config.py
logging.py
exceptions.py


## Local run (dev)
### 1) Install deps

poetry install

### 2) Run server
poetry run uvicorn app.main:app --reload


### 3) Check health
Open:

GET /health

GET /docs

### Lint & tests
poetry run ruff check .
poetry run mypy .
poetry run pytest -q