import React, { useState } from 'react';
import { Layout } from './components/Layout/Layout';
import { SearchPanel } from './components/Search/SearchPanel';
import { Tabs } from './components/Dashboard/Tabs';
import { apiClient, endpoints } from './api/client';
import type { ServeStatsRequest, MatchesResponse, ServeStatsResponse, ReturnStatsResponse, RankingStatsResponse, ChatResponse } from './types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SqlCodeBlock from './components/SqlCodeBlock';
import Expander from './components/Expander';
import { DataTable } from './components/DataTable';
import { Lightbulb, TrendingUp, Info } from 'lucide-react';

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
        // Update filters state
        setFilters({
            player_name: newFilters.player_name,
            opponent: newFilters.opponent || 'All Opponents',
            tournament: newFilters.tournament || 'All Tournaments',
            surface: newFilters.surface || [],
            year: newFilters.year || 'All Years',
        });

        setSelectedPlayer(newFilters.player_name);

        // Don't fetch if "All Players" is selected
        if (!newFilters.player_name || newFilters.player_name === 'All Players') {
            setMatches([]);
            setServeCharts(null);
            setReturnCharts(null);
            setRankingChart(null);
            setHasGeneratedAnalysis(false);
            return;
        }

        // Clear AI response when filter analysis is generated (so analysis replaces AI response)
        setAiResponse('');
        setAiSqlQueries([]);
        setAiData([]);
        setAiError('');

        setLoading(true);
        setHasGeneratedAnalysis(true); // Mark that analysis has been generated

        try {
            // Fetch matches
            const matchesRequest = {
                player_name: newFilters.player_name,
                opponent: newFilters.opponent !== 'All Opponents' ? newFilters.opponent : undefined,
                tournament: newFilters.tournament !== 'All Tournaments' ? newFilters.tournament : undefined,
                surface: newFilters.surface && newFilters.surface.length > 0 ? newFilters.surface : undefined,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            };
            const matchesRes = await apiClient.post<MatchesResponse>(endpoints.getMatches, matchesRequest);
            setMatches(matchesRes.data.matches || []);

            // Fetch serve statistics
            const serveRes = await apiClient.post<ServeStatsResponse>(endpoints.getServeStats, {
                player_name: newFilters.player_name,
                opponent: newFilters.opponent !== 'All Opponents' ? newFilters.opponent : undefined,
                tournament: newFilters.tournament !== 'All Tournaments' ? newFilters.tournament : undefined,
                surface: newFilters.surface && newFilters.surface.length > 0 ? newFilters.surface : undefined,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            });
            setServeCharts(serveRes.data);

            // Fetch return statistics
            const returnRes = await apiClient.post<ReturnStatsResponse>(endpoints.getReturnStats, {
                player_name: newFilters.player_name,
                opponent: newFilters.opponent !== 'All Opponents' ? newFilters.opponent : undefined,
                tournament: newFilters.tournament !== 'All Tournaments' ? newFilters.tournament : undefined,
                surface: newFilters.surface && newFilters.surface.length > 0 ? newFilters.surface : undefined,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            });
            setReturnCharts(returnRes.data);

            // Fetch ranking statistics
            const rankingRes = await apiClient.post<RankingStatsResponse>(endpoints.getRankingStats, {
                player_name: newFilters.player_name,
                year: newFilters.year !== 'All Years' ? newFilters.year : undefined,
            });
            setRankingChart(rankingRes.data);

        } catch (error: any) {
            // Reset data on error
            setMatches([]);
            setServeCharts(null);
            setReturnCharts(null);
            setRankingChart(null);
        } finally {
            setLoading(false);
        }
    };

    // Handle AI query submission - using full /api/query endpoint for detailed response
    const handleQuerySubmit = async (query: string) => {
        if (!query.trim()) {
            return;
        }

        // Clear filter analysis when AI query is submitted (so AI response replaces it)
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
            // Use the full /api/query endpoint to get SQL queries and data
            const response = await apiClient.post(endpoints.query, {
                query: query.trim()
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

    // Handle clear action
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
            {/* Main content area */}
            <div className="space-y-6">
                {/* Header */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                            <span className="text-white text-2xl">🎾</span>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">AskTennis Analytics</h1>
                            <p className="text-sm text-gray-500">Advanced tennis statistics and AI-powered insights</p>
                        </div>
                    </div>
                </div>

                {/* Search Panel (for AI queries) */}
                <SearchPanel
                    onQuerySubmit={handleQuerySubmit}
                    onClear={handleClear}
                    disabled={aiLoading}
                    value={query}
                    onChange={setQuery}
                />

                {/* Quick Insights - Only show when no analysis is active */}
                {!loading && !aiLoading && !hasGeneratedAnalysis && !aiResponse && (
                    <div className="grid md:grid-cols-1 gap-8 animate-in fade-in delay-300 duration-1000 mb-8">
                        <div className="text-center space-y-6">
                            <h3 className="text-slate-400 font-semibold uppercase tracking-widest text-xs">Try an insight:</h3>
                            <div className="flex flex-wrap justify-center gap-3">
                                {[
                                    "Who has the most aces in a single match?",
                                    "Federer vs Nadal head to head on clay",
                                    "Top 10 players in 2023",
                                ].map((q) => (
                                    <button
                                        key={q}
                                        onClick={() => { setQuery(q); handleQuerySubmit(q); }}
                                        className="px-6 py-3 bg-white border border-slate-200 rounded-full text-sm font-medium text-slate-600 hover:border-emerald-500 hover:text-emerald-600 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300 flex items-center gap-2"
                                    >
                                        <Info className="w-4 h-4 opacity-50" />
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* AI Response Display with ReactMarkdown */}
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

                {/* Show AI Response OR Dashboard Tabs (not both) */}
                {!hasGeneratedAnalysis && !aiLoading && aiResponse && (
                    <div className="space-y-4 animate-in fade-in zoom-in-95 duration-500">
                        {/* Answer Card with ReactMarkdown */}
                        <div className="bg-white/80 backdrop-blur-md border border-gray-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex items-center gap-2 mb-6 text-emerald-600 font-bold uppercase tracking-wider text-sm">
                                <Lightbulb className="w-4 h-4" />
                                <span>AI Insight</span>
                            </div>
                            <div className="prose prose-slate max-w-none prose-headings:font-black prose-a:text-emerald-600 prose-strong:text-slate-900">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiResponse}</ReactMarkdown>
                            </div>
                        </div>

                        {/* SQL Queries Expander */}
                        {aiSqlQueries && aiSqlQueries.length > 0 && (
                            <Expander label="Technical Reasoning (SQL)">
                                <div className="space-y-4 mt-4">
                                    {aiSqlQueries.map((sql, i) => (
                                        <SqlCodeBlock key={i} code={sql} />
                                    ))}
                                </div>
                            </Expander>
                        )}

                        {/* Data Expander */}
                        {/* Data Table */}
                        {aiData && aiData.length > 0 && (
                            <Expander label={`Query Results (${aiData.length} rows)`}>
                                <div className="mt-4">
                                    <DataTable data={aiData} maxHeight={400} />
                                </div>
                            </Expander>
                        )}
                    </div>
                )}

                {/* Dashboard Tabs - Only show if analysis has been generated (replaces AI response) */}
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
