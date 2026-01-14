"""
Statistics router - provides tennis statistics charts and data.
Endpoints:
  - POST /api/stats/serve - Serve statistics charts
  - POST /api/stats/return - Return statistics charts
  - POST /api/stats/ranking - Ranking timeline chart
"""

from fastapi import APIRouter, HTTPException
import json
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List

from services.database_service import DatabaseService
from api.models import (
    ServeStatsRequest,
    ServeStatsResponse,
    ReturnStatsRequest,
    ReturnStatsResponse,
    RankingStatsRequest,
    RankingStatsResponse,
    PlotlyChart,
    RawServeMatch
)

# Import stats calculation functions
from serve_tab.serve_stats import (
    calculate_match_serve_stats,
    calculate_aggregated_player_serve_stats, 
    calculate_aggregated_opponent_serve_stats
)
from return_tab.return_stats import (
    calculate_match_return_stats,
    calculate_aggregated_player_return_stats,
    calculate_aggregated_opponent_return_stats
)

router = APIRouter(prefix="/stats")

# Initialize database service
try:
    db_service = DatabaseService()
except Exception as e:
    db_service = None


def parse_year_filter(year_str: Optional[str]) -> Any:
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
            return None
    
    # Single year
    try:
        return int(year_str)
    except ValueError:
        return None


