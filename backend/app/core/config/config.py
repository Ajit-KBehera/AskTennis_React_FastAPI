"""
Unified configuration management for AskTennis AI application.
Consolidates all configuration logic into a single class.
"""

import os
from app.core.constants import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_LLM_PROVIDER,
    OLLAMA_BASE_URL,
)

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load .env file if it exists
except ImportError:
    # python-dotenv not installed, environment variables must be set manually
    pass

from app.infrastructure.database.database_factory import DatabaseFactory
from app.infrastructure.database.base import DatabaseConfig


class Config:
    """
    Unified configuration class for the AskTennis AI application.
    Handles all configuration including LLM settings, API keys, and database paths.
    Supports both local SQLite and GCP Cloud SQL databases, as well as multiple LLM providers.
    """

    def __init__(self):
        """Initialize with default configuration."""
        # LLM configuration
        self.llm_provider = os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER).strip().lower()
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
        self.model_name = os.getenv("DEFAULT_MODEL", DEFAULT_MODEL)
        self.temperature = DEFAULT_TEMPERATURE

        # Vertex AI / GCP configuration
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
        self.gcp_location = os.getenv("GCP_LOCATION", "global")

        self.api_key = self._get_api_key()

        # Database configuration - use factory to create appropriate config
        self.db_config: DatabaseConfig = DatabaseFactory.create_config()

    def _get_api_key(self) -> str:
        """
        Get API key from environment variables.
        Ollama does not require an API key.
        If GCP_PROJECT_ID is set, API key is optional.
        """
        if self.llm_provider == "ollama":
            return ""

        # Fall back to environment variable
        # This works for both .env file (local dev) and Cloud Run environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key.strip():
            return api_key.strip()

        # If GCP_PROJECT_ID is configured, API key is not required
        if self.gcp_project_id:
            return ""

        # Debug: Log available environment variables (for troubleshooting)
        env_vars = [
            k for k in os.environ.keys() if "GOOGLE" in k or "API" in k or "KEY" in k
        ]
        print(
            f"DEBUG: Available environment variables containing 'GOOGLE', 'API', or 'KEY': {env_vars}"
        )
        print(f"DEBUG: GOOGLE_API_KEY env var exists: {api_key is not None}")

        # If we get here, the API key is not found
        error_msg = (
            "❌ Google API key not found!\n\n"
            "Ensure GOOGLE_API_KEY is set as an environment variable.\n"
            "For local development, create a .env file with GOOGLE_API_KEY=your_key_here.\n"
            "Alternatively, run locally with Ollama (LLM_PROVIDER=ollama) or set GCP_PROJECT_ID."
        )
        raise ValueError(error_msg)

    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        if self.llm_provider == "ollama":
            agent_valid = True
        elif self.gcp_project_id:
            agent_valid = True
        else:
            agent_valid = self.api_key is not None and self.api_key.strip() != ""

        # Validate database configuration
        database_valid = self.db_config.validate()

        return agent_valid and database_valid
