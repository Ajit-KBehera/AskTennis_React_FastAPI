# 🎾 AskTennis - Advanced AI Tennis Analytics Platform

**AskTennis** is a comprehensive AI-powered tennis statistics application that provides natural language querying of the most complete tennis database in existence, covering 147 years of tennis history (1877-2024) with advanced analytics, player metadata, and intelligent insights.

## ✨ Key Features

### 🏆 **Complete Tennis Database**
- **147 Years of History**: Complete tennis coverage from 1877 to 2024
- **1.7M+ Singles Matches**: Every recorded tennis match
- **26K+ Doubles Matches**: Complete doubles coverage (2000-2020)
- **136K+ Players**: Complete player database with metadata
- **5.3M+ Rankings**: Historical ranking data (1973-2024)
- **All Tournament Levels**: Grand Slams, Masters, Challengers, Futures, ITF

### 🤖 **Advanced AI Integration**
- **Natural Language Queries**: Ask questions in plain English
- **Google Gemini AI**: Powered by Gemini 2.5 Flash Lite
- **LangGraph Framework**: Stateful AI agent architecture
- **Intelligent Responses**: Context-aware tennis insights with player names
- **Historical Analysis**: AI-powered tennis history exploration
- **Performance Optimized**: 6% faster responses with cached mappings

### 🚀 **Performance Optimizations** (Latest Update)
- **Cached Mapping Tools**: 4x speedup for repeated terminology conversions
- **Performance Monitoring**: Real-time system performance tracking
- **Enhanced Response Quality**: Player names and context in all responses
- **Eliminated Duplicate Calls**: No more redundant tool executions
- **Optimized Prompts**: Better instructions for improved query efficiency
- **Stable Architecture**: No infinite loops or recursion errors

### 📊 **Comprehensive Analytics**
- **Player Metadata**: Handedness, nationality, height, birth dates
- **Surface Analysis**: Performance on Hard, Clay, Grass, Carpet
- **Era Classification**: Amateur (1877-1967) vs Professional (1968-2024)
- **Tournament Types**: Main Tour, Qualifying, Challenger, Futures, ITF
- **Ranking Context**: Historical ranking analysis with match context
- **Head-to-Head**: Complete player matchup analysis

### 🏗️ **Modern Architecture**
- **Modular Design**: Clean separation of concerns across 9 core modules
- **Performance Optimized**: Cached mappings and monitoring systems
- **Clean Code**: Two focused applications (45-line basic, 45-line enhanced UI) with modular components
- **Team Collaboration**: Parallel development on different modules
- **Code Reusability**: Components can be reused across projects
- **Production Ready**: Stable system with comprehensive error handling

## 🛠️ Technical Stack

- **Frontend**: Streamlit with modular UI components
- **Backend**: Python with advanced data processing
- **AI/LLM**: 
  - Google Gemini API (gemini-3-flash-preview)
  - LangChain for tool integration and SQL database toolkit
  - LangGraph for stateful agent orchestration with conversation history
- **Database**: 
  - SQLite (local development) with 15 optimized indexes
  - Cloud SQL PostgreSQL (production) support
- **Data Processing**: Pandas, NumPy for statistical analysis
- **Visualization**: Plotly for interactive charts
- **Data Sources**: ATP, WTA, Grand Slam, and historical tennis data
- **Architecture Patterns**: Factory, Builder, Strategy, Dynamic Schema Pruning
- **Caching**: Streamlit caching (`@st.cache_resource`, `@st.cache_data`) and LRU caching

## 🔄 AI Query Processing Flow

The AskTennis application processes natural language queries through a sophisticated pipeline:

1. **User Input** → User enters query in `search_panel.py`
2. **Query Processing** → `QueryProcessor.handle_user_query()` processes the query
   - Generates/retrieves session ID (UUID) for conversation history
   - Creates LangGraph config with `thread_id` for conversation context
3. **Agent Invocation** → LangGraph agent processes query
   - Loads conversation history from checkpointer (based on `thread_id`)
   - Routes to agent node for processing
