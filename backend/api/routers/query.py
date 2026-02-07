"""
Query router - AI-powered natural language tennis queries.

Endpoints:
    POST /api/query - Process natural language questions using LangGraph agent
    GET /api/query/history - List saved query results for the logged-in user
"""

import asyncio
import traceback
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
import structlog

from config.auth import get_current_user
from config.rate_limiter import limiter, get_query_rate_limit_string
from agent.agent_factory import setup_langgraph_agent
from services.query_service import QueryProcessor
from services.auth_db_service import AuthDBService
from constants import QUERY_TIMEOUT_SECONDS
from utils.error_utils import get_500_detail

# =============================================================================
# SETUP
# =============================================================================

router = APIRouter()
logger = structlog.get_logger()

# Lazy-loaded service singletons
_agent_graph = None
_query_processor = None
_auth_db = AuthDBService()


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


# Max length for query text (avoids abuse and keeps history bounded)
QUERY_MAX_LENGTH = 2000


class QueryRequest(BaseModel):
    """Request model for AI query endpoint."""

    query: str = Field(..., max_length=QUERY_MAX_LENGTH)

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        """Validate that query is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
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
    username: str = Depends(get_current_user),
    db: Session = Depends(_auth_db.get_db),
):
    """
    AI query endpoint - processes natural language questions about tennis.
    Results are saved to the logged-in user's query history.

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
            status_code=503, detail="AI services unavailable. Please try again later."
        )

    try:
        results = await asyncio.wait_for(
            run_in_threadpool(
                query_processor.handle_user_query,
                query_request.query,
                agent_graph,
            ),
            timeout=QUERY_TIMEOUT_SECONDS,
        )

        # Save to user's query history
        user = _auth_db.get_user_by_username(db, username)
        if user:
            _auth_db.save_query_history(
                db,
                user_id=user.id,
                query_text=query_request.query,
                sql_queries=results.get("sql_queries", []),
                answer=results.get("answer", ""),
                data=results.get("data", []),
                conversation_flow=results.get("conversation_flow", []),
            )

        return QueryResponse(
            answer=results.get("answer", ""),
            sql_queries=results.get("sql_queries", []),
            data=results.get("data", []),
            conversation_flow=results.get("conversation_flow", []),
        )

    except asyncio.TimeoutError:
        logger.warning(
            "query_timeout",
            query_preview=query_request.query[:80],
        )
        raise HTTPException(
            status_code=504,
            detail="Query took too long. Try a simpler question or try again.",
        )
    except Exception as e:
        logger.error(
            "query_processing_failed",
            query=query_request.query[:100],
            error=str(e),
        )
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=get_500_detail(e),
        )


@router.get("/query/history")
async def get_query_history(
    username: str = Depends(get_current_user),
    db: Session = Depends(_auth_db.get_db),
    limit: int = 50,
):
    """
    Return the logged-in user's saved query history (query text, SQL, answer, data).
    Most recent first, up to `limit` items (default 50).
    """
    user = _auth_db.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    history = _auth_db.get_query_history_for_user(db, user.id, limit=min(limit, 100))
    return {"history": history}
