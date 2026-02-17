from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.movies import Certification, Director, Genre, Movie, Star


SortField = Literal["price", "year", "imdb", "votes"]
SortOrder = Literal["asc", "desc"]


async def get_movie_by_uuid(session: AsyncSession, movie_uuid: UUID) -> Movie | None:
    stmt = (
        select(Movie)
        .where(Movie.uuid == movie_uuid)
        .options(
            selectinload(Movie.certification),
            selectinload(Movie.genres),
            selectinload(Movie.directors),
            selectinload(Movie.stars),
        )
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def list_movies(
    session: AsyncSession,
    *,
    page: int,
    page_size: int,
    q: str | None = None,
    year: int | None = None,
    imdb_min: float | None = None,
    imdb_max: float | None = None,
    certification_id: int | None = None,
    genre_id: int | None = None,
    director_id: int | None = None,
    star_id: int | None = None,
    sort_by: SortField = "year",
    order: SortOrder = "desc",
) -> tuple[int, list[Movie]]:
    filters = []

    if q:
        like = f"%{q.strip()}%"
        filters.append(or_(Movie.name.ilike(like), Movie.description.ilike(like)))

    if year is not None:
        filters.append(Movie.year == year)

    if imdb_min is not None:
        filters.append(Movie.imdb >= imdb_min)

    if imdb_max is not None:
        filters.append(Movie.imdb <= imdb_max)

    if certification_id is not None:
        filters.append(Movie.certification_id == certification_id)

    stmt = (
        select(Movie)
        .options(selectinload(Movie.certification))
    )

    if filters:
        stmt = stmt.where(*filters)

    # join-based filters for M2M
    if genre_id is not None:
        stmt = stmt.join(Movie.genres).where(Genre.id == genre_id)

    if director_id is not None:
        stmt = stmt.join(Movie.directors).where(Director.id == director_id)

    if star_id is not None:
        stmt = stmt.join(Movie.stars).where(Star.id == star_id)

    # total count
    count_stmt = select(func.count(func.distinct(Movie.id)))
    count_stmt = count_stmt.select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    # sorting
    sort_col = {
        "price": Movie.price,
        "year": Movie.year,
        "imdb": Movie.imdb,
        "votes": Movie.votes,
    }[sort_by]

    stmt = stmt.distinct(Movie.id)
    if order == "asc":
        stmt = stmt.order_by(sort_col.asc())
    else:
        stmt = stmt.order_by(sort_col.desc())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = (await session.execute(stmt)).scalars().all()

    return total, items


async def create_entity(session: AsyncSession, entity: Genre | Star | Director | Certification) -> None:
    session.add(entity)
    await session.commit()


async def get_genre(session: AsyncSession, genre_id: int) -> Genre | None:
    res = await session.execute(select(Genre).where(Genre.id == genre_id))
    return res.scalar_one_or_none()


async def get_star(session: AsyncSession, star_id: int) -> Star | None:
    res = await session.execute(select(Star).where(Star.id == star_id))
    return res.scalar_one_or_none()


async def get_director(session: AsyncSession, director_id: int) -> Director | None:
    res = await session.execute(select(Director).where(Director.id == director_id))
    return res.scalar_one_or_none()


async def get_certification(session: AsyncSession, certification_id: int) -> Certification | None:
    res = await session.execute(select(Certification).where(Certification.id == certification_id))
    return res.scalar_one_or_none()


async def get_movie(session: AsyncSession, movie_id: int) -> Movie | None:
    stmt = (
        select(Movie)
        .where(Movie.id == movie_id)
        .options(
            selectinload(Movie.certification),
            selectinload(Movie.genres),
            selectinload(Movie.directors),
            selectinload(Movie.stars),
        )
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def delete_by_id(session: AsyncSession, entity) -> None:
    await session.delete(entity)
    await session.commit()