4. **Schema Pruning** → `TennisSchemaPruner` analyzes query
   - Identifies relevant tables and columns
   - Prunes schema from ~5000 to ~500 tokens (80-90% reduction)
   - Improves LLM performance and reduces API costs
5. **Dynamic Prompt Generation** → `TennisPromptBuilder` creates prompt
   - Query phase: Includes pruned schema, SQL instructions, tool usage guidelines
   - Synthesis phase: Minimal prompt focused on formatting (no schema)
6. **LLM Reasoning** → Google Gemini processes query
   - Uses tennis mapping tools (cached via `@lru_cache`) for terminology conversion
   - Generates SQL query using pruned database schema
   - Executes via `sql_db_query` tool (from LangChain SQL toolkit)
7. **Database Query** → SQL executed against database
   - SQLite (local) or Cloud SQL PostgreSQL (production)
   - Results truncated to 100 rows if needed
8. **Message Trimming** → `LangGraphBuilder._trim_messages_for_synthesis()`
   - Trims conversation history to only user query + SQL results
   - Removes intermediate tool calls and validations
9. **Synthesis** → LLM generates final natural language response
   - Uses synthesis prompt (no schema, focused on formatting)
   - Converts SQL results to natural language with context
10. **Response Processing** → `QueryProcessor.process_agent_response()`
    - Extracts final answer from AIMessage content
    - Handles Gemini-specific response formats (list of dicts)
    - Extracts SQL queries for display
    - Stores in session state for UI display
11. **UI Display** → `results_panel.py` displays results
    - Formatted response with context
    - SQL queries (in expander)
    - Conversation flow (in expander)
    - Analysis tabs if filters applied

**Key Features**:
- **Conversation History**: Maintains context across multiple queries via LangGraph checkpointer
- **Dynamic Schema Pruning**: Reduces token count by 80-90% for faster processing
- **Cached Tools**: Mapping functions cached with `@lru_cache` for 4x speedup
- **Message Trimming**: Optimizes synthesis phase by removing intermediate messages
- **Error Handling**: Graceful error handling at each step with fallback mechanisms

## 🏗️ Modular Architecture

AskTennis features a clean, modular architecture designed for maintainability, testability, and scalability. The system follows a layered architecture pattern with clear separation of concerns across 9 core modules.

### 🧩 **Core Architecture Layers**

#### **1. Application Entry Point**
- **`app.py`** (43 lines) - Single enhanced application interface
  - Initializes LangGraph agent (cached with `@st.cache_resource`)
  - Creates `QueryProcessor`, `DatabaseService`, and `AnswerFormatter`
  - Orchestrates main UI layout via `render_main_content()`
  - Handles initialization errors gracefully

#### **2. UI Layer** (`ui/components/`)
- **`main_layout.py`** - Main layout orchestrator
  - `render_main_content()`: Coordinates filter panel, search panel, and results panel
  - Two-column layout: Filter panel (left) + Search/Results (right)
  - Configurable column widths via `column_layout` parameter
  
- **`filter_panel.py`** - Advanced filtering controls
  - `render_filter_panel()`: Dynamic filtering interface
  - Player selection with tournament/surface filtering
  - Opponent selection (filtered by selected player)
  - Tournament selection (filtered by selected player)
  - Year range selection (filtered by selected player)
  - Surface selection (filtered by selected player)
  
- **`search_panel.py`** - Search input and query submission
  - `render_search_panel()`: Natural language query input
  - Query submission and clearing
  - Session state management for query persistence
  
- **`results_panel.py`** - Results display orchestrator
  - `render_results_panel()`: AI query results display
  - Analysis tabs (matches, serve, return, ranking, raw)
  - Coordinates with specialized tab components
  - Displays SQL queries and conversation flow
  
- **`tabs/`** - Specialized tab components
  - `matches_tab.py`: Match data table display
  - `serve_tab.py`: Serve statistics charts
  - `return_tab.py`: Return statistics charts
  - `ranking_tab.py`: Ranking timeline charts
  - `raw_tab.py`: Raw data display

