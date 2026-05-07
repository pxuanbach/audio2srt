# Audio2SRT API

FastAPI server dùng **Faster-Whisper** để transcribe audio → xuất file `.srt`.

## Cách 1: Docker (Khuyến nghị)

### Build & Run

```bash
cd D:\Dev\audio2srt

# Build image
docker compose build

# Chạy container (GPU sẽ được expose tự động)
docker compose up -d
```

### Hoặc chạy thủ công

```bash
# Build
docker build -t audio2srt .

# Run (cần --gpus all để dùng GPU)
docker run --gpus all -p 8000:8000 \
  -e WHISPER_MODEL=large-v3 \
  -e WHISPER_DEVICE=cuda \
  audio2srt
```

## Cách 2: Local (Python)

```bash
cd D:\Dev\audio2srt

uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

> **Yêu cầu local:** NVIDIA GPU + CUDA Toolkit 12.x + cuBLAS. Nếu không có GPU, dùng `WHISPER_DEVICE=cpu`.

## Biến môi trường

| Biến | Giá trị | Mặc định |
|------|---------|-----------|
| `WHISPER_MODEL` | `tiny` / `base` / `small` / `medium` / `large-v3` | `large-v3` |
| `WHISPER_DEVICE` | `cuda` / `cpu` | `cuda` |
| `WHISPER_COMPUTE` | `float16` / `int8` | `float16` |

## API

### `POST /transcribe`

Upload file audio → trả về file `.srt`.

```bash
curl -X POST "http://localhost:8000/transcribe" -F "file=@audio.mp3"
```

### `GET /health`

```json
{"status": "ok", "model": "large-v3", "device": "cuda"}
```

## Python client

```python
import requests

with open("audio.mp3", "rb") as f:
    resp = requests.post("http://localhost:8000/transcribe", files={"file": f})

with open("audio.srt", "wb") as out:
    out.write(resp.content)
```

## Yêu cầu

- **Docker** + **NVIDIA Container Toolkit** (cho GPU support)
  - Hướng dẫn cài: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
- Hoặc **Python 3.10+** + NVIDIA GPU + CUDA Toolkit 12.x
