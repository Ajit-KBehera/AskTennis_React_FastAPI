import axios from 'axios';
import type {
  FilterOptionsResponse,
  ChatRequest,
  ChatResponse,
  StatsRequest,
  ServeStatsRequest,
  ReturnStatsRequest,
  RankingStatsRequest,
  ServeStatsResponse,
  ReturnStatsResponse,
  RankingStatsResponse,
  MatchesResponse,
  RawServeStatsResponse,
} from '../types';

// Automatically detect API URL based on current hostname
// If accessed from network IP, use that IP for backend too
// Otherwise, use localhost
const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If not localhost, use the same hostname for backend
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:8000/api`;
    }
  }
  // Default to localhost for development
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const endpoints = {
  getFilters: '/filters',
  chat: '/chat',
  query: '/query',  // Full AI query with SQL and data
  getServeStats: '/stats/serve',
  getRawServeStats: '/stats/serve/raw',
  getReturnStats: '/stats/return',
  getRankingStats: '/stats/ranking',
  getMatches: '/matches',
};

// Re-export types for convenience
export type {
  FilterOptionsResponse,
  ChatRequest,
  ChatResponse,
  StatsRequest,
  ServeStatsRequest,
  ReturnStatsResponse,
  RankingStatsResponse,
  MatchesResponse,
  Match,
  StatsFilters,
} from '../types';

// Type-safe API methods
export const api = {
  /**
   * Get filter options for the sidebar
   * @param playerName Optional player name to get player-specific filters
   */
  getFilters: async (playerName?: string): Promise<FilterOptionsResponse> => {
    const response = await apiClient.get<FilterOptionsResponse>(endpoints.getFilters, {
      params: playerName ? { player_name: playerName } : undefined,
    });
    return response.data;
  },

  /**
   * Send a chat message to the AI agent
   */
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>(endpoints.chat, request);
    return response.data;
  },

  /**
   * Get serve statistics charts
   */
  getServeStats: async (filters: ServeStatsRequest): Promise<ServeStatsResponse> => {
    const response = await apiClient.post<ServeStatsResponse>(endpoints.getServeStats, filters);
    return response.data;
  },

  /**
   * Get raw serve statistics data for frontend visualization
   */
  getRawServeStats: async (filters: ServeStatsRequest): Promise<RawServeStatsResponse> => {
    const response = await apiClient.post<RawServeStatsResponse>(endpoints.getRawServeStats, filters);
    return response.data;
  },

  /**
   * Get return statistics charts
   */
  getReturnStats: async (filters: ReturnStatsRequest): Promise<ReturnStatsResponse> => {
    const response = await apiClient.post<ReturnStatsResponse>(endpoints.getReturnStats, filters);
    return response.data;
  },

  /**
   * Get ranking timeline chart
   */
  getRankingStats: async (filters: RankingStatsRequest): Promise<RankingStatsResponse> => {
    const response = await apiClient.post<RankingStatsResponse>(endpoints.getRankingStats, filters);
    return response.data;
  },

  /**
   * Get filtered matches
   */
  getMatches: async (filters: StatsRequest): Promise<MatchesResponse> => {
    const response = await apiClient.post<MatchesResponse>(endpoints.getMatches, filters);
    return response.data;
  },
};

