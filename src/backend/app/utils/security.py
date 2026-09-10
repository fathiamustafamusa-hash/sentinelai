"""
Security utilities: password hashing (bcrypt) and JWT tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# ============ Password hashing ============
# bcrypt has a 72-byte limit; truncate password to avoid errors
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BCRYPT_MAX_BYTES = 72


def _truncate_password(password: str) -> str:
    """Truncate password to 72 bytes (bcrypt limit) safely."""
    encoded = password.encode("utf-8")
    if len(encoded) <= BCRYPT_MAX_BYTES:
        return password
    # Truncate to 72 bytes, decode ignoring partial characters
    return encoded[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(_truncate_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(_truncate_password(plain_password), hashed_password)


# ============ JWT tokens ============
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns None if invalid."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
