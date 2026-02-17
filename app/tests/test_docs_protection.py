from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.accounts import ActivationToken


@pytest.mark.asyncio
async def test_docs_are_protected(client, db_session: AsyncSession, monkeypatch):
    # Prevent real SMTP send
    monkeypatch.setattr("app.api.v1.accounts.send_activation_email", lambda *args, **kwargs: None)

    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    # Without auth: docs should be protected
    r = await client.get("/docs")
    assert r.status_code in (401, 403), r.text

    r = await client.get("/openapi.json")
    assert r.status_code in (401, 403), r.text

    # Create user for auth
    r = await client.post("/api/v1/accounts/register", json={"email": email, "password": password})
    assert r.status_code == 200, r.text

    res = await db_session.execute(select(ActivationToken))
    token_row = res.scalars().first()
    assert token_row is not None

    r = await client.get("/api/v1/accounts/activate", params={"token": token_row.token})
    assert r.status_code == 200, r.text

    r = await client.post("/api/v1/accounts/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    access = r.json()["access_token"]

    # With auth: docs should open
    r = await client.get("/docs", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200, r.text
    assert "Swagger UI" in r.text or "swagger" in r.text.lower()

    r = await client.get("/openapi.json", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200, r.text
    schema = r.json()
    assert "openapi" in schema
    assert "paths" in schema
