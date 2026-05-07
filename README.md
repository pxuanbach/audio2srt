# Audio2SRT API

FastAPI server that transcribes audio files → outputs `.srt` subtitles using Faster-Whisper.

## Quick Start

### Docker (Recommended)

```bash
cd D:\Dev\audio2srt

# Build & run with GPU
docker compose build
docker compose up -d

# First run downloads the model (~3GB) into ./models/ volume
# Subsequent runs reuse the cached model

# Verify it's running
curl http://localhost:8000/health
```

### Local (No Docker)

```bash
cd D:\Dev\audio2srt

uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Requires: NVIDIA GPU + CUDA Toolkit 12.x. Without GPU, set `WHISPER_DEVICE=cpu`.

## API

### `POST /transcribe`

Upload an audio file → receive `.srt` as downloadable file.

```bash
curl -X POST "http://localhost:8000/transcribe" -F "file=@audio.mp3"
```

**Supported formats:** mp3, wav, m4a, flac, ogg, webm, mp4, … (anything ffmpeg can decode)

### `GET /health`

```json
{"status": "ok", "model": "large-v3", "device": "cuda"}
```

## Python Client

```python
import requests

with open("audio.mp3", "rb") as f:
    resp = requests.post("http://localhost:8000/transcribe", files={"file": f})

with open("audio.srt", "wb") as out:
    out.write(resp.content)
```

## Environment Variables

| Variable | Values | Default |
|----------|--------|---------|
| `WHISPER_MODEL` | `tiny` / `base` / `small` / `medium` / `large-v3` | `large-v3` |
| `WHISPER_DEVICE` | `cuda` / `cpu` | `cuda` |
| `WHISPER_COMPUTE` | `float16` / `int8` | `float16` |

## Requirements

- **Docker** + **NVIDIA Container Toolkit** (for GPU support)
  - Install: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
- Or **Python 3.10+** + NVIDIA GPU + CUDA Toolkit 12.x
- **ffmpeg** in PATH
