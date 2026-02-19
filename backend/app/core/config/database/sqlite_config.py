"""
SQLite database configuration.
Handles local SQLite database setup and connection.
"""

from typing import Optional
from sqlalchemy import create_engine, Engine
from constants import DEFAULT_TENNIS_DB_PATH
from .base import DatabaseConfig


class SQLiteConfig(DatabaseConfig):
    """
    Configuration for SQLite database.
    Handles local SQLite database connections.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite configuration.

        Args:
            db_path: Database file path or connection string.
                    If None, uses DEFAULT_TENNIS_DB_PATH from constants.
        """
        self.db_path = db_path or DEFAULT_TENNIS_DB_PATH

        # Ensure proper URI format
        if not self.db_path.startswith("sqlite://"):
            if self.db_path.startswith("/"):
                self.db_path = f"sqlite:///{self.db_path}"
            else:
                self.db_path = f"sqlite:///{self.db_path}"

    def get_engine(self) -> Engine:
        """
        Create and return a SQLAlchemy Engine for SQLite.

        Returns:
            SQLAlchemy Engine instance
        """
        return create_engine(self.db_path)

    def get_db_type(self) -> str:
        """Get the database type identifier."""
        return "sqlite"

    def validate(self) -> bool:
        """
        Validate SQLite configuration.

        Returns:
            True if db_path is set and not empty
        """
        return self.db_path is not None and self.db_path.strip() != ""
