from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import OrderRepository, PaymentRepository


async def create_stripe_checkout_session(db: AsyncSession, user_id: int, order_id: int) -> str:
    """
    Repository-driven check that order exists and belongs to user.
    Stripe integration is implemented elsewhere; here we keep it minimal.
    """
    order = await OrderRepository.get_for_user(db, user_id, order_id)
    if order is None:
        raise ValueError("Order not found")

    if str(order.status.value) != "pending":
        raise ValueError("Only pending orders can be paid")

    # Stripe call is usually here; in tests we monkeypatch it.
    # Return placeholder; real integration should return actual checkout URL.
    return "https://checkout.stripe.com/"


async def process_stripe_webhook(db: AsyncSession, payload: bytes, signature: str) -> tuple[str, int]:
    """
    Stub webhook processor.
    In real implementation you:
    - verify signature via stripe.Webhook.construct_event
    - handle checkout.session.completed and payment_intent events
    - update Payment/Order records
    """
    # Keep minimal contract used in routes/tests
    _ = payload
    _ = signature
    return ("Webhook received", 200)
