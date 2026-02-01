"""
Pydantic models for API request/response validation.
These models match the TypeScript types in frontend/src/types/index.ts
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ============================================================================
# Filter Models
# ============================================================================


class YearRange(BaseModel):
    """Year range for filter options."""

    min: int
    max: int


class FilterOptionsResponse(BaseModel):
    """Response model for filter options endpoint."""

    players: List[str]
    tournaments: List[str]
    opponents: Optional[List[str]] = None
    surfaces: Optional[List[str]] = None
    year_range: Optional[YearRange] = None


# ============================================================================
# Statistics Models
# ============================================================================


class StatsRequest(BaseModel):
    """Base request model for statistics endpoints."""

    player_name: str = Field(..., description="Player name for statistics")
    opponent: Optional[str] = Field(None, description="Opponent filter")
    tournament: Optional[str] = Field(None, description="Tournament filter")
    surface: Optional[List[str]] = Field(
        None, description="Surface filters (Hard, Clay, Grass, Carpet)"
    )
    year: Optional[str] = Field(
        None, description="Year filter (e.g., '2023', '2020-2023', or 'All Years')"
    )


class ServeStatsRequest(StatsRequest):
    """Request model for serve statistics endpoint."""

    pass


class ReturnStatsRequest(StatsRequest):
    """Request model for return statistics endpoint."""

    pass


class RankingStatsRequest(BaseModel):
    """Request model for ranking statistics endpoint."""

    player_name: str = Field(..., description="Player name for ranking timeline")
    opponent: Optional[str] = None
    tournament: Optional[str] = None
    surface: Optional[List[str]] = None
    year: Optional[str] = None


class PlotlyChart(BaseModel):
    """Plotly chart data structure."""

    data: List[Dict[str, Any]]
    layout: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


class ServeStatsResponse(BaseModel):
    """Response model for serve statistics endpoint."""

    timeline_chart: Optional[PlotlyChart] = None
    ace_df_chart: Optional[PlotlyChart] = None
    bp_chart: Optional[PlotlyChart] = None
    radar_chart: Optional[PlotlyChart] = None
    # Raw data for frontend visualization
    matches: Optional[List[dict]] = None
    aggregated_stats: Optional[Dict[str, float]] = None
    aggregated_opponent_stats: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class ReturnStatsResponse(BaseModel):
    """Response model for return statistics endpoint."""

    return_points_chart: Optional[PlotlyChart] = None
    bp_conversion_chart: Optional[PlotlyChart] = None
    radar_chart: Optional[PlotlyChart] = None
    # Raw data for frontend visualization
    matches: Optional[List[dict]] = None
    aggregated_stats: Optional[Dict[str, float]] = None
    aggregated_opponent_stats: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class RankingStatsResponse(BaseModel):
    """Response model for ranking statistics endpoint."""

    ranking_chart: Optional[PlotlyChart] = None
    # Raw data
    ranking_data: Optional[List[dict]] = None
    error: Optional[str] = None
    reasons: Optional[List[str]] = None


# ============================================================================
# Match Models
# ============================================================================


class Match(BaseModel):
    """Match data model."""

    event_year: int
    tourney_date: str
    tourney_name: str
    round: str
    winner_name: str
    loser_name: str
    surface: str
    score: str

    class Config:
        extra = "allow"  # Allow additional fields from database


class MatchesResponse(BaseModel):
    """Response model for matches endpoint."""

    matches: List[Match]
    count: int


# ============================================================================
# Raw Data Models
# ============================================================================


class RawServeMatch(BaseModel):
    """Raw serve match data for frontend visualization."""

    match_index: int
    year: str
    tourney_name: str
    round: str
    opponent: str
    opponent_rank: Optional[int] = None
    result: str
    surface: str
    tourney_date: str
    player_1stIn: Optional[float] = None
    player_1stWon: Optional[float] = None
    player_2ndWon: Optional[float] = None
    player_ace_rate: Optional[float] = None
    player_df_rate: Optional[float] = None
    player_bpFaced: Optional[int] = None
    player_bpSaved: Optional[int] = None
    player_bpSavePct: Optional[float] = None
    opponent_1stIn: Optional[float] = None
    opponent_1stWon: Optional[float] = None
    opponent_2ndWon: Optional[float] = None
    opponent_ace_rate: Optional[float] = None
    opponent_df_rate: Optional[float] = None


class RawServeStatsFilters(BaseModel):
    """Filters applied to raw serve stats."""

    opponent: Optional[str] = None
    tournament: Optional[str] = None
    year: Optional[str] = None
    surface: Optional[List[str]] = None


class RawServeStatsResponse(BaseModel):
    """Response model for raw serve statistics endpoint."""

    matches: List[RawServeMatch]
    player_name: str
    filters: RawServeStatsFilters
