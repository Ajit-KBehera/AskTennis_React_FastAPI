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
  QueryHistoryResponse,
  AuthCredentials,
  AuthResponse,
  UserResponse,
} from '../types';

// Automatically detect API URL based on environment
// Priority: env variable > production backend > local development
const getBackendBaseUrl = (): string => {
  // Check for explicit backend URL (set during build for production)
  const envApiUrl = import.meta.env.VITE_API_URL;
  if (envApiUrl) {
    // If it ends with /api, strip it to get the base
    return envApiUrl.replace(/\/api\/?$/, '');
  }

  // For Cloud Run deployments, use HTTPS and backend service
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If running on Cloud Run (*.run.app domain)
    if (hostname.includes('.run.app')) {
      // Replace 'frontend' with 'backend' in the hostname
      const backendHost = hostname.replace('frontend', 'backend');
      return `https://${backendHost}`;
    }
    // If accessed from local network IP (not localhost)
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:8000`;
    }
  }
  // Default to localhost for development
  return 'http://localhost:8000';
};

const BACKEND_URL = getBackendBaseUrl();

export const apiClient = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Required for HttpOnly cookies
});

export const endpoints = {
  // Auth endpoints (prefix with /auth)
  login: '/auth/login',
  register: '/auth/register',
  logout: '/auth/logout',
  getMe: '/auth/me',
  checkUsername: '/auth/check-username',

  // API endpoints (prefix with /api)
  getFilters: '/api/filters',
  query: '/api/query',
  queryHistory: '/api/query/history',
  getServeStats: '/api/stats/serve',
  getReturnStats: '/api/stats/return',
  getRankingStats: '/api/stats/ranking',
  getMatches: '/api/matches',
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

  /**
   * Auth: Login
   */
  login: async (credentials: AuthCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(endpoints.login, credentials);
    return response.data;
  },

  /**
   * Auth: Register
   */
  register: async (credentials: AuthCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(endpoints.register, credentials);
    return response.data;
  },

  /**
   * Auth: Logout
   */
  logout: async (): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(endpoints.logout);
    return response.data;
  },

  /**
   * Auth: Get Current User
   */
  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>(endpoints.getMe);
    return response.data;
  },

  /**
   * Auth: Check if username is available (for registration)
   */
  checkUsername: async (username: string): Promise<{ available: boolean }> => {
    const response = await apiClient.get<{ available: boolean }>(
      endpoints.checkUsername,
      { params: { username } }
    );
    return response.data;
  },

  /**
   * Get current user's query history (saved AI queries/results)
   */
  getQueryHistory: async (limit = 10): Promise<QueryHistoryResponse> => {
    const response = await apiClient.get<QueryHistoryResponse>(
      endpoints.queryHistory,
      { params: { limit } }
    );
    return response.data;
  },
};

