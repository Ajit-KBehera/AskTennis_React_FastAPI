# 🎾 AskTennis

**AskTennis** is an AI-powered analytics platform that allows users to query tennis statistics using natural language. It combines a robust SQL-based backend with LangGraph agents to answer complex questions about player performance, historical records, and match strategies.

## ✨ Features

- **Natural Language Querying**: Ask questions like _"Who has the best win rate on grass in the last 5 years?"_ and get instant answers.
- **Deep Statistical Analysis**: Powered by DuckDB and a rich dataset covering the Open Era.
- **Agentic AI**: Uses LangGraph to decompose complex queries into SQL steps.
- **Modern UI**: React 19 frontend for visualizing data and interacting with the agent.
- **Exclusion Logic**: Intelligent bundler to prepare codebase context without noise (excludes `node_modules`, lock files, etc.).

## 🏗️ Tech Stack

### Backend

- **Framework**: FastAPI (Python)
- **Database**: DuckDB (`tennis_data_with_mcp.db`)
- **AI/Agents**: LangGraph, LangChain
- **Analysis**: Pandas, NumPy

### Frontend

- **Framework**: React 19 (Vite)
- **Styling**: CSS Modules / Vanilla CSS
- **Visualization**: Recharts / Plotly (planned)

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the API server:

```bash
python main.py
# Server running at http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App running at http://localhost:5173
```

## 🤖 CI/CD

This project uses **GitHub Actions** for Continuous Integration.

- **Frontend**: Automatically lints (`eslint`) and builds (`vite build`) on push/PR.
- **Backend**: automatically installs dependencies and lints with `flake8`.

Workflows are defined in `.github/workflows/ci.yml`.

## 📂 Project Structure

```
AskTennis/
├── backend/                # FastAPI application
│   ├── agent/             # LangGraph agent definitions
│   ├── api/               # API routers and endpoints
│   ├── services/          # Core business logic (QueryProcessor)
│   ├── data/              # Database files
│   └── main.py            # Entry point
├── frontend/               # React application
│   ├── src/               # Components and logic
│   └── public/            # Static assets
├── bundler.py              # Utility to bundle code for AI analysis
├── TENNIS_ANALYTICAL_QUESTIONS.md  # Benchmark questions
└── project_evolution.md    # Roadmap and architecture notes
```

## 🛠️ Utility Scripts

**Bundler**:
Generate a single context file for LLM analysis, excluding ignored directories and lock files.

```bash
python3 bundler.py
```

## 🗺️ Roadmap

See `project_evolution.md` for the detailed evolution plan, including:

- 🧠 Benchmark Suite for Text-to-SQL accuracy
- 🎨 Head-to-Head Comparison UI
- 🐳 Docker Compose setup
- 🔌 MCP Server integration

## 📄 License

MIT
