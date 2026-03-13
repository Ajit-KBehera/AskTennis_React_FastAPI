# 🎾 AskTennis

**AskTennis** is an AI-powered analytics platform that allows users to query tennis statistics using natural language. It combines a robust multi-database backend with LangGraph agents to answer complex questions about player performance, historical records, and match strategies.

## ✨ Features

- **Natural Language Querying**: Ask questions like _"Who has the best win rate on grass in the last 5 years?"_ and get instant answers powered by LangGraph agents.
- **Voice Input**: Speak your questions using the built-in Web Speech API microphone button in the search panel.
- **Multi-Turn Conversations**: Maintain context across follow-up questions within the same session using persistent LangGraph checkpointing.
- **Query History**: Every AI query is saved per user and can be retrieved via the API or browsed in the UI.
- **Deep Statistical Analysis**: Powered by DuckDB, SQLite, or Cloud SQL PostgreSQL with a rich dataset covering the Open Era.
- **Agentic AI**: Uses LangGraph to decompose complex queries into SQL steps with stateful agent execution.
- **Modern UI**: React 19 frontend with Tailwind CSS 4 for visualizing data and interacting with the agent.
- **User Authentication**: Secure JWT-based authentication with HttpOnly cookies, including a "Remember Me" option for extended sessions.
- **Multi-Database Support**: Seamlessly works with DuckDB (local), SQLite (local), or Cloud SQL PostgreSQL (production).
  - **Tennis Data**: Stores match statistics, player info, and tournament data.
  - **Auth Data**: Dedicated database for user credentials and sessions.
- **Caching Layer**: Redis-based caching for improved performance.
- **Observability**: OpenTelemetry tracing and structured logging with request IDs.
- **Rate Limiting**: Configurable rate limits for API protection.
- **MCP Server**: Model Context Protocol server for external integrations.

## 🏗️ Tech Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **Databases**:
  - DuckDB (local development, read-optimized)
  - SQLite (local fallback)
  - Cloud SQL PostgreSQL (production)
- **AI/Agents**: LangGraph, LangChain, Google Gemini
- **Authentication**: JWT (python-jose), bcrypt password hashing
- **Caching**: Redis
- **Analysis**: Pandas, NumPy, Plotly
- **Observability**: OpenTelemetry, structlog
- **Rate Limiting**: slowapi
- **MCP**: Model Context Protocol server

### Frontend

- **Framework**: React 19 (Vite 7)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand
- **Visualization**: Recharts, Plotly.js
- **Markdown Rendering**: react-markdown with KaTeX for math
- **HTTP Client**: Axios
- **Testing**: Vitest, React Testing Library

### Infrastructure

- **Containerization**: Docker (each service has its own `Dockerfile`)
- **CI/CD**: GitHub Actions
- **Deployment**: Google Cloud Platform (Cloud Run)
- **Database**: Cloud SQL PostgreSQL (production)
- **Secrets Management**: Google Cloud Secret Manager

## 🚀 Getting Started

### Prerequisites

- Python 3.11+ (Tested with 3.13)
- Node.js 20+
- Redis (for caching, optional in development)
- Docker (optional, for containerized setup)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add:
# - GOOGLE_API_KEY=your_google_api_key
# - JWT_SECRET_KEY=your_jwt_secret (or use default for development)
# - DB_TYPE=duckdb (or sqlite)
# - DB_FILE_NAME=tennis.db (optional default)
# - AUTH_DB_FILE_NAME=auth.db (optional default)
# - REDIS_URL=redis://localhost:6379/0 (optional)
```

Start the API server:

```bash
python main.py
# Server running at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables (optional for local dev)
cp .env.example .env
# The app auto-detects the backend at http://localhost:8000 by default.
# Set VITE_API_URL only if your backend runs on a different address:
# VITE_API_URL=http://localhost:8000/api
```

Start the development server:

```bash
npm run dev
# App running at http://localhost:5173
```

## 🔐 Authentication

The API uses **JWT-based authentication** with HttpOnly cookies for secure session management.

### User Registration & Login

```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword123"}'

# Login (sets HttpOnly cookie)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword123"}'

# Make authenticated API call
curl -X GET http://localhost:8000/api/filters \
  --cookie "access_token=your-jwt-token"
