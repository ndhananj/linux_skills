#!/usr/bin/env python3
"""LLM completion gateway with overflow downsizing and fallback."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

import openai


@dataclass
class CompletionMetrics:
    backend: str
    model: str
    latency_s: float
    tool_count: int


class OpenAILLMGateway:
    def __init__(
        self,
        local_client: openai.OpenAI,
        groq_client: Optional[openai.OpenAI],
        local_model: str,
        groq_model: str,
        min_tools_per_request: int,
        tracer: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_metrics: Optional[Callable[[CompletionMetrics], None]] = None,
    ):
        self.local_client = local_client
        self.groq_client = groq_client
        self.local_model = local_model
        self.groq_model = groq_model
        self.min_tools_per_request = max(1, min_tools_per_request)
        self.tracer = tracer
        self.on_metrics = on_metrics

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tool_configs: Sequence[Dict[str, Any]],
        tool_choice: str,
    ):
        candidate_tools = list(tool_configs)

        while True:
            start = time.perf_counter()
            try:
                self._trace(
                    "llm_request",
                    {
                        "backend": "local",
                        "model": self.local_model,
                        "message_count": len(messages),
                        "tool_count": len(candidate_tools),
                    },
                )
                resp = self.local_client.chat.completions.create(
                    model=self.local_model,
                    messages=messages,
                    tools=candidate_tools,
                    tool_choice=tool_choice,
                )
                latency = time.perf_counter() - start
                self._emit_metrics("local", self.local_model, latency, len(candidate_tools))
                self._trace(
                    "llm_response",
                    {
                        "backend": "local",
                        "model": self.local_model,
                        "tool_calls": _extract_tool_call_names(resp.choices[0].message),
                        "latency_s": round(latency, 4),
                    },
                )
                return resp.choices[0].message
            except (openai.APIConnectionError, openai.APIStatusError) as local_err:
                latency = time.perf_counter() - start
                self._emit_metrics("local", self.local_model, latency, len(candidate_tools))
                self._trace(
                    "llm_error",
                    {
                        "backend": "local",
                        "model": self.local_model,
                        "tool_count": len(candidate_tools),
                        "latency_s": round(latency, 4),
                        "error": str(local_err),
                    },
                )
                err_text = str(local_err)
                context_overflow = "exceeds the available context size" in err_text
                if context_overflow and len(candidate_tools) > self.min_tools_per_request:
                    next_count = max(self.min_tools_per_request, len(candidate_tools) // 2)
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

        if self.groq_client is None:
            raise RuntimeError(
                "Local LLM is unavailable and no Groq API key is configured. "
                "Set GROQ_API_KEY or llm.groq.api_key in config.local.yaml."
            )

        start = time.perf_counter()
        self._trace(
            "llm_request",
            {
                "backend": "groq",
                "model": self.groq_model,
                "message_count": len(messages),
                "tool_count": len(candidate_tools),
            },
        )
        resp = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=messages,
            tools=candidate_tools,
            tool_choice=tool_choice,
        )
        latency = time.perf_counter() - start
        self._emit_metrics("groq", self.groq_model, latency, len(candidate_tools))
        self._trace(
            "llm_response",
            {
                "backend": "groq",
                "model": self.groq_model,
                "tool_calls": _extract_tool_call_names(resp.choices[0].message),
                "latency_s": round(latency, 4),
            },
        )
        return resp.choices[0].message

    def _trace(self, event: str, payload: Dict[str, Any]) -> None:
        if self.tracer is not None:
            self.tracer(event, payload)

    def _emit_metrics(self, backend: str, model: str, latency_s: float, tool_count: int) -> None:
        if self.on_metrics is None:
            return
        self.on_metrics(CompletionMetrics(backend=backend, model=model, latency_s=latency_s, tool_count=tool_count))


def _extract_tool_call_names(response_msg: Any) -> List[str]:
    names: List[str] = []
    for tc in getattr(response_msg, "tool_calls", []) or []:
        fn = getattr(tc, "function", None)
        name = getattr(fn, "name", None)
        if isinstance(name, str):
            names.append(name)
    return names
