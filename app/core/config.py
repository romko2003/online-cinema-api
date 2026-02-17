from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Online Cinema API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cinema"
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
