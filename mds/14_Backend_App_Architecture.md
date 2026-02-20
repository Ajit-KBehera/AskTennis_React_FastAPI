# AskTennis Backend Architecture Analysis

The backend has been comprehensively restructured into an industry-standard **Layered Architecture**. This document details all folders, subfolders, and Python scripts within the `backend/app/` directory, explaining their functionality and how they maintain separation of concerns.

> **General Philosophy**: Dependencies point _inward_. The `api/` layer depends on `services/`. `services/` depends on `domain/` and `infrastructure/`. The `domain/` layer depends on nothing but itself (pure Python logic).

---

## 🚀 Entry Points (Root Level)

These files live at `backend/` and bootstrap the application.

- **`main.py`**: The primary FastAPI entry point. It loads environment variables, initializes the `app`, registers routers from `app.api.routers`, attaches middleware (from `app.core.config`), and starts the Uvicorn server.
- **`mcp_server.py`**: A secondary entry point running the Model Context Protocol server. It bypasses the HTTP API entirely, interacting directly with `app.infrastructure.repositories` to serve data locally.

---

## 🌐 1. The API Layer (`app/api/`)

Responsible _only_ for HTTP request handling, data validation, and response formatting. It contains no business logic or SQL.

- **`dependencies.py`**: Centralizes FastAPI `Depends` injectables. Contains `get_current_user`, isolating JWT token extraction and verification from the endpoint code.
- **`routers/`**: The HTTP handlers.
  - `auth.py`: Registration, login, and token generation endpoints.
  - `query.py`: The main AI endpoint (`/query`). It extracts the request and passes it to the `QueryProcessor` service.
  - `stats.py` & `matches.py` & `filters.py`: Standard REST endpoints that retrieve UI data via repositories.
- **`schemas/`**: Pydantic models (Data Transfer Objects).
  - `auth_schemas.py`: Defines the shape of user registration and login payloads.
  - `tennis_schemas.py`: Defines the strictly typed structures for UI charts (e.g., `ServeStatsResponse`, `PlotlyChart`) and the AI `QueryRequest`.

---

## ⚙️ 2. The Core Layer (`app/core/`)

Responsible for application-wide, cross-cutting configurations that affect the environment but aren't specific to business features.

- **`constants.py`**: The single source of truth for hardcoded values (e.g., DB file names, default LLM models, token expiration times).
- **`config/`**:
  - `config.py`: The unified `Config` class that loads `.env` variables and validates API keys (e.g., `GOOGLE_API_KEY`).
  - `cors.py`: Configures Cross-Origin Resource Sharing rules.
  - `logging_config.py` & `observability.py`: Set up `structlog`, JSON logging formatting, and LangSmith tracing.
  - `rate_limiter.py`: Defines the SlowAPI rate limiter to prevent abuse on the `/query` endpoint.

---

## 🧠 3. The Domain Layer (`app/domain/`)

The heart of the application. Contains pure business logic and rules. It does not know about databases, HTTP, or Redis.

- **`agent/`**: The AI orchestration logic.
  - `agent_factory.py`: Configures the LangChain environment and binds tools to the LLM.
  - `agent_state.py`: Defines the TypedDict memory state passed between nodes in the Graph.
  - `graph/langgraph_builder.py`: Constructs the state machine (StateGraph) defining the conversational logic loop (Parse -> Query -> Respond).
- **`tennis/`**: Tennis-specific rules and mappers.
  - `tennis_core.py`: Foundational tennis constants and logic blocks.
  - `tennis_mappings.py`: Maps external terms to internal database representations (e.g., standardizing tournament names).
  - `tennis_schema_pruner.py`: A highly specialized script that dynamically feeds lightweight schema definitions to the LLM to save token context.
  - `tennis_prompts.py`: The System Prompts instructing the AI how to act as a tennis expert.
- **`analysis/`**: Analytical logic.
  - `ranking_analysis.py`: Mathematical logic to calculate and format player ranking timelines over the years.

---

## 🏗️ 4. The Infrastructure Layer (`app/infrastructure/`)

The adapters to the outside world. This layer implements the interfaces required by the core application to talk to databases, caches, and external APIs.

- **`database/`**: Database connection lifecycles.
  - `models.py`: The SQLAlchemy ORM definitions (`User`, `QueryHistory`).
  - `database_factory.py` & `base.py`: The Abstract Factory pattern allowing the app to switch between SQLite, DuckDB, and Cloud SQL without changing business code.
  - `duckdb_config.py` & `sqlite_config.py` & `cloud_sql_config.py`: Concrete connection implementations.
- **`repositories/`**: The Data Access Layer (DAL).
  - `tennis_repository.py`: (Formerly DatabaseService) Executes all raw SQL queries against the tennis dataset using Pandas.
  - `user_repository.py`: (Formerly AuthDBService) Executes all ORM queries against the authentication database (creating users, saving query history).
- **`llm/`**: External AI providers.
  - `llm_setup.py`: Configures the connection to Google's Gemini models via LangChain's `ChatGoogleGenerativeAI`.
- **`cache/`**:
  - `redis_cache.py`: Adapters for connecting to and interacting with a Redis instance (if implemented).

---

## 🛠️ 5. The Services Layer (`app/services/`)

The Orchestration layer. Services glue the API, Domain, and Infrastructure layers together to satisfy specific use cases.

- **`query_service.py`**: The `QueryProcessor`. It's called by the `api/query.py` router. It takes the user's string, invokes the LangGraph `agent` (Domain), handles timeouts, formats the conversational output, and returns it to the API.
- **`auth_service.py`**: Contains the cryptography logic via `passlib` and `python-jose`. It orchestrates password hashing and JWT token generation/verification, utilized by `dependencies.py` and `routers/auth.py`.

---

## 🧰 6. The Utils Layer (`app/utils/`)

Generic, shared helper functions that aren't specific to any one business domain.

- **`df_utils.py`**: Pandas DataFrame helpers (e.g., replacing NaNs).
- **`error_utils.py`**: Standardized error string formatting.
- **`string_utils.py`**: Contains `safe_parse`, a critical recursive function to safely decode fragile JSON strings returned by the LLM.
- **`filter_utils.py`**: Helpers for formatting dropdown filter lists.

---

## Conclusion & Architecture Benefits

This advanced structure achieves **Clean Architecture**:

1. **Framework Agnostic**: You can swap FastAPI for a CLI app by bypassing `api/` and calling `services/` directly (which is exactly what `mcp_server.py` does).
2. **Provider Agnostic**: You can swap Gemini for OpenAI by editing only _one_ file in `infrastructure/llm/llm_setup.py`.
3. **High Cohesion**: The AI reasoning (`domain/`) is protected from HTTP specific logic (`api/`), preventing messy, spaghetti-code files. Every file has one strict responsibility.
