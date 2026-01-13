import React from 'react';

export const Header: React.FC = () => {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex flex-col items-center gap-3 text-center">
                <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 mb-1">
                    <span className="text-white text-3xl">🎾</span>
                </div>
                <div>
                    <h1 className="text-3xl font-black text-slate-900 tracking-tight">AskTennis Analytics</h1>
                    <p className="text-slate-500 font-medium">Advanced tennis statistics and AI-powered insights</p>
                </div>
            </div>
        </div>
    );
};
