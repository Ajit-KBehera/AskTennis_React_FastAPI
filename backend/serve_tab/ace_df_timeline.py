"""
Ace and Double Fault timeline chart visualization.

This module provides functions to create timeline charts showing ace rate
and double fault rate over time for both player and opponent.
"""

# Third-party imports
import numpy as np

# Local application imports
from utils.timeline_chart_utils import create_generic_timeline_chart


def create_ace_df_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create ace rate and double fault rate timeline chart.
    
    Args:
        player_df: DataFrame with calculated serve statistics
        player_name: Name of the player
        title: Chart title
        show_opponent_comparison: If True, show opponent stats overlay (default: False)
        opponent_name: Name of opponent for comparison (optional, for legend)
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Determine dynamic y-max based on data
    # (Logic from original: cap at 30%, add 15% padding)
    all_series = [player_df['player_ace_rate'], player_df['player_df_rate']]
    if show_opponent_comparison:
        if 'opponent_ace_rate' in player_df.columns:
            all_series.append(player_df['opponent_ace_rate'])
        if 'opponent_df_rate' in player_df.columns:
            all_series.append(player_df['opponent_df_rate'])
            
    max_values = []
    for series in all_series:
        if series is not None and len(series) > 0:
            max_val = series.max()
            if not np.isnan(max_val):
                max_values.append(max_val)
    
    if max_values:
        max_value = max(max_values)
        y_max = min(30, max_value * 1.15)
    else:
        y_max = 30
        
    # Player traces configuration
    player_traces = [
        {
            'column': 'player_ace_rate',
            'name': 'Ace Rate',
            'color': '#10B981', # green-500
            'label': 'Ace Rate',
            'is_percentage': True
        },
        {
            'column': 'player_df_rate',
            'name': 'DF Rate',
            'color': '#EF4444', # red-500
            'label': 'Double Fault Rate',
            'is_percentage': True
        }
    ]

    # Opponent traces configuration
    opponent_traces = [
        {
            'column': 'opponent_ace_rate',
            'name': 'Opponent Ace Rate',
            'color': '#86EFAC', # light green
            'label': 'Opponent Ace Rate',
            'is_percentage': True
        },
        {
            'column': 'opponent_df_rate',
            'name': 'Opponent DF Rate',
            'color': '#FCA5A5', # light red
            'label': 'Opponent Double Fault Rate',
            'is_percentage': True
        }
    ]

    # Y-axis configuration
    y_axis_config = {
        'title': 'Rate (%)',
        'range': [0, y_max]
    }

    return create_generic_timeline_chart(
        player_df,
        player_name,
        title,
        player_traces,
        y_axis_config=y_axis_config,
        show_opponent_comparison=show_opponent_comparison,
        opponent_name=opponent_name,
        opponent_traces_config=opponent_traces
    )
