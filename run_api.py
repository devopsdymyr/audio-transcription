#!/usr/bin/env python3
"""Run the FastAPI server for audio transcription."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.audio_transcription_cli.api:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False  # Disable reload for production
    )

