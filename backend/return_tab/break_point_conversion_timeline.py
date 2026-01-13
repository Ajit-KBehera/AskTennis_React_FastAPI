"""
Break point conversion timeline chart visualization.

This module provides functions to create timeline charts showing break points converted
and break point conversion percentage over time for a player when returning.
"""

# Third-party imports
import numpy as np

# Local application imports
from .return_stats import calculate_match_return_stats
from utils.timeline_chart_utils import create_generic_timeline_chart


def create_break_point_conversion_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create break point conversion timeline chart showing break points converted and conversion percentage.
    
    Args:
        player_df: DataFrame with match data (should have w_bpFaced, l_bpFaced, w_bpSaved, l_bpSaved columns)
        player_name: Name of the player
        title: Chart title
        show_opponent_comparison: If True, show opponent stats overlay (default: False)
        opponent_name: Name of opponent for comparison (optional, for legend)
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Calculate return statistics (includes break point conversion stats)
    # Note: player_df should already have is_winner column pre-calculated
    df = calculate_match_return_stats(player_df)
    
    # Calculate dynamic y-max values
    
    # Primary y-axis (counts)
    max_values_count = []
    if 'player_bpConverted' in df.columns:
        series = df['player_bpConverted']
        if series is not None and len(series) > 0:
             max_val = series.max()
             if not np.isnan(max_val):
                 max_values_count.append(max_val)
    
    if max_values_count:
        y_max_count = max(max_values_count) * 1.15
    else:
        y_max_count = 10
        
    # Secondary y-axis (percentage)
    max_values_pct = []
    if 'player_bpConversion_pct' in df.columns:
        series = df['player_bpConversion_pct']
        if series is not None and len(series) > 0:
             max_val = series.max()
             if not np.isnan(max_val):
                 max_values_pct.append(max_val)
                 
    if max_values_pct:
        y_max_pct = min(max(max_values_pct) * 1.15, 100)
    else:
        y_max_pct = 100

    # Player traces configuration
    player_traces = [
        {
            'column': 'player_bpConverted',
            'name': 'BPs Converted',
            'color': '#10B981', # green-500
            'label': 'Break Points Converted',
            'is_percentage': False,
            'secondary_y': False
        },
        {
            'column': 'player_bpConversion_pct',
            'name': 'BP Conversion %',
            'color': '#3B82F6', # blue-500
            'label': 'Break Point Conversion %',
            'is_percentage': True,
            'secondary_y': True
        }
    ]

    # Opponent traces configuration
    opponent_traces = [
        {
            'column': 'opponent_bpConverted',
            'name': 'Opponent BPs Converted',
            'color': '#86EFAC', # light green
            'label': 'Opponent Break Points Converted',
            'is_percentage': False,
            'secondary_y': False
        },
        {
            'column': 'opponent_bpConversion_pct',
            'name': 'Opponent BP Conversion %',
            'color': '#93C5FD', # light blue
            'label': 'Opponent Break Point Conversion %',
            'is_percentage': True,
            'secondary_y': True
        }
    ]

    # Y-axis configuration
    y_axis_config = {
        'title': 'Break Points Converted (Count)',
        'range': [0, y_max_count],
        'secondary_title': 'Break Point Conversion (%)',
        'secondary_range': [0, y_max_pct]
    }

    return create_generic_timeline_chart(
        df,
        player_name,
        title,
        player_traces,
        y_axis_config=y_axis_config,
        show_opponent_comparison=show_opponent_comparison,
        opponent_name=opponent_name,
        opponent_traces_config=opponent_traces,
        secondary_y=True
    )
