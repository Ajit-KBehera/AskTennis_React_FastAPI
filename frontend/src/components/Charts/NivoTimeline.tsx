import React, { useMemo, useState, useCallback } from 'react';
import { ResponsiveLine } from '@nivo/line';
import type { RawServeMatch } from '../../types';

interface NivoTimelineProps {
  data: RawServeMatch[];
  showOpponentComparison?: boolean;
}

export const NivoTimeline: React.FC<NivoTimelineProps> = ({
  data,
  showOpponentComparison = false,
}) => {
  // State to track which series are visible
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set());

  // Toggle series visibility
  const toggleSeries = useCallback((seriesId: string) => {
    setHiddenSeries((prev) => {
      const next = new Set(prev);
      if (next.has(seriesId)) {
        next.delete(seriesId);
      } else {
        next.add(seriesId);
      }
      return next;
    });
  }, []);
  // Helper to calculate point size based on opponent rank
  const calculatePointSize = (rank: number | null | undefined): number => {
    if (rank === null || rank === undefined) {
      return 6; // Small for unknown rank
    }
    if (rank <= 5) return 18;   // Top 5: Massive
    if (rank <= 10) return 14;  // Top 10: Very Big
    if (rank <= 50) return 10;  // Top 50: Big
    if (rank <= 100) return 8;  // Top 100: Normal
    return 6; // Outside Top 100: Small
  };

  // Transform data for Nivo
  const chartData = useMemo(() => {
    const player1stIn = {
      id: '1st Serve In %',
      color: '#0066FF', // Bright blue
      data: data.map((match, index) => ({
        x: index + 1,
        y: match.player_1stIn !== null ? match.player_1stIn : null,
        matchData: match,
        pointSize: calculatePointSize(match.opponent_rank),
      })).filter(point => point.y !== null),
    };

    const player1stWon = {
      id: '1st Serve Won %',
      color: '#FF3300', // Bright red/orange
      data: data.map((match, index) => ({
        x: index + 1,
        y: match.player_1stWon !== null ? match.player_1stWon : null,
        matchData: match,
        pointSize: calculatePointSize(match.opponent_rank),
      })).filter(point => point.y !== null),
    };

    const player2ndWon = {
      id: '2nd Serve Won %',
      color: '#9933FF', // Bright purple/violet
      data: data.map((match, index) => ({
        x: index + 1,
        y: match.player_2ndWon !== null ? match.player_2ndWon : null,
        matchData: match,
        pointSize: calculatePointSize(match.opponent_rank),
      })).filter(point => point.y !== null),
    };

    const lines = [player1stIn, player1stWon, player2ndWon];

    if (showOpponentComparison) {
      lines.push(
        {
          id: 'Opponent 1st In %',
          color: '#60A5FA', // Lighter blue for opponent
          data: data.map((match, index) => ({
            x: index + 1,
            y: match.opponent_1stIn !== null ? match.opponent_1stIn : null,
            matchData: match,
            pointSize: calculatePointSize(match.opponent_rank),
          })).filter(point => point.y !== null),
        },
        {
          id: 'Opponent 1st Won %',
          color: '#F87171', // Lighter red for opponent
          data: data.map((match, index) => ({
            x: index + 1,
            y: match.opponent_1stWon !== null ? match.opponent_1stWon : null,
            matchData: match,
            pointSize: calculatePointSize(match.opponent_rank),
          })).filter(point => point.y !== null),
        },
        {
          id: 'Opponent 2nd Won %',
          color: '#A78BFA', // Lighter purple for opponent
          data: data.map((match, index) => ({
            x: index + 1,
            y: match.opponent_2ndWon !== null ? match.opponent_2ndWon : null,
            matchData: match,
            pointSize: calculatePointSize(match.opponent_rank),
          })).filter(point => point.y !== null),
        }
      );
    }

    return lines;
  }, [data, showOpponentComparison]);

  // Filter out hidden series
  const visibleChartData = useMemo(() => {
    return chartData.filter((series) => !hiddenSeries.has(series.id));
  }, [chartData, hiddenSeries]);

  // Create a color map for quick lookup
  const colorMap = useMemo(() => {
    const map = new Map<string, string>();
    visibleChartData.forEach((series) => {
      map.set(series.id, series.color);
    });
    return map;
  }, [visibleChartData]);


  // Calculate vertical lines data (max value at each match across all visible series)
  const verticalLinesData = useMemo(() => {
    if (visibleChartData.length === 0) return [];
    
    // Find all unique x positions across all series
    const allXPositions = new Set<number>();
    visibleChartData.forEach(series => {
      series.data.forEach(point => {
        if (point.x !== null && point.x !== undefined) {
          allXPositions.add(point.x as number);
        }
      });
    });
    
    const xPositions = Array.from(allXPositions).sort((a, b) => a - b);
    
    return xPositions.map(x => {
      // Find max y value across all visible series at this x position
      let maxY = 0;
      visibleChartData.forEach(series => {
        const point = series.data.find(p => p.x === x);
        if (point && point.y !== null && point.y !== undefined) {
          maxY = Math.max(maxY, point.y as number);
        }
      });
      return { x, maxY };
    });
  }, [visibleChartData]);

  // Handle point click
  const handlePointClick = useCallback((point: unknown) => {
    const p = point as { data?: { x: number; y: number | null; matchData?: RawServeMatch } };
    if (p.data?.matchData) {
      const matchData = p.data.matchData;
      console.log('Clicked match:', matchData);
      // You can add custom click behavior here, e.g., open a modal, navigate, etc.
      // For now, just log to console
    }
  }, []);

  // Custom layer for vertical background lines (rendered behind data)
  const verticalLinesLayer = useCallback((props: { xScale: (value: number) => number; yScale: (value: number) => number }) => {
    const { xScale, yScale } = props;
    
    return (
      <g>
        {verticalLinesData.map((line, index) => {
          const x = xScale(line.x);
          const y0 = yScale(0);
          const y1 = yScale(line.maxY);
          
          return (
            <line
              key={`vertical-${index}`}
              x1={x}
              y1={y0}
              x2={x}
              y2={y1}
              stroke="gray"
              strokeWidth={0.8}
              opacity={0.3}
              style={{ pointerEvents: 'none' }}
            />
          );
        })}
      </g>
    );
  }, [verticalLinesData]);

  // Helper to get point size from embedded data
  // Size is pre-calculated and embedded in each data point
  const getPointSize = (point: any): number => {
    try {
      // Nivo passes point with data property
      // Try multiple ways to access the size
      const data = point?.data || point;
      const size = data?.pointSize;
      
      // Ensure we return a valid number between 4 and 20
      if (typeof size === 'number' && size >= 4 && size <= 20) {
        return size;
      }
    } catch (e) {
      console.warn('Error getting point size:', e);
    }
    // Fallback to a visible default size if not found or invalid
    return 10;
  };

  return (
    <div className="w-full h-[500px]">
      {/* Legend for Dot Size (Opponent Difficulty) */}
      {/* <div className="absolute top-4 right-4 bg-white/80 p-2 rounded text-xs text-gray-500 border border-gray-100 z-10 pointer-events-none">
        <span className="font-semibold block mb-1">Opponent Difficulty (Dot Size)</span>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <div className="w-[14px] h-[14px] rounded-full bg-gray-400"></div> Top 10
          </div>
          <div className="flex items-center gap-1">
            <div className="w-[10px] h-[10px] rounded-full bg-gray-400"></div> Top 50
          </div>
          <div className="flex items-center gap-1">
            <div className="w-[6px] h-[6px] rounded-full bg-gray-400"></div> 100+
          </div>
        </div>
      </div> */}
      <ResponsiveLine
        data={visibleChartData}
        margin={{ top: 50, right: 50, bottom: 80, left: 70 }}
        xScale={{ type: 'linear', min: 1, max: 'auto' }}
        yScale={{ type: 'linear', min: 0, max: 100 }}
        curve="linear"
        colors={(d) => d.color}
        enablePoints={true}
        axisTop={{}}
        lineWidth={0}
        enableSlices={false}
        layers={['grid','axes', verticalLinesLayer, 'markers', 'areas', 'lines', 'points', 'mesh', 'legends']}
        onClick={handlePointClick}
        axisRight={null}
        axisBottom={{
          tickSize: 0,
          tickPadding: 10,
          tickRotation: 1,
          legend: 'Matches',
          legendOffset: 25,
          truncateTickAt: 16
      }}
        axisLeft={{
          legend: '(%)',
          legendOffset: -40,
        }}
        // Dynamic point size based on opponent rank
        // Temporarily use fixed size to debug, then switch back to getPointSize
        pointSize={10}
        pointColor={(point: { series?: { id: string; color: string }; serieId?: string; id?: string }) => {
          const serieId = point.series?.id || point.serieId || point.id || '';
          return colorMap.get(serieId) || point.series?.color || '#000000';
        }}
        pointBorderWidth={2}
        pointBorderColor="#FFFFFF"
        useMesh={true}
        legends={[
          {
            anchor: 'bottom',
            direction: 'row',
            justify: false,
            translateX: 0,
            translateY: 50,
            itemsSpacing: 20,
            itemDirection: 'left-to-right',
            itemWidth: 100,
            itemHeight: 20,
            itemOpacity: 0.75,
            itemTextColor: '#374151',
            symbolSize: 12,
            symbolShape: 'circle',
            onClick: (d) => {
              const id = typeof d.id === 'string' ? d.id : String(d.id);
              toggleSeries(id);
            },
            effects: [
              {
                on: 'hover',
                style: {
                  itemBackground: 'rgba(0, 0, 0, .03)',
                  itemOpacity: 1,
                },
              },
            ],
          },
        ]}
        tooltip={({ point }) => {
          const matchData = (point.data as any).matchData as RawServeMatch | undefined;
          if (!matchData) return null;

          // Logic to find series color
          const pointX = (point.data as any)?.x;
          const pointY = (point.data as any)?.y;
          const series = visibleChartData.find((s) => s.data.some((d) => d.x === pointX && d.y === pointY));
          const serieId = series?.id || 'Unknown';
          const serieColor = series?.color || '#000000';

          return (
            // 1. Reduced padding from p-4 to p-3, added text-xs for tighter font
            <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg text-xs min-w-[200px] z-50">
              
              {/* Header: Match # and Result side-by-side */}
              <div className="flex justify-between items-center mb-2 border-b border-gray-100 pb-2">
                <span className="font-bold text-gray-800">Match #{point.data.x}</span>
                <span className={`font-bold px-2 py-0.5 rounded ${matchData.result === 'W' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {matchData.result}
                </span>
              </div>

              {/* Body: Opponent (Prominent) */}
              <div className="mb-2">
                <span className="text-gray-500">vs </span>
                <span className="font-semibold text-gray-800 text-sm">
                  {matchData.opponent}
                </span>
                <span className="ml-2 px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-[10px] font-mono border border-gray-300">
                  #{matchData.opponent_rank ?? 'N/A'}
                </span>
              </div>

              {/* Metadata Grid: 2 columns to save vertical space */}
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 mb-2 text-gray-600">
                <div>
                  <span className="text-gray-400">Tourney:</span> {matchData.tourney_name}
                </div>
                <div>
                   <span className="text-gray-400">Year:</span> {matchData.year}
                </div>
                <div>
                   <span className="text-gray-400">Surf:</span> {matchData.surface}
                </div>
                <div>
                   <span className="text-gray-400">Rd:</span> {matchData.round}
                </div>
              </div>

              {/* Footer: Statistic Value */}
              <div className="mt-2 pt-2 border-t border-gray-100">
                <p className="font-bold text-sm" style={{ color: serieColor }}>
                  {serieId}: {point.data.y !== null ? `${Number(point.data.y).toFixed(2)}%` : 'N/A'}
                </p>
              </div>
            </div>
          );
        }}
        theme={{
          axis: {
            legend: {
              text: {
                fill: '#374151',
                fontSize: 14,
                fontWeight: 600,
              },
            },
            ticks: {
              text: {
                fill: '#374151',
                fontSize: 12,
              },
            },
          },
        }}
      />
    </div>
  );
};

