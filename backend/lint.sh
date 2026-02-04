#!/bin/bash
# Convenience script to run linting and formatting locally

# Change to backend directory if not already there
cd "$(dirname "$0")"

echo "🔍 Running Ruff checks..."
ruff check . --fix

echo "✨ Running Ruff formatter..."
ruff format .

echo "✅ Local checks complete!"
