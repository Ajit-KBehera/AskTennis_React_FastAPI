import React, { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { Lightbulb, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';
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
    const answerRef = useRef<HTMLDivElement>(null);
    const [copyAnswer, setCopyAnswer] = useState(false);
    const [copySql, setCopySql] = useState(false);
    const [sqlOpen, setSqlOpen] = useState(false);
    const [dataOpen, setDataOpen] = useState(false);
    const [flowOpen, setFlowOpen] = useState(false);

    const hasExpanders = (aiSqlQueries?.length > 0) || (aiData?.length > 0) || (conversationFlow?.length > 1);
    const allExpanded = sqlOpen && dataOpen && flowOpen;
    const expandAll = () => {
        setSqlOpen(true);
        setDataOpen(true);
        setFlowOpen(true);
    };
    const collapseAll = () => {
        setSqlOpen(false);
        setDataOpen(false);
        setFlowOpen(false);
    };

    const handleCopyAnswer = async () => {
        await navigator.clipboard.writeText(aiResponse);
        setCopyAnswer(true);
        setTimeout(() => setCopyAnswer(false), 2000);
    };

    const handleCopySql = async () => {
        const text = (aiSqlQueries || []).join('\n\n');
        await navigator.clipboard.writeText(text);
        setCopySql(true);
        setTimeout(() => setCopySql(false), 2000);
    };

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
        <div ref={answerRef} className="space-y-6 animate-in fade-in zoom-in-95 duration-500" role="region" aria-live="polite" aria-label="AI answer">
            {/* Answer Card with ReactMarkdown + Math */}
            <div className="glass-panel rounded-3xl p-8 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                    <div className="flex items-center gap-2 text-emerald-400 font-bold uppercase tracking-wider text-sm">
                        <Lightbulb className="w-5 h-5 text-yellow-400 fill-yellow-400/20 shrink-0" />
                        <span>AI Insight</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={handleCopyAnswer}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-slate-300 hover:bg-emerald-500/20 hover:border-emerald-500/30 hover:text-emerald-400 transition-all text-sm"
                            aria-label="Copy answer"
                        >
                            {copyAnswer ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                            {copyAnswer ? 'Copied' : 'Copy answer'}
                        </button>
                        {aiSqlQueries && aiSqlQueries.length > 0 && (
                            <button
                                type="button"
                                onClick={handleCopySql}
                                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-slate-300 hover:bg-emerald-500/20 hover:border-emerald-500/30 hover:text-emerald-400 transition-all text-sm"
                                aria-label="Copy SQL"
                            >
                                {copySql ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                                {copySql ? 'Copied' : 'Copy SQL'}
                            </button>
                        )}
                    </div>
                </div>
                <div className="prose prose-invert max-w-none">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                    >
                        {aiResponse}
                    </ReactMarkdown>
                </div>
            </div>

            {hasExpanders && (
                <div className="flex flex-wrap items-center gap-2">
                    <button
                        type="button"
                        onClick={expandAll}
                        className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-slate-400 hover:text-white text-sm transition-colors"
                        aria-label="Expand all sections"
                    >
                        <ChevronDown className="w-4 h-4" /> Expand all
                    </button>
                    <button
                        type="button"
                        onClick={collapseAll}
                        className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-slate-400 hover:text-white text-sm transition-colors"
                        aria-label="Collapse all sections"
                    >
                        <ChevronUp className="w-4 h-4" /> Collapse all
                    </button>
                </div>
            )}

            {/* SQL Queries Expander */}
            {aiSqlQueries && aiSqlQueries.length > 0 && (
                <Expander
                    label="Technical Reasoning (SQL)"
                    expanded={sqlOpen}
                    onToggle={() => setSqlOpen(!sqlOpen)}
                >
                    <div className="space-y-4 mt-4">
                        {aiSqlQueries.map((sql, i) => (
                            <SqlCodeBlock key={i} code={sql} />
                        ))}
                    </div>
                </Expander>
            )}

            {/* Data Expander */}
            {aiData && aiData.length > 0 && (
                <Expander
                    label={`Query Results (${aiData.length} rows)`}
                    expanded={dataOpen}
                    onToggle={() => setDataOpen(!dataOpen)}
                >
                    <div className="mt-4">
                        <DataVisualizer data={aiData} />
                    </div>
                    <div className="mt-4">
                        <DataTable data={aiData} maxHeight={400} />
                    </div>
                </Expander>
            )}

            {/* Conversation Flow Expander */}
            {conversationFlow && conversationFlow.length > 1 && (
                <Expander
                    label="💬 Conversational Flow"
                    expanded={flowOpen}
                    onToggle={() => setFlowOpen(!flowOpen)}
                >
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
