#!/usr/bin/env bash
# =============================================================================
# install.sh — One-shot setup for the Linux Skills Agent on a fresh VPS
#
# Tested on: Ubuntu 22.04 LTS (Vultr $6/mo: 1 vCPU, 1 GB RAM)
# Run as:    bash install.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$RUNTIME_DIR/.." && pwd)"
VENDOR_DIR="$RUNTIME_DIR/vendor"
MODELS_DIR="$RUNTIME_DIR/models"

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[1;33m%s\033[0m\n' "$*"; }
red()    { printf '\033[0;31m%s\033[0m\n' "$*"; }

green "=== Linux Skills Agent — Installer ==="
echo  "Repo root : $REPO_ROOT"
echo  "Runtime   : $RUNTIME_DIR"
echo

# ---------------------------------------------------------------------------
# 0. Cleanup checks
# ---------------------------------------------------------------------------
yellow "1/6  Running cleanup checks..."

if [ -L "$RUNTIME_DIR/llama-server" ] && [ ! -e "$RUNTIME_DIR/llama-server" ]; then
    yellow "     Removing broken llama-server symlink"
    rm -f "$RUNTIME_DIR/llama-server"
fi

if [ -d "$VENDOR_DIR/llama.cpp/build" ] && [ -f "$VENDOR_DIR/llama.cpp/build/CMakeCache.txt" ]; then
    if ! grep -q "$VENDOR_DIR/llama.cpp" "$VENDOR_DIR/llama.cpp/build/CMakeCache.txt"; then
        yellow "     Removing stale llama.cpp/build (cache points to a different path)"
        rm -rf "$VENDOR_DIR/llama.cpp/build"
    fi
fi

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
yellow "2/6  Installing system packages..."
if ! sudo apt-get update -qq; then
    red "apt-get update failed."
    yellow "This is usually caused by a broken third-party APT repository."
    yellow "Fix or disable the failing repo, then re-run this installer."
    echo
    echo "Quick diagnosis:"
    echo "  grep -R \"^deb .*packagecloud.io/shiftkey\" /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null"
    echo
    echo "If you no longer need that repo, remove it:"
    echo "  sudo rm -f /etc/apt/sources.list.d/*shiftkey*.list"
    echo "  sudo apt-get update"
    exit 1
fi
sudo apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    wget \
    curl \
    locatedb 2>/dev/null || true   # updatedb / mlocate — optional

# ---------------------------------------------------------------------------
# 2. Python dependencies
# ---------------------------------------------------------------------------
yellow "3/6  Installing Python dependencies..."
pip3 install --quiet --upgrade pip
pip3 install --quiet -r "$RUNTIME_DIR/requirements.txt"

# ---------------------------------------------------------------------------
# 3. Build llama.cpp (CPU-only, no GPU flags needed)
# ---------------------------------------------------------------------------
yellow "4/6  Building llama.cpp server..."
mkdir -p "$VENDOR_DIR"
LLAMA_DIR="$VENDOR_DIR/llama.cpp"

if [ ! -d "$LLAMA_DIR" ]; then
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$LLAMA_DIR"
else
    yellow "     llama.cpp already cloned — pulling latest..."
    git -C "$LLAMA_DIR" pull --ff-only
fi

# Build only the server binary to keep compile time short on a 1-vCPU VPS
(
    cd "$LLAMA_DIR"
    # If the repo was moved/copied, CMake cache can point at an old path and fail.
    if [ -f build/CMakeCache.txt ]; then
        if ! grep -q "$LLAMA_DIR" build/CMakeCache.txt; then
            yellow "     Detected stale CMake cache path — cleaning llama.cpp/build"
            rm -rf build
        fi
    fi
    cmake -B build -DLLAMA_NATIVE=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF 2>&1 | tail -5
    cmake --build build --config Release --target llama-server -j"$(nproc)" 2>&1 | tail -10
)

# Symlink the binary to a predictable location
SERVER_BIN="$LLAMA_DIR/build/bin/llama-server"
if [ ! -f "$SERVER_BIN" ]; then
    # Older llama.cpp versions put the binary elsewhere
    SERVER_BIN="$(find "$LLAMA_DIR/build" -name "llama-server" -type f | head -1)"
fi
ln -sf "$SERVER_BIN" "$RUNTIME_DIR/llama-server"
green "     llama-server binary: $SERVER_BIN"

# ---------------------------------------------------------------------------
# 4. Create models directory
# ---------------------------------------------------------------------------
yellow "5/6  Creating models directory..."
mkdir -p "$MODELS_DIR"

# ---------------------------------------------------------------------------
# 5. Remind user about config
# ---------------------------------------------------------------------------
yellow "6/6  Checking configuration..."
LOCAL_CONFIG="$RUNTIME_DIR/config.local.yaml"
LOCAL_CONFIG_EXAMPLE="$RUNTIME_DIR/config.local.example.yaml"

if [ ! -f "$LOCAL_CONFIG" ] && [ -f "$LOCAL_CONFIG_EXAMPLE" ]; then
    cp "$LOCAL_CONFIG_EXAMPLE" "$LOCAL_CONFIG"
    green "     Created $LOCAL_CONFIG from template"
fi

yellow "     Security note: keep secrets out of runtime/config.yaml"
yellow "     Use GROQ_API_KEY env var or runtime/config.local.yaml instead."

echo
green "=== Installation complete! ==="
echo
echo "Next steps:"
echo "  1.  Download a model:  bash $SCRIPT_DIR/download_model.sh"
echo "  2.  Start the server:  bash $SCRIPT_DIR/start_server.sh"
echo "  3.  Run the agent:     python3 $RUNTIME_DIR/agent.py --prompt \"your task\""
