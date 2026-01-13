import React from 'react';
import { Search, Loader2 } from 'lucide-react';

interface SearchPanelProps {
  onQuerySubmit: (query: string) => void;
  onClear: () => void;
  disabled?: boolean;
  value: string;
  onChange: (value: string) => void;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({
  onQuerySubmit,
  onClear,
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
    <div className="relative mb-6 animate-in fade-in fill-mode-both delay-150 duration-700">
      <div className="group relative flex items-center bg-white/70 backdrop-blur-xl border border-slate-200 rounded-2xl shadow-xl shadow-slate-200/50 focus-within:ring-2 focus-within:ring-emerald-500/20 focus-within:border-emerald-500/50 transition-all duration-300">
        <div className="pl-6 pointer-events-none text-slate-400">
          <Search className="w-5 h-5 group-focus-within:text-emerald-500 transition-colors" />
        </div>
        <input
          className="w-full py-5 px-6 bg-transparent text-lg focus:outline-none placeholder:text-slate-400"
          type="text"
          placeholder="Who has the most aces? Federer vs Nadal stats..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          disabled={disabled}
        />
        <div className="pr-3">
          <button
            className="bg-slate-900 hover:bg-emerald-600 disabled:bg-slate-300 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 active:scale-95 flex items-center gap-2 group shadow-lg shadow-slate-900/10"
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
