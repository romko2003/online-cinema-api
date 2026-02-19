from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str) -> str:
    now = _utcnow()
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, datetime]:
    now = _utcnow()
    expire = now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expire


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as e:
        raise ValueError("Invalid token") from e


# -------------------------
# Backwards-compatible API
# -------------------------

def decode_access_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")
    return payload
