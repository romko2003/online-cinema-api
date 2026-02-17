from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.payments import Payment, PaymentItem
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    @classmethod
    async def list_for_user(cls, db: AsyncSession, user_id: int) -> list[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .options(selectinload(Payment.items))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def list_all(cls, db: AsyncSession) -> list[Payment]:
        stmt = (
            select(Payment)
            .order_by(Payment.created_at.desc())
            .options(selectinload(Payment.items))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


class PaymentItemRepository(BaseRepository[PaymentItem]):
    model = PaymentItem

    @classmethod
    async def list_for_payment(cls, db: AsyncSession, payment_id: int) -> list[PaymentItem]:
        res = await db.execute(select(PaymentItem).where(PaymentItem.payment_id == payment_id))
        return list(res.scalars().all())
