/**
 * TypeScript types matching backend Pydantic models
 * These types should stay in sync with backend/main.py models
 * 
 * To auto-generate from OpenAPI schema, run:
 * npm run generate:types
 */

// ============================================================================
// Request Types (matching backend Pydantic models)
// ============================================================================



export interface StatsRequest {
  player_name: string;
  opponent?: string | null;
  tournament?: string | null;
  surface?: string[] | null;
  year?: string | null;
}

export interface FilterState {
  player_name: string;
  opponent: string;
  tournament: string;
  surface: string[];
  year: string;
}

export interface ServeStatsRequest extends StatsRequest {
  // Inherits all fields from StatsRequest
}

export interface ReturnStatsRequest extends StatsRequest {
  // Inherits all fields from StatsRequest
}

export interface RankingStatsRequest {
  player_name: string;
  opponent?: string | null;
  tournament?: string | null;
  surface?: string[] | null;
  year?: string | null;
}

// ============================================================================
// Response Types (matching backend Pydantic models)
// ============================================================================

export interface FilterOptionsResponse {
  players: string[];
  tournaments: string[];
  opponents?: string[] | null;
  surfaces?: string[] | null;
  year_range?: { min: number; max: number } | null;
}



// Plotly chart data structure (from json.loads(fig.to_json()))
export interface PlotlyChartData {
  data: any[];
  layout: any;
  config?: any;
}

export interface ServeStatsResponse {
  timeline_chart?: PlotlyChartData;
  ace_df_chart?: PlotlyChartData;
  bp_chart?: PlotlyChartData;
  radar_chart?: PlotlyChartData;
  // Raw data for frontend visualization
  matches?: any[];
  aggregated_stats?: Record<string, number | null>;
  aggregated_opponent_stats?: Record<string, number | null>;
  error?: string;
}

// Raw match-level data for frontend visualization
export interface RawServeMatch {
  match_index: number;
  year: string;
  tourney_name: string;
  round: string;
  opponent: string;
  opponent_rank: number | null;
  result: string;
  surface: string;
  tourney_date: string;
  player_1stIn: number | null;
  player_1stWon: number | null;
  player_2ndWon: number | null;
  player_ace_rate: number | null;
  player_df_rate: number | null;
  player_bpFaced: number | null;
  player_bpSaved: number | null;
  player_bpSavePct: number | null;
  opponent_1stIn: number | null;
  opponent_1stWon: number | null;
  opponent_2ndWon: number | null;
  opponent_ace_rate: number | null;
  opponent_df_rate: number | null;
}

export interface RawServeStatsResponse {
  matches: RawServeMatch[];
  player_name: string;
  filters: {
    opponent?: string | null;
    tournament?: string | null;
    year?: string | null;
    surface?: string[] | null;
  };
}

export interface ReturnStatsResponse {
  return_points_chart?: PlotlyChartData;
  bp_conversion_chart?: PlotlyChartData;
  radar_chart?: PlotlyChartData;
  // Raw data for frontend visualization
  matches?: any[];
  aggregated_stats?: Record<string, number | null>;
  aggregated_opponent_stats?: Record<string, number | null>;
  error?: string;
}

export interface RankingStatsResponse {
  ranking_chart?: PlotlyChartData;
  // Raw data
  ranking_data?: any[];
  error?: string;
  reasons?: string[];
}

export interface Match {
  event_year: number;
  tourney_date: string;
  tourney_name: string;
  round: string;
  winner_name: string;
  loser_name: string;
  surface: string;
  score: string;
  [key: string]: any; // Allow additional fields
}

export interface MatchesResponse {
  matches: Match[];
  count: number;
}

// ============================================================================
// Frontend-specific types
// ============================================================================

export interface StatsFilters {
  player_name: string;
  opponent?: string;
  tournament?: string;
  surface?: string[];
  year?: string;
}

// Re-export for backward compatibility
export type FilterOptions = FilterOptionsResponse;

// ============================================================================
// AI Query Types
// ============================================================================

export interface AiQueryResponse {
  answer: string;
  sql_queries: string[];
  data: Record<string, unknown>[];
  conversation_flow: ConversationFlowItem[];
}

export interface ConversationFlowItem {
  role: string;
  content: string;
  [key: string]: unknown;
}

export interface AiQueryState {
  response: string;
  sqlQueries: string[];
  data: Record<string, unknown>[];
  conversationFlow: ConversationFlowItem[];
  loading: boolean;
  error: string;
}

// ============================================================================
// Auth Types
// ============================================================================

export interface UserResponse {
  id: number;
  username: string;
  created_at: string;
  last_login?: string | null;
}

export interface AuthCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

export interface AuthResponse {
  message: string;
  username: string;
}
