"""
Tennis Mapping Tools
Contains cached mapping functions and LangChain tools for tennis terminology mapping.
Optimized for production-level LLM applications with reduced latency and token usage.
"""

from langchain_core.tools import tool
from typing import List, Dict, Any, Union
from functools import lru_cache
import re
from .ranking_analysis import (
    get_ranking_context,
    extract_ranking_parameters
)

# =============================================================================
# TENNIS MAPPING DICTIONARIES
# =============================================================================

ROUND_MAPPINGS = {
    # Finals
    "final": "F", "finals": "F", "championship": "F", "champion": "F", "winner": "F",
    
    # Semi-Finals
    "semi-final": "SF", "semi finals": "SF", "semifinal": "SF", "semifinals": "SF",
    "semi": "SF", "last four": "SF", "last 4": "SF",
    
    # Quarter-Finals
    "quarter-final": "QF", "quarter finals": "QF", "quarterfinal": "QF", "quarterfinals": "QF",
    "quarter": "QF", "quarters": "QF", "last eight": "QF", "last 8": "QF",
    
    # Round of 16
    "round of 16": "R16", "round 16": "R16", "last 16": "R16", "fourth round": "R16", "4th round": "R16",
    
    # Round of 32
    "round of 32": "R32", "round 32": "R32", "third round": "R32", "3rd round": "R32",
    
    # Round of 64
    "round of 64": "R64", "round 64": "R64", "second round": "R64", "2nd round": "R64",
    
    # Round of 128
    "round of 128": "R128", "round 128": "R128", "first round": "R128", "1st round": "R128",
    
    # Qualifying rounds
    "qualifying": "Q1", "qualifier": "Q1", "qualifying 1": "Q1", "qualifying 2": "Q2", "qualifying 3": "Q3",
    
    # Round Robin
    "round robin": "RR", "group stage": "RR", "group": "RR",
    
    # Other rounds
    "bronze": "BR", "playoff": "PR", "consolation": "CR", "exhibition": "ER"
}

SURFACE_MAPPINGS = {
    # Clay courts
    "clay": "Clay", "clay court": "Clay", "clay courts": "Clay", "red clay": "Clay", "terre battue": "Clay",
    "dirt": "Clay", "slow court": "Clay",
    
    # Hard courts
    "hard": "Hard", "hard court": "Hard", "hard courts": "Hard", "concrete": "Hard", "asphalt": "Hard",
    "acrylic": "Hard", "deco turf": "Hard", "plexicushion": "Hard", "fast court": "Hard",
    "indoor hard": "Hard", "outdoor hard": "Hard",
    
    # Grass courts
    "grass": "Grass", "grass court": "Grass", "grass courts": "Grass", "lawn": "Grass", "natural grass": "Grass",
    "very fast court": "Grass", "quick court": "Grass",
    
    # Carpet courts
    "carpet": "Carpet", "carpet court": "Carpet", "carpet courts": "Carpet", "indoor carpet": "Carpet",
    "synthetic": "Carpet", "artificial": "Carpet"
}

TOUR_MAPPINGS = {
    # Main tours
    "atp": "ATP", "atp tour": "ATP", "men's tour": "ATP", "men tour": "ATP", "men": "ATP", "male": "ATP",
    "wta": "WTA", "wta tour": "WTA", "women's tour": "WTA", "women tour": "WTA", "women": "WTA", "female": "WTA", "ladies": "WTA",
    "main tour": "Main Tour", "main": "Main Tour", "professional": "Main Tour", "pro tour": "Main Tour",
    
    # Development tours
    "challenger": "Challenger", "atp challenger": "Challenger", "challenger tour": "Challenger", "development tour": "Challenger",
    "futures": "Futures", "atp futures": "Futures", "futures tour": "Futures", "itf futures": "Futures",
    "itf": "ITF", "itf tour": "ITF", "junior tour": "ITF", "development": "ITF",
    
    # Combined
    "both": "Both", "combined": "Both", "men and women": "Both", "atp and wta": "Both"
}

