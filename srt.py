"""SRT subtitle generation utilities."""

from datetime import timedelta


def format_time(td) -> str:
    """Format timedelta (or float in seconds) to SRT timestamp: HH:MM:SS,mmm"""
    if isinstance(td, float):
        td = timedelta(seconds=td)
    total_ms = int(td.total_seconds() * 1000)
    hours, remainder = divmod(total_ms, 3600 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    seconds, ms = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


def generate_srt(segments, output_path: str):
    """Write whisper segments to SRT file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = format_time(seg.start)
            end = format_time(seg.end)
            text = seg.text.strip()
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
