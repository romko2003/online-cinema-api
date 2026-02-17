from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.db.models.accounts import User
from app.db.session import get_db
from app.schemas.cart import (
    CartAddItemRequest,
    CartRemoveItemRequest,
    CartResponse,
    CartItemResponse,
)
from app.services import cart as cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


def _build_cart_response(user_id: int, cart_items, movies) -> CartResponse:
    movies_by_id = {m.id: m for m in movies}

    items: list[CartItemResponse] = []
    for item in cart_items:
        m = movies_by_id.get(item.movie_id)
        if m is None:
            # Movie deleted/unavailable:
            # for cart we simply skip missing movie rows in response.
            continue

        items.append(
            CartItemResponse(
                movie_id=m.id,
                movie_uuid=m.uuid,
                title=m.name,
                year=m.year,
                price=m.price,
                added_at=item.added_at.isoformat(),
            )
        )

    total = cart_service.calc_total(
        [movies_by_id[i.movie_id] for i in cart_items if i.movie_id in movies_by_id]
    )
    return CartResponse(user_id=user_id, items=items, total_amount=total)


@router.get(
    "",
    response_model=CartResponse,
    summary="Get current user's cart",
    description="Returns cart items with movie info and total amount.",
)
async def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    cart, movies = await cart_service.get_cart_details(db, current_user.id)
    if cart is None:
        return CartResponse(user_id=current_user.id, items=[], total_amount=cart_service.calc_total([]))

    return _build_cart_response(current_user.id, cart.items, movies)


@router.post(
    "/add",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Add movie to cart",
    description="Adds a movie to the authenticated user's cart. Prevents duplicates and already purchased movies.",
)
async def add_to_cart(
    payload: CartAddItemRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await cart_service.add_movie_to_cart(db, current_user, payload.movie_id)
    except ValueError as e:
        msg = str(e).lower()
        raise HTTPException(
            status_code=404 if "not found" in msg else 400,
            detail=str(e),
        )
    return {"message": "Movie added to cart"}


@router.post(
    "/remove",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Remove movie from cart",
    description="Removes a movie from the authenticated user's cart.",
)
async def remove_from_cart(
    payload: CartRemoveItemRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await cart_service.remove_movie_from_cart(db, current_user, payload.movie_id)
    except ValueError as e:
        msg = str(e).lower()
        raise HTTPException(
            status_code=404 if "not in cart" in msg or "empty" in msg else 400,
            detail=str(e),
        )
    return {"message": "Movie removed from cart"}


@router.post(
    "/clear",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Clear cart",
    description="Clears all items from the authenticated user's cart.",
)
async def clear_my_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await cart_service.clear_cart(db, current_user)
    return {"message": "Cart cleared"}


# -------------------------
# Admin endpoint (analysis / troubleshooting)
# -------------------------

@router.get(
    "/admin/{user_id}",
    response_model=CartResponse,
    summary="Get user's cart (admin only)",
    description="Admin troubleshooting endpoint to inspect a specific user's cart.",
)
async def get_user_cart_admin(
    user_id: int,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    cart, movies = await cart_service.get_cart_details(db, user_id)
    if cart is None:
        return CartResponse(user_id=user_id, items=[], total_amount=cart_service.calc_total([]))

    return _build_cart_response(user_id, cart.items, movies)
