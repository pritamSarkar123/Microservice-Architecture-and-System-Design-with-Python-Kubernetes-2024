from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from .. import models
from ..config import settings
from ..database import Session, get_db
from ..schemas import (
    AccessToken,
    RefreshToken,
    Token,
    TokenForValidation,
    TokenForValidationForPasswordReset,
    TokenValidation,
    User,
    UserReturn,
)
from ..utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    rate_limiter,
    send_email,
    verify_password,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth-router"],
    responses={
        401: {  # default one, if we did not set up for any endpoint , this will be returned by default
            "user": "Not authorized"
        }
    },
)


@router.post(
    "/register", response_model=UserReturn, status_code=status.HTTP_201_CREATED
)
@rate_limiter(max_requests=100, period=60)
async def register_user(request: Request, user: User, db: Session = Depends(get_db)):

    try:
        already_present_user = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )
        if already_present_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(user.password)
        user.password = hashed_password
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # returning
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=10000, period=60)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "admin": user.admin},
        expires_delta=access_token_expires,
    )
    refresh_token_expires = timedelta(hours=settings.refresh_token_expire_hours)
    refresh_token = create_refresh_token(
        data={"sub": user.email, "admin": user.admin},
        expires_delta=refresh_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=AccessToken, status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=100, period=60)
async def refresh_token(
    request: Request, refresh_token: RefreshToken, db: Session = Depends(get_db)
):
    user = decode_token(refresh_token.refresh_token)
    user_email = user["sub"]
    adimin_user = user["admin"]
    user = (
        db.query(models.User)
        .filter(models.User.email == user_email, models.User.admin == adimin_user)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_email, "admin": adimin_user},
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/validate",
    status_code=status.HTTP_200_OK,
    response_model=TokenValidation,
)
@rate_limiter(max_requests=10000, period=60)
async def validate_user(
    request: Request, token: TokenForValidation, db: Session = Depends(get_db)
):
    user = decode_token(token.token)
    user_email = user["sub"]
    adimin_user = user["admin"]
    user = (
        db.query(models.User)
        .filter(models.User.email == user_email, models.User.admin == adimin_user)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"valid": True, "admin": adimin_user, "email": user_email}


@router.post("/logout", status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=100, period=60)
async def logout(request: Request, token: RefreshToken, db: Session = Depends(get_db)):
    user = decode_token(token.refresh_token)
    user_email = user["sub"]
    adimin_user = user["admin"]
    user = (
        db.query(models.User)
        .filter(models.User.email == user_email, models.User.admin == adimin_user)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "Successfully logged out"}


@router.post("/forget-password", status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=100, period=60)
async def forget_password(request: Request, email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "admin": user.admin},
        expires_delta=access_token_expires,
    )

    status, message = await send_email(settings, access_token, user.email)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
        )
    return {"message": "Successfully sent email to reset password"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@rate_limiter(max_requests=100, period=60)
async def reset_password(
    request: Request,
    reset_data: TokenForValidationForPasswordReset,
    db: Session = Depends(get_db),
):
    user = decode_token(reset_data.token)
    user_email = user["sub"]
    adimin_user = user["admin"]
    user = (
        db.query(models.User)
        .filter(models.User.email == user_email, models.User.admin == adimin_user)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.password = get_password_hash(reset_data.new_password)
    db.commit()
    return {"message": "Password reset successfully"}
