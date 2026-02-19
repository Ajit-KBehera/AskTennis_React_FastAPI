"""
DuckDB database configuration.
Handles local DuckDB database setup and connection with read-only support.
"""

from typing import Optional
from sqlalchemy import create_engine, Engine
from .base import DatabaseConfig


class DuckDBConfig(DatabaseConfig):
    """
    Configuration for DuckDB database.
    Handles DuckDB connections with specific settings for concurrency.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize DuckDB configuration.

        Args:
            db_path: Database connection string (duckdb:///path/to/db).
                    If None, converts DEFAULT_DB_PATH to duckdb scheme.
        """
        if db_path:
            self.db_path = db_path
        else:
            # Convert default sqlite path to duckdb if needed, or use as is if it's just a path
            # DEFAULT_TENNIS_DB_PATH is usually "sqlite:///{TENNIS_DB_FILE_PATH}"
            # We need to extract the file path and use "duckdb:///"
            from constants import TENNIS_DB_FILE_PATH

            self.db_path = f"duckdb:///{TENNIS_DB_FILE_PATH}"

        # Ensure proper URI format for SQLAlchemy
        if not self.db_path.startswith("duckdb://"):
            if self.db_path.startswith("/"):
                self.db_path = f"duckdb:///{self.db_path}"
            else:
                self.db_path = f"duckdb:///{self.db_path}"

    def get_engine(self) -> Engine:
        """
        Create and return a SQLAlchemy Engine for DuckDB.
        Configures the engine with read_only=True to allow concurrent reads.

        Returns:
            SQLAlchemy Engine instance
        """
        # DuckDB-specific configuration
        # read_only=True creates a read-only connection which allows multiple processes/threads
        # to read simultaneously without locking the file.
        connect_args = {"read_only": True, "config": {"access_mode": "READ_ONLY"}}

        return create_engine(self.db_path, connect_args=connect_args)

    def get_db_type(self) -> str:
        """Get the database type identifier."""
        return "duckdb"

    def validate(self) -> bool:
        """
        Validate DuckDB configuration.

        Returns:
            True if db_path is configured
        """
        return self.db_path is not None and "duckdb" in self.db_path
