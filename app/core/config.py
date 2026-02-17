from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Online Cinema API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"

    # Later:
    # DATABASE_URL: str
    # JWT_SECRET_KEY: str
    # JWT_ACCESS_TTL_MINUTES: int = 15
    # JWT_REFRESH_TTL_DAYS: int = 14

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
