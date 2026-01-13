import React from 'react';
import { StatsChart } from '../Charts/StatsChart'; // The one we built in the previous step

interface StatsViewProps {
  charts: any; // Data from API
  loading: boolean;
}

export const StatsView: React.FC<StatsViewProps> = ({ charts, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm">
        <div className="text-lg text-gray-500 animate-pulse">Generating Analysis...</div>
      </div>
    );
  }

  if (!charts) {
    return (
      <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm border-2 border-dashed border-gray-300">
        <div className="text-gray-400">Select filters and click "Generate" to see stats.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Serve Performance</h2>
      
      {/* Grid Layout for Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <StatsChart chartData={charts.timeline_chart} title="Timeline Analysis" />
        <StatsChart chartData={charts.radar_chart} title="Skill Radar" />
        <StatsChart chartData={charts.ace_df_chart} title="Aces vs Double Faults" />
        <StatsChart chartData={charts.bp_chart} title="Break Points Saved" />
      </div>
    </div>
  );
};

