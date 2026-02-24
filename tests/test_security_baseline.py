from __future__ import annotations

import ast
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(module_name: str, rel_path: str):
    module_path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_shell_true_in_first_party_python():
    offenders: list[str] = []
    for path in REPO_ROOT.rglob("*.py"):
        if "runtime/vendor" in path.as_posix() or "/tests/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        if "shell=True" in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == [], f"shell=True is forbidden in first-party python: {offenders}"


def test_command_runner_subprocess_run_does_not_set_shell_true():
    command_runner = REPO_ROOT / "runtime/command_runner.py"
    tree = ast.parse(command_runner.read_text(encoding="utf-8"))

    shell_true_found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "run":
            continue
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                shell_true_found = True

    assert not shell_true_found, "runtime/command_runner.py must not use shell=True"


def test_ssh_defaults_to_strict_host_key_checking_yes():
    ssh_tools = _load_module("linux_skills_ssh_tools", "ssh/tools.py")
    captured: list[list[str]] = []

    def fake_run_command(cmd, **_kwargs):
        captured.append(cmd)
        return "ok"

    ssh_tools.run_command = fake_run_command
    ssh_tools.run_remote_command("host", "user", "echo hi")

    assert captured, "expected run_command invocation"
    assert "StrictHostKeyChecking=yes" in captured[0]


def test_ssh_can_explicitly_disable_host_key_checking():
    ssh_tools = _load_module("linux_skills_ssh_tools_relaxed", "ssh/tools.py")
    captured: list[list[str]] = []

    def fake_run_command(cmd, **_kwargs):
        captured.append(cmd)
        return "ok"

    ssh_tools.run_command = fake_run_command
    ssh_tools.copy_to_remote(
        "local.txt",
        "host",
        "user",
        "/tmp/local.txt",
        strict_host_key_checking=False,
    )

    assert captured, "expected run_command invocation"
    assert "StrictHostKeyChecking=no" in captured[0]


def test_start_server_binds_localhost_by_default():
    script = (REPO_ROOT / "runtime/scripts/start_server.sh").read_text(encoding="utf-8")
    assert 'HOST="127.0.0.1"' in script


def test_default_config_disables_groq_fallback():
    cfg = (REPO_ROOT / "runtime/config.yaml").read_text(encoding="utf-8")
    assert "enabled: false" in cfg
