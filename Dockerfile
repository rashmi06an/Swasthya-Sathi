# ─────────────────────────────────────────────────────────────────────────────
# Swasthya Sathi — Agentic Rural Health Assistant
# Build:  docker build -t swasthya-sathi .
# Run:    docker run -p 8000:8000 -p 8501:8501 swasthya-sathi
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Build-time metadata ───────────────────────────────────────────────────────
LABEL org.opencontainers.image.title="Swasthya Sathi"
LABEL org.opencontainers.image.description="Agentic Rural Health Assistant"
LABEL org.opencontainers.image.version="1.0.0"

# ── Environment ───────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # HuggingFace model cache inside container (writable)
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers \
    # Streamlit server settings
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    # App defaults (can be overridden at runtime via --env or .env)
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    STREAMLIT_PORT=8501 \
    BACKEND_URL=http://localhost:8000

WORKDIR /app

# ── System dependencies ───────────────────────────────────────────────────────
# ffmpeg: required by Whisper for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies (cached layer) ───────────────────────────────────────
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
COPY . .

# ── Permissions ───────────────────────────────────────────────────────────────
RUN chmod +x /app/start.sh \
    && mkdir -p /app/.cache/huggingface /app/.cache/sentence_transformers

# ── Ports ─────────────────────────────────────────────────────────────────────
# 8000 → FastAPI backend
# 8501 → Streamlit frontend
EXPOSE 8000 8501

# ── Health check ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["/app/start.sh"]
