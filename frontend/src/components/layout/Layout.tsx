import React, { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { useUiStore } from '../../store/useUiStore';

interface LayoutProps {
  children: ReactNode;
  onFilterChange: (filters: any) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, onFilterChange }) => {
  const { sidebarOpen, closeSidebar, openSidebar } = useUiStore();

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950">
      {/* Fixed Sidebar on the left */}
      <Sidebar
        onFilterChange={onFilterChange}
        isOpen={sidebarOpen}
        onClose={closeSidebar}
      />

      {/* Main Content Area */}
      <main id="main-content" className="flex-1 overflow-auto bg-transparent relative custom-scrollbar" tabIndex={-1}>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-emerald-500 focus:text-white focus:rounded-lg focus:outline-none"
        >
          Skip to main content
        </a>
        {/* Mobile Menu Trigger */}
        <div className="md:hidden p-4 pb-0">
          <button
            onClick={openSidebar}
            className="p-2 bg-slate-800 rounded-lg text-emerald-400 border border-white/10"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
          </button>
        </div>

        <div className="max-w-7xl mx-auto p-4 md:p-8">
          <div className="glass-panel rounded-3xl p-6 md:p-8 min-h-[calc(100vh-4rem)]">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};
