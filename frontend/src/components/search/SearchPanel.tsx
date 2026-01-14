import React from 'react';
import { Search, Loader2 } from 'lucide-react';

interface SearchPanelProps {
  onQuerySubmit: (query: string) => void;
  disabled?: boolean;
  value: string;
  onChange: (value: string) => void;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({
  onQuerySubmit,
  disabled = false,
  value,
  onChange
}) => {
  const handleSubmit = () => {
    if (value.trim() && !disabled) {
      onQuerySubmit(value.trim());
    }
  };

  return (
    <div className="sticky top-0 z-30 -mx-8 px-8 pt-4 pb-4 -mt-4 bg-slate-950/0 backdrop-blur-sm mb-6 animate-in fade-in fill-mode-both delay-150 duration-700">
      <div className="group relative flex items-center bg-slate-800/50 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl shadow-black/20 focus-within:ring-2 focus-within:ring-emerald-500/20 focus-within:border-emerald-500/50 transition-all duration-300">
        <div className="pl-6 pointer-events-none text-slate-400">
          <Search className="w-5 h-5 group-focus-within:text-emerald-400 transition-colors" />
        </div>
        <input
          className="w-full py-5 px-6 bg-transparent text-lg text-white focus:outline-none placeholder:text-slate-500"
          type="text"
          placeholder="Ask anything... (e.g., 'Roger Federer vs Nadal stats')"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          disabled={disabled}
        />
        <div className="pr-3">
          <button
            className="bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-950 font-bold py-3 px-6 rounded-xl transition-all duration-300 active:scale-95 flex items-center gap-2 group shadow-lg shadow-emerald-500/20"
            onClick={handleSubmit}
            disabled={disabled || !value.trim()}
          >
            {disabled ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Analyze</span>}
          </button>
        </div>
      </div>
    </div>
  );
};
