"""
Tennis Schema Pruner

Implements dynamic column pruning to reduce token count by filtering
CREATE TABLE statements based on user query intent.
"""

import re
from typing import Dict, List, Set


class TennisSchemaPruner:
    """
    Prunes database schema DDL based on user query to reduce token count.
    
    Categorizes columns into three tiers:
    - Tier 1 (Always Include): Essential columns for almost every query
    - Tier 2 (Conditional): Only included if query mentions specific metrics
    - Tier 3 (Never Include): Internal IDs or metadata rarely used
    """
    
    # Constraint keywords to preserve in DDL
    CONSTRAINT_KEYWORDS = {'PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'INDEX'}
    
    def __init__(self, full_schema: str) -> None:
        """
        Initialize the schema pruner with full database schema.
        
        Args:
            full_schema: Complete database schema string from db.get_table_info()
        """
        self.full_schema = full_schema
        
        # Tier 1: Core columns that are almost always needed
        # Note: atp_matches and wta_matches have the same structure as matches
        self.core_cols = {
            'matches': [
                'winner_name', 'loser_name', 'tourney_name', 'event_year',
                'score', 'round', 'surface', 'tour', 'tourney_date',
                'tourney_level', 'winner_id', 'loser_id'
            ],
            'atp_matches': [
                'winner_name', 'loser_name', 'tourney_name', 'event_year',
                'score', 'round', 'surface', 'tourney_date',
                'tourney_level', 'winner_id', 'loser_id'
            ],
            'wta_matches': [
                'winner_name', 'loser_name', 'tourney_name', 'event_year',
                'score', 'round', 'surface', 'tourney_date',
                'tourney_level', 'winner_id', 'loser_id'
            ]
        }
        
        # Tier 2: Mapping keywords in user query to specific columns
        # Optimized: Pre-compute reverse lookup for faster matching
        self.stat_map = {
            'ace': ['w_ace', 'l_ace'],
            'aces': ['w_ace', 'l_ace'],
            'double fault': ['w_df', 'l_df'],
            'double faults': ['w_df', 'l_df'],
            'fault': ['w_df', 'l_df'],
            'faults': ['w_df', 'l_df'],
            'df': ['w_df', 'l_df'],
            'serve': [
                'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_svpt',
                'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_svpt',
                'w_ace', 'l_ace', 'w_df', 'l_df'
            ],
            'serving': [
                'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_svpt',
                'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_svpt'
            ],
            'first serve': ['w_1stIn', 'w_1stWon', 'l_1stIn', 'l_1stWon'],
            'break': [
                'w_bpSaved', 'w_bpFaced', 'l_bpSaved', 'l_bpFaced'
            ],
            'break point': [
                'w_bpSaved', 'w_bpFaced', 'l_bpSaved', 'l_bpFaced'
            ],
            'breakpoint': [
                'w_bpSaved', 'w_bpFaced', 'l_bpSaved', 'l_bpFaced'
            ],
            'bp': ['w_bpSaved', 'w_bpFaced', 'l_bpSaved', 'l_bpFaced'],
            'rank': [
                'winner_rank', 'loser_rank',
                'winner_rank_points', 'loser_rank_points'
            ],
            'ranking': [
                'winner_rank', 'loser_rank',
                'winner_rank_points', 'loser_rank_points'
            ],
            'points': ['winner_rank_points', 'loser_rank_points'],
            'age': ['winner_age', 'loser_age'],
            'height': ['winner_ht', 'loser_ht'],
            'hand': ['winner_hand', 'loser_hand'],
            'handedness': ['winner_hand', 'loser_hand'],
            'country': ['winner_ioc', 'loser_ioc'],
            'nationality': ['winner_ioc', 'loser_ioc'],
            'ioc': ['winner_ioc', 'loser_ioc'],
            'seed': ['winner_seed', 'loser_seed'],
            'seeded': ['winner_seed', 'loser_seed'],
            'entry': ['winner_entry', 'loser_entry'],
            'minutes': ['minutes'],
            'duration': ['minutes'],
            'time': ['minutes'],
            'set': ['set1', 'set2', 'set3', 'set4', 'set5'],
            'sets': ['set1', 'set2', 'set3', 'set4', 'set5'],
            'best of': ['best_of'],
            'status': ['match_status'],
            'retired': ['match_status'],
            'retirement': ['match_status'],
            'walkover': ['match_status'],
        }
        
        # Pre-compute keyword set for faster lookup
        self.stat_keywords = set(self.stat_map.keys())
        
        # Tier 3: Columns to never include (internal IDs, metadata)
        # Note: atp_matches and wta_matches have similar excluded columns
        excluded_match_cols = [
            'match_num', 'draw_size', 'event_month', 'event_day',
            'created_at', 'updated_at', 'data_source', 'total_sets'
        ]
        self.excluded_cols = {
            'matches': excluded_match_cols,
            'atp_matches': excluded_match_cols,
            'wta_matches': excluded_match_cols
        }
        
        # Pre-compute excluded columns as set for faster lookup
        self.excluded_cols_set = {
            table: set(cols) for table, cols in self.excluded_cols.items()
        }
        
        # Tables that should be included based on query
        match_keywords = [
            'match', 'game', 'tournament', 'tourney',
            'player', 'won', 'lost', 'defeat'
        ]
        self.table_keywords = {
            'matches': match_keywords,
            'atp_matches': match_keywords + ['atp'],
            'wta_matches': match_keywords + ['wta'],
            'atp_players': ['atp', 'player', 'name'],
            'wta_players': ['wta', 'player', 'name'],
            'atp_rankings': ['atp', 'rank', 'ranking', 'points'],
            'wta_rankings': ['wta', 'rank', 'ranking', 'points'],
            'rankings': ['rank', 'ranking', 'points', 'official'],
            # MCP tables
            'atp_mcp_matches': match_keywords + ['atp', 'mcp', 'chart', 'point'],
            'wta_mcp_matches': match_keywords + ['wta', 'mcp', 'chart', 'point'],
            'atp_mcp_points': ['point', 'atp', 'mcp', 'chart', 'rally'],
            'wta_mcp_points': ['point', 'wta', 'mcp', 'chart', 'rally'],
        }
        
        # Cache parsed schema to avoid re-parsing on every query
        self._cached_table_blocks = None
        
        # Pre-compile regex patterns for better performance
        self._re_create_table = re.compile(
            r'CREATE TABLE\s+(\w+)\s*\([^;]+\);',
            re.IGNORECASE | re.DOTALL
        )
        self._re_table_content = re.compile(
            r'CREATE TABLE\s+\w+\s*\((.*?)\);',
            re.IGNORECASE | re.DOTALL
        )
        self._re_table_name = re.compile(
            r'CREATE TABLE\s+(\w+)',
            re.IGNORECASE
        )
        self._re_column_name = re.compile(r'(\w+)')
        
        self._parse_schema()
    
    def prune_schema(self, user_query: str) -> str:
        """
        Prune the full schema based on user query intent.
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Pruned schema string with only relevant columns
        """
        query_lower = user_query.lower()
        
        # Step 1: Identify which tables are needed
        needed_tables = self._identify_tables(query_lower)
        
        # Step 2: For each table, identify which columns are needed
        pruned_schema_parts = []
        
        # Use cached table blocks instead of re-parsing
        table_blocks = self._cached_table_blocks
        
        # Detect which match tables exist in the schema
        has_unified_matches = 'matches' in table_blocks
        has_atp_matches = 'atp_matches' in table_blocks
        has_wta_matches = 'wta_matches' in table_blocks
        
        for table_name, table_ddl in table_blocks.items():
            if table_name in needed_tables:
                # Prune columns for this table
                pruned_ddl = self._prune_table_ddl(
                    table_name, table_ddl, query_lower
                )
                if pruned_ddl:
                    pruned_schema_parts.append(pruned_ddl)
            elif table_name == 'matches' and has_unified_matches:
                # Always include unified matches table, but pruned
                pruned_ddl = self._prune_table_ddl(
                    table_name, table_ddl, query_lower
                )
                if pruned_ddl:
                    pruned_schema_parts.append(pruned_ddl)
            elif table_name in ['atp_matches', 'wta_matches']:
                # Always include match tables (unified or separate), but pruned
                pruned_ddl = self._prune_table_ddl(
                    table_name, table_ddl, query_lower
                )
                if pruned_ddl:
                    pruned_schema_parts.append(pruned_ddl)
        
        # If no tables matched, return minimal match schema
        if not pruned_schema_parts:
            # Fallback: return pruned match table(s) only
            if has_unified_matches:
                pruned_ddl = self._prune_table_ddl(
                    'matches', table_blocks['matches'], query_lower
                )
                if pruned_ddl:
                    pruned_schema_parts.append(pruned_ddl)
            else:
                # New schema: include both atp_matches and wta_matches
                if has_atp_matches:
                    pruned_ddl = self._prune_table_ddl(
                        'atp_matches', table_blocks['atp_matches'], query_lower
                    )
                    if pruned_ddl:
                        pruned_schema_parts.append(pruned_ddl)
                if has_wta_matches:
                    pruned_ddl = self._prune_table_ddl(
                        'wta_matches', table_blocks['wta_matches'], query_lower
                    )
                    if pruned_ddl:
                        pruned_schema_parts.append(pruned_ddl)
        
        return (
            '\n\n'.join(pruned_schema_parts)
            if pruned_schema_parts
            else self.full_schema
        )
    
    def _parse_schema(self) -> None:
        """Parse and cache the schema once during initialization."""
        if self._cached_table_blocks is None:
            self._cached_table_blocks = self._split_schema_into_tables(
                self.full_schema
            )
    
    def _identify_tables(self, query_lower: str) -> Set[str]:
        """
        Identify which tables are needed based on query keywords.
        
        Args:
            query_lower: Lowercase user query
            
        Returns:
            Set of table names needed for the query
        """
        needed = set()
        
        # Check which match tables exist in the schema
        table_blocks = self._cached_table_blocks
        has_unified_matches = 'matches' in table_blocks
        has_atp_matches = 'atp_matches' in table_blocks
        has_wta_matches = 'wta_matches' in table_blocks
        
        # Always include match table(s) for tennis queries
        if has_unified_matches:
            needed.add('matches')
        else:
            # New schema: include both atp_matches and wta_matches
            if has_atp_matches:
                needed.add('atp_matches')
            if has_wta_matches:
                needed.add('wta_matches')
        
        # Check for ranking-related queries
        ranking_keywords = ['rank', 'ranking', 'points', 'official']
        if any(kw in query_lower for kw in ranking_keywords):
            if 'atp' in query_lower:
                needed.add('atp_rankings')
                needed.add('atp_players')
            elif 'wta' in query_lower:
                needed.add('wta_rankings')
                needed.add('wta_players')
            else:
                # Include both if tour not specified
                needed.add('atp_rankings')
                needed.add('wta_rankings')
                needed.add('atp_players')
                needed.add('wta_players')
        
        # Check for MCP-related queries (point-by-point, shot-level analysis)
        mcp_keywords = ['point', 'point-by-point', 'shot', 'rally', 'serve direction', 
                       'return depth', 'net point', 'key point', 'mcp']
        if any(kw in query_lower for kw in mcp_keywords):
            if 'atp' in query_lower:
                needed.add('atp_mcp_matches')
                needed.add('atp_mcp_points')
            elif 'wta' in query_lower:
                needed.add('wta_mcp_matches')
                needed.add('wta_mcp_points')
            else:
                # Include both if tour not specified
                needed.add('atp_mcp_matches')
                needed.add('atp_mcp_points')
                needed.add('wta_mcp_matches')
                needed.add('wta_mcp_points')
        
        return needed
    
    def _split_schema_into_tables(self, schema: str) -> Dict[str, str]:
        """
        Split schema string into individual table DDL blocks.
        
        Args:
            schema: Full database schema string
            
        Returns:
            Dictionary mapping table names to their DDL strings
        """
        tables = {}
        
        # Use pre-compiled regex pattern for better performance
        matches = self._re_create_table.finditer(schema)
        
        for match in matches:
            table_name = match.group(1).lower()
            table_ddl = match.group(0)
            tables[table_name] = table_ddl
        
        return tables
    
    def _prune_table_ddl(
        self, table_name: str, table_ddl: str, query_lower: str
    ) -> str:
        """
        Prune columns from a single table's DDL.
        
        Args:
            table_name: Name of the table
            table_ddl: CREATE TABLE DDL statement for the table
            query_lower: Lowercase user query
            
        Returns:
            Pruned DDL statement with only relevant columns
        """
        # Check if this is a match table (unified or separate)
        is_match_table = table_name in ['matches', 'atp_matches', 'wta_matches']
        
        if not is_match_table:
            # For non-match tables, return full DDL (they're smaller)
            # Exception: MCP tables might be large, but we'll include them fully for now
            return table_ddl
        
        # Extract column definitions from CREATE TABLE statement
        # Find the content between parentheses using pre-compiled regex
        match = self._re_table_content.search(table_ddl)
        if not match:
            return table_ddl
        
        columns_content = match.group(1)
        
        # Identify which columns to keep
        # Handle both unified 'matches' and separate 'atp_matches'/'wta_matches'
        if table_name in ['atp_matches', 'wta_matches']:
            # Use the same core columns as matches (they have the same structure)
            selected_cols = set(self.core_cols.get('matches', []))
        else:
            selected_cols = set(self.core_cols.get(table_name, []))
        
        # Optimized: Check keywords more efficiently
        # For single-word keywords, check if they appear in query words
        query_words = set(query_lower.split())
        single_word_keywords = {
            kw for kw in self.stat_keywords if ' ' not in kw
        }
        found_single_words = single_word_keywords.intersection(query_words)
        
        # Add columns for found single-word keywords
        for keyword in found_single_words:
            selected_cols.update(self.stat_map[keyword])
        
        # Check multi-word keywords (must check as substring)
        for keyword in self.stat_map.keys():
            if ' ' in keyword and keyword in query_lower:
                selected_cols.update(self.stat_map[keyword])
        
        # Remove excluded columns using pre-computed set
        excluded = self.excluded_cols_set.get(table_name, set())
        selected_cols -= excluded
        
        # Optimized column parsing: Split by comma while respecting
        # nested parentheses. More efficient than character-by-character
        # parsing
        lines = []
        current_line = ""
        paren_depth = 0
        
        for char in columns_content:
            if char == '(':
                paren_depth += 1
                current_line += char
            elif char == ')':
                paren_depth -= 1
                current_line += char
            elif char == ',' and paren_depth == 0:
                if current_line.strip():
                    lines.append(current_line.strip())
                current_line = ""
            else:
                current_line += char
        
        # Add the last line
        if current_line.strip():
            lines.append(current_line.strip())
        
        filtered_lines = []
        
        for line in lines:
            if not line:
                continue
            
            # Extract column name (first word before space or parenthesis)
            # Use pre-compiled regex
            col_match = self._re_column_name.match(line)
            if col_match:
                col_name = col_match.group(1).lower()
                
                # Keep if in selected columns
                if col_name in selected_cols:
                    filtered_lines.append(line)
            else:
                # Keep constraints and other non-column definitions
                # (like PRIMARY KEY, FOREIGN KEY, etc.)
                line_upper = line.upper()
                if any(
                    keyword in line_upper
                    for keyword in self.CONSTRAINT_KEYWORDS
                ):
                    filtered_lines.append(line)
        
        # Rebuild CREATE TABLE statement
        if not filtered_lines:
            # Fallback: return minimal version with core columns
            core_cols_ddl = ',\n    '.join([
                f"{col} TEXT"
                for col in self.core_cols.get(table_name, [])
            ])
            table_match = self._re_table_name.match(table_ddl)
            table_name_orig = (
                table_match.group(1) if table_match else table_name
            )
            return (
                f"CREATE TABLE {table_name_orig} (\n"
                f"    {core_cols_ddl}\n"
                ");"
            )
        
        filtered_content = ',\n    '.join(filtered_lines)
        
        # Reconstruct the CREATE TABLE statement using pre-compiled regex
        table_match = self._re_table_name.match(table_ddl)
        if table_match:
            return (
                f"CREATE TABLE {table_match.group(1)} (\n"
                f"    {filtered_content}\n"
                ");"
            )
        
        return table_ddl
