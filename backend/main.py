from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Import core logic
from agent.agent_factory import setup_langgraph_agent
from services.query_service import QueryProcessor

# Import API routers
from api.routers import filters_router, matches_router, stats_router

# Import configuration
from config.cors import get_cors_config
from config.rate_limiter import limiter, get_query_rate_limit_string

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

# Initialize services
try:
    agent_graph = setup_langgraph_agent()
    query_processor = QueryProcessor()
    

    
    print("✅ Services initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize services: {e}")
    agent_graph = None
    query_processor = None

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Original models for /query endpoint
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sql_queries: List[str]
    data: List[Dict[str, Any]]
    conversation_flow: List[Any]

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

# New /api/query endpoint (same as legacy, but under /api prefix)
@api_router.post("/query", response_model=QueryResponse)
@limiter.limit(get_query_rate_limit_string())
async def process_query(request: Request, query_request: QueryRequest):
    """
    AI query endpoint - generates SQL and returns detailed results.
    For chat-style interface, use /api/chat instead.
    """
    if not agent_graph or not query_processor:
        raise HTTPException(status_code=500, detail="Services not initialized")

    try:
        results = await run_in_threadpool(
            query_processor.handle_user_query,
            query_request.query,
            agent_graph
        )

        return QueryResponse(
            answer=results.get("answer", ""),
            sql_queries=results.get("sql_queries", []),
            data=results.get("data", []),
            conversation_flow=results.get("conversation_flow", [])
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Include all API routers
api_router.include_router(filters_router, tags=["Filters"])

api_router.include_router(matches_router, tags=["Matches"])
api_router.include_router(stats_router, tags=["Statistics"])

# Mount the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
