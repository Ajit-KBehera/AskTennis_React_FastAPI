"""
Agent state definitions for LangGraph.
Contains the enhanced AgentState TypedDict with more detailed state tracking.
"""
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict, total=False):
    """
    Defines the state structure for the LangGraph agent.

    Fields:
    - messages: Conversation messages (always present, accumulates)
    - user_query: Latest user-submitted question for the agent to answer.
    - phase: Current processing phase. Typical values: "query_generation", "synthesis", "complete".
    - sql_queries: List of SQL queries executed during the agent's processing.
    - pruned_schema: Current pruned schema of the database relevant to the current user query.
    """
    # Core conversation (always present)
    messages: Annotated[List[BaseMessage], operator.add]

    # User query is the latest user-submitted question for the agent to answer.
    user_query: Optional[str]

    # Phase is the current step in processing. Typical values: "query_generation", "synthesis", "complete".
    phase: Optional[str]

    # SQL queries is a list of SQL queries executed during the agent's processing.
    sql_queries: Annotated[List[str], operator.add]

    # Pruned schema is the pruned schema of the database relevant to the current user query.
    pruned_schema: Optional[str]

    # Data list is a list of data returned from the agent's processing.
    data_list: Optional[List[dict]]