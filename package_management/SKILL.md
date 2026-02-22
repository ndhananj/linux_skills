# Package Management

This skill provides tools for managing software packages on a Linux system, including installation, removal, and updates. It covers the most common package managers for different Linux distributions.

## Concepts

- **Package:** A collection of files that make up a software application.
- **Package Manager:** A tool that automates the process of installing, upgrading, configuring, and removing software packages.
- **Repository:** A central location where software packages are stored and can be retrieved by a package manager.

## Tools

### `yum`

Yellowdog Updater, Modified (YUM) is a command-line package-management utility for RPM-based Linux distributions like CentOS and RHEL. This tool is a wrapper for the `yum` command.

**Usage:**

```python
def yum(command: str, package: str = None) -> str:
    """
    Manages packages on RPM-based systems.

    Args:
        command: The command to execute (e.g., 'install', 'remove', 'update', 'search').
        package: The name of the package.

    Returns:
        The output of the yum command.
    """
    pass
```

### `pacman`

A package manager for Arch Linux and its derivatives. This tool is a wrapper for the `pacman` command.

**Usage:**

```python
def pacman(options: str) -> str:
    """
    Manages packages on Arch-based systems.

    Args:
        options: The options to pass to the pacman command (e.g., '-Syu', '-S package_name', '-R package_name').

    Returns:
        The output of the pacman command.
    """
    pass
```

### `apt`

Advanced Package Tool (APT) is a command-line package-management utility for Debian-based Linux distributions like Ubuntu. This tool is a wrapper for the `apt` command.

**Usage:**

```python
def apt(command: str, package: str = None) -> str:
    """
    Manages packages on Debian-based systems.

    Args:
        command: The command to execute (e.g., 'install', 'remove', 'update', 'search').
        package: The name of the package.

    Returns:
        The output of the apt command.
    """
    pass
```

### `compile_from_source`

Compiles and installs software from source code. This is a more advanced method of software installation.

**Usage:**

```python
def compile_from_source(path: str) -> str:
    """
    Compiles and installs software from source code.

    Args:
        path: The path to the source code directory.

    Returns:
        The output of the compilation and installation process (configure, make, make install).
    """
    pass
```
