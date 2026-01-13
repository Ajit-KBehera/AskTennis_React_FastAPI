"""
Query processing service for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Moved from ui/processing/ for better architectural separation.
"""

import uuid
import ast
from langchain_core.messages import HumanMessage
from typing import Dict, Any, List

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
            config = {"configurable": {"thread_id": session_id}}
            initial_state = {
                "messages": [HumanMessage(content=user_question)]
            }
            response = agent_graph.invoke(
                initial_state,
                config=config,
                recursion_limit=100
            ) 

            conversation_messages = response.get("messages", [])
            sql_queries = response.get("sql_queries", [])
            data_list = response.get("data_list", [])
            
            def safe_parse(val):
                if not val:
                    return []
                
                # Case 1: Already a list
                if isinstance(val, list):
                    # Check if it's a list containing a stringified list (common LLM pattern)
                    if len(val) == 1 and isinstance(val[0], str) and val[0].strip().startswith('['):
                        return safe_parse(val[0])
                    # Otherwise return as is
                    return val
                
                # Case 2: String that needs parsing
                if isinstance(val, str):
                    val = val.strip()
                    if not val:
                        return []
                    try:
                        parsed = ast.literal_eval(val)
                        return safe_parse(parsed) # Recurse if needed
                    except Exception:
                        try:
                            import json
                            parsed = json.loads(val)
                            return safe_parse(parsed) # Recurse if needed
                        except Exception:
                            return [val] if val else []
                
                # Case 3: Single dictionary (wrap it)
                if isinstance(val, dict):
                    return [val]
                
                return []

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
                "conversation_flow": [msg.content for msg in conversation_messages],
                "session_id": session_id
            }
            
        except Exception as e:
            raise Exception(f"An error occurred while processing your request: {e}")
    
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