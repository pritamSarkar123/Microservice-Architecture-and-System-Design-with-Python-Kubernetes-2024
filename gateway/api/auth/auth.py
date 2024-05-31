import httpx
from fastapi import HTTPException, Request, status

from ..config import settings


async def validateToken(request: Request):
    if "Authorization" not in request.headers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials"
        )

    token = request.headers["Authorization"].split(" ")[-1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token"
        )

    response = httpx.post(
        f"{settings.auth_uri}/api/v1/auth/validate",
        json={"token": token},
    )
    if response.status_code == 429:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=response.json().get("detail"),
        )
    if response.status_code not in {200, 429}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.json().get("detail"),
        )
    return response.json()
