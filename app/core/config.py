from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Online Cinema API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"

    # Async DB URL for SQLAlchemy
    DATABASE_URL: str = "postgresql+asyncpg://cinema:cinema@db:5432/cinema"
    DB_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MINUTES: int = 15
    JWT_REFRESH_TTL_DAYS: int = 14

    # Stripe
    STRIPE_SECRET_KEY: str = "change-me"
    STRIPE_WEBHOOK_SECRET: str = "change-me"
    STRIPE_CURRENCY: str = "usd"
    STRIPE_SUCCESS_URL: str = "http://localhost:8000/success"
    STRIPE_CANCEL_URL: str = "http://localhost:8000/cancel"

    # Celery / Redis
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # SMTP (MailHog defaults)
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = False
    EMAIL_FROM: str = "no-reply@cinema.local"

    # MinIO (for avatars / media later)
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET: str = "cinema"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
