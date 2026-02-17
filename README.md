# 🎬 Online Cinema API

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A **portfolio-ready backend API** for an online cinema platform built with **FastAPI**, featuring:

- JWT authentication (access + refresh tokens)
- Movies catalog with filtering and sorting
- Shopping cart and order workflow
- Stripe payments
- Celery background jobs
- Dockerized environment
- CI/CD with GitHub Actions

---

## ✨ Features

### 🔐 Accounts
- Registration with email activation
- Password reset via email
- JWT authentication (access + refresh tokens)
- User roles:
  - **User**
  - **Moderator**
  - **Admin**

---

### 🎬 Movies
- Paginated catalog
- Filtering by:
  - year
  - IMDb rating
  - genre
  - director
  - star
- Sorting:
  - price
  - year
  - votes
- Moderator CRUD:
  - movies
  - genres
  - stars
  - directors
  - certifications

---

### 🛒 Cart
- One cart per user
- Add/remove movies
- Prevent duplicates
- Clear cart
- Admin cart inspection

---

### 📦 Orders
- Create order from cart
- Cancel order
- Order history
- Stored prices at order time

---

### 💳 Payments
- Stripe checkout sessions
- Webhook-based payment confirmation
- Payment history
- Admin filters

---

## 🧱 Architecture

```mermaid
flowchart LR
    Client -->|HTTP| FastAPI
    FastAPI --> Postgres[(PostgreSQL)]
    FastAPI --> Redis[(Redis)]
    FastAPI --> MinIO[(MinIO S3)]
    FastAPI --> Stripe[(Stripe API)]

    Celery --> Redis
    Celery --> Postgres
🗂 Project Structure
app/
 ├── api/
 │   └── v1/
 │       ├── accounts.py
 │       ├── movies.py
 │       ├── cart.py
 │       ├── orders.py
 │       ├── payments.py
 │       └── router.py
 │
 ├── core/
 │   ├── config.py
 │   ├── security.py
 │   └── emails.py
 │
 ├── db/
 │   ├── models/
 │   └── session.py
 │
 ├── schemas/
 ├── services/
 ├── workers/
 └── main.py
🚀 Quickstart (Docker)
1. Clone the repository
git clone https://github.com/your-username/online-cinema-api.git
cd online-cinema-api
2. Create .env
Example:

POSTGRES_DB=cinema
POSTGRES_USER=cinema
POSTGRES_PASSWORD=cinema
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY=supersecret
JWT_ALGORITHM=HS256

STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
3. Run with Docker Compose
docker compose up --build
Services:

Service	URL
API	http://localhost:8000
MailHog	http://localhost:8025
MinIO	http://localhost:9001
📚 API Documentation
Docs are protected.

Steps:

Register user:

POST /api/v1/accounts/register
Activate account via email.

Login:

POST /api/v1/accounts/login
Use access token in Swagger:

Authorization: Bearer <access_token>
Open:

http://localhost:8000/docs
🔁 Main User Flow
Register

Activate account

Login

Browse movies

Add movies to cart

Create order

Pay via Stripe

Receive confirmation

🧪 Testing
Run tests:

pytest
CI pipeline includes:

flake8

mypy

pytest

coverage

⚙️ Tech Stack
Backend: FastAPI, SQLAlchemy (async)

DB: PostgreSQL

Auth: JWT

Payments: Stripe

Storage: MinIO (S3-compatible)

Background jobs: Celery + Redis

Containerization: Docker, Docker Compose

Dependency management: Poetry

CI/CD: GitHub Actions

📄 License
MIT License.


---

## PR Description (GitHub)

**Title**
Add final portfolio README with architecture diagram and quickstart


**Description**
This PR adds a final, portfolio-ready README.

Main additions:

Project overview with badges

Feature breakdown by domain (Accounts, Movies, Cart, Orders, Payments)

Architecture diagram (Mermaid)

Project structure section

Docker quickstart guide

API documentation usage steps

Main user flow

Tech stack section

This finalizes the project for portfolio presentation.