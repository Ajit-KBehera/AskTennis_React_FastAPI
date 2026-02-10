"""
LangGraph construction and node definitions.
Extracted from agent_setup.py for better modularity.
"""

import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import ast
from agent.agent_state import AgentState
from typing import List, Any, Callable
from tennis.tennis_schema_pruner import TennisSchemaPruner
from tennis.tennis_prompts import TennisPromptBuilder

# import diskcache  # Replaced by CacheService
import hashlib
from services.cache_service import CacheFactory


class LangGraphBuilder:
    """
    Builder class for constructing the LangGraph agent.
    Centralizes all graph construction logic.

    Method execution order:
    1. __init__() - Initialize the graph builder
    2. build_graph() - Main entry point, builds and compiles the graph
    3. create_agent_node() - Creates agent node (called by build_graph)
    4. create_tool_node() - Creates tool node (called by build_graph)
    5. create_conditional_edges() - Creates routing logic (called by build_graph)
    """

    def __init__(
        self,
        tools: List[Any],
        llm_with_tools,
        prompt_template_factory: Callable[[str, str], str],
        db,
        full_schema: str,
    ):
        """
        Initialize the graph builder with dynamic schema pruning support.

        Args:
            tools: List of tools available to the agent
            llm_with_tools: LLM instance with bound tools
            prompt_template_factory: Function to create prompt template with schema (pruned_schema, user_query) -> system_prompt
            db: Database instance (for schema pruning)
            full_schema: Full database schema for pruning
        """
        self.tools = tools
        self.llm_with_tools = llm_with_tools
        self.prompt_template_factory = prompt_template_factory
        self.db = db
        self.full_schema = full_schema
        self.full_schema = full_schema
        self.schema_pruner = TennisSchemaPruner(full_schema)

        # Initialize abstract cache service
        self.cache = CacheFactory.get_service()

    def _has_sql_results(self, messages: List[Any]) -> bool:
        """
        Check if any message in the state contains SQL query results.

        Args:
            messages: List of messages from AgentState

        Returns:
            True if SQL results are present, False otherwise
        """
        for msg in messages:
            if isinstance(msg, AIMessage) and hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, str):
                    # Check if content looks like SQL results (list format)
                    content_stripped = content.strip()
                    if content_stripped.startswith("[") and content_stripped.endswith(
                        "]"
                    ):
                        try:
                            # Try to parse as a list to verify it's SQL results
                            parsed = ast.literal_eval(content_stripped)
                            if isinstance(parsed, list) and len(parsed) > 0:
                                # Check if it's a list of lists (typical SQL result format)
                                if isinstance(parsed[0], list):
                                    return True
                        except (ValueError, SyntaxError):
                            pass
        return False

    def _trim_messages_for_synthesis(self, messages: List[Any]) -> List[Any]:
        """
        Trim message history to only essential messages for final synthesis.
        Keeps only the original user query and the final SQL query results.
        Removes all intermediate tool calls and validations.

        Args:
            messages: List of messages from AgentState

        Returns:
            Trimmed list containing only user query and SQL results
        """
        trimmed = []

        # Find and keep the first HumanMessage (user query)
        first_human_msg = None
        for msg in messages:
            if isinstance(msg, HumanMessage):
                first_human_msg = msg
                break

        if first_human_msg:
            trimmed.append(first_human_msg)

        # Find and keep the last AIMessage with SQL results
        sql_result_msg = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, str):
                    content_stripped = content.strip()
                    if content_stripped.startswith("[") and content_stripped.endswith(
                        "]"
                    ):
                        try:
                            parsed = ast.literal_eval(content_stripped)
                            if isinstance(parsed, list) and len(parsed) > 0:
                                if isinstance(parsed[0], list):
                                    sql_result_msg = msg
                                    break
                        except (ValueError, SyntaxError):
                            pass

        if sql_result_msg:
            trimmed.append(sql_result_msg)

        # If we couldn't find SQL results, return original messages to avoid breaking the flow
        if len(trimmed) < 2:
            return messages

        return trimmed

    def build_graph(self):
        """
        Build the complete LangGraph.

        Returns:
            Compiled LangGraph instance
        """
        # Create the graph
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("agent", self.create_agent_node())
        graph.add_node("tools", self.create_tool_node())

        # Set entry point
        graph.set_entry_point("agent")

        # Add conditional edges
        graph.add_conditional_edges(
            "agent", self.create_conditional_edges(), {"tools": "tools", "end": END}
        )

        # Add edge from tools back to agent
        graph.add_edge("tools", "agent")

        # Compile with checkpointer (enables multi-turn context via thread_id)
        #
        # Defaults to a persistent SQLite checkpointer so conversation memory
        # survives server restarts. Set LANGGRAPH_CHECKPOINTER=memory to disable.
        checkpointer_type = os.getenv("LANGGRAPH_CHECKPOINTER", "sqlite").strip().lower()
        checkpointer = None

        if checkpointer_type == "memory":
            checkpointer = MemorySaver()
        else:
            # Default SQLite checkpoint location inside backend/ (repo-safe, durable).
            default_db_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "langgraph_checkpoints.sqlite")
            )
            conn_string = os.getenv("LANGGRAPH_CHECKPOINT_DB", "").strip()
            if not conn_string:
                conn_string = f"sqlite:///{default_db_path}"

            try:
                from langgraph.checkpoint.sqlite import SqliteSaver

                checkpointer = SqliteSaver.from_conn_string(conn_string)
            except Exception:
                # Fallback: if sqlite checkpointer isn't available, still run in-memory
                checkpointer = MemorySaver()

        runnable_graph = graph.compile(checkpointer=checkpointer)

        return runnable_graph

    def create_agent_node(self):
        """
        Create the agent node that calls the LLM with dynamic schema pruning.

        Returns:
            Agent node function
        """

        def call_agent(state: AgentState):
            """Calls the LLM to decide the next step with pruned schema."""
            messages = state["messages"]

            # Phase 1: Determine user_query and phase
            user_query = state.get("user_query")
            if not user_query:
                # First time, extract user query and set phase
                for msg in reversed(messages):
                    if isinstance(msg, HumanMessage):
                        content = msg.content
                        if isinstance(content, str):
                            user_query = content
                        elif isinstance(content, list) and len(content) > 0:
                            user_query = (
                                str(content[0].get("text", ""))
                                if isinstance(content[0], dict)
                                else str(content[0])
                            )
                        else:
                            user_query = str(content)
                        break
                phase = "query_generation"
            else:
                # Subsequent calls, get phase from state, default to query_generation
                phase = state.get("phase", "query_generation")

            # Phase 2: Check for phase transition
            if phase == "query_generation" and self._has_sql_results(messages):
                phase = "synthesis"

            # Phase 3: Act based on phase
            return_state = {"user_query": user_query}  # always preserve user_query

            if phase == "synthesis":
                # Use synthesis prompt with trimmed messages
                trimmed_messages = self._trim_messages_for_synthesis(messages)
                system_prompt = TennisPromptBuilder.create_synthesis_system_prompt()

                return_state["phase"] = "complete"  # Next state is 'complete'
                current_messages = trimmed_messages
            else:  # phase == "query_generation"
                # Prune schema, create dynamic prompt
                pruned_schema = self.schema_pruner.prune_schema(user_query)
                system_prompt = self.prompt_template_factory(pruned_schema, user_query)

                return_state["phase"] = "query_generation"
                return_state["pruned_schema"] = pruned_schema
                current_messages = messages

            # Create and invoke prompt
            prompt_template = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("human", "{messages}")]
            )

            response = self.llm_with_tools.invoke(
                prompt_template.format_prompt(messages=current_messages)
            )

            return_state["messages"] = [response]
            return return_state

        return call_agent

    def create_tool_node(self):
        """
        Create the tool node that executes tools.

        Returns:
            Tool node function
        """

        def tool_node(state: AgentState):
            """Custom tool node that executes tools."""
            messages = state["messages"]
            last_message = messages[-1]

            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    tool_name = tool_call["name"]
                    tool_input = tool_call["args"]

                    # Find the tool and execute it
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                # Check cache for sql_db_query
                                if tool_name == "sql_db_query":
                                    query = tool_input.get("query")
                                    if query:
                                        # Create a deterministic cache key
                                        cache_key = hashlib.md5(
                                            f"sql_query:{query}".encode()
                                        ).hexdigest()

                                        # Check cache
                                        cached_result = self.cache.get(cache_key)
                                        if cached_result:
                                            print(
                                                f"--- Serving from cache: {query[:50]}... ---"
                                            )
                                            return_state = {}
                                            return_state["sql_queries"] = [query]
                                            return_state["messages"] = [
                                                AIMessage(
                                                    content=str(cached_result),
                                                    tool_calls=[],
                                                )
                                            ]
                                            return_state["data_list"] = [cached_result]
                                            return return_state

                                result = tool.invoke(tool_input)
                                # print(tool_name, "\n\n", tool_input, "\n\n", result, "\n\n")
                                return_state = {}

                                # If it's a database query, truncate results to 100 rows maximum
                                if tool_name == "sql_db_query":
                                    query = tool_input.get("query")
                                    if query:
                                        return_state["sql_queries"] = [query]

                                    truncated = False

                                    # Check if result is a string representation of a list
                                    if isinstance(result, str):
                                        result_stripped = result.strip()
                                        if result_stripped.startswith(
                                            "["
                                        ) and result_stripped.endswith("]"):
                                            try:
                                                parsed_result = ast.literal_eval(
                                                    result_stripped
                                                )
                                                if (
                                                    isinstance(parsed_result, list)
                                                    and len(parsed_result) > 100
                                                ):
                                                    # Truncate to first 100 rows
                                                    truncated_result = parsed_result[
                                                        :100
                                                    ]
                                                    result = str(truncated_result)
                                                    truncated = True
                                            except (ValueError, SyntaxError):
                                                # If parsing fails, keep original result
                                                pass
                                    # Check if result is already a list
                                    elif isinstance(result, list) and len(result) > 100:
                                        result = result[:100]
                                        truncated = True

                                    # Add truncation note if results were truncated
                                    if truncated:
                                        result_str = str(result)
                                        truncation_note = "\n\n[Note: Results truncated to 100 rows. Original query returned more rows.]"
                                        result = result_str + truncation_note

                                    # Cache the result (TTL: 24 hours)
                                    if query:
                                        # Store original result in cache, not truncated one if possible?
                                        # Actually, for analysis we want the data.
                                        # Let's cache the RESULT that we are returning.
                                        cache_key = hashlib.md5(
                                            f"sql_query:{query}".encode()
                                        ).hexdigest()
                                        self.cache.set(cache_key, result, expire=86400)

                                # If sql_db_query_checker returned formatted SQL, add a hint to execute
                                if (
                                    tool_name == "sql_db_query_checker"
                                    and result
                                    and "SELECT" in str(result).upper()
                                ):
                                    result_str = str(result)
                                    # Extract SQL from markdown code blocks if present
                                    if "```" in result_str:
                                        # Add hint message
                                        hint = "\n\n[Note: Query validation successful. Use sql_db_query with this exact query to retrieve data.]"
                                        result = result_str + hint

                                return_state["messages"] = [
                                    AIMessage(content=str(result), tool_calls=[])
                                ]
                                return_state["data_list"] = [result]
                                return return_state
                            except Exception as e:
                                return {
                                    "messages": [
                                        AIMessage(
                                            content=f"Error executing {tool_name}: {str(e)}",
                                            tool_calls=[],
                                        )
                                    ]
                                }

            return {"messages": []}

        return tool_node

    def create_conditional_edges(self):
        """
        Create the conditional edges function for the graph.

        Returns:
            Conditional edges function
        """

        def should_continue(state: AgentState):
            """Decide whether to continue with tools or finish."""
            # The ReAct agent returns an AIMessage with tool_calls if it needs to act.
            if (
                isinstance(state["messages"][-1], AIMessage)
                and hasattr(state["messages"][-1], "tool_calls")
                and state["messages"][-1].tool_calls
            ):
                return "tools"
            return "end"

        return should_continue
