import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, LogOut, User } from 'lucide-react';

interface HeaderProps {
    user: string;
    onLogout: () => void;
    mode: 'ask' | 'stats';
    selectedPlayer?: string;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout, mode, selectedPlayer }) => {
    const [menuOpen, setMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
                setMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <header className="mb-6 relative z-20">
            <div className="glass-card rounded-2xl p-6 relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-emerald-400 to-blue-500 opacity-80" />

                <div className="flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left relative z-10">
                    <div className="flex flex-wrap items-center gap-4 md:gap-5">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20 transform group-hover:scale-105 transition-transform duration-300 border border-white/10 shrink-0">
                            <span className="text-4xl filter drop-shadow-md" aria-hidden>🎾</span>
                        </div>
                        <div>
                            {(mode === 'stats' && selectedPlayer && selectedPlayer !== 'All Players') && (
                                <nav className="text-sm text-slate-400 mb-1" aria-label="Breadcrumb">
                                    <span>Stats</span>
                                    <span className="mx-2">→</span>
                                    <span className="text-emerald-400">{selectedPlayer}</span>
                                </nav>
                            )}
                            <h1 className="text-3xl md:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-300 tracking-tight mb-1">
                                AskTennis Analytics
                            </h1>
                            <p className="text-slate-400 font-medium text-base md:text-lg">
                                Advanced AI-powered tennis intelligence engine
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="hidden sm:flex gap-2">
                            <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/5 text-xs font-mono text-slate-400">
                                <span className="text-emerald-400">●</span> Live
                            </div>
                            <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/5 text-xs font-mono text-slate-400">
                                v2.5.0
                            </div>
                        </div>
                        <div className="relative" ref={menuRef}>
                            <button
                                type="button"
                                onClick={() => setMenuOpen((o) => !o)}
                                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 hover:text-white transition-all min-h-[44px]"
                                aria-expanded={menuOpen}
                                aria-haspopup="true"
                                aria-label="User menu"
                            >
                                <User className="w-5 h-5 text-emerald-400 shrink-0" />
                                <span className="font-medium truncate max-w-[120px] md:max-w-[180px]">{user}</span>
                                <ChevronDown className={`w-4 h-4 shrink-0 transition-transform ${menuOpen ? 'rotate-180' : ''}`} />
                            </button>
                            {menuOpen && (
                                <div
                                    className="absolute right-0 mt-2 py-2 w-48 rounded-xl bg-slate-800 border border-white/10 shadow-xl z-50"
                                    role="menu"
                                >
                                    <button
                                        type="button"
                                        onClick={() => {
                                            onLogout();
                                            setMenuOpen(false);
                                        }}
                                        className="w-full flex items-center gap-2 px-4 py-3 text-left text-slate-300 hover:bg-white/10 hover:text-white transition-colors"
                                        role="menuitem"
                                    >
                                        <LogOut className="w-4 h-4" /> Logout
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="absolute -top-24 -right-24 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" aria-hidden />
                <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl" aria-hidden />
            </div>
        </header>
    );
};
