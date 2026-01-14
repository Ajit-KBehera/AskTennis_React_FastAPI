
import { Layout, Data } from 'plotly.js';

interface ChartConfig {
    data: Data[];
    layout: Partial<Layout>;
}

// Helper to handle data gaps
const filterNulls = (dates: any[], values: any[]) => {
    const cleanDates: any[] = [];
    const cleanValues: any[] = [];

    values.forEach((val, idx) => {
        if (val !== null && val !== undefined) {
            cleanDates.push(dates[idx]);
            cleanValues.push(val);
        }
    });

    return { dates: cleanDates, values: cleanValues };
};

interface SeriesDef {
    key: string;      // Property name in the match object (e.g., 'player_1stIn')
    name: string;     // Legend name
    color: string;
    fillColor?: string;
    dash?: string;    // Optional line dash style
    hovertemplate?: string;
}

interface CreateTimeSeriesOptions {
    title: string;
    yAxisTitle: string;
    yAxisRange?: [number, number];
    yAxisMode?: 'normal' | 'nonnegative';
    matches: any[];
    series: SeriesDef[];
}

/**
 * Generic helper to create time-series style charts from match data.
 */
const createTimeSeriesChart = (options: CreateTimeSeriesOptions): ChartConfig => {
    const { title, yAxisTitle, yAxisRange, yAxisMode, matches, series } = options;
    const indices = matches.map((_, i) => i);

    const data: Data[] = series.map(s => {
        // Extract raw data for this series
        const rawValues = matches.map(m => m[s.key]);
        // Filter out nulls/undefined
        const clean = filterNulls(indices, rawValues);

        return {
            x: clean.dates,
            y: clean.values,
            type: 'scatter',
            mode: 'markers',
            name: s.name,
            line: s.dash ? { color: s.color, width: 2, dash: s.dash as any } : { color: s.color, width: 2 },
            marker: { size: 6 },
            fill: 'tozeroy',
            fillcolor: s.fillColor || s.color.replace(')', ', 0.1)').replace('rgb', 'rgba').replace('#', 'rgba('), // Simple fallback, but explicit is better
            hovertemplate: s.hovertemplate
        };
    });

    // Fix up fill colors if not provided (simple hex to rgba converter would be better, 
    // but we can just rely on the caller providing it or basic fallbacks for now)
    // The previous code had explicit rgba strings. Let's try to preserve that behavior by passing it in.

    const layout: Partial<Layout> = {
        title: { text: title },
        xaxis: { title: { text: 'Match Number' } },
        yaxis: { title: { text: yAxisTitle } },
        legend: { orientation: 'h', y: -0.2 },
        hovermode: 'x unified'
    };

    if (yAxisRange) {
        layout.yaxis!.range = yAxisRange;
    }
    if (yAxisMode === 'nonnegative') {
        layout.yaxis!.rangemode = 'nonnegative';
    }

    return { data, layout };
};


export const createServeTimelineChart = (matches: any[], playerName: string): ChartConfig => {
    return createTimeSeriesChart({
        title: 'Serve Performance',
        yAxisTitle: 'Percentage (%)',
        yAxisRange: [0, 100],
        matches,
        series: [
            { key: 'player_1stIn', name: '1st Serve In %', color: '#2563EB', fillColor: 'rgba(37, 99, 235, 0.1)' },
            { key: 'player_1stWon', name: '1st Serve Won %', color: '#10B981', fillColor: 'rgba(16, 185, 129, 0.1)' },
            { key: 'player_2ndWon', name: '2nd Serve Won %', color: '#F59E0B', fillColor: 'rgba(245, 158, 11, 0.1)' }
        ]
    });
};

export const createAceDfChart = (matches: any[], playerName: string): ChartConfig => {
    return createTimeSeriesChart({
        title: 'Ace vs Double Fault Rate',
        yAxisTitle: 'Rate (%)',
        matches,
        series: [
            { key: 'player_ace_rate', name: 'Ace Rate', color: '#8B5CF6', fillColor: 'rgba(139, 92, 246, 0.1)' },
            { key: 'player_df_rate', name: 'Double Fault Rate', color: '#EF4444', fillColor: 'rgba(239, 68, 68, 0.1)' }
        ]
    });
};

