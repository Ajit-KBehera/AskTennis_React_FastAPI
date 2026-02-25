"""
LLM setup and configuration for the tennis AI agent.
Extracted from agent_setup.py for better modularity.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import (
    QuerySQLDatabaseTool,
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
)
import re
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
        api_key: str, db_config: DatabaseConfig, model: str, temperature: float
    ) -> tuple[ChatGoogleGenerativeAI, SQLDatabase, List]:
        """
        Setup all LLM components in one call.

        Args:
            api_key: Google API key
            db_config: DatabaseConfig instance (SQLiteConfig or CloudSQLConfig)
            model: Model name
            temperature: Temperature setting

        Returns:
            Tuple of (llm, db, tools)
        """
        # Create LLM
        llm = LLMFactory.create_llm(
            api_key=api_key, model=model, temperature=temperature
        )

        # Create database connection from app.core.config
        db = LLMFactory.create_database_connection_from_config(db_config)

        # Create tools directly from database
        tools = LLMFactory.create_sql_tools(db)

        return llm, db, tools

    @staticmethod
    def create_llm(
        api_key: str, model: str, temperature: float
    ) -> ChatGoogleGenerativeAI:
        """
        Create a ChatGoogleGenerativeAI instance.

        Args:
            api_key: Google API key
            model: Model name
            temperature: Temperature setting

        Returns:
            Configured ChatGoogleGenerativeAI instance
        """
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

            # Check for forbidden keywords (for security/safety)
            forbidden = ["DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "TRUNCATE"]
            for word in forbidden:
                # Use regex for whole word match to avoid false positives like 'updated_at'
                if re.search(rf"\b{word}\b", query_upper):
                    return f"Error: Forbidden keyword detected: {word}"

            # Return formatted query (the actual validation happens when executing)
            # This tool mainly serves to format and prepare the query
            return f"```sql\n{query}\n```"

        return [
            CustomQuerySQLDatabaseTool(db=db),
            InfoSQLDatabaseTool(db=db),
            ListSQLDatabaseTool(db=db),
            sql_db_query_checker,
        ]
