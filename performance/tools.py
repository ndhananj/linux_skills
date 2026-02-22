"""
performance/tools.py — Tools for monitoring Linux system performance.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def show_memory_usage(human_readable: bool = True) -> str:
    """Show the amount of free and used memory in the system.

    human_readable: When True, print sizes in human-readable format (K, M, G).
    """
    cmd = ["free"]
    if human_readable:
        cmd.append("-h")
    return run_command(cmd)


def show_cpu_info() -> str:
    """Show CPU information including model, cores, and clock speed."""
    return run_command(["lscpu"])


def show_load_average() -> str:
    """Show the system load average for the past 1, 5, and 15 minutes."""
    return run_command(["uptime"])


def show_disk_io(interval: int = 1, count: int = 3) -> str:
    """Report CPU and I/O statistics.

    interval: Seconds between each report.
    count: Number of reports to generate.
    """
    return run_command(["iostat", "-x", str(interval), str(count)])


def show_virtual_memory_stats(interval: int = 1, count: int = 3) -> str:
    """Report virtual memory statistics including processes, memory, paging, and CPU.

    interval: Seconds between each report.
    count: Number of reports to generate.
    """
    return run_command(["vmstat", str(interval), str(count)])


def show_top_processes_by_cpu(count: int = 10) -> str:
    """Show the top N processes by CPU usage.

    count: Number of processes to show.
    """
    return run_command(["ps", "aux", "--sort=-%cpu", "--no-headers", "-o", "pid,pcpu,pmem,comm"])


def show_top_processes_by_memory(count: int = 10) -> str:
    """Show the top N processes by memory usage.

    count: Number of processes to show.
    """
    return run_command(["ps", "aux", "--sort=-%mem", "--no-headers", "-o", "pid,pcpu,pmem,comm"])


def show_network_stats(interface: str = None) -> str:
    """Show network interface statistics.

    interface: Optional interface name to show. If omitted, shows all interfaces.
    """
    cmd = ["ip", "-s", "link", "show"]
    if interface:
        cmd.append(interface)
    return run_command(cmd)


def show_open_files(pid: int = None) -> str:
    """Show open files and network connections.

    pid: Optional process ID to filter by. If omitted, shows all open files.
    """
    cmd = ["lsof"]
    if pid:
        cmd.extend(["-p", str(pid)])
    return run_command(cmd)


def show_hardware_info() -> str:
    """Show a summary of hardware information."""
    return run_command(["lshw", "-short"], allow_nonzero=True)


def benchmark_disk(path: str = "/tmp", size_mb: int = 100) -> str:
    """Run a simple disk write benchmark using dd.

    path: Directory to write the test file to.
    size_mb: Size of the test file in megabytes.
    """
    test_file = os.path.join(path, "disk_benchmark_test")
    result = run_command([
        "dd", "if=/dev/zero", f"of={test_file}",
        "bs=1M", f"count={size_mb}", "oflag=dsync",
    ])
    run_command(["rm", "-f", test_file])
    return result


def show_system_uptime() -> str:
    """Show how long the system has been running."""
    return run_command(["uptime", "-p"])


def show_interrupts() -> str:
    """Show CPU interrupt statistics."""
    return run_command(["cat", "/proc/interrupts"])
