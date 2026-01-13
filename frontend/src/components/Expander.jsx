import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

const Expander = ({ label, children, defaultExpanded = false }) => {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="border border-slate-200 rounded-2xl bg-white/50 backdrop-blur-sm overflow-hidden transition-all duration-300 hover:border-emerald-200">
            <button
                className="w-full flex items-center justify-between p-4 text-left hover:bg-emerald-50/50 transition-colors duration-200 group"
                onClick={() => setIsExpanded(!isExpanded)}
                aria-expanded={isExpanded}
            >
                <div className="flex items-center gap-3">
                    <div className={`p-1 rounded-md transition-colors duration-200 ${isExpanded ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-400 group-hover:bg-emerald-100 group-hover:text-emerald-500'}`}>
                        {isExpanded ? <ChevronDown size={18} strokeWidth={2.5} /> : <ChevronRight size={18} strokeWidth={2.5} />}
                    </div>
                    <span className={`font-semibold transition-colors duration-200 ${isExpanded ? 'text-slate-900' : 'text-slate-600 group-hover:text-emerald-700'}`}>
                        {label}
                    </span>
                </div>
            </button>
            <div
                className={`grid transition-all duration-300 ease-in-out ${isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}
            >
                <div className="overflow-hidden">
                    <div className="p-4 pt-0 border-t border-slate-100">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Expander;

