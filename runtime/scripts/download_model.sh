#!/usr/bin/env bash
# =============================================================================
# download_model.sh — Downloads GGUF models for the Linux Skills Agent
#
# Models are chosen to fit inside 1 GB RAM (Vultr $6/mo VPS):
#
#   PRIMARY   Qwen2.5-1.5B-Instruct Q4_K_M  ~900 MB  ~10-14 t/s on 1 vCPU
#             Best-in-class tool-calling at this size.
#
#   FALLBACK  SmolLM2-360M Q4_K_M           ~220 MB  ~25-35 t/s on 1 vCPU
#             Ultra-fast; use when RAM is critically low.
#
# If you have more RAM (e.g. Vultr $12/mo with 2 GB), you can also try:
#   Qwen2.5-3B-Instruct Q4_K_M  ~1.9 GB  — better reasoning, still fast
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$(cd "$SCRIPT_DIR/../models" && pwd)"

green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[1;33m%s\033[0m\n' "$*"; }

mkdir -p "$MODELS_DIR"

# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------
declare -A MODELS
MODELS["qwen2.5-1.5b-instruct-q4_k_m.gguf"]="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODELS["SmolLM2-360M-Q4_K_M.gguf"]="https://huggingface.co/QuantFactory/SmolLM2-360M-GGUF/resolve/main/SmolLM2-360M-Q4_K_M.gguf"

# ---------------------------------------------------------------------------
# Download loop
# ---------------------------------------------------------------------------
for filename in "${!MODELS[@]}"; do
    url="${MODELS[$filename]}"
    dest="$MODELS_DIR/$filename"

    if [ -f "$dest" ]; then
        yellow "Already exists: $filename — skipping."
        continue
    fi

    yellow "Downloading $filename ..."
    wget --quiet --show-progress -O "${dest}.tmp" "$url"
    mv "${dest}.tmp" "$dest"
    green "Saved: $dest"
done

echo
green "All models are ready in $MODELS_DIR"
ls -lh "$MODELS_DIR"
