from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.core.enums import MovieSortField, SortOrder


class GenreBase(BaseModel):
    name: str


class GenreResponse(BaseModel):
    id: int
    name: str


class StarBase(BaseModel):
    name: str


class StarResponse(BaseModel):
    id: int
    name: str


class DirectorBase(BaseModel):
    name: str


class DirectorResponse(BaseModel):
    id: int
    name: str


class CertificationBase(BaseModel):
    name: str


class CertificationResponse(BaseModel):
    id: int
    name: str


class MovieCreateRequest(BaseModel):
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None = None
    gross: float | None = None
    description: str
    price: Decimal
    certification_id: int

    genre_ids: list[int] = Field(default_factory=list)
    director_ids: list[int] = Field(default_factory=list)
    star_ids: list[int] = Field(default_factory=list)


class MovieUpdateRequest(BaseModel):
    name: str | None = None
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
    uuid: Any
    name: str
    year: int
    time: int
    imdb: float
    price: Decimal
    certification: CertificationResponse


class MovieDetailResponse(BaseModel):
    id: int
    uuid: Any
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    price: Decimal
    certification: CertificationResponse
    genres: list[GenreResponse]
    directors: list[DirectorResponse]
    stars: list[StarResponse]


class PaginatedMoviesResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[MovieShortResponse]


# -------------------------
# Query schema with enums
# -------------------------

class MoviesListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=12, ge=1, le=100)

    q: str | None = None
    year: int | None = None
    imdb_min: float | None = None
    imdb_max: float | None = None

    certification_id: int | None = None
    genre_id: int | None = None
    director_id: int | None = None
    star_id: int | None = None

    sort_by: MovieSortField = MovieSortField.year
    order: SortOrder = SortOrder.desc
