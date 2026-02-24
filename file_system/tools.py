"""
file_system/tools.py — Tools for navigating and manipulating the Linux file system.

All functions call run_command() from the runtime command_runner module so
that errors, timeouts, and output normalisation are handled consistently.
"""

import sys
import os
import heapq
from typing import List, Tuple

# Allow running tools.py standalone for testing without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def _human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{num_bytes} B"


def list_directory(path: str, long_format: bool = False, show_all: bool = False) -> str:
    """List the contents of a directory.

    path: Absolute or relative path to the directory to list.
    long_format: When True, show permissions, owner, size, and modification time.
    show_all: When True, include hidden files (names starting with a dot).
    """
    cmd = ["ls"]
    if long_format:
        cmd.append("-l")
    if show_all:
        cmd.append("-a")
    cmd.append(path)
    return run_command(cmd)


def copy_file(source: str, destination: str, recursive: bool = False) -> str:
    """Copy a file or directory from source to destination.

    source: Path to the file or directory to copy.
    destination: Path to the copy target.
    recursive: When True, copy directories recursively.
    """
    cmd = ["cp"]
    if recursive:
        cmd.append("-r")
    cmd.extend([source, destination])
    return run_command(cmd)


def move_file(source: str, destination: str) -> str:
    """Move or rename a file or directory.

    source: Path to the file or directory to move.
    destination: New path or name.
    """
    return run_command(["mv", source, destination])


def remove_file(path: str, recursive: bool = False, force: bool = False) -> str:
    """Remove a file or directory.

    path: Path to the file or directory to remove.
    recursive: When True, remove directories and their contents recursively.
    force: When True, ignore nonexistent files and never prompt.
    """
    cmd = ["rm"]
    if recursive:
        cmd.append("-r")
    if force:
        cmd.append("-f")
    cmd.append(path)
    return run_command(cmd)


def create_directory(path: str, create_parents: bool = False) -> str:
    """Create a new directory.

    path: Path of the directory to create.
    create_parents: When True, create parent directories as needed (mkdir -p).
    """
    cmd = ["mkdir"]
    if create_parents:
        cmd.append("-p")
    cmd.append(path)
    return run_command(cmd)


def touch_file(path: str) -> str:
    """Create an empty file, or update the access/modification time of an existing file.

    path: Path to the file.
    """
    return run_command(["touch", path])


def find_files(path: str, name: str = None, file_type: str = None, max_depth: int = None) -> str:
    """Search for files in a directory hierarchy.

    path: Root directory to search from.
    name: Shell glob pattern to match file names, e.g. '*.log'.
    file_type: Filter by type: 'f' (regular file), 'd' (directory), 'l' (symlink).
    max_depth: Maximum directory depth to descend.
    """
    cmd = ["find", path]
    if max_depth is not None:
        cmd.extend(["-maxdepth", str(max_depth)])
    if file_type:
        cmd.extend(["-type", file_type])
    if name:
        cmd.extend(["-name", name])
    return run_command(cmd)


def largest_files(path: str = ".", limit: int = 10, include_hidden: bool = True) -> str:
    """Find the largest regular files under a directory.

    path: Root directory to scan recursively.
    limit: Number of files to return.
    include_hidden: When False, skip hidden files and directories.
    """
    try:
        n = max(1, int(limit))
    except Exception:
        n = 10

    top: List[Tuple[int, str]] = []
    skipped = 0

    def _onerror(_err):
        nonlocal skipped
        skipped += 1

    for root, dirs, files in os.walk(path, topdown=True, onerror=_onerror, followlinks=False):
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            files = [f for f in files if not f.startswith(".")]

        for fname in files:
            fp = os.path.join(root, fname)
            try:
                st = os.stat(fp, follow_symlinks=False)
            except OSError:
                skipped += 1
                continue
            if not os.path.isfile(fp):
                continue
            item = (int(st.st_size), fp)
            if len(top) < n:
                heapq.heappush(top, item)
            else:
                heapq.heappushpop(top, item)

    top_sorted = sorted(top, key=lambda x: (-x[0], x[1]))
    lines = []
    for idx, (size, fp) in enumerate(top_sorted, start=1):
        lines.append(f"{idx:2d}. {_human_size(size):>10}  {fp}")

    if not lines:
        lines = ["No files found."]
    if skipped:
        lines.append(f"\nSkipped entries due to errors: {skipped}")
    return "\n".join(lines)


def grep_in_file(pattern: str, path: str, ignore_case: bool = False, invert: bool = False, recursive: bool = False) -> str:
    """Search for a pattern in a file or directory.

    pattern: Regular expression or fixed string to search for.
    path: File or directory to search.
    ignore_case: When True, perform case-insensitive matching.
    invert: When True, print lines that do NOT match.
    recursive: When True, search all files under path recursively.
    """
    cmd = ["grep"]
    if ignore_case:
        cmd.append("-i")
    if invert:
        cmd.append("-v")
    if recursive:
        cmd.append("-r")
    cmd.extend([pattern, path])
    return run_command(cmd, allow_nonzero=True)


def sed_transform(script: str, path: str, in_place: bool = False) -> str:
    """Transform text in a file using a sed script.

    script: A sed expression, e.g. 's/old/new/g'.
    path: File to process.
    in_place: When True, edit the file in place (sed -i).
    """
    cmd = ["sed"]
    if in_place:
        cmd.append("-i")
    cmd.extend([script, path])
    return run_command(cmd)


def awk_process(program: str, path: str) -> str:
    """Process a text file with an awk program.

    program: An awk program string, e.g. '{print $1}'.
    path: File to process.
    """
    return run_command(["awk", program, path])


def create_symlink(target: str, link_name: str) -> str:
    """Create a symbolic link pointing to target.

    target: The file or directory the link should point to.
    link_name: The path of the new symbolic link.
    """
    return run_command(["ln", "-s", target, link_name])


def disk_usage(path: str, human_readable: bool = True) -> str:
    """Show the disk usage of a file or directory.

    path: Path to measure.
    human_readable: When True, print sizes in human-readable format (K, M, G).
    """
    cmd = ["du", "-s"]
    if human_readable:
        cmd.append("-h")
    cmd.append(path)
    return run_command(cmd)


def disk_free(human_readable: bool = True) -> str:
    """Report file system disk space usage.

    human_readable: When True, print sizes in human-readable format.
    """
    cmd = ["df"]
    if human_readable:
        cmd.append("-h")
    return run_command(cmd)


def check_filesystem(device: str, auto_repair: bool = False) -> str:
    """Check and optionally repair a Linux file system.

    device: Block device to check, e.g. '/dev/sda1'.
    auto_repair: When True, automatically repair errors without prompting.
    """
    cmd = ["fsck"]
    if auto_repair:
        cmd.append("-y")
    cmd.append(device)
    return run_command(cmd)


def mount_filesystem(device: str, mount_point: str, options: str = None) -> str:
    """Mount a file system.

    device: Block device or network share to mount.
    mount_point: Directory to mount the file system at.
    options: Comma-separated mount options, e.g. 'ro,noexec'.
    """
    cmd = ["mount"]
    if options:
        cmd.extend(["-o", options])
    cmd.extend([device, mount_point])
    return run_command(cmd)


def unmount_filesystem(mount_point: str, force: bool = False) -> str:
    """Unmount a file system.

    mount_point: Directory or device to unmount.
    force: When True, force unmount even if busy.
    """
    cmd = ["umount"]
    if force:
        cmd.append("-f")
    cmd.append(mount_point)
    return run_command(cmd)
