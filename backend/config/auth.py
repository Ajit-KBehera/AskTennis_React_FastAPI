"""
Authentication module for AskTennis API.
Handles API key validation and Referer/Origin checks.
"""

import os
from fastapi import Header, HTTPException, Request
from typing import Optional, Annotated
from constants import ALLOWED_PATTERNS

def get_api_key(
    request: Request,
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
    referer: Annotated[Optional[str], Header()] = None,
    origin: Annotated[Optional[str], Header()] = None,
) -> str:
    """
    Consolidated authentication dependency.
    1. Validates API Secret Key.
    2. Performs defense-in-depth Origin/Referer checks in production.
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
