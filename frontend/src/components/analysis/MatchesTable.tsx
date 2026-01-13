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
      <div className="h-40 flex items-center justify-center text-gray-400">
        No matches found.
      </div>
    );
  }

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const match = matches[index];
    // Alternating row colors
    const bgClass = index % 2 === 0 ? "bg-white" : "bg-gray-50";
    
    return (
      <div style={style} className={`flex items-center border-b border-gray-100 text-sm text-gray-700 ${bgClass} hover:bg-blue-50`}>
        <div className="w-[10%] px-4">{match.event_year}</div>
        <div className="w-[15%] px-4 truncate" title={match.tourney_date}>{match.tourney_date}</div>
        <div className="w-[20%] px-4 truncate" title={match.tourney_name}>{match.tourney_name}</div>
        <div className="w-[10%] px-4">{match.round}</div>
        <div className="w-[15%] px-4 font-medium text-gray-900 truncate" title={match.winner_name}>{match.winner_name}</div>
        <div className="w-[15%] px-4 truncate" title={match.loser_name}>{match.loser_name}</div>
        <div className="w-[15%] px-4 font-mono text-xs">{match.score}</div>
      </div>
    );
  };

  return (
    <div className="w-full h-[500px] border rounded-lg bg-white shadow-sm flex flex-col">
      {/* Static Header */}
      <div className="flex items-center bg-gray-100 border-b border-gray-200 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">
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
      
      <div className="p-2 text-xs text-gray-400 text-right border-t">
        Showing {matches.length} matches
      </div>
    </div>
  );
};

