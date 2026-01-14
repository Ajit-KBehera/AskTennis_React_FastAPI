import React from 'react';

export const Header: React.FC = () => {
    return (
        <div className="glass-card rounded-2xl p-6 mb-8 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-emerald-400 to-blue-500 opacity-80" />

            <div className="flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left relative z-10">
                <div className="flex items-center gap-5">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20 transform group-hover:scale-105 transition-transform duration-300 border border-white/10">
                        <span className="text-4xl filter drop-shadow-md">🎾</span>
                    </div>
                    <div>
                        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-300 tracking-tight mb-1">
                            AskTennis Analytics
                        </h1>
                        <p className="text-slate-400 font-medium text-lg">
                            Advanced AI-powered tennis intelligence engine
                        </p>
                    </div>
                </div>

                <div className="flex gap-3">
                    <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/5 text-xs font-mono text-slate-400">
                        <span className="text-emerald-400">●</span> Live System
                    </div>
                    <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/5 text-xs font-mono text-slate-400">
                        v2.5.0
                    </div>
                </div>
            </div>

            {/* Background decorative glow */}
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl" />
        </div>
    );
};
