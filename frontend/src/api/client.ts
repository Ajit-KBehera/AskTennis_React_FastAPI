import axios from 'axios';
import type {
  FilterOptionsResponse,

  StatsRequest,
  ServeStatsRequest,
  ReturnStatsRequest,
  RankingStatsRequest,
  ServeStatsResponse,
  ReturnStatsResponse,
  RankingStatsResponse,
  MatchesResponse,

} from '../types';

// Automatically detect API URL based on environment
// Priority: env variable > production backend > local development
const getApiBaseUrl = (): string => {
  // Check for explicit backend URL (set during build for production)
  const envApiUrl = import.meta.env.VITE_API_URL;
  if (envApiUrl) {
    return envApiUrl;
  }

  // For Cloud Run deployments, use HTTPS and backend service
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If running on Cloud Run (*.run.app domain)
    if (hostname.includes('.run.app')) {
      // Replace 'frontend' with 'backend' in the hostname
      const backendHost = hostname.replace('frontend', 'backend');
      return `https://${backendHost}/api`;
    }
    // If accessed from local network IP (not localhost)
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:8000/api`;
    }
  }
  // Default to localhost for development
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

const API_KEY = import.meta.env.VITE_API_KEY || 'dev-key';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

export const endpoints = {
  getFilters: '/filters',

  query: '/query',  // Full AI query with SQL and data
  getServeStats: '/stats/serve',
  getReturnStats: '/stats/return',
  getRankingStats: '/stats/ranking',
  getMatches: '/matches',
};

// Re-export types for convenience
export type {
  FilterOptionsResponse,

  StatsRequest,
  ServeStatsRequest,
  ReturnStatsResponse,
  RankingStatsResponse,
  MatchesResponse, // This re-export is for external consumption
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
   * Get serve statistics data for frontend visualization
   */
  getServeStats: async (filters: ServeStatsRequest): Promise<ServeStatsResponse> => {
    const response = await apiClient.post<ServeStatsResponse>(endpoints.getServeStats, filters);
    return response.data;
  },

  /**
   * Get return statistics data for frontend visualization
   */
  getReturnStats: async (filters: ReturnStatsRequest): Promise<ReturnStatsResponse> => {
    const response = await apiClient.post<ReturnStatsResponse>(endpoints.getReturnStats, filters);
    return response.data;
  },

  /**
   * Get ranking timeline data for frontend visualization
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

