from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from services.auth_db_service import AuthDBService
from services.auth_service import AuthService
from api.auth_schemas import UserCreate, UserResponse, Token
from api.auth_models import User
from constants import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
auth_db = AuthDBService()

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
    user_in: UserCreate, 
    db: Session = Depends(auth_db.get_db)
):
    user = auth_db.get_user_by_username(db, username=user_in.username)
    if not user or not AuthService.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True, # Should be True in production
        samesite="Lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    auth_db.update_last_login(db, user.id)
    return {"message": "Login successful", "username": user.username}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}
