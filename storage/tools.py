"""
storage/tools.py — Tools for managing Linux storage devices, partitions, and file systems.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def list_block_devices(json_output: bool = False) -> str:
    """List all block devices (disks and partitions).

    json_output: When True, return output in JSON format.
    """
    cmd = ["lsblk"]
    if json_output:
        cmd.append("-J")
    return run_command(cmd)


def show_disk_usage(human_readable: bool = True) -> str:
    """Show disk space usage for all mounted file systems.

    human_readable: When True, print sizes in human-readable format.
    """
    cmd = ["df"]
    if human_readable:
        cmd.append("-h")
    return run_command(cmd)


def show_partition_table(device: str) -> str:
    """Show the partition table of a disk.

    device: Block device path, e.g. '/dev/sda'.
    """
    return run_command(["parted", device, "print"])


def create_partition(device: str, partition_type: str, start: str, end: str) -> str:
    """Create a new partition on a disk.

    device: Block device path, e.g. '/dev/sda'.
    partition_type: Partition type: 'primary', 'extended', or 'logical'.
    start: Start position, e.g. '1MiB' or '0%'.
    end: End position, e.g. '10GiB' or '100%'.
    """
    return run_command(["parted", "-s", device, "mkpart", partition_type, start, end])


def format_partition(device: str, filesystem: str = "ext4", label: str = None) -> str:
    """Format a partition with a file system.

    device: Partition device path, e.g. '/dev/sda1'.
    filesystem: File system type: 'ext4', 'xfs', 'btrfs', 'vfat', 'ntfs', etc.
    label: Optional volume label.
    """
    cmd = [f"mkfs.{filesystem}"]
    if label:
        if filesystem in ("ext2", "ext3", "ext4"):
            cmd.extend(["-L", label])
        elif filesystem == "xfs":
            cmd.extend(["-L", label])
    cmd.append(device)
    return run_command(cmd)


def mount_device(device: str, mount_point: str, filesystem: str = None, options: str = None) -> str:
    """Mount a block device or partition.

    device: Device path or UUID to mount.
    mount_point: Directory to mount the device at.
    filesystem: Optional file system type hint.
    options: Comma-separated mount options, e.g. 'ro,noexec'.
    """
    cmd = ["mount"]
    if filesystem:
        cmd.extend(["-t", filesystem])
    if options:
        cmd.extend(["-o", options])
    cmd.extend([device, mount_point])
    return run_command(cmd)


def unmount_device(mount_point: str, force: bool = False, lazy: bool = False) -> str:
    """Unmount a file system.

    mount_point: Mount point or device to unmount.
    force: When True, force unmount even if busy.
    lazy: When True, detach the file system immediately and clean up later.
    """
    cmd = ["umount"]
    if force:
        cmd.append("-f")
    if lazy:
        cmd.append("-l")
    cmd.append(mount_point)
    return run_command(cmd)


def show_mounts() -> str:
    """Show all currently mounted file systems."""
    return run_command(["findmnt"])


def check_filesystem(device: str, auto_repair: bool = False) -> str:
    """Check and optionally repair a file system.

    device: Partition device path, e.g. '/dev/sda1'.
    auto_repair: When True, automatically repair errors without prompting.
    """
    cmd = ["fsck"]
    if auto_repair:
        cmd.append("-y")
    cmd.append(device)
    return run_command(cmd)


def resize_filesystem(device: str) -> str:
    """Resize an ext2/ext3/ext4 file system to fill its partition.

    device: Partition device path, e.g. '/dev/sda1'.
    """
    return run_command(["resize2fs", device])


def enable_swap(device: str) -> str:
    """Enable a swap partition or file.

    device: Swap partition or file path.
    """
    return run_command(["swapon", device])


def disable_swap(device: str) -> str:
    """Disable a swap partition or file.

    device: Swap partition or file path.
    """
    return run_command(["swapoff", device])


def show_swap_usage() -> str:
    """Show swap partition usage."""
    return run_command(["swapon", "--show"])


def create_swap_file(path: str, size_mb: int = 1024) -> str:
    """Create and enable a swap file.

    path: Path for the new swap file, e.g. '/swapfile'.
    size_mb: Size of the swap file in megabytes.
    """
    output = ""
    output += run_command(["dd", "if=/dev/zero", f"of={path}", "bs=1M", f"count={size_mb}"])
    output += run_command(["chmod", "600", path])
    output += run_command(["mkswap", path])
    output += run_command(["swapon", path])
    return output


def configure_lvm(command: str, options: str) -> str:
    """Run an LVM management command.

    command: LVM command: 'pvcreate', 'vgcreate', 'lvcreate', 'pvdisplay', 'vgdisplay', 'lvdisplay', etc.
    options: Command arguments as a space-separated string.
    """
    return run_command([command] + options.split())


def configure_raid(options: str) -> str:
    """Run an mdadm software RAID management command.

    options: mdadm arguments as a space-separated string, e.g. '--create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc'.
    """
    return run_command(["mdadm"] + options.split())
