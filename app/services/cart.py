from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.accounts import User
from app.db.models.cart import Cart
from app.db.models.movies import Movie
from app.db.repositories import cart as cart_repo


async def _get_or_create_cart(session: AsyncSession, user_id: int) -> Cart:
    cart = await cart_repo.get_cart_by_user_id(session, user_id)
    if cart is not None:
        return cart
    return await cart_repo.create_cart(session, user_id)


async def _movie_exists(session: AsyncSession, movie_id: int) -> Movie | None:
    stmt = select(Movie).where(Movie.id == movie_id).options(selectinload(Movie.certification))
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def _is_movie_purchased(session: AsyncSession, user_id: int, movie_id: int) -> bool:
    """
    Full check will be implemented in PR #8 (Orders) using paid OrderItems.
    For now we keep a strict placeholder: nothing is considered purchased.
    """
    _ = session, user_id, movie_id
    return False


async def add_movie_to_cart(session: AsyncSession, user: User, movie_id: int) -> None:
    movie = await _movie_exists(session, movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    if await _is_movie_purchased(session, user.id, movie_id):
        raise ValueError("Movie already purchased")

    cart = await _get_or_create_cart(session, user.id)

    existing_item = await cart_repo.get_item(session, cart.id, movie_id)
    if existing_item is not None:
        raise ValueError("Movie already in cart")

    await cart_repo.add_item(session, cart.id, movie_id)


async def remove_movie_from_cart(session: AsyncSession, user: User, movie_id: int) -> None:
    cart = await cart_repo.get_cart_by_user_id(session, user.id)
    if cart is None:
        raise ValueError("Cart is empty")

    item = await cart_repo.get_item(session, cart.id, movie_id)
    if item is None:
        raise ValueError("Movie not in cart")

    await cart_repo.remove_item(session, item)


async def clear_cart(session: AsyncSession, user: User) -> None:
    cart = await cart_repo.get_cart_by_user_id(session, user.id)
    if cart is None:
        return
    await cart_repo.clear_cart(session, cart)


async def get_cart_details(session: AsyncSession, user_id: int) -> tuple[Cart | None, list[Movie]]:
    """
    Returns cart and list of Movie entities corresponding to cart items.
    """
    cart = await cart_repo.get_cart_by_user_id(session, user_id)
    if cart is None:
        return None, []

    movie_ids = [i.movie_id for i in cart.items]
    if not movie_ids:
        return cart, []

    stmt = select(Movie).where(Movie.id.in_(movie_ids))
    res = await session.execute(stmt)
    movies = res.scalars().all()
    return cart, movies


def calc_total(movies: list[Movie]) -> Decimal:
    total = Decimal("0.00")
    for m in movies:
        total += Decimal(str(m.price))
    return total
