import React, { ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: ReactNode;
  onFilterChange: (filters: any) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, onFilterChange }) => {
  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Fixed Sidebar on the left */}
      <Sidebar onFilterChange={onFilterChange} />

      {/* Scrollable Main Content Area */}
      <main className="flex-1 overflow-auto bg-transparent relative custom-scrollbar">
        <div className="max-w-7xl mx-auto p-4 md:p-8">
          <div className="glass-panel rounded-3xl p-6 md:p-8 min-h-[calc(100vh-4rem)]">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};
