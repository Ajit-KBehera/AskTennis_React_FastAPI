import React, { useState } from 'react';
import { StatsChart } from '../charts/StatsChart';
import { MatchesTable } from './MatchesTable';
import {
  createServeTimelineChart,
  createAceDfChart,
  createRadarChart,
  createReturnPointsChart,
  createBpConversionChart,
  createRankingChart
} from '../../utils/chartGenerators';

import type { ServeStatsRequest } from '../../types';

interface TabsProps {
  serveCharts?: any;
  returnCharts?: any;
  rankingChart?: any;
  matches?: any[];
  loading?: boolean;
  selectedPlayer?: string;
  filters?: ServeStatsRequest;
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

  // Helper to get serve chart data (either from backend or generated on frontend)
  const getServeChartData = (type: 'timeline' | 'acedf' | 'radar' | 'bp') => {
    if (!serveCharts) return null;

    // Prefer raw data generation if available
    if (serveCharts.matches && serveCharts.matches.length > 0) {
      const playerName = selectedPlayer || 'Player';
      switch (type) {
        case 'timeline':
          return createServeTimelineChart(serveCharts.matches, playerName);
        case 'acedf':
          return createAceDfChart(serveCharts.matches, playerName);
        case 'radar':
          if (serveCharts.aggregated_stats) {
            return createRadarChart(
              serveCharts.aggregated_stats,
              serveCharts.aggregated_opponent_stats,
              playerName
            );
          }
          break;
        case 'bp':
          if (serveCharts.bp_chart) return serveCharts.bp_chart;
          break;
      }
    }

    // Fallback to legacy backend charts
    switch (type) {
      case 'timeline': return serveCharts.timeline_chart;
      case 'acedf': return serveCharts.ace_df_chart;
      case 'radar': return serveCharts.radar_chart;
      case 'bp': return serveCharts.bp_chart;
    }
    return null;
  };

  const getReturnChartData = (type: 'return_points' | 'bp_conversion' | 'radar') => {
    if (!returnCharts) return null;

    // Prefer raw data generation if available
    if (returnCharts.matches && returnCharts.matches.length > 0) {
      const playerName = selectedPlayer || 'Player';
      switch (type) {
        case 'return_points':
          return createReturnPointsChart(returnCharts.matches, playerName);
        case 'bp_conversion':
          return createBpConversionChart(returnCharts.matches, playerName);
        case 'radar':
          if (returnCharts.aggregated_stats) {
            return createRadarChart(
              returnCharts.aggregated_stats,
              returnCharts.aggregated_opponent_stats,
              playerName
            );
          }
          break;
      }
    }

    switch (type) {
      case 'return_points': return returnCharts.return_points_chart;
      case 'bp_conversion': return returnCharts.bp_conversion_chart;
      case 'radar': return returnCharts.radar_chart;
    }
    return null;
  };

  const getRankingChartData = () => {
    if (!rankingChart) return null;

    if (rankingChart.ranking_data && rankingChart.ranking_data.length > 0) {
      return createRankingChart(rankingChart.ranking_data, selectedPlayer || 'Player');
    }

    return rankingChart.ranking_chart;
  }

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
            {serveCharts ? (
              <div className="flex flex-col w-full max-w-full">
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={getServeChartData('timeline')} title="Serve Timeline" />
                </div>
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={getServeChartData('radar')} title="Skill Radar" />
                </div>
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={getServeChartData('acedf')} title="Ace vs DF Rate" />
                </div>
                <div className="w-full max-w-full">
                  <StatsChart data={getServeChartData('bp')} title="Break Points Saved" />
                </div>
              </div>
            ) : (
              // Only show empty state if truly no stats
              !loading && (
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
              )
            )}
          </>
        )}

        {!loading && activeTab === 'return' && (
          <>
            {returnCharts ? (
              <div className="flex flex-col w-full max-w-full">
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={getReturnChartData('return_points')} title="Return Points Won % Timeline" />
                </div>
                <div className="mb-6 w-full max-w-full">
                  <StatsChart data={getReturnChartData('bp_conversion')} title="Break Point Conversion Timeline" />
                </div>
                <div className="w-full max-w-full">
                  <StatsChart data={getReturnChartData('radar')} title="Return Statistics Radar" />
                </div>
              </div>
            ) : (
              !loading && (
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
              )
            )}
          </>
        )}

        {!loading && activeTab === 'ranking' && (
          <>
            {(rankingChart && (rankingChart.ranking_chart || rankingChart.ranking_data)) ? (
              <div className="w-full max-w-full">
                <StatsChart data={getRankingChartData()} title="Ranking Timeline" />
              </div>
            ) : (
              !loading && (
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
              )
            )}
          </>
        )}

      </div>
    </div>
  );
};
