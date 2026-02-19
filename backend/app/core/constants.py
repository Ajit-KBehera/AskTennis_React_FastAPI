"""
Configuration constants for AskTennis application.
Centralizes all hardcoded values and configuration settings.
"""

import os

# Base Directories
# __file__ is backend/app/core/constants.py
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CORE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")

# Tennis Database Configuration (Local)
TENNIS_DB_FILE_NAME = os.getenv("DB_FILE_NAME", "tennis_data_with_mcp.db")
TENNIS_DB_FILE_PATH = os.path.join(DATA_DIR, TENNIS_DB_FILE_NAME)
DEFAULT_TENNIS_DB_PATH = f"sqlite:///{TENNIS_DB_FILE_PATH}"

# Auth Database Configuration (Local)
AUTH_DB_FILE_NAME = os.getenv("AUTH_DB_FILE_NAME", "asktennis_auth.db")
AUTH_DB_FILE_PATH = os.path.join(DATA_DIR, AUTH_DB_FILE_NAME)
DEFAULT_AUTH_DB_PATH = f"sqlite:///{AUTH_DB_FILE_PATH}"

# Tennis Database (Main)
TENNIS_DB_NAME = os.getenv("TENNIS_DB_NAME")
TENNIS_DB_USER = os.getenv("TENNIS_DB_USER")
TENNIS_DB_PASSWORD = os.getenv("TENNIS_DB_PASSWORD")

# Auth Database (Main)
AUTH_DB_NAME = os.getenv("AUTH_DB_NAME")
AUTH_DB_USER = os.getenv("AUTH_DB_USER")
AUTH_DB_PASSWORD = os.getenv("AUTH_DB_PASSWORD")

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
