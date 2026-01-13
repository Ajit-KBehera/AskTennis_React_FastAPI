"""
Cloud SQL database configuration.
Handles GCP Cloud SQL (PostgreSQL/MySQL) database setup and connection.
"""

from typing import Optional
from sqlalchemy import create_engine, Engine

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
        db_engine: Optional[str] = None
    ):
        """
        Initialize Cloud SQL configuration.
        
        Args:
            instance_connection_name: Cloud SQL instance connection name (format: project:region:instance)
            db_user: Database user name
            db_password: Database password
            db_name: Database name (default: 'tennis_data_with_mcp')
            db_engine: Database engine type ('postgresql' or 'mysql', default: 'postgresql')
        """
        # Get configuration from secrets/env vars if not provided
        self.instance_connection_name = instance_connection_name or self._get_secret("INSTANCE_CONNECTION_NAME")
        self.db_user = db_user or self._get_secret("DB_USER")
        self.db_password = db_password or self._get_secret("DB_PASSWORD")
        self.db_name = db_name or self._get_secret("DB_NAME", default="tennis_data_with_mcp")
        
        # Normalize db_engine (lowercase, strip whitespace)
        db_engine_raw = db_engine or self._get_secret("DB_ENGINE", default="postgresql")
        if db_engine_raw:
            self.db_engine = db_engine_raw.lower().strip()
        else:
            self.db_engine = "postgresql"
        
        # Validate db_engine
        if self.db_engine not in ['postgresql', 'mysql']:
            raise ValueError(
                f"Invalid DB_ENGINE value: '{db_engine_raw}'. "
                "Must be 'postgresql' or 'mysql' (case-insensitive)."
            )
    
    def get_engine(self) -> Engine:
        """
        Create and return a SQLAlchemy Engine for Cloud SQL.
        
        Returns:
            SQLAlchemy Engine instance
            
        Raises:
            ImportError: If cloud-sql-python-connector is not installed
        """
        if not CLOUD_SQL_AVAILABLE:
            raise ImportError(
                "cloud-sql-python-connector is not installed. "
                "Install it with: pip install cloud-sql-python-connector[pg8000] "
                "or pip install cloud-sql-python-connector[pymysql]"
            )
        
        # Initialize Cloud SQL Connector with credentials
        connector = self._create_connector()
        
        def getconn():
            """Get a connection to the Cloud SQL instance."""
            if self.db_engine == "postgresql":
                return connector.connect(
                    self.instance_connection_name,
                    "pg8000",
                    user=self.db_user,
                    password=self.db_password,
                    db=self.db_name
                )
            else:  # mysql
                return connector.connect(
                    self.instance_connection_name,
                    "pymysql",
                    user=self.db_user,
                    password=self.db_password,
                    db=self.db_name
                )
        
        # Create SQLAlchemy engine with the connector
        if self.db_engine == "postgresql":
            engine_url = "postgresql+pg8000://"
        else:  # mysql
            engine_url = "mysql+pymysql://"
        
        return create_engine(
            engine_url,
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
                if service_account_path.strip().startswith('{'):
                    service_account_info = json.loads(service_account_path)
                    credentials = service_account.Credentials.from_service_account_info(
                        service_account_info
                    )
                else:
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_path
                    )
                connector = Connector(credentials=credentials)
                print(f"DEBUG: Using service account credentials from {service_account_path}")
            else:
                # Fall back to default connector (will try ADC/metadata service)
                connector = Connector()
                print("DEBUG: Using default connector (ADC/metadata service)")
        except Exception as e:
            # If credential setup fails, fall back to default connector
            print(f"DEBUG: Credential setup failed, using default connector: {e}")
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
            self.instance_connection_name is not None and 
            self.instance_connection_name.strip() != "" and
            self.db_user is not None and 
            self.db_user.strip() != "" and
            self.db_password is not None and 
            self.db_password.strip() != "" and
            self.db_name is not None and 
            self.db_name.strip() != ""
        )

