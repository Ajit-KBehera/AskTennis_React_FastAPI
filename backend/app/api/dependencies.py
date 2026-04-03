"""
Authentication module for AskTennis API.
Handles JWT-based authentication via HttpOnly cookies.
"""

import os
from typing import cast
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth_service import AuthService
from app.infrastructure.repositories.user_repository import AuthDBService

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(request: Request, auth_header: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    """
    JWT Validation Dependency (Phase 2).
    Extracts the 'access_token' from HttpOnly cookies or Authorization header.
    """
    token = request.cookies.get("access_token")
    
    if not token and auth_header and auth_header.credentials:
        token = auth_header.credentials
        
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = AuthService.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    username: str = cast(str, payload.get("sub"))
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    return username
