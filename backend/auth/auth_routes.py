from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.auth.auth_service import login_user, register_user
from backend.models.user_model import User, UserCreate, UserLogin


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=User)
def signup(user_data: UserCreate) -> User:
    """
    Register a new user account.

    This endpoint is intentionally simple for the prototype and does not
    perform duplicate checks or password hashing.
    """

    try:
        return register_user(user_data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=User)
def login(credentials: UserLogin) -> User:
    """
    Authenticate a user with email and password.

    Returns the user details on success, or a 401 error if credentials
    are invalid.
    """

    user = login_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return user


@router.post("/admin_login", response_model=User)
def admin_login(credentials: UserLogin) -> User:
    """
    Authenticate an administrative user.

    Only users with role='admin' are allowed to log in via this endpoint.
    """

    user = login_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="User is not an admin.")

    return user

