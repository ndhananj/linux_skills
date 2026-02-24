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
import sys
import textwrap
from typing import Any, Dict, List, Optional

import openai
import yaml

# The tool registry lives in the same directory as this file
sys.path.insert(0, os.path.dirname(__file__))
from tool_registry import discover_skills

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
        system_prompt = self.cfg["agent"]["system_prompt"]
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        for turn in range(1, self.MAX_TURNS + 1):
            print(_c(_CYAN, f"\n[agent] Turn {turn}/{self.MAX_TURNS}"))
            response_msg = self._complete(messages)

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
        final = self._complete(messages)
        return final.content or ""

    # ------------------------------------------------------------------
    # LLM completion with local → Groq fallback
    # ------------------------------------------------------------------

    def _complete(self, messages: List[Dict[str, Any]]):
        """Call the LLM; fall back to Groq on connection error."""
        local_model = self.cfg["llm"]["local"]["model"]
        groq_model = self.cfg["llm"].get("groq", {}).get("model", "llama-3.1-8b-instant")

        # --- Try local llama.cpp server ---
        try:
            print(_c(_YELLOW, f"[agent]   → local ({local_model})"))
            resp = self._local_client.chat.completions.create(
                model=local_model,
                messages=messages,
                tools=self._tool_configs,
                tool_choice="auto",
            )
            return resp.choices[0].message
        except (openai.APIConnectionError, openai.APIStatusError) as local_err:
            print(_c(_RED, f"[agent]   Local LLM error: {local_err}"))
            err_text = str(local_err)
            if "exceeds the available context size" in err_text:
                raise RuntimeError(
                    "Local LLM context window is too small for the loaded tool set. "
                    "Restart the local server with a larger context, e.g.:\n"
                    "  LLAMA_CTX_SIZE=32768 bash scripts/start_server.sh\n"
                    "Then re-run agent.py."
                ) from local_err

        # --- Fall back to Groq ---
        if self._groq_client is None:
            raise RuntimeError(
                "Local LLM is unavailable and no Groq API key is configured. "
                "Set GROQ_API_KEY or llm.groq.api_key in config.local.yaml."
            )
        print(_c(_YELLOW, f"[agent]   → Groq fallback ({groq_model})"))
        resp = self._groq_client.chat.completions.create(
            model=groq_model,
            messages=messages,
            tools=self._tool_configs,
            tool_choice="auto",
        )
        return resp.choices[0].message

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
