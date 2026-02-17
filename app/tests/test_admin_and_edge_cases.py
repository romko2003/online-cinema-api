from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import movies as movies_service


async def _register_activate_login(
    client,
    db_session: AsyncSession,
    monkeypatch,
) -> tuple[int, str]:
    monkeypatch.setattr("app.api.v1.accounts.send_activation_email", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.api.v1.accounts.send_password_reset_email", lambda *args, **kwargs: None)

    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    r = await client.post("/api/v1/accounts/register", json={"email": email, "password": password})
    assert r.status_code == 200, r.text

    from app.db.models.accounts import ActivationToken, User

    res = await db_session.execute(select(ActivationToken))
    token_row = res.scalars().first()
    assert token_row is not None

    r = await client.get("/api/v1/accounts/activate", params={"token": token_row.token})
    assert r.status_code == 200, r.text

    r = await client.post("/api/v1/accounts/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    access = r.json()["access_token"]

    res = await db_session.execute(select(User).where(User.email == email))
    user = res.scalars().first()
    assert user is not None

    return user.id, access


async def _ensure_admin_group_and_promote(db_session: AsyncSession, user_id: int) -> None:
    from app.db.models.accounts import User, UserGroup

    res = await db_session.execute(select(UserGroup).where(UserGroup.name == "ADMIN"))
    admin_group = res.scalars().first()
    if admin_group is None:
        admin_group = UserGroup(name="ADMIN")
        db_session.add(admin_group)
        await db_session.commit()
        await db_session.refresh(admin_group)

    res = await db_session.execute(select(User).where(User.id == user_id))
    user = res.scalars().first()
    assert user is not None

    user.group_id = admin_group.id
    await db_session.commit()


async def _create_movie_for_tests(db: AsyncSession):
    cert = await movies_service.create_certification(db, f"PG-13-{uuid.uuid4().hex[:6]}")
    genre = await movies_service.create_genre(db, f"Action-{uuid.uuid4().hex[:6]}")
    director = await movies_service.create_director(db, f"Director-{uuid.uuid4().hex[:6]}")
    star = await movies_service.create_star(db, f"Star-{uuid.uuid4().hex[:6]}")

    payload = {
        "name": f"Movie {uuid.uuid4().hex[:6]}",
        "year": 2024,
        "time": 120,
        "imdb": 8.1,
        "votes": 100_000,
        "meta_score": None,
        "gross": None,
        "description": "Test movie description",
        "price": "9.99",
        "certification_id": cert.id,
        "genre_ids": [genre.id],
        "director_ids": [director.id],
        "star_ids": [star.id],
    }

    try:
        movie = await movies_service.create_movie(db, payload)  # type: ignore[arg-type]
    except TypeError:
        from app.schemas.movies import MovieCreateRequest
        movie = await movies_service.create_movie(db, MovieCreateRequest(**payload))

    return movie


@pytest.mark.asyncio
async def test_cart_add_duplicate_movie_returns_400(client, db_session: AsyncSession, monkeypatch):
    _, access = await _register_activate_login(client, db_session, monkeypatch)
    headers = {"Authorization": f"Bearer {access}"}

    movie = await _create_movie_for_tests(db_session)

    r = await client.post("/api/v1/cart/add", headers=headers, json={"movie_id": movie.id})
    assert r.status_code == 200, r.text

    r = await client.post("/api/v1/cart/add", headers=headers, json={"movie_id": movie.id})
    assert r.status_code in (400, 404), r.text
    assert "detail" in r.json()


@pytest.mark.asyncio
async def test_payments_admin_requires_admin(client, db_session: AsyncSession, monkeypatch):
    _, access = await _register_activate_login(client, db_session, monkeypatch)
    headers = {"Authorization": f"Bearer {access}"}

    r = await client.get("/api/v1/payments/admin", headers=headers)
    assert r.status_code == 403, r.text


@pytest.mark.asyncio
async def test_payments_admin_returns_list_for_admin(client, db_session: AsyncSession, monkeypatch):
    admin_user_id, admin_access = await _register_activate_login(client, db_session, monkeypatch)
    await _ensure_admin_group_and_promote(db_session, admin_user_id)
    headers = {"Authorization": f"Bearer {admin_access}"}

    r = await client.get("/api/v1/payments/admin", headers=headers)
    assert r.status_code == 200, r.text
    assert "items" in r.json()


@pytest.mark.asyncio
async def test_payments_admin_filters_do_not_crash(client, db_session: AsyncSession, monkeypatch):
    admin_user_id, admin_access = await _register_activate_login(client, db_session, monkeypatch)
    await _ensure_admin_group_and_promote(db_session, admin_user_id)
    headers = {"Authorization": f"Bearer {admin_access}"}

    date_from = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    date_to = datetime.now(timezone.utc).date().isoformat()

    r = await client.get(
        "/api/v1/payments/admin",
        headers=headers,
        params={
            "user_id": admin_user_id,
            "status_filter": "successful",
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert r.status_code == 200, r.text
    assert "items" in r.json()
