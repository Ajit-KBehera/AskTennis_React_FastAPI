"""
CORS (Cross-Origin Resource Sharing) configuration for AskTennis API.
Environment-based configuration for development and production.
"""

import os
from constants import ALLOWED_HOSTS

def get_cors_config() -> dict:
    """
    Get consolidated CORS middleware configuration based on environment.
    
    Environment Variables:
        ENVIRONMENT: 'development' or 'production' (default: development)
        ALLOWED_ORIGINS: Comma-separated whitelist for production
        ALLOW_ALL_ORIGINS: Set to 'true' to bypass origin restrictions (e.g. for mobile)
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    is_prod = env == "production"
    allow_all = os.getenv("ALLOW_ALL_ORIGINS", "false").lower() == "true"

    # 1. Determine Allowed Origins
    credentials_allowed = True # Default
    if allow_all:
        origins = ["*"]
        credentials_allowed = False # Browser disallows "*" with credentials
    elif not is_prod:
        # Development: common local ports
        origins = [
            "http://localhost:3000", "http://localhost:5173", "http://localhost:5174",
            "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174",
        ]
    else:
        # Production: Env-based whitelist or defaults
        env_origins = os.getenv("ALLOWED_ORIGINS", "")
        if env_origins:
            origins = [o.strip() for o in env_origins.split(",") if o.strip()]
        else:
            origins = ALLOWED_HOSTS

    # 2. Build Base Configuration
    config = {
        "allow_origins": origins,
        "allow_credentials": credentials_allowed, # Required for HttpOnly cookies
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Set-Cookie"], # Explicit headers for cookies
        "expose_headers": [
            "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"
        ],
        "max_age": 600 if is_prod else 0,
    }

    # 3. Add Dynamic Cloud Run Previews for Production
    if is_prod:
        # Match any frontend on Cloud Run to support dynamic previews/service subdomains.
        # This is CRITICAL for credentials (cookies) to work across Cloud Run services.
        config["allow_origin_regex"] = r"https://.*\.run\.app"
        config["allow_credentials"] = True
        
        # If allow_all was set, the regex above is safer and more compatible with cookies.
        if allow_all:
            # FORCE clear allow_origins to remove "*" because wildcard + credentials = CORS Error.
            # The regex above will handle the matching.
            config["allow_origins"] = []

    return config
