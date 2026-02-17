from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_admin
from app.db.models.accounts import User
from app.db.models.payments import Payment
from app.db.session import get_db
from app.schemas.payments import (
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse,
    PaymentItemResponse,
    PaymentResponse,
    PaymentsAdminQuery,
    PaymentsListResponse,
)
from app.services import payments as payments_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/checkout-session", response_model=CreateCheckoutSessionResponse)
async def create_checkout_session(
    payload: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreateCheckoutSessionResponse:
    try:
        checkout_url = await payments_service.create_stripe_checkout_session(
            db,
            user_id=current_user.id,
            order_id=payload.order_id,
        )
    except ValueError as e:
        msg = str(e).lower()
        raise HTTPException(status_code=404 if "not found" in msg else 400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create Stripe checkout session")

    return CreateCheckoutSessionResponse(checkout_url=checkout_url)


@router.post("/webhook", response_model=dict)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()

    message, code = await payments_service.process_stripe_webhook(
        db,
        payload=payload,
        signature=stripe_signature,
    )

    return {"message": message, "status": code}


def _to_response(p: Payment) -> PaymentResponse:
    return PaymentResponse(
        id=p.id,
        order_id=p.order_id,
        created_at=p.created_at.isoformat(),
        status=p.status.value,
        amount=p.amount,
        external_payment_id=p.external_payment_id,
        items=[PaymentItemResponse(order_item_id=i.order_item_id, price_at_payment=i.price_at_payment) for i in p.items],
    )


@router.get("", response_model=PaymentsListResponse)
async def list_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentsListResponse:
    stmt = (
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .options(selectinload(Payment.items))
    )
    res = await db.execute(stmt)
    payments = res.scalars().all()
    return PaymentsListResponse(items=[_to_response(p) for p in payments])


@router.get("/admin", response_model=PaymentsListResponse)
async def list_payments_admin(
    query: PaymentsAdminQuery = Depends(),
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PaymentsListResponse:
    conditions = []

    if query.user_id is not None:
        conditions.append(Payment.user_id == query.user_id)

    if query.status_filter is not None:
        conditions.append(Payment.status == query.status_filter)

    if query.date_from:
        conditions.append(Payment.created_at >= datetime.fromisoformat(query.date_from))

    if query.date_to:
        conditions.append(Payment.created_at <= datetime.fromisoformat(query.date_to))

    stmt = select(Payment).order_by(Payment.created_at.desc()).options(selectinload(Payment.items))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    res = await db.execute(stmt)
    payments = res.scalars().all()
    return PaymentsListResponse(items=[_to_response(p) for p in payments])
