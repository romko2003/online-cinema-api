from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.movies import Certification, Director, Genre, Movie, Star
from app.repositories import (
    CertificationRepository,
    DirectorRepository,
    GenreRepository,
    MovieRepository,
    StarRepository,
)


async def create_genre(db: AsyncSession, name: str) -> Genre:
    return await GenreRepository.create(db, name=name)


async def create_star(db: AsyncSession, name: str) -> Star:
    return await StarRepository.create(db, name=name)


async def create_director(db: AsyncSession, name: str) -> Director:
    return await DirectorRepository.create(db, name=name)


async def create_certification(db: AsyncSession, name: str) -> Certification:
    return await CertificationRepository.create(db, name=name)


async def get_movie_by_uuid(db: AsyncSession, movie_uuid: UUID) -> Movie | None:
    return await MovieRepository.get_by_uuid(db, movie_uuid)


def _apply_filters(
    stmt: Select,
    *,
    q: str | None,
    year: int | None,
    imdb_min: float | None,
    imdb_max: float | None,
    certification_id: int | None,
    genre_id: int | None,
    director_id: int | None,
    star_id: int | None,
) -> Select:
    # NOTE: filters that require joins can be implemented by repositories later.
    # For now we keep stmt-level filters minimal and stable.
    if q:
        stmt = stmt.where(Movie.name.ilike(f"%{q}%"))  # type: ignore[attr-defined]
    if year is not None:
        stmt = stmt.where(Movie.year == year)
    if imdb_min is not None:
        stmt = stmt.where(Movie.imdb >= imdb_min)
    if imdb_max is not None:
        stmt = stmt.where(Movie.imdb <= imdb_max)
    if certification_id is not None:
        stmt = stmt.where(Movie.certification_id == certification_id)

    # Relation filters (genre/director/star) require joins; keep for later extension.
    # You can implement them inside MovieRepository with explicit joins.
    if genre_id is not None:
        stmt = stmt.join(Movie.genres).where(Genre.id == genre_id)  # type: ignore[attr-defined]
    if director_id is not None:
        stmt = stmt.join(Movie.directors).where(Director.id == director_id)  # type: ignore[attr-defined]
    if star_id is not None:
        stmt = stmt.join(Movie.stars).where(Star.id == star_id)  # type: ignore[attr-defined]

    return stmt


async def list_movies(
    db: AsyncSession,
    *,
    page: int,
    page_size: int,
    q: str | None,
    year: int | None,
    imdb_min: float | None,
    imdb_max: float | None,
    certification_id: int | None,
    genre_id: int | None,
    director_id: int | None,
    star_id: int | None,
    sort_by: str,
    order: str,
) -> tuple[int, list[Movie]]:
    stmt = MovieRepository._base_list_stmt()
    stmt = _apply_filters(
        stmt,
        q=q,
        year=year,
        imdb_min=imdb_min,
        imdb_max=imdb_max,
        certification_id=certification_id,
        genre_id=genre_id,
        director_id=director_id,
        star_id=star_id,
    )

    sort_col = getattr(Movie, sort_by)
    stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

    total = await MovieRepository.count_movies(db, stmt)

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = await MovieRepository.list_movies(db, stmt)
    return total, items


async def create_movie(db: AsyncSession, payload) -> Movie:
    # payload is MovieCreateRequest or dict-like
    data = payload.dict() if hasattr(payload, "dict") else dict(payload)

    # Validate referenced entities exist (via repositories)
    cert = await CertificationRepository.get_by_id(db, data["certification_id"])
    if cert is None:
        raise ValueError("Invalid certification_id")

    genre_ids = data.get("genre_ids", [])
    director_ids = data.get("director_ids", [])
    star_ids = data.get("star_ids", [])

    genres = []
    for gid in genre_ids:
        g = await GenreRepository.get_by_id(db, gid)
        if g is None:
            raise ValueError("Invalid genre_ids")
        genres.append(g)

    directors = []
    for did in director_ids:
        d = await DirectorRepository.get_by_id(db, did)
        if d is None:
            raise ValueError("Invalid director_ids")
        directors.append(d)

    stars = []
    for sid in star_ids:
        s = await StarRepository.get_by_id(db, sid)
        if s is None:
            raise ValueError("Invalid star_ids")
        stars.append(s)

    movie = await MovieRepository.create(
        db,
        name=data["name"],
        year=data["year"],
        time=data["time"],
        imdb=data["imdb"],
        votes=data["votes"],
        meta_score=data.get("meta_score"),
        gross=data.get("gross"),
        description=data["description"],
        price=data["price"],
        certification_id=data["certification_id"],
    )

    movie.genres = genres
    movie.directors = directors
    movie.stars = stars

    await db.flush()
    return movie


async def update_movie(db: AsyncSession, movie_id: int, payload) -> Movie:
    movie = await MovieRepository.get_by_id(db, movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    data = payload.dict(exclude_unset=True) if hasattr(payload, "dict") else dict(payload)

    # scalar fields
    for key in ["name", "year", "time", "imdb", "votes", "meta_score", "gross", "description", "price"]:
        if key in data:
            setattr(movie, key, data[key])

    if "certification_id" in data:
        cert = await CertificationRepository.get_by_id(db, data["certification_id"])
        if cert is None:
            raise ValueError("Invalid certification_id")
        movie.certification_id = data["certification_id"]

    # relations (optional)
    if "genre_ids" in data:
        genres = []
        for gid in data["genre_ids"]:
            g = await GenreRepository.get_by_id(db, gid)
            if g is None:
                raise ValueError("Invalid genre_ids")
            genres.append(g)
        movie.genres = genres

    if "director_ids" in data:
        directors = []
        for did in data["director_ids"]:
            d = await DirectorRepository.get_by_id(db, did)
            if d is None:
                raise ValueError("Invalid director_ids")
            directors.append(d)
        movie.directors = directors

    if "star_ids" in data:
        stars = []
        for sid in data["star_ids"]:
            s = await StarRepository.get_by_id(db, sid)
            if s is None:
                raise ValueError("Invalid star_ids")
            stars.append(s)
        movie.stars = stars

    await db.flush()
    return movie


async def delete_movie(db: AsyncSession, movie_id: int) -> None:
    movie = await MovieRepository.get_by_id(db, movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    await db.delete(movie)
    await db.flush()
