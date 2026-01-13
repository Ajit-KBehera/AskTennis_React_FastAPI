"""
Return points won percentage timeline chart visualization.

This module provides functions to create timeline charts showing return points won
percentage over time, tracking return performance progression.
"""

# Local application imports
from utils.timeline_chart_utils import create_generic_timeline_chart


def create_return_points_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create the return points won percentage timeline chart with optional opponent comparison.
    
    Args:
        player_df: DataFrame with calculated return statistics
        player_name: Name of the player
        title: Chart title
        show_opponent_comparison: If True, show opponent stats overlay (default: False)
        opponent_name: Name of opponent for comparison (optional, for legend)
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Player traces configuration
    player_traces = [
        {
            'column': 'player_return_points_won_pct',
            'name': 'Return Points Won %',
            'color': '#2563EB', # blue
            'label': 'Return Points Won %',
            'is_percentage': True
        }
    ]

    # Opponent traces configuration
    opponent_traces = [
        {
            'column': 'opponent_return_points_won_pct',
            'name': 'Opponent Return Points Won %',
            'color': '#93C5FD', # light blue
            'label': 'Opponent Return Points Won %',
            'is_percentage': True
        }
    ]

    # Y-axis configuration
    y_axis_config = {
        'title': 'Return Points Won (%)',
        'range': [0, 100]
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
