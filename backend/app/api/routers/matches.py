"""
Matches router - provides filtered match data.
Endpoint: POST /api/matches
"""

from fastapi import APIRouter, HTTPException
from typing import List
import pandas as pd
import structlog

from app.infrastructure.repositories.tennis_repository import DatabaseService
from app.api.schemas.tennis_schemas import StatsRequest, MatchesResponse, Match
from app.utils.filter_utils import parse_year_filter
from app.utils.error_utils import get_500_detail

logger = structlog.get_logger()

router = APIRouter()

# Initialize database service
try:
    db_service = DatabaseService()
except Exception:
    db_service = None


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
        # Parse filter values - match the logic used in serve/return stats endpoints
        player = request.player_name
        # Handle opponent: if None or "All Opponents", set to None
        opponent = (
            None
            if (
                request.opponent is None
                or request.opponent == DatabaseService.ALL_OPPONENTS
            )
            else request.opponent
        )
        # Handle tournament: if None or "All Tournaments", set to None
        tournament = (
            None
            if (
                request.tournament is None
                or request.tournament == DatabaseService.ALL_TOURNAMENTS
            )
            else request.tournament
        )
        surfaces = (
            request.surface if request.surface and len(request.surface) > 0 else None
        )
        year = parse_year_filter(request.year) if request.year else None

        # Get matches from database
        df = db_service.get_matches_with_filters(
            player=player,
            opponent=opponent,
            tournament=tournament,
            year=year,
            surfaces=surfaces,
            return_all_columns=False,
        )

        # Convert DataFrame to list of Match models
        matches: List[Match] = []
        if not df.empty:
            for idx, row in df.iterrows():
                try:
                    # Convert row to dict and handle NaN values
                    match_dict = row.to_dict()
                    # Ensure required fields are present and handle NaN
                    match_data = {
                        "event_year": int(match_dict.get("event_year", 0))
                        if pd.notna(match_dict.get("event_year"))
                        else 0,
                        "tourney_date": str(match_dict.get("tourney_date", ""))
                        if pd.notna(match_dict.get("tourney_date"))
                        else "",
                        "tourney_name": str(match_dict.get("tourney_name", ""))
                        if pd.notna(match_dict.get("tourney_name"))
                        else "",
                        "round": str(match_dict.get("round", ""))
                        if pd.notna(match_dict.get("round"))
                        else "",
                        "winner_name": str(match_dict.get("winner_name", ""))
                        if pd.notna(match_dict.get("winner_name"))
                        else "",
                        "loser_name": str(match_dict.get("loser_name", ""))
                        if pd.notna(match_dict.get("loser_name"))
                        else "",
                        "surface": str(match_dict.get("surface", ""))
                        if pd.notna(match_dict.get("surface"))
                        else "",
                        "score": str(match_dict.get("score", ""))
                        if pd.notna(match_dict.get("score"))
                        else "",
                    }
                    matches.append(Match(**match_data))
                except Exception:
                    continue

        return MatchesResponse(matches=matches, count=len(matches))

    except Exception as e:
        logger.error("matches_fetch_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=get_500_detail(e),
        )
