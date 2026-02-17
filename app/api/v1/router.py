from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# Here we will plug accounts/movies/cart/orders/payments routers later.
# Example:
# router.include_router(accounts.router)


api_v1_router = router

