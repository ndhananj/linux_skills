# File System

This skill covers navigating, manipulating, and maintaining the Linux file system hierarchy. It spans everything from basic directory listing and file copying through to advanced tasks such as file system integrity checking, mounting, and disk usage analysis.

## Concepts

The Linux file system is a single unified hierarchy rooted at `/`. Every file, device, and process is represented as a node in this tree. Understanding the standard directory layout (FHS — Filesystem Hierarchy Standard) is essential: `/etc` holds configuration, `/var` holds variable data such as logs, `/home` contains user home directories, and `/proc` and `/sys` expose kernel state as virtual files.

**Inodes** are the data structures that store file metadata (permissions, owner, timestamps, block pointers). A file name is simply a directory entry that maps a human-readable name to an inode number. Hard links share the same inode; symbolic links are separate files that contain a path.

**Permissions** are expressed as three sets of read/write/execute bits for the owner, group, and others. The `setuid`, `setgid`, and sticky bits provide additional access-control mechanisms.

## Tools Available

| Tool | Description |
|------|-------------|
| `list_directory` | List directory contents with optional long format and hidden files |
| `copy_file` | Copy files or directories |
| `move_file` | Move or rename files and directories |
| `remove_file` | Remove files or directories |
| `create_directory` | Create directories, optionally with parents |
| `touch_file` | Create empty files or update timestamps |
| `find_files` | Search the file system by name, type, or depth |
| `grep_in_file` | Search file contents with regular expressions |
| `sed_transform` | Transform file content with sed scripts |
| `awk_process` | Process structured text with awk programs |
| `create_symlink` | Create symbolic links |
| `disk_usage` | Show disk usage of a path |
| `disk_free` | Show free disk space on all file systems |
| `check_filesystem` | Check and repair a file system with fsck |
| `mount_filesystem` | Mount a device or network share |
| `unmount_filesystem` | Unmount a file system |

## Usage Examples

**Find all log files larger than 100 MB:**
```
find_files(path="/var/log", name="*.log")
```

**Search for error messages in a log file:**
```
grep_in_file(pattern="ERROR", path="/var/log/syslog", ignore_case=True)
```

**Replace a configuration value in place:**
```
sed_transform(script="s/^#MaxSessions.*/MaxSessions 20/", path="/etc/ssh/sshd_config", in_place=True)
```

**Show the 20 largest directories under /var:**
```
awk_process(program="{print $1}", path="/var/log/syslog")
```

## Skill Levels

**Entry** — Navigate directories, copy/move/delete files, understand absolute vs relative paths.

**Beginner** — Use find and grep effectively, understand file permissions and ownership, create symbolic links.

**Intermediate** — Write sed and awk one-liners for text transformation, manage mount points, interpret inode usage.

**Advanced** — Diagnose and repair file system corruption with fsck, tune ext4/xfs parameters, manage ACLs and extended attributes.
