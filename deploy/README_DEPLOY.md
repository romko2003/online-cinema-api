# Deploy to AWS EC2 (GitHub Actions - SSH)

This repository includes a simple "portfolio-friendly" deployment workflow that:
- SSH-es into an EC2 instance
- pulls `main`
- runs `docker compose up -d --build` using `deploy/docker-compose.prod.yml`

## Requirements on EC2
- Docker + Docker Compose installed
- A directory for the app, e.g. `/home/ubuntu/online-cinema`
- Repository cloned into that directory
- `.env` file created on the server (NOT committed)

## GitHub Secrets
Add these repository secrets:

- `EC2_HOST` - public IP or domain
- `EC2_USER` - e.g. `ubuntu`
- `EC2_SSH_KEY` - private key for SSH (PEM content)
- `EC2_PORT` - optional, default 22
- `EC2_APP_DIR` - app directory on server, e.g. `/home/ubuntu/online-cinema`

## First-time setup on EC2 (example)
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
newgrp docker

mkdir -p ~/online-cinema
cd ~/online-cinema
git clone <your_repo_url> .
cp .env.example .env
# edit .env for production
docker compose -f deploy/docker-compose.prod.yml up -d --build

Trigger

Push to main triggers deployment.


---

# PR Description (GitHub) — English (вкінці)

**Title**


Add CI/CD pipelines with GitHub Actions (quality checks, Docker build, EC2 deploy stub)


**Description**


This PR adds GitHub Actions workflows for continuous integration and a simple deployment stub.

CI:

Runs ruff lint + format check

Runs mypy type checking

Runs pytest with coverage

Uses Postgres + Redis services for integration-ready environment

Docker:

Builds Docker image on PR/push to ensure container build stays healthy

CD (stub):

Deploys on push to main via SSH to AWS EC2

Pulls latest main and restarts the stack with docker compose

Additional:

Added pytest-cov and .coveragerc for coverage reporting

Added deployment documentation under deploy/