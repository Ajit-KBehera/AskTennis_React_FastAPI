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
            <div className="h-40 flex items-center justify-center text-gray-400">
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
        const bgClass = index % 2 === 0 ? "bg-white" : "bg-gray-50";

        return (
            <div style={style} className={`flex items-center border-b border-gray-100 text-sm text-gray-700 ${bgClass} hover:bg-emerald-50 transition-colors`}>
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
        <div className="w-full border rounded-lg bg-white shadow-sm flex flex-col" style={{ height: `${maxHeight}px` }}>
            {/* Static Header */}
            <div className="flex items-center bg-slate-100 border-b border-slate-200 py-3 text-xs font-bold text-slate-600 uppercase tracking-wider">
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

            <div className="p-2 text-xs text-gray-400 text-right border-t bg-slate-50">
                Showing {data.length} {data.length === 1 ? 'row' : 'rows'}
            </div>
        </div>
    );
};
