from __future__ import annotations

from enum import Enum

import bcrypt


class PasswordError(str, Enum):
    TOO_SHORT = "Password must be at least 8 characters long."
    NEED_UPPER = "Password must contain at least 1 uppercase letter."
    NEED_LOWER = "Password must contain at least 1 lowercase letter."
    NEED_DIGIT = "Password must contain at least 1 digit."
    NEED_SPECIAL = "Password must contain at least 1 special character."


def validate_password_complexity(password: str) -> None:
    if len(password) < 8:
        raise ValueError(PasswordError.TOO_SHORT.value)

    has_upper = any(ch.isupper() for ch in password)
    has_lower = any(ch.islower() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    has_special = any(not ch.isalnum() for ch in password)

    if not has_upper:
        raise ValueError(PasswordError.NEED_UPPER.value)
    if not has_lower:
        raise ValueError(PasswordError.NEED_LOWER.value)
    if not has_digit:
        raise ValueError(PasswordError.NEED_DIGIT.value)
    if not has_special:
        raise ValueError(PasswordError.NEED_SPECIAL.value)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
