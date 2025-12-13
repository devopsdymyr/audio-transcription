# 🎤 Audio Transcription - Real-Time Speech-to-Text

A powerful, local-first audio transcription tool with live streaming capabilities. Transcribe audio files or record from your microphone in real-time using the LFM2-Audio-1.5B model - all running completely offline on your machine.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ✨ Key Features

- 🎤 **Live Audio Recording** - Record directly from your browser microphone
- ⚡ **Real-Time Transcription** - Get transcription as you speak (live streaming)
- 🔄 **WebSocket Streaming** - Live updates via WebSocket for instant feedback
- 🎨 **Modern Web Interface** - Beautiful, responsive UI with audio visualization
- 🐳 **Docker Support** - Easy deployment with Docker (solves GLIBC compatibility)
- 📝 **File Transcription** - Transcribe existing audio files (WAV, MP3, WebM)
- 🔒 **100% Local** - All processing happens on your machine, no cloud services
- 🚀 **Fast Processing** - Optimized for speed with chunk-based processing

## 🎯 Model Information

### LFM2-Audio-1.5B Model

- **Model**: LFM2-Audio-1.5B (Liquid AI)
- **Size**: ~1.5B parameters
- **Quantization**: Q8_0 (8-bit quantization)
- **Format**: GGUF (llama.cpp compatible)
- **Auto-Download**: Models download automatically on first run
- **Location**: `LFM2-Audio-1.5B-GGUF/` (created automatically)

### Model Files (Auto-Downloaded)

- `LFM2-Audio-1.5B-Q8_0.gguf` - Main model file (~1.5GB)
- `mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf` - Audio encoder
- `audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf` - Audio decoder
- Platform-specific binaries (auto-detected)

### Supported Platforms

