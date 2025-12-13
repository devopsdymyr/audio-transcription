#!/usr/bin/env python3
"""Simple script to record audio from microphone and save it as a WAV file."""

import argparse
import sys
import time

try:
    import pyaudio
    import soundfile as sf
    import numpy as np
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("💡 Make sure you've run 'uv sync' to install dependencies")
    sys.exit(1)


def record_audio(
    output_file: str,
    duration: float = 5.0,
    sample_rate: int = 48000,
    channels: int = 1,
    chunk_size: int = 1024,
):
    """
    Record audio from microphone and save to file.

    Args:
        output_file: Path to output WAV file
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz (default: 48000 for LFM2-Audio)
        channels: Number of audio channels (1 = mono)
        chunk_size: Audio chunk size for processing
    """
    print(f"🎤 Recording audio for {duration} seconds...")
    print("💡 Speak now! Recording will start in 1 second...")
    time.sleep(1)

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    try:
        # Open audio stream
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size,
        )

        print("🔴 Recording...")
        frames = []

        # Record audio
        for _ in range(0, int(sample_rate / chunk_size * duration)):
            data = stream.read(chunk_size)
            frames.append(data)

        print("⏹️  Recording stopped")

        # Stop and close stream
        stream.stop_stream()
        stream.close()

        # Convert frames to numpy array
        audio_data = np.frombuffer(b"".join(frames), dtype=np.int16)
        # Normalize to float32 range [-1, 1]
        audio_data = audio_data.astype(np.float32) / 32768.0

        # Save to file
        sf.write(output_file, audio_data, sample_rate, subtype="PCM_16")
        print(f"✅ Audio saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error during recording: {e}")
        raise
    finally:
        audio.terminate()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Record audio from microphone and save as WAV file"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="my_voice_recording.wav",
        help="Output WAV file path (default: my_voice_recording.wav)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        default=5.0,
        help="Recording duration in seconds (default: 5.0)",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=48000,
        help="Sample rate in Hz (default: 48000)",
    )
    args = parser.parse_args()

    try:
        record_audio(
            output_file=args.output,
            duration=args.duration,
            sample_rate=args.sample_rate,
        )
    except KeyboardInterrupt:
        print("\n⚠️  Recording interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to record audio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

