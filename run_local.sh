#!/usr/bin/env bash
# ==============================================================================
# LexiLegal AI — One-Command Local Startup Script
# Starts: AI Engine (FastAPI :8000) -> Spring Boot (:8080) -> Frontend (:5173)
# ==============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=========================================================="
echo " Starting LexiLegal AI Platform Services..."
echo " Root directory: $ROOT_DIR"
echo "=========================================================="

# 1. Load environment variables
if [ -f "$ROOT_DIR/.env" ]; then
    echo "[+] Loading environment configuration from .env..."
    set -a
    source "$ROOT_DIR/.env"
    set +a
else
    echo "[!] Warning: No .env file found. Using default development values."
fi

# Track child PIDs for clean teardown
AI_PID=""
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "=========================================================="
    echo " Shutting down LexiLegal AI services..."
    echo "=========================================================="
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "[*] Stopping Frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "[*] Stopping Backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$AI_PID" ] && kill -0 "$AI_PID" 2>/dev/null; then
        echo "[*] Stopping AI Engine (PID: $AI_PID)..."
        kill "$AI_PID" 2>/dev/null || true
    fi
    echo "[+] All services stopped gracefully."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 2. Start AI Engine (FastAPI on port 8000)
echo "[1/3] Starting AI Engine (FastAPI on http://127.0.0.1:8000)..."
if [ ! -d "$ROOT_DIR/ai-engine/.venv" ]; then
    echo "[-] Error: ai-engine/.venv directory not found. Please run setup first."
    exit 1
fi

(
    cd "$ROOT_DIR/ai-engine"
    PATH="/home/rishichowdary/.local/bin:$PATH" .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
) &
AI_PID=$!
echo "      AI Engine launched with PID: $AI_PID"

# Wait for AI Engine health check
echo "      Waiting for AI Engine readiness..."
for i in {1..20}; do
    if curl -s "http://127.0.0.1:8000/internal/health" -H "X-Internal-Api-Key: ${INTERNAL_API_KEY:-lexilegal_internal_service_key_secret_2026}" > /dev/null 2>&1; then
        echo "      AI Engine is UP and ready."
        break
    fi
    sleep 1
done

# 3. Start Spring Boot Backend (Port 8080)
echo "[2/3] Starting Spring Boot Backend (http://localhost:8080)..."
(
    cd "$ROOT_DIR/backend"
    mvn spring-boot:run
) &
BACKEND_PID=$!
echo "      Backend launched with PID: $BACKEND_PID"

# Wait for Backend health check
echo "      Waiting for Spring Boot readiness..."
for i in {1..30}; do
    if curl -s "http://127.0.0.1:8080/api/health" > /dev/null 2>&1; then
        echo "      Backend is UP and ready."
        break
    fi
    sleep 1
done

# 4. Start Frontend Development Server (Port 5173)
echo "[3/3] Starting Frontend (http://localhost:5173)..."
(
    cd "$ROOT_DIR/frontend"
    npm run dev -- --host 127.0.0.1 --port 5173
) &
FRONTEND_PID=$!
echo "      Frontend launched with PID: $FRONTEND_PID"

echo "=========================================================="
echo " All LexiLegal AI services are now running!"
echo "   - Web App UI:    http://localhost:5173"
echo "   - REST API:      http://localhost:8080/api"
echo "   - Swagger UI:    http://localhost:8080/swagger-ui.html"
echo "   - AI Engine:     http://localhost:8000"
echo " Press Ctrl+C at any time to shut down all services."
echo "=========================================================="

wait
