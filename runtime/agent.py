#!/usr/bin/env python3
"""
agent.py — Linux Skills Agent

A tool-calling agent that:
  1. Tries the local llama.cpp server first (CPU-only, zero API cost).
  2. Falls back to the Groq free-tier API if the local server is unreachable
     or returns a rate-limit error.
  3. Executes the tools requested by the LLM and feeds results back in a
     multi-turn loop until the model produces a final text answer.

Quick start
-----------
    # Start the llama.cpp server in another terminal first:
    #   cd runtime/scripts && bash start_server.sh
    #
    # Then run the agent:
    python3 agent.py --prompt "Show me the 10 largest files in /var/log"

Configuration
-------------
Edit runtime/config.yaml to change non-secret settings (models, prompts, etc).
Put secrets in runtime/config.local.yaml (untracked) or environment variables
such as GROQ_API_KEY.
"""

import json
import os
import re
import sys
import textwrap
from typing import Any, Dict, List, Optional

import openai
import yaml

# The tool registry lives in the same directory as this file
sys.path.insert(0, os.path.dirname(__file__))
from tool_registry import discover_skills
from tracing import JsonlTracer, default_log_dir, make_default_run_id

# ---------------------------------------------------------------------------
# Colour helpers (degrade gracefully on non-ANSI terminals)
# ---------------------------------------------------------------------------
_RESET = "\033[0m"
_GREEN = "\033[0;32m"
_YELLOW = "\033[1;33m"
_RED = "\033[0;31m"
_CYAN = "\033[0;36m"


