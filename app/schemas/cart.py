from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CartAddItemRequest(BaseModel):
    movie_id: int = Field(ge=1)


class CartRemoveItemRequest(BaseModel):
    movie_id: int = Field(ge=1)


class CartItemResponse(BaseModel):
    movie_id: int
    movie_uuid: UUID
    title: str
    year: int
    price: Decimal
    added_at: str  # ISO string


class CartResponse(BaseModel):
    user_id: int
    items: list[CartItemResponse]
    total_amount: Decimal
