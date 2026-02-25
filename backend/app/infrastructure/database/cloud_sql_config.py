"""
Cloud SQL database configuration.
Handles GCP Cloud SQL (PostgreSQL/MySQL) database setup and connection.
"""

from typing import Optional, cast
import structlog
from sqlalchemy import create_engine, Engine

logger = structlog.get_logger()

# Cloud SQL imports (optional - only needed for Cloud SQL)
try:
    from google.cloud.sql.connector import Connector

    CLOUD_SQL_AVAILABLE = True
except ImportError:
    CLOUD_SQL_AVAILABLE = False

from .base import DatabaseConfig


class CloudSQLConfig(DatabaseConfig):
    """
    Configuration for GCP Cloud SQL database.
    Supports both PostgreSQL and MySQL engines.
    """

    def __init__(
        self,
        instance_connection_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        db_name: Optional[str] = None,
        db_engine: str = "postgresql",
    ):
        """
        Initialize Cloud SQL configuration.
        """
        self.instance_connection_name = instance_connection_name or self._get_secret("INSTANCE_CONNECTION_NAME")
        self.db_user = db_user or self._get_secret("DB_USER")
        self.db_password = db_password or self._get_secret("DB_PASSWORD")
        self.db_name = db_name or self._get_secret("DB_NAME", default="tennis_data_with_mcp")
        self.db_engine = "postgresql"

    def get_engine(self) -> Engine:
        """
        Create and return a SQLAlchemy Engine for Cloud SQL.
        """
        if not CLOUD_SQL_AVAILABLE:
            raise ImportError(
                "cloud-sql-python-connector is not installed. "
                "Install it with: pip install cloud-sql-python-connector[pg8000]"
            )

        connector = self._create_connector()

        def getconn():
            """Get a connection to the Cloud SQL instance."""
            return connector.connect(
                cast(str, self.instance_connection_name),
                "pg8000",
                user=self.db_user,
                password=self.db_password,
                db=self.db_name,
            )

        return create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

    def _create_connector(self) -> Connector:
        """
        Create a Cloud SQL Connector with appropriate credentials.

        Returns:
            Cloud SQL Connector instance
        """
        try:
            import os
            import json

            # Try to get service account credentials from environment variables
            service_account_info = None

            # If service account info is not available, try environment variable for service account file path
            service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if service_account_path and os.path.exists(service_account_path):
                from google.oauth2 import service_account

                # Check if it's a JSON string or a file path
                if service_account_path.strip().startswith("{"):
                    service_account_info = json.loads(service_account_path)
                    credentials = service_account.Credentials.from_service_account_info(
                        service_account_info
                    )
                else:
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_path
                    )
                connector = Connector(credentials=credentials)
                logger.debug(
                    "using_service_account_credentials",
                    path=service_account_path
                )
            else:
                # Fall back to default connector (will try ADC/metadata service)
                connector = Connector()
                logger.debug("using_default_connector")
        except Exception as e:
            # If credential setup fails, fall back to default connector
            logger.error("credential_setup_failed", error=str(e))
            connector = Connector()

        return connector

    def get_db_type(self) -> str:
        """Get the database type identifier."""
        return self.db_engine

    def validate(self) -> bool:
        """
        Validate Cloud SQL configuration.

        Returns:
            True if all required fields are present
        """
        return (
            self.instance_connection_name is not None
            and self.instance_connection_name.strip() != ""
            and self.db_user is not None
            and self.db_user.strip() != ""
            and self.db_password is not None
            and self.db_password.strip() != ""
            and self.db_name is not None
            and self.db_name.strip() != ""
        )
