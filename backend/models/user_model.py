from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """
    Payload schema for registering a new user in the system.
    """

    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., min_length=3)
    location: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """
    Payload schema for authenticating an existing user.
    """

    email: EmailStr
    password: str = Field(..., min_length=6)


class User(BaseModel):
    """
    Public representation of a user record returned by the API.

    Note: This intentionally omits sensitive fields such as password hashes.
    """

    id: int
    name: str
    email: EmailStr
    phone: str
    location: str
    role: str = "user"

