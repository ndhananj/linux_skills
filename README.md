# Linux Skills — AI Agent Repository

A complete, self-contained repository that gives any AI agent the knowledge and executable tools to administer a Linux system, backed by a **blazing-fast, CPU-only LLM** that runs on a **Vultr $6/month VPS** (1 vCPU, 1 GB RAM).

---

## Architecture

```
linux_skills/
├── runtime/                  ← LLM server, agent loop, tool registry
│   ├── agent.py              ← Main entry point (tool-calling loop)
│   ├── tool_registry.py      ← Auto-discovers tools, builds OpenAI schemas
│   ├── command_runner.py     ← Robust subprocess wrapper used by all tools
│   ├── config.yaml           ← LLM endpoints, prompts, non-secret defaults
│   ├── config.local.yaml     ← local secret overrides (gitignored)
│   ├── requirements.txt      ← Python dependencies
│   └── scripts/
│       ├── install.sh        ← One-shot VPS setup (builds llama.cpp)
│       ├── download_model.sh ← Downloads GGUF models from HuggingFace
│       └── start_server.sh   ← Starts the llama.cpp OpenAI-compatible server
│
├── file_system/              ┐
├── user_and_group/           │
├── networking/               │
├── process_and_service/      │  18 skill modules, each containing:
├── storage/                  │    SKILL.md  — human/agent reference docs
├── boot_and_kernel/          │    tools.py  — callable Python functions
├── package_management/       │
├── shell_scripting/          │
├── security/                 │
├── containerization/         │
├── iac_and_cicd/             │
├── version_control/          │
├── troubleshooting/          │
├── scheduling/               │
├── ssh/                      │
├── logging/                  │
├── performance/              │
└── text_processing/          ┘
```

### LLM Strategy

| Tier | Model | Size | Speed (1 vCPU) | Cost |
|------|-------|------|----------------|------|
| **Primary** | Qwen2.5-1.5B-Instruct Q4\_K\_M | ~900 MB | ~10–14 t/s | Free |
| **Tiny fallback** | SmolLM2-360M Q4\_K\_M | ~220 MB | ~25–35 t/s | Free |
| **Cloud fallback** | Groq `llama-3.1-8b-instant` | — | ~300 t/s | Free tier |

The agent tries the **local llama.cpp server** first. If it is unreachable (e.g. not yet started, or the VPS is under heavy load), it automatically falls back to the **Groq free-tier API** — no code changes required.

Important for tiny VPS setups: this repository loads a large tool registry. With a **4K context** local server, some prompts can exceed context size before tool execution starts. Keep 4K as the default on small machines, and configure Groq fallback for reliability.

---

## Quick Start

### 1. Clone and install

```bash
git clone <your-repo-url> linux_skills
cd linux_skills/runtime/scripts
bash install.sh
```

`install.sh` will:
- Install `build-essential`, `cmake`, `git`, `python3`, `wget`
- Clone and compile `llama.cpp` (server binary only — fast even on 1 vCPU)
- Install Python dependencies from `requirements.txt`
- Create `runtime/config.local.yaml` from the safe template if missing

### 2. Download a model

```bash
bash download_model.sh
```

Downloads both the primary Qwen2.5-1.5B model and the tiny SmolLM2-360M fallback.

### 3. (Recommended on tiny VPS) Set your Groq API key

Do not store secrets in `runtime/config.yaml` (tracked file). Use one of:
- Environment variable: `export GROQ_API_KEY="your-key"`
- Local override file: copy `runtime/config.local.example.yaml` to `runtime/config.local.yaml` and edit it.

Keep `llm.groq.enabled: true` for tiny 4K local setups so overflowed local requests can fall back to Groq.

### 4. Start the LLM server

Open a **second terminal** and run:

```bash
cd linux_skills/runtime/scripts
bash start_server.sh
```

The server listens on `http://localhost:8080/v1` (OpenAI-compatible).

Defaults are tuned for tiny machines:
- `start_server.sh` defaults to `4096` context tokens.
- This is the safest default for low-RAM hosts.
- You can raise context only on larger hosts:
  `LLAMA_CTX_SIZE=32768 bash start_server.sh`

### 5. Run the agent

```bash
cd linux_skills/runtime
python3 agent.py --prompt "Show me the 10 largest files in /var/log"
```

---

## Skill Modules

Each skill module contains a `SKILL.md` (human-readable reference and agent instructions) and a `tools.py` (callable Python functions). The `tool_registry.py` auto-discovers all tools at startup and generates the OpenAI function-calling schema — no manual registration needed.

