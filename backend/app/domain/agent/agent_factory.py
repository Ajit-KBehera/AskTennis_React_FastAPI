"""
Main factory for creating and configuring the tennis AI agent.
Orchestrates all components to create the complete LangGraph agent.
"""

import functools
import logging
from app.core.config.config import Config
from app.infrastructure.llm.llm_setup import LLMFactory
from app.domain.tennis.tennis_core import TennisMappingTools, TennisPromptBuilder
from app.domain.agent.graph.langgraph_builder import LangGraphBuilder

# Set up logging
logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def setup_langgraph_agent():
    """
    Main factory function to create the complete LangGraph agent.
    This is cached to avoid re-initializing on every interaction.

    Returns:
        Compiled LangGraph agent ready for use
    """
    print("--- Initializing LangGraph Agent with Gemini ---")

    # Load unified application configuration (includes database setup)
    config = Config()

    # Validate configuration
    if not config.validate_config():
        raise Exception("Invalid configuration detected!")

    # Create LLM components
    llm, db, sql_tools = LLMFactory.setup_llm_components(
        api_key=config.api_key,
        db_config=config.db_config,
        model=config.model_name,
        temperature=config.temperature,
    )

    # Add tennis mapping tools (cached via @lru_cache on parent function)
    tennis_mapping_tools = TennisMappingTools.create_all_mapping_tools()
    all_tools = sql_tools + tennis_mapping_tools

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(all_tools)

    # Get full schema for dynamic pruning
    full_schema = db.get_table_info()

    # Create prompt template factory (returns a function that creates prompts with pruned schema)
    def create_prompt_template(pruned_schema: str, user_query: str = ""):
        """Factory function to create prompt templates with dynamic schema."""
        return TennisPromptBuilder.create_query_system_prompt(pruned_schema, user_query)

    # Build graph with dynamic schema support
    graph_builder = LangGraphBuilder(
        all_tools, llm_with_tools, create_prompt_template, db, full_schema
    )

    # Build the runnable LangGraph agent with all dependencies
    runnable_graph = graph_builder.build_graph()

    print("--- LangGraph Agent Compiled Successfully with Gemini ---")
    return runnable_graph
