"""
API routers package.
Contains route handlers for different API endpoints.
"""

from .filters import router as filters_router
from .matches import router as matches_router
from .stats import router as stats_router
from .query import router as query_router
from .auth import router as auth_router

__all__ = [
    "filters_router",
    "matches_router",
    "stats_router",
    "query_router",
    "auth_router",
]
