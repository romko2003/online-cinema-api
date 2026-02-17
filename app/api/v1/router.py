from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.cart import router as cart_router
from app.api.v1.movies import router as movies_router

router = APIRouter()
router.include_router(accounts_router)
router.include_router(movies_router)
router.include_router(cart_router)

api_v1_router = router
