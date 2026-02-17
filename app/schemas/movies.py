from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class GenreBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GenreResponse(GenreBase):
    id: int


class StarBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class StarResponse(StarBase):
    id: int


class DirectorBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class DirectorResponse(DirectorBase):
    id: int


class CertificationBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CertificationResponse(CertificationBase):
    id: int


class MovieCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None = None
    gross: float | None = None
    description: str
    price: Decimal

    certification_id: int
    genre_ids: list[int] = []
    director_ids: list[int] = []
    star_ids: list[int] = []


class MovieUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    year: int | None = None
    time: int | None = None
    imdb: float | None = None
    votes: int | None = None
    meta_score: float | None = None
    gross: float | None = None
    description: str | None = None
    price: Decimal | None = None

    certification_id: int | None = None
    genre_ids: list[int] | None = None
    director_ids: list[int] | None = None
    star_ids: list[int] | None = None


class MovieShortResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    year: int
    time: int
    imdb: float
    price: Decimal
    certification: CertificationResponse


class MovieDetailResponse(MovieShortResponse):
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    genres: list[GenreResponse]
    directors: list[DirectorResponse]
    stars: list[StarResponse]


class PaginatedMoviesResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[MovieShortResponse]
