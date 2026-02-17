from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.orders import Order, OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    @classmethod
    async def list_for_user(cls, db: AsyncSession, user_id: int) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .options(selectinload(Order.items))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def get_for_user(cls, db: AsyncSession, user_id: int, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id, Order.id == order_id)
            .options(selectinload(Order.items))
        )
        res = await db.execute(stmt)
        return res.scalars().first()


class OrderItemRepository(BaseRepository[OrderItem]):
    model = OrderItem

    @classmethod
    async def list_for_order(cls, db: AsyncSession, order_id: int) -> list[OrderItem]:
        res = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
        return list(res.scalars().all())
