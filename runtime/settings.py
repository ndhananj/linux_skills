#!/usr/bin/env python3
"""Centralized runtime settings loading and validation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

import yaml


@dataclass(frozen=True)
class TracingSettings:
    enabled: bool = True
    log_dir: str = "logs"


@dataclass(frozen=True)
class ProgressSettings:
    enabled: bool = True
    show_latency: bool = True


@dataclass(frozen=True)
class ShortlistingSettings:
    mode: str = "per_skill_fixed_slice"
    fallback_mode: str = "score_based"


@dataclass(frozen=True)
class AgentSettings:
    system_prompt: str
    max_tool_output_chars: int = 4000
    max_tools_per_request: int = 16
    min_tools_per_request: int = 4
    shortlisting: ShortlistingSettings = ShortlistingSettings()
    tracing: TracingSettings = TracingSettings()
    progress: ProgressSettings = ProgressSettings()


@dataclass(frozen=True)
class LocalLLMSettings:
    base_url: str
    api_key: str
    model: str


@dataclass(frozen=True)
class GroqSettings:
    enabled: bool = True
    api_key: str = ""
    model: str = "llama-3.1-8b-instant"


@dataclass(frozen=True)
class LLMSettings:
    local: LocalLLMSettings
    groq: GroqSettings


@dataclass(frozen=True)
class AppSettings:
    agent: AgentSettings
    llm: LLMSettings


def _deep_merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_settings(config_path: str, env: Optional[Mapping[str, str]] = None) -> AppSettings:
    env = env or os.environ

    cfg = _load_yaml(config_path)

    config_dir = os.path.dirname(config_path)
    local_path = os.path.join(config_dir, "config.local.yaml")
    if os.path.exists(local_path):
        cfg = _deep_merge_dicts(cfg, _load_yaml(local_path))

    if env.get("GROQ_API_KEY"):
        cfg.setdefault("llm", {}).setdefault("groq", {})["api_key"] = env["GROQ_API_KEY"]

    agent_cfg = cfg.get("agent", {})
    llm_cfg = cfg.get("llm", {})

    short_cfg = agent_cfg.get("shortlisting", {})
    trace_cfg = agent_cfg.get("tracing", {})
    prog_cfg = agent_cfg.get("progress", {})

    local_cfg = llm_cfg.get("local", {})
    groq_cfg = llm_cfg.get("groq", {})

    system_prompt = agent_cfg.get("system_prompt", "You are a Linux admin assistant.")

    agent = AgentSettings(
        system_prompt=system_prompt,
        max_tool_output_chars=int(agent_cfg.get("max_tool_output_chars", 4000)),
        max_tools_per_request=int(agent_cfg.get("max_tools_per_request", 16)),
        min_tools_per_request=max(1, int(agent_cfg.get("min_tools_per_request", 4))),
        shortlisting=ShortlistingSettings(
            mode=str(short_cfg.get("mode", "per_skill_fixed_slice")),
            fallback_mode=str(short_cfg.get("fallback_mode", "score_based")),
        ),
        tracing=TracingSettings(
            enabled=bool(trace_cfg.get("enabled", True)),
            log_dir=str(trace_cfg.get("log_dir", "logs")),
        ),
        progress=ProgressSettings(
            enabled=bool(prog_cfg.get("enabled", True)),
            show_latency=bool(prog_cfg.get("show_latency", True)),
        ),
    )

    llm = LLMSettings(
        local=LocalLLMSettings(
            base_url=str(local_cfg.get("base_url", "http://localhost:8080/v1")),
            api_key=str(local_cfg.get("api_key", "local-key")),
            model=str(local_cfg.get("model", "local-model")),
        ),
        groq=GroqSettings(
            enabled=bool(groq_cfg.get("enabled", True)),
            api_key=str(groq_cfg.get("api_key", "")),
            model=str(groq_cfg.get("model", "llama-3.1-8b-instant")),
        ),
    )

    return AppSettings(agent=agent, llm=llm)
