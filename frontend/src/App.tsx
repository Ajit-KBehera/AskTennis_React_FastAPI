import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { Header } from './components/layout/Header';
import { SearchPanel } from './components/search/SearchPanel';
import { QuickInsights } from './components/search/QuickInsights';
import { AiResponseView } from './components/views/AiResponseView';
import { StatsDashboardView } from './components/views/StatsDashboardView';
import { apiClient, endpoints } from './api/client';
import { FilterState } from './types';

function App() {
    // Filter state
    const [filters, setFilters] = useState<FilterState>({
        player_name: 'All Players',
        opponent: 'All Opponents',
        tournament: 'All Tournaments',
        surface: [],
        year: 'All Years',
    });

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

    const handleFilterChange = (newFilters: FilterState) => {
        setFilters(newFilters);
        setSelectedPlayer(newFilters.player_name);

        if (!newFilters.player_name || newFilters.player_name === 'All Players') {
            setHasGeneratedAnalysis(false);
            return;
        }

        // Clear AI state when switching to analysis view
        setAiResponse('');
        setAiSqlQueries([]);
        setAiData([]);
        setAiError('');

        setHasGeneratedAnalysis(true);
    };

    const handleQuerySubmit = async (queryText: string) => {
        if (!queryText.trim()) return;

        // Switch to AI view
        setHasGeneratedAnalysis(false);
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

                {!aiLoading && !hasGeneratedAnalysis && !aiResponse && (
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
                    <AiResponseView
                        aiResponse={aiResponse}
                        aiSqlQueries={aiSqlQueries}
                        aiData={aiData}
                    />
                )}

                {hasGeneratedAnalysis && (
                    <StatsDashboardView filters={filters} selectedPlayer={selectedPlayer} />
                )}
            </div>
        </Layout>
    );
}

export default App;
