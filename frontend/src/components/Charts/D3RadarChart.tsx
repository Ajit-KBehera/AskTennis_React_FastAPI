import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import type { RawServeMatch } from '../../types';

interface RadarStats {
  '1st Serve %': number;
  '1st Serve Won %': number;
  '2nd Serve Won %': number;
}

interface D3RadarChartProps {
  data: RawServeMatch[];
  playerName: string;
  opponentStats?: RadarStats | null;
  opponentName?: string;
  height?: number;
}

/**
 * D3-based Radar/Spider Chart for Serve Statistics
 * 
 * Displays 3 metrics in a circular polar chart:
 * - 1st Serve %
 * - 1st Serve Won %
 * - 2nd Serve Won %
 */
export const D3RadarChart: React.FC<D3RadarChartProps> = ({
  data,
  playerName,
  opponentStats = null,
  opponentName,
  height = 500,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: height });

  // Calculate aggregated stats from raw match data
  const calculateStats = useCallback((matches: RawServeMatch[]): RadarStats => {
    const stats: RadarStats = {
      '1st Serve %': 0,
      '1st Serve Won %': 0,
      '2nd Serve Won %': 0,
    };

    // Filter out null values and calculate averages
    const valid1stIn = matches.filter(m => m.player_1stIn !== null).map(m => m.player_1stIn!);
    const valid1stWon = matches.filter(m => m.player_1stWon !== null).map(m => m.player_1stWon!);
    const valid2ndWon = matches.filter(m => m.player_2ndWon !== null).map(m => m.player_2ndWon!);

    if (valid1stIn.length > 0) {
      stats['1st Serve %'] = valid1stIn.reduce((a, b) => a + b, 0) / valid1stIn.length;
    }
    if (valid1stWon.length > 0) {
      stats['1st Serve Won %'] = valid1stWon.reduce((a, b) => a + b, 0) / valid1stWon.length;
    }
    if (valid2ndWon.length > 0) {
      stats['2nd Serve Won %'] = valid2ndWon.reduce((a, b) => a + b, 0) / valid2ndWon.length;
    }

    return stats;
  }, []);

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
    updateDimensions();

    return () => resizeObserver.disconnect();
  }, [height]);

  // Render chart
  useEffect(() => {
    if (!svgRef.current || !containerRef.current || data.length === 0 || dimensions.width === 0) return;

    const svg = d3.select(svgRef.current);
    const width = dimensions.width;
    const size = Math.min(width, height);
    const radius = (size - 100) / 2; // Leave space for labels
    const centerX = width / 2;
    const centerY = height / 2;

    // Clear previous render
    svg.selectAll('*').remove();

    // Calculate stats
    const playerStats = calculateStats(data);
    const categories = Object.keys(playerStats);
    const maxValue = 100; // Radar chart uses 0-100 scale

    // Calculate angles for each category (distribute evenly around circle)
    // Start at top (12 o'clock) and go clockwise
    const getAngle = (index: number): number => {
      const angleStep = (2 * Math.PI) / categories.length;
      return (index * angleStep) - (Math.PI / 2); // Start at top
    };

    // Create radius scale (0 to maxValue maps to 0 to radius)
    const radiusScale = d3.scaleLinear()
      .domain([0, maxValue])
      .range([0, radius]);

    // Create main group
    const g = svg.append('g')
      .attr('transform', `translate(${centerX},${centerY})`);

    // Draw concentric circles (grid lines)
    const gridLevels = [20, 40, 60, 80, 100];
    gridLevels.forEach((level) => {
      g.append('circle')
        .attr('r', radiusScale(level))
        .attr('fill', 'none')
        .attr('stroke', '#E5E7EB')
        .attr('stroke-width', 1)
        .attr('opacity', 0.5);
    });

    // Draw axis lines (spokes)
    categories.forEach((category, index) => {
      const angle = getAngle(index);
      const x = radius * Math.sin(angle);
      const y = -radius * Math.cos(angle); // Negative because SVG Y increases downward

      g.append('line')
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', x)
        .attr('y2', y)
        .attr('stroke', '#D1D5DB')
        .attr('stroke-width', 1)
        .attr('opacity', 0.5);

      // Add category labels
      const labelRadius = radius + 35;
      const labelX = labelRadius * Math.sin(angle);
      const labelY = -labelRadius * Math.cos(angle);

      g.append('text')
        .attr('x', labelX)
        .attr('y', labelY)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('fill', '#374151')
        .style('font-size', '11px')
        .style('font-weight', '500')
        .text(category);
    });

    // Draw value labels on axes
    gridLevels.forEach((level) => {
      if (level > 0 && level % 20 === 0) {
        g.append('text')
          .attr('x', radiusScale(level) * Math.sin(0) + 5)
          .attr('y', -radiusScale(level) * Math.cos(0) - 5)
          .attr('fill', '#9CA3AF')
          .style('font-size', '10px')
          .text(`${level}%`);
      }
    });

    // Helper function to create path for radar area
    const createRadarPath = (stats: RadarStats, color: string, opacity: number, isDashed: boolean = false) => {
      const pathData = categories.map((category, index) => {
        const value = stats[category as keyof RadarStats];
        const r = radiusScale(value);
        const angle = getAngle(index);
        const x = r * Math.sin(angle);
        const y = -r * Math.cos(angle);
        return [x, y];
      });

      // Close the path
      pathData.push(pathData[0]);

      const line = d3.line<[number, number]>()
        .x(d => d[0])
        .y(d => d[1])
        .curve(d3.curveLinearClosed);

      return { path: line(pathData) || '', pathData };
    };

    // Draw player radar area
    const playerPath = createRadarPath(playerStats, '#3B82F6', 0.3);
    g.append('path')
      .attr('d', playerPath.path)
      .attr('fill', '#3B82F6')
      .attr('fill-opacity', 0.3)
      .attr('stroke', '#3B82F6')
      .attr('stroke-width', 2)
      .attr('opacity', 0.7);

    // Draw player data points
    categories.forEach((category, index) => {
      const value = playerStats[category as keyof RadarStats];
      const r = radiusScale(value);
      const angle = getAngle(index);
      const x = r * Math.sin(angle);
      const y = -r * Math.cos(angle);

      g.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 4)
        .attr('fill', '#3B82F6')
        .attr('stroke', '#FFFFFF')
        .attr('stroke-width', 2);
    });

    // Draw opponent radar area if provided
    if (opponentStats) {
      const opponentPath = createRadarPath(opponentStats, '#EF4444', 0.2);
      g.append('path')
        .attr('d', opponentPath.path)
        .attr('fill', '#EF4444')
        .attr('fill-opacity', 0.2)
        .attr('stroke', '#EF4444')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.5);

      // Draw opponent data points
      categories.forEach((category, index) => {
        const value = opponentStats[category as keyof RadarStats];
        const r = radiusScale(value);
        const angle = getAngle(index);
        const x = r * Math.sin(angle);
        const y = -r * Math.cos(angle);

        g.append('circle')
          .attr('cx', x)
          .attr('cy', y)
          .attr('r', 4)
          .attr('fill', '#EF4444')
          .attr('stroke', '#FFFFFF')
          .attr('stroke-width', 2);
      });
    }

    // Cleanup function
    return () => {
      svg.selectAll('*').remove();
    };
  }, [data, playerName, opponentStats, opponentName, dimensions, calculateStats, height]);

  return (
    <div className="relative w-full">
      {/* Chart Container */}
      <div ref={containerRef} className="w-full flex justify-center">
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={height}
          style={{ display: 'block' }}
        />
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500"></div>
          <span className="text-sm text-gray-700">{playerName}</span>
        </div>
        {opponentStats && opponentName && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span className="text-sm text-gray-700">{opponentName}</span>
          </div>
        )}
      </div>
    </div>
  );
};

