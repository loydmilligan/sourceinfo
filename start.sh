#!/bin/bash
# Start both the SourceInfo API and Web UI

cd "$(dirname "$0")"

echo "Starting SourceInfo..."
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    # Use tmux for side-by-side terminals
    tmux new-session -d -s sourceinfo -n api './run_api.sh'
    tmux new-window -t sourceinfo -n web './run_web.sh'
    tmux attach -t sourceinfo
else
    # Fallback: Start API in background
    echo "Starting API server in background..."
    ./run_api.sh &
    API_PID=$!

    sleep 2  # Wait for API to start

    echo ""
    echo "Starting Web UI..."
    ./run_web.sh

    # Cleanup
    kill $API_PID 2>/dev/null
fi
