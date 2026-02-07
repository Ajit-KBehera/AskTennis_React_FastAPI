import { useState, useRef, useEffect } from 'react';
import { Layout } from './components/layout/Layout';
import { Header } from './components/layout/Header';
import { SearchPanel, type SearchPanelRef } from './components/search/SearchPanel';
import { QuickInsights } from './components/search/QuickInsights';
import { AiResponseView } from './components/views/AiResponseView';
import { StatsDashboardView } from './components/views/StatsDashboardView';
import { FilterState } from './types';
import { TennisLoader } from './components/ui/TennisLoader';
import { useAiQuery } from './hooks/useAiQuery';
import { api } from './api/client';
import { useAuth } from './store/AuthContext';
import Login from './components/Login';
import { MessageCircle, BarChart3, RefreshCw, Edit3, Users } from 'lucide-react';

function App() {
    const { user, isLoading, logout } = useAuth();
    const searchRef = useRef<SearchPanelRef>(null);
    const answerHeadingRef = useRef<HTMLDivElement>(null);

    const [filters, setFilters] = useState<FilterState>({
        player_name: 'All Players',
        opponent: 'All Opponents',
        tournament: 'All Tournaments',
        surface: [],
        year: 'All Years',
    });

    const [mode, setMode] = useState<'ask' | 'stats'>('ask');
    const [queryHistory, setQueryHistory] = useState<string[]>([]);
    const [query, setQuery] = useState('');
    const [lastSubmittedQuery, setLastSubmittedQuery] = useState('');

    const ai = useAiQuery();

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const res = await api.getQueryHistory(10);
                const texts = (res.history || []).map((h) => h.query_text).filter(Boolean);
                setQueryHistory(texts);
            } catch {
                setQueryHistory([]);
            }
        };
        if (user) loadHistory();
    }, [user, ai.response]);

    useEffect(() => {
        const onKeyDown = (e: KeyboardEvent) => {
            if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
                e.preventDefault();
                searchRef.current?.focus();
            }
        };
        document.addEventListener('keydown', onKeyDown);
        return () => document.removeEventListener('keydown', onKeyDown);
    }, []);

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
                <TennisLoader />
            </div>
        );
    }

    if (!user) {
        return (
            <div className="min-h-screen bg-[#0f172a] flex items-center justify-center p-4">
                <Login />
            </div>
        );
    }

    const handleFilterChange = (newFilters: FilterState) => {
        setFilters(newFilters);
        if (!newFilters.player_name || newFilters.player_name === 'All Players') {
            setMode('ask');
            return;
        }
        ai.reset();
        setMode('stats');
    };

    const handleQuerySubmit = async (queryText: string) => {
        if (!queryText.trim()) return;
        setLastSubmittedQuery(queryText.trim());
        setMode('ask');
        await ai.submitQuery(queryText.trim());
        if (!ai.error) {
            answerHeadingRef.current?.focus();
        }
    };

    const handleInsightClick = (q: string) => {
        setQuery(q);
        handleQuerySubmit(q);
    };

    const selectedPlayer = filters.player_name;
    const showStatsEmpty = mode === 'stats' && (!selectedPlayer || selectedPlayer === 'All Players');

    return (
        <Layout onFilterChange={handleFilterChange}>
            <div className="space-y-8 animate-fade-in">
                <Header
                    user={user}
                    onLogout={logout}
                    mode={mode}
                    selectedPlayer={selectedPlayer}
                />

                <nav className="flex gap-2 border-b border-white/10 pb-4" aria-label="Main navigation">
                    <button
                        type="button"
                        onClick={() => setMode('ask')}
                        className={`flex items-center gap-2 px-5 py-3 rounded-xl font-medium transition-all min-h-[44px] ${
                            mode === 'ask'
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : 'bg-white/5 text-slate-400 border border-white/10 hover:text-white hover:bg-white/10'
                        }`}
                        aria-current={mode === 'ask' ? 'page' : undefined}
                    >
                        <MessageCircle className="w-5 h-5" /> Ask AI
                    </button>
                    <button
                        type="button"
                        onClick={() => setMode('stats')}
                        className={`flex items-center gap-2 px-5 py-3 rounded-xl font-medium transition-all min-h-[44px] ${
                            mode === 'stats'
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : 'bg-white/5 text-slate-400 border border-white/10 hover:text-white hover:bg-white/10'
                        }`}
                        aria-current={mode === 'stats' ? 'page' : undefined}
                    >
                        <BarChart3 className="w-5 h-5" /> Stats
                    </button>
                </nav>

                <SearchPanel
                    ref={searchRef}
                    onQuerySubmit={handleQuerySubmit}
                    disabled={ai.loading}
                    value={query}
                    onChange={setQuery}
                />

                {mode === 'ask' && !ai.loading && !ai.response && !ai.error && (
                    <QuickInsights
                        onInsightClick={handleInsightClick}
                        recentQueries={queryHistory}
                    />
                )}

                {ai.loading && (
                    <div className="space-y-6 my-8">
                        <div className="glass-card rounded-2xl p-12 flex flex-col justify-center items-center gap-4">
                            <TennisLoader />
                            <p className="text-slate-400 text-sm">Analyzing tennis data…</p>
                        </div>
                        <div className="glass-panel rounded-3xl p-8 space-y-4" aria-hidden>
                            <div className="skeleton-line w-3/4 max-w-md" />
                            <div className="skeleton-line w-full max-w-2xl" />
                            <div className="skeleton-line w-5/6 max-w-xl" />
                        </div>
                    </div>
                )}

                {ai.error && (
                    <div
                        className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 backdrop-blur-sm"
                        role="alert"
                        aria-live="assertive"
                    >
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center shrink-0">
                                <span className="text-red-400 text-xl" aria-hidden>❌</span>
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-bold text-red-400 mb-1 text-lg">Analysis Error</h3>
                                <p className="text-red-300/80 mb-4">{ai.error}</p>
                                <div className="flex flex-wrap gap-3">
                                    <button
                                        type="button"
                                        onClick={() => { ai.reset(); handleQuerySubmit(lastSubmittedQuery); }}
                                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 border border-red-500/30 text-red-300 hover:bg-red-500/30 transition-colors"
                                    >
                                        <RefreshCw className="w-4 h-4" /> Retry
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            ai.reset();
                                            setQuery(lastSubmittedQuery);
                                            searchRef.current?.focus();
                                        }}
                                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-slate-300 hover:bg-white/20 transition-colors"
                                    >
                                        <Edit3 className="w-4 h-4" /> Edit question
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {mode === 'ask' && !ai.loading && ai.response && (
                    <div ref={answerHeadingRef} tabIndex={-1}>
                        <AiResponseView
                            aiResponse={ai.response}
                            aiSqlQueries={ai.sqlQueries}
                            aiData={ai.data}
                            conversationFlow={ai.conversationFlow}
                        />
                    </div>
                )}

                {showStatsEmpty && (
                    <div className="glass-card rounded-2xl p-12 flex flex-col items-center justify-center text-center my-8 gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                            <Users className="w-8 h-8 text-slate-400" />
                        </div>
                        <p className="text-slate-400 font-medium">Select a player in the sidebar to see their stats and matches.</p>
                    </div>
                )}

                {mode === 'stats' && !showStatsEmpty && (
                    <StatsDashboardView filters={filters} selectedPlayer={selectedPlayer} />
                )}
            </div>
        </Layout>
    );
}

export default App;
