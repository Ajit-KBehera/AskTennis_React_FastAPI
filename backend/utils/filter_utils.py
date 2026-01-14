from typing import Any, Optional

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
