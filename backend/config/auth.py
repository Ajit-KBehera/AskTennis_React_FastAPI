"""
Authentication module for AskTennis API.
Handles API key validation.
"""

import os
from fastapi import Header, HTTPException
from typing import Optional


def get_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Validate the API key from the request header.
    
    Args:
        x_api_key: The API key sent in the X-API-Key header.
        
    Returns:
        The validated API key.
        
    Raises:
        HTTPException: If the API key is missing or invalid.
    """
    # specific API key provided in environment, or default for dev
    # Ideally, this should be mandatory in production.
    expected_key = os.getenv("API_SECRET_KEY")
    
    # If no key is configured in environment, we might want to fail open or closed.
    # For security, we should fail closed if it's supposed to be protected.
    # But for ease of development, if not set, maybe allow? 
    # Let's enforcing setting it.
    
    if not expected_key:
        # If server isn't configured with a key, log warning (in real app) 
        # For now, if no key set in env, allow access (dev mode convenience) OR block.
        # User requested "Add CORS restrictions for production" and "Missing Authentication".
        # So we should enforce it.
        # However, to avoid breaking existing setups without the key, 
        # maybe we use a default if not set? 
        # Let's enforce it but provide a clear error message.
        environment = os.getenv("ENVIRONMENT", "development").lower()
        if environment == "development":
             # In dev, if not set, maybe allow or use default "dev-key"
             expected_key = "dev-key"
        else:
             # In prod, must be set
             if not expected_key:
                 raise HTTPException(status_code=500, detail="Server misconfiguration: API key not set.")

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
        
    return x_api_key
