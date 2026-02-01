"""
Rate limiting configuration for AskTennis API using SlowAPI.
Provides in-memory rate limiting without Redis dependency.
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_rate_limit_string() -> str:
    """
    Get rate limit string from environment or use default.

    Environment Variables:
        RATE_LIMIT_PER_MINUTE: Requests per minute (default: 30)

    Returns:
        Rate limit string in SlowAPI format (e.g., "30/minute")
    """
    requests_per_minute = os.getenv("RATE_LIMIT_PER_MINUTE", "30")
    return f"{requests_per_minute}/minute"


def get_query_rate_limit_string() -> str:
    """
    Get rate limit string specifically for AI query endpoints.
    These are more expensive, so we rate limit more aggressively.

    Environment Variables:
        QUERY_RATE_LIMIT_PER_MINUTE: Requests per minute for /api/query (default: 10)

    Returns:
        Rate limit string in SlowAPI format
    """
    requests_per_minute = os.getenv("QUERY_RATE_LIMIT_PER_MINUTE", "10")
    return f"{requests_per_minute}/minute"


# Create limiter instance with in-memory storage
# Key function extracts client IP for rate limiting
limiter = Limiter(key_func=get_remote_address)
