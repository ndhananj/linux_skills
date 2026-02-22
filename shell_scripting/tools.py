"""
shell_scripting/tools.py — Tools for creating and executing shell scripts.
"""

import sys
import os
import subprocess
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def run_shell_script(path: str, args: str = None) -> str:
    """Execute a shell script file.

    path: Path to the shell script to execute.
    args: Optional space-separated arguments to pass to the script.
    """
    cmd = ["bash", path]
    if args:
        cmd.extend(args.split())
    return run_command(cmd)


def run_shell_command(command: str) -> str:
    """Execute an arbitrary shell command string.

    command: Shell command string to execute, e.g. 'ls -la /tmp | head -5'.
    """
    return run_command(["bash", "-c", command])


def create_script(path: str, content: str, executable: bool = True) -> str:
    """Create a shell script file with the given content.

    path: Path where the script should be saved.
    content: Shell script content (without the shebang; it will be added automatically).
    executable: When True, make the script executable (chmod +x).
    """
    full_content = "#!/usr/bin/env bash\nset -euo pipefail\n\n" + content
    with open(path, "w") as fh:
        fh.write(full_content)
    if executable:
        os.chmod(path, 0o755)
    return f"Script created at {path}"


def run_inline_script(script: str) -> str:
    """Execute a multi-line shell script provided as a string.

    script: Multi-line shell script content to execute.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as tmp:
        tmp.write("#!/usr/bin/env bash\nset -euo pipefail\n\n" + script)
        tmp_path = tmp.name
    try:
        os.chmod(tmp_path, 0o700)
        return run_command(["bash", tmp_path])
    finally:
        os.unlink(tmp_path)


def pipe_commands(commands: str) -> str:
    """Execute a pipeline of shell commands.

    commands: Pipeline string, e.g. 'cat /etc/passwd | grep root | cut -d: -f1'.
    """
    return run_command(["bash", "-c", commands])


def check_script_syntax(path: str) -> str:
    """Check a shell script for syntax errors without executing it.

    path: Path to the shell script to check.
    """
    return run_command(["bash", "-n", path], allow_nonzero=True)


def make_executable(path: str) -> str:
    """Make a file executable.

    path: Path to the file.
    """
    return run_command(["chmod", "+x", path])


def show_shell_variables() -> str:
    """Show all currently set shell variables and their values."""
    return run_command(["bash", "-c", "set"])


def show_command_history(lines: int = 20) -> str:
    """Show the most recent shell command history.

    lines: Number of recent history entries to show.
    """
    history_file = os.path.expanduser("~/.bash_history")
    return run_command(["tail", "-n", str(lines), history_file], allow_nonzero=True)
