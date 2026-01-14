import React, { useState } from 'react';
import { StatsChart } from '../charts/StatsChart';
import { MatchesTable } from './MatchesTable';

import type { ServeStatsRequest } from '../../types';

interface TabsProps {
  serveCharts?: any;
  returnCharts?: any;
  rankingChart?: any;
  matches?: any[];
  loading?: boolean;
  selectedPlayer?: string;
  filters?: ServeStatsRequest; // Add filters prop
}

export const Tabs: React.FC<TabsProps> = ({
  serveCharts,
  returnCharts,
  rankingChart,
  matches,
  loading,
  selectedPlayer,
  filters
}) => {
  const [activeTab, setActiveTab] = useState<'matches' | 'serve' | 'return' | 'ranking'>('matches');


  const tabs = [
    { id: 'matches' as const, label: '📊 Matches', icon: '📊' },
    { id: 'serve' as const, label: '🎾 Serve', icon: '🎾' },
    { id: 'return' as const, label: '🏓 Return', icon: '🏓' },
    { id: 'ranking' as const, label: '📈 Ranking', icon: '📈' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Tab Headers */}
      <div className="p-6 pb-0">
        <div className="flex gap-2 mb-6">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              type="button"
              className={`px-6 py-3 rounded-lg font-semibold transition-all border cursor-pointer ${activeTab === tab.id
                ? 'bg-blue-600 text-white shadow-lg border-blue-700 hover:bg-blue-700'
                : 'bg-white text-gray-700 hover:bg-blue-50 border-gray-200 hover:border-blue-200'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="px-6 pb-6 overflow-x-auto">
        {loading && (
          <div className="h-64 flex items-center justify-center">
            <div className="text-gray-500 animate-pulse">Loading...</div>
          </div>
        )}

        {!loading && activeTab === 'matches' && (
          <MatchesTable matches={matches || []} />
        )}

        {!loading && activeTab === 'serve' && (
          <>
            {/* New Recharts visualization */}
            {serveCharts ? (
              <div className="flex flex-col w-full max-w-full">
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={serveCharts.timeline_chart} title="Serve Timeline" />
                </div>
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={serveCharts.radar_chart} title="Skill Radar" />
                </div>
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={serveCharts.ace_df_chart} title="Ace vs DF Rate" />
                </div>
                <div className="w-full max-w-full">
                  <StatsChart data={serveCharts.bp_chart} title="Break Points Saved" />
                </div>
              </div>
            ) : null}
          </>
        )}

        {!loading && activeTab === 'serve' && !serveCharts && (
          <div className="h-40 flex items-center justify-center">
            {(!selectedPlayer || selectedPlayer === 'All Players') ? (
              <div className="text-center">
                <p className="text-blue-600 font-medium">ℹ️ Please select a player to view serve statistics.</p>
              </div>
            ) : (
              <div className="text-gray-400">
                No serve statistics available. Select filters and generate analysis.
              </div>
            )}
          </div>
        )}

        {!loading && activeTab === 'return' && returnCharts && (
          <div className="flex flex-col w-full max-w-full">
            <div className="mb-6 w-full max-w-full">
              <StatsChart data={returnCharts.return_points_chart} title="Return Points Won % Timeline" />
            </div>
            <div className="mb-6 w-full max-w-full">
              <StatsChart data={returnCharts.bp_conversion_chart} title="Break Point Conversion Timeline" />
            </div>
            <div className="w-full max-w-full">
              <StatsChart data={returnCharts.radar_chart} title="Return Statistics Radar" />
            </div>
          </div>
        )}

        {!loading && activeTab === 'return' && !returnCharts && (
          <div className="h-40 flex items-center justify-center">
            {(!selectedPlayer || selectedPlayer === 'All Players') ? (
              <div className="text-center">
                <p className="text-blue-600 font-medium">ℹ️ Please select a player to view return statistics.</p>
              </div>
            ) : (
              <div className="text-gray-400">
                No return statistics available. Select filters and generate analysis.
              </div>
            )}
          </div>
        )}

        {!loading && activeTab === 'ranking' && rankingChart && rankingChart.ranking_chart && !rankingChart.error && (
          <div className="w-full max-w-full">
            <StatsChart data={rankingChart.ranking_chart} title="Ranking Timeline" />
          </div>
        )}

        {!loading && activeTab === 'ranking' && (!rankingChart || rankingChart.error || !rankingChart.ranking_chart) && (
          <div className="h-40 flex items-center justify-center">
            <div className="text-center max-w-2xl px-4">
              <p className="text-blue-600 font-medium mb-2">
                {rankingChart?.error || "Ranking timeline chart not available."}
              </p>
              {rankingChart?.reasons && Array.isArray(rankingChart.reasons) && rankingChart.reasons.length > 0 && (
                <div className="mt-3 text-sm text-gray-600">
                  <p className="font-semibold mb-1">Requirements:</p>
                  <ul className="list-disc list-inside space-y-1 text-left inline-block">
                    {rankingChart.reasons.map((reason: string, index: number) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

