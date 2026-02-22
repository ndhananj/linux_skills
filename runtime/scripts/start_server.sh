#!/usr/bin/env bash
# =============================================================================
# start_server.sh — Starts the llama.cpp OpenAI-compatible server
#
# Usage:
#   bash start_server.sh                          # uses default model
#   bash start_server.sh SmolLM2-360M-Q4_K_M.gguf  # use a specific model
#
# The server exposes an OpenAI-compatible API at http://localhost:8080/v1
# which the agent.py connects to automatically.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MODELS_DIR="$RUNTIME_DIR/models"
SERVER_BIN="$RUNTIME_DIR/llama-server"

green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[1;33m%s\033[0m\n' "$*"; }
red()    { printf '\033[0;31m%s\033[0m\n' "$*"; }

# ---------------------------------------------------------------------------
# Resolve model
# ---------------------------------------------------------------------------
DEFAULT_MODEL="qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_FILE="${1:-$DEFAULT_MODEL}"
MODEL_PATH="$MODELS_DIR/$MODEL_FILE"

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
if [ ! -f "$SERVER_BIN" ]; then
    red "ERROR: llama-server binary not found at $SERVER_BIN"
    red "       Run install.sh first."
    exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
    red "ERROR: Model not found: $MODEL_PATH"
    red "       Run download_model.sh first, or pass a different filename."
    echo
    echo "Available models in $MODELS_DIR:"
    ls -lh "$MODELS_DIR" 2>/dev/null || echo "  (none)"
    exit 1
fi

# ---------------------------------------------------------------------------
# Server parameters tuned for 1 vCPU / 1 GB RAM
# ---------------------------------------------------------------------------
HOST="0.0.0.0"
PORT="8080"
CTX_SIZE=4096          # context window in tokens
N_THREADS="$(nproc)"   # use all available CPU threads
N_PARALLEL=1           # only one concurrent request on a $6 VPS
BATCH_SIZE=512         # prompt-processing batch size

green "=== Starting llama.cpp server ==="
echo  "  Model   : $MODEL_FILE"
echo  "  Address : http://$HOST:$PORT/v1"
echo  "  Context : $CTX_SIZE tokens"
echo  "  Threads : $N_THREADS"
echo

"$SERVER_BIN" \
    --model        "$MODEL_PATH" \
    --ctx-size     "$CTX_SIZE" \
    --host         "$HOST" \
    --port         "$PORT" \
    --threads      "$N_THREADS" \
    --parallel     "$N_PARALLEL" \
    --batch-size   "$BATCH_SIZE" \
    --log-disable
