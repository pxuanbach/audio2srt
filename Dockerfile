FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

WORKDIR /app

# Install Python + system deps in one layer
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for better cache
COPY pyproject.toml ./

# Install uv with Python 3.11 explicitly
RUN /usr/bin/python3.11 -m pip install uv

# Generate lockfile + venv
RUN UV_PYTHON=python3.11 uv lock && UV_PYTHON=python3.11 uv sync

# Copy source
COPY main.py ./

EXPOSE 8000

ENV WHISPER_MODEL=large-v3
ENV WHISPER_DEVICE=cuda
ENV WHISPER_COMPUTE=float16

ENV UV_PYTHON=python3.11

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD /root/.local/bin/uv run python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run
CMD ["/usr/bin/python3.11", "-m", "uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
