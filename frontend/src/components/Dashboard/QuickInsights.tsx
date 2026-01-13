import React from 'react';
import { Info } from 'lucide-react';

interface QuickInsightsProps {
    onInsightClick: (query: string) => void;
}

const INSIGHTS = [
    "Who has the most aces in a single match?",
    "Federer vs Nadal head to head on clay",
    "Top 10 players in 2023",
];

export const QuickInsights: React.FC<QuickInsightsProps> = ({ onInsightClick }) => {
    return (
        <div className="grid md:grid-cols-1 gap-8 animate-in fade-in delay-300 duration-1000 mb-8">
            <div className="text-center space-y-6">
                <h3 className="text-slate-400 font-semibold uppercase tracking-widest text-xs">Try an insight:</h3>
                <div className="flex flex-wrap justify-center gap-3">
                    {INSIGHTS.map((q) => (
                        <button
                            key={q}
                            onClick={() => onInsightClick(q)}
                            className="px-6 py-3 bg-white border border-slate-200 rounded-full text-sm font-medium text-slate-600 hover:border-emerald-500 hover:text-emerald-600 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300 flex items-center gap-2"
                        >
                            <Info className="w-4 h-4 opacity-50" />
                            {q}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};
