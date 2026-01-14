# AskTennis Project Evolution & Improvement Roadmap

Based on the analysis of the current codebase (`AskTennis_Trial`), here are several avenues for evolution and improvement. The project is already well-structured with a modern stack (FastAPI, React 19, LangGraph, DuckDB), but there is significant potential to deepen the analytical capabilities and improve the user experience.

## 1. AI & Agentic Evolution (The "Brain")

The presence of `agent/` and `TENNIS_ANALYTICAL_QUESTIONS_MCP.md` suggests a strong focus on "Chat with Data".

- **Benchmark Suite Implementation**: Convert the `TENNIS_ANALYTICAL_QUESTIONS_MCP.md` into an automated test suite.
    - **Why?** To quantitatively measure the accuracy of your Text-to-SQL agent.
    - **How?** Create a script that runs these natural language questions through your agent and compares the generated SQL/Answer against a "Gold Standard" or manually verified result for a subset.
- **Dynamic Few-Shot Prompting**:
    - **Improvement**: If not already present in `agent_factory.py`, implement a vector store (Chroma/FAISS) containing "Question -> Valid SQL" pairs. When a user asks a question, retrieve the most similar training examples to inject into the LLM prompt. This drastically improves SQL generation accuracy for complex metrics like "break points converted in deciding sets".
- **MCP Server Exposure**:
    - **Evolution**: Turn this backend into a true [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server.
    - **Why?** This would allow *other* AI agents (like Claude Desktop or other assistants) to "install" your tennis database as a tool and query it natively.
- **"Play Style" Clustering**:
    - **New Feature**: Use unsupervised learning (K-Means) on the point-by-point MCP data to categorize players (e.g., "Aggressive Baseriner", "Counter-Puncher"). Allow users to ask "Who plays most like Roger Federer in the Top 100?".

## 2. Frontend & UX Enhancements (The "Face")

The frontend uses React 19 and Recharts, which is excellent.

- **Head-to-Head Comparison Mode**:
    - **New Feature**: Currently, the flow calls for single-player stats. Add a "Compare" mode where users select Player A and Player B. The charts (Radar, Line) should overlay both players' data for direct visual comparison.
- **Match Simulator**:
    - **Fun/Engagement**: Use the calculated probabilities (Serve Win %, Return Win %) to run a Monte Carlo simulation of a match between any two selected players. Visualize the "Match Prediction" with a win probability meter.
- **Natural Language Dashboard Builder**:
    - **Evolution**: Instead of pre-defined tabs, allow the "Ask AI" feature to generate *charts* on the fly.
    - **How?** The API `QueryResponse` already returns `data`. Update the frontend to detect if the data is time-series or categorical and automatically render the appropriate Plotly/Recharts component instead of just text/tables.

## 3. Backend & Infrastructure (The "Backbone")

- **DuckDB Concurrency**:
    - **Critical Check**: DuckDB is embedded. Ensure your `DatabaseService` manages connections correctly, especially with FastAPI's async nature. If you scale, consider using `duckdb.connect()` with `read_only=True` for the query threads to avoid lock contention.
- **Caching Layer**:
    - **Improvement**: `data_flow.md` mentions caching. Ensure this is robust (e.g., Redis or disk-based LRU) because analytical queries on millions of points can be slow.
- **Docker Compose Setup**:
    - **DevOps**: Currently using `concurrently` for `npm run dev`. Create a `docker-compose.yml` that defines `backend`, `frontend`, and potentially a `redis` service. This makes onboarding new developers (or yourself on a new machine) instant and ensures environment consistency.

## 4. Data Engineering

- **Real-Time Ingestion**:
    - **Evolution**: If the MCP data source updates frequently (e.g., weekly GitHub dumps), build a "Sync" button or a background cron job (using Celery/Arq) to fetch the latest csv/sql dump and merge it into `tennis_data_with_mcp.db` without downtime.
- **Data Validation**:
    - **Quality**: Implement checks (using Pydantic or Great Expectations) to ensure no negative durations, impossible scores (e.g., 7-5 in a tiebreak set without a tiebreak flag), or duplicate match IDs.

## Summary of Recommended Next Steps

1.  **Immediate:** Verify `DatabaseService` concurrency settings in FastAPI.
2.  **Feature:** Build the "Head-to-Head" comparison UI.
3.  **AI:** Implement Dynamic Few-Shot prompting using the questions file as a source of truth.
