import { useState, useEffect } from 'react';
import { endpoints, apiClient } from '../api/client';
import {
    ServeStatsRequest, MatchesResponse, ServeStatsResponse,
    ReturnStatsResponse, RankingStatsResponse, FilterState
} from '../types';

interface AnalysisData {
    matches: any[];
    serveCharts: any;
    returnCharts: any;
    rankingChart: any;
    loading: boolean;
    error: string | null;
}

export const useAnalysisData = (filters: FilterState): AnalysisData => {
    const [matches, setMatches] = useState<any[]>([]);
    const [serveCharts, setServeCharts] = useState<any>(null);
    const [returnCharts, setReturnCharts] = useState<any>(null);
    const [rankingChart, setRankingChart] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            // Only fetch if a player is selected (not 'All Players')
            if (!filters.player_name || filters.player_name === 'All Players') {
                setMatches([]);
                setServeCharts(null);
                setReturnCharts(null);
                setRankingChart(null);
                return;
            }

            setLoading(true);
            setError(null);

            try {
                // Prepare request payloads
                // Common logic for optional parameters
                const opponent = filters.opponent !== 'All Opponents' ? filters.opponent : undefined;
                const tournament = filters.tournament !== 'All Tournaments' ? filters.tournament : undefined;
                const surface = filters.surface && filters.surface.length > 0 ? filters.surface : undefined;
                const year = filters.year !== 'All Years' ? filters.year : undefined;

                const commonRequest = {
                    player_name: filters.player_name,
                    opponent,
                    tournament,
                    surface,
                    year
                };

                const rankingRequest = {
                    player_name: filters.player_name,
                    year // Ranking only needs year
                };

                // Parallel requests
                const [matchesRes, serveRes, returnRes, rankingRes] = await Promise.all([
                    apiClient.post<MatchesResponse>(endpoints.getMatches, commonRequest),
                    apiClient.post<ServeStatsResponse>(endpoints.getServeStats, commonRequest),
                    apiClient.post<ReturnStatsResponse>(endpoints.getReturnStats, commonRequest),
                    apiClient.post<RankingStatsResponse>(endpoints.getRankingStats, rankingRequest)
                ]);

                setMatches(matchesRes.data.matches || []);
                setServeCharts(serveRes.data);
                setReturnCharts(returnRes.data);
                setRankingChart(rankingRes.data);

            } catch (err: any) {
                console.error("Error fetching analysis data:", err);
                setError(err.message || 'Failed to fetch analysis data');
                // On error, clear charts but keep what we can? Or clear all?
                // App.tsx cleared all. Let's do same for consistency.
                setMatches([]);
                setServeCharts(null);
                setReturnCharts(null);
                setRankingChart(null);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [filters]); // Re-run whenever filters change

    return { matches, serveCharts, returnCharts, rankingChart, loading, error };
};
