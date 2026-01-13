"""
Matches router - provides filtered match data.
Endpoint: POST /api/matches
"""

from fastapi import APIRouter, HTTPException
import logging
from typing import List, Dict, Any

from services.database_service import DatabaseService
from api.models import StatsRequest, MatchesResponse, Match

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize database service
try:
    db_service = DatabaseService()
except Exception as e:
    logger.error(f"Failed to initialize DatabaseService: {e}")
    db_service = None


def parse_year_filter(year_str: str) -> Any:
    """
    Parse year filter string into appropriate format for DatabaseService.
    
    Args:
        year_str: Year string like "2023", "2020-2023", or "All Years"
        
    Returns:
        int, tuple, or None
    """
    if not year_str or year_str == "All Years":
        return None
    
    # Check if it's a range (e.g., "2020-2023")
    if "-" in year_str:
        try:
            start, end = year_str.split("-")
            return (int(start.strip()), int(end.strip()))
        except ValueError:
            logger.warning(f"Invalid year range format: {year_str}")
            return None
    
    # Single year
    try:
        return int(year_str)
    except ValueError:
        logger.warning(f"Invalid year format: {year_str}")
        return None


@router.post("/matches", response_model=MatchesResponse)
async def get_matches(request: StatsRequest):
    """
    Get filtered match data based on player, opponent, tournament, surface, and year.
    
    Args:
        request: StatsRequest with filter parameters
        
    Returns:
        MatchesResponse with list of matches and count
    """
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    
    try:
        # Parse filter values
        player = request.player_name if request.player_name != DatabaseService.ALL_PLAYERS else None
        opponent = request.opponent if request.opponent and request.opponent != DatabaseService.ALL_OPPONENTS else None
        tournament = request.tournament if request.tournament and request.tournament != DatabaseService.ALL_TOURNAMENTS else None
        surfaces = request.surface if request.surface and len(request.surface) > 0 else None
        year = parse_year_filter(request.year) if request.year else None
        
        logger.info(f"Fetching matches: player={player}, opponent={opponent}, "
                   f"tournament={tournament}, surfaces={surfaces}, year={year}")
        
        # Get matches from database
        df = db_service.get_matches_with_filters(
            player=player,
            opponent=opponent,
            tournament=tournament,
            year=year,
            surfaces=surfaces,
            return_all_columns=False
        )
        
        # Convert DataFrame to list of Match models
        matches: List[Match] = []
        for _, row in df.iterrows():
            match_dict = row.to_dict()
            matches.append(Match(**match_dict))
        
        logger.info(f"Found {len(matches)} matches")
        
        return MatchesResponse(
            matches=matches,
            count=len(matches)
        )
    
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch matches: {str(e)}"
        )
