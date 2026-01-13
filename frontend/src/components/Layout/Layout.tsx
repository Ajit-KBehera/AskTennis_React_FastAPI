import React, { ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: ReactNode; // This represents the main page content
  onFilterChange: (filters: any) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, onFilterChange }) => {
  return (
    <div className="flex h-screen w-full bg-gray-100">
      {/* Fixed Sidebar on the left */}
      <Sidebar onFilterChange={onFilterChange} />

      {/* Scrollable Main Content Area */}
      <main className="flex-1 overflow-auto p-8">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

