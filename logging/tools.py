"""
logging/tools.py — Tools for viewing and managing Linux system logs.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def tail_log(path: str, lines: int = 50) -> str:
    """Show the last N lines of a log file.

    path: Path to the log file.
    lines: Number of lines to show from the end of the file.
    """
    return run_command(["tail", "-n", str(lines), path])


def head_log(path: str, lines: int = 50) -> str:
    """Show the first N lines of a log file.

    path: Path to the log file.
    lines: Number of lines to show from the start of the file.
    """
    return run_command(["head", "-n", str(lines), path])


def search_log(path: str, pattern: str, ignore_case: bool = False) -> str:
    """Search a log file for lines matching a pattern.

    path: Path to the log file.
    pattern: Regular expression or fixed string to search for.
    ignore_case: When True, perform case-insensitive matching.
    """
    cmd = ["grep"]
    if ignore_case:
        cmd.append("-i")
    cmd.extend([pattern, path])
    return run_command(cmd, allow_nonzero=True)


def view_journal(unit: str = None, since: str = None, until: str = None, lines: int = 100, priority: str = None) -> str:
    """View the systemd journal.

    unit: Optional service/unit name to filter by, e.g. 'nginx'.
    since: Show entries since this time, e.g. '2024-01-01 00:00:00' or '1 hour ago'.
    until: Show entries until this time.
    lines: Number of recent lines to show.
    priority: Filter by priority: 'emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug'.
    """
    cmd = ["journalctl", "-n", str(lines), "--no-pager"]
    if unit:
        cmd.extend(["-u", unit])
    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])
    if priority:
        cmd.extend(["-p", priority])
    return run_command(cmd)


def list_log_files() -> str:
    """List log files in /var/log."""
    return run_command(["ls", "-lhrt", "/var/log"])


def show_dmesg(lines: int = 50) -> str:
    """Show kernel ring buffer messages (hardware and driver events).

    lines: Number of recent lines to show.
    """
    return run_command(["dmesg", "--time-format=iso", "-T"])


def rotate_logs(config_file: str = "/etc/logrotate.conf", force: bool = False) -> str:
    """Rotate log files according to a logrotate configuration.

    config_file: Path to the logrotate configuration file.
    force: When True, force rotation even if it is not yet due.
    """
    cmd = ["logrotate"]
    if force:
        cmd.append("--force")
    cmd.append(config_file)
    return run_command(cmd)


def write_log_entry(message: str, priority: str = "info", tag: str = "agent") -> str:
    """Write a message to the system log via logger.

    message: The message to write.
    priority: Syslog priority: 'emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug'.
    tag: Tag to identify the source of the message.
    """
    return run_command(["logger", "-p", f"user.{priority}", "-t", tag, message])


def show_auth_log(lines: int = 100) -> str:
    """Show recent authentication log entries.

    lines: Number of recent lines to show.
    """
    auth_log = "/var/log/auth.log"
    if not os.path.exists(auth_log):
        auth_log = "/var/log/secure"  # RHEL/CentOS
    return run_command(["tail", "-n", str(lines), auth_log])


def show_syslog(lines: int = 100) -> str:
    """Show recent syslog entries.

    lines: Number of recent lines to show.
    """
    syslog = "/var/log/syslog"
    if not os.path.exists(syslog):
        syslog = "/var/log/messages"  # RHEL/CentOS
    return run_command(["tail", "-n", str(lines), syslog])
