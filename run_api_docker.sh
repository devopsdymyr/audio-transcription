#!/bin/bash
# Run the FastAPI server in Docker to avoid GLIBC issues

set -e

cd "$(dirname "$0")"

echo "🐳 Starting API server in Docker..."
echo ""

# Check if we have the audio-transcription-cli image
if docker images | grep -q "audio-transcription-cli"; then
    IMAGE="audio-transcription-cli"
    echo "✅ Using existing Docker image: $IMAGE"
else
    echo "❌ Docker image not found. Building..."
    docker build -t audio-transcription-cli .
    IMAGE="audio-transcription-cli"
fi

# Stop existing container if running
docker stop audio-transcription-api 2>/dev/null || true
docker rm audio-transcription-api 2>/dev/null || true

# Run container with API server
echo "🚀 Starting container..."
docker run -d \
    --name audio-transcription-api \
    -p 8001:8001 \
    -v "$(pwd):/app" \
    -w /app \
    $IMAGE \
    bash -c "export PATH=\"/root/.local/bin:\$PATH\" && uv run python run_api.py"

echo "✅ Server started!"
echo ""
echo "📋 View logs: docker logs -f audio-transcription-api"
echo "🛑 Stop server: docker stop audio-transcription-api"
echo "🌐 Access at: http://localhost:8001"
echo ""

# Show logs
sleep 5
docker logs audio-transcription-api 2>&1 | tail -20
