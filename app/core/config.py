from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Online Cinema API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cinema"
    DB_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
