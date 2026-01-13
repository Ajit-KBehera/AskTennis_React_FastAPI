from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core logic
from agent.agent_factory import setup_langgraph_agent
from services.query_service import QueryProcessor

# Import API routers
from api.routers import filters_router, chat_router, matches_router, stats_router
import api.routers.chat as chat_module

app = FastAPI(
    title="AskTennis API",
    description="AI-powered tennis statistics and analytics API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    agent_graph = setup_langgraph_agent()
    query_processor = QueryProcessor()
    
    # Set dependencies for chat router
    chat_module.set_dependencies(query_processor, agent_graph)
    
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
    return {
        "message": "Welcome to AskTennis API",
        "version": "1.0.0",
        "endpoints": {
            "legacy": ["/query"],
            "api": [
                "/api/filters",
                "/api/chat",
                "/api/matches",
                "/api/query",
                "/api/stats/serve",
                "/api/stats/serve/raw",
                "/api/stats/return",
                "/api/stats/ranking"
            ]
        }
    }

# Legacy /query endpoint (preserved for backward compatibility)
@app.post("/query", response_model=QueryResponse)
async def process_query_legacy(request: QueryRequest):
    """
    Legacy query endpoint (preserved for backward compatibility).
    Use /api/query or /api/chat for new integrations.
    """
    if query_processor is None or agent_graph is None:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        results = query_processor.handle_user_query(
            request.query, 
            agent_graph
        )
        
        return {
            "answer": results["answer"],
            "sql_queries": results["sql_queries"],
            "data": results["data"],
            "conversation_flow": results["conversation_flow"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# New /api/query endpoint (same as legacy, but under /api prefix)
@api_router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    AI query endpoint - generates SQL and returns detailed results.
    For chat-style interface, use /api/chat instead.
    """
    if query_processor is None or agent_graph is None:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        results = query_processor.handle_user_query(
            request.query, 
            agent_graph
        )
        
        return {
            "answer": results["answer"],
            "sql_queries": results["sql_queries"],
            "data": results["data"],
            "conversation_flow": results["conversation_flow"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Include all API routers
api_router.include_router(filters_router, tags=["Filters"])
api_router.include_router(chat_router, tags=["Chat"])
api_router.include_router(matches_router, tags=["Matches"])
api_router.include_router(stats_router, tags=["Statistics"])

# Mount the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
