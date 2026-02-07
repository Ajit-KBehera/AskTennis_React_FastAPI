import React from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

interface DataTableProps {
    data: any[];
    maxHeight?: number;
}

export const DataTable: React.FC<DataTableProps> = ({ data, maxHeight = 400 }) => {
    if (!data || data.length === 0) {
        return (
            <div className="h-40 flex items-center justify-center text-slate-500">
                No data available.
            </div>
        );
    }

    // Extract column headers from first row
    const columns = Object.keys(data[0]);
    const columnCount = columns.length;

    // Calculate column width (equal distribution)
    const columnWidth = `${100 / columnCount}%`;

    const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
        const row = data[index];
        const bgClass = index % 2 === 0 ? "bg-white/0" : "bg-white/[0.02]";

        return (
            <div style={style} className={`flex items-center border-b border-white/5 text-sm text-slate-300 ${bgClass} hover:bg-white/5 transition-colors`}>
                {columns.map((col, colIndex) => {
                    const value = row[col];
                    const displayValue = value === null || value === undefined ? '-' : String(value);

                    return (
                        <div
                            key={colIndex}
                            className="px-4 py-2 truncate"
                            style={{ width: columnWidth }}
                            title={displayValue}
                        >
                            {displayValue}
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <div className="w-full border border-white/10 rounded-xl bg-slate-900/40 shadow-inner flex flex-col overflow-hidden" style={{ height: `${maxHeight}px` }}>
            {/* Sticky Header */}
            <div className="sticky top-0 z-10 flex items-center bg-slate-900/95 border-b border-white/10 py-3 text-xs font-bold text-slate-400 uppercase tracking-wider backdrop-blur-sm">
                {columns.map((col, index) => (
                    <div
                        key={index}
                        className="px-4 truncate"
                        style={{ width: columnWidth }}
                        title={col}
                    >
                        {col.replace(/_/g, ' ')}
                    </div>
                ))}
            </div>

            {/* Virtualized Body */}
            <div className="flex-1">
                <AutoSizer>
                    {({ height, width }) => (
                        <List
                            height={height}
                            itemCount={data.length}
                            itemSize={45}
                            width={width}
                        >
                            {Row}
                        </List>
                    )}
                </AutoSizer>
            </div>

            <div className="p-2 text-xs text-slate-500 text-right border-t border-white/5 bg-slate-900/20">
                Showing {data.length} {data.length === 1 ? 'row' : 'rows'}
            </div>
        </div>
    );
};
