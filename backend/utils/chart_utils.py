"""
Chart utilities for tennis visualization scripts.

This module provides general utilities for creating consistent
chart titles and suffixes across all chart types (serve, return, ranking, etc.).
"""


def build_year_suffix(year):
    """
    Build year suffix string for chart titles.
    
    Args:
        year: Year(s) for the chart. Can be:
            - int or str: Single year (e.g., 2024)
            - tuple: Year range (e.g., (2020, 2024)) for consecutive years
            - list: Multiple years (e.g., [2022, 2023, 2024])
            - None: Career view (all years)
    
    Returns:
        str: Year suffix string (e.g., "2024 Season", "2020-2024 Seasons", "Career")
    """
    if year is None:
        return "Career"
    elif isinstance(year, tuple) and len(year) == 2:
        # Year range tuple (start_year, end_year)
        start_year, end_year = year[0], year[1]
        if start_year == end_year:
            return f"{start_year} Season"
        else:
            return f"{start_year}-{end_year} Seasons"
    elif isinstance(year, list):
        if len(year) == 1:
            return f"{year[0]} Season"
        else:
            return f"{min(year)}-{max(year)} Seasons"
    else:
        # Single year (int or str)
        return f"{year} Season"


def build_chart_title_suffixes(year, opponent=None, tournament=None, surfaces=None):
    """
    Build filter and year suffixes for chart titles.
    
    Args:
        year: Year(s) for the chart
        opponent: Optional opponent name
        tournament: Optional tournament name
        surfaces: Optional list of surfaces
        
    Returns:
        tuple: (year_suffix, filter_suffix) - Two suffix strings for chart titles
    """
    # Build filter suffix for chart titles
    filter_parts = []
    if opponent:
        filter_parts.append(f"vs {opponent}")
    if tournament:
        filter_parts.append(f"at {tournament}")
    if surfaces and len(surfaces) > 0:
        filter_parts.append(f"on {', '.join(surfaces)}")
    filter_suffix = f" ({', '.join(filter_parts)})" if filter_parts else ""
    
    # Build year suffix for titles
    year_suffix = build_year_suffix(year)
    
    return year_suffix, filter_suffix
