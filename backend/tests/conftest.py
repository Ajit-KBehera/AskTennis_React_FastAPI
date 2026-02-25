"""
Pytest fixtures and configuration for AskTennis backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Provide dummy API key for tests that don't mock it
os.environ["GOOGLE_API_KEY"] = "dummy-key-for-testing"


@pytest.fixture
def mock_agent_graph():
    """Mock the LangGraph agent for testing."""
    mock = MagicMock()
    mock.invoke.return_value = {
        "answer": "Test answer from mocked agent",
        "sql_queries": ["SELECT * FROM test"],
        "data": [{"test": "data"}],
        "conversation_flow": [],
        "session_id": "test-session",
    }
    return mock


@pytest.fixture
def mock_query_processor():
    """Mock the QueryProcessor for testing."""
    mock = MagicMock()
    mock.handle_user_query.return_value = {
        "answer": "Test answer",
        "sql_queries": ["SELECT 1"],
        "data": [],
        "conversation_flow": [],
        "session_id": "test-session",
    }
    return mock


@pytest.fixture
def mock_db_service():
    """Mock the DatabaseService for testing."""
    mock = MagicMock()
    mock.get_all_players.return_value = [
        "Roger Federer",
        "Rafael Nadal",
        "Novak Djokovic",
    ]
    mock.get_all_tournaments.return_value = [
        "Wimbledon",
        "US Open",
        "French Open",
        "Australian Open",
    ]
    mock.get_opponents_for_player.return_value = ["Rafael Nadal", "Novak Djokovic"]
    mock.get_surfaces_for_player.return_value = ["Hard", "Clay", "Grass"]
    mock.get_player_year_range.return_value = (2003, 2024)
    return mock


@pytest.fixture
def client(mock_agent_graph, mock_query_processor):
    """Create a test client with mocked dependencies."""
    from main import app
    from app.api.dependencies import get_current_user
    from app.api.routers.query import get_ai_services

    # Override AI services dependency
    app.dependency_overrides[get_ai_services] = lambda: (mock_agent_graph, mock_query_processor)
    # Override authentication for tests
    app.dependency_overrides[get_current_user] = lambda: "testuser"

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_no_mocks(mock_agent_graph, mock_query_processor):
    """
    Create a test client without most mocks, but still overriding AI services
    to avoid heavy initialization in test environment.
    """
    from main import app
    from app.api.dependencies import get_current_user
    from app.api.routers.query import get_ai_services
    
    # Override AI services dependency to avoid DB/LLM init
    app.dependency_overrides[get_ai_services] = lambda: (mock_agent_graph, mock_query_processor)
    # Override authentication for tests
    app.dependency_overrides[get_current_user] = lambda: "testuser"
    
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_db_session():
    """Fixture for a clean, in-memory auth database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.infrastructure.database.models import Base
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_db_service_mock():
    """AuthDBService instance configured to use an in-memory test database."""
    from app.infrastructure.repositories.user_repository import AuthDBService
    from sqlalchemy import create_engine
    
    # Create an in-memory engine
    test_engine = create_engine("sqlite:///:memory:")
    
    with patch("app.infrastructure.database.database_factory.DatabaseFactory.create_auth_config") as mock_create:
        # Create a mock config that returns our test engine
        mock_config = MagicMock()
        mock_config.get_engine.return_value = test_engine
        mock_create.return_value = mock_config
        
        # Initialize service (will run create_all on the test_engine)
        service = AuthDBService()
        return service
