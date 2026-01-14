"""
String manipulation and parsing utilities.
"""
import ast
import json
from typing import Any, List, Union, Dict

def safe_parse(val: Any) -> List[Any]:
    """
    Safely parse a value into a list.
    Handles strings, lists, stringified lists, and single dictionaries.
    Recursive for nested stringified structures.
    """
    if not val:
        return []
    
    # Case 1: Already a list
    if isinstance(val, list):
        # Check if it's a list containing a stringified list (common LLM pattern)
        if len(val) == 1 and isinstance(val[0], str) and val[0].strip().startswith('['):
            return safe_parse(val[0])
        # Otherwise return as is
        return val
    
    # Case 2: String that needs parsing
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return []
        try:
            parsed = ast.literal_eval(val)
            return safe_parse(parsed) # Recurse if needed
        except Exception:
            try:
                parsed = json.loads(val)
                return safe_parse(parsed) # Recurse if needed
            except Exception:
                return [val] if val else []
    
    # Case 3: Single dictionary (wrap it)
    if isinstance(val, dict):
        return [val]
    
    return []
