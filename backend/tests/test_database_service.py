"""
Tests for DatabaseService abstraction.
"""
import pytest
from unittest.mock import MagicMock, patch
from services.database_service import DatabaseService

class TestDatabaseService:
    @pytest.fixture
    def mock_db_factory(self):
        with patch("services.database_service.DatabaseFactory.create_config") as mock:
            config = MagicMock()
            mock.return_value = config
            yield config

    def test_get_all_players(self, mock_db_factory):
        """Test retrieval of player list."""
        import pandas as pd
        mock_df = pd.DataFrame({"player_name": ["Federer", "Nadal"]})
        
        with patch("pandas.read_sql_query", return_value=mock_df):
            service = DatabaseService()
            # Mock _detect_schema_type to avoid DB connection
            service._detect_schema_type = MagicMock(return_value="unified")
            players = service.get_all_players()
            assert "Federer" in players
            assert "Nadal" in players
            assert DatabaseService.ALL_PLAYERS in players

    def test_get_all_tournaments(self, mock_db_factory):
        """Test retrieval of tournament list."""
        import pandas as pd
        mock_df = pd.DataFrame({"tourney_name": ["Wimbledon", "US Open"]})
        
        with patch("pandas.read_sql_query", return_value=mock_df):
            service = DatabaseService()
            service._detect_schema_type = MagicMock(return_value="unified")
            tourneys = service.get_all_tournaments()
            assert "Wimbledon" in tourneys
            assert "US Open" in tourneys
            assert DatabaseService.ALL_TOURNAMENTS in tourneys

    def test_get_player_year_range(self, mock_db_factory):
        """Test min/max year retrieval."""
        import pandas as pd
        mock_df = pd.DataFrame({"min_year": [2000], "max_year": [2024]})
        
        with patch("pandas.read_sql_query", return_value=mock_df):
            service = DatabaseService()
            service._detect_schema_type = MagicMock(return_value="unified")
            years = service.get_player_year_range("Federer")
            assert years == (2000, 2024)
