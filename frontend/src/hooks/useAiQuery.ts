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
      const axiosError = error as { response?: { data?: { detail?: string } } };
      const message =
        axiosError?.response?.data?.detail ||
        'Failed to get AI response. Please try again.';
      setState((prev) => ({ ...prev, loading: false, error: message }));
    }
  }, []);

  return { ...state, submitQuery, reset };
}
