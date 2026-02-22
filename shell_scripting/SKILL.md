# Shell Scripting

This skill provides tools for creating and executing shell scripts, which are used to automate tasks on a Linux system.

## Concepts

- **Shell Script:** A text file containing a sequence of commands for a Unix-like operating system.
- **Shebang (`#!`):** The first line of a script that specifies the interpreter to be used to execute the script.
- **Variables:** Used to store data in a script.
- **Control Structures:** Used to control the flow of execution in a script (e.g., `if`, `for`, `while`).
- **Redirection:** Used to redirect the input and output of commands.

## Tools

### `run_shell_script`

Executes a shell script.

**Usage:**

```python
def run_shell_script(path: str) -> str:
    """
    Executes a shell script.

    Args:
        path: The path to the shell script.

    Returns:
        The output of the shell script.
    """
    pass
```

### `tee`

Reads from standard input and writes to standard output and files. This is useful for viewing the output of a command while also saving it to a file.

**Usage:**

```python
def tee(file: str, append: bool = False) -> None:
    """
    Reads from standard input and writes to standard output and files.

    Args:
        file: The file to write to.
        append: Whether to append to the file instead of overwriting (-a).
    """
    pass
```
