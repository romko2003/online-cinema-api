from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppError(Exception):
    """
    Base application error used for consistent error handling later.
    """
    message: str


@dataclass(frozen=True)
class NotFoundError(AppError):
    pass


@dataclass(frozen=True)
class ValidationError(AppError):
    pass


@dataclass(frozen=True)
class AuthError(AppError):
    pass
