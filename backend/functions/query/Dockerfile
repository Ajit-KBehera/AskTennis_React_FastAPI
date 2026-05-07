FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD uvicorn functions.query.main:app --host 0.0.0.0 --port ${PORT}
