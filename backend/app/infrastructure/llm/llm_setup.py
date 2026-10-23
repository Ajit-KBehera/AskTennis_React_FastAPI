"""
LLM setup and configuration for the tennis AI agent.
Extracted from agent_setup.py for better modularity.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import (
    QuerySQLDatabaseTool,
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
)
from langchain_core.tools import tool
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Dict, Any, List, Optional, Union, Sequence, cast

from app.infrastructure.database.base import DatabaseConfig


class CustomQuerySQLDatabaseTool(QuerySQLDatabaseTool):
    """
    Custom QuerySQLDatabaseTool that includes column names in results.
    Overrides the _run method to pass include_columns=True to run_no_throw.
    """

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Sequence[Dict[str, Any]]]:
        """Execute the query with column names included, return the results or an error message."""
        return cast(Union[str, Sequence[Dict[str, Any]]], self.db.run_no_throw(query, include_columns=True))


class LLMFactory:
    """
    Factory class for creating LLM and database components.
    Centralizes LLM and database setup logic.
    """

    @staticmethod
    def setup_llm_components(
        api_key: Optional[str],
        db_config: DatabaseConfig,
        model: str,
        temperature: float,
        gcp_project_id: Optional[str] = None,
        gcp_location: Optional[str] = None,
        provider: str = "gemini",
        base_url: Optional[str] = None,
    ) -> tuple[BaseChatModel, SQLDatabase, List]:
        """
        Setup all LLM components in one call.

        Args:
            api_key: Google API key (optional if using Ollama or Vertex AI)
            db_config: DatabaseConfig instance (SQLiteConfig or CloudSQLConfig)
            model: Model name
            temperature: Temperature setting
            gcp_project_id: Optional GCP project ID for Vertex AI
            gcp_location: Optional GCP region/location for Vertex AI
            provider: LLM provider ("ollama" or "gemini")
            base_url: Base URL for Ollama service

        Returns:
            Tuple of (llm, db, tools)
        """
        # Create LLM
        llm = LLMFactory.create_llm(
            api_key=api_key,
            model=model,
            temperature=temperature,
            gcp_project_id=gcp_project_id,
            gcp_location=gcp_location,
            provider=provider,
            base_url=base_url,
        )

        # Create database connection from app.core.config
        db = LLMFactory.create_database_connection_from_config(db_config)

        # Create tools directly from database
        tools = LLMFactory.create_sql_tools(db)

        return llm, db, tools

    @staticmethod
    def create_llm(
        api_key: Optional[str] = None,
        model: str = "qwen2.5-coder:7b",
        temperature: float = 0.0,
        gcp_project_id: Optional[str] = None,
        gcp_location: Optional[str] = None,
        provider: str = "gemini",
        base_url: Optional[str] = None,
    ) -> BaseChatModel:
        """
        Create a BaseChatModel instance (Ollama, Gemini, or Vertex AI).

        Args:
            api_key: Google API key (if using Gemini)
            model: Model name (e.g., qwen2.5-coder:7b or gemini-1.5-flash)
            temperature: Temperature setting
            gcp_project_id: Optional GCP project ID for Vertex AI
            gcp_location: Optional GCP region/location for Vertex AI
            provider: LLM provider name ("ollama", "gemini")
            base_url: Optional host URL for Ollama (defaults to http://localhost:11434)

        Returns:
            Configured BaseChatModel instance
        """
        if provider == "ollama":
            try:
                from langchain_ollama import ChatOllama
            except ImportError:
                from langchain_community.chat_models import ChatOllama

            return ChatOllama(
                model=model,
                base_url=base_url or "http://localhost:11434",
                temperature=temperature,
            )
        elif gcp_project_id:
            from langchain_google_vertexai import ChatVertexAI

            return ChatVertexAI(
                model=model,
                project=gcp_project_id,
                location=gcp_location or "global",
                temperature=temperature,
            )
        else:
            return ChatGoogleGenerativeAI(
                model=model, google_api_key=api_key, temperature=temperature
            )

    @staticmethod
    def create_database_connection_from_config(
        db_config: DatabaseConfig,
    ) -> SQLDatabase:
        """
        Create a database connection from a DatabaseConfig instance.

        Args:
            db_config: DatabaseConfig instance (SQLiteConfig or CloudSQLConfig)

        Returns:
            SQLDatabase instance
        """
        db_engine = db_config.get_engine()
        return SQLDatabase(engine=db_engine)

    @staticmethod
    def create_sql_tools(db: SQLDatabase) -> List:
        """
        Create SQL tools directly from the database.
        This replaces SQLDatabaseToolkit which has compatibility issues.

        Args:
            db: SQLDatabase instance

        Returns:
            List of SQL tools
        """

        # Create custom query checker tool
        @tool
        def sql_db_query_checker(query: str) -> str:
            """
            Validates and formats SQL query syntax.
            Returns the formatted query if valid, or an error message if invalid.
            Use this tool ONCE to validate a query before executing it with sql_db_query.

            Args:
                query: SQL query string to validate

            Returns:
                Formatted SQL query if valid, or error message if invalid
            """
            # Simple validation: check for basic SQL keywords and structure
            query_upper = query.upper().strip()

            # Remove markdown code blocks if present
            if "```" in query:
                lines = query.split("\n")
                query = "\n".join(
                    [line for line in lines if not line.strip().startswith("```")]
                )
                query = query.strip()

            # Basic validation checks
            if not query_upper.startswith(("SELECT", "WITH")):
                return (
                    f"Error: Query must start with SELECT or WITH. Got: {query[:50]}..."
                )

            # Return formatted query (the actual validation happens when executing)
            # This tool mainly serves to format and prepare the query
            return f"```sql\n{query}\n```"

        return [
            CustomQuerySQLDatabaseTool(db=db),
            InfoSQLDatabaseTool(db=db),
            ListSQLDatabaseTool(db=db),
            sql_db_query_checker,
        ]
