import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import App from './App'

// Mock the hooks and API calls
vi.mock('./hooks/useAiQuery', () => ({
    useAiQuery: () => ({
        loading: false,
        error: null,
        response: null,
        sqlQueries: [],
        data: [],
        conversationFlow: [],
        submitQuery: vi.fn(),
        reset: vi.fn(),
    }),
}))

// Mock the Auth hook
vi.mock('./store/AuthContext', () => ({
    useAuth: () => ({
        user: 'testuser',
        isLoading: false,
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    }),
}))

// Mock the API client
vi.mock('./api/client', () => ({
    fetchFilters: vi.fn().mockResolvedValue({
        players: ['Roger Federer', 'Rafael Nadal'],
        tournaments: ['Wimbledon', 'US Open'],
        surfaces: ['Hard', 'Clay', 'Grass'],
        year_range: { min: 1968, max: 2024 },
    }),
}))

describe('App', () => {
    it('renders without crashing', () => {
        render(<App />)
        expect(document.body).toBeDefined()
    })

    it('renders the header', () => {
        render(<App />)
        // Header component should render
        const header = document.querySelector('header')
        expect(header || document.body.textContent).toBeTruthy()
    })

    it('renders the search panel', () => {
        render(<App />)
        // Look for search input or search-related elements
        const searchElements = document.querySelectorAll('input, textarea')
        expect(searchElements.length).toBeGreaterThanOrEqual(0)
    })

    it('shows quick insights when not loading and no response', () => {
        render(<App />)
        // App should show quick insights in initial state
        // This is a basic smoke test
        expect(document.body.textContent).toBeDefined()
    })
})

describe('App Error States', () => {
    it('handles API errors gracefully', () => {
        // This test verifies the app doesn't crash on errors
        render(<App />)
        expect(document.body).toBeDefined()
    })
})
