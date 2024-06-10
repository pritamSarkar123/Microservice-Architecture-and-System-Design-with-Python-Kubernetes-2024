import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status

from ..config import settings
from ..schemas import AccessToken, RefreshToken, Token, User, UserReturn,TokenForValidationForPasswordReset
from ..utils.rate_limit_handler import rate_limiter

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth-router"],
    responses={
        401: {  # default one, if we did not set up for any endpoint , this will be returned by default
            "user": "Not authorized"
        }
    },
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
@rate_limiter(max_requests=100, period=60)
async def register(request: Request, user: User):
    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/register", json=user.model_dump()
    )
    if response.status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.json().get("detail"),
        )
    return response.json()


@router.post("/login", status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=10000, period=60)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.json().get("detail"),
        )
    return response.json()


@router.post("/refresh", status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=100, period=60)
async def refresh(request: Request, refresh_token: RefreshToken):
    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/refresh",
        json={"refresh_token": refresh_token.refresh_token},
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.json().get("detail"),
        )
    return response.json()

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, refresh_token: RefreshToken):
    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/logout",
        json={"refresh_token": refresh_token.refresh_token},
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.json().get("detail"),
        )
    return response.json()

@router.post("/forget-password", status_code=status.HTTP_200_OK)
async def forget_password(request: Request, email: str = Form(...)):
    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/forget-password?email={email}",
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.json().get("detail"),
        )
    return response.json()


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: Request, reset_data: TokenForValidationForPasswordReset):
    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/reset-password?",
        json={"token": reset_data.token, "new_password": reset_data.new_password},
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.json().get("detail"),
        )
    return response.json()
