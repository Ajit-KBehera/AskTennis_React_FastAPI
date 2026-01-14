import React from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import type { Match } from '../../api/client';

interface MatchesTableProps {
  matches: Match[];
}

export const MatchesTable: React.FC<MatchesTableProps> = ({ matches }) => {
  if (matches.length === 0) {
    return (
      <div className="h-40 flex items-center justify-center text-slate-500">
        No matches found.
      </div>
    );
  }

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const match = matches[index];
    // Alternating row colors for dark mode
    const bgClass = index % 2 === 0 ? "bg-white/0" : "bg-white/[0.02]";

    return (
      <div style={style} className={`flex items-center border-b border-white/5 text-sm text-slate-400 ${bgClass} hover:bg-white/5 transition-colors`}>
        <div className="w-[10%] px-4">{match.event_year}</div>
        <div className="w-[15%] px-4 truncate" title={match.tourney_date}>{match.tourney_date}</div>
        <div className="w-[20%] px-4 truncate text-slate-300" title={match.tourney_name}>{match.tourney_name}</div>
        <div className="w-[10%] px-4 text-emerald-400/80">{match.round}</div>
        <div className="w-[15%] px-4 font-bold text-emerald-400 truncate" title={match.winner_name}>{match.winner_name}</div>
        <div className="w-[15%] px-4 truncate text-red-400/70" title={match.loser_name}>{match.loser_name}</div>
        <div className="w-[15%] px-4 font-mono text-xs text-slate-500">{match.score}</div>
      </div>
    );
  };

  return (
    <div className="w-full h-[500px] border border-white/10 rounded-xl bg-slate-900/40 shadow-inner flex flex-col overflow-hidden">
      {/* Static Header */}
      <div className="flex items-center bg-white/5 border-b border-white/10 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider backdrop-blur-sm">
        <div className="w-[10%] px-4">Year</div>
        <div className="w-[15%] px-4">Date</div>
        <div className="w-[20%] px-4">Tournament</div>
        <div className="w-[10%] px-4">Round</div>
        <div className="w-[15%] px-4">Winner</div>
        <div className="w-[15%] px-4">Loser</div>
        <div className="w-[15%] px-4">Score</div>
      </div>

      {/* Virtualized Body */}
      <div className="flex-1">
        <AutoSizer>
          {({ height, width }) => (
            <List
              height={height}
              itemCount={matches.length}
              itemSize={45} // Height of each row in px
              width={width}
            >
              {Row}
            </List>
          )}
        </AutoSizer>
      </div>

      <div className="p-2 text-xs text-slate-500 text-right border-t border-white/5 bg-slate-900/20">
        Showing {matches.length} matches
      </div>
    </div>
  );
};
