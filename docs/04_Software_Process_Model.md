# 🔄 AskTennis AI - Software Process Model

## Overview

AskTennis AI follows an **Agile Software Development Life Cycle (SDLC)**, specifically leveraging the **Scrum** framework adapted for AI-driven development. The process emphasizes iterative development, continuous integration, and rapid feedback loops, which is essential for tuning AI agent performance.

## 🔄 SDLC Phases

### 1. **Planning & Requirements**
-   **User Stories**: Define user needs (e.g., "As a user, I want to compare player stats").
-   **AI Capabilities**: Determine if a requirement needs LLM reasoning or simple SQL.
-   **Tech Specs**: Define API contracts (OpenAPI/Swagger) between React and FastAPI.

### 2. **Design & Architecture**
-   **Frontend**: Component hierarchy in React, atomic design principles.
-   **Backend**: RESTful endpoint definition, Pydantic models.
-   **Database**: Schema updates (Schema migrations using Alembic if needed).

### 3. **Development (Iterative)**
-   **Feature Branching**: Git workflow (feature/* branches).
-   **Local Dev**:
    -   Frontend: `npm run dev` (Vite hmr).
    -   Backend: `uvicorn main:app --reload`.
-   **Prompt Engineering**: Iterative testing of system prompts (`tennis_prompts.py`).

### 4. **Testing & Validation**
-   **Unit Tests**: Pytest for backend logic.
-   **Integration Tests**: Testing the API endpoints.
-   **AI Evaluation**: Verifying answer accuracy against known ground truth (e.g., "Who won Wimbledon 2022?").

### 5. **Deployment**
-   **Docker**: Containerization of Frontend (Nginx serve) and Backend (Python image).
-   **CI/CD**: GitHub Actions (planned) for automated testing and deployment.

## 🚀 Workflows

### AI Feature Development Flow
1.  **Identify Gap**: "Agent fails to understand 'Clay Court Kings'".
2.  **Data Analysis**: Check if data exists in `matches` table.
3.  **Prompt/Tool Update**: Add `Clay` context or specific mapping tool.
4.  **Test**: Run specific queries to verify fix.
5.  **Deploy**: Push changes to production.

## 🤝 Collaboration
-   **Code Reviews**: GitHub Pull Requests.
-   **Documentation**: Maintaining this `docs/` folder to keep architecture transparent.