#### **3. Query Processing Layer** (`services/`)
- **`query_service.py`** - Query processing and agent interaction
  - `QueryProcessor` class: Centralized query processing
  - `handle_user_query()`: Main entry point for query processing
    - Generates/retrieves session ID (UUID) for conversation history
    - Creates LangGraph config with `thread_id` for conversation context
    - Invokes LangGraph agent with user query
    - Processes agent response and stores in session state
  - `process_agent_response()`: Processes agent response and formats output
    - Handles Gemini-specific response formats (list of dicts)
    - Extracts final answer from AIMessage content
    - Falls back to tool messages if needed
  - `_extract_sql_queries()`: Extracts SQL queries from agent response
    - Scans tool calls for `sql_db_query` tool
    - Extracts SQL from message content (code blocks)
    - Returns unique SQL queries

- **`database_service.py`** - Database service layer for enhanced UI
  - `DatabaseService` class: Advanced filtering and data retrieval
  - `get_matches_with_filters()`: Multi-criteria match filtering
    - Player, opponent, tournament, year, and surface filters
    - Dynamic filtering based on selected player
  - `get_all_players()`: Player list for dropdowns (cached)
  - `get_all_tournaments()`: Tournament list with player filtering (cached)
  - `get_opponents_for_player()`: Opponent list filtered by player
  - `get_player_year_range()`: Year range for selected player
  - `get_player_ranking_timeline()`: Ranking history data
  - Cached data retrieval with Streamlit `@st.cache_data`
  - Supports both SQLite and Cloud SQL (PostgreSQL) connections

#### **4. AI Agent Layer** (`agent/`, `graph/`, `llm/`)
- **`agent/agent_factory.py`** - AI agent configuration and factory
  - `setup_langgraph_agent()`: Main factory function (cached with `@st.cache_resource`)
  - Orchestrates LLM setup, tool binding, and graph construction
  - Validates configuration before agent creation
  - Combines base SQL tools with tennis mapping tools
  - Creates prompt template factory for dynamic schema pruning
  
- **`agent/agent_state.py`** - Agent state management
  - `AgentState` TypedDict: Defines state structure
  - Messages list with automatic accumulation via `operator.add`
  
- **`graph/langgraph_builder.py`** - LangGraph builder and state management
  - `LangGraphBuilder` class: Graph construction and management
  - `build_graph()`: Main entry point, builds and compiles the graph
  - `create_agent_node()`: Creates agent node with dynamic schema pruning
    - Extracts user query from messages
    - Checks for SQL results (synthesis phase detection)
    - Prunes schema based on user query
    - Creates dynamic prompt with pruned schema
    - Trims messages for synthesis phase
  - `create_tool_node()`: Creates tool node for tool execution
    - Executes tools (SQL queries, term resolution)
    - Truncates database results to 100 rows
    - Handles tool execution errors gracefully
  - `create_conditional_edges()`: Creates routing logic
    - Routes to tools if tool calls present
    - Routes to end if no tool calls
  - `_has_sql_results()`: Detects SQL results in messages
  - `_trim_messages_for_synthesis()`: Trims messages for final synthesis
  
- **`llm/llm_setup.py`** - LLM setup and configuration management
  - `LLMFactory` class: Manages LLM instance creation
  - `setup_llm_components()`: Sets up LLM, database connection, and SQL toolkit
  - Configures Google Gemini (gemini-3-flash-preview by default)
  - Sets up SQL database toolkit for database queries
  - Supports both SQLite and Cloud SQL connections

#### **5. Tennis Core Layer** (`tennis/`)
- **`tennis_core.py`** - Core tennis functionality orchestrator
  - Exports all tennis functionality through clean interface
  - Centralizes imports from compartmentalized modules
  
- **`tennis_mappings.py`** - Consolidated tennis terminology mapping
  - Mapping dictionaries: `ROUND_MAPPINGS`, `SURFACE_MAPPINGS`, `TOUR_MAPPINGS`, etc.
  - `TennisMappingTools` class: LangChain tools for terminology conversion
  - Cached mapping functions with `@lru_cache` for performance
  - Tools: `round`, `surface`, `tour`, `hand`, `tournament`, `grand_slam`, `ranking_analysis`
  - `create_all_mapping_tools()`: Creates all mapping tools
  
