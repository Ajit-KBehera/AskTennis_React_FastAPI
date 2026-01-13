import React, { useState } from 'react';

interface RawDataViewProps {
  data: any[];
}

export const RawDataView: React.FC<RawDataViewProps> = ({ data }) => {
  const [expanded, setExpanded] = useState(false);

  if (data.length === 0) {
    return (
      <div className="h-40 flex items-center justify-center text-gray-400">
        No raw data available. Select filters and generate analysis.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-700">
          Raw Match Data ({data.length} records)
        </h3>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          {expanded ? 'Collapse' : 'Expand All'}
        </button>
      </div>

      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {data.map((item, idx) => (
          <details
            key={idx}
            className="bg-gray-50 rounded-lg p-4 border border-gray-200"
            open={expanded}
          >
            <summary className="cursor-pointer font-medium text-gray-700 mb-2">
              Match {idx + 1}: {item.tourney_name || 'Unknown'} - {item.event_year || 'N/A'}
            </summary>
            <pre className="mt-2 text-xs text-gray-600 overflow-x-auto">
              {JSON.stringify(item, null, 2)}
            </pre>
          </details>
        ))}
      </div>
    </div>
  );
};

