import React from 'react';
import Plot from 'react-plotly.js';

interface PlotlyChartProps {
  data: any;
  title?: string;
}

export const StatsChart: React.FC<PlotlyChartProps> = ({ data, title }) => {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-64 border border-white/5 rounded-xl bg-slate-900/30">
        <p className="text-slate-500">No chart data available</p>
      </div>
    );
  }

  // If data has error, show error message
  if (data.error) {
    return (
      <div className="flex items-center justify-center h-64 bg-red-500/10 rounded-xl border border-red-500/20">
        <div className="text-center p-4">
          <p className="text-red-400 font-medium">{data.error}</p>
          {data.reasons && data.reasons.length > 0 && (
            <ul className="mt-2 text-sm text-red-300/80 list-disc list-inside">
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

    // Merge layout with dark mode overrides
    const layout = {
      ...(data.layout || {}),
      title: {
        text: title || data.layout?.title?.text || data.layout?.title,
        font: { color: '#e2e8f0', size: 18 }
      },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#94a3b8' }, // Slate-400
      xaxis: {
        ...(data.layout?.xaxis || {}),
        gridcolor: 'rgba(255,255,255,0.1)',
        zerolinecolor: 'rgba(255,255,255,0.1)',
        tickfont: { color: '#94a3b8' }
      },
      yaxis: {
        ...(data.layout?.yaxis || {}),
        gridcolor: 'rgba(255,255,255,0.1)',
        zerolinecolor: 'rgba(255,255,255,0.1)',
        tickfont: { color: '#94a3b8' }
      },
      legend: {
        ...(data.layout?.legend || {}),
        font: { color: '#e2e8f0' },
        bgcolor: 'rgba(0,0,0,0)'
      },
      autosize: true,
      responsive: true,
      margin: data.layout?.margin || { l: 40, r: 20, t: 40, b: 40 }
    };

    const config = {
      ...(data.config || {}),
      responsive: true,
      displayModeBar: false, // Hide the bar for cleaner look
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
      <div className="flex items-center justify-center h-64 bg-red-500/10 rounded-xl border border-red-500/20">
        <p className="text-red-400">Failed to render chart</p>
      </div>
    );
  }
};
