
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

export const createServeTimelineChart = (matches: any[], playerName: string): ChartConfig => {
    const indices = matches.map((_, i) => i);
    const firstServeIn = matches.map(m => m.player_1stIn);
    const firstServeWon = matches.map(m => m.player_1stWon);
    const secondServeWon = matches.map(m => m.player_2ndWon);

    const cleanIn = filterNulls(indices, firstServeIn);
    const cleanWon = filterNulls(indices, firstServeWon);
    const cleanSecondWon = filterNulls(indices, secondServeWon);

    return {
        data: [
            {
                x: cleanIn.dates, // dates is actually indices here
                y: cleanIn.values,
                type: 'scatter',
                mode: 'markers',
                name: '1st Serve In %',
                line: { color: '#2563EB', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(37, 99, 235, 0.1)'
            },
            {
                x: cleanWon.dates,
                y: cleanWon.values,
                type: 'scatter',
                mode: 'markers',
                name: '1st Serve Won %',
                line: { color: '#10B981', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(16, 185, 129, 0.1)'
            },
            {
                x: cleanSecondWon.dates,
                y: cleanSecondWon.values,
                type: 'scatter',
                mode: 'markers',
                name: '2nd Serve Won %',
                line: { color: '#F59E0B', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(245, 158, 11, 0.1)'
            }
        ],
        layout: {
            title: { text: 'Serve Performance' },
            xaxis: { title: { text: 'Match Number' } },
            yaxis: { title: { text: 'Percentage (%)' }, range: [0, 100] },
            legend: { orientation: 'h', y: -0.2 },
            hovermode: 'x unified'
        }
    };
};

export const createAceDfChart = (matches: any[], playerName: string): ChartConfig => {
    const indices = matches.map((_, i) => i);
    const aceRate = matches.map(m => m.player_ace_rate);
    const dfRate = matches.map(m => m.player_df_rate);

    const cleanAce = filterNulls(indices, aceRate);
    const cleanDf = filterNulls(indices, dfRate);

    return {
        data: [
            {
                x: cleanAce.dates,
                y: cleanAce.values,
                type: 'scatter',
                mode: 'markers',
                name: 'Ace Rate',
                line: { color: '#8B5CF6', width: 2 },
                fill: 'tozeroy',
                fillcolor: 'rgba(139, 92, 246, 0.1)'
            },
            {
                x: cleanDf.dates,
                y: cleanDf.values,
                type: 'scatter',
                mode: 'markers',
                name: 'Double Fault Rate',
                line: { color: '#EF4444', width: 2 },
                fill: 'tozeroy',
                fillcolor: 'rgba(239, 68, 68, 0.1)'
            }
        ],
        layout: {
            title: { text: 'Ace vs Double Fault Rate' },
            xaxis: { title: { text: 'Match Number' } },
            yaxis: { title: { text: 'Rate (%)' } },
            legend: { orientation: 'h', y: -0.2 },
            hovermode: 'x unified'
        }
    };
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

export const createReturnPointsChart = (matches: any[], playerName: string): ChartConfig => {
    const indices = matches.map((_, i) => i);
    const returnPointsWon = matches.map(m => m.player_return_points_won_pct);

    const cleanData = filterNulls(indices, returnPointsWon);

    return {
        data: [
            {
                x: cleanData.dates,
                y: cleanData.values,
                type: 'scatter',
                mode: 'markers',
                name: 'Return Points Won %',
                hovertemplate: '<b>%{fullData.name}</b>: %{y}%<extra></extra>',
                line: { color: '#F59E0B', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(245, 158, 11, 0.1)'
            }
        ],
        layout: {
            title: { text: 'Return Points Won' },
            xaxis: { title: { text: 'Match Number' } },
            yaxis: { title: { text: 'Percentage (%)' }, range: [0, 100] },
            hovermode: 'x unified'
        }
    };
};

export const createBpConversionChart = (matches: any[], playerName: string): ChartConfig => {
    const indices = matches.map((_, i) => i);
    const bpConversion = matches.map(m => m.player_bpConversion_pct);

    const cleanData = filterNulls(indices, bpConversion);

    return {
        data: [
            {
                x: cleanData.dates,
                y: cleanData.values,
                type: 'scatter',
                mode: 'markers',
                name: 'BP Conversion %',
                hovertemplate: '<b>%{fullData.name}</b>: %{y}%<extra></extra>',
                line: { color: '#10B981', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(16, 185, 129, 0.1)'
            }
        ],
        layout: {
            title: { text: 'Break Point Conversion Rate' },
            xaxis: { title: { text: 'Match Number' } },
            yaxis: { title: { text: 'Percentage (%)' }, range: [0, 100] },
            hovermode: 'x unified'
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
export const createBpSavedChart = (matches: any[], playerName: string): ChartConfig => {
    const indices = matches.map((_, i) => i);
    const bpFaced = matches.map(m => m.player_bpFaced);
    const bpSaved = matches.map(m => m.player_bpSaved);

    const cleanFaced = filterNulls(indices, bpFaced);
    const cleanSaved = filterNulls(indices, bpSaved);

    return {
        data: [
            {
                x: cleanFaced.dates,
                y: cleanFaced.values,
                type: 'scatter',
                mode: 'markers',
                name: 'BPs Faced',
                line: { color: '#EF4444', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(239, 68, 68, 0.1)'
            },
            {
                x: cleanSaved.dates,
                y: cleanSaved.values,
                type: 'scatter',
                mode: 'markers',
                name: 'BPs Saved',
                line: { color: '#10B981', width: 2 },
                marker: { size: 6 },
                fill: 'tozeroy',
                fillcolor: 'rgba(16, 185, 129, 0.1)'
            }
        ],
        layout: {
            title: { text: 'Break Points Faced vs Saved' },
            xaxis: { title: { text: 'Match Number' } },
            yaxis: { title: { text: 'Count' }, rangemode: 'nonnegative' },
            legend: { orientation: 'h', y: -0.2 },
            hovermode: 'x unified'
        }
    };
};
