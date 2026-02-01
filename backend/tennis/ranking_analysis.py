"""
Tennis Ranking Analysis Module

This module provides intelligent ranking question analysis and data source determination
for tennis-related queries involving player rankings.
"""

import re
from enum import Enum
from functools import lru_cache
from typing import Dict, Optional, Any


class RankingQuestionType(Enum):
    """Types of ranking questions."""

    OFFICIAL_RANKINGS = "official_rankings"  # Year-end, weekly rankings
    MATCH_TIME_RANKINGS = "match_time_rankings"  # Winner/loser rank at match time
    CAREER_HIGH_RANKINGS = "career_high"  # Best ranking achieved
    RANKING_PROGRESSION = "ranking_progression"  # Ranking changes over time
    RANKING_COMPARISON = "ranking_comparison"  # Compare rankings between players


# Ranking question patterns for classification
RANKING_PATTERNS = {
    # Official Rankings Patterns
    "top.*in.*year": RankingQuestionType.OFFICIAL_RANKINGS,
    "ranked.*in.*": RankingQuestionType.OFFICIAL_RANKINGS,
    "year.*end.*rank": RankingQuestionType.OFFICIAL_RANKINGS,
    "weekly.*rank": RankingQuestionType.OFFICIAL_RANKINGS,
    "top.*players.*in": RankingQuestionType.OFFICIAL_RANKINGS,
    "who.*were.*top": RankingQuestionType.OFFICIAL_RANKINGS,
    "rankings.*in": RankingQuestionType.OFFICIAL_RANKINGS,
    # Match-time Rankings Patterns
    "rank.*when.*beat": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*during.*match": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*at.*time.*match": RankingQuestionType.MATCH_TIME_RANKINGS,
    "winner.*rank": RankingQuestionType.MATCH_TIME_RANKINGS,
    "loser.*rank": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*when.*won": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*when.*lost": RankingQuestionType.MATCH_TIME_RANKINGS,
    # Career High Patterns
    "highest.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "best.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "peak.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "career.*high": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "maximum.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    # Progression Patterns
    "rank.*improvement": RankingQuestionType.RANKING_PROGRESSION,
    "rank.*decline": RankingQuestionType.RANKING_PROGRESSION,
    "rank.*change": RankingQuestionType.RANKING_PROGRESSION,
    "ranking.*evolution": RankingQuestionType.RANKING_PROGRESSION,
    "rank.*progress": RankingQuestionType.RANKING_PROGRESSION,
    # Comparison Patterns
    "compare.*rank": RankingQuestionType.RANKING_COMPARISON,
    "rank.*vs": RankingQuestionType.RANKING_COMPARISON,
    "rank.*between": RankingQuestionType.RANKING_COMPARISON,
}


# Data source mapping for different ranking question types
RANKING_DATA_SOURCES = {
    RankingQuestionType.OFFICIAL_RANKINGS: {
        "primary_table": "atp_rankings/wta_rankings",
        "backup_table": "matches",
        "key_fields": ["ranking_date", "rank", "player", "player_name"],
        "join_required": True,
        "tour_separation": True,
        "description": "Official ATP/WTA rankings (use UNION for both tours)",
    },
    RankingQuestionType.MATCH_TIME_RANKINGS: {
        "primary_table": "matches",
        "backup_table": "matches",
        "key_fields": [
            "winner_rank",
            "loser_rank",
            "event_year",
            "tourney_name",
            "winner_name",
            "loser_name",
        ],
        "join_required": False,
        "tour_separation": False,
        "description": "Match-specific rankings at time of match",
    },
    RankingQuestionType.CAREER_HIGH_RANKINGS: {
        "primary_table": "atp_rankings/wta_rankings",
        "backup_table": "matches",
        "key_fields": ["rank", "player", "player_name"],
        "join_required": True,
        "tour_separation": True,
        "description": "Career high rankings (use UNION for both tours)",
    },
    RankingQuestionType.RANKING_PROGRESSION: {
        "primary_table": "atp_rankings/wta_rankings",
        "backup_table": "matches",
        "key_fields": ["ranking_date", "rank", "player", "player_name"],
        "join_required": True,
        "tour_separation": True,
        "description": "Ranking progression over time (use UNION for both tours)",
    },
    RankingQuestionType.RANKING_COMPARISON: {
        "primary_table": "atp_rankings/wta_rankings",
        "backup_table": "matches",
        "key_fields": ["ranking_date", "rank", "player", "player_name"],
        "join_required": True,
        "tour_separation": True,
        "description": "Ranking comparisons between players (use UNION for both tours)",
    },
}


