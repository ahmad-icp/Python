from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_token

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    college_id: str = "college-demo"
    mfa_code: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_required: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: str
    college_id: str


class EmailVerificationRequest(BaseModel):
    token: str


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest) -> TokenPair:
    if not payload.username.strip() or not payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    claims = {"college_id": payload.college_id, "role": "administrator", "jti": str(uuid4())}
    access = create_token(payload.username, settings.JWT_SECRET_KEY, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access", claims)
    refresh = create_token(payload.username, settings.JWT_SECRET_KEY, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh", claims)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: RefreshRequest) -> TokenPair:
    claims = {"college_id": "college-demo", "role": "administrator", "jti": str(uuid4())}
    access = create_token("refresh-subject", settings.JWT_SECRET_KEY, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access", claims)
    refresh = create_token("refresh-subject", settings.JWT_SECRET_KEY, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh", claims)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/password-reset")
def request_password_reset(payload: PasswordResetRequest) -> dict[str, str]:
    return {"status": "queued", "college_id": payload.college_id}


@router.post("/email-verification")
def verify_email(payload: EmailVerificationRequest) -> dict[str, str]:
    return {"status": "verified", "token_id": payload.token[-8:]}
