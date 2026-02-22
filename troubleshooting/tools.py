"""
troubleshooting/tools.py — Tools for diagnosing and troubleshooting Linux systems.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def show_system_info() -> str:
    """Show basic system information including OS, kernel, and hostname."""
    return run_command(["uname", "-a"])


def show_os_release() -> str:
    """Show operating system identification information."""
    return run_command(["cat", "/etc/os-release"])


def show_kernel_messages(lines: int = 50) -> str:
    """Show recent kernel ring buffer messages.

    lines: Number of recent lines to show.
    """
    return run_command(["dmesg", "-T", "--level=err,warn,crit,emerg"])


def list_pci_devices() -> str:
    """List all PCI devices in the system."""
    return run_command(["lspci", "-v"], allow_nonzero=True)


def list_usb_devices() -> str:
    """List all USB devices connected to the system."""
    return run_command(["lsusb"], allow_nonzero=True)


def show_hardware_info() -> str:
    """Show detailed hardware information using dmidecode."""
    return run_command(["dmidecode", "-t", "system"], allow_nonzero=True)


def check_disk_health(device: str) -> str:
    """Check the SMART health status of a disk.

    device: Block device path, e.g. '/dev/sda'.
    """
    return run_command(["smartctl", "-H", device], allow_nonzero=True)


def show_failed_services() -> str:
    """List all systemd services that have failed."""
    return run_command(["systemctl", "--failed"])


def check_dns_resolution(hostname: str) -> str:
    """Test DNS resolution for a hostname.

    hostname: Domain name to resolve.
    """
    return run_command(["dig", hostname, "+short"])


def test_port_connectivity(host: str, port: int, timeout: int = 5) -> str:
    """Test TCP connectivity to a host and port.

    host: Hostname or IP address to test.
    port: TCP port number to test.
    timeout: Connection timeout in seconds.
    """
    return run_command(["nc", "-zv", "-w", str(timeout), host, str(port)], allow_nonzero=True)


def show_last_logins() -> str:
    """Show a list of the last logged-in users."""
    return run_command(["last", "-n", "20"])


def show_who_is_logged_in() -> str:
    """Show who is currently logged in to the system."""
    return run_command(["who"])


def check_file_system_errors() -> str:
    """Check for file system errors in the system journal."""
    return run_command(["journalctl", "-p", "err", "-n", "50", "--no-pager"])


def show_resource_limits(pid: int = None) -> str:
    """Show resource limits for a process or the current shell.

    pid: Optional process ID. If omitted, shows limits for the current shell.
    """
    if pid:
        return run_command(["cat", f"/proc/{pid}/limits"])
    return run_command(["ulimit", "-a"])


def trace_system_calls(pid: int = None, command: str = None) -> str:
    """Trace system calls made by a process.

    pid: PID of a running process to attach to.
    command: Command to run and trace. Either pid or command must be provided.
    """
    cmd = ["strace", "-c"]
    if pid:
        cmd.extend(["-p", str(pid)])
    elif command:
        cmd.extend(command.split())
    return run_command(cmd, allow_nonzero=True)


def show_environment_variables() -> str:
    """Show all environment variables in the current environment."""
    return run_command(["env"])


def check_network_connectivity(host: str = "8.8.8.8") -> str:
    """Check basic internet connectivity by pinging a host.

    host: Hostname or IP address to ping. Defaults to Google's DNS.
    """
    return run_command(["ping", "-c", "3", "-W", "2", host], allow_nonzero=True)
