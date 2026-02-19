import os
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from typing import cast
from sqlalchemy.orm import Session
from datetime import timedelta
from app.services.auth_db_service import AuthDBService
from app.services.auth_service import AuthService
from app.api.auth_schemas import UserCreate, UserResponse, Token, LoginRequest
from app.api.auth_models import User
from app.core.constants import ACCESS_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER_ME

router = APIRouter()
auth_db = AuthDBService()

@router.get("/check-username")
def check_username(username: str, db: Session = Depends(auth_db.get_db)):
    """Check if a username is available (for registration). No auth required."""
    user = auth_db.get_user_by_username(db, username=username)
    return {"available": user is None}


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(auth_db.get_db)):
    db_user = auth_db.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(
        username=user_in.username,
        hashed_password=AuthService.get_password_hash(user_in.password)
    )
    return auth_db.create_user(db, new_user)

@router.post("/login")
def login(
    response: Response,
    user_in: LoginRequest,
    db: Session = Depends(auth_db.get_db),
):
    user = auth_db.get_user_by_username(db, username=user_in.username)
    if not user or not AuthService.verify_password(user_in.password, cast(str, user.hashed_password)):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if user_in.remember_me:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER_ME)
        max_age_seconds = ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER_ME * 24 * 60 * 60
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        max_age_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60

    access_token = AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        max_age=max_age_seconds,
    )

    auth_db.update_last_login(db, cast(int, user.id))
    return {"message": "Login successful", "username": user.username}

from app.core.config.auth import get_current_user

@router.get("/me", response_model=UserResponse)
def get_me(
    username: str = Depends(get_current_user),
    db: Session = Depends(auth_db.get_db)
):
    user = auth_db.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}
