# AskTennis - FastAPI + React

Tennis match analysis and AI query system.

## Project Structure

- `backend/`: FastAPI server with LangGraph agent.
- `frontend/`: React frontend using Vite.

## Getting Started

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Legacy Migration
The original monolithic Streamlit project has been completely migrated to this decoupled FastAPI + React architecture. All Streamlit-specific dependencies and UI code have been removed from the backend to ensure a clean API service.
