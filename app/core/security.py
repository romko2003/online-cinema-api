from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


_PASSWORD_RULES = (
    "Password must be at least 8 characters long and include: "
    "1 uppercase letter, 1 lowercase letter, 1 digit, 1 special character."
)


def validate_password_complexity(password: str) -> None:
    """
    Enforces basic password complexity:
    - min 8 chars
    - at least 1 uppercase, 1 lowercase, 1 digit, 1 special
    """
    if len(password) < 8:
        raise ValueError(_PASSWORD_RULES)

    if not re.search(r"[A-Z]", password):
        raise ValueError(_PASSWORD_RULES)

    if not re.search(r"[a-z]", password):
        raise ValueError(_PASSWORD_RULES)

    if not re.search(r"\d", password):
        raise ValueError(_PASSWORD_RULES)

    if not re.search(r"[^\w\s]", password):
        raise ValueError(_PASSWORD_RULES)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


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
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e
