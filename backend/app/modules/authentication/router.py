from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    """Credentials accepted by the authentication module."""

    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest) -> dict[str, str]:
    """Placeholder JWT login endpoint for the authentication phase."""
    return {
        "access_token": "development-placeholder-token",
        "refresh_token": "development-placeholder-refresh-token",
        "token_type": "bearer",
    }
