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
from typing import Optional, Dict, Any

from services.database_service import DatabaseService
from api.models import (
    ServeStatsRequest,
    ServeStatsResponse,
    ReturnStatsRequest,
    ReturnStatsResponse,
    RankingStatsRequest,
    RankingStatsResponse,

    PlotlyChart,
)

# Import chart generation functions
from serve_tab.combined_serve_charts import create_combined_serve_charts
from return_tab.combined_return_charts import create_combined_return_charts
from rankings_tab.ranking_timeline_chart import create_ranking_timeline_chart

router = APIRouter(prefix="/stats")

# Initialize database service
try:
    db_service = DatabaseService()
except Exception as e:
    db_service = None


def plotly_fig_to_dict(fig) -> Optional[Dict[str, Any]]:
    """
    Convert a Plotly figure to a dictionary for JSON serialization.
    
    Args:
        fig: Plotly figure object
        
    Returns:
        Dictionary with data, layout, and config keys, or None if conversion fails
    """
    if fig is None:
        return None
    
    try:
        # Convert figure to JSON then parse back to dict
        fig_json = fig.to_json()
        fig_dict = json.loads(fig_json)
        
        return PlotlyChart(
            data=fig_dict.get('data', []),
            layout=fig_dict.get('layout', {}),
            config=fig_dict.get('config')
        )
    except Exception as e:
        return None


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


@router.post("/serve", response_model=ServeStatsResponse)
async def get_serve_stats(request: ServeStatsRequest):
    """
    Get serve statistics charts for a player.
    
    Returns Plotly charts for:
    - First serve performance timeline
    - Ace/Double Fault rate timeline
    - Break points saved timeline
    - Serve statistics radar chart
    
    Args:
        request: ServeStatsRequest with player and filter parameters
        
    Returns:
        ServeStatsResponse with chart data or error message
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
        
        # Generate charts
        timeline_fig, ace_df_fig, bp_fig, radar_fig = create_combined_serve_charts(
            player_name=player,
            df=df,
            year=request.year,
            opponent=opponent,
            tournament=tournament,
            surfaces=surfaces
        )
        
        # Convert Plotly figures to dictionaries
        return ServeStatsResponse(
            timeline_chart=plotly_fig_to_dict(timeline_fig),
            ace_df_chart=plotly_fig_to_dict(ace_df_fig),
            bp_chart=plotly_fig_to_dict(bp_fig),
            radar_chart=plotly_fig_to_dict(radar_fig)
        )
        
    except Exception as e:
        return ServeStatsResponse(
            error=f"Failed to generate serve statistics: {str(e)}"
        )


@router.post("/return", response_model=ReturnStatsResponse)
async def get_return_stats(request: ReturnStatsRequest):
    """
    Get return statistics charts for a player.
    
    Returns Plotly charts for:
    - Return points won % timeline
    - Break point conversion timeline
    - Return statistics radar chart
    
    Args:
        request: ReturnStatsRequest with player and filter parameters
        
    Returns:
        ReturnStatsResponse with chart data or error message
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
        
        # Generate charts
        return_points_fig, bp_conversion_fig, radar_fig = create_combined_return_charts(
            player_name=player,
            df=df,
            year=request.year,
            opponent=opponent,
            tournament=tournament,
            surfaces=surfaces
        )
        
        # Convert Plotly figures to dictionaries
        return ReturnStatsResponse(
            return_points_chart=plotly_fig_to_dict(return_points_fig),
            bp_conversion_chart=plotly_fig_to_dict(bp_conversion_fig),
            radar_chart=plotly_fig_to_dict(radar_fig)
        )
        
    except Exception as e:
        return ReturnStatsResponse(
            error=f"Failed to generate return statistics: {str(e)}"
        )


@router.post("/ranking", response_model=RankingStatsResponse)
async def get_ranking_stats(request: RankingStatsRequest):
    """
    Get ranking timeline chart for a player.
    
    Returns a Plotly chart showing the player's ranking progression over time.
    
    Args:
        request: RankingStatsRequest with player name and optional filters
        
    Returns:
        RankingStatsResponse with chart data or error message
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
        
        # Generate ranking chart
        title = f"{player} - Ranking Timeline"
        if request.year:
            title += f" ({request.year})"
        
        ranking_fig = create_ranking_timeline_chart(
            player_name=player,
            ranking_df=ranking_df,
            title=title
        )
        
        if ranking_fig is None:
            return RankingStatsResponse(
                error="Failed to generate ranking chart",
                reasons=["Insufficient ranking data points"]
            )
        
        # Convert Plotly figure to dictionary
        return RankingStatsResponse(
            ranking_chart=plotly_fig_to_dict(ranking_fig)
        )
        
    except Exception as e:
        return RankingStatsResponse(
            error=f"Failed to generate ranking statistics: {str(e)}",
            reasons=["Internal server error"]
        )


