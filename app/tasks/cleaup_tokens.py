from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.celery_app import celery
from app.core.config import settings
from app.db.models.accounts import ActivationToken, PasswordResetToken


def _engine() -> AsyncEngine:
    # DATABASE_URL is expected to be asyncpg URL
    return create_async_engine(settings.DATABASE_URL, echo=False, future=True)


async def _cleanup() -> dict:
    engine = _engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    now = datetime.now(timezone.utc)
    deleted_activation = 0
    deleted_reset = 0

    async with async_session() as session:
        res1 = await session.execute(
            delete(ActivationToken).where(ActivationToken.expires_at < now)
        )
        deleted_activation = int(res1.rowcount or 0)

        res2 = await session.execute(
            delete(PasswordResetToken).where(PasswordResetToken.expires_at < now)
        )
        deleted_reset = int(res2.rowcount or 0)

        await session.commit()

    await engine.dispose()
    return {
        "deleted_activation_tokens": deleted_activation,
        "deleted_password_reset_tokens": deleted_reset,
    }


@celery.task(name="app.tasks.cleanup_tokens.cleanup_expired_tokens")
def cleanup_expired_tokens() -> dict:
    """
    Celery task wrapper (sync) that runs async SQLAlchemy cleanup.
    """
    return asyncio.run(_cleanup())
