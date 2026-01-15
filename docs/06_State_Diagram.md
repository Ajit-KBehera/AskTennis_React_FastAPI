# 🔄 AskTennis AI - State Diagram

## Overview

This document models the life cycle of the application states, focusing on the User Interface (React) and the Agent Processing (Backend) states.

## 🖥️ Application State (Frontend)

The React application moves through several high-level states during user interaction.

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> LoadingFilters : App Mount
    LoadingFilters --> Idle : Filters Loaded
    
    Idle --> Querying : User Submits Question
    Querying --> ResultDisplay : Success Response
    Querying --> ErrorState : API Error
    
    ResultDisplay --> Querying : New Question
    ResultDisplay --> FilterUpdate : User Changes Filter
    
    FilterUpdate --> Querying : Apply Filter (Refines Data)
```

### State Descriptions
-   **Idle**: App is loaded, waiting for user input.
-   **LoadingFilters**: Fetching list of players/tournaments from API.
-   **Querying**: Waiting for specific API request (`/api/query`) to complete. Shows spinners/skeletons.
-   **ResultDisplay**: Showing answer card and data tables.
-   **ErrorState**: Showing toast notification or error boundary message.

## 🤖 Agent State (Backend)

The LangGraph agent manages the state of a single conversation thread.

```mermaid
stateDiagram-v2
    [*] --> Init
    
    Init --> Reasoning : Receive Query
    
    Reasoning --> SQL_Generation : Intent = Data Fetch
    Reasoning --> DirectAnswer : Intent = Greeting/General
    
    SQL_Generation --> SQL_Validation : Generate SQL
    SQL_Validation --> Execute : SQL Valid
    SQL_Validation --> SQL_Generation : SQL Invalid (Retry)
    
    Execute --> Synthesis : Data Retrieved
    Synthesis --> Complete : Generate Response
    
    DirectAnswer --> Complete
    
    Complete --> [*]
```

### State Descriptions
-   **Init**: Load conversation history.
-   **Reasoning**: LLM decides next step (Tool call vs Final Answer).
-   **SQL_Generation**: Constructing query based on schema.
-   **Execute**: Running query against Database.
-   **Synthesis**: Combining raw data with natural language.