- **`tennis_prompts.py`** - Optimized tennis-specific prompts
  - `TennisPromptBuilder` class: System prompt generation
  - `create_query_system_prompt()`: Generates system prompt with pruned database schema
  - `create_synthesis_system_prompt()`: Generates synthesis prompt for final answer generation
  - Dynamic schema integration for context-aware prompts
  - 44.6% reduction in prompt size (617 → 342 lines) while maintaining functionality
  
- **`tennis_schema_pruner.py`** - Dynamic schema pruning for performance optimization
  - `TennisSchemaPruner` class: Intelligent schema reduction
  - Categorizes columns into three tiers:
    - Tier 1 (Always Include): Essential columns for almost every query
    - Tier 2 (Conditional): Only included if query mentions specific metrics
    - Tier 3 (Never Include): Internal IDs or metadata rarely used
  - `prune_schema()`: Analyzes user query and prunes schema
  - Reduces token count by 80-90% (from ~5000 to ~500 tokens)
  - Improves LLM performance and reduces API costs

- **`ranking_analysis.py`** - Ranking analysis tools
  - Specialized tools for ranking-related queries

#### **6. Configuration Layer** (`config/`)
- **`config/config.py`** - Unified configuration management
  - `Config` class: Single source for all configuration needs
  - Handles LLM settings (model, temperature, API key from environment variables)
  - Manages database configuration (db_path for SQLite or Cloud SQL settings)
  - Supports both local SQLite and GCP Cloud SQL (PostgreSQL)
  - `validate_config()`: Validates configuration before use
  - `get_llm_config()`: Returns LLM configuration dictionary
  - `get_database_config()`: Returns database configuration dictionary
  
- **`constants.py`** - Application-wide constants (root level)
  - `DEFAULT_MODEL`: "gemini-3-flash-preview"
  - `DEFAULT_TEMPERATURE`: Default LLM temperature
  - `DEFAULT_DB_PATH`: Database file path
  - `APP_TITLE`, `APP_SUBTITLE`: Application branding

#### **7. Utilities Layer** (`utils/`)
- **`formatters.py`** - Data formatting utilities
  - `AnswerFormatter` class: Formats database query results into human-readable answers
  - `format_with_context()`: Formats data with context-aware explanations
  - Adds player names and contextual information
  - Generates intelligent summaries
  
- **`chart_utils.py`** - Chart generation utilities
- **`df_utils.py`** - DataFrame utilities
- **`radar_chart_utils.py`** - Radar chart utilities
- **`timeline_chart_utils.py`** - Timeline chart utilities

#### **8. Data Loading Layer** (`load_data/`)
- **`load_data.py`** - Main data loading script
- **`data_loaders.py`** - Data loading utilities
- **`data_transformers.py`** - Data transformation utilities
- **`database_builder.py`** - Database construction
- **`database_verifier.py`** - Database verification

#### **9. UI Utilities** (`ui/utils/`)
- **`style_loader.py`** - Style loader utilities
  - `load_css()`: Loads custom CSS from external file

### 🎯 **Architectural Patterns**

1. **Factory Pattern**: `setup_langgraph_agent()` creates and configures AI agents
2. **Builder Pattern**: `LangGraphBuilder` constructs the AI agent graph
3. **Strategy Pattern**: Different formatting strategies for different data types
4. **Dynamic Schema Pruning**: Intelligent schema reduction based on query content
5. **Caching Strategy**: Multiple levels of caching for performance
   - `@st.cache_resource`: Agent initialization (persists across reruns)
   - `@st.cache_data`: Database queries (TTL-based)
   - `@lru_cache`: Mapping functions (in-memory)

### 🎯 **Benefits of Modular Design**
- **Single Responsibility**: Each module has a focused purpose
- **Code Reusability**: Components can be reused across projects
- **Maintainability**: Changes are isolated to specific modules
- **Collaboration**: Multiple developers can work on different modules
- **Readability**: Clean, focused modules with clear interfaces
- **Testability**: Each module can be tested independently
- **Scalability**: Easy to add new features without affecting existing code

## 📁 Project Structure

