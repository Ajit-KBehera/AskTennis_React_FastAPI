import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Lightbulb } from 'lucide-react';
import SqlCodeBlock from '../SqlCodeBlock';
import Expander from '../Expander';
import { DataTable } from '../DataTable';

interface AiResponseSectionProps {
    aiResponse: string;
    aiSqlQueries: string[];
    aiData: any[];
}

export const AiResponseSection: React.FC<AiResponseSectionProps> = ({
    aiResponse,
    aiSqlQueries,
    aiData
}) => {
    return (
        <div className="space-y-4 animate-in fade-in zoom-in-95 duration-500">
            {/* Answer Card with ReactMarkdown */}
            <div className="bg-white/80 backdrop-blur-md border border-gray-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center gap-2 mb-6 text-emerald-600 font-bold uppercase tracking-wider text-sm">
                    <Lightbulb className="w-4 h-4" />
                    <span>AI Insight</span>
                </div>
                <div className="prose prose-slate max-w-none prose-headings:font-black prose-a:text-emerald-600 prose-strong:text-slate-900">
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
