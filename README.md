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
│   ├── config.yaml           ← LLM endpoints, API keys, system prompt
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
- Reproduce `runtime/config.yaml` from the repository defaults on each install run

### 2. Download a model

```bash
bash download_model.sh
```

Downloads both the primary Qwen2.5-1.5B model and the tiny SmolLM2-360M fallback.

### 3. (Optional) Set your Groq API key

Edit `runtime/config.yaml` and replace `YOUR_GROQ_API_KEY` with your key from [console.groq.com/keys](https://console.groq.com/keys). The agent works without it, but Groq provides a powerful cloud fallback at no cost.

### 4. Start the LLM server

Open a **second terminal** and run:

```bash
cd linux_skills/runtime/scripts
bash start_server.sh
```

The server listens on `http://localhost:8080/v1` (OpenAI-compatible).

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

## Configuration Reference (`runtime/config.yaml`)

| Key | Description |
|-----|-------------|
| `agent.system_prompt` | The system prompt sent to the LLM at the start of every session. |
| `agent.max_tool_output_chars` | Maximum characters of tool output included in the LLM context (default 4000). |
| `llm.local.base_url` | URL of the local llama.cpp server. |
| `llm.local.model` | Model name sent in the request (llama.cpp ignores this). |
| `llm.groq.api_key` | Your Groq API key (optional). |
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
