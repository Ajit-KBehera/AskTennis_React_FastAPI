import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { Header } from './components/layout/Header';
import { SearchPanel } from './components/search/SearchPanel';
import { QuickInsights } from './components/search/QuickInsights';
import { AiResponseSection } from './components/results/AiResponseSection';
import { Tabs } from './components/analysis/Tabs';
import { apiClient, endpoints } from './api/client';
import type { ServeStatsRequest, MatchesResponse, ServeStatsResponse, ReturnStatsResponse, RankingStatsResponse } from './types';
import { TrendingUp } from 'lucide-react';

function App() {
    // Filter state
    const [filters, setFilters] = useState<ServeStatsRequest>({
        player_name: 'All Players',
        opponent: 'All Opponents',
        tournament: 'All Tournaments',
        surface: [],
        year: 'All Years',
    });

    // Data state
    const [matches, setMatches] = useState<any[]>([]);
    const [serveCharts, setServeCharts] = useState<any>(null);
    const [returnCharts, setReturnCharts] = useState<any>(null);
    const [rankingChart, setRankingChart] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [selectedPlayer, setSelectedPlayer] = useState<string>('All Players');
    const [hasGeneratedAnalysis, setHasGeneratedAnalysis] = useState(false);

    // AI Query state
    const [aiResponse, setAiResponse] = useState<string>('');
    const [aiSqlQueries, setAiSqlQueries] = useState<string[]>([]);
    const [aiData, setAiData] = useState<any[]>([]);
    const [aiLoading, setAiLoading] = useState(false);
    const [aiError, setAiError] = useState<string>('');

    // Shared Query State
    const [query, setQuery] = useState('');

    // Handle filter changes from sidebar
    const handleFilterChange = async (newFilters: {
        player_name: string;
        opponent?: string;
        tournament?: string;
        surface?: string[];
        year?: string;
    }) => {
        setFilters({
            player_name: newFilters.player_name,
            opponent: newFilters.opponent || 'All Opponents',
            tournament: newFilters.tournament || 'All Tournaments',
            surface: newFilters.surface || [],
            year: newFilters.year || 'All Years',
        });

        setSelectedPlayer(newFilters.player_name);

        if (!newFilters.player_name || newFilters.player_name === 'All Players') {
            setMatches([]);
            setServeCharts(null);
            setReturnCharts(null);
            setRankingChart(null);
            setHasGeneratedAnalysis(false);
            return;
        }

        setAiResponse('');
        setAiSqlQueries([]);
        setAiData([]);
        setAiError('');

        setLoading(true);
        setHasGeneratedAnalysis(true);

        try {
            const matchesRequest = {
                player_name: newFilters.player_name,
                opponent: newFilters.opponent !== 'All Opponents' ? newFilters.opponent : undefined,
                tournament: newFilters.tournament !== 'All Tournaments' ? newFilters.tournament : undefined,
                surface: newFilters.surface && newFilters.surface.length > 0 ? newFilters.surface : undefined,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            };
            const matchesRes = await apiClient.post<MatchesResponse>(endpoints.getMatches, matchesRequest);
            setMatches(matchesRes.data.matches || []);

            const serveRes = await apiClient.post<ServeStatsResponse>(endpoints.getServeStats, {
                player_name: newFilters.player_name,
                opponent: newFilters.opponent !== 'All Opponents' ? newFilters.opponent : undefined,
                tournament: newFilters.tournament !== 'All Tournaments' ? newFilters.tournament : undefined,
                surface: newFilters.surface && newFilters.surface.length > 0 ? newFilters.surface : undefined,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            });
            setServeCharts(serveRes.data);

            const returnRes = await apiClient.post<ReturnStatsResponse>(endpoints.getReturnStats, {
                player_name: newFilters.player_name,
                opponent: newFilters.opponent !== 'All Opponents' ? newFilters.opponent : undefined,
                tournament: newFilters.tournament !== 'All Tournaments' ? newFilters.tournament : undefined,
                surface: newFilters.surface && newFilters.surface.length > 0 ? newFilters.surface : undefined,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            });
            setReturnCharts(returnRes.data);

            const rankingRes = await apiClient.post<RankingStatsResponse>(endpoints.getRankingStats, {
                player_name: newFilters.player_name,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            });
            setRankingChart(rankingRes.data);

        } catch (error: any) {
            setMatches([]);
            setServeCharts(null);
            setReturnCharts(null);
            setRankingChart(null);
        } finally {
            setLoading(false);
        }
    };

    const handleQuerySubmit = async (queryText: string) => {
        if (!queryText.trim()) return;

        setHasGeneratedAnalysis(false);
        setMatches([]);
        setServeCharts(null);
        setReturnCharts(null);
        setRankingChart(null);

        setAiLoading(true);
        setAiError('');
        setAiResponse('');
        setAiSqlQueries([]);
        setAiData([]);

        try {
            const response = await apiClient.post(endpoints.query, {
                query: queryText.trim()
            });

            setAiResponse(response.data.answer || '');
            setAiSqlQueries(response.data.sql_queries || []);
            setAiData(response.data.data || []);
        } catch (error: any) {
            setAiError(error.response?.data?.detail || 'Failed to get AI response. Please try again.');
        } finally {
            setAiLoading(false);
        }
    };

    const handleClear = () => {
        setMatches([]);
        setServeCharts(null);
        setReturnCharts(null);
        setRankingChart(null);
        setFilters({
            player_name: 'All Players',
            opponent: 'All Opponents',
            tournament: 'All Tournaments',
            surface: [],
            year: 'All Years',
        });
        setSelectedPlayer('All Players');
        setHasGeneratedAnalysis(false);
        setAiResponse('');
        setAiSqlQueries([]);
        setAiData([]);
        setAiError('');
        setQuery('');
    };

    return (
        <Layout onFilterChange={handleFilterChange}>
            <div className="space-y-6">
                <Header />

                <SearchPanel
                    onQuerySubmit={handleQuerySubmit}
                    disabled={aiLoading}
                    value={query}
                    onChange={setQuery}
                />

                {!loading && !aiLoading && !hasGeneratedAnalysis && !aiResponse && (
                    <QuickInsights onInsightClick={(q) => { setQuery(q); handleQuerySubmit(q); }} />
                )}

                {aiLoading && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <div className="flex items-center gap-3">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                            <p className="text-gray-600">Analyzing tennis data...</p>
                        </div>
                    </div>
                )}

                {aiError && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                        <div className="flex items-start gap-3">
                            <div className="text-red-600 text-2xl">❌</div>
                            <div>
                                <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                                <p className="text-red-800 text-sm">{aiError}</p>
                            </div>
                        </div>
                    </div>
                )}

                {!hasGeneratedAnalysis && !aiLoading && aiResponse && (
                    <AiResponseSection
                        aiResponse={aiResponse}
                        aiSqlQueries={aiSqlQueries}
                        aiData={aiData}
                    />
                )}

                {hasGeneratedAnalysis && (
                    <div>
                        <div className="flex items-center gap-2 mb-4 text-blue-600 font-semibold">
                            <TrendingUp className="w-5 h-5" />
                            <span>Statistical Analysis Dashboard</span>
                        </div>
                        <Tabs
                            serveCharts={serveCharts}
                            returnCharts={returnCharts}
                            rankingChart={rankingChart}
                            matches={matches}
                            loading={loading}
                            selectedPlayer={selectedPlayer}
                            filters={filters}
                        />
                    </div>
                )}
            </div>
        </Layout>
    );
}

export default App;
