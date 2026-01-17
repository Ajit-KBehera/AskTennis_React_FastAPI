"""
Query processing service for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Moved from ui/processing/ for better architectural separation.
"""

import uuid
import ast
from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
from utils.string_utils import safe_parse

class QueryProcessor:
    """
    Centralized query processing class for tennis queries.
    Handles agent interaction, response processing, and error handling.
    """
    
    def __init__(self):
        """
        Initialize the query processor.
        """
        pass
    
    def handle_user_query(self, user_question: str, agent_graph, session_id: str = None) -> Dict[str, Any]:
        """Handle user query processing and return results."""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        try:
            config = {
                "configurable": {"thread_id": session_id},
                "recursion_limit": 100
            }
            initial_state = {
                "messages": [HumanMessage(content=user_question)]
            }
            response = agent_graph.invoke(
                initial_state,
                config=config
            ) 

            conversation_messages = response.get("messages", [])
            sql_queries = response.get("sql_queries", [])
            data_list = response.get("data_list", [])
            
            # safe_parse moved to backend.utils.string_utils

            sql_queries = safe_parse(sql_queries)
            data_list = safe_parse(data_list)
            
            # Final validation: Ensure it's a list of dicts for data
            if not isinstance(data_list, list):
                data_list = []
            data_list = [d for d in data_list if isinstance(d, dict)]
            
            # Ensure sql_queries is a list of strings
            if not isinstance(sql_queries, list):
                sql_queries = []
            sql_queries = [str(s) for s in sql_queries if s]
            
            final_answer = self.process_agent_response(conversation_messages)
            
            return {
                "answer": final_answer,
                "sql_queries": sql_queries,
                "data": data_list,
                "conversation_flow": self._serialize_messages(conversation_messages),
                "session_id": session_id
            }
            
        except Exception as e:
            raise Exception(f"An error occurred while processing your request: {e}")
    
    def _serialize_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """Serialize messages for frontend consumption."""
        serialized = []
        for msg in messages:
            msg_data = {
                "type": type(msg).__name__,
                "content": msg.content,
            }
            # Include tool calls if present (mostly for AIMessage)
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                msg_data["tool_calls"] = [
                    {"name": tc.get("name"), "args": tc.get("args")} 
                    for tc in msg.tool_calls
                ]
            serialized.append(msg_data)
        return serialized
    
    def process_agent_response(self, conversation_messages: List[Any]) -> str:
        """Process and format the agent's response."""
        if not conversation_messages:
            return ""
            
        last_message = conversation_messages[-1]
        
        if isinstance(last_message.content, list) and last_message.content:
            final_answer = last_message.content[0].get("text", "")
        else:
            final_answer = last_message.content
        
        return final_answer