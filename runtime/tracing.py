#!/usr/bin/env python3
"""Lightweight JSONL tracer for agent and tool-call events."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonlTracer:
    """Append structured events to a per-run JSONL file."""

    def __init__(self, log_dir: str, run_id: str):
        self.run_id = run_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"agent_trace_{run_id}.jsonl"

    def log(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        record = {
            "ts": _utc_now_iso(),
            "run_id": self.run_id,
            "event": event,
            "payload": payload or {},
        }
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")


def make_default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def default_log_dir(runtime_dir: str) -> str:
    return os.path.join(runtime_dir, "logs")