HAND_MAPPINGS = {
    # Right-handed
    "right": "R", "right-handed": "R", "right hand": "R", "righty": "R", "right handed": "R",
    
    # Left-handed
    "left": "L", "left-handed": "L", "left hand": "L", "lefty": "L", "left handed": "L", "southpaw": "L",
    
    # Ambidextrous
    "ambidextrous": "A", "both": "A", "either": "A", "switch": "A",
    
    # Unknown
    "unknown": "U", "unclear": "U", "not specified": "U"
}

GRAND_SLAM_MAPPINGS = {
    # French Open variations
    "french open": "Roland Garros", "roland garros": "Roland Garros", "french": "Roland Garros",
    "French Open": "Roland Garros", "Roland Garros": "Roland Garros", "French": "Roland Garros",
    
    # Australian Open variations
    "aus open": "Australian Open", "australian open": "Australian Open", "aus": "Australian Open",
    "Australian Open": "Australian Open", "Aus Open": "Australian Open", "Australian": "Australian Open",
    
    # Wimbledon variations
    "wimbledon": "Wimbledon", "the championship": "Wimbledon", "wimby": "Wimbledon",
    "Wimbledon": "Wimbledon", "The Championship": "Wimbledon", "Wimby": "Wimbledon",
    
    # US Open variations
    "us open": "US Open", "us": "US Open",
    "US Open": "US Open", "US": "US Open"
}

TOURNEY_LEVEL_MAPPINGS = {
    # ATP Levels
    'G': 'G',  # Grand Slam
    'M': 'M',  # Masters 1000
    'A': 'A',  # ATP Tour
    'C': 'C',  # Challenger
    'D': 'D',  # Davis Cup (ATP only)
    'F': 'F',  # Tour Finals
    'E': 'E',  # Exhibition
    'J': 'J',  # Juniors
    'O': 'O',  # Olympics
    
    # WTA Levels
    'PM': 'PM',  # Premier Mandatory
    'P': 'P',    # Premier
    'I': 'I',    # International
    'W': 'W',    # WTA Tour
    'CC': 'CC',  # Colgate Series
    
    # Historical WTA Tiers → Modern equivalents
    'T1': 'PM',  # Tier I → Premier Mandatory
    'T2': 'P',   # Tier II → Premier
    'T3': 'I',   # Tier III → International
    'T4': 'I',   # Tier IV → International
    'T5': 'I',   # Tier V → International
    
    # ITF Prize Money Levels
    '10': 'ITF_10K', '15': 'ITF_15K', '20': 'ITF_20K', '25': 'ITF_25K',
    '35': 'ITF_35K', '40': 'ITF_40K', '50': 'ITF_50K', '60': 'ITF_60K',
    '75': 'ITF_75K', '80': 'ITF_80K', '100': 'ITF_100K', '200': 'ITF_200K'
}

COMBINED_TOURNAMENT_MAPPINGS = {
    "rome": {"atp": "Rome Masters", "wta": "Rome"},
    "basel": {"atp": "Basel", "wta": "Basel"},
    "madrid": {"atp": "Madrid Masters", "wta": "Madrid"},
    "indian wells": {"atp": "Indian Wells Masters", "wta": "Indian Wells"},
    "miami": {"atp": "Miami Masters", "wta": "Miami"},
    "monte carlo": {"atp": "Monte Carlo Masters", "wta": "Monte Carlo"},
    "hamburg": {"atp": "Hamburg", "wta": "Hamburg"},
    "stuttgart": {"atp": "Stuttgart", "wta": "Stuttgart"},
    "eastbourne": {"atp": "Eastbourne", "wta": "Eastbourne"},
    "newport": {"atp": "Newport", "wta": "Newport"},
    "atlanta": {"atp": "Atlanta", "wta": "Atlanta"},
    "washington": {"atp": "Washington", "wta": "Washington"},
    "toronto": {"atp": "Toronto Masters", "wta": "Toronto"},
    "montreal": {"atp": "Montreal Masters", "wta": "Montreal"},
    "cincinnati": {"atp": "Cincinnati Masters", "wta": "Cincinnati"},
    "winston salem": {"atp": "Winston Salem", "wta": "Winston Salem"},
    "stockholm": {"atp": "Stockholm", "wta": "Stockholm"},
    "antwerp": {"atp": "Antwerp", "wta": "Antwerp"},
    "vienna": {"atp": "Vienna", "wta": "Vienna"},
    "paris": {"atp": "Paris Masters", "wta": "Paris"},
    "auckland": {"atp": "Auckland", "wta": "Auckland"}
}

