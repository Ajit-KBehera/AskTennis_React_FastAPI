import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

const Expander = ({ label, children, defaultExpanded = false }) => {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className={`expander-wrapper ${isExpanded ? 'is-expanded' : ''}`}>
            <button
                className="expander-header"
                onClick={() => setIsExpanded(!isExpanded)}
                aria-expanded={isExpanded}
            >
                <div className="expander-header-content">
                    <span className="expander-icon">
                        {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                    </span>
                    <span className="expander-label">{label}</span>
                </div>
            </button>
            <div className={`expander-content ${isExpanded ? 'is-visible' : ''}`}>
                <div className="expander-inner">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Expander;
