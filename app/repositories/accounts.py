from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.accounts import (
    ActivationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserGroup,
)

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> User | None:
        return await cls.get_one_by(db, email=email)

    @classmethod
    async def set_active(cls, db: AsyncSession, user: User, is_active: bool) -> None:
        user.is_active = is_active
        await db.flush()

    @classmethod
    async def update_password_hash(cls, db: AsyncSession, user: User, password_hash: str) -> None:
        user.hashed_password = password_hash
        await db.flush()


class UserGroupRepository(BaseRepository[UserGroup]):
    model = UserGroup

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str):
        return await cls.get_one_by(db, name=name)


class ActivationTokenRepository(BaseRepository[ActivationToken]):
    model = ActivationToken

    @classmethod
    async def get_by_token(cls, db: AsyncSession, token: str) -> ActivationToken | None:
        return await cls.get_one_by(db, token=token)

    @classmethod
    async def delete_for_user(cls, db: AsyncSession, user_id: int) -> int:
        return await cls.delete_where(db, cls.col("user_id") == user_id)

    @classmethod
    async def delete_expired(cls, db: AsyncSession, now: datetime) -> int:
        return await cls.delete_where(db, cls.col("expires_at") < now)


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    model = PasswordResetToken

    @classmethod
    async def get_by_token(cls, db: AsyncSession, token: str) -> PasswordResetToken | None:
        return await cls.get_one_by(db, token=token)

    @classmethod
    async def delete_for_user(cls, db: AsyncSession, user_id: int) -> int:
        return await cls.delete_where(db, cls.col("user_id") == user_id)

    @classmethod
    async def delete_expired(cls, db: AsyncSession, now: datetime) -> int:
        return await cls.delete_where(db, cls.col("expires_at") < now)


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    @classmethod
    async def get_by_token(cls, db: AsyncSession, token: str) -> RefreshToken | None:
        return await cls.get_one_by(db, token=token)

    @classmethod
    async def list_for_user(cls, db: AsyncSession, user_id: int) -> list[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def delete_by_token(cls, db: AsyncSession, token: str) -> int:
        return await cls.delete_where(db, cls.col("token") == token)

    @classmethod
    async def delete_expired(cls, db: AsyncSession, now: datetime) -> int:
        return await cls.delete_where(db, cls.col("expires_at") < now)
