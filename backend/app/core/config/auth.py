"""
Authentication module for AskTennis API.
Handles JWT-based authentication via HttpOnly cookies.
"""

import os
from typing import cast
from fastapi import HTTPException, Request
from app.services.auth_service import AuthService
from app.services.auth_db_service import AuthDBService

async def get_current_user(request: Request):
    """
    JWT Validation Dependency (Phase 2).
    Extracts the 'access_token' from HttpOnly cookies.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = AuthService.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    username: str = cast(str, payload.get("sub"))
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    return username
