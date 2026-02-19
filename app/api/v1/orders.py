from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.accounts import User
from app.db.models.movies import Movie
from app.db.session import get_db
from app.schemas.orders import (
    CreateOrderResponse,
    OrderItemResponse,
    OrderResponse,
    OrdersListResponse,
)
from app.services import orders as orders_service

router = APIRouter(prefix="/orders", tags=["Orders"])


async def _movies_map(db: AsyncSession, movie_ids: list[int]) -> dict[int, Movie]:
    if not movie_ids:
        return {}
    res = await db.execute(select(Movie).where(Movie.id.in_(movie_ids)))
    movies = res.scalars().all()
    return {m.id: m for m in movies}


@router.post(
    "",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order from current cart",
    description="Creates a new order from the authenticated user's cart items.",
)
async def create_order(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreateOrderResponse:
    try:
        order = await orders_service.create_order_from_cart(db, current_user.id)
    except ValueError as e:
        msg = str(e).lower()
        raise HTTPException(status_code=400 if "not found" not in msg else 404, detail=str(e))

    return CreateOrderResponse(message="Order created", order_id=order.id)


@router.get(
    "",
    response_model=OrdersListResponse,
    summary="List current user's orders",
    description="Returns a list of orders with items and totals.",
)
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrdersListResponse:
    orders = await orders_service.list_orders(db, current_user.id)

    all_movie_ids: list[int] = []
    for o in orders:
        all_movie_ids.extend([i.movie_id for i in o.items])

    movies_by_id = await _movies_map(db, list(set(all_movie_ids)))

    items: list[OrderResponse] = []
    for o in orders:
        items.append(
            OrderResponse(
                id=o.id,
                status=o.status.value,
                created_at=o.created_at.isoformat(),
                total_amount=o.total_amount,
                items=[
                    OrderItemResponse(
                        movie_id=i.movie_id,
                        movie_uuid=movies_by_id[i.movie_id].uuid
                        if i.movie_id in movies_by_id
                        else None,  # type: ignore[arg-type]
                        title=movies_by_id[i.movie_id].name
                        if i.movie_id in movies_by_id
                        else "Unknown",
                        price_at_order=i.price_at_order,
                    )
                    for i in o.items
                ],
            )
        )

    return OrdersListResponse(items=items)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get current user's order by id",
    description="Returns detailed order information including items and stored prices.",
)
async def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    order = await orders_service.get_order(db, current_user.id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    movie_ids = [i.movie_id for i in order.items]
    movies_by_id = await _movies_map(db, movie_ids)

    return OrderResponse(
        id=order.id,
        status=order.status.value,
        created_at=order.created_at.isoformat(),
        total_amount=order.total_amount,
        items=[
            OrderItemResponse(
                movie_id=i.movie_id,
                movie_uuid=movies_by_id[i.movie_id].uuid if i.movie_id in movies_by_id else None,  # type: ignore[arg-type]
                title=movies_by_id[i.movie_id].name if i.movie_id in movies_by_id else "Unknown",
                price_at_order=i.price_at_order,
            )
            for i in order.items
        ],
    )


@router.post(
    "/{order_id}/cancel",
    response_model=dict,
    summary="Cancel current user's order",
    description="Cancels an order if cancellation rules allow it (e.g., before payment).",
)
async def cancel_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await orders_service.cancel_order(db, current_user.id, order_id)
    except ValueError as e:
        msg = str(e).lower()
        raise HTTPException(status_code=404 if "not found" in msg else 400, detail=str(e))

    return {"message": "Order canceled"}
