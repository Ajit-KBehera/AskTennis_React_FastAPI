import { useState, useCallback } from 'react';
import { apiClient, endpoints } from '../api/client';
import { AiQueryState, AiQueryResponse } from '../types';

const SESSION_ID_STORAGE_KEY = 'asktennis_session_id';

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

function getStoredSessionId(): string | null {
  try {
    if (typeof window === 'undefined') return null;
    return window.localStorage.getItem(SESSION_ID_STORAGE_KEY);
  } catch {
    return null;
  }
}

function setStoredSessionId(sessionId: string): void {
  try {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(SESSION_ID_STORAGE_KEY, sessionId);
  } catch {
    // ignore (e.g. storage disabled)
  }
}

function clearStoredSessionId(): void {
  try {
    if (typeof window === 'undefined') return;
    window.localStorage.removeItem(SESSION_ID_STORAGE_KEY);
  } catch {
    // ignore
  }
}

export function useAiQuery() {
  const [state, setState] = useState<AiQueryState>(initialState);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  const resetConversation = useCallback(() => {
    clearStoredSessionId();
    setState(initialState);
  }, []);

  const submitQuery = useCallback(async (queryText: string) => {
    if (!queryText.trim()) return;

    setState({ ...initialState, loading: true });

    try {
      const existingSessionId = getStoredSessionId();
      const response = await apiClient.post<AiQueryResponse>(endpoints.query, {
        query: queryText.trim(),
        session_id: existingSessionId || undefined,
      });

      if (response.data.session_id) {
        setStoredSessionId(response.data.session_id);
      }

      setState({
        response: response.data.answer || '',
        sqlQueries: response.data.sql_queries || [],
        data: response.data.data || [],
        conversationFlow: response.data.conversation_flow || [],
        sessionId: response.data.session_id || existingSessionId || undefined,
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

  return { ...state, submitQuery, reset, resetConversation };
}
