#!/usr/bin/env python3
"""Update TESTS.md with latest runner pass/fail status."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


RUNNER_ORDER = [
    "live_prompt_contract",
    "unit_pytest",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _load_status(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_status(path: Path, data: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _render_status_table(status: Dict[str, dict]) -> str:
    lines: List[str] = []
    lines.append("| Runner | Last Status | Last Run (UTC) | Duration | Command | Summary |")
    lines.append("|---|---|---|---:|---|---|")

    for runner in RUNNER_ORDER:
        item = status.get(runner)
        if not item:
            lines.append(f"| `{runner}` | `NEVER` | - | - | - | - |")
            continue
        lines.append(
            "| `{runner}` | `{state}` | {run_at} | {duration}s | `{command}` | {summary} |".format(
                runner=runner,
                state=item.get("status", "UNKNOWN"),
                run_at=item.get("run_at", "-"),
                duration=item.get("duration_s", "-"),
                command=item.get("command", "-"),
                summary=item.get("summary", "-").replace("|", "\\|"),
            )
        )
    return "\n".join(lines)


def _update_tests_md(path: Path, status_table: str) -> None:
    text = path.read_text(encoding="utf-8")
    start_marker = "<!-- TEST_RUN_STATUS_START -->"
    end_marker = "<!-- TEST_RUN_STATUS_END -->"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError("TESTS.md is missing status markers.")

    before = text[: start + len(start_marker)]
    after = text[end:]
    new_text = f"{before}\n\n{status_table}\n\n{after}"
    path.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update TESTS.md run status block.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--status", required=True, choices=["PASS", "FAIL"])
    parser.add_argument("--command", required=True)
    parser.add_argument("--duration-s", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    tests_md = repo_root / "TESTS.md"
    status_json = repo_root / "runtime" / "logs" / "test_runner_status.json"

    data = _load_status(status_json)
    data[args.runner] = {
        "status": args.status,
        "run_at": _utc_now(),
        "duration_s": args.duration_s,
        "command": args.command,
        "summary": args.summary.strip() or "-",
    }
    _save_status(status_json, data)
    _update_tests_md(tests_md, _render_status_table(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

