from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CreateCheckoutSessionRequest(BaseModel):
    order_id: int = Field(ge=1)


class CreateCheckoutSessionResponse(BaseModel):
    checkout_url: str


class PaymentItemResponse(BaseModel):
    order_item_id: int
    price_at_payment: Decimal


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    created_at: str
    status: str
    amount: Decimal
    external_payment_id: str | None
    items: list[PaymentItemResponse]


class PaymentsListResponse(BaseModel):
    items: list[PaymentResponse]
