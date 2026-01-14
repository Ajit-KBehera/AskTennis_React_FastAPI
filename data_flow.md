# Data Flow Documentation: Tennis Analysis

## Overview
This document details the end-to-end data flow when a user generates a statistical analysis report (e.g., Serve, Return, Matches) by filtering for a specific player.

## Example Scenario
**User Action**: Selects **"Novak Djokovic"** from the Sidebar Player Dropdown and sets Year to **"2023"**.

### High-Level Flow
1.  **Sidebar Component**: Detects change, calls `onFilterChange`.
2.  **App Component**: Receives new filter state, triggers `handleFilterChange`.
3.  **API Requests**: `App.tsx` fires 4 parallel async requests to the Backend.
4.  **Backend Processing**: FastAPI routers call `DatabaseService` (now cached) to fetch raw match data, then compute statistics.
5.  **Frontend State**: Responses are stored in React State (`matches`, `serveCharts`, etc.).
6.  **Results Rendering**: The `Tabs` component propagates data to specific views (`MatchesTable`, `ServeStatsView`).

## Detailed Architecture Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Sidebar as <Layout><Sidebar/>
    participant App as App.tsx (State Orchestrator)
    participant API as API Client (Axios)
    participant BE_Matches as Backend: /matches
    participant BE_Stats as Backend: /stats/*
    participant DB as DatabaseService (DuckDB)
    participant UI_Tabs as <Tabs/> Component

    note over User, Sidebar: Step 1: User Selection
    User->>Sidebar: Select "Novak Djokovic", Year "2023"
    Sidebar->>App: onFilterChange({player: "Novak", year: "2023"})

    note over App: Step 2: Orchestration
    App->>App: setFilters(...)
    App->>App: setLoading(true)
    App->>App: setHasGeneratedAnalysis(true)

    note over App, DB: Step 3: Parallel Data Fetching
    par Fetch Matches
        App->>API: POST /api/matches
        API->>BE_Matches: Request Matches
        BE_Matches->>DB: get_matches_with_filters()
        DB-->>BE_Matches: Raw Match Data (Cached)
        BE_Matches-->>API: JSON List[Match]
        API-->>App: setMatches(...)
    and Fetch Serve Stats
        App->>API: POST /api/stats/serve
        API->>BE_Stats: Request Serve Stats
        BE_Stats->>DB: get_matches_with_filters()
        DB-->>BE_Stats: Raw Match Data (Cached Hit)
        BE_Stats->>BE_Stats: Calculate Ace%, 1st Serve%, etc.
        BE_Stats-->>API: JSON {timeline_chart, radar_chart...}
        API-->>App: setServeCharts(...)
    and Fetch Return Stats
        App->>API: POST /api/stats/return
        API->>BE_Stats: Request Return Stats
        BE_Stats->>DB: get_matches_with_filters()
        DB-->>BE_Stats: Raw Match Data (Cached Hit)
        BE_Stats->>BE_Stats: Calculate Break Pt%, Return Pts Won%
        BE_Stats-->>API: JSON {charts...}
        API-->>App: setReturnCharts(...)
    and Fetch Ranking
        App->>API: POST /api/stats/ranking
        API->>BE_Stats: Request Ranking History
        BE_Stats->>DB: get_player_ranking_timeline()
        DB-->>BE_Stats: DataFrame
        BE_Stats-->>API: JSON {ranking_history}
        API-->>App: setRankingChart(...)
    end

    note over App, UI_Tabs: Step 4: Rendering
    App->>App: setLoading(false)
    App->>UI_Tabs: Props: (matches, serveCharts, returnCharts...)
    
    rect rgb(240, 248, 255)
        note right of UI_Tabs: Users sees dashboard
        UI_Tabs->>UI_Tabs: Render <MatchesTable/>
        UI_Tabs->>UI_Tabs: Render <ServeStatsView/> (Charts)
        UI_Tabs->>UI_Tabs: Render <ReturnStatsView/> (Charts)
    end
```

## Data Transformation Steps

### 1. Frontend: Filter Construction
`App.tsx` constructs a `ServeStatsRequest` object:
```json
{
  "player_name": "Novak Djokovic",
  "opponent": undefined,
  "tournament": undefined,
  "surface": [],
  "year": "2023"
}
```

### 2. Backend: Database Query (Optimized)
The `DatabaseService` receives the request.
*   **Cache Check**: Checks `@lru_cache` for signature `("Novak Djokovic", "2023", ...)`.
*   **Query**: Executes SQL:
    ```sql
    SELECT * FROM matches 
    WHERE (winner_name = 'Novak Djokovic' OR loser_name = 'Novak Djokovic')
    AND event_year = 2023
    ```
*   **Return**: Returns a pandas DataFrame of ~60 matches.

### 3. Backend: Stats Calculation
*   **Serve Stats**: Iterates DataFrame. Calculates:
    *   aces / total_serve_points
    *   1st_serve_in / total_serve_points
*   **Comparisons**: Calculates the same stats for the *opponent* in those matches for context.

### 4. Frontend: Visualization
The Frontend receives pre-calculated JSON ready for `Recharts` or `Nivo`.
```json
{
  "timeline_chart": [
    {"date": "2023-01", "aces": 15, "df": 2},
    {"date": "2023-02", "aces": 12, "df": 1}
  ]
}
```
`ServeStatsView` maps this directly to `<LineChart data={data.timeline_chart} />`.