- ✅ Ubuntu x64 (Linux)
- ✅ Ubuntu ARM64 (Linux ARM)
- ✅ macOS ARM64 (Apple Silicon)
- ✅ Android ARM64

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (or Docker)
- **uv** package manager ([Install uv](https://github.com/astral-sh/uv))
- **Docker** (optional, for GLIBC compatibility)
- **Microphone** (for live recording)

### Option 1: Run with Docker (Recommended)

Docker is recommended because it solves GLIBC compatibility issues and includes all dependencies.

#### Step 1: Clone Repository

```bash
git clone https://github.com/devopsdymry/audio-transcription.git
cd audio-transcription
```

#### Step 2: Start Docker Container

```bash
./run_api_docker.sh
```

This will:
- Build Docker image (first time only)
- Download models automatically
- Start API server on port 8001

#### Step 3: Access Web Interface

Open your browser: **http://localhost:8001**

### Option 2: Run Locally (Advanced)

**Note**: Requires GLIBC 2.38+. If you have GLIBC 2.35 (Ubuntu 22.04), use Docker instead.

#### Step 1: Install Dependencies

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y portaudio19-dev libasound2-dev ffmpeg

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

#### Step 2: Install Python Dependencies

```bash
cd audio-transcription
uv sync
```

#### Step 3: Start Server

```bash
uv run python run_api.py
```

Server will start on **http://localhost:8001**

## 📖 Detailed Usage

### Web Interface

1. **Start Recording**
   - Click "Start Recording" button
   - Allow microphone access when prompted
   - Start speaking

2. **Live Transcription**
   - Text appears in real-time as you speak
   - Updates every 2-3 seconds
   - Audio visualization shows recording status

3. **Stop Recording**
   - Click "Stop Recording" when done
   - Final transcription will be processed
   - Complete text displayed

### Command Line (CLI)

#### Transcribe Audio File

```bash
# Using Docker
docker exec -it audio-transcription-api uv run transcribe --audio ./audio-samples/barackobamafederalplaza.mp3

# Or locally
uv run transcribe --audio ./path/to/audio.wav
```

#### Record and Transcribe

```bash
# Record 10 seconds of audio
uv run python record_voice.py --output my_voice.wav --duration 10.0

# Transcribe the recording
uv run transcribe --audio ./my_voice.wav
```

### API Endpoints

#### REST API

```bash
# Transcribe audio file
curl -X POST http://localhost:8001/api/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio",
    "sample_rate": 48000,
    "format": "webm"
  }'
```

#### WebSocket (Live Streaming)

```javascript
const ws = new WebSocket('ws://localhost:8001/ws/transcribe');

// Send audio chunk
ws.send(JSON.stringify({
  type: 'audio_chunk',
  data: base64Audio,
  format: 'webm',
  sample_rate: 48000
}));

// End recording
ws.send(JSON.stringify({ type: 'end' }));
```

## 🐳 Docker Details

### Build Docker Image

```bash
docker build -t audio-transcription-cli .
```

### Run Container

```bash
docker run -d \
  --name audio-transcription-api \
  -p 8001:8001 \
  -v $(pwd):/app \
  audio-transcription-cli \
  bash -c "export PATH='/root/.local/bin:$PATH' && uv run python run_api.py"
```

### View Logs

```bash
docker logs -f audio-transcription-api
```

### Stop Container

```bash
docker stop audio-transcription-api
docker rm audio-transcription-api
```

## 📁 Project Structure

```
audio-transcription/
├── src/audio_transcription_cli/    # Main source code
│   ├── api.py                      # FastAPI server with WebSocket
│   ├── transcribe.py               # CLI transcription script
│   ├── model_wrapper.py            # Model interface
│   ├── model_downloader.py         # Auto-download models
│   └── ...
├── run_api.py                      # Start API server
├── run_api_docker.sh               # Docker startup script
├── record_voice.py                 # Microphone recording script
├── Dockerfile                      # Docker image definition
├── pyproject.toml                  # Python dependencies
├── README.md                       # This file
└── LFM2-Audio-1.5B-GGUF/          # Models (auto-created)
```

## 🔧 Configuration

### Environment Variables

```bash
# Base directory for models
export LIQUID_ASR_BASE_DIR=/path/to/models

# Sample rate (default: 48000)
export LIQUID_ASR_SAMPLE_RATE=48000
```

### Model Download

Models are **automatically downloaded** on first run. They are stored in:
- `LFM2-Audio-1.5B-GGUF/` directory
- Size: ~5GB total
- Download happens automatically - no manual steps needed

## 🧪 Testing

### Test with Sample Audio

```bash
# Download sample audio
uv run python download_audio_samples.py

# Transcribe sample
uv run transcribe --audio ./audio-samples/barackobamafederalplaza.mp3
```

### Test Live Recording

1. Start server: `./run_api_docker.sh`
2. Open browser: http://localhost:8001
3. Click "Start Recording"
4. Speak for 10-20 seconds
5. Watch text appear in real-time
6. Click "Stop Recording"

## 🐛 Troubleshooting

### GLIBC Version Error

**Error**: `GLIBC_2.38 not found`

**Solution**: Use Docker (recommended) or upgrade your system.

```bash
# Check GLIBC version
ldd --version

# Use Docker instead
./run_api_docker.sh
```

### Port Already in Use

**Error**: `address already in use`

**Solution**: Change port in `run_api.py` or stop existing server.

```bash
# Stop existing server
docker stop audio-transcription-api
# Or
pkill -f run_api.py
```

### Microphone Not Working

**Error**: `Microphone access denied`

**Solution**:
- Check browser permissions
- Use HTTPS or localhost (required for microphone)
- Check system audio settings

### Model Download Fails

**Error**: `Failed to download models`

**Solution**:
- Check internet connection
- Ensure sufficient disk space (~5GB)
- Check Hugging Face access

### Audio Conversion Fails

**Error**: `Audio conversion failed`

**Solution**: Install ffmpeg

```bash
sudo apt-get install ffmpeg
# Or use Docker (includes ffmpeg)
```

## 📊 Performance

- **Transcription Speed**: ~2-5 seconds per 2-second audio chunk
- **Latency**: 2-5 seconds behind speech (live streaming)
- **Accuracy**: High accuracy for clear speech
- **Model Size**: ~1.5GB (Q8_0 quantization)
- **Memory**: ~2-4GB RAM required

## 🔐 Privacy & Security

- ✅ **100% Local Processing** - No data leaves your machine
- ✅ **No Cloud Services** - Everything runs offline
- ✅ **No API Keys Required** - Completely free and open
- ✅ **No Data Collection** - Your audio never leaves your device

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project uses the LFM2-Audio-1.5B model from Liquid AI. Please check their license terms.

## 🙏 Acknowledgments

- [Liquid AI](https://liquid.ai/) for the LFM2-Audio-1.5B model
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for efficient inference
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/devopsdymry/audio-transcription/issues)
- **Documentation**: See `README_API.md` and `SETUP_GUIDE.md`

## 🎯 Use Cases

- 📝 **Meeting Transcription** - Transcribe meetings in real-time
- 🎙️ **Podcast Transcription** - Convert podcasts to text
- 📚 **Lecture Notes** - Transcribe lectures automatically
- 🗣️ **Voice Notes** - Convert voice memos to text
- ♿ **Accessibility** - Real-time captions for audio

---

**Made with ❤️ for local-first AI applications**
