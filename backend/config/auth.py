"""
Authentication module for AskTennis API.
Handles API key validation and Referer/Origin checks.
"""

import os
from fastapi import Header, HTTPException, Request, Depends
from typing import Optional, Annotated
from constants import ALLOWED_PATTERNS
from services.auth_service import AuthService
from services.auth_db_service import AuthDBService

def get_api_key(
    request: Request,
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
    referer: Annotated[Optional[str], Header()] = None,
    origin: Annotated[Optional[str], Header()] = None,
) -> str:
    """
    Validates the static API Key (Phase 1 hardening).
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    is_prod = env == "production"
    
    # 1. Resolve Expected Key
    expected_key = os.getenv("API_SECRET_KEY")
    if not expected_key and env in ["development", "testing"]:
        expected_key = "dev-key"
    
    if not expected_key:
        raise HTTPException(status_code=500, detail="API key not configured.")

    # 2. Validate Key
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    # 3. Production Extra Check: Origin/Referer Validation
    if is_prod:
        source = origin or referer
        if source and not any(p in source for p in ALLOWED_PATTERNS):
            raise HTTPException(status_code=403, detail="Request origin not authorized")

    return x_api_key

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
        
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    return username