def convert_df_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert DataFrame to list of dicts, replacing NaN with None."""
    # Replace NaN/Infinity with None for JSON compatibility
    if df.empty:
        return []
    df_clean = df.where(pd.notnull(df), None)
    return df_clean.to_dict('records')


@router.post("/serve", response_model=ServeStatsResponse)
async def get_serve_stats(request: ServeStatsRequest):
    """
    Get serve statistics raw data for a player.
    """
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    
    try:
        player = request.player_name
        opponent = request.opponent if request.opponent != DatabaseService.ALL_OPPONENTS else None
        tournament = request.tournament if request.tournament != DatabaseService.ALL_TOURNAMENTS else None
        surfaces = request.surface if request.surface and len(request.surface) > 0 else None
        year = parse_year_filter(request.year) if request.year else None
        
        # Get matches from database
        df = db_service.get_matches_with_filters(
            player=player,
            opponent=opponent,
            tournament=tournament,
            year=year,
            surfaces=surfaces,
            return_all_columns=True  # Need all columns for statistics
        )
        
        if df.empty:
            return ServeStatsResponse(
                error="No matches found for the specified filters"
            )
        
        # Calculate raw statistics for frontend
        from utils.df_utils import add_player_match_columns
        # We work on a copy to avoid SettingWithCopy warnings if df is a view
        stats_df = df.copy()
        
        if 'is_winner' not in stats_df.columns:
            stats_df = add_player_match_columns(stats_df, player)
            
        matches_with_stats = calculate_match_serve_stats(stats_df)
        serve_stats = calculate_aggregated_player_serve_stats(matches_with_stats, player_name=player)
        
        # Determine opponent comparison
        show_comparison = opponent is not None
        opponent_stats = None
        
        if show_comparison:
            try:
                opponent_stats = calculate_aggregated_opponent_serve_stats(matches_with_stats, opponent_name=opponent)
            except Exception:
                pass
        
        # Format matches for response
        matches_with_stats['match_index'] = range(len(matches_with_stats))
        matches_with_stats['year'] = matches_with_stats['event_year'].astype(str)
        matches_with_stats['result'] = np.where(matches_with_stats['is_winner'], 'Win', 'Loss')
        
        matches_data = convert_df_to_records(matches_with_stats)

        # Convert Aggregated stats
        def clean_stats_dict(stats_dict):
            if not stats_dict: return None
            return {k: (float(v) if not pd.isna(v) else None) for k, v in stats_dict.items()}
            
        return ServeStatsResponse(
            timeline_chart=None,
            ace_df_chart=None,
            bp_chart=None,
            radar_chart=None,
            matches=matches_data,
            aggregated_stats=clean_stats_dict(serve_stats),
            aggregated_opponent_stats=clean_stats_dict(opponent_stats)
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ServeStatsResponse(
            error=f"Failed to generate serve statistics: {str(e)}"
        )


@router.post("/return", response_model=ReturnStatsResponse)
async def get_return_stats(request: ReturnStatsRequest):
    """
    Get return statistics raw data for a player.
    """
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    
    try:
        player = request.player_name
        opponent = request.opponent if request.opponent != DatabaseService.ALL_OPPONENTS else None
        tournament = request.tournament if request.tournament != DatabaseService.ALL_TOURNAMENTS else None
        surfaces = request.surface if request.surface and len(request.surface) > 0 else None
        year = parse_year_filter(request.year) if request.year else None
        
        # Get matches from database
        df = db_service.get_matches_with_filters(
            player=player,
            opponent=opponent,
            tournament=tournament,
            year=year,
            surfaces=surfaces,
            return_all_columns=True
        )
        
        if df.empty:
            return ReturnStatsResponse(
                error="No matches found for the specified filters"
            )
        
        # Calculate raw statistics
        from utils.df_utils import add_player_match_columns
        stats_df = df.copy()
        
        if 'is_winner' not in stats_df.columns:
            stats_df = add_player_match_columns(stats_df, player)
            
        matches_with_stats = calculate_match_return_stats(stats_df)
        return_stats = calculate_aggregated_player_return_stats(matches_with_stats, player_name=player)
        
        # Determine opponent comparison
        show_comparison = opponent is not None
        opponent_stats = None
        
        if show_comparison:
            try:
                opponent_stats = calculate_aggregated_opponent_return_stats(matches_with_stats, opponent_name=opponent)
            except Exception:
                pass

        # Helper to clean stats
        def clean_stats_dict(stats_dict):
            if not stats_dict: return None
            return {k: (float(v) if not pd.isna(v) else None) for k, v in stats_dict.items()}

        matches_with_stats['match_index'] = range(len(matches_with_stats))
        matches_with_stats['year'] = matches_with_stats['event_year'].astype(str)
        matches_with_stats['result'] = np.where(matches_with_stats['is_winner'], 'Win', 'Loss')
        
        matches_data = convert_df_to_records(matches_with_stats)
        
        return ReturnStatsResponse(
            return_points_chart=None,
            bp_conversion_chart=None,
            radar_chart=None,
            matches=matches_data,
            aggregated_stats=clean_stats_dict(return_stats),
            aggregated_opponent_stats=clean_stats_dict(opponent_stats)
        )
        
    except Exception as e:
        return ReturnStatsResponse(
            error=f"Failed to generate return statistics: {str(e)}"
        )


@router.post("/ranking", response_model=RankingStatsResponse)
async def get_ranking_stats(request: RankingStatsRequest):
    """
    Get ranking timeline raw data for a player.
    """
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    
    try:
        player = request.player_name
        year = parse_year_filter(request.year) if request.year else None
        
        # Get ranking data from database
        ranking_df = db_service.get_player_ranking_timeline(
            player_name=player,
            year=year
        )
        
        if ranking_df.empty:
            return RankingStatsResponse(
                error="No ranking data available for this player",
                reasons=[
                    "Player name may be misspelled",
                    "Ranking data only available from 1973 onwards",
                    "Player may not have been ranked in the specified time period"
                ]
            )
        
        # Prepare raw data
        # ranking_df has columns: ranking_date, rank, tour
        ranking_df['ranking_date'] = ranking_df['ranking_date'].astype(str)
        ranking_data = convert_df_to_records(ranking_df)
        
        return RankingStatsResponse(
            ranking_chart=None,
            ranking_data=ranking_data
        )
        
    except Exception as e:
        return RankingStatsResponse(
            error=f"Failed to generate ranking statistics: {str(e)}",
            reasons=["Internal server error"]
        )


