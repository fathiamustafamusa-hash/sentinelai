"""
Authentication service: user registration and login.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.schemas import Token, UserCreate, UserLogin
from app.utils.security import create_access_token, get_password_hash, verify_password


class AuthError(Exception):
    """Base exception for authentication errors."""

    pass


class UserAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


def create_user(db: Session, user_data: UserCreate, role: str = UserRole.ANALYST.value) -> User:
    """
    Create a new user.
    Raises UserAlreadyExistsError if username or email already exists.
    """
    existing = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )
    if existing:
        raise UserAlreadyExistsError("Username or email already registered")

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=role,
        is_active=True,
    )

    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise UserAlreadyExistsError("Username or email already registered") from e


def authenticate_user(db: Session, login_data: UserLogin) -> User:
    """
    Authenticate a user.
    Raises InvalidCredentialsError if credentials are wrong or user inactive.
    """
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user:
        raise InvalidCredentialsError("Incorrect username or password")

    if not verify_password(login_data.password, user.hashed_password or ""):
        raise InvalidCredentialsError("Incorrect username or password")

    if not user.is_active:
        raise InvalidCredentialsError("Inactive user account")

    return user


def create_user_token(user: User) -> Token:
    """Generate a JWT token for a user."""
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=token, token_type="bearer")
