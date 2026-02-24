#!/usr/bin/env python3
"""
agent.py — Linux Skills Agent

A tool-calling agent that:
  1. Tries the local llama.cpp server first (CPU-only, zero API cost).
  2. Falls back to the Groq free-tier API if the local server is unreachable
     or returns an error.
  3. Executes the tools requested by the LLM and feeds results back in a
     multi-turn loop until the model produces a final text answer.
"""

from __future__ import annotations

import os
import sys
import textwrap
from typing import Any, Dict, List, Optional

import openai

# The runtime helpers live in the same directory as this file
sys.path.insert(0, os.path.dirname(__file__))
from intent_policy import SelectionResult, select_tools
from llm_gateway import CompletionMetrics, OpenAILLMGateway
from settings import AppSettings, load_settings
from tool_dispatch import dispatch_tool_call
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


class LinuxSkillsAgent:
    """Orchestrates the LLM ↔ tool-calling loop."""

    MAX_TURNS = 8

    def __init__(self, config_path: str = "config.yaml"):
        abs_cfg = os.path.join(os.path.dirname(__file__), config_path)
        self.settings: AppSettings = load_settings(abs_cfg)
        self.cfg = self._to_legacy_cfg_dict(self.settings)

        self._local_client = openai.OpenAI(
            base_url=self.settings.llm.local.base_url,
            api_key=self.settings.llm.local.api_key,
        )
        self._groq_client = self._make_groq_client()

        self._tool_configs, self._tool_functions = self._load_tools()
        self._tool_config_by_name = {
            tc["function"]["name"]: tc for tc in self._tool_configs if tc.get("function", {}).get("name")
        }
        self._tool_names = tuple(sorted(self._tool_config_by_name.keys()))
        self._skills = sorted({name.split("__", 1)[0] for name in self._tool_functions.keys()})

        self._runtime_dir = os.path.dirname(__file__)
        self._tracer = self._make_tracer()
        self._gateway = OpenAILLMGateway(
            local_client=self._local_client,
            groq_client=self._groq_client,
            local_model=self.settings.llm.local.model,
            groq_model=self.settings.llm.groq.model,
            min_tools_per_request=self.settings.agent.min_tools_per_request,
            tracer=self._trace,
            on_metrics=self._on_completion_metrics,
        )

        print(_c(_GREEN, f"[agent] Ready — {len(self._tool_configs)} tools loaded."))

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _to_legacy_cfg_dict(self, settings: AppSettings) -> Dict[str, Any]:
        """Compat shim so tests/docs relying on `agent.cfg` still work."""
        return {
            "agent": {
                "system_prompt": settings.agent.system_prompt,
                "max_tool_output_chars": settings.agent.max_tool_output_chars,
                "max_tools_per_request": settings.agent.max_tools_per_request,
                "min_tools_per_request": settings.agent.min_tools_per_request,
                "shortlisting": {
                    "mode": settings.agent.shortlisting.mode,
                    "fallback_mode": settings.agent.shortlisting.fallback_mode,
                },
                "tracing": {
                    "enabled": settings.agent.tracing.enabled,
                    "log_dir": settings.agent.tracing.log_dir,
                },
                "progress": {
                    "enabled": settings.agent.progress.enabled,
                    "show_latency": settings.agent.progress.show_latency,
                },
            },
            "llm": {
                "local": {
                    "base_url": settings.llm.local.base_url,
                    "api_key": settings.llm.local.api_key,
                    "model": settings.llm.local.model,
                },
                "groq": {
                    "enabled": settings.llm.groq.enabled,
                    "api_key": settings.llm.groq.api_key,
                    "model": settings.llm.groq.model,
                },
            },
        }

    def _make_tracer(self) -> Optional[JsonlTracer]:
        tracing_cfg = self.settings.agent.tracing
        if not tracing_cfg.enabled:
            return None
        run_id = make_default_run_id()
        log_dir = tracing_cfg.log_dir or default_log_dir(self._runtime_dir)
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(self._runtime_dir, log_dir)
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
        gc = self.settings.llm.groq
        if not gc.enabled:
            print(_c(_YELLOW, "[agent] Groq fallback disabled in config (llm.groq.enabled=false)."))
            return None
        if not gc.api_key or gc.api_key == "YOUR_GROQ_API_KEY":
            print(_c(_YELLOW, "[agent] Groq API key not set — fallback disabled."))
            return None
        return openai.OpenAI(base_url="https://api.groq.com/openai/v1", api_key=gc.api_key)

    def _load_tools(self):
        skills_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return discover_skills(skills_dir)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, prompt: str) -> str:
        self._trace("prompt_received", {"prompt": prompt})
        direct = self._try_builtin_answer(prompt)
        if direct is not None:
            self._trace("prompt_built_in_response", {"prompt": prompt, "answer": direct})
            print(_c(_GREEN, "\n[agent] Final answer:\n") + direct)
            return direct

        system_prompt = self.settings.agent.system_prompt
        selection = self._select_tool_configs(prompt)
        active_tools = selection["tools"]

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
                "selection_mode": selection["mode"],
                "intent_family": selection.get("intent_family"),
                "confidence": selection.get("confidence"),
                "excluded_tools": selection.get("excluded_tools", []),
            },
        )

        for turn in range(1, self.MAX_TURNS + 1):
            print(_c(_CYAN, f"\n[agent] Turn {turn}/{self.MAX_TURNS}"))
            response_msg = self._complete(messages, active_tools)

            if not response_msg.tool_calls:
                answer = response_msg.content or ""
                print(_c(_GREEN, "\n[agent] Final answer:\n") + answer)
                return answer

            messages.append(response_msg)
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

        print(_c(_RED, f"[agent] Reached {self.MAX_TURNS} turns. Requesting summary."))
        messages.append({"role": "user", "content": "Please summarise what you have found so far."})
        final = self._complete(messages, active_tools)
        return final.content or ""

    # ------------------------------------------------------------------
    # Selection / completion / dispatch (backward-compatible internals)
    # ------------------------------------------------------------------

    def _select_tool_configs(self, prompt: str) -> Dict[str, Any]:
        result: SelectionResult = select_tools(
            prompt=prompt,
            tool_names=self._tool_names,
            max_tools=self.settings.agent.max_tools_per_request,
            mode=self.settings.agent.shortlisting.mode,
        )
        tools = [self._tool_config_by_name[name] for name in result.tool_names if name in self._tool_config_by_name]
        return {
            "tools": tools,
            "mode": result.mode,
            "intent_family": result.intent_family,
            "confidence": result.confidence,
            "excluded_tools": list(result.excluded_tools),
        }

    def _complete(self, messages: List[Dict[str, Any]], tool_configs: List[Dict[str, Any]], tool_choice: str = "auto"):
        if self.settings.agent.progress.enabled:
            print(
                _c(
                    _YELLOW,
                    f"[agent]   -> local ({self.settings.llm.local.model}) tools={len(tool_configs)} choice={tool_choice}",
                )
            )
        return self._gateway.complete(messages=messages, tool_configs=tool_configs, tool_choice=tool_choice)

    def _dispatch(self, tool_call) -> str:
        name = tool_call.function.name
        try:
            args_preview = tool_call.function.arguments
        except Exception:
            args_preview = "{}"
        print(_c(_CYAN, f"[agent]   tool: {name}({args_preview})"))

        output = dispatch_tool_call(
            tool_call=tool_call,
            tool_functions=self._tool_functions,
            max_output_chars=self.settings.agent.max_tool_output_chars,
            tracer=self._trace,
        )
        print(textwrap.indent(output[:200], "    "))
        return output

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _try_builtin_answer(self, prompt: str) -> Optional[str]:
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

    def _on_completion_metrics(self, metrics: CompletionMetrics) -> None:
        if not self.settings.agent.progress.enabled or not self.settings.agent.progress.show_latency:
            return
        print(
            _c(
                _YELLOW,
                f"[agent]   <- {metrics.backend} ({metrics.model}) {metrics.latency_s:.2f}s tools={metrics.tool_count}",
            )
        )

    def _trace(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if self._tracer is None:
            return
        self._tracer.log(event=event, payload=payload or {})


# ---------------------------------------------------------------------------
# CLI entry point
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
