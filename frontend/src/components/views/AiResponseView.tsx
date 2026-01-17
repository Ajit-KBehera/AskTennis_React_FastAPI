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
    conversationFlow: any[];
}

export const AiResponseView: React.FC<AiResponseViewProps> = ({
    aiResponse,
    aiSqlQueries,
    aiData,
    conversationFlow
}) => {
    const renderMessageContent = (msg: any) => {
        const type = msg.type;
        const content = msg.content;

        if (type === 'HumanMessage') {
            return (
                <div className="space-y-1">
                    <div className="text-sm font-bold text-blue-300">👤 Human:</div>
                    <div className="text-gray-300 whitespace-pre-wrap">{typeof content === 'string' ? content : JSON.stringify(content)}</div>
                </div>
            );
        }

        if (type === 'AIMessage') {
            let textContent = "";
            if (Array.isArray(content)) {
                for (const part of content) {
                    if (typeof part === 'string') {
                        textContent += part;
                    } else if (typeof part === 'object' && part !== null) {
                        textContent += part.text || JSON.stringify(part);
                    }
                }
            } else {
                textContent = String(content);
            }

            if (!textContent && msg.tool_calls && msg.tool_calls.length > 0) {
                const toolNames = msg.tool_calls.map((tc: any) => tc.name).join(', ');
                textContent = `🔧 Calling tool(s): ${toolNames}`;
            } else if (!textContent) {
                textContent = "*[No text content]*";
            }

            return (
                <div className="space-y-1">
                    <div className="text-sm font-bold text-emerald-300">🤖 AI:</div>
                    <div className="text-gray-300 whitespace-pre-wrap">{textContent}</div>
                </div>
            );
        }

        if (type === 'ToolMessage') {
            let contentStr = String(content);
            if (contentStr.length > 500) {
                contentStr = contentStr.substring(0, 500) + "...";
            }
            return (
                <div className="space-y-1">
                    <div className="text-sm font-bold text-amber-300">🔧 Tool Response:</div>
                    <div className="bg-black/30 p-2 rounded text-xs font-mono text-gray-400 overflow-x-auto">
                        {contentStr}
                    </div>
                </div>
            );
        }

        // Fallback for other message types
        let displayContent = String(content);
        if (displayContent.length > 200) {
            displayContent = displayContent.substring(0, 200) + "...";
        }
        return (
            <div className="space-y-1">
                <div className="text-sm font-bold text-gray-400">📝 {type}:</div>
                <div className="text-gray-300">{displayContent}</div>
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
