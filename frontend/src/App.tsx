import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { Header } from './components/layout/Header';
import { SearchPanel } from './components/search/SearchPanel';
import { QuickInsights } from './components/search/QuickInsights';
import { AiResponseView } from './components/views/AiResponseView';
import { StatsDashboardView } from './components/views/StatsDashboardView';
import { apiClient, endpoints } from './api/client';
import { FilterState } from './types';
import { TennisLoader } from './components/ui/TennisLoader';

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
    const [aiConversationFlow, setAiConversationFlow] = useState<any[]>([]);
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
        setAiSqlQueries([]);
        setAiData([]);
        setAiConversationFlow([]);
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
        setAiSqlQueries([]);
        setAiData([]);
        setAiConversationFlow([]);

        try {
            const response = await apiClient.post(endpoints.query, {
                query: queryText.trim()
            });

            setAiResponse(response.data.answer || '');
            setAiSqlQueries(response.data.sql_queries || []);
            setAiSqlQueries(response.data.sql_queries || []);
            setAiData(response.data.data || []);
            setAiConversationFlow(response.data.conversation_flow || []);
        } catch (error: any) {
            setAiError(error.response?.data?.detail || 'Failed to get AI response. Please try again.');
        } finally {
            setAiLoading(false);
        }
    };

    return (
        <Layout onFilterChange={handleFilterChange}>
            <div className="space-y-8 animate-fade-in">
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
                    <div className="glass-card rounded-2xl p-12 flex justify-center items-center my-8">
                        <TennisLoader />
                    </div>
                )}

                {aiError && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 backdrop-blur-sm">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center shrink-0">
                                <span className="text-red-400 text-xl">❌</span>
                            </div>
                            <div>
                                <h3 className="font-bold text-red-400 mb-1 text-lg">Analysis Error</h3>
                                <p className="text-red-300/80">{aiError}</p>
                            </div>
                        </div>
                    </div>
                )}

                {!hasGeneratedAnalysis && !aiLoading && aiResponse && (
                    <AiResponseView
                        aiResponse={aiResponse}
                        aiSqlQueries={aiSqlQueries}
                        aiData={aiData}
                        conversationFlow={aiConversationFlow}
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
