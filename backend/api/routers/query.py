"""
Query router - AI-powered natural language tennis queries.
Endpoints:
  - POST /api/query - Process natural language questions using LangGraph agent
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Dict, Any

from config.rate_limiter import limiter, get_query_rate_limit_string
from config.auth import get_api_key
from agent.agent_factory import setup_langgraph_agent
from services.query_service import QueryProcessor

router = APIRouter()


# Request/Response models
class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sql_queries: List[str]
    data: List[Dict[str, Any]]
    conversation_flow: List[Any]


# Initialize services
try:
    agent_graph = setup_langgraph_agent()
    query_processor = QueryProcessor()
    print("✅ Query router services initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize query services: {e}")
    agent_graph = None
    query_processor = None


@router.post("/query", response_model=QueryResponse)
@limiter.limit(get_query_rate_limit_string())
async def process_query(
    request: Request,
    query_request: QueryRequest,
    api_key: str = Depends(get_api_key)
):
    """
    AI query endpoint - processes natural language questions about tennis.
    Uses LangGraph agent to generate SQL queries and return structured results.
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
