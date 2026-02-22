# Performance Monitoring

This skill provides tools for monitoring the performance of a Linux system, including CPU, memory, and I/O.

## Concepts

- **CPU Load:** A measure of the amount of computational work that a computer system performs.
- **Memory Usage:** The amount of main memory used by the operating system and applications.
- **I/O (Input/Output):** The communication between an information processing system, such as a computer, and the outside world.

## Tools

### `vmstat`

Reports information about processes, memory, paging, block IO, traps, and cpu activity.

**Usage:**

```python
def vmstat(interval: int = 1, count: int = 5) -> str:
    """
    Reports information about processes, memory, paging, block IO, traps, and cpu activity.

    Args:
        interval: The time interval between reports in seconds.
        count: The number of reports to generate.

    Returns:
        The vmstat report.
    """
    pass
```

### `iostat`

Reports Central Processing Unit (CPU) statistics and input/output statistics for devices and partitions.

**Usage:**

```python
def iostat(interval: int = 1, count: int = 5) -> str:
    """
    Reports CPU and I/O statistics.

    Args:
        interval: The time interval between reports in seconds.
        count: The number of reports to generate.

    Returns:
        The iostat report.
    """
    pass
```

### `free`

Displays the amount of free and used memory in the system.

**Usage:**

```python
def free(human_readable: bool = True) -> str:
    """
    Displays the amount of free and used memory in the system.

    Args:
        human_readable: Whether to display the output in human-readable format (-h).

    Returns:
        The memory usage report.
    """
    pass
```
