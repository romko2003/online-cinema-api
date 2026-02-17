from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.movies import Certification, Director, Genre, Movie, Star
from app.db.repositories import movies as repo
from app.schemas.movies import MovieCreateRequest, MovieUpdateRequest


async def list_movies(
    session: AsyncSession,
    *,
    page: int,
    page_size: int,
    q: str | None = None,
    year: int | None = None,
    imdb_min: float | None = None,
    imdb_max: float | None = None,
    certification_id: int | None = None,
    genre_id: int | None = None,
    director_id: int | None = None,
    star_id: int | None = None,
    sort_by: repo.SortField = "year",
    order: repo.SortOrder = "desc",
) -> tuple[int, list[Movie]]:
    return await repo.list_movies(
        session,
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
        sort_by=sort_by,
        order=order,
    )


async def get_movie_by_uuid(session: AsyncSession, movie_uuid: UUID) -> Movie | None:
    return await repo.get_movie_by_uuid(session, movie_uuid)


async def create_genre(session: AsyncSession, name: str) -> Genre:
    entity = Genre(name=name)
    await repo.create_entity(session, entity)
    return entity


async def create_star(session: AsyncSession, name: str) -> Star:
    entity = Star(name=name)
    await repo.create_entity(session, entity)
    return entity


async def create_director(session: AsyncSession, name: str) -> Director:
    entity = Director(name=name)
    await repo.create_entity(session, entity)
    return entity


async def create_certification(session: AsyncSession, name: str) -> Certification:
    entity = Certification(name=name)
    await repo.create_entity(session, entity)
    return entity


async def create_movie(session: AsyncSession, payload: MovieCreateRequest) -> Movie:
    certification = await repo.get_certification(session, payload.certification_id)
    if certification is None:
        raise ValueError("Certification not found")

    genres: list[Genre] = []
    for gid in payload.genre_ids:
        g = await repo.get_genre(session, gid)
        if g is None:
            raise ValueError(f"Genre not found: {gid}")
        genres.append(g)

    directors: list[Director] = []
    for did in payload.director_ids:
        d = await repo.get_director(session, did)
        if d is None:
            raise ValueError(f"Director not found: {did}")
        directors.append(d)

    stars: list[Star] = []
    for sid in payload.star_ids:
        s = await repo.get_star(session, sid)
        if s is None:
            raise ValueError(f"Star not found: {sid}")
        stars.append(s)

    movie = Movie(
        name=payload.name,
        year=payload.year,
        time=payload.time,
        imdb=payload.imdb,
        votes=payload.votes,
        meta_score=payload.meta_score,
        gross=payload.gross,
        description=payload.description,
        price=payload.price,
        certification_id=payload.certification_id,
        genres=genres,
        directors=directors,
        stars=stars,
    )
    session.add(movie)
    await session.commit()
    await session.refresh(movie)
    return movie


async def update_movie(session: AsyncSession, movie_id: int, payload: MovieUpdateRequest) -> Movie:
    movie = await repo.get_movie(session, movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    if payload.name is not None:
        movie.name = payload.name
    if payload.year is not None:
        movie.year = payload.year
    if payload.time is not None:
        movie.time = payload.time
    if payload.imdb is not None:
        movie.imdb = payload.imdb
    if payload.votes is not None:
        movie.votes = payload.votes
    if payload.meta_score is not None:
        movie.meta_score = payload.meta_score
    if payload.gross is not None:
        movie.gross = payload.gross
    if payload.description is not None:
        movie.description = payload.description
    if payload.price is not None:
        movie.price = payload.price

    if payload.certification_id is not None:
        cert = await repo.get_certification(session, payload.certification_id)
        if cert is None:
            raise ValueError("Certification not found")
        movie.certification_id = payload.certification_id

    if payload.genre_ids is not None:
        new_genres: list[Genre] = []
        for gid in payload.genre_ids:
            g = await repo.get_genre(session, gid)
            if g is None:
                raise ValueError(f"Genre not found: {gid}")
            new_genres.append(g)
        movie.genres = new_genres

    if payload.director_ids is not None:
        new_directors: list[Director] = []
        for did in payload.director_ids:
            d = await repo.get_director(session, did)
            if d is None:
                raise ValueError(f"Director not found: {did}")
            new_directors.append(d)
        movie.directors = new_directors

    if payload.star_ids is not None:
        new_stars: list[Star] = []
        for sid in payload.star_ids:
            s = await repo.get_star(session, sid)
            if s is None:
                raise ValueError(f"Star not found: {sid}")
            new_stars.append(s)
        movie.stars = new_stars

    await session.commit()
    await session.refresh(movie)
    return movie


async def can_delete_movie(session: AsyncSession, movie_id: int) -> bool:
    """
    Requirement: prevent deleting a movie if at least one user purchased it.
    Full enforcement will be added when Orders module is implemented (PR #8).
    """
    _ = session, movie_id
    return True


async def delete_movie(session: AsyncSession, movie_id: int) -> None:
    movie = await repo.get_movie(session, movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    if not await can_delete_movie(session, movie_id):
        raise ValueError("Movie cannot be deleted because it has purchases")

    await repo.delete_by_id(session, movie)
