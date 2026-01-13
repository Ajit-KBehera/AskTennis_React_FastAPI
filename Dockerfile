# Use an official Python runtime as a parent image
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry (optional, if you use it) – otherwise use pip
RUN curl -sSL https://install.python-poetry.org | python - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# -------------------
# Build stage for the frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# -------------------
# Final stage
FROM base AS final
WORKDIR /app

# Copy backend source code
COPY backend/ ./backend
COPY pyproject.toml poetry.lock ./

# Install Python dependencies (using Poetry if present, fallback to pip)
RUN if [ -f poetry.lock ]; then \
        poetry install --no-root --only main; \
    else \
        pip install -r requirements.txt; \
    fi

# Copy built frontend assets into backend static folder (FastAPI can serve them)
COPY --from=frontend-build /app/frontend/build ./backend/static

# Expose the port that Cloud Run expects (environment variable $PORT)
ENV PORT=${PORT:-8080}
EXPOSE $PORT

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
