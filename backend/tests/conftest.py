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


@pytest.fixture
def mock_agent_graph():
    """Mock the LangGraph agent for testing."""
    mock = MagicMock()
    mock.invoke.return_value = {
        "answer": "Test answer from mocked agent",
        "sql_queries": ["SELECT * FROM test"],
        "data": [{"test": "data"}],
        "conversation_flow": [],
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
    # Reset lazy-loaded singletons in query router
    import api.routers.query as query_module

    query_module._agent_graph = None
    query_module._query_processor = None

    # Patch the correct module location (after refactoring to query router)
    with patch(
        "api.routers.query.setup_langgraph_agent", return_value=mock_agent_graph
    ):
        with patch(
            "api.routers.query.QueryProcessor", return_value=mock_query_processor
        ):
            from main import app

            yield TestClient(app)


@pytest.fixture
def client_no_mocks():
    """
    Create a test client without mocks.
    Use this for testing endpoints that don't require the agent/processor.
    """
    from main import app

    return TestClient(app)
