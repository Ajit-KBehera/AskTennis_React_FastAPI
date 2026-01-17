import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Lightbulb } from 'lucide-react';
import SqlCodeBlock from '../ui/SqlCodeBlock';
import Expander from '../ui/Expander';
import { DataTable } from '../ui/DataTable';
import { parseMessageForDisplay } from '../../utils/messageParser';
import { DataVisualizer } from '../ui/DataVisualizer';

interface AiResponseViewProps {
    aiResponse: string;
    aiSqlQueries: string[];
    aiData: any[];
    conversationFlow: any[];
}

export const AiResponseView: React.FC<AiResponseViewProps> = ({
    aiResponse,
    aiSqlQueries,
    aiData,
    conversationFlow
}) => {
    const renderMessageContent = (msg: any) => {
        const { label, labelClass, content, isCodeBlock } = parseMessageForDisplay(msg);

        return (
            <div className="space-y-1">
                <div className={`text-sm font-bold ${labelClass}`}>{label}</div>
                {isCodeBlock ? (
                    <div className="bg-black/30 p-2 rounded text-xs font-mono text-gray-400 overflow-x-auto">
                        {content}
                    </div>
                ) : (
                    <div className="text-gray-300 whitespace-pre-wrap">{content}</div>
                )}
            </div>
        );
    };

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
                    {/* 1. Visual Analysis (Auto-Detected) */}
                    <div className="mt-4">
                        <DataVisualizer data={aiData} />
                    </div>

                    {/* 2. Raw Data Table */}
                    <div className="mt-4">
                        <DataTable data={aiData} maxHeight={400} />
                    </div>
                </Expander>
            )}

            {/* Conversation Flow Expander */}
            {conversationFlow && conversationFlow.length > 1 && (
                <Expander label="💬 Conversational Flow">
                    <div className="space-y-4 mt-4 p-4 bg-white/5 rounded-xl border border-white/10">
                        {conversationFlow.slice(0, -1).map((msg, i) => (
                            <div key={i}>
                                {renderMessageContent(msg)}
                                {i < conversationFlow.length - 2 && (
                                    <hr className="border-white/10 my-4" />
                                )}
                            </div>
                        ))}
                    </div>
                </Expander>
            )}
        </div>
    );
};
