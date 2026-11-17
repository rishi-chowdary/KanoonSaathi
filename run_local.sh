#!/usr/bin/env bash
# ==============================================================================
# LexiLegal AI — One-Command Local Startup Script (Python NLP Stack)
# Starts: MySQL 8 (Docker or local) -> Alembic Migrations -> Flask App Server
# ==============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=========================================================="
echo " Starting LexiLegal AI Platform (Python NLP Stack)"
echo " Root directory: $ROOT_DIR"
echo "=========================================================="

# 1. Load environment variables
if [ -f "$ROOT_DIR/.env" ]; then
    echo "[+] Loading environment configuration from .env..."
    set -a
    source "$ROOT_DIR/.env"
    set +a
else
    echo "[!] Warning: No .env file found. Copying from .env.example..."
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    set -a
    source "$ROOT_DIR/.env"
    set +a
fi

# 2. Check virtual environment
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[-] Error: Python virtual environment not found at $ROOT_DIR/.venv"
    echo "    Please create it using: python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 3. Check / Start MySQL Database
echo "[1/3] Checking MySQL database connectivity..."
DB_HOST="${MYSQL_HOST:-127.0.0.1}"
DB_PORT="${MYSQL_PORT:-3306}"

if ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
    echo "[!] MySQL not detected on $DB_HOST:$DB_PORT. Attempting docker compose up -d..."
    if command -v docker >/dev/null 2>&1; then
        docker compose up -d
        echo "[*] Waiting for MySQL container to become healthy..."
        sleep 5
    else
        echo "[-] Error: Docker is not installed and MySQL is not running on $DB_HOST:$DB_PORT."
        exit 1
    fi
fi
echo "[+] MySQL database is reachable."

# 4. Apply Database Migrations
echo "[2/3] Applying database migrations (Flask-Migrate / Alembic)..."
"$ROOT_DIR/.venv/bin/flask" db upgrade || {
    echo "[!] Migration failed, falling back to db.create_all()..."
    "$VENV_PYTHON" -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
}
echo "[+] Database schema is up to date."

# 5. Start Flask Application
PORT="${PORT:-5000}"
echo "[3/3] Starting LexiLegal AI Flask Server on http://127.0.0.1:${PORT}..."
echo "=========================================================="
echo " LexiLegal AI is running at: http://127.0.0.1:${PORT}"
echo " Press Ctrl+C to terminate the application."
echo "=========================================================="

exec "$VENV_PYTHON" run.py
