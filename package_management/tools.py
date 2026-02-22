"""
package_management/tools.py — Tools for managing software packages on Linux.

Supports Debian/Ubuntu (apt), RHEL/CentOS (yum/dnf), and Arch (pacman).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


# ---------------------------------------------------------------------------
# Debian / Ubuntu (apt)
# ---------------------------------------------------------------------------

def apt_update() -> str:
    """Update the apt package index."""
    return run_command(["apt-get", "update", "-q"])


def apt_install(package: str, yes: bool = True) -> str:
    """Install a package using apt.

    package: Package name to install, e.g. 'nginx' or 'python3-pip'.
    yes: When True, automatically confirm installation prompts.
    """
    cmd = ["apt-get", "install"]
    if yes:
        cmd.append("-y")
    cmd.append(package)
    return run_command(cmd)


def apt_remove(package: str, purge: bool = False) -> str:
    """Remove a package using apt.

    package: Package name to remove.
    purge: When True, also remove configuration files.
    """
    action = "purge" if purge else "remove"
    return run_command(["apt-get", action, "-y", package])


def apt_upgrade(yes: bool = True) -> str:
    """Upgrade all installed packages to their latest versions.

    yes: When True, automatically confirm upgrade prompts.
    """
    cmd = ["apt-get", "upgrade"]
    if yes:
        cmd.append("-y")
    return run_command(cmd)


def apt_search(query: str) -> str:
    """Search for packages in the apt repository.

    query: Search term.
    """
    return run_command(["apt-cache", "search", query])


def apt_show(package: str) -> str:
    """Show detailed information about a package.

    package: Package name.
    """
    return run_command(["apt-cache", "show", package])


def apt_list_installed() -> str:
    """List all installed packages."""
    return run_command(["dpkg", "-l"])


# ---------------------------------------------------------------------------
# RHEL / CentOS (yum / dnf)
# ---------------------------------------------------------------------------

def yum_install(package: str, yes: bool = True) -> str:
    """Install a package using yum.

    package: Package name to install.
    yes: When True, automatically confirm installation prompts.
    """
    cmd = ["yum", "install"]
    if yes:
        cmd.append("-y")
    cmd.append(package)
    return run_command(cmd)


def yum_remove(package: str) -> str:
    """Remove a package using yum.

    package: Package name to remove.
    """
    return run_command(["yum", "remove", "-y", package])


def yum_update(package: str = None) -> str:
    """Update packages using yum.

    package: Optional package name to update. If omitted, updates all packages.
    """
    cmd = ["yum", "update", "-y"]
    if package:
        cmd.append(package)
    return run_command(cmd)


def yum_search(query: str) -> str:
    """Search for packages in the yum repository.

    query: Search term.
    """
    return run_command(["yum", "search", query])


# ---------------------------------------------------------------------------
# Arch Linux (pacman)
# ---------------------------------------------------------------------------

def pacman_install(package: str) -> str:
    """Install a package using pacman.

    package: Package name to install.
    """
    return run_command(["pacman", "-S", "--noconfirm", package])


def pacman_remove(package: str) -> str:
    """Remove a package using pacman.

    package: Package name to remove.
    """
    return run_command(["pacman", "-R", "--noconfirm", package])


def pacman_update() -> str:
    """Update all installed packages using pacman."""
    return run_command(["pacman", "-Syu", "--noconfirm"])


# ---------------------------------------------------------------------------
# Source compilation
# ---------------------------------------------------------------------------

def compile_from_source(source_dir: str) -> str:
    """Compile and install software from source using the standard configure/make workflow.

    source_dir: Path to the directory containing the configure script and Makefile.
    """
    output = ""
    output += run_command(["./configure"], cwd=source_dir) + "\n"
    output += run_command(["make", f"-j{os.cpu_count() or 1}"], cwd=source_dir) + "\n"
    output += run_command(["make", "install"], cwd=source_dir) + "\n"
    return output


# ---------------------------------------------------------------------------
# Python packages (pip)
# ---------------------------------------------------------------------------

def pip_install(package: str, upgrade: bool = False) -> str:
    """Install a Python package using pip.

    package: Package name and optional version, e.g. 'requests' or 'flask==3.0'.
    upgrade: When True, upgrade the package if already installed.
    """
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    cmd.append(package)
    return run_command(cmd)


def pip_list() -> str:
    """List installed Python packages."""
    return run_command([sys.executable, "-m", "pip", "list"])
