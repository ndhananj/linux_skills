#!/usr/bin/env python3
"""
command_runner.py — Robust subprocess wrapper for the Linux Skills Agent.

All tool functions in this repository call run_command() rather than
subprocess directly, so that error handling, timeouts, and output
normalisation are applied consistently across every skill module.
"""

import subprocess
from typing import List, Optional


class CommandRunnerError(Exception):
    """Raised when a shell command exits with a non-zero return code,
    times out, or the executable cannot be found."""

    def __init__(self, message: str, stdout: str = "", stderr: str = "", returncode: int = -1):
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __str__(self):
        parts = [super().__str__()]
        if self.stderr:
            parts.append(f"stderr: {self.stderr.strip()}")
        return "\n".join(parts)


def _preview(text: str, limit: int = 500) -> str:
    value = text.strip()
    if not value:
        return "(no output)"
    if len(value) <= limit:
        return value
    return value[:limit] + f"\n... [truncated to {limit} chars]"


def _log_exchange(command: List[str], output: str) -> None:
    cmd = " ".join(command)
    print(f"[tool->terminal] {cmd}", flush=True)
    print(f"[terminal->tool] {_preview(output)}", flush=True)


def run_command(
    command: List[str],
    *,
    cwd: Optional[str] = None,
    stdin_input: Optional[str] = None,
    timeout: int = 120,
    allow_nonzero: bool = False,
) -> str:
    """Execute *command* and return its stdout as a stripped string.

    Parameters
    ----------
    command:
        The command and its arguments as a list, e.g. ``["ls", "-la", "/tmp"]``.
    cwd:
        Working directory for the subprocess.  Defaults to the caller's cwd.
    stdin_input:
        Optional text to pass to the process via stdin.
    timeout:
        Maximum seconds to wait before raising ``CommandRunnerError``.
    allow_nonzero:
        When *True*, a non-zero exit code is not treated as an error and the
        combined stdout+stderr is returned instead.  Useful for commands like
        ``grep`` that exit 1 when there are no matches.

    Returns
    -------
    str
        The stripped stdout of the command.

    Raises
    ------
    CommandRunnerError
        On non-zero exit (unless *allow_nonzero* is True), timeout, or
        missing executable.
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        _log_exchange(command, (exc.stdout or "") + (exc.stderr or ""))
        raise CommandRunnerError(
            f"Command timed out after {timeout}s: {' '.join(command)}",
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            returncode=-1,
        ) from exc
    except FileNotFoundError as exc:
        _log_exchange(command, f"Executable not found: '{command[0]}'")
        raise CommandRunnerError(
            f"Executable not found: '{command[0]}'. "
            "Ensure it is installed and present in $PATH.",
            returncode=-1,
        ) from exc

    if result.returncode != 0 and not allow_nonzero:
        _log_exchange(command, result.stdout.strip() or result.stderr.strip())
        raise CommandRunnerError(
            f"Command failed (exit {result.returncode}): {' '.join(command)}",
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    # Return stdout; if empty, fall back to stderr (some tools write there)
    output = result.stdout.strip() or result.stderr.strip()
    _log_exchange(command, output)
    return output
