# Text Processing

This skill provides a collection of powerful tools for processing and manipulating text data on a Linux system.

## Concepts

- **Regular Expression (Regex):** A sequence of characters that define a search pattern.
- **Standard Input (stdin):** The default source of input for a command.
- **Standard Output (stdout):** The default destination for output from a command.
- **Standard Error (stderr):** The default destination for error messages from a command.
- **Pipe (|):** A mechanism for passing the output of one command as the input to another command.

## Tools

### `sort`

Sorts lines of text files.

**Usage:**

```python
def sort(file: str, reverse: bool = False, numeric: bool = False) -> str:
    """
    Sorts lines of text files.

    Args:
        file: The path to the file to sort.
        reverse: Whether to sort in reverse order (-r).
        numeric: Whether to sort numerically (-n).

    Returns:
        The sorted output.
    """
    pass
```

### `uniq`

Reports or omits repeated lines.

**Usage:**

```python
def uniq(file: str, count: bool = False) -> str:
    """
    Reports or omits repeated lines.

    Args:
        file: The path to the file to process.
        count: Whether to prefix lines by the number of occurrences (-c).

    Returns:
        The processed output.
    """
    pass
```

### `cut`

Removes sections from each line of files.

**Usage:**

```python
def cut(file: str, delimiter: str, fields: str) -> str:
    """
    Removes sections from each line of files.

    Args:
        file: The path to the file to process.
        delimiter: The delimiter to use (-d).
        fields: The fields to select (-f).

    Returns:
        The processed output.
    """
    pass
```

### `tr`

Translates or deletes characters.

**Usage:**

```python
def tr(set1: str, set2: str) -> str:
    """
    Translates or deletes characters.

    Args:
        set1: The set of characters to translate from.
        set2: The set of characters to translate to.

    Returns:
        The translated output.
    """
    pass
```

### `wc`

Prints newline, word, and byte counts for each file.

**Usage:**

```python
def wc(file: str) -> str:
    """
    Prints newline, word, and byte counts for each file.

    Args:
        file: The path to the file to process.

    Returns:
        The word count output.
    """
    pass
```
