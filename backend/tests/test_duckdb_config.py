"""
Tests for DuckDB configuration and DatabaseFactory.
"""

import os
from unittest.mock import patch
from app.core.config.database.database_factory import DatabaseFactory
from app.core.config.database.duckdb_config import DuckDBConfig
from app.core.config.database.sqlite_config import SQLiteConfig


class TestDatabaseFactoryTypes:
    """Test DatabaseFactory returns correct config types based on environment."""

    def test_create_config_default(self):
        """Test default returns SQLiteConfig."""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseFactory.create_config()
            assert isinstance(config, SQLiteConfig)
            assert config.get_db_type() == "sqlite"

    def test_create_config_duckdb_env(self):
        """Test DB_TYPE=duckdb returns DuckDBConfig."""
        with patch.dict(os.environ, {"DB_TYPE": "duckdb"}, clear=True):
            config = DatabaseFactory.create_config()
            assert isinstance(config, DuckDBConfig)
            assert config.get_db_type() == "duckdb"

    def test_create_config_duckdb_scheme(self):
        """Test duckdb:// scheme returns DuckDBConfig."""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseFactory.create_config(db_path="duckdb:///test.db")
            assert isinstance(config, DuckDBConfig)
            assert config.get_db_type() == "duckdb"
            assert "duckdb:///test.db" in config.db_path


class TestDuckDBConfig:
    """Test DuckDBConfig behavior."""

    def test_duckdb_config_init(self):
        """Test initialization ensures correct scheme."""
        config = DuckDBConfig("duckdb:///custom.db")
        assert config.db_path == "duckdb:///custom.db"

        # Test auto-prefix
        config = DuckDBConfig("/path/to/db")
        assert config.db_path.startswith("duckdb:///")

    def test_validation(self):
        """Test validation logic."""
        config = DuckDBConfig("duckdb:///valid.db")
        assert config.validate() is True

    @patch("app.core.config.database.duckdb_config.create_engine")
    def test_get_engine_read_only(self, mock_create_engine):
        """Test that get_engine sets read_only=True."""
        config = DuckDBConfig("duckdb:///test.db")
        config.get_engine()

        # Verify call args
        args, kwargs = mock_create_engine.call_args
        assert args[0] == "duckdb:///test.db"
        assert "connect_args" in kwargs
        assert kwargs["connect_args"]["read_only"] is True
