# Docker development stack

This project ships with a full local stack:
- FastAPI API container
- Postgres 16
- Redis 7
- Celery worker + Celery beat
- MailHog (SMTP + UI)
- MinIO (S3-compatible)

## Quick start

1) Create `.env` from example:
```bash
cp .env.example .env
 
Start everything:

docker compose up --build
API: http://localhost:8000
MailHog UI: http://localhost:8025
MinIO Console: http://localhost:9001 (default user/pass: minioadmin/minioadmin)

Migrations
Migrations run automatically on container startup via docker/entrypoint.sh.

Celery
Worker: cinema_celery_worker

Beat: cinema_celery_beat

Beat schedule includes cleanup of expired activation/reset tokens every 10 minutes.

Stripe webhook (optional)
Use Stripe CLI:

stripe listen --forward-to localhost:8000/api/v1/payments/webhook
Stop
docker compose down
To remove volumes (DB data):

docker compose down -v

---

## Commit 6
### `chore: add minio client dependency for future media uploads`

**Files changed**
- `pyproject.toml` (updated)

---

### `pyproject.toml` (updated, повний файл)
```toml
[tool.poetry]
name = "online-cinema"
version = "0.1.0"
description = "Online Cinema API (FastAPI) - portfolio-ready project"
authors = ["Roman Azhniuk"]
readme = "README.md"
packages = [{ include = "app" }]

[tool.poetry.dependencies]
python = ">=3.11,<3.13"
fastapi = "^0.115.0"
uvicorn = { extras = ["standard"], version = "^0.30.0" }
pydantic = "^2.8.2"
pydantic-settings = "^2.4.0"
python-dotenv = "^1.0.1"

# DB
sqlalchemy = "^2.0.32"
asyncpg = "^0.29.0"
alembic = "^1.13.2"

# Security
bcrypt = "^4.1.3"
python-jose = { extras = ["cryptography"], version = "^3.3.0" }

# Payments
stripe = "^10.10.0"

# MinIO (S3-compatible) client (for later avatar/media uploads)
minio = "^7.2.8"

[tool.poetry.group.dev.dependencies]
ruff = "^0.6.3"
mypy = "^1.11.1"
pytest = "^8.3.2"
pytest-asyncio = "^0.23.8"
httpx = "^0.27.0"

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "B", "UP"]
ignore = []

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_any_generics = true
no_implicit_optional = true

[tool.pytest.ini_options]
testpaths = ["app/tests"]
asyncio_mode = "auto"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
