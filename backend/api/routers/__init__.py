"""
API routers package.
Contains route handlers for different API endpoints.
"""

from .filters import router as filters_router
from .chat import router as chat_router
from .matches import router as matches_router
from .stats import router as stats_router

__all__ = [
    "filters_router",
    "chat_router",
    "matches_router",
    "stats_router",
]
