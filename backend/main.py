from fastapi import FastAPI, HTTPException
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

app = FastAPI(title="AskTennis API")

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
except Exception as e:
    print(f"Failed to initialize services: {e}")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sql_queries: List[str]
    data: List[Dict[str, Any]]
    conversation_flow: List[Any]

@app.get("/")
async def root():
    return {"message": "Welcome to AskTennis API"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
