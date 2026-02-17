from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.accounts import User
from app.db.models.movies import Movie
from app.repositories import CartItemRepository, CartRepository, MovieRepository


def calc_total(movies: list[Movie]) -> Decimal:
    total = Decimal("0.00")
    for m in movies:
        total += Decimal(str(m.price))
    return total


async def get_cart_details(db: AsyncSession, user_id: int):
    cart = await CartRepository.get_by_user_id(db, user_id)
    if cart is None:
        return None, []

    movie_ids = [i.movie_id for i in cart.items]
    if not movie_ids:
        return cart, []

    res = await db.execute(select(Movie).where(Movie.id.in_(movie_ids)))
    movies = res.scalars().all()
    return cart, movies


async def add_movie_to_cart(db: AsyncSession, user: User, movie_id: int) -> None:
    movie = await MovieRepository.get_by_id(db, movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    cart = await CartRepository.get_by_user_id(db, user.id)
    if cart is None:
        cart = await CartRepository.create_for_user(db, user.id)

    existing = await CartItemRepository.get_one(db, cart.id, movie_id)
    if existing is not None:
        raise ValueError("Movie already in cart")

    await CartItemRepository.create(db, cart_id=cart.id, movie_id=movie_id)
    await db.flush()


async def remove_movie_from_cart(db: AsyncSession, user: User, movie_id: int) -> None:
    cart = await CartRepository.get_by_user_id(db, user.id)
    if cart is None:
        raise ValueError("Cart is empty")

    existing = await CartItemRepository.get_one(db, cart.id, movie_id)
    if existing is None:
        raise ValueError("Movie not in cart")

    await db.delete(existing)
    await db.flush()


async def clear_cart(db: AsyncSession, user: User) -> None:
    cart = await CartRepository.get_by_user_id(db, user.id)
    if cart is None:
        return

    await CartItemRepository.delete_for_cart(db, cart.id)
    await db.flush()
