import React from 'react';
import { TrendingUp, Loader2 } from 'lucide-react';
import { Tabs } from '../analysis/Tabs';
import { useAnalysisData } from '../../hooks/useAnalysisData';
import { FilterState } from '../../types';

interface StatsDashboardViewProps {
    filters: FilterState;
    selectedPlayer: string;
}

export const StatsDashboardView: React.FC<StatsDashboardViewProps> = ({ filters, selectedPlayer }) => {
    const { matches, serveCharts, returnCharts, rankingChart, loading, error } = useAnalysisData(filters);

    if (loading) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 flex justify-center items-center">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
                    <p className="text-gray-500 font-medium">Fetching match data and calculating statistics...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                <div className="flex items-start gap-3">
                    <div className="text-red-600 text-2xl">❌</div>
                    <div>
                        <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                        <p className="text-red-800 text-sm">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
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
    );
};
