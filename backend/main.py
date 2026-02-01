from fastapi import FastAPI, APIRouter, Request
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

# Configuration imports
from config.cors import get_cors_config
from config.rate_limiter import limiter
from config.observability import setup_observability
from config.logging_config import configure_logging

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AskTennis API",
    description="AI-powered tennis statistics and analytics API",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware with environment-based configuration
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Initialize OpenTelemetry
tracer = setup_observability()
FastAPIInstrumentor.instrument_app(app)

# Initialize structured logging
configure_logging()
logger = structlog.get_logger()

# Request ID and Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
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
            process_time=process_time
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
            process_time=process_time
        )
        raise

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    # Dynamically generate endpoint list
    endpoints = []
    for route in app.routes:
        if hasattr(route, "path") and route.path.startswith("/api"):
            methods = [m for m in route.methods if m not in ["OPTIONS", "HEAD"]] if hasattr(route, "methods") else []
            endpoints.append({
                "path": route.path,
                "methods": methods,
                "name": route.name
            })
            
    return {
        "message": "Welcome to AskTennis API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": endpoints
    }

# Include all API routers
api_router.include_router(query_router, tags=["AI Query"])
api_router.include_router(filters_router, tags=["Filters"])
api_router.include_router(matches_router, tags=["Matches"])
api_router.include_router(stats_router, tags=["Statistics"])

# Mount the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