# SQL templates for different ranking question types
# Note: For queries requiring player names, use UNION to combine ATP and WTA rankings
# and join with respective players tables (atp_players/wta_players)
# Optimized with window functions for better performance on large datasets
RANKING_SQL_TEMPLATES = {
    RankingQuestionType.OFFICIAL_RANKINGS: {
        "top_players_year": """
            SELECT player_name, rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    ar.rank,
                    RANK() OVER (ORDER BY ar.rank ASC) as r
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE ar.ranking_date = '{year}-12-30'
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    wr.rank,
                    RANK() OVER (ORDER BY wr.rank ASC) as r
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE wr.ranking_date = '{year}-12-30'
            )
            WHERE r <= {limit}
            ORDER BY rank
            LIMIT {limit}
        """,
        "top_players_week": """
            SELECT player_name, rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    ar.rank,
                    RANK() OVER (ORDER BY ar.rank ASC) as r
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE ar.ranking_date = '{date}'
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    wr.rank,
                    RANK() OVER (ORDER BY wr.rank ASC) as r
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE wr.ranking_date = '{date}'
            )
            WHERE r <= {limit}
            ORDER BY rank
            LIMIT {limit}
        """,
        "specific_rank": """
            SELECT player_name, rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    ar.rank,
                    RANK() OVER (PARTITION BY ar.ranking_date ORDER BY ar.rank ASC) as r
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE ar.ranking_date = '{date}'
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    wr.rank,
                    RANK() OVER (PARTITION BY wr.ranking_date ORDER BY wr.rank ASC) as r
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE wr.ranking_date = '{date}'
            )
            WHERE r = {rank}
        """,
        "who_was_number_one": """
            SELECT player_name, ranking_date, rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    ar.ranking_date,
                    ar.rank,
                    RANK() OVER (PARTITION BY ar.ranking_date ORDER BY ar.rank ASC) as r
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE ar.ranking_date BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    wr.ranking_date,
                    wr.rank,
                    RANK() OVER (PARTITION BY wr.ranking_date ORDER BY wr.rank ASC) as r
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE wr.ranking_date BETWEEN '{start_date}' AND '{end_date}'
            )
            WHERE r = 1
            ORDER BY ranking_date
        """,
    },
    RankingQuestionType.MATCH_TIME_RANKINGS: {
        "winner_rank_at_match": """
            SELECT winner_name, winner_rank, event_year, tourney_name
            FROM matches 
            WHERE LOWER(winner_name) = LOWER('{player}') 
              AND event_year = {year}
              AND winner_rank IS NOT NULL
            ORDER BY event_year, tourney_name
        """,
        "loser_rank_at_match": """
            SELECT loser_name, loser_rank, event_year, tourney_name
            FROM matches 
            WHERE LOWER(loser_name) = LOWER('{player}') 
              AND event_year = {year}
              AND loser_rank IS NOT NULL
            ORDER BY event_year, tourney_name
        """,
        "rank_during_match": """
            SELECT winner_name, loser_name, winner_rank, loser_rank, event_year, tourney_name
            FROM matches 
            WHERE ((LOWER(winner_name) = LOWER('{player1}') AND LOWER(loser_name) = LOWER('{player2}'))
               OR (LOWER(winner_name) = LOWER('{player2}') AND LOWER(loser_name) = LOWER('{player1}')))
              AND event_year = {year}
              AND (winner_rank IS NOT NULL OR loser_rank IS NOT NULL)
        """,
    },
    RankingQuestionType.CAREER_HIGH_RANKINGS: {
        "career_high_rank": """
            SELECT player_name, career_high_rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    MIN(ar.rank) as career_high_rank
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE LOWER(COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last)) = LOWER('{player}')
                GROUP BY ap.player_id, ap.full_name, ap.name_first, ap.name_last
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    MIN(wr.rank) as career_high_rank
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE LOWER(COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last)) = LOWER('{player}')
                GROUP BY wp.player_id, wp.full_name, wp.name_first, wp.name_last
            )
            ORDER BY career_high_rank
            LIMIT 1
        """,
        "multiple_players_career_high": """
            SELECT player_name, career_high_rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    MIN(ar.rank) as career_high_rank
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE LOWER(COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last)) IN ({players})
                GROUP BY ap.player_id, ap.full_name, ap.name_first, ap.name_last
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    MIN(wr.rank) as career_high_rank
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE LOWER(COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last)) IN ({players})
                GROUP BY wp.player_id, wp.full_name, wp.name_first, wp.name_last
            )
            ORDER BY career_high_rank
        """,
    },
    RankingQuestionType.RANKING_PROGRESSION: {
        "player_rank_history": """
            SELECT ranking_date, rank
            FROM (
                SELECT 
                    ar.ranking_date,
                    ar.rank
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE LOWER(COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last)) = LOWER('{player}')
                  AND ar.ranking_date BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    wr.ranking_date,
                    wr.rank
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE LOWER(COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last)) = LOWER('{player}')
                  AND wr.ranking_date BETWEEN '{start_date}' AND '{end_date}'
            )
            ORDER BY ranking_date ASC
        """
    },
    RankingQuestionType.RANKING_COMPARISON: {
        "compare_players_rankings": """
            SELECT player_name, ranking_date, rank
            FROM (
                SELECT 
                    COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) as player_name,
                    ar.ranking_date,
                    ar.rank,
                    RANK() OVER (PARTITION BY ar.ranking_date ORDER BY ar.rank ASC) as date_rank
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE LOWER(COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last)) IN ({players})
                  AND ar.ranking_date BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) as player_name,
                    wr.ranking_date,
                    wr.rank,
                    RANK() OVER (PARTITION BY wr.ranking_date ORDER BY wr.rank ASC) as date_rank
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE LOWER(COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last)) IN ({players})
                  AND wr.ranking_date BETWEEN '{start_date}' AND '{end_date}'
            )
            ORDER BY ranking_date, rank
        """
    },
}


