import React from 'react';
import Plot from 'react-plotly.js';

interface PlotlyChartProps {
  data: any;
  title?: string;
}

export const StatsChart: React.FC<PlotlyChartProps> = ({ data, title }) => {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-400">No chart data available</p>
      </div>
    );
  }

  // If data has error, show error message
  if (data.error) {
    return (
      <div className="flex items-center justify-center h-64 bg-red-50 rounded-lg border border-red-200">
        <div className="text-center p-4">
          <p className="text-red-600 font-medium">{data.error}</p>
          {data.reasons && data.reasons.length > 0 && (
            <ul className="mt-2 text-sm text-red-500 list-disc list-inside">
              {data.reasons.map((reason: string, idx: number) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  }

  try {
    // Plotly chart data structure
    const plotData = data.data || [];
    const layout = {
      ...(data.layout || {}),
      title: title || data.layout?.title,
      autosize: true,
      responsive: true,
    };
    const config = {
      ...(data.config || {}),
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
    };

    return (
      <div className="w-full" style={{ minHeight: '450px' }}>
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          className="w-full"
          useResizeHandler={true}
          style={{ width: '100%', height: '100%', minHeight: '450px' }}
        />
      </div>
    );
  } catch (error) {
    return (
      <div className="flex items-center justify-center h-64 bg-yellow-50 rounded-lg border border-yellow-200">
        <p className="text-yellow-600">Failed to render chart</p>
      </div>
    );
  }
};
