import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';

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
        <div className="sql-code-wrapper">
            <div className="sql-header">
                <span>SQL</span>
                <button onClick={copyToClipboard} className="copy-btn">
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                    {copied ? 'Copied!' : 'Copy'}
                </button>
            </div>
            <SyntaxHighlighter
                language="sql"
                style={oneDark}
                customStyle={{ margin: 0, borderRadius: '0 0 8px 8px' }}
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );
};

export default SqlCodeBlock;
