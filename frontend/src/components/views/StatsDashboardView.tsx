import React from 'react';
import { TrendingUp } from 'lucide-react';
import { Tabs } from '../analysis/Tabs';
import { useAnalysisData } from '../../hooks/useAnalysisData';
import { FilterState } from '../../types';
import { TennisLoader } from '../ui/TennisLoader';

interface StatsDashboardViewProps {
    filters: FilterState;
    selectedPlayer: string;
}

export const StatsDashboardView: React.FC<StatsDashboardViewProps> = ({ filters, selectedPlayer }) => {
    const { matches, serveCharts, returnCharts, rankingChart, loading, error } = useAnalysisData(filters);

    if (loading) {
        return (
            <div className="glass-card rounded-xl p-12 flex justify-center items-center">
                <TennisLoader />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center shrink-0">
                        <span className="text-red-400 text-xl">❌</span>
                    </div>
                    <div>
                        <h3 className="font-bold text-red-400 mb-1">Error</h3>
                        <p className="text-red-300/80 text-sm">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="flex items-center gap-2 mb-6 text-emerald-400 font-bold uppercase tracking-wider text-sm">
                <TrendingUp className="w-4 h-4" />
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
    );
};
