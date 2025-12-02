#!/bin/bash
# Start the SourceInfo API server

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Start the server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
