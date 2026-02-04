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
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    expected_key = os.getenv("API_SECRET_KEY")

    # In development, use a default if not set
    if environment == "development" and not expected_key:
        expected_key = "dev-key"

    # In production, the key MUST be set
    if environment != "development" and not expected_key:
        raise HTTPException(
            status_code=500, detail="Server misconfiguration: API key not set."
        )

    # Validate the key
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

    return x_api_key
