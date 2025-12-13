#!/bin/bash
# Test script for voice transcription end-to-end

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PATH="$HOME/.local/bin:$PATH"

echo "🎤 Voice Transcription Test Script"
echo "===================================="
echo ""

# Step 1: Record voice
echo "📝 Step 1: Recording your voice..."
echo "💡 You'll have 5 seconds to speak after the countdown"
echo ""
read -p "Press Enter to start recording..."

uv run python record_voice.py --output my_voice.wav --duration 5.0

if [ ! -f "my_voice.wav" ]; then
    echo "❌ Failed to record audio"
    exit 1
fi

echo ""
echo "✅ Recording saved to: my_voice.wav"
echo ""

# Step 2: Transcribe
echo "📝 Step 2: Transcribing your voice..."
echo ""

uv run transcribe --audio ./my_voice.wav

echo ""
echo "🎉 Transcription complete!"
echo ""