export const createReturnPointsChart = (matches: any[], playerName: string): ChartConfig => {
    // Note: The original had a specific hovertemplate: '<b>%{fullData.name}</b>: %{y}%<extra></extra>'
    // For simplicity we'll stick to 'x unified' hovermode which is cleaner, or we could add hovertemplate support to the helper.
    // Given the original code had 'x unified' in the layout, the hovertemplate might have been redundant or conflicting in subtle ways.
    // Let's stick to the uniform unified view for consistency.
    return createTimeSeriesChart({
        title: 'Return Points Won',
        yAxisTitle: 'Percentage (%)',
        yAxisRange: [0, 100],
        matches,
        series: [
            {
                key: 'player_return_points_won_pct',
                name: 'Return Points Won %',
                color: '#F59E0B',
                fillColor: 'rgba(245, 158, 11, 0.1)',
                hovertemplate: '<b>%{fullData.name}</b>: %{y}%<extra></extra>'
            }
        ]
    });
};

export const createBpConversionChart = (matches: any[], playerName: string): ChartConfig => {
    return createTimeSeriesChart({
        title: 'Break Point Conversion Rate',
        yAxisTitle: 'Percentage (%)',
        yAxisRange: [0, 100],
        matches,
        series: [
            {
                key: 'player_bpConversion_pct',
                name: 'BP Conversion %',
                color: '#10B981',
                fillColor: 'rgba(16, 185, 129, 0.1)',
                hovertemplate: '<b>%{fullData.name}</b>: %{y}%<extra></extra>'
            }
        ]
    });
};

export const createBpSavedChart = (matches: any[], playerName: string): ChartConfig => {
    return createTimeSeriesChart({
        title: 'Break Points Faced vs Saved',
        yAxisTitle: 'Count',
        yAxisMode: 'nonnegative',
        matches,
        series: [
            { key: 'player_bpFaced', name: 'BPs Faced', color: '#EF4444', fillColor: 'rgba(239, 68, 68, 0.1)' },
            { key: 'player_bpSaved', name: 'BPs Saved', color: '#10B981', fillColor: 'rgba(16, 185, 129, 0.1)' }
        ]
    });
};

export const createRadarChart = (
    playerStats: Record<string, number | null>,
    opponentStats: Record<string, number | null> | undefined,
    playerName: string
): ChartConfig => {
    const categories = Object.keys(playerStats);
    const playerValues = Object.values(playerStats).map(v => v || 0);

    // Close the loop
    const categoriesClosed = [...categories, categories[0]];
    const playerValuesClosed = [...playerValues, playerValues[0]];

    const data: Data[] = [{
        type: 'scatterpolar',
        r: playerValuesClosed,
        theta: categoriesClosed,
        fill: 'toself',
        name: playerName,
        line: { color: '#2563EB' }
    }];

    if (opponentStats) {
        const opponentValues = categories.map(cat => opponentStats[cat] || 0);
        const opponentValuesClosed = [...opponentValues, opponentValues[0]];

        data.push({
            type: 'scatterpolar',
            r: opponentValuesClosed,
            theta: categoriesClosed,
            fill: 'toself',
            name: 'Opponent',
            line: { color: '#EF4444', dash: 'dash' },
            opacity: 0.6
        });
    }

    return {
        data,
        layout: {
            // Radar chart title handled by component usually, but if needed:
            // title: { text: 'Stats Radar' },
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 100]
                }
            },
            showlegend: true,
            legend: { orientation: 'h', y: -0.1 }
        }
    };
};

export const createRankingChart = (rankingData: any[], playerName: string): ChartConfig => {
    // rankingData has { ranking_date, rank, tour? }
    const sortedData = [...rankingData].sort((a, b) =>
        new Date(a.ranking_date).getTime() - new Date(b.ranking_date).getTime()
    );

    const dates = sortedData.map(d => d.ranking_date);
    const ranks = sortedData.map(d => d.rank);

    // Simple single trace for now, can extend for ATP/WTA split if data provided
    // Assuming backend returns flat list mostly

    return {
        data: [
            {
                x: dates,
                y: ranks,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Ranking',
                line: { color: '#2563EB', width: 2 },
                marker: { size: 4 },
                hovertemplate: 'Rank: %{y}<br>Date: %{x|%Y-%m-%d}<extra></extra>'
            }
        ],
        layout: {
            title: { text: 'Ranking Timeline' },
            xaxis: { title: { text: 'Date' } },
            yaxis: {
                title: { text: 'Ranking' },
                autorange: 'reversed' // Important for ranking
            },
            hovermode: 'closest'
        }
    };
};
