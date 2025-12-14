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
    <title>Voice Transcriber</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            padding: 0;
        }
        
        .header {
            background: white;
            border-bottom: 1px solid #e0e0e0;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .header-title {
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .header-stats {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 14px;
        }
        
        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .connect-btn {
            padding: 8px 16px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .connect-btn:hover {
            background: #1d4ed8;
        }
        
        .settings-btn {
            width: 36px;
            height: 36px;
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        
        .settings-btn:hover {
            background: #f5f5f5;
        }
        
        .main-container {
            display: flex;
            height: calc(100vh - 65px);
            gap: 1px;
            background: #e0e0e0;
        }
        
        .left-panel {
            flex: 0 0 400px;
            background: white;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        
        .right-panel {
            flex: 1;
            background: white;
            display: flex;
            flex-direction: column;
        }
        
        .description {
            padding: 16px 24px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .description-text {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .section {
            padding: 24px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .section-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }
        
        .dropdown {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            background: white;
            cursor: pointer;
        }
        
        .audio-visualizer-box {
            background: #1e3a8a;
            border-radius: 8px;
            padding: 20px;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .audio-visualizer-box.active {
            background: #2563eb;
        }
        
        .visualizer-dots {
            display: flex;
            align-items: center;
            gap: 6px;
            height: 100%;
        }
        
        .visualizer-dot {
            width: 8px;
            height: 8px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 50%;
            animation: pulse-dot 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse-dot {
            0%, 100% { 
                opacity: 0.4;
                transform: scale(1);
            }
            50% { 
                opacity: 1;
                transform: scale(1.2);
            }
        }
        
        .device-info {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 0;
            font-size: 14px;
            color: #333;
        }
        
        .device-icon {
            width: 20px;
            height: 20px;
            opacity: 0.6;
        }
        
        .wave-line {
            height: 2px;
            background: #e0e0e0;
            margin: 8px 0;
            border-radius: 1px;
        }
        
        .chat-header {
            padding: 16px 24px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .chat-dropdown {
            padding: 6px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            background: white;
            cursor: pointer;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .message {
            display: flex;
            gap: 12px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .message.transcriber .message-avatar {
            background: #2563eb;
            color: white;
        }
        
        .message.user .message-avatar {
            background: #e5e7eb;
            color: #333;
        }
        
        .message-content {
            flex: 1;
        }
        
        .message-label {
            font-size: 12px;
            font-weight: 600;
            color: #666;
            margin-bottom: 4px;
        }
        
        .message-text {
            font-size: 15px;
            line-height: 1.6;
            color: #1a1a1a;
        }
        
        .empty-state {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 14px;
            text-align: center;
        }
        
        .record-button {
            margin: 24px;
            padding: 12px 24px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            width: calc(100% - 48px);
        }
        
        .record-button:hover:not(:disabled) {
            background: #1d4ed8;
            transform: translateY(-1px);
        }
        
        .record-button.recording {
            background: #dc2626;
        }
        
        .record-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1 class="header-title">Voice Transcriber</h1>
            <div class="header-stats">
                <span>🔍</span>
                <span id="sessionId">transcriber_001</span>
            </div>
        </div>
        <div class="header-actions">
            <button class="connect-btn" id="connectBtn">Connect</button>
            <button class="settings-btn" title="Settings">⚙️</button>
        </div>
    </div>
    
    <div class="main-container">
        <div class="left-panel">
            <div class="description">
                <p class="description-text">Real-Time Voice Transcription System Powered by LFM2 Audio Model</p>
            </div>
            
            <div class="section">
                <div class="section-title">Audio & Voice</div>
                <select class="dropdown" id="voiceSelect">
                    <option>Default</option>
                    <option>High Quality</option>
                    <option>Fast Processing</option>
                </select>
                <div class="audio-visualizer-box" id="audioBox">
                    <div class="visualizer-dots" id="visualizerDots"></div>
                    <div style="position: absolute; color: white; font-size: 14px; font-weight: 500;" id="audioBoxText">Transcriber</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Microphone</div>
                <div class="device-info">
                    <span class="device-icon">🎤</span>
                    <span id="micDevice">Default Microphone</span>
                </div>
                <div class="wave-line"></div>
            </div>
            
            <div class="section">
                <div class="section-title">Audio Input</div>
                <div class="device-info">
                    <span class="device-icon">🔊</span>
                    <span>Live Audio Stream</span>
                </div>
            </div>
            
            <button class="record-button" id="recordBtn" onclick="toggleRecording()">
                🎤 Start Recording
            </button>
        </div>
        
        <div class="right-panel">
            <div class="chat-header">
                <select class="chat-dropdown" id="modelSelect">
                    <option>LFM2 Audio 1.5B</option>
                    <option>High Accuracy Mode</option>
                    <option>Fast Mode</option>
                </select>
                <select class="chat-dropdown" id="languageSelect">
                    <option>English</option>
                    <option>Multi-language</option>
                </select>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="empty-state" id="emptyState">
                    <div>
                        <p style="font-size: 16px; margin-bottom: 8px;">Welcome to Voice Transcriber</p>
                        <p style="font-size: 14px; color: #999;">Click "Start Recording" to begin transcribing your voice</p>
                    </div>
                </div>
            </div>
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
        let transcriptHistory = [];
        let accumulatedText = '';  // Accumulate transcriptions as they come in
        
        // Create visualizer dots
        function createVisualizerDots() {
            const container = document.getElementById('visualizerDots');
            container.innerHTML = '';
            for (let i = 0; i < 18; i++) {
                const dot = document.createElement('div');
                dot.className = 'visualizer-dot';
                dot.style.animationDelay = (i * 0.08) + 's';
                container.appendChild(dot);
            }
        }
        
        createVisualizerDots();
        
        // Get microphone devices
        async function updateMicrophoneDevices() {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                const audioInputs = devices.filter(device => device.kind === 'audioinput');
                const micDeviceEl = document.getElementById('micDevice');
                if (audioInputs.length > 0) {
                    micDeviceEl.textContent = audioInputs[0].label || 'Default Microphone';
                }
            } catch (error) {
                console.error('Error getting devices:', error);
            }
        }
        
        updateMicrophoneDevices();
        
        function toggleRecording() {
            if (!isRecording) {
                startRecording();
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
                
                // Update device name
                const tracks = stream.getAudioTracks();
                if (tracks.length > 0) {
                    document.getElementById('micDevice').textContent = tracks[0].label || 'Microphone';
                }
                
                // Setup audio context
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                source.connect(analyser);
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                // Connect WebSocket
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws/transcribe`);
                
                // Reset accumulated text for new session
                accumulatedText = '';
                
                ws.onopen = () => {
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.status === 'transcription') {
                        if (data.is_final) {
                            // Final transcription - replace accumulated text
                            accumulatedText = data.text;
                            addMessage('transcriber', data.text, true);
                        } else {
                            // Partial transcription - show latest chunk text for live streaming
                            // Each chunk is processed independently and we show the latest
                            const newText = data.text.trim();
                            if (newText) {
                                // For live streaming, show the latest complete chunk
                                // We'll accumulate properly when final transcription comes
                                updateLatestMessage('transcriber', newText);
                                // Also keep accumulating for final version
                                if (!accumulatedText.includes(newText)) {
                                    accumulatedText += (accumulatedText ? ' ' : '') + newText;
                                }
                            }
                        }
                    } else if (data.status === 'processing') {
                        updateStatus('Processing audio...');
                    } else if (data.status === 'error') {
                        addMessage('transcriber', 'Error: ' + data.error, true);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
                
                ws.onclose = () => {
                    console.log('WebSocket closed');
                };
                
                // Setup MediaRecorder
                const options = { mimeType: 'audio/webm;codecs=opus' };
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'audio/webm';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options.mimeType = '';
                    }
                }
                
                mediaRecorder = new MediaRecorder(stream, options);
                audioChunks = [];
                let chunkBuffer = [];
                let chunkSendCounter = 0;
                
                // Buffer chunks before sending to ensure valid WebM files
                mediaRecorder.ondataavailable = async (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                        chunkBuffer.push(event.data);
                        chunkSendCounter++;
                        
                        // Send chunks every 2 intervals (accumulate ~3-4 seconds of audio)
                        // This ensures valid WebM files while still being responsive
                        if (chunkSendCounter >= 2 && ws && ws.readyState === WebSocket.OPEN) {
                            // Combine buffered chunks into a single blob
                            const blob = new Blob(chunkBuffer, { type: 'audio/webm' });
                            
                            // Only send if blob is large enough to be a valid WebM file
                            if (blob.size > 2000) {  // Minimum size for valid WebM
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
                                reader.readAsDataURL(blob);
                                
                                // Reset buffer
                                chunkBuffer = [];
                                chunkSendCounter = 0;
                            }
                        }
                    }
                };
                
                mediaRecorder.onstop = async () => {
                    // Send any remaining buffered chunks
                    if (chunkBuffer.length > 0 && ws && ws.readyState === WebSocket.OPEN) {
                        const blob = new Blob(chunkBuffer, { type: 'audio/webm' });
                        if (blob.size > 500) {
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const base64Audio = reader.result.split(',')[1];
                                if (ws && ws.readyState === WebSocket.OPEN) {
                                    try {
                                        ws.send(JSON.stringify({
                                            type: 'audio_chunk',
                                            data: base64Audio,
                                            format: 'webm',
                                            sample_rate: 48000
                                        }));
                                        // Send end signal after a short delay
                                        setTimeout(() => {
                                            if (ws && ws.readyState === WebSocket.OPEN) {
                                                try {
                                                    ws.send(JSON.stringify({ type: 'end' }));
                                                } catch (e) {
                                                    console.error('Error sending end signal:', e);
                                                }
                                            }
                                        }, 200);
                                    } catch (e) {
                                        console.error('Error sending final chunk:', e);
                                        // Try to send end signal anyway
                                        if (ws && ws.readyState === WebSocket.OPEN) {
                                            try {
                                                ws.send(JSON.stringify({ type: 'end' }));
                                            } catch (e2) {
                                                console.error('Error sending end signal:', e2);
                                            }
                                        }
                                    }
                                }
                            };
                            reader.readAsDataURL(blob);
                        } else {
                            // No remaining chunks, just send end signal
                            if (ws && ws.readyState === WebSocket.OPEN) {
                                try {
                                    ws.send(JSON.stringify({ type: 'end' }));
                                } catch (e) {
                                    console.error('Error sending end signal:', e);
                                }
                            }
                        }
                    } else {
                        // Send end signal
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            try {
                                ws.send(JSON.stringify({ type: 'end' }));
                            } catch (e) {
                                console.error('Error sending end signal:', e);
                            }
                        }
                    }
                };
                
                // Record in 2-second chunks for better WebM validity
                // We buffer 2 chunks before sending (so ~4 seconds per transmission)
                mediaRecorder.start(2000);
                isRecording = true;
                
                // Update UI
                document.getElementById('recordBtn').classList.add('recording');
                document.getElementById('recordBtn').textContent = '⏹ Stop Recording';
                document.getElementById('audioBox').classList.add('active');
                document.getElementById('audioBoxText').textContent = 'Listening...';
                document.getElementById('connectBtn').textContent = 'Connected';
                document.getElementById('connectBtn').style.background = '#16a34a';
                
                visualize();
                updateMicrophoneDevices();
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                addMessage('transcriber', 'Microphone access denied. Please allow microphone access.', true);
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                
                if (audioContext) {
                    audioContext.close();
                }
                
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                
                document.getElementById('recordBtn').classList.remove('recording');
                document.getElementById('recordBtn').textContent = '🎤 Start Recording';
                document.getElementById('audioBox').classList.remove('active');
                document.getElementById('audioBoxText').textContent = 'Transcriber';
                document.getElementById('connectBtn').textContent = 'Connect';
                document.getElementById('connectBtn').style.background = '#2563eb';
            }
        }
        
        function visualize() {
            if (!isRecording || !analyser) return;
            
            analyser.getByteFrequencyData(dataArray);
            requestAnimationFrame(visualize);
        }
        
        function addMessage(sender, text, isFinal) {
            const container = document.getElementById('chatContainer');
            const emptyState = document.getElementById('emptyState');
            
            if (emptyState) {
                emptyState.remove();
            }
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.id = sender === 'transcriber' && !isFinal ? 'latest-transcriber' : null;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'transcriber' ? '🤖' : '👤';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            
            const label = document.createElement('div');
            label.className = 'message-label';
            label.textContent = sender === 'transcriber' ? 'Transcriber' : 'You';
            
            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.textContent = text;
            
            content.appendChild(label);
            content.appendChild(messageText);
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            container.appendChild(messageDiv);
            
            container.scrollTop = container.scrollHeight;
            
            if (isFinal) {
                transcriptHistory.push({ sender, text, timestamp: Date.now() });
            }
        }
        
        function updateLatestMessage(sender, text) {
            let latestMsg = document.getElementById('latest-transcriber');
            if (!latestMsg) {
                addMessage(sender, text, false);
            } else {
                const textEl = latestMsg.querySelector('.message-text');
                if (textEl) {
                    textEl.textContent = text;
                    const container = document.getElementById('chatContainer');
                    container.scrollTop = container.scrollHeight;
                }
            }
        }
        
        function updateStatus(message) {
            console.log('Status:', message);
        }
        
        // Connect button functionality
        document.getElementById('connectBtn').addEventListener('click', function() {
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        });
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
    if file_size < 1000:  # Very small file, likely corrupted/incomplete WebM
        raise Exception(f"Audio file too small ({file_size} bytes), likely corrupted or incomplete")
    
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
        
        # Transcribe chunk (fast method - non-blocking)
        loop = asyncio.get_event_loop()
        transcription = await loop.run_in_executor(
            None,
            model.transcribe_audio_file,
            wav_path
        )
        
        # Send partial result immediately for live streaming
        if transcription and len(transcription.strip()) > 0:
            await websocket.send_json({
                "status": "transcription",
                "text": transcription.strip(),
                "is_final": False,
                "chunk": chunk_num
            })
        
    except Exception as e:
        # Don't send error for individual chunks - just log (silent failure for live streaming)
        # Filter out expected errors (small/invalid chunks)
        error_msg = str(e)
        if "small" not in error_msg.lower() and "invalid" not in error_msg.lower() and "corrupted" not in error_msg.lower():
            print(f"Warning processing chunk {chunk_num}: {error_msg[:100]}")
    finally:
        # Cleanup temp files
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
                        # Only process if chunk is large enough to be a valid WebM file
                        if len(audio_bytes) > 2000:  # Minimum size for valid WebM file
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
