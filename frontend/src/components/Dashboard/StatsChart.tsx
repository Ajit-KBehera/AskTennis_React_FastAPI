import React from 'react';
import Plot from 'react-plotly.js';
import type { PlotlyChartData } from '../../types';

interface StatsChartProps {
  data: PlotlyChartData | null | undefined;
  title: string;
}

export const StatsChart: React.FC<StatsChartProps> = ({ data, title }) => {
  if (!data || !data.data || !data.layout) {
    return null;
  }

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 w-full max-w-full overflow-hidden">
      <h3 className="text-gray-700 font-semibold mb-4 ml-2">{title}</h3>
      <div className="w-full h-[400px] max-w-full overflow-hidden">
        <Plot
          data={data.data}
          layout={{
            ...data.layout,
            autosize: true,
            width: undefined,
            height: 400,
            margin: { l: 50, r: 30, t: 30, b: 50 },
            showlegend: true,
            legend: { orientation: 'h', y: -0.15, x: 0.5, xanchor: 'center' }
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%', maxWidth: '100%' }}
          config={{ 
            displayModeBar: false,
            responsive: true
          }}
        />
      </div>
    </div>
  );
};

