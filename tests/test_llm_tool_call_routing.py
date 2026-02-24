from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_agent_class():
    module_path = REPO_ROOT / "runtime/agent.py"
    spec = importlib.util.spec_from_file_location("linux_skills_runtime_agent", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LinuxSkillsAgent


def _make_temp_config(tmp_path: Path, *, tracing_enabled: bool = False) -> Path:
    base_cfg = yaml.safe_load((REPO_ROOT / "runtime/config.yaml").read_text(encoding="utf-8"))
    base_cfg.setdefault("agent", {}).setdefault("tracing", {})["enabled"] = tracing_enabled
    if tracing_enabled:
        base_cfg["agent"]["tracing"]["log_dir"] = str(tmp_path)
    cfg_path = tmp_path / "test.config.yaml"
    cfg_path.write_text(yaml.safe_dump(base_cfg), encoding="utf-8")
    return cfg_path


def test_prompt_matrix_routes_to_expected_skills(tmp_path: Path):
    LinuxSkillsAgent = _load_agent_class()
    cfg_path = _make_temp_config(tmp_path, tracing_enabled=False)
    agent = LinuxSkillsAgent(config_path=str(cfg_path))

    matrix = yaml.safe_load(
        (REPO_ROOT / "tests/fixtures/llm_tool_call_expectations.yaml").read_text(encoding="utf-8")
    )
    failures: list[str] = []

    for case in matrix["cases"]:
        prompt = case["prompt"]
        expected_skills = set(case["expected_skills"])

        selected = agent._select_tool_configs(prompt)
        selected_skills = {cfg["function"]["name"].split("__", 1)[0] for cfg in selected["tools"]}

        if selected_skills.isdisjoint(expected_skills):
            failures.append(
                f"{case['id']}: expected one of {sorted(expected_skills)} but got {sorted(selected_skills)}"
            )

    assert not failures, "\n".join(failures)


def test_largest_files_prompt_uses_file_size_slice(tmp_path: Path):
    LinuxSkillsAgent = _load_agent_class()
    cfg_path = _make_temp_config(tmp_path, tracing_enabled=False)
    agent = LinuxSkillsAgent(config_path=str(cfg_path))

    selected = agent._select_tool_configs("Show me the 10 largest files in .")
    names = [cfg["function"]["name"] for cfg in selected["tools"]]

    assert selected["mode"] == "per_skill_fixed_slice"
    assert selected["intent_family"] == "file_size_listing"
    assert "file_system__largest_files" in names
    assert "file_system__find_files" not in names
    assert "text_processing__concatenate_files" not in names


def test_directories_prompt_uses_directory_listing_slice(tmp_path: Path):
    LinuxSkillsAgent = _load_agent_class()
    cfg_path = _make_temp_config(tmp_path, tracing_enabled=False)
    agent = LinuxSkillsAgent(config_path=str(cfg_path))

    selected = agent._select_tool_configs("What are all the directories in ../?")
    names = [cfg["function"]["name"] for cfg in selected["tools"]]

    assert selected["mode"] == "per_skill_fixed_slice"
    assert selected["intent_family"] == "directory_listing"
    assert "file_system__list_directories" in names


def test_recursive_directories_prompt_uses_recursive_slice(tmp_path: Path):
    LinuxSkillsAgent = _load_agent_class()
    cfg_path = _make_temp_config(tmp_path, tracing_enabled=False)
    agent = LinuxSkillsAgent(config_path=str(cfg_path))

    selected = agent._select_tool_configs("List directories recursively under ../")
    names = [cfg["function"]["name"] for cfg in selected["tools"]]

    assert selected["mode"] == "per_skill_fixed_slice"
    assert selected["intent_family"] == "directory_listing_recursive"
    assert "file_system__list_directories_recursive" in names


def test_tracing_logs_tool_calls(tmp_path: Path):
    LinuxSkillsAgent = _load_agent_class()
    cfg_path = _make_temp_config(tmp_path, tracing_enabled=True)
    agent = LinuxSkillsAgent(config_path=str(cfg_path))

    agent._tool_functions = {"dummy__echo": lambda text="": f"echo:{text}"}

    tool_call = SimpleNamespace(
        id="tc_1",
        function=SimpleNamespace(name="dummy__echo", arguments='{"text": "hello"}'),
    )
    output = agent._dispatch(tool_call)

    assert output == "echo:hello"

    trace_files = sorted(tmp_path.glob("agent_trace_*.jsonl"))
    assert trace_files, "expected at least one trace file"

    events = []
    for line in trace_files[0].read_text(encoding="utf-8").splitlines():
        events.append(json.loads(line))

    event_names = [ev["event"] for ev in events]
    assert "tool_call" in event_names
    assert "tool_result" in event_names

    tool_events = [ev for ev in events if ev["event"] == "tool_call"]
    assert any(ev["payload"].get("name") == "dummy__echo" for ev in tool_events)
