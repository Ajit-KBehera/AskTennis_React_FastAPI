import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Username: alphanumeric and underscore only
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

    @field_validator("username")
    @classmethod
    def username_alphanumeric_underscore(cls, v: str) -> str:
        if not USERNAME_PATTERN.match(v):
            raise ValueError("Username may only contain letters, numbers, and underscores")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        return v


class LoginRequest(BaseModel):
    """Login request body; supports optional remember_me for extended session."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    remember_me: bool = False

    @field_validator("username")
    @classmethod
    def username_alphanumeric_underscore(cls, v: str) -> str:
        if not USERNAME_PATTERN.match(v):
            raise ValueError("Username may only contain letters, numbers, and underscores")
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
