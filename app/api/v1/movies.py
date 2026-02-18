from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_moderator
from app.db.session import get_db
from app.schemas.movies import (
    CertificationBase,
    CertificationResponse,
    DirectorBase,
    DirectorResponse,
    GenreBase,
    GenreResponse,
    MovieDetailResponse,
    MovieShortResponse,
    PaginatedMoviesResponse,
    StarBase,
    StarResponse,
)
from app.services import movies as movies_service

router = APIRouter(prefix="/movies", tags=["Movies"])


# -------------------------
# Public catalog endpoints
# -------------------------


@router.get(
    "",
    response_model=PaginatedMoviesResponse,
    summary="Browse movie catalog",
)
async def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    q: str | None = None,
    year: int | None = None,
    imdb_min: float | None = None,
    imdb_max: float | None = None,
    certification_id: int | None = None,
    genre_id: int | None = None,
    director_id: int | None = None,
    star_id: int | None = None,
    sort_by: str = Query("year", pattern="^(price|year|imdb|votes)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedMoviesResponse:
    total, items = await movies_service.list_movies(
        db,
        page=page,
        page_size=page_size,
        q=q,
        year=year,
        imdb_min=imdb_min,
        imdb_max=imdb_max,
        certification_id=certification_id,
        genre_id=genre_id,
        director_id=director_id,
        star_id=star_id,
        sort_by=sort_by,  # type: ignore[arg-type]
        order=order,  # type: ignore[arg-type]
    )

    return PaginatedMoviesResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[
            MovieShortResponse(
                id=m.id,
                uuid=m.uuid,
                name=m.name,
                year=m.year,
                time=m.time,
                imdb=m.imdb,
                price=m.price,
                certification=CertificationResponse(
                    id=m.certification.id,
                    name=m.certification.name,
                ),
            )
            for m in items
        ],
    )


@router.get(
    "/{movie_uuid}",
    response_model=MovieDetailResponse,
    summary="Get detailed information about a movie",
)
async def get_movie(
    movie_uuid: UUID,
    db: AsyncSession = Depends(get_db),
) -> MovieDetailResponse:
    movie = await movies_service.get_movie_by_uuid(db, movie_uuid)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    return MovieDetailResponse(
        id=movie.id,
        uuid=movie.uuid,
        name=movie.name,
        year=movie.year,
        time=movie.time,
        imdb=movie.imdb,
        votes=movie.votes,
        meta_score=movie.meta_score,
        gross=movie.gross,
        description=movie.description,
        price=movie.price,
        certification=CertificationResponse(
            id=movie.certification.id,
            name=movie.certification.name,
        ),
        genres=[GenreResponse(id=g.id, name=g.name) for g in movie.genres],
        directors=[DirectorResponse(id=d.id, name=d.name) for d in movie.directors],
        stars=[StarResponse(id=s.id, name=s.name) for s in movie.stars],
    )


# -------------------------
# Moderator CRUD endpoints
# -------------------------


@router.post(
    "/genres",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new genre (moderator only)",
)
async def create_genre(
    payload: GenreBase,
    db: AsyncSession = Depends(get_db),
    _moderator=Depends(require_moderator),
) -> GenreResponse:
    try:
        entity = await movies_service.create_genre(db, payload.name)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Genre already exists")
    return GenreResponse(id=entity.id, name=entity.name)


@router.post(
    "/stars",
    response_model=StarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new star (moderator only)",
)
async def create_star(
    payload: StarBase,
    db: AsyncSession = Depends(get_db),
    _moderator=Depends(require_moderator),
) -> StarResponse:
    try:
        entity = await movies_service.create_star(db, payload.name)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Star already exists")
    return StarResponse(id=entity.id, name=entity.name)


@router.post(
    "/directors",
    response_model=DirectorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new director (moderator only)",
)
async def create_director(
    payload: DirectorBase,
    db: AsyncSession = Depends(get_db),
    _moderator=Depends(require_moderator),
) -> DirectorResponse:
    try:
        entity = await movies_service.create_director(db, payload.name)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Director already exists")
    return DirectorResponse(id=entity.id, name=entity.name)


@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new certification (moderator only)",
)
async def create_certification(
    payload: CertificationBase,
    db: AsyncSession = Depends(get_db),
    _moderator=Depends(require_moderator),
) -> CertificationResponse:
    try:
        entity = await movies_service.create_certification(db, payload.name)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Certification already exists")
    return CertificationResponse(id=entity.id, name=entity.name)
