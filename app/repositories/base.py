from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """
    Base repository with generic helpers.
    Child repositories must set: model = <SQLAlchemy model class>.
    """

    model: type[ModelT]

    @classmethod
    async def get_by_id(cls, db: AsyncSession, entity_id: Any) -> ModelT | None:
        res = await db.execute(select(cls.model).where(getattr(cls.model, "id") == entity_id))
        return res.scalars().first()

    @classmethod
    async def get_one_by(cls, db: AsyncSession, **filters: Any) -> ModelT | None:
        stmt = select(cls.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(cls.model, key) == value)
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    async def list_by(cls, db: AsyncSession, **filters: Any) -> list[ModelT]:
        stmt = select(cls.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(cls.model, key) == value)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def create(cls, db: AsyncSession, **data: Any) -> ModelT:
        entity = cls.model(**data)  # type: ignore[call-arg]
        db.add(entity)
        await db.flush()
        return entity

    @classmethod
    async def delete_where(cls, db: AsyncSession, *conditions: Any) -> int:
        res = await db.execute(delete(cls.model).where(*conditions))
        await db.flush()
        return int(res.rowcount or 0)

    @classmethod
    def col(cls, name: str) -> InstrumentedAttribute:
        return getattr(cls.model, name)
