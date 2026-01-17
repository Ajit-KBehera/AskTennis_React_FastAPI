import React from 'react';
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface DataVisualizerProps {
    data: any[];
}

export const DataVisualizer: React.FC<DataVisualizerProps> = ({ data }) => {
    if (!data || data.length === 0) return null;

    // 1. Analyze Columns
    const columns = Object.keys(data[0]);

    const dateKeys: string[] = [];
    const categoricalKeys: string[] = [];
    const numericKeys: string[] = [];

    // Simple heuristics to classify columns
    columns.forEach(col => {
        const sampleValue = data[0][col];
        const lowerCol = col.toLowerCase();

        // Check for Numeric
        if (typeof sampleValue === 'number' && !lowerCol.includes('id') && !lowerCol.includes('year')) {
            numericKeys.push(col);
            return;
        }

        // Check for Date/Year (treat as categorical X-axis but conceptually time)
        if (
            lowerCol.includes('date') ||
            lowerCol.includes('year') ||
            lowerCol.includes('time') ||
            /^\d{4}$/.test(String(sampleValue)) // looks like a year "2023"
        ) {
            dateKeys.push(col);
            return;
        }

        // Check for Categorical (String)
        if (typeof sampleValue === 'string') {
            categoricalKeys.push(col);
            return;
        }

        // Treat numbers that look like years as dates if we missed them above
        if (typeof sampleValue === 'number' && (lowerCol.includes('year') || (sampleValue > 1900 && sampleValue < 2100))) {
            dateKeys.push(col);
            return;
        }
    });

    // 2. Decide Chart Type

    // Scenario A: Time Series (Line Chart)
    // Requirements: 1 Date Key (X-axis) + At least 1 Numeric Key (Y-axis)
    if (dateKeys.length === 1 && numericKeys.length > 0) {
        const xKey = dateKeys[0];

        // Sort data by date just in case
        const sortedData = [...data].sort((a, b) => {
            const valA = a[xKey];
            const valB = b[xKey];
            // Simple string/number compare
            return valA < valB ? -1 : valA > valB ? 1 : 0;
        });

        return (
            <div className="w-full h-80 min-h-[320px] mb-6 p-4 glass-panel rounded-xl flex flex-col">
                <h3 className="text-emerald-400 text-xs font-bold uppercase tracking-wider mb-4 flex-none">
                    📈 Trend Analysis
                </h3>
                <div className="flex-1 w-full min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={sortedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                            <XAxis
                                dataKey={xKey}
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#e2e8f0' }}
                                itemStyle={{ color: '#e2e8f0' }}
                            />
                            <Legend />
                            {numericKeys.slice(0, 3).map((key, index) => (
                                <Line
                                    key={key}
                                    type="monotone"
                                    dataKey={key}
                                    stroke={getThemeColor(index)}
                                    strokeWidth={2}
                                    dot={{ fill: getThemeColor(index) }}
                                    activeDot={{ r: 8 }}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }

    // Scenario B: Categorical Comparison (Bar Chart)
    // Requirements: 1 Categorical Key (X-axis names) + At least 1 Numeric Key (Y-axis values)
    if (categoricalKeys.length > 0 && numericKeys.length > 0) {
        // Prioritize "name", "player", "tournament" as primary categorical key
        const xKey = categoricalKeys.find(k =>
            ['name', 'player', 'tournament', 'opponent'].some(term => k.toLowerCase().includes(term))
        ) || categoricalKeys[0];

        return (
            <div className="w-full h-80 min-h-[320px] mb-6 p-4 glass-panel rounded-xl flex flex-col">
                <h3 className="text-amber-400 text-xs font-bold uppercase tracking-wider mb-4 flex-none">
                    📊 Comparative Analysis
                </h3>
                <div className="flex-1 w-full min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                            <XAxis
                                dataKey={xKey}
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                interval={0}
                                angle={data.length > 10 ? -45 : 0}
                                textAnchor={data.length > 10 ? 'end' : 'middle'}
                                height={data.length > 10 ? 60 : 30}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <Tooltip
                                cursor={{ fill: '#ffffff05' }}
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#e2e8f0' }}
                            />
                            <Legend />
                            {numericKeys.slice(0, 2).map((key, index) => (
                                <Bar
                                    key={key}
                                    dataKey={key}
                                    fill={getThemeColor(index)}
                                    radius={[4, 4, 0, 0]}
                                />
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }

    // Fallback: No chart, just return null (AiResponseView will still show the table)
    return null;
};

// Start with Emerald, then Sky, then Amber
const COLORS = ['#34d399', '#38bdf8', '#fbbf24', '#f87171', '#a78bfa'];
const getThemeColor = (index: number) => COLORS[index % COLORS.length];
