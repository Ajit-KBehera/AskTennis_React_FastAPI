# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# build-essential for compiling some python packages if needed
# curl for healthchecks
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port (FastAPI default is 8000)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
# Use host 0.0.0.0 to be accessible from outside container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