@lru_cache(maxsize=256)
def classify_ranking_question(question: str) -> RankingQuestionType:
    """
    Classify a ranking question into its appropriate type.

    Args:
        question: The ranking question to classify

    Returns:
        RankingQuestionType enum value
    """
    question_lower = question.lower()

    # Check patterns in order of specificity
    for pattern, question_type in RANKING_PATTERNS.items():
        if re.search(pattern, question_lower):
            return question_type

    # Default to official rankings if no pattern matches
    return RankingQuestionType.OFFICIAL_RANKINGS


@lru_cache(maxsize=256)
def get_ranking_context(
    question: str, year: Optional[int] = None, tour: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive ranking context for a question.
    Returns a dictionary directly to avoid double-parsing overhead.

    Args:
        question: The ranking question
        year: Optional year for temporal context
        tour: Optional tour specification

    Returns:
        Dictionary with ranking analysis and recommendations
    """
    # Classify question type
    question_type = classify_ranking_question(question)

    # Tour detection is handled by LLM via prompt instructions
    # If tour is not provided, LLM will determine it from the question context
    # or use UNION queries for ambiguous cases

    # Get appropriate data source
    data_source = RANKING_DATA_SOURCES.get(question_type)

    # Get SQL templates
    sql_templates = RANKING_SQL_TEMPLATES.get(question_type, {})

    return {
        "question_type": question_type.value,
        "data_source": data_source,
        "tour": tour,
        "year": year,
        "sql_templates": sql_templates,
        "recommendations": [
            f"Use table: {data_source['primary_table']}",
            f"Tour separation: {data_source['tour_separation']}",
            f"Join required: {data_source['join_required']}",
            "Use window functions (RANK(), DENSE_RANK()) for complex multi-year comparisons.",
            "Ensure player_id is indexed for rank history lookups.",
            "Filter date ranges in WHERE clause before applying window functions to limit dataset size.",
        ],
    }


@lru_cache(maxsize=128)
def get_ranking_sql_approach(
    question_type: str, tour: str = "ATP", year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get SQL approach for ranking questions.
    Returns a dictionary directly to avoid double-parsing overhead.

    Args:
        question_type: Type of ranking question
        tour: Tour type (ATP or WTA)
        year: Optional year for temporal context

    Returns:
        Dictionary with SQL approach
    """
    question_type_enum = RankingQuestionType(question_type)
    data_source = RANKING_DATA_SOURCES.get(question_type_enum)
    sql_templates = RANKING_SQL_TEMPLATES.get(question_type_enum, {})

    return {
        "data_source": data_source,
        "sql_templates": sql_templates,
        "tour": tour,
        "year": year,
        "key_considerations": {
            "tour_separation": data_source["tour_separation"],
            "join_required": data_source["join_required"],
            "primary_table": data_source["primary_table"],
        },
    }


# Stop words to filter out from player name extraction
STOP_WORDS = {
    "Grand",
    "Slam",
    "Open",
    "Masters",
    "Final",
    "Tour",
    "ATP",
    "WTA",
    "French",
    "Australian",
    "Wimbledon",
    "Roland",
    "Garros",
    "Championship",
    "Tournament",
    "Tourney",
    "Event",
    "Match",
    "Round",
    "Quarter",
    "Semi",
}


def extract_ranking_parameters(question: str) -> Dict[str, Any]:
    """
    Extract key parameters from ranking questions.

    Args:
        question: The ranking question

    Returns:
        Dictionary with extracted parameters
    """
    parameters = {"year": None, "rank_limit": None, "players": [], "tour": None}

    # Extract year
    year_match = re.search(r"\b(19|20)\d{2}\b", question)
    if year_match:
        parameters["year"] = int(year_match.group())

    # Extract rank limit (top 10, top 5, etc.)
    rank_match = re.search(r"top\s+(\d+)", question.lower())
    if rank_match:
        parameters["rank_limit"] = int(rank_match.group(1))

    # Extract specific rank
    specific_rank_match = re.search(r"rank(?:ed)?\s+(\d+)", question.lower())
    if specific_rank_match:
        parameters["rank_limit"] = int(specific_rank_match.group(1))

    # Extract player names (basic pattern)
    # This could be enhanced with more sophisticated NLP
    player_patterns = [
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # First Last
        r"([A-Z][a-z]+)",  # Single name
    ]

    for pattern in player_patterns:
        matches = re.findall(pattern, question)
        parameters["players"].extend(matches)

    # Clean players: Remove stop words and common tennis terms
    parameters["players"] = [
        p
        for p in parameters["players"]
        if p not in STOP_WORDS and len(p) > 1  # Filter stop words and single characters
    ]

    return parameters


# Export key functions
__all__ = [
    "RankingQuestionType",
    "classify_ranking_question",
    "get_ranking_context",
    "get_ranking_sql_approach",
    "extract_ranking_parameters",
    "RANKING_DATA_SOURCES",
    "RANKING_SQL_TEMPLATES",
]
