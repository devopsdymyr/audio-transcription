# Audio Transcription CLI - Setup Guide

## Current Status

The repository has been cloned and set up. However, there's a **GLIBC compatibility issue** that needs to be addressed:

### GLIBC Version Issue

- **System GLIBC**: 2.35 (Ubuntu 22.04)
- **Required GLIBC**: 2.38 (for the pre-compiled binaries)

The pre-compiled `llama-lfm2-audio` binary requires GLIBC 2.38, but Ubuntu 22.04 only provides GLIBC 2.35.

## Solutions

### Option 1: Use Docker (Recommended)

Use the provided Docker setup which uses Ubuntu 24.04 with GLIBC 2.39:

```bash
# Build and run Docker container
./docker-run.sh

# Inside the container, record and transcribe:
uv run python record_voice.py --output my_voice.wav --duration 5.0
uv run transcribe --audio ./my_voice.wav
```

### Option 2: Record Locally, Transcribe in Docker

1. **Record your voice locally** (this works fine):
   ```bash
   uv run python record_voice.py --output my_voice.wav --duration 5.0
   ```

2. **Transcribe using Docker**:
   ```bash
   docker build -t audio-transcription-cli .
   docker run -it --rm \
       -v "$(pwd):/app" \
       -w /app \
       audio-transcription-cli \
       bash -c "export PATH=\"/root/.local/bin:\$PATH\" && uv run transcribe --audio ./my_voice.wav"
   ```

### Option 3: Upgrade System (Not Recommended)

Upgrading GLIBC on Ubuntu 22.04 is risky and can break system stability. It's better to use Docker.

## Quick Test

### Test Recording (Works Locally)

```bash
# Record 5 seconds of audio
uv run python record_voice.py --output test.wav --duration 5.0
```

### Test Transcription (Requires Docker or GLIBC 2.38+)

```bash
# Using Docker
docker run -it --rm \
    -v "$(pwd):/app" \
    -w /app \
    audio-transcription-cli \
    bash -c "export PATH=\"/root/.local/bin:\$PATH\" && uv run transcribe --audio ./test.wav"
```

## Files Created

1. **`record_voice.py`** - Script to record audio from microphone
2. **`test_voice_transcription.sh`** - End-to-end test script
3. **`Dockerfile`** - Docker image with Ubuntu 24.04
4. **`docker-run.sh`** - Convenience script to run Docker container

## Next Steps

1. Test the recording script locally to ensure microphone access works
2. Use Docker for transcription to avoid GLIBC issues
3. Once working, you can integrate this into your workflow

