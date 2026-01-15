# AI Query Data Flow - Detailed Documentation

This document provides an in-depth explanation of how AI queries are processed in the AskTennis React+FastAPI application.

## Table of Contents
1. [Overview](#overview)
2. [Architecture Components](#architecture-components)
3. [Complete Data Flow](#complete-data-flow)
4. [Real Example: "Who won Wimbledon 2022?"](#real-example-who-won-wimbledon-2022)

---

## Overview

The AskTennis application uses a **LangGraph-based AI agent** served via a **FastAPI backend** and consumed by a **React frontend**. The system follows a **ReAct (Reasoning + Acting) pattern** where the AI agent reasons about the query, executes SQL tools, and synthesizes responses.

---

## Architecture Components

### 1. **Frontend Layer (React)**
-   **`SearchPanel.tsx`**: Captures user input.
-   **`api.js/ts`**: Sends POST requests to `/api/query`.
-   **`ResultsPanel.tsx`**: Renders the JSON response (answer text and data tables).

### 2. **Backend Entry Point (`backend/main.py`)**
-   **`/api/query` Endpoint**: Receives the user's question, invokes the `QueryProcessor`.

### 3. **Query Processing Layer (`backend/services/query_service.py`)**
-   **`QueryProcessor`**: Orchestrates the interaction between the API request and the LangGraph agent.
-   **Session Management**: Uses `thread_id` to maintain conversation history in LangGraph.

### 4. **AI Agent Layer (`backend/graph/`, `backend/agent/`)**
-   **LangGraph**: Stateful graph execution.
-   **Gemini AI**: LLM for reasoning.
-   **Tools**: SQLite/PostgreSQL tools for data retrieval.

---

## Complete Data Flow

```
User Input (React) → API Request (FastAPI) → QueryProcessor → LangGraph Agent → LLM → Database → Response → React UI
```

### Detailed Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          1. USER INPUT (Frontend)                           │
│  User types: "Who won Wimbledon 2022?" in SearchPanel                       │
│  Triggers: POST request to http://localhost:8000/api/query                  │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ JSON Payload: { "query": "Who won..." }
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          2. API ENDPOINT (Backend)                          │
│  FastAPI Router: @api_router.post("/query")                                 │
│  Validates input model (QueryRequest)                                       │
│  Calls: query_processor.handle_user_query(query, agent_graph)               │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   3. QUERY PROCESSOR & STATE MANAGEMENT                     │
│  (services/query_service.py)                                                │
│                                                                             │
│  - Generates/Retrieves `thread_id` (passed from frontend or new)            │
│  - Configures LangGraph execution context                                   │
│  - Invokes agent_graph.invoke()                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  4. LANGGRAPH AGENT EXECUTION (ReAct Loop)                  │
│  a) Schema Pruning: Optimizes context                                       │
│  b) LLM Reasoning: Decides to call SQL tools                                │
│  c) Tool Execution: Runs SQL against Tennis DB                              │
│  d) Synthesis: Generates natural language answer                            │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Return: { answer, sql_queries, data, ... }
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  5. RESPONSE FORMATTING & API REPLY                         │
│  QueryProcessor formats the final dictionary.                               │
│  FastAPI serializes to JSON (QueryResponse model).                          │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ JSON Response
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       6. UI RENDERING (Frontend)                            │
│  App receives success response.                                             │
│  - Displays text answer ("Novak Djokovic won...")                           │
│  - Renders data table component with match details                          │
│  - Shows SQL query in "Debug/Expand" section                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Real Example: "Who won Wimbledon 2022?"

### Step 1: Frontend Request
**Method**: `POST`
**URL**: `/api/query`
**Body**:
```json
{
  "query": "Who won Wimbledon 2022?"
}
```

### Step 2: Backend Processing
The `QueryProcessor` initializes the agent. The agent sees "Wimbledon", maps it to the correct tournament name, and generates SQL.

### Step 3: SQL Generation & Execution
**Generated SQL**:
```sql
SELECT winner_name, loser_name, score, round
FROM matches
WHERE LOWER(tourney_name) = 'wimbledon'
  AND event_year = 2022
  AND round = 'F'
```

**Result**:
`[["Novak Djokovic", "Nick Kyrgios", "6-4 6-3 6-4", "F"]]`

### Step 4: Final Synthesis
The LLM converts the row into: *"Novak Djokovic won Wimbledon 2022, defeating Nick Kyrgios in the final."*

### Step 5: Backend Response
**Status**: `200 OK`
**Body**:
```json
{
  "answer": "Novak Djokovic won Wimbledon 2022, defeating Nick Kyrgios in the final.",
  "sql_queries": ["SELECT winner_name..."],
  "data": [
    { "winner_name": "Novak Djokovic", "loser_name": "Nick Kyrgios", ... }
  ],
  "conversation_flow": [...]
}
```

### Step 6: Frontend Display
The React component `ResultsPanel` takes the `answer` string and displays it prominently. It takes the `data` array and renders a responsive table showing the match details.
