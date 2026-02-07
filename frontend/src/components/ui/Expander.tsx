import React, { useState, ReactNode } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface ExpanderProps {
    label: string;
    children: ReactNode;
    defaultExpanded?: boolean;
    /** Controlled: when provided with onToggle, use this instead of internal state */
    expanded?: boolean;
    onToggle?: () => void;
}

const Expander: React.FC<ExpanderProps> = ({ label, children, defaultExpanded = false, expanded, onToggle }) => {
    const [internalExpanded, setInternalExpanded] = useState(defaultExpanded);
    const isControlled = expanded !== undefined && onToggle !== undefined;
    const isExpanded = isControlled ? expanded : internalExpanded;
    const setExpanded = isControlled ? onToggle : () => setInternalExpanded((p) => !p);

    return (
        <div className="border border-white/10 rounded-2xl bg-slate-800/20 backdrop-blur-sm overflow-hidden transition-all duration-300 hover:border-white/20">
            <button
                type="button"
                className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors duration-200 group"
                onClick={setExpanded}
                aria-expanded={isExpanded}
            >
                <div className="flex items-center gap-3">
                    <div className={`p-1 rounded-md transition-colors duration-200 ${isExpanded ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 text-slate-400 group-hover:bg-emerald-500/10 group-hover:text-emerald-400'}`}>
                        {isExpanded ? <ChevronDown size={18} strokeWidth={2.5} /> : <ChevronRight size={18} strokeWidth={2.5} />}
                    </div>
                    <span className={`font-semibold transition-colors duration-200 ${isExpanded ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`}>
                        {label}
                    </span>
                </div>
            </button>
            <div
                className={`grid transition-all duration-300 ease-in-out ${isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}
            >
                <div className="overflow-hidden">
                    <div className="p-4 pt-0 border-t border-white/5">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Expander;
