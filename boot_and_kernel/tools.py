"""
boot_and_kernel/tools.py — Tools for managing the Linux boot process and kernel.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command
from os_runner import write_text


def show_kernel_version() -> str:
    """Show the currently running kernel version."""
    return run_command(["uname", "-r"])


def list_installed_kernels() -> str:
    """List all installed kernel packages."""
    return run_command(["ls", "/boot/vmlinuz*"], allow_nonzero=True)


def show_kernel_parameters() -> str:
    """Show the kernel boot parameters for the currently running kernel."""
    return run_command(["cat", "/proc/cmdline"])


def get_kernel_sysctl(parameter: str = None) -> str:
    """Show kernel runtime parameters.

    parameter: Optional parameter name, e.g. 'net.ipv4.ip_forward'. If omitted, shows all.
    """
    cmd = ["sysctl"]
    if parameter:
        cmd.append(parameter)
    else:
        cmd.append("-a")
    return run_command(cmd, allow_nonzero=True)


def set_kernel_sysctl(parameter: str, value: str) -> str:
    """Set a kernel runtime parameter.

    parameter: Parameter name, e.g. 'net.ipv4.ip_forward'.
    value: Value to set, e.g. '1'.
    """
    return run_command(["sysctl", "-w", f"{parameter}={value}"])


def persist_kernel_sysctl(parameter: str, value: str) -> str:
    """Persist a kernel parameter across reboots by writing to /etc/sysctl.conf.

    parameter: Parameter name, e.g. 'net.ipv4.ip_forward'.
    value: Value to set, e.g. '1'.
    """
    entry = f"{parameter} = {value}\n"
    write_text("/etc/sysctl.conf", entry, mode="a")
    return run_command(["sysctl", "-p"])


def update_grub() -> str:
    """Regenerate the GRUB bootloader configuration."""
    return run_command(["update-grub"], allow_nonzero=True)


def install_grub(device: str) -> str:
    """Install the GRUB bootloader to a disk.

    device: Disk device path, e.g. '/dev/sda'.
    """
    return run_command(["grub-install", device])


def update_initramfs(kernel_version: str = None) -> str:
    """Update the initial RAM disk (initramfs) for a kernel.

    kernel_version: Kernel version string. If omitted, updates for the running kernel.
    """
    cmd = ["update-initramfs", "-u"]
    if kernel_version:
        cmd.extend(["-k", kernel_version])
    return run_command(cmd, allow_nonzero=True)


def list_kernel_modules() -> str:
    """List all currently loaded kernel modules."""
    return run_command(["lsmod"])


def load_kernel_module(module: str, options: str = None) -> str:
    """Load a kernel module.

    module: Module name, e.g. 'nf_conntrack'.
    options: Optional module parameters as a space-separated string.
    """
    cmd = ["modprobe", module]
    if options:
        cmd.extend(options.split())
    return run_command(cmd)


def unload_kernel_module(module: str) -> str:
    """Unload a kernel module.

    module: Module name to unload.
    """
    return run_command(["modprobe", "-r", module])


def show_module_info(module: str) -> str:
    """Show information about a kernel module.

    module: Module name to inspect.
    """
    return run_command(["modinfo", module])


def show_boot_log() -> str:
    """Show the boot log from the systemd journal."""
    return run_command(["journalctl", "-b", "-n", "100", "--no-pager"])


def reboot_system() -> str:
    """Reboot the system immediately."""
    return run_command(["systemctl", "reboot"])


def shutdown_system(delay: int = 0) -> str:
    """Shut down the system.

    delay: Minutes to wait before shutting down. 0 means immediately.
    """
    return run_command(["shutdown", "-h", f"+{delay}"])
