#!/bin/bash
# Start the FastAPI server for audio transcription

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"

echo "🚀 Starting Audio Transcription API Server..."
echo ""

# Kill any existing server
pkill -f "run_api.py" 2>/dev/null
sleep 2

# Start server
uv run python run_api.py

