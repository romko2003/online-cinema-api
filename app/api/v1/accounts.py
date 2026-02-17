from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.emails import send_activation_email, send_password_reset_email
from app.db.models.accounts import User
from app.db.session import get_db
from app.schemas.accounts import (
    ChangePasswordRequest,
    LogoutRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenPairResponse,
    UserLoginRequest,
    UserRegistrationRequest,
)
from app.services.accounts import (
    activate_user,
    change_password,
    confirm_password_reset,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
    request_password_reset,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/register", response_model=MessageResponse)
async def register(
    payload: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        token = await register_user(db, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    send_activation_email(payload.email, token)
    return MessageResponse(message="Activation email sent")


@router.get("/activate", response_model=MessageResponse)
async def activate(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await activate_user(db, token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return MessageResponse(message="Account activated")


@router.post("/login", response_model=TokenPairResponse)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPairResponse:
    try:
        access, refresh = await login_user(db, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TokenPairResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPairResponse:
    try:
        access, refresh_token = await refresh_access_token(db, payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TokenPairResponse(access_token=access, refresh_token=refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await logout_user(db, payload.refresh_token)
    return MessageResponse(message="Logged out")


@router.post("/change-password", response_model=MessageResponse)
async def change_password_endpoint(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await change_password(db, current_user, payload.old_password, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageResponse(message="Password changed")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    # Return generic response to avoid user enumeration
    token = await request_password_reset(db, payload.email)
    if token:
        send_password_reset_email(payload.email, token)

    return MessageResponse(
        message="If the email is registered and active, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        await confirm_password_reset(db, payload.token, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageResponse(message="Password has been reset")
