from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def healthcheck() -> dict:
    return {"status": "ok"}
