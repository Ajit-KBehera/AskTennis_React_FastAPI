"""
Filters router - provides filter options for the UI.
Endpoint: GET /api/filters
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import structlog

from app.infrastructure.repositories.tennis_repository import DatabaseService
from app.api.schemas.tennis_schemas import FilterOptionsResponse, YearRange
from app.utils.error_utils import get_500_detail

logger = structlog.get_logger()

router = APIRouter()

# Initialize database service (singleton pattern)
try:
    db_service = DatabaseService()
except Exception:
    db_service = None


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_filters(
    player_name: Optional[str] = Query(
        None, description="Player name to filter options"
    ),
):
    """
    Get filter options for the UI.

    If player_name is provided and not "All Players", returns filtered options:
    - opponents: List of opponents for this player
    - tournaments: List of tournaments where this player competed
    - surfaces: List of surfaces where this player competed
    - year_range: Min and max years for this player's career

    If player_name is None or "All Players", returns all options.

    Args:
        player_name: Optional player name to filter by

    Returns:
        FilterOptionsResponse with players, tournaments, opponents, surfaces, year_range
    """
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")

    try:
        # Get all players (always returned)
        all_players = db_service.get_all_players()

        # If specific player selected, get filtered options
        if player_name and player_name != DatabaseService.ALL_PLAYERS:
            # Get player-specific options
            opponents = db_service.get_opponents_for_player(player_name)
            tournaments = db_service.get_all_tournaments(player_name)
            surfaces = db_service.get_surfaces_for_player(player_name)
            year_range_tuple = db_service.get_player_year_range(player_name)

            return FilterOptionsResponse(
                players=all_players,
                tournaments=tournaments,
                opponents=opponents,
                surfaces=surfaces,
                year_range=YearRange(min=year_range_tuple[0], max=year_range_tuple[1]),
            )
        else:
            # Return all options
            all_tournaments = db_service.get_all_tournaments()
            default_surfaces = ["Hard", "Clay", "Grass", "Carpet"]

            return FilterOptionsResponse(
                players=all_players,
                tournaments=all_tournaments,
                opponents=None,  # Not applicable when no player selected
                surfaces=default_surfaces,
                year_range=YearRange(min=1968, max=2024),
            )

    except Exception as e:
        logger.error("filters_fetch_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=get_500_detail(e),
        )
