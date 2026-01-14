import React from 'react';

export const TennisLoader: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center p-8">
            <div className="relative w-16 h-16">
                {/* Tennis Ball */}
                <div className="absolute inset-0 w-16 h-16 bg-[#dcfce7] rounded-full shadow-lg animate-bounce border-2 border-[#22c55e] flex items-center justify-center overflow-hidden">
                    <div className="w-full h-full relative">
                        {/* Tennis Ball Seams */}
                        <div className="absolute top-1/2 left-0 w-full h-[2px] bg-white opacity-40 transform -rotate-45" />
                        <div className="absolute top-0 left-1/2 w-[2px] h-full bg-white opacity-40 transform -rotate-45" />
                        <div className="absolute w-12 h-12 border-2 border-white/50 rounded-full top-2 left-2 opacity-60" />
                    </div>
                </div>
                {/* Shadow */}
                <div className="absolute bottom-[-10px] left-1/2 transform -translate-x-1/2 w-10 h-2 bg-black/20 rounded-full blur-sm animate-pulse" />
            </div>
            <p className="mt-6 text-slate-400 font-medium animate-pulse">Serving up insights...</p>
        </div>
    );
};
