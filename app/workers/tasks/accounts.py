from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete

from app.db.models.accounts import ActivationToken, PasswordResetToken
from app.db.session import AsyncSessionLocal
from app.workers.celery_app import celery_app


@celery_app.task
def cleanup_expired_activation_tokens() -> None:
    import asyncio

    async def _cleanup() -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(ActivationToken).where(ActivationToken.expires_at < datetime.utcnow())
            )
            await session.commit()

    asyncio.run(_cleanup())


@celery_app.task
def cleanup_expired_password_reset_tokens() -> None:
    import asyncio

    async def _cleanup() -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(PasswordResetToken).where(PasswordResetToken.expires_at < datetime.utcnow())
            )
            await session.commit()

    asyncio.run(_cleanup())