# =============================================================================
# OPTIMIZED MAPPING FUNCTIONS WITH FUZZY NORMALIZATION
# =============================================================================

def _normalize_key(text: str) -> str:
    """Standardize input by removing special chars and extra whitespace for fuzzy matching."""
    return re.sub(r'[^a-z0-9]', '', text.lower().strip())

# Pre-compute normalized dictionaries once at startup for O(1) lookups
# This eliminates runtime normalization overhead
_NORM_SURFACES = {_normalize_key(k): v for k, v in SURFACE_MAPPINGS.items()}
_NORM_ROUNDS = {_normalize_key(k): v for k, v in ROUND_MAPPINGS.items()}
_NORM_TOURNAMENTS = {_normalize_key(k): v for k, v in GRAND_SLAM_MAPPINGS.items()}
_NORM_COMBINED = {_normalize_key(k): v for k, v in COMBINED_TOURNAMENT_MAPPINGS.items()}
_NORM_TOURS = {_normalize_key(k): v for k, v in TOUR_MAPPINGS.items()}
_NORM_HANDS = {_normalize_key(k): v for k, v in HAND_MAPPINGS.items()}

@lru_cache(maxsize=256)
def _resolve_term(term: str) -> Dict[str, Any]:
    """
    Internal logic to find a match across all categories with fuzzy normalization.
    Returns Python dictionary directly (no JSON overhead).
    
    Priority order:
    1. Tournaments (Grand Slams)
    2. Combined Tournaments (Rome, Madrid, etc.)
    3. Rounds
    4. Surfaces
    5. Tours
    6. Hands
    """
    norm_term = _normalize_key(term)
    
    # Priority 1: Grand Slam Tournaments
    if norm_term in _NORM_TOURNAMENTS:
        return {
            "value": _NORM_TOURNAMENTS[norm_term],
            "category": "tournament",
            "type": "grand_slam"
        }
    
    # Priority 2: Combined Tournaments (Now with fuzzy support!)
    if norm_term in _NORM_COMBINED:
        return {
            "value": _NORM_COMBINED[norm_term],
            "category": "tournament",
            "type": "combined_event"
        }
    
    # Priority 3: Rounds
    if norm_term in _NORM_ROUNDS:
        return {
            "value": _NORM_ROUNDS[norm_term],
            "category": "round",
            "type": "tennis_round"
        }
    
    # Priority 4: Surfaces
    if norm_term in _NORM_SURFACES:
        return {
            "value": _NORM_SURFACES[norm_term],
            "category": "surface",
            "type": "tennis_surface"
        }
    
    # Priority 5: Tours
    if norm_term in _NORM_TOURS:
        return {
            "value": _NORM_TOURS[norm_term],
            "category": "tour",
            "type": "tennis_tour"
        }
    
    # Priority 6: Hands
    if norm_term in _NORM_HANDS:
        return {
            "value": _NORM_HANDS[norm_term],
            "category": "hand",
            "type": "tennis_hand"
        }
    
    # Unknown term
    return {
        "value": term,
        "category": "unknown",
        "type": "unknown",
        "suggestion": f"Try searching for '{term}' directly in the database using LIKE operator."
    }

# =============================================================================
# TENNIS MAPPING TOOLS (OPTIMIZED FOR PRODUCTION)
# =============================================================================

