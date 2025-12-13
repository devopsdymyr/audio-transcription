# Quick Start Guide - Voice Transcription

## ✅ Setup Complete!

The repository has been cloned and configured. Here's what's ready:

### What's Working
- ✅ Dependencies installed (uv, Python packages)
- ✅ Audio recording script created (`record_voice.py`)
- ✅ Sample audio downloaded
- ✅ Docker setup for GLIBC compatibility

### Known Issue
⚠️ **GLIBC Version Mismatch**: The pre-compiled binary requires GLIBC 2.38, but your system has 2.35. Use Docker for transcription.

## 🎤 Test Your Voice - Step by Step

### Method 1: Record Locally, Transcribe in Docker (Recommended)

**Step 1: Record your voice**
```bash
cd /home/kathirvel-new/poc/cookbook/examples/audio-transcription-cli
export PATH="$HOME/.local/bin:$PATH"
uv run python record_voice.py --output my_voice.wav --duration 10.0
```
*Speak for 10 seconds when prompted*

**Step 2: Transcribe using Docker**
```bash
# Build Docker image (first time only)
docker build -t audio-transcription-cli .

# Run transcription
docker run -it --rm \
    -v "$(pwd):/app" \
    -w /app \
    audio-transcription-cli \
    bash -c "export PATH=\"/root/.local/bin:\$PATH\" && uv run transcribe --audio ./my_voice.wav"
```

### Method 2: All-in-One Docker (If you have audio device access)

```bash
./docker-run.sh
# Then inside container:
uv run python record_voice.py --output my_voice.wav --duration 10.0
uv run transcribe --audio ./my_voice.wav
```

## 📝 Example Commands

### Record different durations
```bash
# 5 seconds
uv run python record_voice.py --duration 5.0

# 10 seconds  
uv run python record_voice.py --duration 10.0

# Custom output file
uv run python record_voice.py --output custom_name.wav --duration 8.0
```

### Transcribe with options
```bash
# Basic transcription
uv run transcribe --audio ./my_voice.wav

# With audio playback
uv run transcribe --audio ./my_voice.wav --play-audio

# With text cleaning
uv run transcribe --audio ./my_voice.wav --clean-text
```

## 🐳 Docker Quick Reference

```bash
# Build image
docker build -t audio-transcription-cli .

# Run interactive shell
docker run -it --rm -v "$(pwd):/app" -w /app audio-transcription-cli bash

# Run single command
docker run -it --rm -v "$(pwd):/app" -w /app audio-transcription-cli \
    bash -c "export PATH=\"/root/.local/bin:\$PATH\" && uv run transcribe --audio ./my_voice.wav"
```

## 📁 Project Structure

```
audio-transcription-cli/
├── record_voice.py          # Record audio from microphone
├── test_voice_transcription.sh  # End-to-end test script
├── docker-run.sh           # Docker convenience script
├── Dockerfile              # Docker image definition
├── SETUP_GUIDE.md          # Detailed setup guide
├── QUICK_START.md          # This file
└── audio-samples/          # Sample audio files
```

## 🎯 Next Steps

1. **Test recording**: Run `uv run python record_voice.py` to test microphone
2. **Build Docker image**: `docker build -t audio-transcription-cli .`
3. **Record and transcribe**: Follow Method 1 above
4. **Experiment**: Try different durations and transcription options

## 💡 Tips

- The recording script uses 48kHz sample rate (required by LFM2-Audio model)
- Record in a quiet environment for best results
- Longer recordings (10+ seconds) often produce better transcriptions
- Use `--clean-text` flag for better formatted output

## ❓ Troubleshooting

**"No module named pyaudio"**
- Run `uv sync` to install dependencies

**"GLIBC version not found"**
- Use Docker for transcription (see Method 1)

**"Audio device not found"**
- Check microphone permissions
- Try running with `sudo` (for testing only)
- Use Docker with `--device /dev/snd` flag

**Recording fails**
- Ensure microphone is connected and working
- Check system audio settings
- Try: `arecord -d 5 test.wav` to test system recording

