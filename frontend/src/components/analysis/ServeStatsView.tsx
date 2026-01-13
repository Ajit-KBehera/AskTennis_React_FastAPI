import React, { useState, useEffect } from 'react';
// import { NivoTimeline } from '../Charts/NivoTimeline'; // Disabled for now
import { D3ServeTimeline } from '../charts/D3ServeTimeline';
import { D3AceDFTimeline } from '../charts/D3AceDFTimeline';
import { D3RadarChart } from '../charts/D3RadarChart';
import { api } from '../../api/client';
import type { ServeStatsRequest, RawServeStatsResponse, RawServeMatch } from '../../types';

interface ServeStatsViewProps {
  filters: ServeStatsRequest | null | undefined;
  useRawData?: boolean; // Toggle between raw data and Plotly charts
}

export const ServeStatsView: React.FC<ServeStatsViewProps> = ({
  filters,
  useRawData = true,
}) => {
  const [rawData, setRawData] = useState<RawServeStatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showOpponentComparison, setShowOpponentComparison] = useState(false);

  // Calculate opponent stats if a specific opponent is selected
  const calculateOpponentStats = (matches: RawServeMatch[]): { stats: any; name: string } | null => {
    if (!filters?.opponent || filters.opponent === 'All Opponents') {
      return null;
    }

    // Filter matches against the specific opponent
    const opponentMatches = matches.filter(m => m.opponent === filters.opponent);
    if (opponentMatches.length === 0) {
      return null;
    }

    // Calculate aggregated opponent stats
    const valid1stIn = opponentMatches.filter(m => m.opponent_1stIn !== null).map(m => m.opponent_1stIn!);
    const valid1stWon = opponentMatches.filter(m => m.opponent_1stWon !== null).map(m => m.opponent_1stWon!);
    const valid2ndWon = opponentMatches.filter(m => m.opponent_2ndWon !== null).map(m => m.opponent_2ndWon!);
    const validAceRate = opponentMatches.filter(m => m.opponent_ace_rate !== null).map(m => m.opponent_ace_rate!);
    const validDfRate = opponentMatches.filter(m => m.opponent_df_rate !== null).map(m => m.opponent_df_rate!);

    const stats = {
      '1st Serve %': valid1stIn.length > 0 ? valid1stIn.reduce((a, b) => a + b, 0) / valid1stIn.length : 0,
      '1st Serve Won %': valid1stWon.length > 0 ? valid1stWon.reduce((a, b) => a + b, 0) / valid1stWon.length : 0,
      '2nd Serve Won %': valid2ndWon.length > 0 ? valid2ndWon.reduce((a, b) => a + b, 0) / valid2ndWon.length : 0,
    };

    return { stats, name: filters.opponent };
  };

  useEffect(() => {
    if (!useRawData || !filters?.player_name || filters.player_name === 'All Players') {
      return;
    }

    const fetchRawData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Ensure all required fields are present
        const requestFilters: ServeStatsRequest = {
          player_name: filters.player_name,
          opponent: filters.opponent || 'All Opponents',
          tournament: filters.tournament || 'All Tournaments',
          surface: filters.surface || null,
          year: filters.year || 'All Years',
        };
        const data = await api.getRawServeStats(requestFilters);
        setRawData(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load serve statistics');
        setRawData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchRawData();
  }, [filters, useRawData]);

  if (!useRawData) {
    return null; // Fall back to Plotly charts
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm">
        <div className="text-lg text-gray-500 animate-pulse">Loading serve statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm border border-red-200">
        <div className="text-red-600 text-center">
          <p className="font-semibold mb-2">Error loading statistics</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!rawData || rawData.matches.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm border-2 border-dashed border-gray-300">
        <div className="text-gray-400">No serve statistics available for selected filters.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with toggle */}
      {/* <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">
          {rawData.player_name} - Serve Performance
        </h2>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showOpponentComparison}
            onChange={(e) => setShowOpponentComparison(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-600">Show opponent comparison</span>
        </label>
      </div>

      {/* Serve Timeline Chart (D3-based with rank-sized dots) */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-gray-700 font-semibold mb-4">Serve Performance Timeline</h3>
        <D3ServeTimeline
          data={rawData.matches}
          metrics={['player_1stIn', 'player_1stWon', 'player_2ndWon']}
          showOpponentComparison={showOpponentComparison}
          height={500}
        />
      </div>

      {/* Ace/DF Timeline Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-gray-700 font-semibold mb-4">Ace & Double Fault Timeline</h3>
        <D3AceDFTimeline
          data={rawData.matches}
          showOpponentComparison={showOpponentComparison}
          height={500}
        />
      </div>

      {/* Skill Radar Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-gray-700 font-semibold mb-4">Skill Radar</h3>
        <D3RadarChart
          data={rawData.matches}
          playerName={rawData.player_name}
          opponentStats={calculateOpponentStats(rawData.matches)?.stats || null}
          opponentName={calculateOpponentStats(rawData.matches)?.name}
          height={500}
        />
      </div>

      {/* Nivo Timeline - Disabled for now */}
      {/* <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-gray-700 font-semibold mb-4">Serve Timeline (Nivo)</h3>
        <NivoTimeline
          data={rawData.matches}
          showOpponentComparison={showOpponentComparison}
        />
      </div> */}

      {/* Stats Summary */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-gray-700 font-semibold mb-4">Summary Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {rawData.matches.length}
            </p>
            <p className="text-sm text-gray-600 mt-1">Matches</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">
              {rawData.matches.filter((m) => m.result === 'W').length}
            </p>
            <p className="text-sm text-gray-600 mt-1">Wins</p>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <p className="text-2xl font-bold text-orange-600">
              {(
                rawData.matches.reduce((sum, m) => sum + (m.player_1stIn || 0), 0) /
                rawData.matches.filter((m) => m.player_1stIn !== null).length
              ).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-600 mt-1">Avg 1st Serve %</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">
              {(
                rawData.matches.reduce((sum, m) => sum + (m.player_1stWon || 0), 0) /
                rawData.matches.filter((m) => m.player_1stWon !== null).length
              ).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-600 mt-1">Avg 1st Won %</p>
          </div>
        </div>
      </div>
    </div>
  );
};

