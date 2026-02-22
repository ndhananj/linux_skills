# Process and Service Management

This skill provides tools for managing processes, services, and jobs on a Linux system. It covers process monitoring, signaling, and service management using both traditional init systems and systemd.

## Concepts

- **Process:** An instance of a running program.
- **Service (Daemon):** A process that runs in the background to provide a service.
- **Job:** A command or a set of commands that can be managed by the shell.
- **PID (Process ID):** A unique identifier for a process.
- **Signal:** A notification sent to a process to interrupt it and handle events.
- **systemd:** A system and service manager for Linux operating systems.
- **Init:** The first process started during booting of the computer system.

## Tools

### `ps`

Reports a snapshot of the current processes. This tool is a wrapper for the `ps` command.

**Usage:**

```python
def ps(options: str = 'aux') -> str:
    """
    Reports a snapshot of the current processes.

    Args:
        options: The options to pass to the ps command (e.g., 'aux', '-ef').

    Returns:
        The output of the ps command.
    """
    pass
```

### `top`

Displays Linux processes in real-time. This tool is a wrapper for the `top` command.

**Usage:**

```python
def top(options: str = '-b -n 1') -> str:
    """
    Displays Linux processes.

    Args:
        options: The options to pass to the top command. '-b -n 1' runs it in batch mode for a single iteration.

    Returns:
        The output of the top command.
    """
    pass
```

### `kill`

Sends a signal to a process. This tool is a wrapper for the `kill` command.

**Usage:**

```python
def kill(pid: int, signal: int = 15) -> None:
    """
    Sends a signal to a process.

    Args:
        pid: The process ID.
        signal: The signal to send (e.g., 9 for SIGKILL, 15 for SIGTERM).
    """
    pass
```

### `service`

Runs a System V init script. This is used on older Linux distributions that do not use systemd.

**Usage:**

```python
def service(name: str, action: str) -> str:
    """
    Runs a System V init script.

    Args:
        name: The name of the service.
        action: The action to perform (e.g., 'start', 'stop', 'status', 'restart').

    Returns:
        The output of the service command.
    """
    pass
```

### `bg`

Resumes a suspended job in the background.

**Usage:**

```python
def bg(job_id: int) -> None:
    """
    Resumes a suspended job in the background.

    Args:
        job_id: The job ID (e.g., 1, 2).
    """
    pass
```

### `fg`

Resumes a job in the foreground.

**Usage:**

```python
def fg(job_id: int) -> None:
    """
    Resumes a job in the foreground.

    Args:
        job_id: The job ID (e.g., 1, 2).
    """
    pass
```

### `jobs`

Lists the active jobs.

**Usage:**

```python
def jobs() -> str:
    """
    Lists the active jobs.

    Returns:
        The output of the jobs command.
    """
    pass
```

### `systemctl`

Controls the systemd system and service manager. This is the standard on modern Linux distributions.

**Usage:**

```python
def systemctl(action: str, service: str = None) -> str:
    """
    Controls the systemd system and service manager.

    Args:
        action: The action to perform (e.g., 'start', 'stop', 'status', 'enable', 'disable').
        service: The name of the service (e.g., 'sshd.service').

    Returns:
        The output of the systemctl command.
    """
    pass
```

### `journalctl`

Queries the systemd journal, which is a centralized logging solution.

**Usage:**

```python
def journalctl(options: str = None) -> str:
    """
    Queries the systemd journal.

    Args:
        options: The options to pass to the journalctl command (e.g., '-u sshd.service', '--since "yesterday"').

    Returns:
        The output of the journalctl command.
    """
    pass
```
