import React, { useState } from 'react';
import axios from 'axios';
import { Search, Loader2, Trophy, Info, Lightbulb } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SqlCodeBlock from './components/SqlCodeBlock';
import Expander from './components/Expander';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResults(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-blue-50 via-slate-50 to-emerald-50 text-slate-900 selection:bg-emerald-100">
      <main className="max-w-4xl mx-auto px-6 py-16 md:py-24">
        {/* Header Section */}
        <header className="text-center mb-16 space-y-4 animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="inline-flex items-center justify-center p-3 bg-emerald-100 rounded-2xl mb-2">
            <Trophy className="w-8 h-8 text-emerald-600" />
          </div>
          <h1 className="text-5xl md:text-6xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-emerald-600">
            AskTennis AI
          </h1>
          <p className="text-lg md:text-xl text-slate-500 font-medium max-w-2xl mx-auto">
            Instant insights from historical tennis data using advanced AI reasoning.
          </p>
        </header>

        {/* Search Interface */}
        <div className="relative mb-16 animate-in fade-in fill-mode-both delay-150 duration-700">
          <div className="group relative flex items-center bg-white/70 backdrop-blur-xl border border-slate-200 rounded-2xl shadow-xl shadow-slate-200/50 focus-within:ring-2 focus-within:ring-emerald-500/20 focus-within:border-emerald-500/50 transition-all duration-300">
            <div className="pl-6 pointer-events-none text-slate-400">
              <Search className="w-5 h-5 group-focus-within:text-emerald-500 transition-colors" />
            </div>
            <input
              className="w-full py-5 px-6 bg-transparent text-lg focus:outline-none placeholder:text-slate-400"
              type="text"
              placeholder="Who has the most aces? Federer vs Nadal stats..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <div className="pr-3">
              <button
                className="bg-slate-900 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 active:scale-95 flex items-center gap-2 group shadow-lg shadow-slate-900/10"
                onClick={handleSearch}
                disabled={loading}
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Analyze</span>}
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {results ? (
          <div className="space-y-10 animate-in fade-in zoom-in-95 duration-500">
            {/* Answer Card */}
            <div className="bg-white/80 backdrop-blur-md border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-2 mb-6 text-emerald-600 font-bold uppercase tracking-wider text-sm">
                <Lightbulb className="w-4 h-4" />
                <span>AI Insight</span>
              </div>
              <div className="prose prose-slate max-w-none prose-headings:font-black prose-a:text-emerald-600 prose-strong:text-slate-900">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{results.answer}</ReactMarkdown>
              </div>
            </div>

            {/* Expander Sections */}
            {(results.sql_queries?.length > 0) && (
              <div className="space-y-4">
                <Expander label="Technical Reasoning (SQL)">
                  <div className="space-y-4 mt-4">
                    {results.sql_queries.map((sql, i) => (
                      <SqlCodeBlock key={i} code={sql} />
                    ))}
                  </div>
                </Expander>
              </div>
            )}
          </div>
        ) : (
          !loading && (
            <div className="grid md:grid-cols-1 gap-8 animate-in fade-in delay-300 duration-1000">
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
                      onClick={() => { setQuery(q); handleSearch(); }}
                      className="px-6 py-3 bg-white border border-slate-200 rounded-full text-sm font-medium text-slate-600 hover:border-emerald-500 hover:text-emerald-600 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300 flex items-center gap-2"
                    >
                      <Info className="w-4 h-4 opacity-50" />
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )
        )}
      </main>
    </div>
  );
}

export default App;

