import { create } from 'zustand';

interface AppState {
    theme: 'light' | 'dark';
    sidebarOpen: boolean;
    toggleSidebar: () => void;
    closeSidebar: () => void;
    openSidebar: () => void;
    setTheme: (theme: 'light' | 'dark') => void;
}

export const useAppStore = create<AppState>((set) => ({
    theme: 'light', // Default theme
    // Default sidebar state: closed on mobile (< 768px), open on desktop
    sidebarOpen: typeof window !== 'undefined' ? window.innerWidth >= 768 : true,
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    closeSidebar: () => set({ sidebarOpen: false }),
    openSidebar: () => set({ sidebarOpen: true }),
    setTheme: (theme) => set({ theme }),
}));
