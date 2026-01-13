"""
Statistics router - provides tennis statistics charts and data.
Endpoints:
  - POST /api/stats/serve - Serve statistics charts
  - POST /api/stats/serve/raw - Raw serve data for frontend visualization
  - POST /api/stats/return - Return statistics charts
  - POST /api/stats/ranking - Ranking timeline chart
"""

from fastapi import APIRouter, HTTPException
import logging
import json
from typing import Optional, Dict, Any

from services.database_service import DatabaseService
from api.models import (
    ServeStatsRequest,
    ServeStatsResponse,
    ReturnStatsRequest,
    ReturnStatsResponse,
    RankingStatsRequest,
    RankingStatsResponse,
    RawServeStatsResponse,
    RawServeMatch,
    RawServeStatsFilters,
    PlotlyChart,
)

# Import chart generation functions
from serve_tab.combined_serve_charts import create_combined_serve_charts
from return_tab.combined_return_charts import create_combined_return_charts
from rankings_tab.ranking_timeline_chart import create_ranking_timeline_chart

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats")

# Initialize database service
try:
    db_service = DatabaseService()
except Exception as e:
    logger.error(f"Failed to initialize DatabaseService: {e}")
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
        logger.error(f"Error converting Plotly figure to dict: {e}")
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
            logger.warning(f"Invalid year range format: {year_str}")
            return None
    
    # Single year
    try:
        return int(year_str)
    except ValueError:
        logger.warning(f"Invalid year format: {year_str}")
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
        
        logger.info(f"Generating serve stats: player={player}, opponent={opponent}, "
                   f"tournament={tournament}, surfaces={surfaces}, year={year}")
        
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
        logger.error(f"Error generating serve stats: {e}")
        import traceback
        traceback.print_exc()
        return ServeStatsResponse(
            error=f"Failed to generate serve statistics: {str(e)}"
        )


