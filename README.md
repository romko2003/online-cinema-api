# Online Cinema API 🎬 (FastAPI)

A portfolio-ready backend for an online cinema platform: authentication, movie catalog, cart → orders → payments (Stripe), background jobs, and a clean layered architecture.

## ✨ Highlights

- **FastAPI + Async SQLAlchemy**
- **JWT auth (access + refresh)** + logout (revokes refresh token)
- **Email activation** (activation tokens expire) + password reset tokens
- **Roles & permissions**: USER / MODERATOR / ADMIN
- **Movies catalog**:
  - pagination, search, filters
  - sorting via **Enums** (Swagger dropdowns)
  - moderator CRUD for movies and dictionary entities
- **Cart**:
  - add/remove/clear
  - prevents duplicates
  - admin can view user carts (analysis/troubleshooting)
- **Orders**:
  - create from cart
  - list/get
  - cancel (before payment)
- **Payments (Stripe)**:
  - create checkout session
  - webhook handler
  - payments history
  - admin filters
- **Layered architecture**:
  - `api` → `services` → `repositories` → `db/models`
  - association tables migrated to full-fledged models (when needed)
- **Tests (pytest)** for main flows and edge cases
- Docker-ready setup (DB/Redis/Celery/etc. if enabled in your compose)

---

## 🧱 Tech Stack

- **FastAPI**
- **SQLAlchemy (async)**
- **Alembic migrations**
- **Pydantic**
- **Pytest**
- **Stripe** (checkout + webhook)
- (optional) Celery + Redis, MinIO, etc. depending on your docker-compose

---


🚀 Quickstart (Local)
1) Create .env
Create a .env in the project root.

Example (adjust values):

# App
APP_NAME=online-cinema
ENV=local
DEBUG=true

# DB
DATABASE_URL=postgresql+asyncpg://cinema:cinema@localhost:5432/cinema

# JWT
JWT_SECRET_KEY=change-me
JWT_ACCESS_TOKEN_TTL_MINUTES=15
JWT_REFRESH_TOKEN_TTL_DAYS=14

# Emails (dev)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=no-reply@example.com

# Stripe (dev)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
2) Install dependencies
If you use Poetry:

poetry install
poetry shell
Or if you use pip:

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3) Run migrations
alembic upgrade head
4) Start API
uvicorn app.main:app --reload
Open Swagger:

http://127.0.0.1:8000/docs

🐳 Docker (Typical)
If you have docker-compose configured:

docker compose up --build
Then run migrations inside the API container if needed:

docker compose exec api alembic upgrade head
🔐 API Overview (Main Endpoints)
Accounts
POST /api/v1/accounts/register

GET /api/v1/accounts/activate?token=...

POST /api/v1/accounts/login

POST /api/v1/accounts/refresh

POST /api/v1/accounts/logout

POST /api/v1/accounts/change-password

POST /api/v1/accounts/forgot-password

POST /api/v1/accounts/reset-password

Movies
GET /api/v1/movies

GET /api/v1/movies/{uuid}

Moderator:

POST /api/v1/movies

PUT /api/v1/movies/{id}

DELETE /api/v1/movies/{id}

dictionaries: genres/stars/directors/certifications

Cart
GET /api/v1/cart

POST /api/v1/cart/add

POST /api/v1/cart/remove

POST /api/v1/cart/clear

Admin:

GET /api/v1/cart/admin/{user_id}

Orders
POST /api/v1/orders

GET /api/v1/orders

GET /api/v1/orders/{id}

POST /api/v1/orders/{id}/cancel

Payments
POST /api/v1/payments/checkout-session

POST /api/v1/payments/webhook

GET /api/v1/payments

Admin:

GET /api/v1/payments/admin

✅ Tests
Run:

pytest -q

## 📁 Project Structure (high level)

```text
app/
  api/
    deps.py
    v1/
      accounts.py
      movies.py
      cart.py
      orders.py
      payments.py
      router.py
  core/
    enums.py
    emails.py
    security/...
  db/
    models/
      accounts.py
      movies.py
      cart.py
      orders.py
      payments.py
    migrations/
      env.py
      versions/
  repositories/
    accounts.py
    movies.py
    cart.py
    orders.py
    payments.py
  schemas/
    accounts.py
    movies.py
    cart.py
    orders.py
    payments.py
  services/
    accounts.py
    movies.py
    cart.py
    orders.py
    payments.py
  main.py
tests/
  test_cart_orders_payments_flow.py
  test_admin_and_edge_cases.py