```
AskTennis_Streamlit/
├── app.py                           # 🎨 Enhanced UI application (43 lines)
├── requirements.txt                 # 📦 Unified dependencies
├── tennis_data.db                   # 🗃️ SQLite database (created after setup)
├── constants.py                     # 📋 Application-wide constants (root level)
│
├── agent/                           # 🤖 AI Agent Configuration
│   ├── __init__.py
│   ├── agent_factory.py            # Agent factory with performance optimizations
│   └── agent_state.py              # Agent state management (TypedDict)
│
├── llm/                             # 🧠 LLM Setup and Configuration
│   ├── __init__.py
│   └── llm_setup.py                # LLM factory and configuration (LLMFactory)
│
├── tennis/                          # 🎾 Tennis-Specific Tools
│   ├── __init__.py
│   ├── tennis_core.py              # Core tennis functionality orchestrator
│   ├── tennis_mappings.py           # Tennis mapping dictionaries and LangChain tools
│   ├── tennis_prompts.py            # Optimized tennis-specific prompts (44.6% reduction)
│   ├── tennis_schema_pruner.py      # Dynamic schema pruning for performance
│   └── ranking_analysis.py          # Ranking analysis tools
│
├── graph/                           # 🔗 LangGraph Builder
│   ├── __init__.py
│   └── langgraph_builder.py        # Graph construction and state management
│
├── services/                        # 🔧 Services Layer
│   ├── __init__.py
│   ├── query_service.py            # Query processing and agent interaction
│   └── database_service.py         # Database service for enhanced UI
│
├── ui/                              # 🎨 User Interface Components
│   ├── __init__.py
│   ├── components/                 # UI component modules
│   │   ├── main_layout.py          # Main layout orchestrator
│   │   ├── filter_panel.py         # Advanced filtering controls
│   │   ├── search_panel.py         # Search input and query submission
│   │   ├── results_panel.py        # Results display orchestrator
│   │   └── tabs/                   # Specialized tab components
│   │       ├── matches_tab.py       # Match data table display
│   │       ├── serve_tab.py        # Serve statistics charts
│   │       ├── return_tab.py       # Return statistics charts
│   │       ├── ranking_tab.py      # Ranking timeline charts
│   │       └── raw_tab.py          # Raw data display
│   ├── styles/                     # UI styles
│   │   └── styles.css              # Custom CSS
│   └── utils/                      # UI utilities
│       └── style_loader.py         # Style loader utilities
│
├── utils/                           # 🛠️ Utility Functions
│   ├── formatters.py               # Answer formatting utilities (AnswerFormatter)
│   ├── chart_utils.py              # Chart generation utilities
│   ├── df_utils.py                 # DataFrame utilities
│   ├── radar_chart_utils.py        # Radar chart utilities
│   └── timeline_chart_utils.py     # Timeline chart utilities
│
├── load_data/                       # 📊 Data Loading
│   ├── __init__.py
│   ├── load_data.py                # Main data loading script
│   ├── data_loaders.py             # Data loading utilities
│   ├── data_transformers.py        # Data transformation utilities
│   ├── database_builder.py         # Database construction
│   ├── database_verifier.py        # Database verification
│   ├── config.py                   # Data loading configuration
│   └── utils.py                    # Data loading utilities
│
├── config/                          # ⚙️ Configuration Management
│   ├── __init__.py
│   └── config.py                   # Unified configuration class (Config)
│
├── docs/                            # 📚 Documentation
│   ├── 01_System_Architecture.md    # System architecture documentation
│   ├── 02_Data_Flow.md              # Data flow documentation
│   ├── 03_Data_Model.md             # Data model documentation
│   ├── 04_Software_Process_Model.md # Software process documentation
│   ├── 05_Use_Case_Diagram.md       # Use case documentation
│   ├── 06_State_Diagram.md          # State diagram documentation
│   ├── 07_UI_UX_Design.md          # UI/UX design documentation
│   ├── 08_Database_Architecture.md  # Database architecture documentation
│   └── 09_AI_Query_Data_Flow.md    # AI query data flow documentation
│
├── data/                            # 📊 Tennis data files (not in repo)
│   ├── tennis_atp/                  # ATP match data
│   ├── tennis_wta/                  # WTA match data
│   ├── tennis_MatchChartingProject/ # Detailed match data
│   └── tennis_slam_pointbypoint/    # Grand Slam data
│
├── bundler.py                       # 📦 Application bundler
├── Dockerfile                       # 🐳 Docker configuration
└── README.md                        # This file
```

