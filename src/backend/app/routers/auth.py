"""
Authentication routes: register and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db, get_current_active_user
from app.schemas import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_user_token,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.

    - **username**: unique, 3-50 chars, alphanumeric + underscore
    - **email**: valid email address
    - **password**: min 8 chars
    """
    try:
        user = create_user(db, user_data)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get JWT token",
)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    """
    try:
        user = authenticate_user(db, login_data)
        return create_user_token(user)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Return the currently authenticated user's profile."""
    return current_user
