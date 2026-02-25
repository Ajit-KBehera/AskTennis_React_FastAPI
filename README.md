# 🎾 AskTennis

**AskTennis** is an AI-powered analytics platform that allows users to query tennis statistics using natural language. It combines a robust multi-database backend with LangGraph agents to answer complex questions about player performance, historical records, and match strategies.

## ✨ Features

- **Natural Language Querying**: Ask questions like _"Who has the best win rate on grass in the last 5 years?"_ and get instant answers powered by LangGraph agents.
- **Deep Statistical Analysis**: Powered by DuckDB, SQLite, or Cloud SQL PostgreSQL with a rich dataset covering the Open Era.
- **Agentic AI**: Uses LangGraph to decompose complex queries into SQL steps with stateful agent execution.
- **Modern UI**: React 19 frontend with Tailwind CSS 4 for visualizing data and interacting with the agent.
- **User Authentication**: Secure JWT-based authentication with HttpOnly cookies.
- **Multi-Database Support**: Seamlessly works with DuckDB (local), SQLite (local), or Cloud SQL PostgreSQL (production).
  - **Tennis Data**: Stores match statistics, player info, and tournament data.
  - **Auth Data**: dedicated database for user credentials and sessions.
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

- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Google Cloud Platform (Cloud Run)
- **Database**: Cloud SQL PostgreSQL (production)
- **Secrets Management**: Google Cloud Secret Manager

## 🚀 Getting Started

### Prerequisites

- Python 3.11+ (Tested with 3.13)
- Node.js 20+
- Redis (for caching, optional in development)
- Docker & Docker Compose (optional, for containerized setup)

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

# Set up environment variables
cp .env.example .env
# Edit .env and add:
# - VITE_API_URL=http://localhost:8000/api
```

Start the development server:

```bash
npm run dev
# App running at http://localhost:5173
```

### 3. Docker Compose Setup (Alternative)

For a complete containerized setup with Redis:

```bash
# From project root
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:80
# Redis: localhost:6379
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
curl -X GET http://localhost:8000/api/stats/players \
  --cookie "access_token=your-jwt-token"
```

## 📂 Project Structure

```
AskTennis/
├── backend/                    # FastAPI application
│   ├── app/                    # Application core logic
│   │   ├── api/                # API routers and endpoints
│   │   │   ├── routers/        # Route handlers (auth, query, stats, etc.)
│   │   │   └── dependencies.py # FastAPI dependencies
│   │   ├── core/               # App configuration and constants
│   │   │   ├── config/         # Config modules (CORS, logging, etc.)
│   │   │   └── constants.py    # Global constants
│   │   ├── domain/             # Domain logic
│   │   │   ├── agent/          # LangGraph agent definitions
│   │   │   ├── tennis/         # Tennis-specific logic and prompts
│   │   │   └── analysis/       # Statistical analysis logic
│   │   ├── infrastructure/     # Infrastructure layer
│   │   │   ├── database/       # Database configs and factory
│   │   │   ├── cache/          # Redis/Disk caching
│   │   │   ├── llm/            # LLM setup and SQL tools
│   │   │   └── repositories/   # Data access services
│   │   ├── services/           # Application services
│   │   └── utils/              # Utility functions
│   ├── tests/                  # Test suite
│   ├── benchmark/              # Agent evaluation benchmarks
│   ├── main.py                 # Application entry point
│   ├── mcp_server.py           # MCP server implementation
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend container image
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── views/         # Page views
│   │   │   ├── charts/        # Chart components
│   │   │   ├── analysis/      # Analysis components
│   │   │   ├── search/        # Search components
│   │   │   ├── layout/        # Layout components
│   │   │   └── ui/            # UI components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── store/             # State management (Zustand)
│   │   ├── api/               # API client
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utility functions
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── Dockerfile             # Frontend container image
│   └── nginx.conf.template    # Nginx config for production
├── .github/
│   └── workflows/             # GitHub Actions workflows
│       ├── ci.yml             # Continuous Integration
│       ├── deploy-backend.yml # Backend deployment
│       └── deploy-frontend.yml # Frontend deployment
├── docker-compose.yml          # Docker Compose configuration
├── bundler.py                  # Utility to bundle code for AI analysis
└── question_bank/              # Benchmark questions
    ├── TENNIS_ANALYTICAL_QUESTIONS.md
    └── TENNIS_ANALYTICAL_QUESTIONS_MCP.md
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
  - Runs ESLint
  - Runs Vitest test suite
  - Builds production bundle

Workflow: `.github/workflows/ci.yml`

### Continuous Deployment to GCP Cloud Run

Automatic deployment to Google Cloud Platform Cloud Run on every push to `main`:

#### Backend Deployment

- **Service**: `asktennis-backend`
- **Database**: Cloud SQL PostgreSQL (production)
- **Secrets**: Managed via Google Cloud Secret Manager
  - `GOOGLE_API_KEY`
  - `JWT_SECRET_KEY`
  - `DB_PASSWORD`
- **Auto-scaling**: Scales to zero when idle, up to 10 instances under load
- **Resources**: 2 CPU, 2Gi memory
- **Timeout**: 300 seconds

Workflow: `.github/workflows/deploy-backend.yml`

#### Frontend Deployment

- **Service**: `asktennis-frontend`
- **Static Assets**: Served via Nginx
- **Build-time Configuration**: `VITE_API_URL` must be set as GitHub secret `BACKEND_URL`
- **Auto-scaling**: Scales to zero when idle, up to 5 instances under load
- **Resources**: 1 CPU, 512Mi memory
- **Timeout**: 60 seconds

Workflow: `.github/workflows/deploy-frontend.yml`

#### Deployment Setup

**Required GitHub Secrets:**

1. `GCP_SA_KEY`: Google Cloud Service Account JSON key
2. `GCP_PROJECT_ID`: GCP project ID
3. `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL instance connection name
4. `DB_NAME`: Database name
5. `DB_USER`: Database user
6. `BACKEND_URL`: Backend Cloud Run URL (e.g., `https://asktennis-backend-xxxxx-uc.a.run.app`)
7. `GOOGLE_API_KEY`: Google API key for Gemini
8. `JWT_SECRET_KEY`: JWT signing secret
9. `DB_PASSWORD`: Database password

**Important Notes:**

- The frontend must know the backend URL at **build time** (Vite inlines `VITE_API_URL`)
- After first backend deployment, get the backend URL from the workflow output or:
  ```bash
  gcloud run services describe asktennis-backend \
    --region us-central1 \
    --format 'value(status.url)'
  ```
- Set `BACKEND_URL` GitHub secret and redeploy frontend to bake in the correct API URL
- **CORS**: Backend allows Cloud Run frontend origins matching `https://asktennis-frontend-*.run.app`. For custom domains, update `ALLOWED_ORIGINS` env var on backend Cloud Run service

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

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (sets HttpOnly cookie)

### AI Query

- `POST /api/query` - Natural language query (requires JWT)

### Statistics

- `GET /api/stats/players` - Get player statistics
- `GET /api/stats/matches` - Get match statistics

### Matches

- `GET /api/matches` - Query matches with filters

### Filters

- `GET /api/filters/players` - Get available player filters
- `GET /api/filters/tournaments` - Get tournament filters

All `/api/*` endpoints require a valid JWT token in an HttpOnly cookie.

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