class TennisMappingTools:
    """
    Optimized tennis mapping tools for production-level LLM applications.
    
    Key optimizations:
    - Returns Python dictionaries directly (no JSON overhead)
    - Fuzzy normalization handles variations like "Australian-Open" or "Claycourt"
    - Consolidated tools reduce LLM decision fatigue
    - Pre-computed normalized dictionaries for O(1) lookups
    - Batch processing support for multiple terms
    """
    
    @staticmethod
    def create_terminology_resolver_tool():
        """
        A single consolidated tool for all tennis-specific mappings.
        Reduces tool-switching overhead for the LLM and allows batch processing.
        
        This replaces the previous separate tools for:
        - Tournament mapping
        - Round mapping
        - Surface mapping
        - Tour mapping
        - Hand mapping
        """
        @tool
        def resolve_tennis_terms(terms: Union[str, List[str]]) -> Dict[str, Any]:
            """
            Resolves tennis terminology (surfaces, rounds, tournaments, tours, hands) to DB values.
            Accepts a single term or a list of terms for batch processing.
            
            Handles fuzzy matching: "Australian-Open", "aus open", and "usopen" all map correctly.
            
            Args:
                terms: A single term string or list of terms like ['clay', 'semi-finals', 'roland garros']
            
            Returns:
                Dictionary mapping each term to its resolved value:
                {
                    "term1": {
                        "value": "database_value",
                        "category": "tournament|round|surface|tour|hand",
                        "type": "specific_type"
                    },
                    ...
                }
            """
            # Handle both single string and list inputs
            if isinstance(terms, str):
                terms = [terms]
            
            results = {}
            for term in terms:
                results[term] = _resolve_term(term)
            
            return results
        
        return resolve_tennis_terms
    
    @staticmethod
    def create_ranking_analysis_tool():
        """
        Consolidated ranking analysis tool.
        Directly merges dictionaries for zero-overhead performance.
        Returns Python dictionary directly (no JSON overhead).
        """
        @tool
        def analyze_ranking_question(question: str, year: int = None, tour: str = None) -> Dict[str, Any]:
            """
            Analyzes ranking questions and provides optimized SQL templates.
            
            Args:
                question: The ranking question to analyze (e.g., "Who was ranked #1 in 2020?")
                year: Optional year for temporal context (will be extracted from question if not provided)
                tour: Optional tour specification (ATP or WTA, will be inferred if not provided)
                
            Returns:
                Dictionary containing:
                - question_type: Classification of the ranking question
                - extracted_parameters: Year, rank limit, players, tour (if found in question)
                - data_source: Recommended tables and join requirements
                - sql_templates: Ready-to-use SQL query templates with window function optimizations
                - recommendations: Best practices for query construction
                - usage_note: Guidance on how to use the provided templates
            """
            # context is already a dict now! No parsing needed
            context = get_ranking_context(question, year, tour)
            
            # Extract parameters from question
            parameters = extract_ranking_parameters(question)
            
            # Direct dictionary merge (Fastest method)
            return {
                **context,
                "extracted_parameters": parameters,
                "usage_note": "Adapt templates using extracted_parameters."
            }
        
        return analyze_ranking_question
    
    @staticmethod
    def create_all_mapping_tools() -> List:
        """
        Create optimized tennis mapping tools.
        
        The "Power Duo": Just two tools that cover everything.
        1. Terminology Resolver (Terms -> DB Values) - Handles all mapping needs
        2. Ranking Analysis (Logic & SQL Templates) - Handles ranking queries
        
        This reduces from 4 tools to 2, significantly reducing:
        - Context window size (fewer tool descriptions for LLM to read)
        - Decision fatigue (fewer choices for LLM)
        - Tool-switching overhead
        
        Returns:
            List of optimized mapping tools compatible with LangChain.
        """
        return [
            TennisMappingTools.create_terminology_resolver_tool(),
            TennisMappingTools.create_ranking_analysis_tool()
        ]

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'TennisMappingTools',
    'ROUND_MAPPINGS',
    'SURFACE_MAPPINGS', 
    'TOUR_MAPPINGS',
    'HAND_MAPPINGS',
    'GRAND_SLAM_MAPPINGS',
    'TOURNEY_LEVEL_MAPPINGS',
    'COMBINED_TOURNAMENT_MAPPINGS'
]
