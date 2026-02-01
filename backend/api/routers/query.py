"""
Query router - AI-powered natural language tennis queries.

Endpoints:
    POST /api/query - Process natural language questions using LangGraph agent
"""

import traceback
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, field_validator
import structlog

from config.rate_limiter import limiter, get_query_rate_limit_string
from config.auth import get_api_key
from agent.agent_factory import setup_langgraph_agent
from services.query_service import QueryProcessor

# =============================================================================
# SETUP
# =============================================================================

router = APIRouter()
logger = structlog.get_logger()

# Lazy-loaded service singletons
_agent_graph = None
_query_processor = None


def get_services():
    """
    Lazy initialization of AI services.
    Services are initialized on first request, not at import time.
    This improves startup time and testability.
    """
    global _agent_graph, _query_processor
    
    if _agent_graph is None:
        try:
            _agent_graph = setup_langgraph_agent()
            _query_processor = QueryProcessor()
            logger.info("query_services_initialized")
        except Exception as e:
            logger.error("query_services_init_failed", error=str(e))
            raise
    
    return _agent_graph, _query_processor


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class QueryRequest(BaseModel):
    """Request model for AI query endpoint."""
    query: str
    
    @field_validator('query')
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        """Validate that query is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class QueryResponse(BaseModel):
    """Response model for AI query endpoint."""
    answer: str
    sql_queries: List[str]
    data: List[Dict[str, Any]]
    conversation_flow: List[Any]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/query", response_model=QueryResponse)
@limiter.limit(get_query_rate_limit_string())
async def process_query(
    request: Request,
    query_request: QueryRequest,
    api_key: str = Depends(get_api_key)  # Auth validation happens in Depends
):
    """
    AI query endpoint - processes natural language questions about tennis.
    
    Uses LangGraph agent to:
    1. Parse the natural language question
    2. Generate appropriate SQL queries
    3. Execute queries against the tennis database
    4. Return structured results with an AI-generated answer
    
    Rate limited and requires API key authentication.
    """
    try:
        agent_graph, query_processor = get_services()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI services unavailable. Please try again later."
        )

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
        logger.error(
            "query_processing_failed",
            query=query_request.query[:100],  # Log first 100 chars only
            error=str(e)
        )
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
