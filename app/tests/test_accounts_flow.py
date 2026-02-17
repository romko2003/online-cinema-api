from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.accounts import ActivationToken


@pytest.mark.asyncio
async def test_accounts_register_activate_login_refresh_logout(
    client,
    db_session: AsyncSession,
    monkeypatch,
):
    # Prevent real SMTP send
    monkeypatch.setattr("app.api.v1.accounts.send_activation_email", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "app.api.v1.accounts.send_password_reset_email", lambda *args, **kwargs: None
    )

    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    # Register
    r = await client.post(
        "/api/v1/accounts/register",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Activation email sent"

    # Fetch activation token from DB
    res = await db_session.execute(
        select(ActivationToken).where(ActivationToken.user_id.isnot(None))
    )
    token_row = res.scalars().first()
    assert token_row is not None
    token = token_row.token

    # Activate
    r = await client.get("/api/v1/accounts/activate", params={"token": token})
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Account activated"

    # Login
    r = await client.post("/api/v1/accounts/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    access = data["access_token"]
    refresh = data["refresh_token"]

    # Refresh
    r = await client.post("/api/v1/accounts/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200, r.text
    data2 = r.json()
    assert "access_token" in data2
    assert "refresh_token" in data2
    assert data2["access_token"] != ""
    assert data2["refresh_token"] != ""

    # Logout (revokes refresh token)
    r = await client.post("/api/v1/accounts/logout", json={"refresh_token": refresh})
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Logged out"

    # Refresh after logout should fail (most likely 400)
    r = await client.post("/api/v1/accounts/refresh", json={"refresh_token": refresh})
    assert r.status_code in (400, 401), r.text

    # Change password should require auth
    r = await client.post(
        "/api/v1/accounts/change-password",
        json={"old_password": password, "new_password": "NewStrongPass123!"},
    )
    assert r.status_code in (401, 403), r.text

    # Change password with auth
    r = await client.post(
        "/api/v1/accounts/change-password",
        headers={"Authorization": f"Bearer {access}"},
        json={"old_password": password, "new_password": "NewStrongPass123!"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Password changed"

    # Login with old password should fail
    r = await client.post("/api/v1/accounts/login", json={"email": email, "password": password})
    assert r.status_code in (400, 401), r.text

    # Login with new password should succeed
    r = await client.post(
        "/api/v1/accounts/login",
        json={"email": email, "password": "NewStrongPass123!"},
    )
    assert r.status_code == 200, r.text
