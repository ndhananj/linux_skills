#!/usr/bin/env python3
"""Helpers for Python-level OS interactions with explicit tracing lines."""

from __future__ import annotations

import os
import tempfile


def _preview(value: str, limit: int = 500) -> str:
    text = (value or "").strip()
    if not text:
        return "(no output)"
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated to {limit} chars]"


def _log_outcome(result: str) -> None:
    print(f"[os->python] {_preview(result)}", flush=True)


def path_exists(path: str) -> bool:
    print(f"[python->os] exists path={path}", flush=True)
    ok = os.path.exists(path)
    _log_outcome(f"exists={ok}")
    return ok


def write_text(path: str, content: str, mode: str = "w") -> None:
    print(f"[python->os] write file={path} mode={mode} bytes={len(content)}", flush=True)
    with open(path, mode, encoding="utf-8") as fh:
        fh.write(content)
    _log_outcome("write=ok")


def chmod(path: str, mode: int) -> None:
    print(f"[python->os] chmod path={path} mode={oct(mode)}", flush=True)
    os.chmod(path, mode)
    _log_outcome("chmod=ok")


def unlink(path: str) -> None:
    print(f"[python->os] unlink path={path}", flush=True)
    os.unlink(path)
    _log_outcome("unlink=ok")


def mkstemp_script(content: str, suffix: str = ".sh") -> str:
    print(f"[python->os] mkstemp suffix={suffix}", flush=True)
    fd, path = tempfile.mkstemp(suffix=suffix)
    _log_outcome(f"fd={fd} path={path}")
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    return path


def expand_user(path: str) -> str:
    print(f"[python->os] expanduser path={path}", flush=True)
    out = os.path.expanduser(path)
    _log_outcome(out)
    return out
