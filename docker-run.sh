#!/bin/bash
# Run audio transcription in Docker container with proper GLIBC version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t audio-transcription-cli .

# Run container with audio device access
echo "🚀 Starting container..."
docker run -it --rm \
    --device /dev/snd \
    -v "$SCRIPT_DIR:/app" \
    -w /app \
    audio-transcription-cli \
    bash -c "export PATH=\"/root/.local/bin:\$PATH\" && bash"

