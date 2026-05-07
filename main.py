"""
Audio2SRT API Server — Faster-Whisper + FastAPI
POST /transcribe → receives audio file, returns .srt
"""

import os
import tempfile
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import faster_whisper

app = FastAPI(title="Audio2SRT API", version="1.0.0")

# ── config ────────────────────────────────────────────────────────────────────
MODEL_SIZE = os.getenv("WHISPER_MODEL", "large-v3")   # tiny/base/small/medium/large-v3
DEVICE     = os.getenv("WHISPER_DEVICE", "cuda")        # cuda / cpu
COMPUTE    = os.getenv("WHISPER_COMPUTE", "float16")    # float16 / int8

# Cache the model at startup
print(f"Loading Faster-Whisper model: {MODEL_SIZE} on {DEVICE}…")
model = faster_whisper.WhisperModel(
    MODEL_SIZE,
    device=DEVICE,
    compute_type=COMPUTE,
)
print("Model loaded.")


# ── helpers ───────────────────────────────────────────────────────────────────
def format_srt_time(td) -> str:
    """Convert timedelta (or float in seconds) to SRT timestamp: HH:MM:SS,mmm"""
    if isinstance(td, float):
        td = timedelta(seconds=td)
    total_ms = int(td.total_seconds() * 1000)
    h, rem = divmod(total_ms, 3600 * 1000)
    m, rem = divmod(rem, 60 * 1000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments) -> str:
    """Build SRT string from whisper segments."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_srt_time(seg.start)
        end   = format_srt_time(seg.end)
        text  = seg.text.strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


# ── routes ────────────────────────────────────────────────────────────────────
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Upload an audio file → returns SRT as downloadable .srt file.

    Supported formats: mp3, wav, m4a, flac, ogg, webm, mp4 …
    (anything ffmpeg can decode, via faster-whisper)
    """
    suffix = Path(file.filename).suffix or ".mp3"

    # Save uploaded file to a temp location (auto-cleaned on process exit)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    try:
        # ── transcription ──────────────────────────────────────────────────────
        segments, info = model.transcribe(
            tmp_path,
            language=None,          # auto-detect; set e.g. "vi" for Vietnamese
            beam_size=5,
            vad_filter=True,       # voice activity detection
        )

        # Materialize generator so we can check timing info
        seg_list = list(segments)
        print(f"Transcribed: {info.language}, {len(seg_list)} segments")

        # ── build SRT ──────────────────────────────────────────────────────────
        srt_content = segments_to_srt(seg_list)

        # Return as downloadable file
        srt_name = Path(file.filename).stem + ".srt"
        return FileResponse(
            content=srt_content.encode("utf-8"),
            media_type="application/x-subrip",
            filename=srt_name,
        )
    finally:
        os.unlink(tmp_path)


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_SIZE, "device": DEVICE}


# ── entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