## 🎯 Application Interface

AskTennis provides a comprehensive single application interface that combines AI-powered querying with advanced data analysis:

### 🎨 **Enhanced UI Application** (`app.py` - 43 lines)
- **Purpose**: Comprehensive tennis data analysis with AI integration
- **Layout**: Two-column layout (Filter Panel + Search/Results Panel)
- **Architecture**:
  - **Entry Point**: `app.py` initializes LangGraph agent, QueryProcessor, DatabaseService, and AnswerFormatter
  - **UI Orchestration**: `main_layout.py` coordinates filter panel, search panel, and results panel
  - **Component-Based**: Modular UI components in `ui/components/` for maintainability

- **Features**:
  - **Advanced Filtering System** (`filter_panel.py`):
    - Player selection with dynamic tournament/surface filtering
    - Opponent selection (filtered by selected player)
    - Tournament selection (filtered by selected player)
    - Year range selection (filtered by selected player)
    - Surface selection (filtered by selected player)
  - **AI Query Integration** (`search_panel.py`):
    - Natural language query input
    - Session state management for query persistence
    - Query submission and clearing
  - **Results Display** (`results_panel.py`):
    - AI query results with formatted responses
    - SQL query display (in expander)
    - Conversation flow visualization (in expander)
    - Analysis tabs (matches, serve, return, ranking, raw)
  - **Database Service** (`database_service.py`):
    - Interactive data tables with filtering via `get_matches_with_filters()`
    - Cached data retrieval with Streamlit `@st.cache_data`
    - Supports both SQLite and Cloud SQL (PostgreSQL)
  - **Chart Generation**:
    - Serve statistics charts (`serve_tab.py`)
    - Return statistics charts (`return_tab.py`)
    - Ranking timeline charts (`ranking_tab.py`)
    - Match data tables (`matches_tab.py`)
    - Raw data display (`raw_tab.py`)
  - **AI Agent Integration**:
    - LangGraph-based stateful agent with conversation history
    - Dynamic schema pruning for performance optimization
    - Cached agent initialization with `@st.cache_resource`
    - Google Gemini AI (gemini-3-flash-preview) for natural language processing

