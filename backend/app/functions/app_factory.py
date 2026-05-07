"""
Appwrite function FastAPI app factories.

These factories keep function-specific API surfaces lean while reusing
existing routers and authentication dependencies.
"""

from fastapi import APIRouter, Depends, FastAPI

from app.api.dependencies import get_current_user
from app.api.routers import (
    auth_router,
    filters_router,
    matches_router,
    query_router,
    stats_router,
)


def _build_base_app(title: str) -> FastAPI:
    app = FastAPI(title=title, version="1.0.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


def create_auth_function_app() -> FastAPI:
    app = _build_base_app("AskTennis Auth Function")
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    return app


def create_data_function_app() -> FastAPI:
    app = _build_base_app("AskTennis Data Function")
    api_router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])
    api_router.include_router(filters_router, tags=["Filters"])
    api_router.include_router(matches_router, tags=["Matches"])
    api_router.include_router(stats_router, tags=["Statistics"])
    app.include_router(api_router)
    return app


def create_query_function_app() -> FastAPI:
    app = _build_base_app("AskTennis Query Function")
    api_router = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])
    api_router.include_router(query_router, tags=["AI Query"])
    app.include_router(api_router)
    return app
