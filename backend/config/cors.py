"""
CORS (Cross-Origin Resource Sharing) configuration for AskTennis API.
Environment-based configuration for development and production.
"""

import os
from typing import List


def get_allowed_origins() -> List[str]:
    """
    Get allowed origins based on environment.

    Environment Variables:
        ENVIRONMENT: 'development' or 'production' (default: development)
        ALLOWED_ORIGINS: Comma-separated list of allowed origins for production

    Returns:
        List of allowed origin URLs
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        # In production, use explicit whitelist from environment
        origins_str = os.getenv("ALLOWED_ORIGINS", "")
        if origins_str:
            origins = [
                origin.strip() for origin in origins_str.split(",") if origin.strip()
            ]
            if origins:
                return origins

        # Default production origins
        origins = [
            "https://asktennis.com",
            "https://www.asktennis.com",
            "https://asktennis-frontend-147976075322.us-central1.run.app",
        ]

        # Auto-detect current Cloud Run project and allow its frontend
        # This helps if the user re-deploys or changes service names
        return origins

    # Development mode - allow common local development origins
    return [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]


def get_cors_config() -> dict:
    """
    Get complete CORS middleware configuration.

    Returns:
        Dictionary of CORS middleware settings
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    return {
        "allow_origins": get_allowed_origins(),
        "allow_credentials": False,  # No cookies/auth-headers used, so keep False for security
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],  # Allow all headers since we are already Origin-restricted
        # In development, expose all headers; in production, be more restrictive
        "expose_headers": [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        "max_age": 600
        if environment == "production"
        else 0,  # Cache preflight for 10 min in prod
    }
