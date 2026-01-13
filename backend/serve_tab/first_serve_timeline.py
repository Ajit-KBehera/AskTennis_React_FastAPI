"""
First serve timeline chart visualization.

This module provides functions to create timeline charts showing first serve
performance over time, including first serves in percentage and first serves won percentage.
"""

# Local application imports
from utils.timeline_chart_utils import create_generic_timeline_chart


def create_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create the first serve timeline chart with optional opponent comparison.
    
    Args:
        player_df: DataFrame with calculated serve statistics
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
            'column': 'player_1stIn',
            'name': '1stIn',
            'color': '#2563EB', # blue
            'label': '1stIn',
            'is_percentage': True
        },
        {
            'column': 'player_1stWon',
            'name': '1stWon',
            'color': '#F97316', # orange
            'label': '1stWon',
            'is_percentage': True
        },
        {
            'column': 'player_2ndWon',
            'name': '2ndWon',
            'color': '#10B981', # green
            'label': '2ndWon',
            'is_percentage': True
        }
    ]

    # Opponent traces configuration
    opponent_traces = [
        {
            'column': 'opponent_1stIn',
            'name': 'Opponent 1stIn',
            'color': '#93C5FD', # light blue
            'label': 'Opponent 1stIn',
            'is_percentage': True
        },
        {
            'column': 'opponent_1stWon',
            'name': 'Opponent 1stWon',
            'color': '#FCD34D', # light orange
            'label': 'Opponent 1stWon',
            'is_percentage': True
        },
        {
            'column': 'opponent_2ndWon',
            'name': 'Opponent 2ndWon',
            'color': '#86EFAC', # light green
            'label': 'Opponent 2ndWon',
            'is_percentage': True
        }
    ]

    # Y-axis configuration
    y_axis_config = {
        'title': '(%)',
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
