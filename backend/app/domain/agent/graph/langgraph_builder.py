"""
LangGraph construction and node definitions.
Extracted from agent_setup.py for better modularity.
"""

import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
import ast
from app.domain.agent.agent_state import AgentState
from typing import List, Any, Callable, Dict, cast
from app.domain.tennis.tennis_schema_pruner import TennisSchemaPruner
from app.domain.tennis.tennis_prompts import TennisPromptBuilder

# import diskcache  # Replaced by CacheService
import hashlib
from app.infrastructure.cache.redis_cache import CacheFactory


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
                            if isinstance(parsed, list):
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
                            if isinstance(parsed, list):
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
        graph = StateGraph(AgentState) # type: ignore

        # Add nodes
        graph.add_node("agent", self.create_agent_node()) # type: ignore
        graph.add_node("tools", self.create_tool_node()) # type: ignore

        # Set entry point
        graph.set_entry_point("agent")

        # Add conditional edges
        graph.add_conditional_edges(
            "agent", self.create_conditional_edges(), {"tools": "tools", "end": END}
        ) # type: ignore

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
                from langgraph.checkpoint.sqlite import SqliteSaver # type: ignore

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

        def call_agent(state: AgentState) -> Dict[str, Any]:
            """Calls the LLM to decide the next step with pruned schema."""
            messages = state["messages"]

            # Phase 1: Determine user_query from the most recent HumanMessage
            last_human_index = -1
            user_query = ""
            for i, msg in enumerate(messages):
                if isinstance(msg, HumanMessage):
                    last_human_index = i
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

            current_turn_messages = (
                messages[last_human_index:] if last_human_index >= 0 else messages
            )

            # Phase 2: Check for phase transition based on current turn messages
            has_sql = self._has_sql_results(current_turn_messages)
            current_tool_turns = len(
                [
                    m
                    for m in current_turn_messages
                    if isinstance(m, AIMessage) and getattr(m, "tool_calls", None)
                ]
            )

            # If SQL query results are present or max tool turns reached, transition to synthesis
            if has_sql or current_tool_turns >= 3:
                phase = "synthesis"
            else:
                phase = "query_generation"

            # Phase 3: Act based on phase
            return_state: Dict[str, Any] = {"user_query": user_query}

            if phase == "synthesis":
                # Use synthesis prompt with trimmed messages from current turn
                trimmed_messages = self._trim_messages_for_synthesis(current_turn_messages)
                system_prompt = TennisPromptBuilder.create_synthesis_system_prompt()

                return_state["phase"] = "complete"  # Next state is 'complete'
                current_messages = trimmed_messages
            else:  # phase == "query_generation"
                # Prune schema, create dynamic prompt
                pruned_schema = self.schema_pruner.prune_schema(user_query or "")
                system_prompt = self.prompt_template_factory(pruned_schema, user_query or "")

                return_state["phase"] = "query_generation"
                return_state["pruned_schema"] = pruned_schema
                current_messages = current_turn_messages

            # Create and invoke prompt
            prompt_template = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("human", "{messages}")]
            )

            response = self.llm_with_tools.invoke(
                prompt_template.format_prompt(messages=current_messages)
            )

            # Auto-extract tool calls if the local model rendered them as text/JSON in content
            self._extract_tool_calls_from_content(response)

            return_state["messages"] = cast(List[BaseMessage], [response])
            return return_state

        return call_agent

    def _extract_tool_calls_from_content(self, message: Any) -> None:
        """
        Extract tool calls if the model outputted them as JSON/text in content
        instead of the structured tool_calls field (common with open-weights/local models).
        """
        if not isinstance(message, AIMessage) or getattr(message, "tool_calls", None):
            return
        content = message.content
        if not isinstance(content, str):
            return
        text = content.strip()
        if text.startswith("```json"):
            text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        elif text.startswith("```"):
            text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        if text.startswith("{") and not text.endswith("}"):
            text += "}"

        import json
        import uuid
        import re

        data = None
        if "{" in text and "}" in text:
            try:
                data = json.loads(text)
            except Exception:
                pass

        if not data or not isinstance(data, dict) or "name" not in data:
            # Fallback to regex pattern matching for {"name": "tool_name", ...}
            m_name = re.search(r'"name":\s*"([^"]+)"', text)
            if m_name:
                tool_name = m_name.group(1)
                m_query = re.search(r'"query":\s*"([^"]+)"', text)
                m_terms = re.search(r'"terms":\s*(\[[^\]]*\]|"[^"]*")', text)
                args: Dict[str, Any] = {}
                if m_query:
                    args = {"query": m_query.group(1)}
                elif m_terms:
                    try:
                        args = {"terms": json.loads(m_terms.group(1))}
                    except Exception:
                        args = {"terms": m_terms.group(1)}
                data = {"name": tool_name, "arguments": args}

        if isinstance(data, dict) and "name" in data:
            args = data.get("arguments", data.get("parameters", {}))
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {"query": args}
            message.tool_calls = [
                {
                    "name": data["name"],
                    "args": args if isinstance(args, dict) else {"query": args},
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                }
            ]
            # Clear raw tool call JSON from text content so it is not treated as final text answer
            message.content = ""

    def create_tool_node(self):
        """
        Create the tool node that executes tools.

        Returns:
            Tool node function
        """

        def tool_node(state: AgentState) -> Dict[str, Any]:
            """Custom tool node that executes tools."""
            print("--- Entering tool_node ---")
            messages = state["messages"]
            last_message = messages[-1]
            
            truncated_result = None
            parsed_result = None
            truncated = False

            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    tool_name = tool_call["name"]
                    tool_input = tool_call["args"]
                    print(f"--- Calling tool: {tool_name} ---")

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

                                # Prepare state updates
                                # We store the RAW result (possibly truncated but unadorned) in data_list
                                # and the potentially annotated string in the message content for the AI.
                                return_state["messages"] = [
                                    AIMessage(content=str(result), tool_calls=[])
                                ]
                                
                                # data_list should be a list of dicts for the frontend to parse correctly.
                                # If it was sql_db_query, we prefer the raw list form to avoid re-parsing strings with notes.
                                if tool_name == "sql_db_query":
                                    data_to_send: Any = []
                                    if truncated_result is not None:
                                        data_to_send = truncated_result
                                    elif parsed_result is not None:
                                        data_to_send = parsed_result
                                    elif isinstance(result, list):
                                        data_to_send = result
                                    else:
                                        # Fallback to parsing result if possible
                                        try:
                                            # result is likely a string here
                                            data_to_send = ast.literal_eval(str(result))
                                        except Exception:
                                            data_to_send = [result]
                                            
                                    return_state["data_list"] = data_to_send
                                else:
                                    # For other tools, just pass result as is (QueryProcessor will safe_parse)
                                    return_state["data_list"] = [result] if not isinstance(result, list) else result
                                
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
            messages = state.get("messages", [])
            if not messages:
                return "end"

            last_message = messages[-1]
            if (
                isinstance(last_message, AIMessage)
                and hasattr(last_message, "tool_calls")
                and last_message.tool_calls
            ):
                return "tools"
            return "end"

        return should_continue
