from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.orders import OrderStatusEnum
from app.repositories import (
    CartItemRepository,
    CartRepository,
    MovieRepository,
    OrderItemRepository,
    OrderRepository,
)


async def create_order_from_cart(db: AsyncSession, user_id: int):
    cart = await CartRepository.get_by_user_id(db, user_id)
    if cart is None or not cart.items:
        raise ValueError("Cart is empty")

    movie_ids = [i.movie_id for i in cart.items]
    movies = []
    for mid in movie_ids:
        m = await MovieRepository.get_by_id(db, mid)
        if m is None:
            # exclude deleted/unavailable movies
            continue
        movies.append(m)

    if not movies:
        raise ValueError("No available movies to order")

    total = Decimal("0.00")
    for m in movies:
        total += Decimal(str(m.price))

    order = await OrderRepository.create(
        db,
        user_id=user_id,
        status=OrderStatusEnum.pending,
        total_amount=total,
    )

    for m in movies:
        await OrderItemRepository.create(
            db,
            order_id=order.id,
            movie_id=m.id,
            price_at_order=m.price,
        )

    # clear cart
    await CartItemRepository.delete_for_cart(db, cart.id)
    await db.flush()

    return order


async def list_orders(db: AsyncSession, user_id: int):
    return await OrderRepository.list_for_user(db, user_id)


async def get_order(db: AsyncSession, user_id: int, order_id: int):
    return await OrderRepository.get_for_user(db, user_id, order_id)


async def cancel_order(db: AsyncSession, user_id: int, order_id: int) -> None:
    order = await OrderRepository.get_for_user(db, user_id, order_id)
    if order is None:
        raise ValueError("Order not found")

    if order.status != OrderStatusEnum.pending:
        raise ValueError("Only pending orders can be canceled")

    order.status = OrderStatusEnum.canceled
    await db.flush()
