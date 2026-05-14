#!/usr/bin/env bash
# Swasthya Sathi — Startup Script
set -euo pipefail

API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-7860}"

if [ -x "./venv/bin/python" ]; then
    PYTHON_BIN="./venv/bin/python"
elif [ -x "./.venv/bin/python" ]; then
    PYTHON_BIN="./.venv/bin/python"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo "[start.sh] ❌ No Python executable found (expected 'python' or 'python3')."
    exit 1
fi

echo "=============================================="
echo "  Swasthya Sathi — Agentic Health Assistant"
echo "=============================================="
echo "  FastAPI   -> http://localhost:${API_PORT}"
echo "  Streamlit -> http://localhost:${STREAMLIT_PORT}"
echo "=============================================="


# ─── Start FastAPI ────────────────────────────────────────────────────────────
echo "[start.sh] Starting FastAPI..."
"${PYTHON_BIN}" -m uvicorn api.main:app \
    --host "${API_HOST}" \
    --port "${API_PORT}" \
    --workers 1 \
    --log-level debug > backend.log 2>&1 &
API_PID=$!
echo "[start.sh] FastAPI started with PID=${API_PID}"

# ─── Wait for FastAPI ─────────────────────────────────────────────────────────
echo "[start.sh] Waiting for FastAPI to be ready at http://localhost:${API_PORT}/health ..."
READY=false
for i in $(seq 1 20); do
    if curl -sf "http://127.0.0.1:${API_PORT}/health" > /dev/null 2>&1 || \
       curl -sf "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
        echo "[start.sh] ✅ FastAPI is up and running!"
        READY=true
        break
    fi
    echo "[start.sh] ... still waiting ($i/20)"
    sleep 3
done

if [ "$READY" = false ]; then
    echo "[start.sh] ❌ FastAPI failed to start in time. Printing backend.log:"
    cat backend.log
    # We don't exit so the container stays up for debugging, 
    # but the logs will show the error.
fi

cleanup() {
    echo "[start.sh] Shutting down..."
    kill "${API_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ─── Start Streamlit ──────────────────────────────────────────────────────────
echo "[start.sh] Starting Streamlit..."
exec "${PYTHON_BIN}" -m streamlit run frontend/app.py \
    --server.port "${STREAMLIT_PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.fileWatcherType none
