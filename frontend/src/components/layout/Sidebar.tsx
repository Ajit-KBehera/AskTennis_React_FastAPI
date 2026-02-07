import React, { useEffect, useState, useMemo, useCallback } from 'react';
import Select from 'react-select';
import type { StylesConfig } from 'react-select';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { apiClient, endpoints } from '../../api/client';
import type { FilterOptionsResponse } from '../../types';
import { Filter, RefreshCcw, X, Search, Users, Trophy, RotateCcw } from 'lucide-react';

type OptionType = { value: string; label: string };

interface SidebarProps {
  onFilterChange: (filters: {
    player_name: string;
    opponent?: string;
    tournament?: string;
    surface?: string[];
    year?: string;
  }) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onFilterChange, isOpen = true, onClose }) => {
  const [options, setOptions] = useState<FilterOptionsResponse>({ players: [], tournaments: [] });
  const [loading, setLoading] = useState(true);

  // Local state for selections
  const [selectedPlayer, setSelectedPlayer] = useState('All Players');
  const [selectedOpponent, setSelectedOpponent] = useState('All Opponents');
  const [selectedTournament, setSelectedTournament] = useState('All Tournaments');
  const [selectedSurfaces, setSelectedSurfaces] = useState<string[]>([]);
  const [minYear, setMinYear] = useState(1968);
  const [maxYear, setMaxYear] = useState(2024);
  const [yearRange, setYearRange] = useState<[number, number]>([1968, 2024]);
  const [useAllYears, setUseAllYears] = useState(false);

  // Fetch initial options
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const res = await apiClient.get<FilterOptionsResponse>(endpoints.getFilters);
        setOptions(res.data);
        if (res.data.year_range) {
          const min = res.data.year_range.min;
          const max = res.data.year_range.max;
          setMinYear(min);
          setMaxYear(max);
          setYearRange([min, max]);
        }
        if (res.data.surfaces) {
          setSelectedSurfaces(res.data.surfaces);
        }
      } catch (err) {
        // Failed to load filters
      } finally {
        setLoading(false);
      }
    };
    fetchOptions();
  }, []);

  // Fetch dynamic options when player changes
  useEffect(() => {
    const fetchPlayerOptions = async () => {
      if (selectedPlayer === 'All Players') {
        // Reset to defaults
        setSelectedOpponent('All Opponents');
        setSelectedSurfaces(['Hard', 'Clay', 'Grass', 'Carpet']);
        setMinYear(1968);
        setMaxYear(2024);
        setYearRange([1968, 2024]);
        return;
      }

      try {
        const res = await apiClient.get<FilterOptionsResponse>(endpoints.getFilters, {
          params: { player_name: selectedPlayer }
        });

        if (res.data.opponents) {
          setOptions(prev => ({ ...prev, opponents: res.data.opponents }));
          // Reset opponent if not in new list
          setSelectedOpponent(prev => {
            if (res.data.opponents && !res.data.opponents.includes(prev)) {
              return 'All Opponents';
            }
            return prev;
          });
        }
        if (res.data.surfaces) {
          setOptions(prev => ({ ...prev, surfaces: res.data.surfaces }));
          setSelectedSurfaces(res.data.surfaces || []);
        }
        if (res.data.year_range) {
          const min = res.data.year_range.min;
          const max = res.data.year_range.max;
          setMinYear(min);
          setMaxYear(max);
          // Only update range if current selection is outside new bounds
          const currentMin = yearRange[0];
          const currentMax = yearRange[1];
          if (currentMin < min || currentMax > max || currentMin > currentMax) {
            setYearRange([min, max]);
          } else {
            // Keep current selection but ensure it's within bounds
            setYearRange([
              Math.max(min, Math.min(currentMin, max)),
              Math.min(max, Math.max(currentMax, min))
            ]);
          }
        }
        if (res.data.tournaments) {
          setOptions(prev => ({ ...prev, tournaments: res.data.tournaments }));
        }
      } catch (err) {
        // Failed to load player-specific filters
      }
    };
    fetchPlayerOptions();
  }, [selectedPlayer]);

  const handleGenerate = () => {
    const yearValue = useAllYears ? 'All Years' :
      yearRange[0] === yearRange[1] ? yearRange[0].toString() :
        `${yearRange[0]}-${yearRange[1]}`;

    onFilterChange({
      player_name: selectedPlayer,
      opponent: selectedOpponent,
      tournament: selectedTournament,
      surface: selectedSurfaces.length > 0 ? selectedSurfaces : undefined,
      year: yearValue
    });
  };

  const handleClearFilters = () => {
    setSelectedPlayer('All Players');
    setSelectedOpponent('All Opponents');
    setSelectedTournament('All Tournaments');
    setSelectedSurfaces(options.surfaces?.length ? options.surfaces : ['Hard', 'Clay', 'Grass', 'Carpet']);
    setYearRange([minYear, maxYear]);
    setUseAllYears(false);
    onFilterChange({
      player_name: 'All Players',
      opponent: 'All Opponents',
      tournament: 'All Tournaments',
      surface: [],
      year: 'All Years'
    });
    onClose?.();
  };

  // Convert options to react-select format
  const playerOptions = useMemo(() =>
    options.players.map(p => ({ value: p, label: p })),
    [options.players]
  );

  const opponentOptions = useMemo(() =>
    (options.opponents || options.players).map(o => ({ value: o, label: o })),
    [options.opponents, options.players]
  );

  const tournamentOptions = useMemo(() =>
    options.tournaments.map(t => ({ value: t, label: t })),
    [options.tournaments]
  );

  // Get current selected values for react-select
  const selectedPlayerOption = useMemo(() =>
    playerOptions.find(p => p.value === selectedPlayer) || playerOptions[0],
    [playerOptions, selectedPlayer]
  );

  const selectedOpponentOption = useMemo(() =>
    opponentOptions.find(o => o.value === selectedOpponent) || opponentOptions[0],
    [opponentOptions, selectedOpponent]
  );

  const selectedTournamentOption = useMemo(() =>
    tournamentOptions.find(t => t.value === selectedTournament) || tournamentOptions[0],
    [tournamentOptions, selectedTournament]
  );

  // Optimized filter function - fast string matching with early exit
  const optimizedFilterOption = useCallback((option: OptionType, searchText: string) => {
    if (!searchText || searchText.length === 0) return true;
    if (searchText.length > option.label.length) return false; // Early exit
    const searchLower = searchText.toLowerCase();
    const labelLower = option.label.toLowerCase();
    return labelLower.includes(searchLower);
  }, []);

  // Custom styles for react-select to match our design
  const selectStyles: StylesConfig<OptionType, false> = {
    control: (base, state) => ({
      ...base,
      backgroundColor: 'rgba(30, 41, 59, 0.5)', // slate-800/50
      borderColor: state.isFocused ? '#22c55e' : 'rgba(255, 255, 255, 0.1)',
      borderRadius: '0.75rem',
      padding: '2px',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(34, 197, 94, 0.2)' : 'none',
      color: '#f8fafc',
      '&:hover': {
        borderColor: state.isFocused ? '#22c55e' : 'rgba(255, 255, 255, 0.2)',
      },
    }),
    singleValue: (base) => ({
      ...base,
      color: '#f8fafc', // slate-50
    }),
    input: (base) => ({
      ...base,
      color: '#f8fafc',
    }),
    menu: (base) => ({
      ...base,
      backgroundColor: '#1e293b', // slate-800
      zIndex: 9999,
      maxHeight: '300px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
    }),
    menuList: (base) => ({
      ...base,
      maxHeight: '300px',
      padding: 0,
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected
        ? '#22c55e' // tennis-green-glow
        : state.isFocused
          ? 'rgba(34, 197, 94, 0.1)'
          : 'transparent',
      color: state.isSelected ? 'black' : '#e2e8f0', // slate-200
      cursor: 'pointer',
      '&:active': {
        backgroundColor: '#22c55e',
        color: 'black',
      },
    }),
  };

  if (loading) return (
    <div className="w-full md:w-80 h-screen glass-panel border-r border-white/5 flex items-center justify-center">
      <div className="text-slate-400 animate-pulse">Loading filters...</div>
    </div>
  );

  return (
    <>
      {/* Mobile overlay backdrop */}
      {onClose && (
        <div
          className={`md:hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-40 transition-opacity ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
            }`}
          onClick={onClose}
        />
      )}

      <aside
        className={`${isOpen ? 'translate-x-0' : '-translate-x-full'
          } md:translate-x-0 md:flex fixed md:relative z-50 w-full md:w-80 glass-panel border-r border-white/5 h-screen flex flex-col transition-transform duration-300 ease-in-out`}
      >
        <div className="p-6 border-b border-white/10 flex items-center justify-between bg-white/5">
          <h1 className="text-xl font-black flex items-center gap-2 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">
            <Filter className="w-5 h-5 text-emerald-400" />
            AskTennis
          </h1>
          {/* Close button for mobile */}
          {onClose && (
            <button
              onClick={onClose}
              className="md:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          )}
        </div>

        <div className="p-6 flex-1 overflow-y-auto space-y-8 custom-scrollbar">
          <div className="space-y-6">
            <div>
              <label className="flex text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 items-center gap-2">
                <Search className="w-3.5 h-3.5 text-emerald-400" /> Player
              </label>
              <Select
                value={selectedPlayerOption}
                onChange={(option) => setSelectedPlayer(option?.value || 'All Players')}
                options={playerOptions}
                isSearchable
                isClearable={false}
                placeholder="Type manually..."
                filterOption={optimizedFilterOption}
                styles={selectStyles}
                className="react-select-container"
                classNamePrefix="react-select"
                maxMenuHeight={300}
                menuPlacement="auto"
                noOptionsMessage={({ inputValue }) =>
                  inputValue ? `No players found` : 'Search...'
                }
              />
            </div>

            <div>
              <label className="flex text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 items-center gap-2">
                <Users className="w-3.5 h-3.5 text-blue-400" /> Opponent
              </label>
              <Select
                value={selectedOpponentOption}
                onChange={(option) => setSelectedOpponent(option?.value || 'All Opponents')}
                options={opponentOptions}
                isSearchable
                isClearable={false}
                isDisabled={selectedPlayer === 'All Players'}
                placeholder="Filter by opponent..."
                filterOption={optimizedFilterOption}
                styles={selectStyles}
                className="react-select-container"
                classNamePrefix="react-select"
                maxMenuHeight={300}
                menuPlacement="auto"
                noOptionsMessage={({ inputValue }) =>
                  inputValue ? `No opponents found` : 'Search...'
                }
              />
            </div>

            <div>
              <label className="flex text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 items-center gap-2">
                <Trophy className="w-3.5 h-3.5 text-amber-400" /> Tournament
              </label>
              <Select
                value={selectedTournamentOption}
                onChange={(option) => setSelectedTournament(option?.value || 'All Tournaments')}
                options={tournamentOptions}
                isSearchable
                isClearable={false}
                placeholder="Filter by tournament..."
                filterOption={optimizedFilterOption}
                styles={selectStyles}
                className="react-select-container"
                classNamePrefix="react-select"
                maxMenuHeight={300}
                menuPlacement="auto"
                noOptionsMessage={({ inputValue }) =>
                  inputValue ? `No tournaments found` : 'Search...'
                }
              />
            </div>
          </div>

          <div className="pt-4 border-t border-white/5">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Era & Timeline
            </label>
            <div className="space-y-4 bg-slate-900/30 p-4 rounded-xl border border-white/5">
              <label className="flex items-center gap-3 text-sm text-slate-300 font-medium cursor-pointer hover:text-white transition-colors">
                <input
                  type="checkbox"
                  checked={useAllYears}
                  onChange={(e) => setUseAllYears(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-emerald-500 focus:ring-emerald-500/20"
                />
                Include All Years ({minYear}-{maxYear})
              </label>
              {!useAllYears && (
                <div className="space-y-4">
                  {minYear === maxYear ? (
                    <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                      <p className="text-sm text-blue-400">
                        Single year available: <strong>{minYear}</strong>
                      </p>
                    </div>
                  ) : (
                    <>
                      <div className="px-2 pt-2">
                        <Slider
                          range
                          min={minYear}
                          max={maxYear}
                          value={[yearRange[0], yearRange[1]]}
                          onChange={(value) => {
                            if (Array.isArray(value)) {
                              setYearRange([value[0], value[1]]);
                            }
                          }}
                          trackStyle={[{ backgroundColor: '#22c55e', height: 4 }]}
                          handleStyle={[
                            {
                              borderColor: '#22c55e',
                              height: 16,
                              width: 16,
                              backgroundColor: '#0f172a',
                              boxShadow: '0 0 0 2px #22c55e',
                              opacity: 1
                            },
                            {
                              borderColor: '#22c55e',
                              height: 16,
                              width: 16,
                              backgroundColor: '#0f172a',
                              boxShadow: '0 0 0 2px #22c55e',
                              opacity: 1
                            }
                          ]}
                          railStyle={{ backgroundColor: 'rgba(255,255,255,0.1)', height: 4 }}
                        />
                      </div>
                      <div className="flex justify-between items-center text-xs text-slate-400 font-mono">
                        <span>{minYear}</span>
                        <span className="font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">
                          {yearRange[0] === yearRange[1]
                            ? `${yearRange[0]}`
                            : `${yearRange[0]} — ${yearRange[1]}`
                          }
                        </span>
                        <span>{maxYear}</span>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-white/5">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Court Surface</label>
            <div className="grid grid-cols-2 gap-2">
              {(options.surfaces || ['Hard', 'Clay', 'Grass', 'Carpet']).map(surface => {
                const isSelected = selectedSurfaces.includes(surface);
                return (
                  <label
                    key={surface}
                    className={`flex items-center justify-between text-sm p-3 rounded-lg border cursor-pointer transition-all duration-200 group ${isSelected
                      ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 shadow-lg shadow-emerald-500/10'
                      : 'bg-slate-900/30 border-white/5 text-slate-400 hover:bg-white/5 hover:border-white/10'
                      }`}
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedSurfaces([...selectedSurfaces, surface]);
                          } else {
                            setSelectedSurfaces(selectedSurfaces.filter(s => s !== surface));
                          }
                        }}
                        className="sr-only"
                      />
                      <span className="font-medium">{surface}</span>
                    </div>
                    {isSelected && (
                      <div className="bg-emerald-500 rounded-full p-0.5 animate-in zoom-in duration-200">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="w-3 h-3 text-slate-950"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      </div>
                    )}
                  </label>
                );
              })}
            </div>
          </div>

          <div className="flex gap-3 mt-4">
            <button
              type="button"
              onClick={handleClearFilters}
              className="flex-1 min-h-[44px] px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white font-medium flex items-center justify-center gap-2 transition-all"
              aria-label="Clear all filters"
            >
              <RotateCcw className="w-4 h-4" /> Clear
            </button>
            <button
              type="button"
              onClick={handleGenerate}
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 px-6 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 border border-white/10 group transform hover:-translate-y-0.5 min-h-[44px]"
            >
              <RefreshCcw className="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
              Generate
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