```

## 📂 Project Structure

```
AskTennis_React_FastAPI/
├── backend/                         # FastAPI application
│   ├── app/                         # Main application package
│   │   ├── api/                     # API layer
│   │   │   ├── routers/             # Route handlers
│   │   │   │   ├── auth.py          # Authentication endpoints
│   │   │   │   ├── query.py         # AI query & history endpoints
│   │   │   │   ├── stats.py         # Statistics endpoints
│   │   │   │   ├── matches.py       # Match data endpoints
│   │   │   │   └── filters.py       # Filter options endpoint
│   │   │   ├── schemas/             # Pydantic request/response models
│   │   │   │   ├── auth_schemas.py  # Auth schemas
│   │   │   │   └── tennis_schemas.py # Tennis data schemas
│   │   │   └── dependencies.py      # Shared FastAPI dependencies (JWT auth)
│   │   ├── core/                    # Cross-cutting concerns
│   │   │   ├── config/              # Configuration modules
│   │   │   │   ├── config.py        # App settings
│   │   │   │   ├── cors.py          # CORS configuration
│   │   │   │   ├── logging_config.py # Structured logging (structlog)
│   │   │   │   ├── observability.py # OpenTelemetry setup
│   │   │   │   └── rate_limiter.py  # Rate limiting (slowapi)
│   │   │   └── constants.py         # App-wide constants
│   │   ├── domain/                  # Business / domain logic
│   │   │   ├── agent/               # LangGraph agent
│   │   │   │   ├── agent_factory.py # Agent creation and configuration
│   │   │   │   ├── agent_state.py   # Agent state definition
│   │   │   │   └── graph/
│   │   │   │       └── langgraph_builder.py # Graph construction
│   │   │   ├── analysis/            # Statistical analysis
│   │   │   │   ├── serve_stats.py   # Serve statistics calculations
│   │   │   │   └── return_stats.py  # Return statistics calculations
│   │   │   └── tennis/              # Tennis domain logic
│   │   │       ├── tennis_core.py   # Core tennis calculations
│   │   │       ├── tennis_prompts.py # LLM prompts
│   │   │       ├── tennis_mappings.py # Data mappings
│   │   │       ├── tennis_schema_pruner.py # Schema optimization for LLM
│   │   │       └── ranking_analysis.py # Ranking timeline logic
│   │   ├── infrastructure/          # External services and data access
│   │   │   ├── cache/
│   │   │   │   └── redis_cache.py   # Redis caching layer
│   │   │   ├── database/            # Database backends
│   │   │   │   ├── database_factory.py # Factory (DuckDB / SQLite / Cloud SQL)
│   │   │   │   ├── duckdb_config.py
│   │   │   │   ├── sqlite_config.py
│   │   │   │   ├── cloud_sql_config.py
│   │   │   │   ├── models.py        # SQLAlchemy ORM models
│   │   │   │   └── base.py          # Declarative base
│   │   │   ├── llm/
│   │   │   │   └── llm_setup.py     # LLM initialisation (Google Gemini)
│   │   │   └── repositories/
│   │   │       ├── tennis_repository.py # Tennis data queries
│   │   │       └── user_repository.py   # Auth DB operations & query history
│   │   ├── services/                # Application services
│   │   │   ├── query_service.py     # AI query orchestration
│   │   │   └── auth_service.py      # JWT & password helpers
│   │   └── utils/                   # Shared utilities
│   │       ├── df_utils.py
│   │       ├── error_utils.py
│   │       ├── filter_utils.py
│   │       └── string_utils.py
│   ├── tests/                       # pytest test suite
│   ├── benchmark/                   # Agent evaluation benchmarks
│   │   ├── evaluate_agent.py
│   │   └── gold_standard.json
│   ├── mcp_server.py                # Model Context Protocol server
│   ├── main.py                      # Application entry point
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile                   # Backend container image
├── frontend/                        # React application
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── views/               # Page-level views
│   │   │   ├── charts/              # Chart components (Recharts / Plotly)
│   │   │   ├── analysis/            # Analysis UI (matches table, tabs)
│   │   │   ├── search/              # Search panel with voice input
│   │   │   ├── layout/              # Header, sidebar, layout wrapper
│   │   │   └── ui/                  # Shared UI components
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── store/                   # State management (Zustand + AuthContext)
│   │   ├── api/                     # Axios API client + typed helpers
│   │   ├── types/                   # TypeScript type definitions
│   │   └── utils/                   # Utility functions
│   ├── public/                      # Static assets
│   ├── package.json                 # Node dependencies
│   ├── vite.config.ts               # Vite configuration
│   ├── Dockerfile                   # Frontend container image
│   └── nginx.conf.template          # Nginx config for production
├── mds/                             # Architecture & design documentation
├── .github/
│   └── workflows/
│       └── pipeline.yml             # CI + CD (test → build → deploy to Cloud Run)
├── bundler.py                       # Utility to bundle code for LLM analysis
└── package.json                     # Root scripts (npm run dev / backend / frontend)
```

## 🤖 CI/CD & Deployment

This project uses **GitHub Actions** for Continuous Integration and Continuous Deployment.

### Continuous Integration

The CI pipeline runs on every push and pull request to `main`:

- **Backend**:
  - Installs Python 3.11 dependencies
  - Runs pytest test suite
  - Uses Redis service for caching tests
- **Frontend**:
  - Installs Node.js 20 dependencies
  - Runs Vitest test suite
  - Builds production bundle

Workflow: `.github/workflows/pipeline.yml`

### Continuous Deployment to GCP Cloud Run

Automatic deployment to Google Cloud Platform Cloud Run on every push to `main`:

#### Backend Deployment

- **Service**: `asktennis-backend`
- **Database**: Cloud SQL PostgreSQL (production)
- **Secrets**: Managed via Google Cloud Secret Manager
  - `GOOGLE_API_KEY`
  - `JWT_SECRET_KEY`
  - `TENNIS_DB_PASSWORD` / `AUTH_DB_PASSWORD`
- **Auto-scaling**: Scales to zero when idle, up to 10 instances under load
- **Resources**: 2 CPU, 2Gi memory
- **Timeout**: 300 seconds

#### Frontend Deployment

- **Service**: `asktennis-frontend`
- **Static Assets**: Served via Nginx
- **Build-time Configuration**: `VITE_API_URL` is baked in at Docker build time from the `BACKEND_URL` GitHub secret
- **Auto-scaling**: Scales to zero when idle, up to 5 instances under load
- **Resources**: 1 CPU, 512Mi memory
- **Timeout**: 60 seconds

Both CI and CD pipelines are defined in `.github/workflows/pipeline.yml`.

#### Deployment Setup

**Required GitHub Secrets:**

1. `GCP_SA_KEY`: Google Cloud Service Account JSON key
2. `GCP_PROJECT_ID`: GCP project ID
3. `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL instance connection name
4. `TENNIS_DB_NAME` / `TENNIS_DB_USER` / `TENNIS_DB_PASSWORD`: Tennis database credentials
5. `AUTH_DB_NAME` / `AUTH_DB_USER` / `AUTH_DB_PASSWORD`: Auth database credentials
6. `BACKEND_URL`: Backend Cloud Run URL (e.g., `https://asktennis-backend-xxxxx-uc.a.run.app`)
7. `GOOGLE_API_KEY`: Google API key for Gemini
8. `JWT_SECRET_KEY`: JWT signing secret
9. `DEFAULT_MODEL`: (optional) override the default Gemini model

