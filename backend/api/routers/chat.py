"""
Chat router - handles AI chat interactions.
Endpoint: POST /api/chat

Wraps the existing QueryProcessor to provide chat-style responses.
"""

from fastapi import APIRouter, HTTPException
import logging
import uuid

from services.query_service import QueryProcessor
from api.models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Global query processor and agent (will be set from main.py)
query_processor = None
agent_graph = None


def set_dependencies(processor: QueryProcessor, agent):
    """
    Set the query processor and agent graph dependencies.
    Called from main.py after initialization.
    """
    global query_processor, agent_graph
    query_processor = processor
    agent_graph = agent


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message to the AI agent and get a response.
    
    This endpoint uses the same QueryProcessor as the /query endpoint,
    but returns a simpler response format optimized for chat interfaces.
    
    Args:
        request: ChatRequest with query and optional session_id
        
    Returns:
        ChatResponse with answer, session_id, and optional summary
    """
    if query_processor is None or agent_graph is None:
        raise HTTPException(
            status_code=500, 
            detail="Chat service not initialized. Agent or processor missing."
        )
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())[:8]
        
        logger.info(f"Processing chat query: '{request.query[:50]}...' (session: {session_id})")
        
        # Use existing QueryProcessor (same as /query endpoint)
        results = query_processor.handle_user_query(
            user_question=request.query,
            agent_graph=agent_graph,
            session_id=session_id
        )
        
        # Extract conversation flow for summary
        conversation_flow = results.get("conversation_flow", [])
        summary = None
        if len(conversation_flow) > 1:
            # Create a simple summary from conversation
            summary = f"Query processed with {len(results.get('sql_queries', []))} SQL queries"
        
        # Return simplified response for chat interface
        return ChatResponse(
            answer=results["answer"],
            session_id=session_id,
            summary=summary,
            sql_debug=None  # Can include SQL queries if needed for debugging
        )
    
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat query: {str(e)}"
        )
