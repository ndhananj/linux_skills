# Storage Management

This skill provides a comprehensive set of tools for managing storage devices, partitions, file systems, and advanced storage technologies like RAID and LVM on a Linux system.

## Concepts

- **Block Device:** A device that moves data in blocks, such as a hard drive, SSD, or USB drive.
- **Partition:** A logical division of a block device.
- **File System:** A method for organizing and storing files on a storage device.
- **RAID (Redundant Array of Inexpensive Disks):** A data storage virtualization technology that combines multiple physical disk drive components into one or more logical units for the purposes of data redundancy, performance improvement, or both.
- **LVM (Logical Volume Manager):** A device mapper framework that provides logical volume management for the Linux kernel.
- **iSCSI (Internet Small Computer Systems Interface):** A transport layer protocol that works on top of the Transport Control Protocol (TCP) and allows clients (called initiators) to send SCSI commands to SCSI storage devices (targets) on remote servers.

## Tools

### `list_block_devices`

Lists block devices. This tool is a wrapper for the `lsblk` command.

**Usage:**

```python
def list_block_devices() -> str:
    """
    Lists block devices.

    Returns:
        The output of the lsblk command.
    """
    pass
```

### `fdisk`

Manipulates the disk partition table. This tool is a wrapper for the `fdisk` command.

**Usage:**

```python
def fdisk(device: str, options: str) -> str:
    """
    Manipulates the disk partition table.

    Args:
        device: The device to manipulate (e.g., /dev/sda).
        options: The options to pass to the fdisk command (e.g., 

-l

, 

-c

).

    Returns:
        The output of the fdisk command.
    """
    pass
```

### `make_filesystem`

Creates a Linux file system. This tool is a wrapper for the `mkfs` command.

**Usage:**

```python
def make_filesystem(device: str, type: str = 'ext4') -> str:
    """
    Creates a Linux file system.

    Args:
        device: The device to create the file system on (e.g., /dev/sda1).
        type: The type of file system to create (e.g., 'ext4', 'xfs', 'btrfs').

    Returns:
        The output of the mkfs command.
    """
    pass
```

### `parted`

A partition manipulation program. This tool is a wrapper for the `parted` command.

**Usage:**

```python
def parted(device: str, options: str) -> str:
    """
    A partition manipulation program.

    Args:
        device: The device to manipulate (e.g., /dev/sda).
        options: The options to pass to the parted command (e.g., 'print', 'mklabel gpt').

    Returns:
        The output of the parted command.
    """
    pass
```

### `partprobe`

Informs the OS of partition table changes. This tool is a wrapper for the `partprobe` command.

**Usage:**

```python
def partprobe(device: str = None) -> str:
    """
    Informs the OS of partition table changes.

    Args:
        device: The device to probe (e.g., /dev/sda).

    Returns:
        The output of the partprobe command.
    """
    pass
```

### `resize_filesystem`

Resizes an ext2/ext3/ext4 file system. This tool is a wrapper for the `resize2fs` command.

**Usage:**

```python
def resize_filesystem(device: str) -> str:
    """
    Resizes an ext2/ext3/ext4 file system.

    Args:
        device: The device to resize (e.g., /dev/sda1).

    Returns:
        The output of the resize2fs command.
    """
    pass
```

### `manage_swap`

Enables/disables devices and files for paging and swapping. This tool is a wrapper for the `swapon` and `swapoff` commands.

**Usage:**

```python
def manage_swap(action: str, device: str = None) -> str:
    """
    Enables/disables devices and files for paging and swapping.

    Args:
        action: The action to perform ('on', 'off', '-s' for summary).
        device: The device or file to use for swapping.

    Returns:
        The output of the swapon/swapoff command.
    """
    pass
```

### `configure_raid`

Configures software RAID in Linux. This tool is a wrapper for the `mdadm` command.

**Usage:**

```python
def configure_raid(options: str) -> str:
    """
    Configures software RAID in Linux.

    Args:
        options: The options to pass to the mdadm command (e.g., '--create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1').

    Returns:
        The output of the mdadm command.
    """
    pass
```

### `configure_lvm`

Configures Logical Volume Manager (LVM) in Linux. This tool is a wrapper for LVM commands like `pvcreate`, `vgcreate`, and `lvcreate`.

**Usage:**

```python
def configure_lvm(command: str, options: str) -> str:
    """
    Configures Logical Volume Manager (LVM) in Linux.

    Args:
        command: The LVM command to execute (e.g., 'pvcreate', 'vgcreate', 'lvcreate').
        options: The options to pass to the LVM command (e.g., '/dev/sdb1', '-n myvg /dev/sdb1', '-L 10G -n mylv myvg').

    Returns:
        The output of the LVM command.
    """
    pass
```

### `configure_iscsi`

Configures an iSCSI initiator in Linux. This tool is a wrapper for the `iscsiadm` command.

**Usage:**

```python
def configure_iscsi(options: str) -> str:
    """
    Configures an iSCSI initiator in Linux.

    Args:
        options: The options to pass to the iscsiadm command (e.g., '-m discovery -t st -p 192.168.1.1', '-m node -T iqn.2023-01.com.example:target1 -l').

    Returns:
        The output of the iscsiadm command.
    """
    pass
```
