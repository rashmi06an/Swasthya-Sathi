#!/usr/bin/env bash
# Swasthya Sathi — Startup Script
set -euo pipefail

API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

echo "=============================================="
echo "  Swasthya Sathi — Agentic Health Assistant"
echo "=============================================="
echo "  FastAPI   -> http://localhost:${API_PORT}"
echo "  Streamlit -> http://localhost:${STREAMLIT_PORT}"
echo "=============================================="

uvicorn api.main:app \
    --host "${API_HOST}" \
    --port "${API_PORT}" \
    --workers 1 \
    --log-level info &
API_PID=$!
echo "[start.sh] FastAPI started PID=${API_PID}"

echo "[start.sh] Waiting for FastAPI to be ready..."
for i in $(seq 1 30); do
    if curl -sf "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
        echo "[start.sh] FastAPI is up"
        break
    fi
    sleep 2
done

cleanup() {
    echo "[start.sh] Shutting down..."
    kill "${API_PID}" 2>/dev/null || true
    wait "${API_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

exec streamlit run frontend/app.py \
    --server.port "${STREAMLIT_PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.fileWatcherType none
