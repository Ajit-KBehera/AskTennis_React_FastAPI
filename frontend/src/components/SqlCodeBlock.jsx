import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Terminal } from 'lucide-react';

const SqlCodeBlock = ({ code }) => {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    return (
        <div className="rounded-xl overflow-hidden border border-slate-800 bg-slate-900 shadow-lg my-4 group">
            <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900 border-b border-slate-800">
                <div className="flex items-center gap-2 text-slate-400 font-mono text-xs font-bold uppercase tracking-wider">
                    <Terminal className="w-4 h-4 text-emerald-500" />
                    <span>PostgreSQL</span>
                </div>
                <button
                    onClick={copyToClipboard}
                    className="flex items-center gap-1.5 py-1 px-2.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-all duration-200 text-xs font-semibold"
                >
                    {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
            </div>
            <div className="p-1">
                <SyntaxHighlighter
                    language="sql"
                    style={vscDarkPlus}
                    customStyle={{
                        margin: 0,
                        background: 'transparent',
                        fontSize: '0.875rem',
                        lineHeight: '1.5',
                        padding: '1rem'
                    }}
                >
                    {code}
                </SyntaxHighlighter>
            </div>
        </div>
    );
};

export default SqlCodeBlock;

