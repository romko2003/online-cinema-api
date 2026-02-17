from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_password_complexity,
    verify_password,
)
from app.db.models.accounts import (
    ActivationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserGroup,
    UserGroupEnum,
)

ACTIVATION_TTL_HOURS = 24
PASSWORD_RESET_TTL_HOURS = 2


def _utcnow_naive() -> datetime:
    # DB at this stage stores naive DateTime; keep consistent across models/migrations.
    return datetime.utcnow()


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> str:
    result = await session.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("User already exists")

    validate_password_complexity(password)

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
    expires_at = _utcnow_naive() + timedelta(hours=ACTIVATION_TTL_HOURS)

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

    if token.expires_at < _utcnow_naive():
        raise ValueError("Token expired")

    user = token.user
    user.is_active = True

    await session.delete(token)
    await session.commit()


async def login_user(session: AsyncSession, email: str, password: str) -> tuple[str, str]:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("Invalid credentials")

    if not user.is_active:
        raise ValueError("Account is not active")

    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    access = create_access_token(subject=user.email)
    refresh, refresh_exp = create_refresh_token(subject=user.email)

    session.add(
        RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=refresh_exp.replace(tzinfo=None),
        )
    )
    await session.commit()
    return access, refresh


async def refresh_access_token(session: AsyncSession, refresh_token: str) -> tuple[str, str]:
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    stored = result.scalar_one_or_none()
    if stored is None:
        raise ValueError("Invalid refresh token")

    if stored.expires_at < _utcnow_naive():
        await session.delete(stored)
        await session.commit()
        raise ValueError("Refresh token expired")

    user = stored.user
    if not user.is_active:
        raise ValueError("Account is not active")

    # Rotate refresh token
    await session.delete(stored)
    await session.flush()

    new_access = create_access_token(subject=user.email)
    new_refresh, new_refresh_exp = create_refresh_token(subject=user.email)

    session.add(
        RefreshToken(
            user_id=user.id,
            token=new_refresh,
            expires_at=new_refresh_exp.replace(tzinfo=None),
        )
    )
    await session.commit()

    return new_access, new_refresh


async def logout_user(session: AsyncSession, refresh_token: str) -> None:
    await session.execute(delete(RefreshToken).where(RefreshToken.token == refresh_token))
    await session.commit()


async def change_password(
    session: AsyncSession,
    user: User,
    old_password: str,
    new_password: str,
) -> None:
    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Old password is incorrect")

    validate_password_complexity(new_password)

    user.hashed_password = hash_password(new_password)
    await session.commit()


async def request_password_reset(session: AsyncSession, email: str) -> str | None:
    """
    Returns token if reset is possible, otherwise None.

    Security note: endpoints should respond with a generic message either way.
    """
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    # invalidate previous token (unique by user_id)
    await session.execute(
        delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
    )
    await session.flush()

    token_str = secrets.token_urlsafe(32)
    expires_at = _utcnow_naive() + timedelta(hours=PASSWORD_RESET_TTL_HOURS)

    session.add(
        PasswordResetToken(
            user_id=user.id,
            token=token_str,
            expires_at=expires_at,
        )
    )
    await session.commit()
    return token_str


async def confirm_password_reset(session: AsyncSession, token_str: str, new_password: str) -> None:
    validate_password_complexity(new_password)

    result = await session.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token_str)
    )
    token = result.scalar_one_or_none()
    if token is None:
        raise ValueError("Invalid token")

    if token.expires_at < _utcnow_naive():
        await session.delete(token)
        await session.commit()
        raise ValueError("Token expired")

    user = token.user
    user.hashed_password = hash_password(new_password)

    # revoke all refresh tokens (optional but правильний security)
    await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))

    await session.delete(token)
    await session.commit()
