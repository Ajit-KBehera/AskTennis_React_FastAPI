import React from 'react';
import { Info, History, Shuffle } from 'lucide-react';

interface QuickInsightsProps {
    onInsightClick: (query: string) => void;
    recentQueries?: string[];
}

const INSIGHTS_BY_CATEGORY: { label: string; queries: string[] }[] = [
    {
        label: 'Head to head',
        queries: [
            'Federer vs Nadal head to head on clay',
            'Djokovic vs Nadal at Roland Garros',
            'Federer vs Djokovic at Wimbledon',
        ],
    },
    {
        label: 'Grand Slams',
        queries: [
            'Who won Wimbledon 2023?',
            'Most US Open titles in the Open Era',
            'French Open winners in the last 10 years',
        ],
    },
    {
        label: 'Rankings & records',
        queries: [
            'Top 10 players in 2024',
            'Who has the most aces in a single match?',
            'Longest winning streak in ATP history',
        ],
    },
];

const ALL_INSIGHTS = INSIGHTS_BY_CATEGORY.flatMap((c) => c.queries);

export const QuickInsights: React.FC<QuickInsightsProps> = ({ onInsightClick, recentQueries = [] }) => {
    const handleSurpriseMe = () => {
        const q = ALL_INSIGHTS[Math.floor(Math.random() * ALL_INSIGHTS.length)];
        onInsightClick(q);
    };

    const recentToShow = recentQueries.slice(0, 3).filter((q) => q.trim());

    return (
        <div className="grid md:grid-cols-1 gap-8 animate-in fade-in delay-300 duration-1000 mb-8">
            <p className="text-slate-400 text-center text-sm">
                Ask anything about 147 years of tennis—players, matches, rankings.
            </p>
            <div className="text-center space-y-6">
                {recentToShow.length > 0 && (
                    <div className="space-y-3">
                        <h3 className="text-slate-500 font-semibold uppercase tracking-widest text-xs flex items-center justify-center gap-2">
                            <History className="w-3.5 h-3.5" /> You recently asked
                        </h3>
                        <div className="flex flex-wrap justify-center gap-3">
                            {recentToShow.map((q) => (
                                <button
                                    key={q}
                                    type="button"
                                    onClick={() => onInsightClick(q)}
                                    className="min-h-[44px] px-5 py-3 bg-white/5 border border-white/10 rounded-full text-sm font-medium text-slate-300 hover:border-blue-500/50 hover:bg-blue-500/10 hover:text-blue-300 hover:shadow-lg transition-all duration-300 flex items-center gap-2 cursor-pointer hover:scale-105 active:scale-100"
                                >
                                    {q.length > 45 ? q.slice(0, 45) + '…' : q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
                <div className="space-y-3">
                    <h3 className="text-slate-500 font-semibold uppercase tracking-widest text-xs">Try an insight</h3>
                    <div className="flex flex-wrap justify-center gap-3">
                        {ALL_INSIGHTS.map((q) => (
                            <button
                                key={q}
                                type="button"
                                onClick={() => onInsightClick(q)}
                                className="min-h-[44px] px-5 py-3 bg-white/5 border border-white/5 rounded-full text-sm font-medium text-slate-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 hover:text-emerald-400 hover:shadow-lg hover:shadow-emerald-500/10 transition-all duration-300 flex items-center gap-2 cursor-pointer hover:scale-105 active:scale-100"
                            >
                                <Info className="w-4 h-4 opacity-50 shrink-0" />
                                {q}
                            </button>
                        ))}
                        <button
                            type="button"
                            onClick={handleSurpriseMe}
                            className="min-h-[44px] px-5 py-3 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-sm font-medium text-emerald-400 hover:bg-emerald-500/30 hover:border-emerald-500/50 transition-all duration-300 flex items-center gap-2 cursor-pointer hover:scale-105 active:scale-100"
                        >
                            <Shuffle className="w-4 h-4" /> Surprise me
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
