# Live Audio Transcription API

## 🚀 Quick Start

### Start the Server

```bash
cd /home/kathirvel-new/poc/audio-transcription-cli-standalone
export PATH="$HOME/.local/bin:$PATH"
./START_SERVER.sh
```

Or manually:
```bash
uv run python run_api.py
```

The server will start on **http://localhost:8001**

### Access the Web Interface

Open your browser and go to:
**http://localhost:8001**

## Features

- 🎤 **Live Audio Recording** - Record directly from your browser
- ⚡ **Real-time Transcription** - Get transcription as you speak
- 🔄 **WebSocket Streaming** - Live updates via WebSocket
- 🎨 **Modern UI** - Beautiful, responsive interface
- 🔊 **Audio Visualization** - Visual feedback while recording

## API Endpoints

### Web Interface
- `GET /` - Main web interface with live recording

### REST API
- `POST /api/transcribe` - Transcribe audio file
  ```json
  {
    "audio_data": "base64_encoded_audio",
    "sample_rate": 48000,
    "format": "webm"
  }
  ```

### WebSocket
- `WS /ws/transcribe` - Real-time transcription streaming
  - Send audio chunks as base64 encoded data
  - Receive transcription updates in real-time

## Usage

1. **Start the server** (see above)
2. **Open browser** to http://localhost:8001
3. **Click "Start Recording"** button
4. **Speak** - transcription appears in real-time
5. **Click "Stop Recording"** when done

## Requirements

- Python 3.12+
- uv package manager
- Model files (auto-downloaded on first run)
- Microphone access in browser

## Troubleshooting

### Port Already in Use
If port 8001 is in use, edit `run_api.py` and change the port number.

### Model Not Loading
The model downloads automatically on first startup. This may take a few minutes.

### Audio Not Working
- Check browser microphone permissions
- Ensure HTTPS or localhost (required for microphone access)
- Check browser console for errors

## Development

The server supports auto-reload. Edit files and changes will be reflected automatically.

## Docker Support

For GLIBC compatibility, use Docker:

```bash
docker build -t audio-transcription-api .
docker run -p 8001:8001 audio-transcription-api
```

