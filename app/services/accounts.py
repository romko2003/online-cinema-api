from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.accounts import ActivationToken, User, UserGroup, UserGroupEnum
from app.core.security import hash_password


ACTIVATION_TTL_HOURS = 24


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> str:
    # check existing
    result = await session.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("User already exists")

    group_result = await session.execute(
        select(UserGroup).where(UserGroup.name == UserGroupEnum.USER)
    )
    group = group_result.scalar_one()

    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=False,
        group_id=group.id,
    )
    session.add(user)
    await session.flush()

    token_str = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=ACTIVATION_TTL_HOURS)

    token = ActivationToken(
        user_id=user.id,
        token=token_str,
        expires_at=expires_at,
    )
    session.add(token)

    await session.commit()
    return token_str


async def activate_user(session: AsyncSession, token_str: str) -> None:
    result = await session.execute(
        select(ActivationToken).where(ActivationToken.token == token_str)
    )
    token = result.scalar_one_or_none()

    if not token:
        raise ValueError("Invalid token")

    if token.expires_at < datetime.utcnow():
        raise ValueError("Token expired")

    user = token.user
    user.is_active = True

    await session.delete(token)
    await session.commit()
