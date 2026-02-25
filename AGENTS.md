# AGENTS.md

## Cursor Cloud specific instructions

### Overview

AskTennis is an AI-powered tennis analytics platform with a **FastAPI backend** (Python 3.11+) and a **React 19 frontend** (Vite 7, TypeScript). See the `README.md` for full architecture and API endpoint documentation.

### Running services

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| Backend | `cd backend && source venv/bin/activate && python main.py` | 8000 | Requires `GOOGLE_API_KEY` in `backend/.env` (placeholder suffices for non-AI endpoints) |
| Frontend | `cd frontend && npx vite --host 0.0.0.0` | 5173 | Connects to backend at `http://localhost:8000` by default |
| Both | `npm run dev` (from root) | 8000 + 5173 | Uses `concurrently`; backend must use the venv Python |

### Key gotchas

- **`GOOGLE_API_KEY` is required at startup.** The backend's `Config.__init__` raises `ValueError` if this env var is missing or empty. For dev/testing without a real key, set `GOOGLE_API_KEY=placeholder-for-dev-setup` in `backend/.env`. All non-AI endpoints (auth, filters, stats, matches, health) work without a real key.
- **Database files live in `backend/data/`.** This directory is not in the repo; create it with `mkdir -p backend/data`. The auth DB (`asktennis_auth.db`) is auto-created on first startup. The tennis data DB (`tennis_data_with_mcp.db`) will be an empty file unless populated externally.
- **The backend venv must be activated** before running `python main.py`. The root `npm run dev` script calls `python3 backend/main.py` which uses the system Python — if you need the venv, run the backend manually instead.
- **No ESLint config exists** in the frontend. Use `npx tsc --noEmit` for type checking (`npm run typecheck`).

### Testing

- **Backend:** `cd backend && source venv/bin/activate && pytest tests/ -v` (46 tests, all mocked — no API key or real DB needed)
- **Frontend:** `cd frontend && npx vitest run` (5 tests) or `npm run typecheck` for type checking
- Backend tests use in-memory SQLite and mock the LangGraph agent/query processor, so no external services are required.

### Environment files

Copy from `.env.example` in both `backend/` and `frontend/` directories. The backend `.env` must contain at least `GOOGLE_API_KEY` (even a placeholder). The frontend `.env` only needs `VITE_API_KEY=dev-key`.
