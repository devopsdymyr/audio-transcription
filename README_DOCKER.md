# Running API Server in Docker

## Quick Start

The API server **must** run in Docker due to GLIBC version requirements.

### Start Server

```bash
./run_api_docker.sh
```

This will:
1. Use existing Docker image (or build if needed)
2. Start the API server on port 8001
3. Mount your project directory for live updates

### Access

Open your browser: **http://localhost:8001**

### View Logs

```bash
docker logs -f audio-transcription-api
```

### Stop Server

```bash
docker stop audio-transcription-api
```

### Restart Server

```bash
docker restart audio-transcription-api
```

## Why Docker?

The pre-compiled binaries require GLIBC 2.38, but Ubuntu 22.04 only has GLIBC 2.35. Docker with Ubuntu 24.04 provides the correct GLIBC version.

## Troubleshooting

### Port Already in Use
```bash
docker stop audio-transcription-api
```

### Check Status
```bash
docker ps | grep audio-transcription-api
```

### View Full Logs
```bash
docker logs audio-transcription-api
```

### Rebuild Image (if needed)
```bash
docker build -t audio-transcription-cli .
```

