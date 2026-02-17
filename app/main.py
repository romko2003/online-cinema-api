from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse, Response

from app.api.deps import get_current_user
from app.api.v1.router import api_v1_router
from app.core.config import settings

OPENAPI_TAGS = [
    {
        "name": "System",
        "description": "Service health and internal system endpoints.",
    },
    {
        "name": "Accounts",
        "description": "Registration, activation, login, logout, password management, JWT refresh.",
    },
    {
        "name": "Movies",
        "description": "Public movie catalog and moderator CRUD for catalog entities.",
    },
    {
        "name": "Cart",
        "description": "Shopping cart operations for authenticated users (and admin troubleshooting endpoint).",
    },
    {
        "name": "Orders",
        "description": "Order creation from cart, listing, retrieving, canceling orders.",
    },
    {
        "name": "Payments",
        "description": "Stripe checkout session creation, webhook processing, and payments listing (admin filters included).",
    },
]

# Disable default docs and openapi routes; we will expose protected versions manually.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Portfolio-ready **Online Cinema API** built with FastAPI.\n\n"
        "Key features:\n"
        "- JWT auth (access/refresh)\n"
        "- Movies catalog with filtering/sorting\n"
        "- Cart → Orders → Stripe Payments\n"
        "- Docker Compose stack (Postgres/Redis/Celery/MinIO/MailHog)\n"
        "- CI/CD with GitHub Actions\n\n"
        "**Docs access is restricted** — you must be authenticated with a valid Bearer token."
    ),
    contact={
        "name": "Roman Azhniuk",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=OPENAPI_TAGS,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["System"], summary="Healthcheck")
async def healthcheck() -> dict:
    return {"status": "ok"}


def _build_openapi_schema() -> dict:
    schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=app.description,
        routes=app.routes,
    )

    # Optional: show server for local dev (nice for portfolio)
    schema.setdefault("servers", [])
    if not any(s.get("url") == "http://localhost:8000" for s in schema["servers"]):
        schema["servers"].append(
            {
                "url": "http://localhost:8000",
                "description": "Local development server",
            }
        )

    return schema


# -------------------------
# Protected OpenAPI schema
# -------------------------

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(_=Depends(get_current_user)) -> JSONResponse:
    return JSONResponse(_build_openapi_schema())


# -------------------------
# Protected Swagger UI / ReDoc
# -------------------------

@app.get("/docs", include_in_schema=False)
async def swagger_ui(_=Depends(get_current_user)) -> Response:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_ui(_=Depends(get_current_user)) -> Response:
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - ReDoc",
    )
