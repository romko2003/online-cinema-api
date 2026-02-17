from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.movies import Certification, Director, Genre, Movie, Star
from app.repositories.base import BaseRepository


class GenreRepository(BaseRepository[Genre]):
    model = Genre

    @classmethod
    async def list_all(cls, db: AsyncSession) -> list[Genre]:
        res = await db.execute(select(Genre).order_by(Genre.name.asc()))
        return list(res.scalars().all())


class StarRepository(BaseRepository[Star]):
    model = Star

    @classmethod
    async def list_all(cls, db: AsyncSession) -> list[Star]:
        res = await db.execute(select(Star).order_by(Star.name.asc()))
        return list(res.scalars().all())


class DirectorRepository(BaseRepository[Director]):
    model = Director

    @classmethod
    async def list_all(cls, db: AsyncSession) -> list[Director]:
        res = await db.execute(select(Director).order_by(Director.name.asc()))
        return list(res.scalars().all())


class CertificationRepository(BaseRepository[Certification]):
    model = Certification

    @classmethod
    async def list_all(cls, db: AsyncSession) -> list[Certification]:
        res = await db.execute(select(Certification).order_by(Certification.name.asc()))
        return list(res.scalars().all())


class MovieRepository(BaseRepository[Movie]):
    model = Movie

    @classmethod
    async def get_by_uuid(cls, db: AsyncSession, movie_uuid: UUID) -> Movie | None:
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
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    def _base_list_stmt(cls) -> Select:
        return (
            select(Movie)
            .options(selectinload(Movie.certification))
        )

    @classmethod
    async def count_movies(cls, db: AsyncSession, stmt: Select) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        res = await db.execute(count_stmt)
        return int(res.scalar() or 0)

    @classmethod
    async def list_movies(cls, db: AsyncSession, stmt: Select) -> list[Movie]:
        res = await db.execute(stmt)
        return list(res.scalars().all())
