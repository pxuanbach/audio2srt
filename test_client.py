"""Test script — gửi file audio lên API và nhận về .srt."""
import requests

URL = "http://localhost:8000/transcribe"
AUDIO_PATH = "test_audio.mp3"   # ← đổi thành file thật của bạn

with open(AUDIO_PATH, "rb") as f:
    resp = requests.post(URL, files={"file": f})

if resp.status_code == 200:
    srt_path = AUDIO_PATH.replace(".mp3", ".srt")
    with open(srt_path, "wb") as out:
        out.write(resp.content)
    print(f"✅ SRT saved → {srt_path}")
    print(f"   Content-Disposition: {resp.headers.get('content-disposition')}")
else:
    print(f"❌ Error {resp.status_code}: {resp.text}")
