import { useState, useCallback } from 'react';
import { apiClient, endpoints } from '../api/client';
import { AiQueryState, AiQueryResponse } from '../types';

const initialState: AiQueryState = {
  response: '',
  sqlQueries: [],
  data: [],
  conversationFlow: [],
  loading: false,
  error: '',
};

function parseRetryAfter(value: string | undefined): number | undefined {
  if (value == null) return undefined;
  const n = parseInt(value, 10);
  return Number.isNaN(n) ? undefined : Math.max(0, n);
}

export function useAiQuery() {
  const [state, setState] = useState<AiQueryState>(initialState);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  const submitQuery = useCallback(async (queryText: string) => {
    if (!queryText.trim()) return;

    setState({ ...initialState, loading: true });

    try {
      const response = await apiClient.post<AiQueryResponse>(endpoints.query, {
        query: queryText.trim(),
      });

      setState({
        response: response.data.answer || '',
        sqlQueries: response.data.sql_queries || [],
        data: response.data.data || [],
        conversationFlow: response.data.conversation_flow || [],
        loading: false,
        error: '',
      });
    } catch (error: unknown) {
      const axiosError = error as {
        response?: {
          status?: number;
          data?: { detail?: string };
          headers?: { 'retry-after'?: string };
        };
      };
      const status = axiosError?.response?.status;
      const message =
        axiosError?.response?.data?.detail ||
        'Failed to get AI response. Please try again.';
      const retryAfterHeader = axiosError?.response?.headers?.['retry-after'];
      const retryAfterSeconds =
        status === 429 ? parseRetryAfter(retryAfterHeader) ?? 60 : undefined;
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
        retryAfterSeconds,
      }));
    }
  }, []);

  return { ...state, submitQuery, reset };
}
