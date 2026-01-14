import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Lightbulb } from 'lucide-react';
import SqlCodeBlock from '../ui/SqlCodeBlock';
import Expander from '../ui/Expander';
import { DataTable } from '../ui/DataTable';

interface AiResponseViewProps {
    aiResponse: string;
    aiSqlQueries: string[];
    aiData: any[];
}

export const AiResponseView: React.FC<AiResponseViewProps> = ({
    aiResponse,
    aiSqlQueries,
    aiData
}) => {
    return (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            {/* Answer Card with ReactMarkdown */}
            <div className="glass-panel rounded-3xl p-8 shadow-xl">
                <div className="flex items-center gap-2 mb-6 text-emerald-400 font-bold uppercase tracking-wider text-sm">
                    <Lightbulb className="w-5 h-5 text-yellow-400 fill-yellow-400/20" />
                    <span>AI Insight</span>
                </div>
                <div className="prose prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiResponse}</ReactMarkdown>
                </div>
            </div>

            {/* SQL Queries Expander */}
            {aiSqlQueries && aiSqlQueries.length > 0 && (
                <Expander label="Technical Reasoning (SQL)">
                    <div className="space-y-4 mt-4">
                        {aiSqlQueries.map((sql, i) => (
                            <SqlCodeBlock key={i} code={sql} />
                        ))}
                    </div>
                </Expander>
            )}

            {/* Data Expander */}
            {aiData && aiData.length > 0 && (
                <Expander label={`Query Results (${aiData.length} rows)`}>
                    <div className="mt-4">
                        <DataTable data={aiData} maxHeight={400} />
                    </div>
                </Expander>
            )}
        </div>
    );
};
