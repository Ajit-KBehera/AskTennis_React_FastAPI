"""
Configuration constants for AskTennis application.
Centralizes all hardcoded values and configuration settings.
"""

import os

# Database Configuration
DB_FILE_NAME = "tennis_data_with_mcp.db"
AUTH_DB_NAME = "asktennis_auth"
# Use absolute path to ensure database file is found regardless of working directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = os.path.join(PROJECT_ROOT, DB_FILE_NAME)
DEFAULT_DB_PATH = f"sqlite:///{DB_FILE_PATH}"

# Project Paths (if needed elsewhere)
# PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # Can create circular imports if not careful, so keeping simple

# LLM Configuration
DEFAULT_MODEL = "gemini-3-flash-preview"
DEFAULT_TEMPERATURE = 0

# Application Configuration
APP_TITLE = "🎾 AskTennis: The Advanced AI Engine"
APP_SUBTITLE = "#### Powered by Gemini & LangGraph (Stateful Agent)"

# Security Configuration
# These are default production origins. If empty, the backend will rely on 
# ALLOWED_ORIGINS environment variable or Cloud Run regex.
ALLOWED_HOSTS = []
ALLOWED_PATTERNS = [
    "run.app",  # Matches default Cloud Run URLs
]

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-do-not-use-in-prod")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day (default session)
ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER_ME = 30  # 30 days when "Remember me" is checked

# Query timeout (seconds) for AI agent invoke
QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", "120"))
