import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Tabs } from '../Dashboard/Tabs';
import { Bot, Info, AlertCircle } from 'lucide-react';
import type { Match, ServeStatsRequest } from '../../api/client';

interface AIResult {
  summary?: string;
  response: string;
}

interface ResultsPanelProps {
  showAIResults: boolean;
  aiResult: AIResult | null;
  analysisGenerated: boolean;
  serveCharts?: any;
  returnCharts?: any;
  rankingChart?: any;
  matches?: Match[];
  loading?: boolean;
  selectedPlayer?: string;
  filters?: ServeStatsRequest | null;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({
  showAIResults,
  aiResult,
  analysisGenerated,
  serveCharts,
  returnCharts,
  rankingChart,
  matches,
  loading,
  selectedPlayer,
  filters
}) => {
  // Show AI results if active
  if (showAIResults && aiResult) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Bot className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-800">AI Query Results</h2>
        </div>

        {aiResult.summary && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-2">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-800 mb-1">Summary</h3>
                <p className="text-sm text-blue-700">{aiResult.summary}</p>
              </div>
            </div>
          </div>
        )}

        <div className="prose prose-sm max-w-none">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-3 last:mb-0 text-gray-700">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1 text-gray-700">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-700">{children}</ol>,
              li: ({ children }) => <li className="ml-2">{children}</li>,
              strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
              code: ({ children }) => (
                <code className="bg-gray-200 px-2 py-1 rounded text-xs font-mono text-gray-800">
                  {children}
                </code>
              ),
              pre: ({ children }) => (
                <pre className="bg-gray-200 p-3 rounded text-xs overflow-x-auto mb-3">
                  {children}
                </pre>
              ),
              h1: ({ children }) => <h1 className="text-2xl font-bold mb-3 text-gray-900">{children}</h1>,
              h2: ({ children }) => <h2 className="text-xl font-bold mb-2 text-gray-900">{children}</h2>,
              h3: ({ children }) => <h3 className="text-lg font-semibold mb-2 text-gray-900">{children}</h3>,
            }}
          >
            {aiResult.response}
          </ReactMarkdown>
        </div>
      </div>
    );
  }

  // Show analysis tabs if generated
  if (analysisGenerated) {
    return (
      <div>
        <Tabs
          serveCharts={serveCharts}
          returnCharts={returnCharts}
          rankingChart={rankingChart}
          matches={matches}
          rawData={matches}
          loading={loading}
          selectedPlayer={selectedPlayer}
          filters={filters || undefined}
        />
      </div>
    );
  }

  // Default empty state
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
      <div className="text-center text-gray-400">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p className="text-lg mb-2">No results to display</p>
        <p className="text-sm">
          Ask a question using the search bar above, or select filters and generate analysis.
        </p>
      </div>
    </div>
  );
};

