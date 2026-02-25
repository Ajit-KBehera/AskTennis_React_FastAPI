"""
Database Service for Enhanced UI
Provides dynamic data for dropdowns and analysis
"""

import pandas as pd
from typing import List, Optional, Tuple, Union, Any, cast, Hashable
from functools import lru_cache
import structlog
from sqlalchemy import Engine, text

logger = structlog.get_logger()

from app.infrastructure.database.base import DatabaseConfig
from app.infrastructure.database.database_factory import DatabaseFactory


class DatabaseService:
    """Service for database operations in enhanced UI."""

    # Constants for filter options
    ALL_PLAYERS = "All Players"
    ALL_TOURNAMENTS = "All Tournaments"
    ALL_OPPONENTS = "All Opponents"
    ALL_YEARS = "All Years"

    # Configuration constants
    MIN_YEAR = 1900
    MAX_YEAR = 2100
    DEFAULT_QUERY_LIMIT = 5000

    def __init__(
        self,
        db_config: Optional[DatabaseConfig] = None,
        db_engine: Optional[Engine] = None,
    ):
        """
        Initialize database service.

        Args:
            db_config: DatabaseConfig instance (SQLiteConfig or CloudSQLConfig).
                      If None, creates one using DatabaseFactory.
            db_engine: SQLAlchemy Engine instance (optional, for pre-configured connections).
                      If None, creates one from db_config.
        """
        # Use provided config or create default one
        if db_config is None:
            db_config = DatabaseFactory.create_config()

        self.db_config = db_config

        # Use provided engine or create one from app.core.config
        if db_engine is None:
            self.db_engine = db_config.get_engine()
        else:
            self.db_engine = db_engine

    def _get_connection(self):
        """Get a database connection (works with both SQLite and Cloud SQL)."""
        return self.db_engine.connect()

    def _get_db_type(self) -> str:
        """Get the database type from the config.

        Returns:
            'sqlite', 'postgresql', or 'mysql'
        """
        return self.db_config.get_db_type()

    def _format_sql_query(self, query: str) -> str:
        """Format SQL query with correct placeholders for the database type.

        SQLite uses '?' while PostgreSQL/MySQL use '%s' when using raw SQL.
        When using SQLAlchemy connections directly (not through pandas text()),
        we need to convert '?' to '%s' for PostgreSQL/MySQL.

        Args:
            query: SQL query string with '?' placeholders

        Returns:
            SQL query with appropriate placeholders
        """
        db_type = self._get_db_type()
        if db_type in ["postgresql", "mysql"]:
            # Convert ? to %s for PostgreSQL/MySQL
            # Count the number of ? placeholders
            placeholder_count = query.count("?")
            if placeholder_count > 0:
                # Replace ? with %s
                query = query.replace("?", "%s")
        return query

    def _format_params(self, params: List) -> Union[tuple, List]:
        """Format parameters for pd.read_sql_query().

        For SQLAlchemy connections (PostgreSQL/MySQL), convert list to tuple.
        For SQLite, keep as list.

        Args:
            params: List of parameters

        Returns:
            Tuple or list of parameters depending on database type
        """
        if not params:
            return params

        # For SQLAlchemy engines (PostgreSQL/MySQL), convert to tuple
        # This fixes the "List argument must consist only of tuples or dictionaries" error
        db_type = self._get_db_type()
        if db_type in ["postgresql", "mysql"]:
            return tuple(params)
        return params

    def _get_year_extraction_expr(self, date_column: str = "ranking_date") -> str:
        """Get the appropriate year extraction expression for the current database type.

        Args:
            date_column: Name of the date column to extract year from

        Returns:
            SQL expression to extract year from date column (returns base expression, CAST can be applied separately)
        """
        db_type = self._get_db_type()
        if db_type == "postgresql":
            return f"EXTRACT(YEAR FROM {date_column})"
        elif db_type == "mysql":
            return f"YEAR({date_column})"
        else:  # sqlite
            return f"strftime('%Y', {date_column})"

    def _detect_schema_type(self) -> str:
        """Detect whether the database uses unified 'matches' table or separate 'atp_matches'/'wta_matches' tables.

        Returns:
            'unified' if matches table exists, 'separate' if atp_matches/wta_matches exist
        """
        try:
            with self._get_connection() as conn:
                db_type = self._get_db_type()
                if db_type == "sqlite":
                    # Check for separate tables FIRST (newer schema)
                    atp_result = conn.execute(
                        text(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name='atp_matches'"
                        )
                    ).fetchone()
                    wta_result = conn.execute(
                        text(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name='wta_matches'"
                        )
                    ).fetchone()
                    if atp_result and wta_result:
                        return "separate"
                    # Check for unified matches table (older schema)
                    result = conn.execute(
                        text(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name='matches'"
                        )
                    ).fetchone()
                    if result:
                        return "unified"
                else:  # PostgreSQL/MySQL
                    # Check for separate tables FIRST (newer schema)
                    # Use explicit schema checking for PostgreSQL
                    if db_type == "postgresql":
                        atp_query = text(
                            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'atp_matches')"
                        )
                        wta_query = text(
                            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'wta_matches')"
                        )
                    else:  # mysql
                        atp_query = text(
                            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'atp_matches')"
                        )
                        wta_query = text(
                            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'wta_matches')"
                        )
                    atp_result = conn.execute(atp_query).fetchone()
                    wta_result = conn.execute(wta_query).fetchone()
                    if atp_result and atp_result[0] and wta_result and wta_result[0]:
                        return "separate"
                    # Check for unified matches table (older schema)
                    if db_type == "postgresql":
                        query = text(
                            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'matches')"
                        )
                    else:  # mysql
                        query = text(
                            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'matches')"
                        )
                    result = conn.execute(query).fetchone()
                    if result and result[0]:
                        return "unified"
        except Exception:
            # Default to separate for new databases
            return "separate"
        # Default to separate for new databases (most common case)
        return "separate"

    @staticmethod
    def _sanitize_string(value: Optional[str]) -> Optional[str]:
        """Sanitize string input by trimming whitespace and handling empty strings.

        Args:
            value: String value to sanitize

        Returns:
            Sanitized string or None if value is empty/invalid
        """
        if not value or not isinstance(value, str):
            return None
        sanitized = value.strip()
        return sanitized if sanitized else None

    def clear_cache(self):
        """Clear all cached data."""
        self.get_all_players.cache_clear()
        self.get_all_tournaments.cache_clear()
        self.get_player_year_range.cache_clear()
        self.get_surfaces_for_player.cache_clear()
        self.get_opponents_for_player.cache_clear()
        self.get_player_ranking_timeline.cache_clear()

    @lru_cache(maxsize=128)
    def get_all_players(_self) -> List[str]:
        """Get all unique players from database who have played matches."""
        try:
            schema_type = _self._detect_schema_type()
            with _self._get_connection() as conn:
                if schema_type == "unified":
                    query = """
                    SELECT player_name
                    FROM (
                        SELECT winner_name as player_name
                        FROM matches 
                        WHERE winner_name IS NOT NULL AND winner_name != ''
                        UNION
                        SELECT loser_name as player_name
                        FROM matches 
                        WHERE loser_name IS NOT NULL AND loser_name != ''
                    )
                    ORDER BY player_name
                    """
                else:
                    # New schema: query both atp_matches and wta_matches
                    query = """
                    SELECT player_name
                    FROM (
                        SELECT winner_name as player_name
                        FROM atp_matches 
                        WHERE winner_name IS NOT NULL AND winner_name != ''
                        UNION
                        SELECT loser_name as player_name
                        FROM atp_matches 
                        WHERE loser_name IS NOT NULL AND loser_name != ''
                        UNION
                        SELECT winner_name as player_name
                        FROM wta_matches 
                        WHERE winner_name IS NOT NULL AND winner_name != ''
                        UNION
                        SELECT loser_name as player_name
                        FROM wta_matches 
                        WHERE loser_name IS NOT NULL AND loser_name != ''
                    )
                    ORDER BY player_name
                    """
                df = pd.read_sql_query(query, conn)
            if df.empty:
                return [DatabaseService.ALL_PLAYERS]
            return [DatabaseService.ALL_PLAYERS] + df["player_name"].tolist()
        except Exception:
            return [
                DatabaseService.ALL_PLAYERS,
                "Roger Federer",
                "Rafael Nadal",
                "Novak Djokovic",
            ]

    @lru_cache(maxsize=128)
    def get_all_tournaments(_self, player_name: Optional[str] = None) -> List[str]:
        """Get tournaments from database, optionally filtered by player.

        Args:
            player_name: Optional player name to filter tournaments. If None or "All Players",
                        returns all tournaments.

        Returns:
            List[str]: List of tournaments with "All Tournaments" as first element
        """
        # Sanitize input: trim whitespace and handle empty strings
        player_name = _self._sanitize_string(player_name)

        # If no player specified or "All Players", return all tournaments
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            try:
                schema_type = _self._detect_schema_type()
                with _self._get_connection() as conn:
                    if schema_type == "unified":
                        query = """
                        SELECT DISTINCT tourney_name FROM matches 
                        WHERE tourney_name IS NOT NULL AND tourney_name != ''
                        ORDER BY tourney_name
                        """
                    else:
                        # New schema: query both tables
                        query = """
                        SELECT DISTINCT tourney_name
                        FROM (
                            SELECT tourney_name FROM atp_matches 
                            WHERE tourney_name IS NOT NULL AND tourney_name != ''
                            UNION
                            SELECT tourney_name FROM wta_matches 
                            WHERE tourney_name IS NOT NULL AND tourney_name != ''
                        )
                        ORDER BY tourney_name
                        """
                    df = pd.read_sql_query(query, conn)
                if df.empty:
                    return [DatabaseService.ALL_TOURNAMENTS]
                return [DatabaseService.ALL_TOURNAMENTS] + df["tourney_name"].tolist()
            except Exception:
                return [
                    DatabaseService.ALL_TOURNAMENTS,
                    "Wimbledon",
                    "French Open",
                    "US Open",
                    "Australian Open",
                ]

        # Filter tournaments for specific player
        try:
            schema_type = _self._detect_schema_type()
            with _self._get_connection() as conn:
                if schema_type == "unified":
                    query = """
                    SELECT DISTINCT tourney_name
                    FROM matches 
                    WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                      AND tourney_name IS NOT NULL AND tourney_name != ''
                    ORDER BY tourney_name
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(_self._format_params([player_name, player_name])),
                    )
                else:
                    # New schema: query both tables
                    query = """
                    SELECT DISTINCT tourney_name
                    FROM (
                        SELECT tourney_name
                        FROM atp_matches 
                        WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                          AND tourney_name IS NOT NULL AND tourney_name != ''
                        UNION
                        SELECT tourney_name
                        FROM wta_matches 
                        WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                          AND tourney_name IS NOT NULL AND tourney_name != ''
                    )
                    ORDER BY tourney_name
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(
                            _self._format_params(
                                [player_name, player_name, player_name, player_name]
                            )
                        ),
                    )
            if df.empty:
                return [DatabaseService.ALL_TOURNAMENTS]
            return [DatabaseService.ALL_TOURNAMENTS] + df["tourney_name"].tolist()
        except Exception:
            # Fallback to all tournaments on error
            try:
                schema_type = _self._detect_schema_type()
                with _self._get_connection() as conn:
                    if schema_type == "unified":
                        query = """
                        SELECT DISTINCT tourney_name FROM matches 
                        WHERE tourney_name IS NOT NULL AND tourney_name != ''
                        ORDER BY tourney_name
                        """
                    else:
                        query = """
                        SELECT DISTINCT tourney_name
                        FROM (
                            SELECT tourney_name FROM atp_matches 
                            WHERE tourney_name IS NOT NULL AND tourney_name != ''
                            UNION
                            SELECT tourney_name FROM wta_matches 
                            WHERE tourney_name IS NOT NULL AND tourney_name != ''
                        )
                        ORDER BY tourney_name
                        """
                    df = pd.read_sql_query(query, conn)
                if df.empty:
                    return [DatabaseService.ALL_TOURNAMENTS]
                return [DatabaseService.ALL_TOURNAMENTS] + df["tourney_name"].tolist()
            except Exception:
                return [
                    DatabaseService.ALL_TOURNAMENTS,
                    "Wimbledon",
                    "French Open",
                    "US Open",
                    "Australian Open",
                ]

    @lru_cache(maxsize=128)
    def get_player_year_range(_self, player_name: Optional[str] = None) -> Tuple[int, int]:
        """Get the year range (min and max event_year) for a specific player.

        Args:
            player_name: Name of the player

        Returns:
            Tuple[int, int]: (min_year, max_year) or (1968, 2025) if no matches found
        """
        player_name = _self._sanitize_string(player_name)
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return (1968, 2024)  # Default range

        try:
            schema_type = _self._detect_schema_type()
            with _self._get_connection() as conn:
                if schema_type == "unified":
                    query = """
                    SELECT MIN(event_year) as min_year, MAX(event_year) as max_year
                    FROM matches 
                    WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                      AND event_year IS NOT NULL
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(_self._format_params([player_name, player_name])),
                    )
                else:
                    # New schema: query both tables
                    query = """
                    SELECT MIN(event_year) as min_year, MAX(event_year) as max_year
                    FROM (
                        SELECT event_year FROM atp_matches 
                        WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                          AND event_year IS NOT NULL
                        UNION ALL
                        SELECT event_year FROM wta_matches 
                        WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                          AND event_year IS NOT NULL
                    )
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(
                            _self._format_params(
                                [player_name, player_name, player_name, player_name]
                            )
                        ),
                    )

            if (
                df.empty
                or df["min_year"].iloc[0] is None
                or df["max_year"].iloc[0] is None
            ):
                return (1968, 2024)  # Default range if no matches found

            min_year = int(df["min_year"].iloc[0])
            max_year = int(df["max_year"].iloc[0])

            # Ensure valid range
            if min_year < _self.MIN_YEAR:
                min_year = _self.MIN_YEAR
            if max_year > _self.MAX_YEAR:
                max_year = _self.MAX_YEAR

            return (min_year, max_year)
        except Exception:
            return (1968, 2024)  # Default range on error

    @lru_cache(maxsize=128)
    def get_surfaces_for_player(_self, player_name: Optional[str] = None) -> List[str]:
        """Get surfaces from database, optionally filtered by player.

        Args:
            player_name: Optional player name to filter surfaces. If None or "All Players",
                        returns all surfaces.

        Returns:
            List[str]: List of surfaces (Hard, Clay, Grass, Carpet)
        """
        # Sanitize input: trim whitespace and handle empty strings
        player_name = _self._sanitize_string(player_name)

        # Standard surface list
        all_surfaces = ["Hard", "Clay", "Grass", "Carpet"]

        # If no player specified or "All Players", return all surfaces
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return all_surfaces

        # Filter surfaces for specific player
        try:
            schema_type = _self._detect_schema_type()
            with _self._get_connection() as conn:
                if schema_type == "unified":
                    query = """
                    SELECT DISTINCT surface
                    FROM matches 
                    WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                      AND surface IS NOT NULL AND surface != ''
                    ORDER BY surface
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(_self._format_params([player_name, player_name])),
                    )
                else:
                    # New schema: query both tables
                    query = """
                    SELECT DISTINCT surface
                    FROM (
                        SELECT surface FROM atp_matches 
                        WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                          AND surface IS NOT NULL AND surface != ''
                        UNION
                        SELECT surface FROM wta_matches 
                        WHERE (LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))
                          AND surface IS NOT NULL AND surface != ''
                    )
                    ORDER BY surface
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(
                            _self._format_params(
                                [player_name, player_name, player_name, player_name]
                            )
                        ),
                    )

            if df.empty:
                return all_surfaces  # Return all surfaces if player has no matches

            player_surfaces = df["surface"].tolist()
            # Filter to only include surfaces that exist in our standard list
            # This ensures we don't return unexpected surface types
            filtered_surfaces = [s for s in all_surfaces if s in player_surfaces]
            return filtered_surfaces if filtered_surfaces else all_surfaces
        except Exception:
            return all_surfaces  # Fallback to all surfaces on error

    @lru_cache(maxsize=128)
    def get_opponents_for_player(_self, player_name: Optional[str] = None) -> List[str]:
        """Get opponents for a specific player."""
        # Sanitize input: trim whitespace and handle empty strings
        player_name = _self._sanitize_string(player_name)
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return _self.get_all_players()

        try:
            schema_type = _self._detect_schema_type()
            with _self._get_connection() as conn:
                if schema_type == "unified":
                    query = """
                    SELECT DISTINCT opponent_name
                    FROM (
                        SELECT loser_name as opponent_name
                        FROM matches 
                        WHERE LOWER(winner_name) = LOWER(?) AND loser_name IS NOT NULL
                        UNION ALL
                        SELECT winner_name as opponent_name
                        FROM matches 
                        WHERE LOWER(loser_name) = LOWER(?) AND winner_name IS NOT NULL
                    )
                    ORDER BY opponent_name
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(_self._format_params([player_name, player_name])),
                    )
                else:
                    # New schema: query both tables
                    query = """
                    SELECT DISTINCT opponent_name
                    FROM (
                        SELECT loser_name as opponent_name
                        FROM atp_matches 
                        WHERE LOWER(winner_name) = LOWER(?) AND loser_name IS NOT NULL
                        UNION ALL
                        SELECT winner_name as opponent_name
                        FROM atp_matches 
                        WHERE LOWER(loser_name) = LOWER(?) AND winner_name IS NOT NULL
                        UNION ALL
                        SELECT loser_name as opponent_name
                        FROM wta_matches 
                        WHERE LOWER(winner_name) = LOWER(?) AND loser_name IS NOT NULL
                        UNION ALL
                        SELECT winner_name as opponent_name
                        FROM wta_matches 
                        WHERE LOWER(loser_name) = LOWER(?) AND winner_name IS NOT NULL
                    )
                    ORDER BY opponent_name
                    """
                    query = _self._format_sql_query(query)
                    df = pd.read_sql_query(
                        query,
                        conn,
                        params=tuple(
                            _self._format_params(
                                [player_name, player_name, player_name, player_name]
                            )
                        ),
                    )
            if df.empty:
                return [DatabaseService.ALL_OPPONENTS]
            return [DatabaseService.ALL_OPPONENTS] + df["opponent_name"].tolist()
        except Exception:
            return _self.get_all_players()

    @lru_cache(maxsize=32)
    def _get_matches_internal(
        self,
        player: Optional[str] = None,
        opponent: Optional[str] = None,
        tournament: Optional[str] = None,
        year: Optional[Union[int, str, Tuple[int, int], Tuple[int, ...]]] = None,
        surfaces: Optional[Tuple[str, ...]] = None,
        return_all_columns: bool = False,
        year_is_range: bool = True,
    ) -> pd.DataFrame:
        """Internal cached method for getting matches."""
        try:
            # Build WHERE clause
            where_conditions = []
            params = []

            # Optimize: if both player and opponent are specified, combine them into one condition
            # Use LOWER() for case-insensitive matching (works with both SQLite and PostgreSQL/MySQL)
            if (
                player
                and player != self.ALL_PLAYERS
                and opponent
                and opponent != self.ALL_OPPONENTS
            ):
                # Match where both players are involved (either order)
                where_conditions.append(
                    "((LOWER(winner_name) = LOWER(?) AND LOWER(loser_name) = LOWER(?)) OR (LOWER(winner_name) = LOWER(?) AND LOWER(loser_name) = LOWER(?)))"
                )
                params.extend([player, opponent, opponent, player])
            else:
                # Handle player and opponent separately if only one is specified
                if player and player != self.ALL_PLAYERS:
                    where_conditions.append(
                        "(LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))"
                    )
                    params.extend([player, player])

                if opponent and opponent != self.ALL_OPPONENTS:
                    where_conditions.append(
                        "(LOWER(winner_name) = LOWER(?) OR LOWER(loser_name) = LOWER(?))"
                    )
                    params.extend([opponent, opponent])

            if tournament and tournament != self.ALL_TOURNAMENTS:
                where_conditions.append("tourney_name = ?")
                params.append(tournament)

            # Handle year filtering
            if year is not None and year != self.ALL_YEARS:
                try:
                    # Handle tuple (could be range or converted list)

                    # Handle valid range (tuple with year_is_range=True)
                    if year_is_range and isinstance(year, tuple) and len(year) == 2:
                        start_year, end_year = int(year[0]), int(year[1])
                        # Ensure start <= end
                        if start_year > end_year:
                            start_year, end_year = end_year, start_year

                        # Validate year range
                        if (
                            self.MIN_YEAR <= start_year <= self.MAX_YEAR
                            and self.MIN_YEAR <= end_year <= self.MAX_YEAR
                        ):
                            where_conditions.append("event_year BETWEEN ? AND ?")
                            params.extend([start_year, end_year])

                    # Handle multiple specific years (tuple with year_is_range=False)
                    elif (
                        not year_is_range and isinstance(year, tuple) and len(year) > 0
                    ):
                        year_list = [
                            int(y)
                            for y in year
                            if isinstance(y, (int, str)) and str(y).isdigit()
                        ]
                        # Validate all years
                        valid_years = [
                            y for y in year_list if self.MIN_YEAR <= y <= self.MAX_YEAR
                        ]

                        if valid_years:
                            if len(valid_years) == 1:
                                # Single year in list - use equality
                                where_conditions.append("event_year = ?")
                                params.append(valid_years[0])
                            else:
                                # Multiple years - use IN
                                placeholders = ",".join(["?" for _ in valid_years])
                                where_conditions.append(
                                    f"event_year IN ({placeholders})"
                                )
                                params.extend(valid_years)

                    # Handle single integer year
                    elif isinstance(year, int):
                        if self.MIN_YEAR <= year <= self.MAX_YEAR:
                            where_conditions.append("event_year = ?")
                            params.append(year)

                    # Handle string (backward compatibility)
                    elif isinstance(year, str):
                        year_int = int(year)
                        if self.MIN_YEAR <= year_int <= self.MAX_YEAR:
                            where_conditions.append("event_year = ?")
                            params.append(year_int)

                except (ValueError, TypeError):
                    pass

            if surfaces:
                # Filter and validate surfaces: remove empty strings, None values, and strip whitespace
                # Since surfaces is now a tuple, we iterate over it directly
                valid_surfaces = [
                    s.strip()
                    for s in surfaces
                    if s and isinstance(s, str) and s.strip()
                ]

                if valid_surfaces:
                    # Handle multiple surface filtering
                    placeholders = ",".join(["?" for _ in valid_surfaces])
                    where_conditions.append(f"surface IN ({placeholders})")
                    params.extend(valid_surfaces)

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            # Detect schema type
            schema_type = self._detect_schema_type()

            # Select columns based on return_all_columns parameter
            if return_all_columns:
                # Return all columns for chart generation
                if schema_type == "unified":
                    query = f"""
                    SELECT *
                    FROM matches 
                    WHERE {where_clause}
                    ORDER BY tourney_date ASC, match_num ASC
                    LIMIT {self.DEFAULT_QUERY_LIMIT}
                    """
                else:
                    # New schema: use UNION ALL for both tours
                    query = f"""
                    SELECT *
                    FROM (
                        SELECT * FROM atp_matches WHERE {where_clause}
                        UNION ALL
                        SELECT * FROM wta_matches WHERE {where_clause}
                    )
                    ORDER BY tourney_date ASC, match_num ASC
                    LIMIT {self.DEFAULT_QUERY_LIMIT}
                    """
            else:
                # Return selected columns for table display
                # Note: match_num is included in SELECT so it can be used in ORDER BY
                if schema_type == "unified":
                    query = f"""
                    SELECT
                        event_year,
                        tourney_date,
                        tourney_name,
                        round,
                        winner_name,
                        loser_name,
                        surface,
                        score,
                        match_num
                    FROM matches 
                    WHERE {where_clause}
                    ORDER BY tourney_date ASC, match_num ASC
                    LIMIT {self.DEFAULT_QUERY_LIMIT}
                    """
                else:
                    # New schema: use UNION ALL for both tours
                    # Ensure column order and types match
                    # Note: match_num is included in SELECT so it can be used in ORDER BY
                    query = f"""
                    SELECT
                        event_year,
                        tourney_date,
                        tourney_name,
                        round,
                        winner_name,
                        loser_name,
                        surface,
                        score,
                        match_num
                    FROM (
                        SELECT
                            event_year,
                            tourney_date,
                            tourney_name,
                            round,
                            winner_name,
                            loser_name,
                            surface,
                            score,
                            match_num
                        FROM atp_matches 
                        WHERE {where_clause}
                        UNION ALL
                        SELECT
                            event_year,
                            tourney_date,
                            tourney_name,
                            round,
                            winner_name,
                            loser_name,
                            surface,
                            score,
                            match_num
                        FROM wta_matches 
                        WHERE {where_clause}
                    )
                    ORDER BY tourney_date ASC, match_num ASC
                    LIMIT {self.DEFAULT_QUERY_LIMIT}
                    """

            # If using UNION ALL with separate tables, duplicate params for each table
            # This must be done BEFORE formatting the query
            if schema_type == "separate" and where_clause != "1=1" and params:
                # Duplicate params for UNION ALL (each table needs the same params)
                params = params * 2

            # Format query for database type (convert ? to %s for PostgreSQL/MySQL)
            query = self._format_sql_query(query)

            with self._get_connection() as conn:
                df = pd.read_sql_query(
                    query, conn, params=tuple(self._format_params(params))
                )

            return df

        except Exception as e:
            logger.error("error_fetching_matches", error=str(e))
            return pd.DataFrame()

    def get_matches_with_filters(
        self,
        player: Optional[str] = None,
        opponent: Optional[str] = None,
        tournament: Optional[str] = None,
        year: Optional[Union[int, str, Tuple[int, int], List[int]]] = None,
        surfaces: Optional[List[str]] = None,
        return_all_columns: bool = False,
        _cache_bust: int = 0,
    ) -> pd.DataFrame:
        """
        Public wrapper for getting matches with caching.
        Converts mutable arguments (lists) to immutable types (tuples) for lru_cache.
        """
        # Sanitize string inputs before caching to ensure consistency
        player = self._sanitize_string(player)
        opponent = self._sanitize_string(opponent)
        tournament = self._sanitize_string(tournament)

        # Convert surfaces list to tuple
        surfaces_tuple = tuple(surfaces) if surfaces else None

        # Handle year conversion
        year_val: Any = year
        year_is_range = True  # Default assumption for tuple

        if isinstance(year, list):
            year_val = tuple(year)
            year_is_range = False  # List converted to tuple is explicitly NOT a range
        elif isinstance(year, tuple):
            year_val = year
            year_is_range = True  # Original tuple is valid range

        # Call internal cached method
        # We assume result is immutable (don't modify in place inside internal),
        # but we return a copy to the caller so they can modify it safely.
        cached_df = self._get_matches_internal(
            player=player,
            opponent=opponent,
            tournament=tournament,
            year=year_val,
            surfaces=surfaces_tuple,
            return_all_columns=return_all_columns,
            year_is_range=year_is_range,
        )

        return cached_df.copy()

    @lru_cache(maxsize=128)
    def get_player_ranking_timeline(
        _self,
        player_name: Optional[str] = None,
        year: Optional[Union[int, str, Tuple[int, int], List[int]]] = None,
    ) -> pd.DataFrame:
        """
        Get ranking timeline data for a specific player from both ATP and WTA rankings.

        Args:
            player_name: Name of the player
            year: Optional year filter. Can be:
                - None: All years
                - int: Single year
                - tuple: Year range (start_year, end_year)
                - list: Multiple specific years

        Returns:
            DataFrame with columns: ranking_date, rank, tour (ATP/WTA)
        """
        player_name = _self._sanitize_string(player_name)
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return pd.DataFrame()

        try:
            with _self._get_connection() as conn:
                # Build year filter clause for ranking_date
                # Use database-specific year extraction function
                year_filter_clause = ""
                year_params = []

                if year is not None and year != _self.ALL_YEARS:
                    try:
                        # Get the appropriate year extraction expression for this database
                        year_expr = _self._get_year_extraction_expr("ranking_date")

                        # Handle tuple (year range) - use BETWEEN for efficiency
                        if isinstance(year, tuple) and len(year) == 2:
                            start_year, end_year = int(year[0]), int(year[1])
                            # Ensure start <= end
                            if start_year > end_year:
                                start_year, end_year = end_year, start_year

                            # Validate year range
                            if (
                                _self.MIN_YEAR <= start_year <= _self.MAX_YEAR
                                and _self.MIN_YEAR <= end_year <= _self.MAX_YEAR
                            ):
                                year_filter_clause = (
                                    f"AND CAST({year_expr} AS INTEGER) BETWEEN ? AND ?"
                                )
                                year_params = [start_year, end_year]

                        # Handle list (multiple specific years) - use IN
                        elif isinstance(year, list) and len(year) > 0:
                            year_list = [
                                int(y)
                                for y in year
                                if isinstance(y, (int, str)) and str(y).isdigit()
                            ]
                            # Validate all years
                            valid_years = [
                                y
                                for y in year_list
                                if _self.MIN_YEAR <= y <= _self.MAX_YEAR
                            ]

                            if valid_years:
                                if len(valid_years) == 1:
                                    # Single year in list - use equality
                                    year_filter_clause = (
                                        f"AND CAST({year_expr} AS INTEGER) = ?"
                                    )
                                    year_params = [valid_years[0]]
                                else:
                                    # Multiple years - use IN
                                    placeholders = ",".join(["?" for _ in valid_years])
                                    year_filter_clause = f"AND CAST({year_expr} AS INTEGER) IN ({placeholders})"
                                    year_params = valid_years

                        # Handle single integer year
                        elif isinstance(year, int):
                            if _self.MIN_YEAR <= year <= _self.MAX_YEAR:
                                year_filter_clause = (
                                    f"AND CAST({year_expr} AS INTEGER) = ?"
                                )
                                year_params = [year]

                        # Handle string (backward compatibility)
                        elif isinstance(year, str):
                            year_int = int(year)
                            if _self.MIN_YEAR <= year_int <= _self.MAX_YEAR:
                                year_filter_clause = (
                                    f"AND CAST({year_expr} AS INTEGER) = ?"
                                )
                                year_params = [year_int]

                    except (ValueError, TypeError):
                        # If year filtering fails, just continue without year filter
                        pass

                # Query ATP rankings - join with atp_players to get player name
                # Note: || is SQLite/PostgreSQL concatenation, MySQL uses CONCAT()
                # COLLATE NOCASE is SQLite-specific, using LOWER() for compatibility
                atp_query = f"""
                SELECT ar.ranking_date, ar.rank, 'ATP' as tour
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE (LOWER(COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last)) = LOWER(?)
                    OR LOWER(ap.full_name) = LOWER(?)
                    OR LOWER(ap.name_first || ' ' || ap.name_last) = LOWER(?))
                  AND ar.ranking_date IS NOT NULL
                  AND ar.rank IS NOT NULL
                  {year_filter_clause}
                ORDER BY ar.ranking_date ASC
                """

                # Query WTA rankings - join with wta_players to get player name
                wta_query = f"""
                SELECT wr.ranking_date, wr.rank, 'WTA' as tour
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE (LOWER(COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last)) = LOWER(?)
                    OR LOWER(wp.full_name) = LOWER(?)
                    OR LOWER(wp.name_first || ' ' || wp.name_last) = LOWER(?))
                  AND wr.ranking_date IS NOT NULL
                  AND wr.rank IS NOT NULL
                  {year_filter_clause}
                ORDER BY wr.ranking_date ASC
                """

                # Format queries for database type (convert ? to %s for PostgreSQL/MySQL)
                atp_query = _self._format_sql_query(atp_query)
                wta_query = _self._format_sql_query(wta_query)

                # Execute both queries with player name params + year params
                player_params = [player_name, player_name, player_name]
                all_params = player_params + year_params
                atp_df = pd.read_sql_query(
                    atp_query, conn, params=tuple(_self._format_params(all_params))
                )
                wta_df = pd.read_sql_query(
                    wta_query, conn, params=tuple(_self._format_params(all_params))
                )

                # Combine results
                if not atp_df.empty and not wta_df.empty:
                    combined_df = pd.concat([atp_df, wta_df], ignore_index=True)
                elif not atp_df.empty:
                    combined_df = atp_df
                elif not wta_df.empty:
                    combined_df = wta_df
                else:
                    return pd.DataFrame()

                # Sort by date
                combined_df["ranking_date"] = pd.to_datetime(
                    combined_df["ranking_date"]
                )
                combined_df = combined_df.sort_values("ranking_date").reset_index(
                    drop=True
                )

                return combined_df

        except Exception:
            return pd.DataFrame()
