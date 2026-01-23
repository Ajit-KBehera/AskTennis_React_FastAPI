import { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { Header } from './components/layout/Header';
import { SearchPanel } from './components/search/SearchPanel';
import { QuickInsights } from './components/search/QuickInsights';
import { AiResponseView } from './components/views/AiResponseView';
import { StatsDashboardView } from './components/views/StatsDashboardView';
import { FilterState } from './types';
import { TennisLoader } from './components/ui/TennisLoader';
import { useAiQuery } from './hooks/useAiQuery';

function App() {
    // Filter state
    const [filters, setFilters] = useState<FilterState>({
        player_name: 'All Players',
        opponent: 'All Opponents',
        tournament: 'All Tournaments',
        surface: [],
        year: 'All Years',
    });

    const [hasGeneratedAnalysis, setHasGeneratedAnalysis] = useState(false);
    const [query, setQuery] = useState('');

    // AI Query state via custom hook
    const ai = useAiQuery();

    const handleFilterChange = (newFilters: FilterState) => {
        setFilters(newFilters);

        if (!newFilters.player_name || newFilters.player_name === 'All Players') {
            setHasGeneratedAnalysis(false);
            return;
        }

        // Clear AI state when switching to analysis view
        ai.reset();
        setHasGeneratedAnalysis(true);
    };

    const handleQuerySubmit = async (queryText: string) => {
        if (!queryText.trim()) return;

        // Switch to AI view
        setHasGeneratedAnalysis(false);
        await ai.submitQuery(queryText);
    };

    const selectedPlayer = filters.player_name;

    return (
        <Layout onFilterChange={handleFilterChange}>
            <div className="space-y-8 animate-fade-in">
                <Header />

                <SearchPanel
                    onQuerySubmit={handleQuerySubmit}
                    disabled={ai.loading}
                    value={query}
                    onChange={setQuery}
                />

                {!ai.loading && !hasGeneratedAnalysis && !ai.response && (
                    <QuickInsights onInsightClick={(q) => { setQuery(q); handleQuerySubmit(q); }} />
                )}

                {ai.loading && (
                    <div className="glass-card rounded-2xl p-12 flex justify-center items-center my-8">
                        <TennisLoader />
                    </div>
                )}

                {ai.error && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 backdrop-blur-sm">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center shrink-0">
                                <span className="text-red-400 text-xl">❌</span>
                            </div>
                            <div>
                                <h3 className="font-bold text-red-400 mb-1 text-lg">Analysis Error</h3>
                                <p className="text-red-300/80">{ai.error}</p>
                            </div>
                        </div>
                    </div>
                )}

                {!hasGeneratedAnalysis && !ai.loading && ai.response && (
                    <AiResponseView
                        aiResponse={ai.response}
                        aiSqlQueries={ai.sqlQueries}
                        aiData={ai.data}
                        conversationFlow={ai.conversationFlow}
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
