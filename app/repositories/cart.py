from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.cart import Cart, CartItem
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    model = Cart

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: int) -> Cart | None:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    async def create_for_user(cls, db: AsyncSession, user_id: int) -> Cart:
        return await cls.create(db, user_id=user_id)


class CartItemRepository(BaseRepository[CartItem]):
    model = CartItem

    @classmethod
    async def get_one(cls, db: AsyncSession, cart_id: int, movie_id: int) -> CartItem | None:
        stmt = select(CartItem).where(CartItem.cart_id == cart_id, CartItem.movie_id == movie_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    async def list_for_cart(cls, db: AsyncSession, cart_id: int) -> list[CartItem]:
        res = await db.execute(select(CartItem).where(CartItem.cart_id == cart_id))
        return list(res.scalars().all())

    @classmethod
    async def delete_for_cart(cls, db: AsyncSession, cart_id: int) -> int:
        return await cls.delete_where(db, cls.col("cart_id") == cart_id)
