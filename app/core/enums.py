from __future__ import annotations

from enum import Enum


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class MovieSortField(str, Enum):
    price = "price"
    year = "year"
    imdb = "imdb"
    votes = "votes"


class PaymentStatus(str, Enum):
    successful = "successful"
    canceled = "canceled"
    refunded = "refunded"
