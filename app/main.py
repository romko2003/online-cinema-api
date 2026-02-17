from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse, Response

from app.api.v1.router import api_v1_router
from app.api.deps import get_current_user
from app.core.config import settings

# disable default docs and openapi routes
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def healthcheck() -> dict:
    return {"status": "ok"}


# -------------------------
# Secured OpenAPI schema
# -------------------------

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(_=Depends(get_current_user)) -> JSONResponse:
    schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        routes=app.routes,
        description=(
            "Portfolio-ready Online Cinema API.\n\n"
            "Docs access is restricted: you must be authenticated with a valid Bearer token."
        ),
    )
    return JSONResponse(schema)


# -------------------------
# Secured Swagger UI
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
