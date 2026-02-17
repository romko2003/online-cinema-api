from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.cart import Cart, CartItem


async def get_cart_by_user_id(session: AsyncSession, user_id: int) -> Cart | None:
    stmt = (
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items))
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def create_cart(session: AsyncSession, user_id: int) -> Cart:
    cart = Cart(user_id=user_id)
    session.add(cart)
    await session.commit()
    await session.refresh(cart)
    return cart


async def add_item(session: AsyncSession, cart_id: int, movie_id: int) -> CartItem:
    item = CartItem(cart_id=cart_id, movie_id=movie_id)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_item(session: AsyncSession, cart_id: int, movie_id: int) -> CartItem | None:
    stmt = select(CartItem).where(CartItem.cart_id == cart_id, CartItem.movie_id == movie_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def remove_item(session: AsyncSession, item: CartItem) -> None:
    await session.delete(item)
    await session.commit()


async def clear_cart(session: AsyncSession, cart: Cart) -> None:
    # cascade delete-orphan on relationship will remove items if we clear the list
    cart.items.clear()
    await session.commit()
