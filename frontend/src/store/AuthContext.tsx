import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../api/client';

import { AuthCredentials } from '../types';

interface AuthContextType {
    user: string | null;
    isLoading: boolean;
    login: (credentials: AuthCredentials) => Promise<void>;
    register: (credentials: AuthCredentials) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await api.getMe();
                setUser(response.username);
                localStorage.setItem('asktennis_user', response.username);
            } catch (err) {
                // Not logged in or session expired
                setUser(null);
                localStorage.removeItem('asktennis_user');
            } finally {
                setIsLoading(false);
            }
        };
        checkAuth();
    }, []);

    const login = async (credentials: AuthCredentials) => {
        const response = await api.login(credentials);
        setUser(response.username);
        localStorage.setItem('asktennis_user', response.username);
    };

    const register = async (credentials: AuthCredentials) => {
        await api.register(credentials);
    };

    const logout = async () => {
        await api.logout();
        setUser(null);
        localStorage.removeItem('asktennis_user');
    };

    return (
        <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
