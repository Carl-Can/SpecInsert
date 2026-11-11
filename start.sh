#!/usr/bin/env bash
# Bio-House one-shot local start.
# Creates the backend venv, installs dependencies, copies env templates,
# and refuses to boot while the LLM API key is still a placeholder.
# Never prints the key. Does not write secrets into git.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
BACKEND_ENV="$BACKEND_DIR/.env"
FRONTEND_ENV="$FRONTEND_DIR/.env"

echo "Bio-House — educational sandbox"
echo "========================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required but was not found on PATH."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is required for the frontend but was not found on PATH."
  echo "Install Node.js 20+ and run ./start.sh again."
  exit 1
fi

copy_if_missing() {
  local source_file="$1"
  local dest_file="$2"
  if [ ! -f "$dest_file" ]; then
    if [ ! -f "$source_file" ]; then
      echo "ERROR: missing template $source_file"
      exit 1
    fi
    cp "$source_file" "$dest_file"
    echo "Created $dest_file from $(basename "$source_file")."
  fi
}

read_env_value() {
  local file="$1"
  local key="$2"
  local line=""
  line="$(grep -E "^${key}=" "$file" | head -n 1 || true)"
  line="${line#*=}"
  line="${line%\"}"
  line="${line#\"}"
  line="${line%\'}"
  line="${line#\'}"
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  printf '%s' "$line"
}

copy_if_missing "$BACKEND_DIR/.env.example" "$BACKEND_ENV"
copy_if_missing "$FRONTEND_DIR/.env.example" "$FRONTEND_ENV"

API_KEY="$(read_env_value "$BACKEND_ENV" "LLM_API_KEY")"
case "$API_KEY" in
  ""|demo-key|your_api_key_here|sk-xxxxxxxxxxxxxxxx)
    echo ""
    echo "ERROR: LLM_API_KEY is missing or still a placeholder in backend/.env."
    echo "Edit backend/.env and set a real key for an OpenAI-compatible API"
    echo "(DeepSeek, OpenAI, Qwen, or a local server)."
    echo "This educational sandbox will not start until that key is set."
    echo "The key stays in backend/.env, which is gitignored. Do not commit it."
    exit 1
    ;;
esac

echo "LLM_API_KEY is set (value not printed)."

if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "ERROR: python3 cannot create a virtualenv (ensurepip is missing)."
  echo "On Debian/Ubuntu install the venv package, then run ./start.sh again:"
  echo "  sudo apt install python3-venv"
  exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Creating Python virtualenv at backend/venv ..."
  rm -rf "$VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo "Installing backend dependencies ..."
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r "$BACKEND_DIR/requirements.txt"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies ..."
  (cd "$FRONTEND_DIR" && npm install)
fi

echo ""
echo "Starting backend (FastAPI @ :8000) ..."
cd "$BACKEND_DIR"
"$VENV_DIR/bin/uvicorn" main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "   backend PID: $BACKEND_PID"

echo ""
echo "Starting frontend (Vite @ :5173) ..."
cd "$FRONTEND_DIR"
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!
echo "   frontend PID: $FRONTEND_PID"

echo ""
echo "========================================"
echo "Bio-House is starting."
echo "   UI:       http://localhost:5173"
echo "   API:      http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "Educational sandbox only. Not a medical device."
echo "Press Ctrl+C to stop both processes."
echo "========================================"

trap 'echo ""; echo "Stopping..."; kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true; exit 0' INT TERM

wait
