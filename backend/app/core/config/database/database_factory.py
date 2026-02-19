"""
Database factory for creating appropriate database configuration instances.
Provides a single source of truth for database type detection and configuration.
"""

from typing import Optional
import os
from constants import (AUTH_DB_NAME, AUTH_DB_USER, AUTH_DB_PASSWORD,
                       TENNIS_DB_NAME, TENNIS_DB_USER, TENNIS_DB_PASSWORD,
                       AUTH_DB_FILE_NAME, DEFAULT_AUTH_DB_PATH)

from .base import DatabaseConfig
from .sqlite_config import SQLiteConfig
from .duckdb_config import DuckDBConfig
from .cloud_sql_config import CloudSQLConfig


class DatabaseFactory:
    """
    Factory class for creating database configuration instances.
    Automatically detects database type from environment/secrets.
    """

    @staticmethod
    def _is_cloud_sql_config() -> bool:
        """
        Check if Cloud SQL configuration is available.
        Only checks environment variables in the FastAPI version.

        Returns:
            True if Cloud SQL configuration is detected, False otherwise
        """
        # Fall back to environment variable (loaded from .env file or system env vars)
        if os.getenv("INSTANCE_CONNECTION_NAME"):
            return True

        return False

    @staticmethod
    def create_config(
        db_path: Optional[str] = None,
        force_sqlite: bool = False,
        force_cloud_sql: bool = False,
    ) -> DatabaseConfig:
        """
        Create a database configuration instance based on environment settings.

        Args:
            db_path: Optional database path (for SQLite/DuckDB). If None, uses DEFAULT_TENNIS_DB_PATH.
            force_sqlite: Force SQLite configuration even if Cloud SQL is available
            force_cloud_sql: Force Cloud SQL configuration (will fail if config is missing)

        Returns:
            DatabaseConfig instance (SQLiteConfig, DuckDBConfig, or CloudSQLConfig)

        Raises:
            ValueError: If force_cloud_sql is True but Cloud SQL config is missing
        """
        # Check environment for explicit DB type
        db_type = os.getenv("DB_TYPE", "").lower()

        # Check if we should use Cloud SQL
        use_cloud_sql = False

        if force_cloud_sql:
            use_cloud_sql = True
        elif not force_sqlite and db_type != "sqlite" and db_type != "duckdb":
            use_cloud_sql = DatabaseFactory._is_cloud_sql_config()

        if use_cloud_sql:
            # Create Cloud SQL configuration
            config = CloudSQLConfig(
                db_name=TENNIS_DB_NAME,
                db_user=TENNIS_DB_USER,
                db_password=TENNIS_DB_PASSWORD,
            )
            if not config.validate():
                if force_cloud_sql:
                    raise ValueError(
                        "Cloud SQL configuration is required but missing. "
                        "Please set INSTANCE_CONNECTION_NAME, DB_USER, and DB_PASSWORD."
                    )
                # Fall back to SQLite if not forced
                print(
                    "WARNING: Cloud SQL configuration incomplete, falling back to SQLite"
                )
                return SQLiteConfig(db_path)
            return config
        elif db_type == "duckdb" or (db_path and db_path.startswith("duckdb://")):
            # Create DuckDB configuration
            return DuckDBConfig(db_path)
        else:
            # Create SQLite configuration (default)
            return SQLiteConfig(db_path)

    @staticmethod
    def create_auth_config(force_sqlite: bool = False) -> DatabaseConfig:
        """
        Create a database configuration specifically for authentication/identity.
        Uses Cloud SQL if available, otherwise falls back to SQLite.
        """
        if not force_sqlite and DatabaseFactory._is_cloud_sql_config():
            return DatabaseFactory.create_cloud_sql_config(
                db_name=AUTH_DB_NAME,
                db_user=AUTH_DB_USER,
                db_password=AUTH_DB_PASSWORD,
            )
        
        # Fallback to local auth sqlite file
        auth_db_path = os.getenv("AUTH_DB_PATH", DEFAULT_AUTH_DB_PATH)
        return SQLiteConfig(auth_db_path)

    @staticmethod
    def create_sqlite_config(db_path: Optional[str] = None) -> SQLiteConfig:
        """
        Create a SQLite configuration instance.
        """
        return SQLiteConfig(db_path)

    @staticmethod
    def create_cloud_sql_config(
        instance_connection_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        db_name: Optional[str] = None,
        db_engine: str = "postgresql",
    ) -> CloudSQLConfig:
        """
        Create a Cloud SQL configuration instance.
        """
        return CloudSQLConfig(
            instance_connection_name=instance_connection_name,
            db_user=db_user,
            db_password=db_password,
            db_name=db_name,
            db_engine=db_engine,
        )
