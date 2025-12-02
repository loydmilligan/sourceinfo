#!/bin/bash
# Start the SourceInfo Web UI development server

cd "$(dirname "$0")/web"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo ""
echo "Starting SourceInfo Web UI..."
echo "  Web UI: http://localhost:5173"
echo "  API:    http://localhost:8000 (make sure to start with ./run_api.sh)"
echo ""

npm run dev
