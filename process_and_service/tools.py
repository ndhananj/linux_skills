"""
process_and_service/tools.py — Tools for managing Linux processes and systemd services.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def list_processes(all_users: bool = True, tree: bool = False) -> str:
    """List running processes.

    all_users: When True, show processes for all users (ps aux).
    tree: When True, show a process tree (pstree).
    """
    if tree:
        return run_command(["pstree", "-p"])
    flags = "aux" if all_users else "x"
    return run_command(["ps", flags])


def show_top_processes(batch: bool = True, iterations: int = 1) -> str:
    """Show a snapshot of the most CPU/memory intensive processes.

    batch: When True, run in batch mode (non-interactive, suitable for scripts).
    iterations: Number of iterations to run in batch mode.
    """
    cmd = ["top"]
    if batch:
        cmd.extend(["-b", "-n", str(iterations)])
    return run_command(cmd)


def find_process(name: str) -> str:
    """Find processes by name.

    name: Process name or substring to search for.
    """
    return run_command(["pgrep", "-la", name], allow_nonzero=True)


def kill_process(pid: int, signal: int = 15) -> str:
    """Send a signal to a process.

    pid: Process ID to signal.
    signal: Signal number. 15 (SIGTERM) for graceful shutdown, 9 (SIGKILL) to force kill.
    """
    return run_command(["kill", f"-{signal}", str(pid)])


def kill_process_by_name(name: str, signal: int = 15) -> str:
    """Send a signal to all processes matching a name.

    name: Process name to match.
    signal: Signal number. 15 (SIGTERM) for graceful shutdown, 9 (SIGKILL) to force kill.
    """
    return run_command(["pkill", f"-{signal}", name], allow_nonzero=True)


def show_process_details(pid: int) -> str:
    """Show detailed information about a specific process.

    pid: Process ID to inspect.
    """
    return run_command(["cat", f"/proc/{pid}/status"])


def run_in_background(command: str) -> str:
    """Run a command in the background using nohup.

    command: Shell command string to run in the background.
    """
    return run_command(["bash", "-c", f"nohup {command} &>/dev/null & echo $!"])


def service_status(service_name: str) -> str:
    """Show the status of a systemd service.

    service_name: Name of the service, e.g. 'nginx' or 'sshd'.
    """
    return run_command(["systemctl", "status", service_name], allow_nonzero=True)


def start_service(service_name: str) -> str:
    """Start a systemd service.

    service_name: Name of the service to start.
    """
    return run_command(["systemctl", "start", service_name])


def stop_service(service_name: str) -> str:
    """Stop a systemd service.

    service_name: Name of the service to stop.
    """
    return run_command(["systemctl", "stop", service_name])


def restart_service(service_name: str) -> str:
    """Restart a systemd service.

    service_name: Name of the service to restart.
    """
    return run_command(["systemctl", "restart", service_name])


def reload_service(service_name: str) -> str:
    """Reload a systemd service's configuration without restarting it.

    service_name: Name of the service to reload.
    """
    return run_command(["systemctl", "reload", service_name])


def enable_service(service_name: str) -> str:
    """Enable a systemd service to start automatically at boot.

    service_name: Name of the service to enable.
    """
    return run_command(["systemctl", "enable", service_name])


def disable_service(service_name: str) -> str:
    """Disable a systemd service from starting at boot.

    service_name: Name of the service to disable.
    """
    return run_command(["systemctl", "disable", service_name])


def list_services(state: str = None) -> str:
    """List systemd services.

    state: Optional filter: 'active', 'inactive', 'failed', etc.
    """
    cmd = ["systemctl", "list-units", "--type=service"]
    if state:
        cmd.extend(["--state", state])
    return run_command(cmd)


def view_journal(service_name: str = None, lines: int = 50, follow: bool = False) -> str:
    """View the systemd journal log.

    service_name: Optional service name to filter log entries.
    lines: Number of recent lines to show.
    follow: When True, follow the log in real time (not suitable for agent use).
    """
    cmd = ["journalctl", "-n", str(lines)]
    if service_name:
        cmd.extend(["-u", service_name])
    if follow:
        cmd.append("-f")
    return run_command(cmd)
