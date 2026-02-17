from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import movies as movies_service


@pytest.mark.asyncio
async def test_cart_to_order_to_checkout_session_flow(
    client,
    db_session: AsyncSession,
    monkeypatch,
):
    """
    Flow:
    - register + activate + login
    - create movie in DB (through services)
    - add movie to cart
    - create order from cart
    - create Stripe checkout session (mocked)
    """

    # avoid real emails
    monkeypatch.setattr("app.api.v1.accounts.send_activation_email", lambda *args, **kwargs: None)

    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    # Register
    r = await client.post("/api/v1/accounts/register", json={"email": email, "password": password})
    assert r.status_code == 200, r.text

    # Grab activation token from DB (same approach as PR#13)
    from sqlalchemy import select
    from app.db.models.accounts import ActivationToken

    res = await db_session.execute(select(ActivationToken))
    token_row = res.scalars().first()
    assert token_row is not None

    # Activate
    r = await client.get("/api/v1/accounts/activate", params={"token": token_row.token})
    assert r.status_code == 200, r.text

    # Login
    r = await client.post("/api/v1/accounts/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    access = r.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access}"}

    # Create minimal relations & movie via services (no moderator dependency in tests)
    cert = await movies_service.create_certification(db_session, "PG-13")
    genre = await movies_service.create_genre(db_session, "Action")
    director = await movies_service.create_director(db_session, "John Doe")
    star = await movies_service.create_star(db_session, "Jane Star")

    movie_payload = {
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

    # services layer expects MovieCreateRequest-like object.
    # Most implementations accept dict-like payload or pydantic model.
    # If your service requires pydantic object, replace with MovieCreateRequest(**movie_payload).
    try:
        movie = await movies_service.create_movie(db_session, movie_payload)  # type: ignore[arg-type]
    except TypeError:
        from app.schemas.movies import MovieCreateRequest

        movie = await movies_service.create_movie(db_session, MovieCreateRequest(**movie_payload))

    # Cart is empty
    r = await client.get("/api/v1/cart", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["items"] == []

    # Add to cart
    r = await client.post("/api/v1/cart/add", headers=auth_headers, json={"movie_id": movie.id})
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Movie added to cart"

    # Cart should contain one item
    r = await client.get("/api/v1/cart", headers=auth_headers)
    assert r.status_code == 200, r.text
    cart = r.json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["movie_id"] == movie.id

    # Create order from cart
    r = await client.post("/api/v1/orders", headers=auth_headers)
    assert r.status_code == 201, r.text
    order_id = r.json()["order_id"]
    assert isinstance(order_id, int)

    # Orders list should contain that order
    r = await client.get("/api/v1/orders", headers=auth_headers)
    assert r.status_code == 200, r.text
    orders = r.json()["items"]
    assert any(o["id"] == order_id for o in orders)

    # Mock Stripe checkout session creation
    async def _fake_create_checkout_session(*args, **kwargs) -> str:
        return "https://checkout.stripe.com/test-session-url"

    monkeypatch.setattr(
        "app.api.v1.payments.payments_service.create_stripe_checkout_session",
        _fake_create_checkout_session,
    )

    # Create checkout session
    r = await client.post(
        "/api/v1/payments/checkout-session",
        headers=auth_headers,
        json={"order_id": order_id},
    )
    assert r.status_code == 200, r.text
    assert "checkout_url" in r.json()
    assert r.json()["checkout_url"].startswith("https://checkout.stripe.com/")


@pytest.mark.asyncio
async def test_stripe_webhook_requires_signature_header(client, monkeypatch):
    # even without auth, webhook requires Stripe-Signature
    r = await client.post("/api/v1/payments/webhook", content=b"{}")
    assert r.status_code == 400
    assert r.json()["detail"] == "Missing Stripe-Signature header"

    # with signature header, we mock processing
    async def _fake_process_webhook(*args, **kwargs):
        return ("Webhook processed", 200)

    monkeypatch.setattr(
        "app.api.v1.payments.payments_service.process_stripe_webhook",
        _fake_process_webhook,
    )

    r = await client.post(
        "/api/v1/payments/webhook",
        content=b'{"type":"checkout.session.completed"}',
        headers={"Stripe-Signature": "t=123,v1=fake"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Webhook processed"
    assert r.json()["status"] == 200


@pytest.mark.asyncio
async def test_list_payments_empty_for_new_user(client, db_session: AsyncSession, monkeypatch):
    monkeypatch.setattr("app.api.v1.accounts.send_activation_email", lambda *args, **kwargs: None)

    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    r = await client.post("/api/v1/accounts/register", json={"email": email, "password": password})
    assert r.status_code == 200, r.text

    from sqlalchemy import select
    from app.db.models.accounts import ActivationToken

    res = await db_session.execute(select(ActivationToken))
    token_row = res.scalars().first()
    assert token_row is not None

    r = await client.get("/api/v1/accounts/activate", params={"token": token_row.token})
    assert r.status_code == 200, r.text

    r = await client.post("/api/v1/accounts/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    access = r.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access}"}

    r = await client.get("/api/v1/payments", headers=auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "items" in data
    assert data["items"] == []
