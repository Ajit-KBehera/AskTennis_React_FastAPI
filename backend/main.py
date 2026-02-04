"""
AskTennis API - Main Application Entry Point

AI-powered tennis statistics and analytics API built with FastAPI.
This module initializes the application and wires up all components.
"""

# =============================================================================
# IMPORTS
# =============================================================================
from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
import structlog
from dotenv import load_dotenv
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# API Routers
from api.routers import filters_router, matches_router, stats_router, query_router

# Configuration
from config.auth import get_api_key
from config.cors import get_cors_config
from config.rate_limiter import limiter
from config.observability import setup_observability
from config.logging_config import configure_logging

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
load_dotenv()

# =============================================================================
# APPLICATION INITIALIZATION
# =============================================================================
app = FastAPI(
    title="AskTennis API",
    description="AI-powered tennis statistics and analytics API",
    version="1.0.0",
)

# =============================================================================
# MIDDLEWARE & EXTENSIONS
# =============================================================================

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (Cross-Origin Resource Sharing)
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# OpenTelemetry Tracing
tracer = setup_observability()
FastAPIInstrumentor.instrument_app(app)

# Structured Logging
configure_logging()
logger = structlog.get_logger()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Request logging middleware.
    - Assigns/propagates a unique request ID for tracing
    - Logs request method, path, status, and duration
    - Attaches request ID to response headers
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            "request_processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time,
        )
        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            process_time=process_time,
        )
        raise


# =============================================================================
# ROUTES
# =============================================================================


# Main API router with /api prefix - Protected by API Key
api_router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])


@app.get("/")
async def root():
    """
    Root endpoint - returns API info and available endpoints.
    Useful for health checks and API discovery.
    """
    endpoints = []
    for route in app.routes:
        if hasattr(route, "path") and route.path.startswith("/api"):
            methods = (
                [m for m in route.methods if m not in ["OPTIONS", "HEAD"]]
                if hasattr(route, "methods")
                else []
            )
            endpoints.append(
                {"path": route.path, "methods": methods, "name": route.name}
            )

    return {
        "message": "Welcome to AskTennis API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": endpoints,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Cloud Run and load balancers.
    Returns 200 OK if the service is healthy.
    """
    return {"status": "healthy", "service": "asktennis-backend"}


# Register all API routers
api_router.include_router(query_router, tags=["AI Query"])
api_router.include_router(filters_router, tags=["Filters"])
api_router.include_router(matches_router, tags=["Matches"])
api_router.include_router(stats_router, tags=["Statistics"])

# Mount the API router to the app
app.include_router(api_router)

# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
