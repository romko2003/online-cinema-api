from __future__ import annotations

from decimal import Decimal

import stripe
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.models.orders import Order, OrderStatusEnum
from app.db.models.payments import Payment, PaymentItem, PaymentStatusEnum


def _money_to_cents(amount: Decimal) -> int:
    return int((amount * Decimal("100")).quantize(Decimal("1")))


async def create_stripe_checkout_session(
    session: AsyncSession,
    *,
    user_id: int,
    order_id: int,
) -> str:
    stmt = (
        select(Order)
        .where(and_(Order.id == order_id, Order.user_id == user_id))
        .options(selectinload(Order.items))
    )
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()

    if order is None:
        raise ValueError("Order not found")

    if order.status != OrderStatusEnum.pending:
        raise ValueError("Only pending orders can be paid")

    # Revalidate totals before payment
    total = Decimal("0.00")
    for item in order.items:
        total += Decimal(str(item.price_at_order))

    order.total_amount = total
    await session.commit()

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout = stripe.checkout.Session.create(
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
        line_items=[
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "unit_amount": _money_to_cents(total),
                    "product_data": {"name": f"Order #{order.id}"},
                },
                "quantity": 1,
            }
        ],
        metadata={
            "order_id": str(order.id),
            "user_id": str(user_id),
        },
    )

    return checkout.url  # type: ignore[return-value]


async def _mark_order_paid_and_create_payment(
    session: AsyncSession,
    *,
    order_id: int,
    user_id: int,
    external_payment_id: str | None,
    amount: Decimal,
) -> None:

    stmt = (
        select(Order)
        .where(and_(Order.id == order_id, Order.user_id == user_id))
        .options(selectinload(Order.items))
    )
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()
    if order is None:
        return

    if order.status == OrderStatusEnum.paid:
        return

    if order.status != OrderStatusEnum.pending:
        return

    payment = Payment(
        user_id=user_id,
        order_id=order_id,
        status=PaymentStatusEnum.successful,
        amount=amount,
        external_payment_id=external_payment_id,
    )
    session.add(payment)
    await session.flush()

    for oi in order.items:
        session.add(
            PaymentItem(
                payment_id=payment.id,
                order_item_id=oi.id,  # OrderItem.id
                price_at_payment=oi.price_at_order,
            )
        )

    order.status = OrderStatusEnum.paid
    await session.commit()


async def process_stripe_webhook(
    session: AsyncSession,
    *,
    payload: bytes,
    signature: str,
) -> tuple[str, int]:
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return "Invalid webhook signature", 400

    event_type = event.get("type")

    if event_type == "checkout.session.completed":
        data = event["data"]["object"]
        metadata = data.get("metadata", {}) or {}

        order_id = int(metadata.get("order_id", "0") or "0")
        user_id = int(metadata.get("user_id", "0") or "0")

        amount_total = data.get("amount_total")
        amount = Decimal("0.00")
        if isinstance(amount_total, int):
            amount = (Decimal(amount_total) / Decimal("100")).quantize(Decimal("0.01"))

        external_id = data.get("payment_intent") or data.get("id")

        if order_id > 0 and user_id > 0:
            await _mark_order_paid_and_create_payment(
                session,
                order_id=order_id,
                user_id=user_id,
                external_payment_id=str(external_id) if external_id else None,
                amount=amount,
            )

        return "Processed", 200

    return "Ignored", 200