- **Best for**: Data analysts, researchers, detailed tennis analysis, and AI-powered querying

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Google Gemini API Key** (for AI functionality)
- **Tennis Data** (from Jeff Sackmann's GitHub repositories)

### Data Setup (Required First Step)

**⚠️ Important**: The tennis data is not included in this repository due to size constraints. You must download it separately.

1. **Download Tennis Data from Jeff Sackmann's GitHub**
   ```bash
   # Create data directory
   mkdir -p data
   
   # Download ATP data
   git clone https://github.com/JeffSackmann/tennis_atp.git data/tennis_atp
   
   # Download WTA data  
   git clone https://github.com/JeffSackmann/tennis_wta.git data/tennis_wta
   
   # Download Grand Slam point-by-point data
   git clone https://github.com/JeffSackmann/tennis_slam_pointbypoint.git data/tennis_slam_pointbypoint
   
   # Download Match Charting Project data
   git clone https://github.com/JeffSackmann/tennis_MatchChartingProject.git data/tennis_MatchChartingProject
   ```

2. **Verify Data Structure**
   ```bash
   # Check that data directories exist
   ls -la data/
   # Should show: tennis_atp, tennis_wta, tennis_slam_pointbypoint, tennis_MatchChartingProject
   ```

**Note**: The `data/` folder is in `.gitignore` to keep the repository lightweight. Each data repository is ~100MB-500MB, so the total download will be 1-2GB.

### Environment Setup

#### Option 1: Virtual Environment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ajit-KBehera/AskTennis_Streamlit.git
   cd AskTennis_Streamlit
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Upgrade pip and install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up API credentials**
   ```bash
   # Copy the example file and edit it
   cp .env.example .env
   # Then edit .env and add your Google API key
   # Or create it manually:
   echo 'GOOGLE_API_KEY=your_gemini_api_key_here' > .env
   ```

5. **Create the database** (First time only - takes 30-90 minutes)
   ```bash
   python load_data.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Open your browser** to `http://localhost:8501`

#### Option 1A: Conda Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ajit-KBehera/AskTennis_Streamlit.git
   cd AskTennis_Streamlit
   ```

2. **Create and activate conda environment**
   ```bash
   # Create conda environment (if not already created)
   conda create -n asktennis python=3.9
   
   # Activate conda environment
   conda activate asktennis
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up API credentials**
   ```bash
   # Copy the example file and edit it
   cp .env.example .env
   # Then edit .env and add your Google API key
   # Or create it manually:
   echo 'GOOGLE_API_KEY=your_gemini_api_key_here' > .env
   ```

5. **Create the database** (First time only - takes 30-90 minutes)
   ```bash
   python load_data.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Open your browser** to `http://localhost:8501`

#### Option 2: Direct Installation

```bash
# Clone and navigate
git clone https://github.com/Ajit-KBehera/AskTennis_Streamlit.git
cd AskTennis_Streamlit

# Install dependencies
pip install -r requirements.txt

# Set up API key (create .env file as above)
# Create database
python load_data.py

# Run application
# Basic AI query interface
streamlit run app_basic.py

# Enhanced UI with filters and database service
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables Setup

The project uses `.env` files for local configuration. A template file `.env.example` is provided with all available options.

**Quick Setup:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_gemini_api_key_here
```

**Minimum Required Configuration:**
For local development with SQLite, only the Google API key is required:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Full Configuration:**
See `.env.example` for all available options including:
- Google API Key (required)
- Cloud SQL configuration (optional)

### Database Configuration
The `load_data.py` script will create a comprehensive database with:
- **Complete Historical Coverage**: 1877-2024
- **All Tournament Levels**: Grand Slams to Futures
- **Player Metadata**: Complete player information
- **Rankings Integration**: Historical ranking context
- **Optimized Performance**: 15 indexes for fast queries

### Customization Options
- **Data Range**: Modify `YEARS` in `load_data.py` for different time periods
- **Data Sources**: Add additional data directories in `DATA_DIRS`
- **Database Name**: Change `DB_FILE` for custom database names

## 📊 Database Schema

### Core Tables
- **`matches`**: 1.7M+ singles matches (1877-2024)
- **`doubles_matches`**: 26K+ doubles matches (2000-2020)
- **`players`**: 136K+ players with complete metadata
- **`rankings`**: 5.3M+ ranking records (1973-2024)

### Enhanced Views
- **`matches_with_full_info`**: Complete match data with player details
- **`matches_with_rankings`**: Match data with ranking context
- **`player_rankings_history`**: Complete player ranking trajectories

### Key Features
- **100% Surface Data**: Complete surface information for all matches
- **Era Classification**: Amateur vs Professional era analysis
- **Tournament Types**: Complete tournament level coverage
- **Player Metadata**: Handedness, nationality, height, birth dates
- **Historical Rankings**: Complete ranking history integration

## 🎯 Example Queries

### Historical Analysis
- "Who won the first Wimbledon in 1877?"
- "How many matches were played in the 1980s?"
- "Compare amateur vs professional eras"

### Player Analysis
- "Which left-handed players won the most matches?"
- "Who are the tallest players in tennis?"
- "Show me Roger Federer's head-to-head record"

### Tournament Analysis
- "How many Grand Slam matches were played on grass?"
- "Which players dominated the 1990s?"
- "Show me the most successful doubles teams"

### Ranking Analysis
- "Who was ranked #1 in 2020?"
- "Which top 10 players won the most matches?"
- "How many upsets happened in Grand Slams?"

## 📈 Performance

- **Database Size**: ~2GB (1.7M+ matches, 5.3M+ rankings)
- **Query Speed**: <2 seconds for complex queries (6% improvement with optimizations)
- **Memory Usage**: Optimized for large datasets
- **Indexing**: 15 optimized indexes for fast lookups
- **Cached Mappings**: 4x speedup for repeated terminology conversions
- **Response Time**: 3.5 seconds average (down from 3.7s)
- **Performance Monitoring**: Real-time system performance tracking
- **Stable Architecture**: No infinite loops or recursion errors

## 🔍 Troubleshooting

### Common Issues

1. **Data Not Found Error**
   - Error: "No data found in any directory"
   - Solution: Download tennis data from Jeff Sackmann's GitHub repositories (see Data Setup section above)

2. **Database Creation Takes Long Time**
   - Normal: 30-90 minutes for complete database
   - Solution: Be patient, process includes 147 years of data

3. **API Key Not Found**
   - Error: "Google API key not found"
   - Solution: Create `.env` file in project root with `GOOGLE_API_KEY=your_key_here`

4. **Memory Issues**
   - Error: Out of memory during database creation
   - Solution: Close other applications, ensure 4GB+ RAM available

5. **Dependencies Issues**
   - Error: Module not found
   - Solution: Ensure virtual environment is activated and run `pip install -r requirements.txt`

### Performance Optimization
- **Large Datasets**: Database is optimized with indexes
- **Memory Usage**: Close unnecessary applications during setup
- **Query Speed**: Use the provided views for faster queries

## 🤝 Contributing

This project represents the most comprehensive tennis database in existence. Contributions are welcome for:
- Additional data sources
- Performance optimizations
- New analytical features
- Documentation improvements

## 📝 License

[Add your license information here]

## 🐛 Known Issues

- Database creation requires significant time (30-90 minutes)
- Large memory usage during initial setup
- API key required for AI functionality
- Some complex queries may take longer with very large datasets

## 📞 Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review the troubleshooting section above
3. Create an issue in the repository

---

## 🚀 Recent Updates (Latest)

### ⚡ Performance Improvements
- **6% Faster Responses**: 3.7s → 3.5s average response time
- **Cached Mapping Tools**: 4x speedup for repeated terminology conversions
- **Performance Monitoring**: Real-time system performance tracking
- **Enhanced Response Quality**: Player names and context in all responses
- **Eliminated Duplicate Calls**: No more redundant tool executions
- **Stable Architecture**: No infinite loops or recursion errors
- **Optimized System Prompt**: 44.6% reduction (617 → 342 lines) while maintaining functionality

### 🏗️ Architectural Enhancements
- **Unified Configuration**: Consolidated AgentConfig and DatabaseConfig into single Config class
- **Mapping Consolidation**: Consolidated mapping dictionaries into `tennis_mappings.py` for simplified structure
- **Prompt Optimization**: Removed duplicate mapping documentation from prompts, references tools instead
- **Single Source of Truth**: Mappings live in dictionaries only, prompts reference tools
- **Code Organization**: Methods organized chronologically by execution flow
- **Constants Management**: Moved constants to root level for easier access
- **Performance Optimizations**: Cached mappings and monitoring systems
- **Production Ready**: Stable system with comprehensive error handling
- **Team Collaboration**: Parallel development on different modules
- **Code Reusability**: Components can be reused across projects
- **Reduced Redundancy**: Eliminated duplicate code and documentation
- **Dynamic Schema Pruning**: Intelligent schema reduction based on query content (80-90% token reduction)
- **Message Trimming**: Optimized synthesis phase by trimming conversation history to essential messages
- **LangGraph Integration**: Stateful agent with conversation history via checkpointer
- **Cloud SQL Support**: Full PostgreSQL support for production deployments
- **Modular UI Components**: Component-based architecture in `ui/components/` for maintainability

---

**Status**: ✅ Production Ready - Complete Tennis Database with AI Integration

**Architecture**: 🏗️ Modular Design - 9 focused modules with performance optimizations

**Database Coverage**: 147 years (1877-2024) | 1.7M+ matches | 136K+ players | 5.3M+ rankings

**AI Capabilities**: Natural language queries | Historical analysis | Player insights | Tournament analytics

**Performance**: ⚡ 6% faster responses | 💾 Cached mappings | 📊 Real-time monitoring | 🎯 Enhanced quality

**Code Quality**: 🧩 Single Responsibility | 🔄 Reusable Modules | 👥 Team Collaboration Ready