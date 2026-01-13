"""
Base database configuration class.
Defines the interface for all database configuration implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy import Engine
import os


class DatabaseConfig(ABC):
    """
    Abstract base class for database configurations.
    All database configuration classes must implement this interface.
    """
    
    @abstractmethod
    def get_engine(self) -> Engine:
        """
        Create and return a SQLAlchemy Engine instance.
        
        Returns:
            SQLAlchemy Engine instance
        """
        pass
    
    @abstractmethod
    def get_db_type(self) -> str:
        """
        Get the database type identifier.
        
        Returns:
            Database type string ('sqlite', 'postgresql', 'mysql')
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @staticmethod
    def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret from environment variables.
        
        Args:
            key: Secret key to retrieve
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        # Fall back to environment variable
        env_value = os.getenv(key)
        if env_value:
            return env_value
        return default
