"""
Error handling utilities for production-safe responses.
"""

import os


def is_production() -> bool:
    """Return True if ENVIRONMENT is production."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def get_500_detail(exception: Exception, production: bool | None = None) -> str:
    """
    Return a safe detail message for 500 responses.
    In production returns a generic message; otherwise returns str(exception).
    """
    if production is None:
        production = is_production()
    if production:
        return "An error occurred. Please try again."
    return str(exception)
