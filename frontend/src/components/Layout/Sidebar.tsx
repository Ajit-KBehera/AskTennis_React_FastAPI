import React, { useEffect, useState, useMemo, useCallback } from 'react';
import Select from 'react-select';
import type { StylesConfig } from 'react-select';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { apiClient, endpoints } from '../../api/client';
import type { FilterOptionsResponse } from '../../types';
import { Filter, RefreshCcw, X } from 'lucide-react';

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
      backgroundColor: '#f9fafb',
      borderColor: state.isFocused ? '#3b82f6' : '#e5e7eb',
      borderRadius: '0.5rem',
      padding: '2px',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(59, 130, 246, 0.5)' : 'none',
      '&:hover': {
        borderColor: state.isFocused ? '#3b82f6' : '#d1d5db',
      },
    }),
    menu: (base) => ({
      ...base,
      zIndex: 9999,
      maxHeight: '300px', // Limit menu height for better performance
    }),
    menuList: (base) => ({
      ...base,
      maxHeight: '300px',
      padding: 0,
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected 
        ? '#3b82f6' 
        : state.isFocused 
        ? '#eff6ff' 
        : 'white',
      color: state.isSelected ? 'white' : '#374151',
      '&:active': {
        backgroundColor: '#3b82f6',
        color: 'white',
      },
    }),
  };

  if (loading) return <div className="p-6 text-gray-500">Loading filters...</div>;

  return (
    <>
      {/* Mobile overlay backdrop */}
      {onClose && (
        <div
          className={`md:hidden fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity ${
            isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}
          onClick={onClose}
        />
      )}
      
      <aside
        className={`${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 md:flex fixed md:relative z-50 w-80 bg-white border-r h-screen flex flex-col shadow-sm transition-transform duration-300 ease-in-out`}
      >
        <div className="p-6 border-b flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2 text-blue-700">
          <Filter className="w-5 h-5" />
          AskTennis
        </h1>
          {/* Close button for mobile */}
          {onClose && (
            <button
              onClick={onClose}
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          )}
      </div>

      <div className="p-6 flex-1 overflow-y-auto space-y-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Search Player</label>
          <Select
            value={selectedPlayerOption}
            onChange={(option) => setSelectedPlayer(option?.value || 'All Players')}
            options={playerOptions}
            isSearchable
            isClearable={false}
            placeholder="Type to search players..."
            filterOption={optimizedFilterOption}
            styles={selectStyles}
            className="react-select-container"
            classNamePrefix="react-select"
            menuMaxHeight={300}
            maxMenuHeight={300}
            menuPlacement="auto"
            noOptionsMessage={({ inputValue }) => 
              inputValue ? `No players found matching "${inputValue}"` : 'Type to search...'
            }
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Search Opponent</label>
          <Select
            value={selectedOpponentOption}
            onChange={(option) => setSelectedOpponent(option?.value || 'All Opponents')}
            options={opponentOptions}
            isSearchable
            isClearable={false}
            isDisabled={selectedPlayer === 'All Players'}
            placeholder="Type to search opponents..."
            filterOption={optimizedFilterOption}
            styles={selectStyles}
            className="react-select-container"
            classNamePrefix="react-select"
            menuMaxHeight={300}
            maxMenuHeight={300}
            menuPlacement="auto"
            noOptionsMessage={({ inputValue }) => 
              inputValue ? `No opponents found matching "${inputValue}"` : 'Type to search...'
            }
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Search Tournament</label>
          <Select
            value={selectedTournamentOption}
            onChange={(option) => setSelectedTournament(option?.value || 'All Tournaments')}
            options={tournamentOptions}
            isSearchable
            isClearable={false}
            placeholder="Type to search tournaments..."
            filterOption={optimizedFilterOption}
            styles={selectStyles}
            className="react-select-container"
            classNamePrefix="react-select"
            menuMaxHeight={300}
            maxMenuHeight={300}
            menuPlacement="auto"
            noOptionsMessage={({ inputValue }) => 
              inputValue ? `No tournaments found matching "${inputValue}"` : 'Type to search...'
            }
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Select Year Range
          </label>
          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={useAllYears}
                onChange={(e) => setUseAllYears(e.target.checked)}
                className="rounded"
              />
              All Years ({minYear}-{maxYear})
            </label>
            {!useAllYears && (
              <div className="space-y-3">
                {minYear === maxYear ? (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      Only one year available: <strong>{minYear}</strong>
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="px-2">
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
                        trackStyle={[{ backgroundColor: '#3b82f6', height: 6 }]}
                        handleStyle={[
                          { 
                            borderColor: '#3b82f6', 
                            height: 20, 
                            width: 20,
                            backgroundColor: '#fff',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                          },
                          { 
                            borderColor: '#3b82f6', 
                            height: 20, 
                            width: 20,
                            backgroundColor: '#fff',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                          }
                        ]}
                        railStyle={{ backgroundColor: '#e5e7eb', height: 6 }}
                        dotStyle={{ borderColor: '#d1d5db', backgroundColor: '#fff' }}
                        activeDotStyle={{ borderColor: '#3b82f6' }}
                      />
                    </div>
                    <div className="flex justify-between items-center text-xs text-gray-600">
                      <span>{minYear}</span>
                      <span className="font-medium text-gray-700">
                        {yearRange[0] === yearRange[1] 
                          ? `Selected: ${yearRange[0]}`
                          : `Selected: ${yearRange[0]} - ${yearRange[1]} (${yearRange[1] - yearRange[0] + 1} years)`
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

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Surfaces</label>
          <div className="space-y-2">
            {(options.surfaces || ['Hard', 'Clay', 'Grass', 'Carpet']).map(surface => (
              <label key={surface} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selectedSurfaces.includes(surface)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSurfaces([...selectedSurfaces, surface]);
                    } else {
                      setSelectedSurfaces(selectedSurfaces.filter(s => s !== surface));
                    }
                  }}
                  className="rounded"
                />
                {surface}
              </label>
            ))}
          </div>
        </div>

        <button 
          type="button"
          onClick={handleGenerate}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors cursor-pointer border-0"
        >
          <RefreshCcw className="w-4 h-4" />
          Generate Analysis
        </button>
      </div>
    </aside>
    </>
  );
};

