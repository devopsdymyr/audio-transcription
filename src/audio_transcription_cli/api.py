"""FastAPI backend for real-time audio transcription with live streaming."""

import asyncio
import base64
import io
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .config import Config
from .model_downloader import ModelDownloader
from .model_wrapper import LFM2AudioWrapper

app = FastAPI(title="Audio Transcription API", version="1.0.0")

# Global model instance (initialized on startup)
model_wrapper: LFM2AudioWrapper | None = None
model_downloader: ModelDownloader | None = None
config: Config | None = None


class TranscriptionRequest(BaseModel):
    """Request model for audio transcription."""
    audio_data: str  # Base64 encoded audio data
    sample_rate: int = 48000
    format: str = "wav"


class TranscriptionResponse(BaseModel):
    """Response model for transcription."""
    text: str
    status: str
    error: str | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    global model_wrapper, model_downloader, config
    
    print("🚀 Initializing Audio Transcription API...")
    config = Config()
    
    try:
        model_downloader = ModelDownloader(target_dir=config.base_dir)
        model_downloader.download()
        model_wrapper = LFM2AudioWrapper(model_downloader, config)
        print("✅ Model initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serve the frontend HTML page."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Audio Transcription</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 900px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            flex: 1;
            min-width: 150px;
        }
        
        .record-btn {
            background: #e74c3c;
            color: white;
        }
        
        .record-btn:hover:not(:disabled) {
            background: #c0392b;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
        }
        
        .record-btn.recording {
            background: #27ae60;
            animation: pulse 1.5s infinite;
        }
        
        .record-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .status {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: 500;
            text-align: center;
        }
        
        .status.idle {
            background: #ecf0f1;
            color: #7f8c8d;
        }
        
        .status.recording {
            background: #fff3cd;
            color: #856404;
        }
        
        .status.processing {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .transcription-box {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
            font-size: 18px;
            line-height: 1.8;
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .transcription-box.empty {
            color: #999;
            font-style: italic;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .transcription-box .live-text {
            color: #667eea;
            font-weight: 600;
        }
        
        .audio-visualizer {
            height: 80px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            position: relative;
            overflow: hidden;
        }
        
        .audio-visualizer.active {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        .visualizer-bars {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 3px;
            height: 100%;
            width: 100%;
        }
        
        .visualizer-bar {
            width: 4px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 2px;
            animation: wave 1s ease-in-out infinite;
        }
        
        @keyframes wave {
            0%, 100% { height: 20%; }
            50% { height: 80%; }
        }
        
        .info {
            margin-top: 20px;
            padding: 15px;
            background: #e8f4f8;
            border-radius: 10px;
            font-size: 0.9em;
            color: #0c5460;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Live Audio Transcription</h1>
        <p class="subtitle">Real-time speech-to-text with live streaming</p>
        
        <div class="audio-visualizer" id="visualizer">
            <div class="visualizer-bars" id="visualizerBars"></div>
            <span id="visualizer-text" style="position: absolute; color: white; font-weight: 600;">Click Record to start</span>
        </div>
        
        <div class="controls">
            <button class="record-btn" id="recordBtn" onclick="toggleRecording()">
                🎤 Start Recording
            </button>
        </div>
        
        <div class="status idle" id="status">
            Ready to record - Transcription will appear in real-time as you speak
        </div>
        
        <div class="transcription-box empty" id="transcription">
            Transcription will appear here in real-time as you speak...
        </div>
        
        <div class="info">
            💡 <strong>Tip:</strong> Speak clearly. Text appears in real-time as you speak (live streaming).
        </div>
    </div>
    
    <script>
        let mediaRecorder;
        let audioContext;
        let analyser;
        let dataArray;
        let isRecording = false;
        let ws = null;
        let audioChunks = [];
        let stream = null;
        let transcriptionText = '';
        
        // Create visualizer bars
        function createVisualizerBars() {
            const container = document.getElementById('visualizerBars');
            container.innerHTML = '';
            for (let i = 0; i < 20; i++) {
                const bar = document.createElement('div');
                bar.className = 'visualizer-bar';
                bar.style.animationDelay = (i * 0.05) + 's';
                container.appendChild(bar);
            }
        }
        
        createVisualizerBars();
        
        async function toggleRecording() {
            if (!isRecording) {
                await startRecording();
            } else {
                stopRecording();
            }
        }
        
        async function startRecording() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        sampleRate: 48000,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    } 
                });
                
                // Setup audio context for visualization
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                source.connect(analyser);
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                // Connect WebSocket for live transcription
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws/transcribe`);
                
                transcriptionText = '';
                
                ws.onopen = () => {
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.status === 'transcription') {
                        // Live streaming - append text as it comes
                        if (data.is_final) {
                            // Final transcription - replace all
                            transcriptionText = data.text;
                            updateTranscription(transcriptionText, true);
                            document.getElementById('status').className = 'status idle';
                            document.getElementById('status').textContent = '✅ Final transcription complete';
                        } else {
                            // Partial transcription - append
                            if (data.text && !transcriptionText.includes(data.text)) {
                                transcriptionText += ' ' + data.text;
                                updateTranscription(transcriptionText, false);
                            }
                        }
                    } else if (data.status === 'processing') {
                        document.getElementById('status').className = 'status processing';
                        document.getElementById('status').innerHTML = '<span class="loading"></span>' + (data.message || 'Processing...');
                    } else if (data.status === 'received') {
                        // Chunk received - show we're processing
                        console.log('Chunk received:', data.chunk);
                    } else if (data.status === 'error') {
                        updateStatus('error', 'Error: ' + data.error);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    updateStatus('error', 'Connection error');
                };
                
                ws.onclose = () => {
                    console.log('WebSocket closed');
                };
                
                // Setup MediaRecorder for chunked audio
                const options = {
                    mimeType: 'audio/webm;codecs=opus'
                };
                
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'audio/webm';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options.mimeType = '';
                    }
                }
                
                mediaRecorder = new MediaRecorder(stream, options);
                
                audioChunks = [];
                
                mediaRecorder.ondataavailable = async (event) => {
                    if (event.data.size > 0) {
                        // Store chunk locally
                        audioChunks.push(event.data);
                        
                        // Send chunk via WebSocket for live processing
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const base64Audio = reader.result.split(',')[1];
                                if (ws && ws.readyState === WebSocket.OPEN) {
                                    ws.send(JSON.stringify({
                                        type: 'audio_chunk',
                                        data: base64Audio,
                                        format: 'webm',
                                        sample_rate: 48000
                                    }));
                                }
                            };
                            reader.readAsDataURL(event.data);
                        }
                    }
                };
                
                mediaRecorder.onstop = async () => {
                    // Send end signal to process final audio
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'end' }));
                    }
                };
                
                // Record in small chunks (every 2 seconds) for live streaming
                mediaRecorder.start(2000);
                isRecording = true;
                
                // Start visualization
                visualize();
                
                // Update UI
                document.getElementById('recordBtn').classList.add('recording');
                document.getElementById('recordBtn').textContent = '⏹ Stop Recording';
                document.getElementById('status').className = 'status recording';
                document.getElementById('status').textContent = '🔴 Recording... Speak now! (Live transcription active)';
                document.getElementById('visualizer').classList.add('active');
                document.getElementById('visualizer-text').textContent = 'Recording...';
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                updateStatus('error', 'Microphone access denied. Please allow microphone access.');
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                
                // Stop visualization
                if (audioContext) {
                    audioContext.close();
                }
                
                // Stop stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                
                // Update UI
                document.getElementById('recordBtn').classList.remove('recording');
                document.getElementById('recordBtn').textContent = '🎤 Start Recording';
                document.getElementById('status').className = 'status processing';
                document.getElementById('status').innerHTML = '<span class="loading"></span>Processing final audio...';
                document.getElementById('visualizer').classList.remove('active');
                document.getElementById('visualizer-text').textContent = 'Processing...';
            }
        }
        
        function visualize() {
            if (!isRecording || !analyser) return;
            
            analyser.getByteFrequencyData(dataArray);
            
            const bars = document.querySelectorAll('.visualizer-bar');
            const step = Math.floor(dataArray.length / bars.length);
            
            bars.forEach((bar, i) => {
                const value = dataArray[i * step] || 0;
                const height = (value / 255) * 100;
                bar.style.height = Math.max(20, height) + '%';
            });
            
            requestAnimationFrame(visualize);
        }
        
        function updateTranscription(text, isFinal) {
            const transcriptionEl = document.getElementById('transcription');
            
            if (text) {
                transcriptionEl.textContent = text;
                transcriptionEl.classList.remove('empty');
                
                // Auto-scroll to bottom
                transcriptionEl.scrollTop = transcriptionEl.scrollHeight;
            }
        }
        
        function updateStatus(type, message) {
            const statusEl = document.getElementById('status');
            statusEl.className = `status ${type}`;
            statusEl.textContent = message;
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio from base64 encoded data."""
    global model_wrapper
    
    if model_wrapper is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Create temporary file
        file_ext = f".{request.format}" if request.format else ".webm"
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_audio_path = temp_file.name
        
        try:
            # Convert to WAV
            wav_path = await convert_audio_to_wav(temp_audio_path, file_ext)
            
            # Transcribe
            transcription = model_wrapper.transcribe_with_real_timing(
                audio_file_path=wav_path,
                chunk_duration=2.0,
                overlap=0.5,
                play_audio=False,
                clean_text=False,
            )
            
            return TranscriptionResponse(
                text=transcription,
                status="success"
            )
            
        finally:
            # Cleanup temp files
            for path in [temp_audio_path, temp_audio_path.replace(file_ext, '.wav')]:
                if os.path.exists(path) and path != temp_audio_path.replace(file_ext, '.wav'):
                    try:
                        os.unlink(path)
                    except:
                        pass
                        
    except Exception as e:
        return TranscriptionResponse(
            text="",
            status="error",
            error=str(e)
        )


async def convert_audio_to_wav(input_path: str, input_ext: str) -> str:
    """Convert audio file to WAV format."""
    wav_path = input_path.replace(input_ext, '.wav')
    
    # Check file size
    if not os.path.exists(input_path):
        raise Exception(f"Input file not found: {input_path}")
    
    file_size = os.path.getsize(input_path)
    if file_size < 100:  # Very small file, likely corrupted
        raise Exception(f"Audio file too small ({file_size} bytes), likely corrupted")
    
    audio_data = None
    sample_rate = None
    
    # Try pydub first (better WebM support)
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(48000).set_channels(1)
        audio.export(wav_path, format="wav")
        audio_data, sample_rate = sf.read(wav_path)
    except Exception as pydub_error:
        # Try ffmpeg conversion
        import subprocess
        try:
            result = subprocess.run(
                ['ffmpeg', '-i', input_path, '-ar', '48000', '-ac', '1', '-f', 'wav', '-y', wav_path],
                check=True,
                capture_output=True,
                timeout=15
            )
            if not os.path.exists(wav_path):
                raise Exception("ffmpeg conversion failed - output file not created")
            audio_data, sample_rate = sf.read(wav_path)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            raise Exception(f"ffmpeg conversion failed: {error_output}")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            # Try direct read as fallback
            try:
                audio_data, sample_rate = sf.read(input_path)
            except Exception as read_error:
                raise Exception(f"All conversion methods failed. Pydub: {str(pydub_error)}, FFmpeg: {str(e)}, Direct read: {str(read_error)}")
    
    if audio_data is None or len(audio_data) == 0:
        raise Exception("Failed to read audio data or empty audio")
    
    # Ensure mono and correct sample rate
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    if sample_rate != 48000:
        from scipy import signal
        num_samples = int(len(audio_data) * 48000 / sample_rate)
        if num_samples > 0:
            audio_data = signal.resample(audio_data, num_samples)
            sample_rate = 48000
        else:
            raise Exception("Invalid audio data after resampling")
    
    # Save as WAV
    sf.write(wav_path, audio_data, sample_rate, subtype='PCM_16')
    
    # Verify output file
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
        raise Exception("Failed to create valid WAV file")
    
    return wav_path


async def process_audio_chunk_live(websocket: WebSocket, audio_bytes: bytes, chunk_num: int, model: LFM2AudioWrapper):
    """Process a single audio chunk for live streaming transcription."""
    temp_path = None
    wav_path = None
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        # Convert to WAV
        wav_path = await convert_audio_to_wav(temp_path, '.webm')
        
        # Transcribe chunk (fast method)
        loop = asyncio.get_event_loop()
        transcription = await loop.run_in_executor(
            None,
            model.transcribe_audio_file,
            wav_path
        )
        
        # Send partial result for live streaming
        if transcription and len(transcription.strip()) > 0:
            await websocket.send_json({
                "status": "transcription",
                "text": transcription.strip(),
                "is_final": False,
                "chunk": chunk_num
            })
        
    except Exception as e:
        # Don't send error for individual chunks - just log
        print(f"Error processing chunk {chunk_num}: {str(e)}")
    finally:
        # Cleanup
        for path in [temp_path, wav_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass


async def process_final_audio(websocket: WebSocket, chunks: list, model: LFM2AudioWrapper):
    """Process final complete audio and send final transcription."""
    temp_path = None
    wav_path = None
    
    try:
        # Combine all chunks
        complete_audio = b''.join(chunks)
        
        if len(complete_audio) == 0:
            raise Exception("Empty audio data")
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(complete_audio)
            temp_path = temp_file.name
        
        # Convert to WAV
        await websocket.send_json({
            "status": "processing",
            "message": "Processing final audio..."
        })
        
        wav_path = await convert_audio_to_wav(temp_path, '.webm')
        
        # Transcribe final audio
        loop = asyncio.get_event_loop()
        transcription = await loop.run_in_executor(
            None,
            model.transcribe_audio_file,
            wav_path
        )
        
        # Send final result
        await websocket.send_json({
            "status": "transcription",
            "text": transcription,
            "is_final": True
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing final audio: {error_msg}")
        await websocket.send_json({
            "status": "error",
            "error": f"Audio processing failed: {error_msg}"
        })
    finally:
        # Cleanup
        for path in [temp_path, wav_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription streaming."""
    global model_wrapper
    
    await websocket.accept()
    
    if model_wrapper is None:
        await websocket.send_json({
            "status": "error",
            "error": "Model not initialized"
        })
        await websocket.close()
        return
    
    all_audio_chunks = []
    chunk_count = 0
    processing_tasks = []
    
    try:
        while True:
            data = await websocket.receive()
            
            if "text" in data:
                message = json.loads(data["text"])
                
                if message.get("type") == "audio_chunk":
                    # Store audio chunk
                    try:
                        audio_bytes = base64.b64decode(message["data"])
                        all_audio_chunks.append(audio_bytes)
                        chunk_count += 1
                        
                        # Process chunk immediately for live streaming
                        if len(audio_bytes) > 1000:  # Only process if chunk has enough data
                            # Process in background without blocking
                            task = asyncio.create_task(
                                process_audio_chunk_live(websocket, audio_bytes, chunk_count, model_wrapper)
                            )
                            processing_tasks.append(task)
                        
                        # Send acknowledgment
                        await websocket.send_json({
                            "status": "received",
                            "chunk": chunk_count
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "status": "error",
                            "error": f"Failed to decode audio chunk: {str(e)}"
                        })
                        
                elif message.get("type") == "end":
                    # Wait for any pending processing tasks
                    if processing_tasks:
                        await asyncio.gather(*processing_tasks, return_exceptions=True)
                    
                    # Process final audio for complete transcription
                    if all_audio_chunks:
                        await process_final_audio(websocket, all_audio_chunks, model_wrapper)
                    else:
                        await websocket.send_json({
                            "status": "error",
                            "error": "No audio data received"
                        })
                    break
                    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "error": str(e)
        })
    finally:
        # Cleanup
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
