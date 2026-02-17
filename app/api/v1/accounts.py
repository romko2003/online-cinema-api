from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.accounts import MessageResponse, UserRegistrationRequest
from app.services.accounts import activate_user, register_user
from app.core.emails import send_activation_email

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