## 🗄️ Database Configuration

The application supports multiple database backends via a factory pattern and differentiates between **Tennis Data** (stats/matches) and **Auth Data** (users/sessions).

### Configuration Variables

- `DB_TYPE`: `duckdb` (default), `sqlite`, or `cloudsql`.
- `DB_FILE_NAME`: Filename for the Tennis DB (default: `tennis.db`).
- `AUTH_DB_FILE_NAME`: Filename for the Auth DB (default: `auth.db`).
- `DB_PATH`: Override path for Tennis DB (e.g., `duckdb:///custom/path.db`).

### Local Development

**DuckDB** (Recommended for analysis):

```bash
export DB_TYPE=duckdb
# Uses backend/tennis.db by default
```

**SQLite**:

```bash
export DB_TYPE=sqlite
# Uses backend/tennis.db by default
```

### Production (Cloud SQL)

```bash
export DB_TYPE=cloudsql
export INSTANCE_CONNECTION_NAME=project:region:instance
export DB_NAME=tennis_db
export DB_USER=db_user
export DB_PASSWORD=db_password  # From Secret Manager
```

## 🔧 Utility Scripts

### Bundler

Generate a single context file for LLM analysis, excluding ignored directories and lock files:

```bash
python3 bundler.py
```

### MCP Server

Run the Model Context Protocol server for external integrations:

```bash
python backend/mcp_server.py
```

The MCP server provides:

- `list_tables()`: List all database tables
- `query_tennis_database(sql_query)`: Execute read-only SQL queries
- `get_database_schema()`: Get database schema definition
- `get_analytical_questions()`: Get curated analytical questions

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm run test          # Watch mode
npm run test:run      # Single run
npm run test:coverage # With coverage
```

## 📊 API Endpoints

### Public

- `GET /health` - Liveness check
- `GET /ready` - Readiness check (verifies DB connectivity)
- `GET /` - Welcome message + endpoint listing (development only)

### Authentication (`/auth`)

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login; sets HttpOnly JWT cookie (`remember_me` supported)
- `POST /auth/logout` - Clear the JWT cookie
- `GET /auth/me` - Get current user info (requires JWT)
- `GET /auth/check-username?username=` - Check username availability

### AI Query (`/api`)

- `POST /api/query` - Natural language tennis query (LangGraph agent, rate-limited)
- `GET /api/query/history` - Retrieve the logged-in user's saved query history

### Statistics (`/api/stats`)

- `POST /api/stats/serve` - Serve statistics charts for a player
- `POST /api/stats/return` - Return statistics charts for a player
- `POST /api/stats/ranking` - Ranking timeline chart for a player

### Matches (`/api`)

- `POST /api/matches` - Filtered match data

### Filters (`/api`)

- `GET /api/filters` - Filter options (players, opponents, tournaments, surfaces, year range)

All `/api/*` and `/auth/me` endpoints require a valid JWT token in an HttpOnly cookie.

## 🛠️ Development

### Running Both Services

From the project root:

```bash
# Using npm scripts (requires concurrently)
npm run dev

# Or manually in separate terminals
npm run backend   # Starts backend
npm run frontend  # Starts frontend
```

### Environment Variables

See `.env.example` files in `backend/` and `frontend/` directories for required environment variables.

## 📄 License

MIT
