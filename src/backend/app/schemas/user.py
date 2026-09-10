"""
User Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user data returned to clients (no password!)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded inside JWT."""
    username: Optional[str] = None
    role: Optional[str] = None
