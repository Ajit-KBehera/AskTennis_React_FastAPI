import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import type { RawServeMatch } from '../../types';

interface D3ServeTimelineProps {
  data: RawServeMatch[];
  metrics?: ('player_1stIn' | 'player_1stWon' | 'player_2ndWon')[]; // Support multiple metrics
  metric?: 'player_1stIn' | 'player_1stWon' | 'player_2ndWon'; // Single metric (backward compat)
  showOpponentComparison?: boolean;
  height?: number;
}

interface ChartPoint {
  x: number; // Match index
  y: number; // Metric value (0-100)
  radius: number; // Based on opponent rank
  match: RawServeMatch;
  color: string;
  metricLabel: string; // Label for the metric (for tooltip/legend)
  metricKey: string; // Key for the metric
}

/**
 * D3-based Serve Timeline Chart
 * 
 * Key Features:
 * - Point radius = Opponent rank (bigger = tougher opponent)
 * - Multiple metrics can be displayed
 * - Interactive tooltips
 * - Responsive design
 */
export const D3ServeTimeline: React.FC<D3ServeTimelineProps> = ({
  data,
  metrics, // New: array of metrics
  metric, // Backward compat: single metric
  showOpponentComparison = false,
  height = 500,
}) => {
  // Determine which metrics to display
  const metricsToDisplay = useMemo(
    () => metrics || (metric ? [metric] : ['player_1stIn', 'player_1stWon', 'player_2ndWon']),
    [metrics, metric]
  );
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<{
    x: number;
    y: number;
    match: RawServeMatch | null;
    value: number | null;
    metricLabel: string;
    metricKey: string;
  } | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: height });

  // Calculate point radius based on opponent rank
  const getRadius = useCallback((rank: number | null | undefined): number => {
    if (rank === null || rank === undefined) return 3; // Tiny for unknown
    if (rank <= 5) return 12;   // Massive for Top 5
    if (rank <= 10) return 10;  // Very Big for Top 10
    if (rank <= 50) return 7;   // Big for Top 50
    if (rank <= 100) return 5;  // Normal for Top 100
    return 3; // Small for 100+
  }, []);

  // Color scheme for different metrics
  const getColor = useCallback((metricType: string, isOpponent: boolean = false): string => {
    if (isOpponent) {
      const colors: Record<string, string> = {
        'player_1stIn': '#60A5FA', // Light blue
        'player_1stWon': '#F87171', // Light red
        'player_2ndWon': '#A78BFA', // Light purple
      };
      return colors[metricType] || '#94A3B8';
    }
    const colors: Record<string, string> = {
      'player_1stIn': '#0066FF', // Bright blue
      'player_1stWon': '#FF3300', // Bright red
      'player_2ndWon': '#9933FF', // Bright purple
    };
    return colors[metricType] || '#000000';
  }, []);

  // Get metric label
  const getMetricLabel = useCallback((metricKey: string): string => {
    const labels: Record<string, string> = {
      'player_1stIn': '1st Serve In %',
      'player_1stWon': '1st Serve Won %',
      'player_2ndWon': '2nd Serve Won %',
      'opponent_1stIn': 'Opponent 1st In %',
      'opponent_1stWon': 'Opponent 1st Won %',
      'opponent_2ndWon': 'Opponent 2nd Won %',
    };
    return labels[metricKey] || metricKey;
  }, []);

  // Transform data into chart points
  const transformData = useCallback((): ChartPoint[] => {
    const points: ChartPoint[] = [];
    
    // Process each metric
    metricsToDisplay.forEach((metricKey) => {
      // Player metrics
      data.forEach((match, index) => {
        const value = match[metricKey as keyof RawServeMatch];
        if (value !== null && value !== undefined) {
          points.push({
            x: index + 1,
            y: typeof value === 'number' ? value : Number(value) || 0,
            radius: getRadius(match.opponent_rank),
            match,
            color: getColor(metricKey, false),
            metricLabel: getMetricLabel(metricKey),
            metricKey: metricKey,
          });
        }
      });

      // Opponent metrics (if enabled)
      if (showOpponentComparison) {
        const opponentMetric = metricKey.replace('player_', 'opponent_') as keyof RawServeMatch;
        data.forEach((match, index) => {
          const value = match[opponentMetric];
          if (value !== null && value !== undefined) {
            points.push({
              x: index + 1,
              y: typeof value === 'number' ? value : Number(value) || 0,
              radius: getRadius(match.opponent_rank),
              match,
              color: getColor(metricKey, true),
              metricLabel: getMetricLabel(opponentMetric),
              metricKey: opponentMetric,
            });
          }
        });
      }
    });

    return points;
  }, [data, metricsToDisplay, showOpponentComparison, getRadius, getColor, getMetricLabel]);

  // Render chart
  useEffect(() => {
    if (!svgRef.current || !containerRef.current || data.length === 0 || dimensions.width === 0) return;

    const svg = d3.select(svgRef.current);
    const width = dimensions.width;
    const margin = { top: 20, right: 50, bottom: 60, left: 70 };

    // Clear previous render
    svg.selectAll('*').remove();

    // Set up dimensions
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create main group
    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Transform data
    const points = transformData();
    if (points.length === 0) return;

    // Create scales
    const xScale = d3
      .scaleLinear()
      .domain([1, d3.max(points, d => d.x) || 1])
      .range([0, innerWidth]);

    const yScale = d3
      .scaleLinear()
      .domain([0, 100])
      .range([innerHeight, 0]);

    // Create axes
    const xAxis = d3.axisBottom(xScale).ticks(Math.min(20, points.length));
    const yAxis = d3.axisLeft(yScale).ticks(10);

    // Add X axis
    const xAxisGroup = g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis);

    // Style X axis ticks and line
    xAxisGroup.selectAll('text')
      .style('fill', '#374151')
      .style('font-size', '11px');
    
    xAxisGroup.selectAll('line, path')
      .style('stroke', '#9CA3AF')
      .style('stroke-width', 1);

    // Add X axis label (separate from axis group for better positioning)
    g.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', innerHeight + 40)
      .attr('fill', '#374151')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', '500')
      .text('Match Number');

    // Add Y axis
    const yAxisGroup = g.append('g')
      .call(yAxis);

    // Style Y axis ticks and line
    yAxisGroup.selectAll('text')
      .style('fill', '#374151')
      .style('font-size', '11px');
    
    yAxisGroup.selectAll('line, path')
      .style('stroke', '#9CA3AF')
      .style('stroke-width', 1);

    // Add Y axis label (separate from axis group for better positioning)
    g.append('text')
      .attr('transform', `rotate(-90)`)
      .attr('y', -55)
      .attr('x', -innerHeight / 2)
      .attr('fill', '#374151')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', '500')
      .text('Percentage (%)');

    // Add vertical background lines (from y=0 to max value at each match)
    // Similar to NivoTimeline's verticalLinesLayer - helps visualize data range per match
    const verticalLinesData: Array<{ x: number; maxY: number }> = [];
    const xPositions = new Set<number>();
    
    // Find all unique x positions
    points.forEach(point => {
      xPositions.add(point.x);
    });
    
    // Calculate max Y value at each x position
    Array.from(xPositions).sort((a, b) => a - b).forEach(x => {
      const pointsAtX = points.filter(p => p.x === x);
      if (pointsAtX.length > 0) {
        const maxY = Math.max(...pointsAtX.map(p => p.y));
        verticalLinesData.push({ x, maxY });
      }
    });
    
    // Draw vertical lines (behind data points)
    g.append('g')
      .attr('class', 'vertical-lines')
      .selectAll('line')
      .data(verticalLinesData)
      .enter()
      .append('line')
      .attr('x1', d => xScale(d.x))
      .attr('x2', d => xScale(d.x))
      .attr('y1', yScale(0))
      .attr('y2', d => yScale(d.maxY))
      .attr('stroke', '#9CA3AF')
      .attr('stroke-width', 0.8)
      .attr('opacity', 0.3)
      .style('pointer-events', 'none');

    // Add grid lines (without duplicate tick labels)
    const xGrid = g.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(
        d3
          .axisBottom(xScale)
          .ticks(Math.min(20, points.length))
          .tickSize(-innerHeight)
          .tickFormat(() => '') // hide tick labels on grid axis
      );

    xGrid.selectAll('line')
      .attr('stroke', '#E5E7EB')
      .attr('stroke-width', 0.5)
      .attr('opacity', 0.5);

    xGrid.selectAll('path')
      .attr('stroke', 'none');

    const yGrid = g.append('g')
      .attr('class', 'grid')
      .call(
        d3
          .axisLeft(yScale)
          .ticks(10)
          .tickSize(-innerWidth)
          .tickFormat(() => '') // hide tick labels on grid axis
      );

    yGrid.selectAll('line')
      .attr('stroke', '#E5E7EB')
      .attr('stroke-width', 0.5)
      .attr('opacity', 0.5);

    yGrid.selectAll('path')
      .attr('stroke', 'none');

    // Draw points
    const circles = g
      .selectAll('circle')
      .data(points)
      .enter()
      .append('circle')
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .attr('r', d => d.radius)
      .attr('fill', d => d.color)
      .attr('stroke', '#FFFFFF')
      .attr('stroke-width', 2)
      .attr('opacity', 0.8)
      .style('cursor', 'pointer');

    // Add hover interactions
    circles
      .on('mouseenter', function (event, d) {
        d3.select(this).attr('opacity', 1).attr('stroke-width', 3);
        const rect = containerRef.current?.getBoundingClientRect();
        if (rect) {
          setTooltip({
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
            match: d.match,
            value: d.y,
            metricLabel: d.metricLabel,
            metricKey: d.metricKey,
          });
        }
      })
      .on('mousemove', function (event) {
        const rect = containerRef.current?.getBoundingClientRect();
        if (rect) {
          setTooltip(prev => 
            prev ? { 
              ...prev, 
              x: event.clientX - rect.left, 
              y: event.clientY - rect.top 
            } : null
          );
        }
      })
      .on('mouseleave', function () {
        d3.select(this).attr('opacity', 0.8).attr('stroke-width', 2);
        setTooltip(null);
      });

    // Cleanup function
    return () => {
      svg.selectAll('*').remove();
    };
  }, [data, metricsToDisplay, showOpponentComparison, dimensions, transformData, height]);

  // Handle container resize
  useEffect(() => {
    if (!containerRef.current) return;

    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: height,
        });
      }
    };

    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(containerRef.current);
    updateDimensions(); // Initial measurement

    return () => resizeObserver.disconnect();
  }, [height]);

  return (
    <div className="relative w-full">
      {/* Legend - Metrics (Bottom) */}
      <div className="absolute top left-1/2 transform -translate-x-1/2 bg-white/90 p-0.5 rounded-lg text-xs text-gray-600 border border-gray-200 z-10 shadow-sm">
        <div className="flex items-center gap-4 justify-center flex-wrap">
          {metricsToDisplay.map((metricKey) => (
            <div key={metricKey} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getColor(metricKey, false) }}
              ></div>
              <span>{getMetricLabel(metricKey)}</span>
            </div>
          ))}
          {showOpponentComparison && metricsToDisplay.map((metricKey) => {
            const opponentKey = metricKey.replace('player_', 'opponent_');
            return (
              <div key={opponentKey} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: getColor(metricKey, true) }}
                ></div>
                <span>{getMetricLabel(opponentKey)}</span>
              </div>
            );
          })}
        </div>
      </div>


      {/* Chart Container */}
      <div ref={containerRef} className="w-full">
        <svg
          ref={svgRef}
          width="100%"
          height={height}
          style={{ display: 'block' }}
        />
      </div>

      {/* Tooltip */}
      {tooltip && tooltip.match && (
        <div
          className="absolute bg-white p-3 border border-gray-200 rounded-lg shadow-lg text-xs min-w-[200px] z-50 pointer-events-none"
          style={{
            left: `${tooltip.x + 15}px`,
            top: `${tooltip.y - 15}px`,
            transform: 'translateY(-100%)',
            maxWidth: '300px',
          }}
        >
          <div className="flex justify-between items-center mb-2 border-b border-gray-100 pb-2">
            <span className="font-bold text-gray-800">Match #{tooltip.match.match_index + 1}</span>
            <span
              className={`font-bold px-2 py-0.5 rounded ${
                tooltip.match.result === 'W' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}
            >
              {tooltip.match.result}
            </span>
          </div>
          <div className="mb-2">
            <span className="text-gray-500">vs </span>
            <span className="font-semibold text-gray-800 text-sm">{tooltip.match.opponent}</span>
            <span className="ml-2 px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-[10px] font-mono border border-gray-300">
              #{tooltip.match.opponent_rank ?? 'N/A'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 mb-2 text-gray-600">
            <div>
              <span className="text-gray-400">Tourney:</span> {tooltip.match.tourney_name}
            </div>
            <div>
              <span className="text-gray-400">Year:</span> {tooltip.match.year}
            </div>
            <div>
              <span className="text-gray-400">Surf:</span> {tooltip.match.surface}
            </div>
            <div>
              <span className="text-gray-400">Rd:</span> {tooltip.match.round}
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="font-bold text-sm" style={{ color: getColor(tooltip.metricKey, tooltip.metricKey.startsWith('opponent_')) }}>
              {tooltip.metricLabel}: {tooltip.value !== null ? `${tooltip.value.toFixed(2)}%` : 'N/A'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