@router.post("/serve/raw", response_model=RawServeStatsResponse)
async def get_raw_serve_stats(request: ServeStatsRequest):
    """
    Get raw match-level serve data for frontend visualization (D3, Recharts, etc).
    
    Returns match-level data including:
    - First serve %, 1st serve won %, 2nd serve won %
    - Ace rate, double fault rate
    - Break points faced, saved, save percentage
    - Opponent serve statistics
    
    Args:
        request: ServeStatsRequest with player and filter parameters
        
    Returns:
        RawServeStatsResponse with match-level data
    """
    if db_service is None:
        raise HTTPException(status_code=500, detail="Database service not initialized")
    
    try:
        player = request.player_name
        opponent = request.opponent if request.opponent != DatabaseService.ALL_OPPONENTS else None
        tournament = request.tournament if request.tournament != DatabaseService.ALL_TOURNAMENTS else None
        surfaces = request.surface if request.surface and len(request.surface) > 0 else None
        year = parse_year_filter(request.year) if request.year else None
        
        logger.info(f"Fetching raw serve data: player={player}")
        
        # Get matches with all columns
        df = db_service.get_matches_with_filters(
            player=player,
            opponent=opponent,
            tournament=tournament,
            year=year,
            surfaces=surfaces,
            return_all_columns=True
        )
        
        if df.empty:
            return RawServeStatsResponse(
                matches=[],
                player_name=player,
                filters=RawServeStatsFilters(
                    opponent=opponent,
                    tournament=tournament,
                    year=request.year,
                    surface=surfaces
                )
            )
        
        # Transform DataFrame to RawServeMatch models
        matches = []
        for idx, row in df.iterrows():
            # Determine player stats (whether player won or lost)
            is_winner = row.get('winner_name', '').lower() == player.lower()
            
            # Map columns based on whether player won or lost
            if is_winner:
                player_prefix = 'w_'
                opponent_name = row.get('loser_name', '')
                opponent_rank = row.get('loser_rank')
                result = 'W'
            else:
                player_prefix = 'l_'
                opponent_name = row.get('winner_name', '')
                opponent_rank = row.get('winner_rank')
                result = 'L'
            
            # Extract serve statistics
            match_data = RawServeMatch(
                match_index=int(idx),
                year=str(row.get('event_year', '')),
                tourney_name=row.get('tourney_name', ''),
                round=row.get('round', ''),
                opponent=opponent_name,
                opponent_rank=int(opponent_rank) if opponent_rank and pd.notna(opponent_rank) else None,
                result=result,
                surface=row.get('surface', ''),
                tourney_date=str(row.get('tourney_date', '')),
                player_1stIn=float(row.get(f'{player_prefix}1stIn', 0)) if pd.notna(row.get(f'{player_prefix}1stIn')) else None,
                player_1stWon=float(row.get(f'{player_prefix}1stWon', 0)) if pd.notna(row.get(f'{player_prefix}1stWon')) else None,
                player_2ndWon=float(row.get(f'{player_prefix}2ndWon', 0)) if pd.notna(row.get(f'{player_prefix}2ndWon')) else None,
                player_ace_rate=float(row.get(f'{player_prefix}ace', 0)) if pd.notna(row.get(f'{player_prefix}ace')) else None,
                player_df_rate=float(row.get(f'{player_prefix}df', 0)) if pd.notna(row.get(f'{player_prefix}df')) else None,
                player_bpFaced=int(row.get(f'{player_prefix}bpFaced', 0)) if pd.notna(row.get(f'{player_prefix}bpFaced')) else None,
                player_bpSaved=int(row.get(f'{player_prefix}bpSaved', 0)) if pd.notna(row.get(f'{player_prefix}bpSaved')) else None,
                player_bpSavePct=float(row.get(f'{player_prefix}bpSaved', 0)) / float(row.get(f'{player_prefix}bpFaced', 1)) * 100 
                    if pd.notna(row.get(f'{player_prefix}bpFaced')) and row.get(f'{player_prefix}bpFaced', 0) > 0 else None,
                # Opponent stats (opposite prefix)
                opponent_1stIn=float(row.get(f'{"l_" if is_winner else "w_"}1stIn', 0)) if pd.notna(row.get(f'{"l_" if is_winner else "w_"}1stIn')) else None,
                opponent_1stWon=float(row.get(f'{"l_" if is_winner else "w_"}1stWon', 0)) if pd.notna(row.get(f'{"l_" if is_winner else "w_"}1stWon')) else None,
                opponent_2ndWon=float(row.get(f'{"l_" if is_winner else "w_"}2ndWon', 0)) if pd.notna(row.get(f'{"l_" if is_winner else "w_"}2ndWon')) else None,
                opponent_ace_rate=float(row.get(f'{"l_" if is_winner else "w_"}ace', 0)) if pd.notna(row.get(f'{"l_" if is_winner else "w_"}ace')) else None,
                opponent_df_rate=float(row.get(f'{"l_" if is_winner else "w_"}df', 0)) if pd.notna(row.get(f'{"l_" if is_winner else "w_"}df')) else None,
            )
            matches.append(match_data)
        
        logger.info(f"Returning {len(matches)} raw serve matches")
        
        return RawServeStatsResponse(
            matches=matches,
            player_name=player,
            filters=RawServeStatsFilters(
                opponent=opponent,
                tournament=tournament,
                year=request.year,
                surface=surfaces
            )
        )
        
    except Exception as e:
        logger.error(f"Error fetching raw serve data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch raw serve data: {str(e)}"
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
        
        logger.info(f"Generating return stats: player={player}")
        
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
        logger.error(f"Error generating return stats: {e}")
        import traceback
        traceback.print_exc()
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
        
        logger.info(f"Generating ranking timeline: player={player}, year={year}")
        
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
        logger.error(f"Error generating ranking stats: {e}")
        import traceback
        traceback.print_exc()
        return RankingStatsResponse(
            error=f"Failed to generate ranking statistics: {str(e)}",
            reasons=["Internal server error - check logs for details"]
        )


# Add pandas import for type checking
import pandas as pd
