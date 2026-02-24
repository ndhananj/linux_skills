from __future__ import annotations

import importlib.util
import socket
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime"


def _load_agent_class():
    module_path = RUNTIME_DIR / "agent.py"
    spec = importlib.util.spec_from_file_location("linux_skills_runtime_agent_live", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LinuxSkillsAgent


def _server_reachable(host: str = "127.0.0.1", port: int = 8080, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _make_live_config(tmp_path: Path) -> Path:
    cfg = yaml.safe_load((RUNTIME_DIR / "config.yaml").read_text(encoding="utf-8"))
    cfg.setdefault("agent", {}).setdefault("tracing", {})["enabled"] = True
    cfg["agent"]["tracing"]["log_dir"] = str(tmp_path / "logs")

    path = tmp_path / "live.config.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


@pytest.mark.skipif(
    not bool(__import__("os").environ.get("RUN_LLM_PROMPT_CONTRACT")),
    reason="Set RUN_LLM_PROMPT_CONTRACT=1 to run live LLM prompt contract tests.",
)
def test_live_llm_prompt_contracts(tmp_path: Path):
    if not _server_reachable():
        pytest.skip("llama.cpp server is not reachable at 127.0.0.1:8080")

    LinuxSkillsAgent = _load_agent_class()
    cfg_path = _make_live_config(tmp_path)
    agent = LinuxSkillsAgent(config_path=str(cfg_path))

    cases = yaml.safe_load((REPO_ROOT / "tests/fixtures/llm_prompt_contracts.yaml").read_text(encoding="utf-8"))["cases"]

    failures: list[str] = []
    for case in cases:
        prompt = case["prompt"]
        expected_skill = case["expected_skill"]
        expected_any_tools = set(case.get("expected_any_tools", []))

        system_prompt = agent.cfg["agent"]["system_prompt"]
        selected = agent._select_tool_configs(prompt)
        active_tools = selected["tools"]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        response_msg = agent._complete(messages, active_tools, tool_choice="required")
        tool_calls = list(getattr(response_msg, "tool_calls", []) or [])
        names = []
        for tc in tool_calls:
            fn = getattr(tc, "function", None)
            name = getattr(fn, "name", None)
            if isinstance(name, str):
                names.append(name)

        if not names:
            failures.append(f"{case['id']}: no tool calls returned")
            continue

        if not any(name.startswith(f"{expected_skill}__") for name in names):
            failures.append(
                f"{case['id']}: expected skill '{expected_skill}' not called; got {names}"
            )
            continue

        if expected_any_tools and expected_any_tools.isdisjoint(set(names)):
            failures.append(
                f"{case['id']}: expected one of {sorted(expected_any_tools)}; got {names}"
            )

    assert not failures, "\n".join(failures)
