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
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import time
import uuid
import structlog
import os
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# API Routers
from api.routers import filters_router, matches_router, stats_router, query_router, auth_router

# Configuration
from config.auth import get_api_key, get_current_user
from config.cors import get_cors_config
from config.rate_limiter import limiter
from config.observability import setup_observability
from config.logging_config import configure_logging
from utils.error_utils import is_production, get_500_detail

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
load_dotenv()

environment = os.getenv("ENVIRONMENT", "development").lower()
show_docs = environment != "production"

app = FastAPI(
    title="AskTennis API",
    description="AI-powered tennis statistics and analytics API",
    version="1.0.0",
    docs_url="/docs" if show_docs else None,
    redoc_url="/redoc" if show_docs else None,
    openapi_url="/openapi.json" if show_docs else None,
)

# =============================================================================
# MIDDLEWARE & EXTENSIONS
# =============================================================================

# Rate Limiting
app.state.limiter = limiter
# Retry-After (seconds) when rate limit is exceeded; frontend can show countdown
RATE_LIMIT_RETRY_AFTER_SECONDS = 60


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Return 429 with Retry-After header for client countdown."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": str(RATE_LIMIT_RETRY_AFTER_SECONDS)},
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS (Cross-Origin Resource Sharing)
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# OpenTelemetry Tracing
tracer = setup_observability()
FastAPIInstrumentor.instrument_app(app)

# Structured Logging
configure_logging()
logger = structlog.get_logger()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch uncaught exceptions; sanitize detail in production. Re-raise HTTPException."""
    if isinstance(exc, HTTPException):
        raise exc
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    detail = get_500_detail(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
    )


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


# Main API router with /api prefix - Protected by BOTH API Key AND JWT Session
api_router = APIRouter(
    prefix="/api", 
    dependencies=[Depends(get_api_key), Depends(get_current_user)]
)


@app.get("/")
async def root():
    """
    Root endpoint - returns a welcome message.
    In development, it also lists available endpoints.
    """
    response = {
        "message": "Welcome to AskTennis API",
        "version": "1.0.0",
    }

    if environment != "production":
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
        response["endpoints"] = endpoints
        response["docs_url"] = "/docs"

    return response


@app.get("/health")
async def health_check():
    """
    Liveness check for Cloud Run and load balancers.
    Returns 200 OK if the process is running.
    """
    return {"status": "healthy", "service": "asktennis-backend"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness check: verifies auth DB connectivity.
    Returns 503 if dependencies are not ready (e.g. for K8s/Cloud Run).
    """
    try:
        from sqlalchemy import text
        from services.auth_db_service import AuthDBService
        auth_db = AuthDBService()
        with auth_db.SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning("readiness_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "detail": "Database not available"},
        )
    return {"status": "ready", "service": "asktennis-backend"}


@app.on_event("startup")
async def startup_checks():
    """Fail fast in production if JWT secret is missing or default."""
    if not is_production():
        return
    secret = os.getenv("JWT_SECRET_KEY", "")
    default = "dev-jwt-secret-do-not-use-in-prod"
    if not secret or secret == default:
        raise RuntimeError(
            "JWT_SECRET_KEY must be set to a secure value in production. "
            "Do not use the default dev secret."
        )


# Register all API routers
api_router.include_router(query_router, tags=["AI Query"])
api_router.include_router(filters_router, tags=["Filters"])
api_router.include_router(matches_router, tags=["Matches"])
api_router.include_router(stats_router, tags=["Statistics"])

# Mount the routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router)

# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
