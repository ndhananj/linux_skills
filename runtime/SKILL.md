# Runtime — Agent Infrastructure

This directory contains the core infrastructure that powers the Linux Skills Agent. It is not a skill module in the traditional sense — it does not expose tools to the LLM. Instead, it provides the scaffolding that loads all skill modules, manages the LLM connection, and orchestrates the tool-calling loop.

## Components

**`agent.py`** is the main entry point. It initialises the tool registry, connects to the local llama.cpp server (with automatic Groq fallback), and runs the multi-turn tool-calling loop until the LLM produces a final text answer.

**`tool_registry.py`** walks the repository tree, imports every `tools.py` it finds, and generates an OpenAI-compatible function-calling schema for each callable. New skill modules are picked up automatically — no manual registration is needed.

**`command_runner.py`** is a thin wrapper around Python's `subprocess.run`. Every tool function in the repository calls `run_command()` rather than `subprocess` directly, ensuring consistent error handling, timeout enforcement, and output normalisation across all 18 skill modules.

**`config.yaml`** holds all runtime configuration: LLM endpoints, API keys, the system prompt, and agent behaviour parameters. Copy it to `config.local.yaml` for local overrides that will not be committed to version control.

## Setup Scripts

The `scripts/` subdirectory contains three Bash scripts that set up the runtime on a fresh VPS:

| Script | Purpose |
|--------|---------|
| `install.sh` | Installs system packages, builds llama.cpp, and installs Python dependencies. |
| `download_model.sh` | Downloads the primary (Qwen2.5-1.5B) and fallback (SmolLM2-360M) GGUF models. |
| `start_server.sh` | Starts the llama.cpp OpenAI-compatible server on port 8080. |

Run them in order on a fresh Vultr $6/mo VPS (Ubuntu 22.04):

```bash
bash install.sh
bash download_model.sh
bash start_server.sh   # run in a separate terminal
```

## LLM Fallback Logic

The agent uses a two-tier LLM strategy to maximise uptime and minimise cost. On every completion request, `agent.py` first attempts to reach the local llama.cpp server. If the connection fails (e.g. the server has not been started yet, or the VPS is under heavy load), the agent transparently retries the same request against the Groq free-tier API. This means the agent remains fully functional even before the local server is running, as long as a Groq API key is configured.