def _c(colour: str, text: str) -> str:
    return f"{colour}{text}{_RESET}" if sys.stdout.isatty() else text


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class LinuxSkillsAgent:
    """Orchestrates the LLM ↔ tool-calling loop."""

    # Maximum number of LLM turns per prompt before giving up
    MAX_TURNS = 8

    def __init__(self, config_path: str = "config.yaml"):
        self.cfg = self._load_config(config_path)
        self._local_client = self._make_local_client()
        self._groq_client = self._make_groq_client()
        self._tool_configs, self._tool_functions = self._load_tools()
        self._tool_config_by_name = {
            tc["function"]["name"]: tc for tc in self._tool_configs if tc.get("function", {}).get("name")
        }
        self._skills = sorted({name.split("__", 1)[0] for name in self._tool_functions.keys()})
        self._runtime_dir = os.path.dirname(__file__)
        self._tracer = self._make_tracer()
        print(_c(_GREEN, f"[agent] Ready — {len(self._tool_configs)} tools loaded."))

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _load_config(self, path: str) -> Dict[str, Any]:
        abs_path = os.path.join(os.path.dirname(__file__), path)
        with open(abs_path) as fh:
            cfg = yaml.safe_load(fh)

        # Optional local override file for secrets and machine-specific tuning.
        local_path = os.path.join(os.path.dirname(abs_path), "config.local.yaml")
        if os.path.exists(local_path):
            with open(local_path) as fh:
                local_cfg = yaml.safe_load(fh) or {}
            cfg = self._deep_merge_dicts(cfg, local_cfg)

        # Environment variables override files (best for secret injection).
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if groq_api_key:
            cfg.setdefault("llm", {}).setdefault("groq", {})["api_key"] = groq_api_key
        return cfg

    def _deep_merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._deep_merge_dicts(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _make_local_client(self) -> openai.OpenAI:
        lc = self.cfg["llm"]["local"]
        return openai.OpenAI(base_url=lc["base_url"], api_key=lc.get("api_key", "local-key"))

    def _make_tracer(self) -> Optional[JsonlTracer]:
        tracing_cfg = self.cfg.get("agent", {}).get("tracing", {})
        if not tracing_cfg.get("enabled", True):
            return None
        run_id = make_default_run_id()
        log_dir = tracing_cfg.get("log_dir") or default_log_dir(self._runtime_dir)
        tracer = JsonlTracer(log_dir=log_dir, run_id=run_id)
        tracer.log(
            "agent_start",
            {
                "tools_loaded": len(self._tool_configs),
                "skills_loaded": len(self._skills),
            },
        )
        return tracer

    def _make_groq_client(self) -> Optional[openai.OpenAI]:
        gc = self.cfg["llm"].get("groq", {})
        if not gc.get("enabled", True):
            print(_c(_YELLOW, "[agent] Groq fallback disabled in config (llm.groq.enabled=false)."))
            return None
        key = gc.get("api_key", "")
        if not key or key == "YOUR_GROQ_API_KEY":
            print(_c(_YELLOW, "[agent] Groq API key not set — fallback disabled."))
            return None
        return openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=key,
        )

    def _load_tools(self):
        skills_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return discover_skills(skills_dir)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, prompt: str) -> str:
        """Run the agent loop for *prompt* and return the final answer."""
        self._trace("prompt_received", {"prompt": prompt})
        direct = self._try_builtin_answer(prompt)
        if direct is not None:
            self._trace("prompt_built_in_response", {"prompt": prompt, "answer": direct})
            print(_c(_GREEN, "\n[agent] Final answer:\n") + direct)
            return direct

        system_prompt = self.cfg["agent"]["system_prompt"]
        active_tools = self._select_tool_configs(prompt)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        print(_c(_YELLOW, f"[agent] Tool schemas in context: {len(active_tools)}/{len(self._tool_configs)}"))
        self._trace(
            "tool_schema_selection",
            {
                "active_tools": len(active_tools),
                "total_tools": len(self._tool_configs),
                "active_tool_names": [t["function"]["name"] for t in active_tools],
            },
        )

        for turn in range(1, self.MAX_TURNS + 1):
            print(_c(_CYAN, f"\n[agent] Turn {turn}/{self.MAX_TURNS}"))
            response_msg = self._complete(messages, active_tools)

            # No tool calls → model is done
            if not response_msg.tool_calls:
                answer = response_msg.content or ""
                print(_c(_GREEN, "\n[agent] Final answer:\n") + answer)
                return answer

            # Append assistant message (with tool_calls) to history
            messages.append(response_msg)

            # Execute each requested tool
            for tc in response_msg.tool_calls:
                tool_result = self._dispatch(tc)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.function.name,
                        "content": tool_result,
                    }
                )

        # Exhausted turns — ask the model for a summary with what it has
        print(_c(_RED, f"[agent] Reached {self.MAX_TURNS} turns. Requesting summary."))
        messages.append({"role": "user", "content": "Please summarise what you have found so far."})
        final = self._complete(messages, active_tools)
        return final.content or ""

    # ------------------------------------------------------------------
    # LLM completion with local → Groq fallback
    # ------------------------------------------------------------------

    def _complete(self, messages: List[Dict[str, Any]], tool_configs: List[Dict[str, Any]]):
        """Call the LLM; fall back to Groq on connection error."""
        local_model = self.cfg["llm"]["local"]["model"]
        groq_model = self.cfg["llm"].get("groq", {}).get("model", "llama-3.1-8b-instant")
        candidate_tools = list(tool_configs)
        minimum_tools = int(self.cfg.get("agent", {}).get("min_tools_per_request", 4))
        if minimum_tools < 1:
            minimum_tools = 1

        # --- Try local llama.cpp server ---
        while True:
            try:
                print(_c(_YELLOW, f"[agent]   → local ({local_model})"))
                self._trace(
                    "llm_request",
                    {
                        "backend": "local",
                        "model": local_model,
                        "message_count": len(messages),
                        "tool_count": len(candidate_tools),
                    },
                )
                resp = self._local_client.chat.completions.create(
                    model=local_model,
                    messages=messages,
                    tools=candidate_tools,
                    tool_choice="auto",
                )
                self._trace(
                    "llm_response",
                    {
                        "backend": "local",
                        "model": local_model,
                        "tool_calls": self._extract_tool_call_names(resp.choices[0].message),
                    },
                )
                return resp.choices[0].message
            except (openai.APIConnectionError, openai.APIStatusError) as local_err:
                print(_c(_RED, f"[agent]   Local LLM error: {local_err}"))
                self._trace(
                    "llm_error",
                    {
                        "backend": "local",
                        "model": local_model,
                        "tool_count": len(candidate_tools),
                        "error": str(local_err),
                    },
                )
                err_text = str(local_err)
                context_overflow = "exceeds the available context size" in err_text
                if context_overflow and len(candidate_tools) > minimum_tools:
                    next_count = max(minimum_tools, len(candidate_tools) // 2)
                    if next_count >= len(candidate_tools):
                        next_count = len(candidate_tools) - 1
                    candidate_tools = candidate_tools[:next_count]
                    self._trace(
                        "tool_context_downsize",
                        {
                            "reason": "context_overflow",
                            "new_tool_count": len(candidate_tools),
                        },
                    )
                    continue
                if context_overflow:
                    raise RuntimeError(
                        "Local LLM context window is too small even after auto-reducing tool schemas. "
                        "Restart with larger context, e.g.:\n"
                        "  LLAMA_CTX_SIZE=32768 bash scripts/start_server.sh\n"
                        "or configure GROQ_API_KEY for fallback."
                    ) from local_err
                break

        # --- Fall back to Groq ---
        if self._groq_client is None:
            raise RuntimeError(
                "Local LLM is unavailable and no Groq API key is configured. "
                "Set GROQ_API_KEY or llm.groq.api_key in config.local.yaml."
            )
        print(_c(_YELLOW, f"[agent]   → Groq fallback ({groq_model})"))
        self._trace(
            "llm_request",
            {
                "backend": "groq",
                "model": groq_model,
                "message_count": len(messages),
                "tool_count": len(tool_configs),
            },
        )
        resp = self._groq_client.chat.completions.create(
            model=groq_model,
            messages=messages,
            tools=candidate_tools,
            tool_choice="auto",
        )
        self._trace(
            "llm_response",
            {
                "backend": "groq",
                "model": groq_model,
                "tool_calls": self._extract_tool_call_names(resp.choices[0].message),
            },
        )
        return resp.choices[0].message

    def _try_builtin_answer(self, prompt: str) -> Optional[str]:
        """Return a deterministic local answer for simple metadata queries."""
        prompt_lc = prompt.lower()
        wants_skill_list = (
            ("list" in prompt_lc or "what" in prompt_lc or "show" in prompt_lc)
            and ("skills" in prompt_lc or "skill modules" in prompt_lc)
        )
        if not wants_skill_list:
            return None

        lines = [f"I have {len(self._skills)} skill modules in linux_skills:"]
        for skill in self._skills:
            tool_count = sum(1 for name in self._tool_functions if name.startswith(f"{skill}__"))
            lines.append(f"- {skill} ({tool_count} tools)")
        return "\n".join(lines)

    def _select_tool_configs(self, prompt: str) -> List[Dict[str, Any]]:
        """Select a context-safe subset of tools for the current prompt."""
        default_max = int(self.cfg.get("agent", {}).get("max_tools_per_request", 24))
        if default_max <= 0:
            return self._tool_configs

        normalized_prompt = prompt.lower().replace("ci/cd", "cicd")
        tokens = set(re.findall(r"[a-zA-Z0-9_]{3,}", normalized_prompt))
        stop = {"the", "and", "for", "with", "that", "this", "from", "into", "show", "list", "have"}
        tokens = {tok for tok in tokens if tok not in stop}
        keyword_skill_scores = self._keyword_skill_scores(tokens)

        scored: List[tuple[int, str]] = []
        for full_name in self._tool_functions.keys():
            skill, func = full_name.split("__", 1)
            score = 0
            if skill in tokens:
                score += 5
            score += keyword_skill_scores.get(skill, 0) * 4
            func_parts = set(func.split("_"))
            score += len(func_parts.intersection(tokens)) * 2
            if score > 0:
                scored.append((score, full_name))

        selected_names: List[str] = []
        if scored:
            scored.sort(key=lambda item: (-item[0], item[1]))
            selected_names = [name for _, name in scored[:default_max]]
        else:
            # Default tiny-safe core set when prompt does not map clearly.
            core_skills = [
                "file_system",
                "process_and_service",
                "networking",
                "package_management",
                "logging",
                "troubleshooting",
            ]
            for skill in core_skills:
                for name in sorted(self._tool_functions.keys()):
                    if name.startswith(f"{skill}__"):
                        selected_names.append(name)
                        if len(selected_names) >= default_max:
                            break
                if len(selected_names) >= default_max:
                    break

        selected = [self._tool_config_by_name[name] for name in selected_names if name in self._tool_config_by_name]
        return selected if selected else self._tool_configs[:default_max]

    def _keyword_skill_scores(self, tokens: set[str]) -> Dict[str, int]:
        keyword_map = {
            "kernel": {"boot_and_kernel"},
            "bootloader": {"boot_and_kernel"},
            "grub": {"boot_and_kernel"},
            "dracut": {"boot_and_kernel"},
            "initramfs": {"boot_and_kernel"},
            "bios": {"boot_and_kernel"},
            "uefi": {"boot_and_kernel"},
            "boot": {"boot_and_kernel", "file_system"},
            "proc": {"file_system"},
            "dev": {"file_system"},
            "var": {"file_system"},
            "filesystem": {"file_system", "storage"},
            "partition": {"storage"},
            "raid": {"storage"},
            "lvm": {"storage"},
            "iscsi": {"storage"},
            "mount": {"storage", "file_system"},
            "permission": {"user_and_group", "file_system"},
            "chmod": {"user_and_group"},
            "chown": {"user_and_group"},
            "chgrp": {"user_and_group"},
            "network": {"networking", "troubleshooting"},
            "ipv4": {"networking"},
            "ipv6": {"networking"},
            "distribution": {"troubleshooting"},
            "distributions": {"troubleshooting"},
            "cloud": {"troubleshooting"},
            "dns": {"networking", "troubleshooting"},
            "dhcp": {"networking"},
            "firewall": {"security"},
            "waf": {"security"},
            "iptables": {"security"},
            "ufw": {"security"},
            "nftables": {"security"},
            "pam": {"security"},
            "ldap": {"security"},
            "authentication": {"security"},
            "auth": {"security"},
            "crypto": {"security"},
            "cryptography": {"security"},
            "threat": {"security"},
            "cia": {"security"},
            "container": {"containerization"},
            "docker": {"containerization"},
            "process": {"process_and_service"},
            "daemon": {"process_and_service"},
            "systemd": {"process_and_service", "logging", "scheduling"},
            "journalctl": {"logging", "process_and_service"},
            "service": {"process_and_service"},
            "script": {"shell_scripting", "text_processing"},
            "awk": {"text_processing", "file_system"},
            "sed": {"text_processing", "file_system"},
            "grep": {"text_processing", "file_system"},
            "egrep": {"text_processing"},
            "find": {"file_system"},
            "tee": {"shell_scripting", "text_processing"},
            "git": {"version_control"},
            "terraform": {"iac_and_cicd"},
            "iac": {"iac_and_cicd"},
            "cicd": {"iac_and_cicd"},
            "package": {"package_management"},
            "apt": {"package_management"},
            "yum": {"package_management"},
            "pacman": {"package_management"},
            "performance": {"performance", "troubleshooting"},
            "cpu": {"performance"},
            "memory": {"performance"},
            "swap": {"storage", "performance"},
            "hardware": {"troubleshooting", "performance"},
            "lspci": {"troubleshooting"},
            "lsusb": {"troubleshooting"},
            "dmidecode": {"troubleshooting"},
            "schedule": {"scheduling"},
            "cron": {"scheduling"},
            "timer": {"scheduling"},
            "resolved": {"troubleshooting"},
            "log": {"logging"},
            "troubleshoot": {"troubleshooting"},
        }
        scores: Dict[str, int] = {}
        for token in tokens:
            for skill in keyword_map.get(token, set()):
                scores[skill] = scores.get(skill, 0) + 1
        return scores

    def _extract_tool_call_names(self, response_msg: Any) -> List[str]:
        names: List[str] = []
        for tc in getattr(response_msg, "tool_calls", []) or []:
            fn = getattr(tc, "function", None)
            name = getattr(fn, "name", None)
            if isinstance(name, str):
                names.append(name)
        return names

    def _trace(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if self._tracer is None:
            return
        self._tracer.log(event=event, payload=payload or {})

    # ------------------------------------------------------------------
    # Tool dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, tool_call) -> str:
        """Execute a single tool call and return its string output."""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}

        print(_c(_CYAN, f"[agent]   tool: {name}({args})"))
        self._trace("tool_call", {"name": name, "args": args})

        func = self._tool_functions.get(name)
        if func is None:
            return f"ERROR: unknown tool '{name}'"

        try:
            result = func(**args)
            output = str(result) if result is not None else "Done."
        except Exception as exc:
            output = f"ERROR executing {name}: {exc}"

        # Truncate very long outputs so they don't overflow the context window
        max_chars = self.cfg.get("agent", {}).get("max_tool_output_chars", 4000)
        if len(output) > max_chars:
            output = output[:max_chars] + f"\n... [truncated to {max_chars} chars]"

        print(textwrap.indent(output[:200], "    "))
        self._trace(
            "tool_result",
            {
                "name": name,
                "output_preview": output[:200],
                "output_chars": len(output),
                "is_error": output.startswith("ERROR"),
            },
        )
        return output


# ---------------------------------------------------------------------------
# CLI entry point (python3 agent.py --prompt "...")
# ---------------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Linux Skills Agent")
    parser.add_argument("--prompt", required=True, help="The task or question for the agent.")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (relative to this file). Default: config.yaml",
    )
    args = parser.parse_args()

    agent = LinuxSkillsAgent(config_path=args.config)
    agent.run(args.prompt)


if __name__ == "__main__":
    main()