| Module | Key Commands Covered |
|--------|---------------------|
| `file_system` | ls, cp, mv, find, grep, sed, awk, ln, fsck |
| `user_and_group` | chown, chgrp, chmod |
| `networking` | ip, ifconfig, dig, traceroute, curl, wget, netstat |
| `process_and_service` | ps, top, kill, systemctl, journalctl |
| `storage` | lsblk, fdisk, mkfs, parted, mdadm, LVM, iSCSI |
| `boot_and_kernel` | grub-install, dracut, sysctl |
| `package_management` | apt, yum, pacman, compile from source |
| `shell_scripting` | bash script execution |
| `security` | iptables, ufw, firewalld, PAM |
| `containerization` | docker |
| `iac_and_cicd` | terraform |
| `version_control` | git |
| `troubleshooting` | lspci, lsusb, dmidecode, systemd-resolve |
| `scheduling` | cron, at |
| `ssh` | scp, ssh-keygen |
| `logging` | tail, logrotate, journalctl |
| `performance` | vmstat, iostat, free |
| `text_processing` | sort, uniq, cut, wc, tr |

---

## Adding a New Skill

1. Create a directory: `linux_skills/<skill_name>/`
2. Add a `SKILL.md` with a description and usage examples.
3. Add a `tools.py` with one function per tool. Use `run_command()` from `runtime/command_runner.py` for all subprocess calls.
4. The tool registry picks it up automatically on the next agent run.

---

## Configuration Reference (`runtime/config.yaml` + `runtime/config.local.yaml`)

| Key | Description |
|-----|-------------|
| `agent.system_prompt` | The system prompt sent to the LLM at the start of every session. |
| `agent.max_tool_output_chars` | Maximum characters of tool output included in the LLM context (default 4000). |
| `agent.max_tools_per_request` | Maximum tool schemas sent per request (default 16, tuned for 4K context). |
| `agent.min_tools_per_request` | Auto-downsize floor for retrying after context overflow (default 4). |
| `llm.local.base_url` | URL of the local llama.cpp server. |
| `llm.local.model` | Model name sent in the request (llama.cpp ignores this). |
| `llm.groq.api_key` | Optional in `config.local.yaml` only (or set `GROQ_API_KEY` env var). |
| `llm.groq.model` | Groq model to use for fallback (default `llama-3.1-8b-instant`). |

---

## Resource Usage on a Vultr $6/mo VPS

| Component | RAM | CPU |
|-----------|-----|-----|
| Qwen2.5-1.5B Q4\_K\_M (loaded) | ~950 MB | ~100% during inference |
| Python agent process | ~50 MB | negligible |
| OS overhead | ~100 MB | negligible |
| **Total** | **~1.1 GB** | — |

> **Tip:** If you hit OOM errors, switch to the SmolLM2-360M model:
> `bash start_server.sh SmolLM2-360M-Q4_K_M.gguf`
> It uses only ~250 MB and is 2–3× faster, at the cost of some reasoning quality.

---

## Troubleshooting: Context Size Errors

If you see an error like:

`request (...) exceeds the available context size (4096 tokens)`

use one of these paths:

1. Tiny VPS path (recommended): keep 4K context and configure Groq fallback via `GROQ_API_KEY` or `runtime/config.local.yaml`.
2. Bigger machine path: restart with larger context, e.g. `LLAMA_CTX_SIZE=32768 bash runtime/scripts/start_server.sh`.

By default, `agent.py` sends a context-safe subset of tools per request, auto-retries with fewer tools if 4K context overflows, and handles skill-list prompts locally.

---

## Tool Call Tracing And Expectation Tests

`agent.py` writes structured JSONL traces by default to:

- `runtime/logs/agent_trace_<timestamp>.jsonl`

Trace events include:

- `llm_request` (backend, model, message/tool counts)
- `llm_response` (tool call names requested by the LLM)
- `tool_call` and `tool_result` (name, args, output preview)

The log directory is gitignored (`runtime/logs/`).

Run the expectation tests (includes the full Entry/Beginner/Intermediate/Advanced matrix in `tests/fixtures/llm_tool_call_expectations.yaml`):

```bash
cd linux_skills
pytest -q tests/test_llm_tool_call_routing.py
```

For live LLM contract checks (natural-language prompts -> expected tool calls, one prompt per skill), start the local server and run:

```bash
cd linux_skills
bash runtime/scripts/run_prompt_contract_tests.sh
```

Contract prompts and expected tool-call targets are in:

- `tests/fixtures/llm_prompt_contracts.yaml`
