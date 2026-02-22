"""
text_processing/tools.py — Tools for processing and transforming text on Linux.
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def sort_lines(path: str, reverse: bool = False, numeric: bool = False, unique: bool = False) -> str:
    """Sort lines of a text file.

    path: Path to the file to sort.
    reverse: When True, sort in descending order.
    numeric: When True, sort numerically rather than lexicographically.
    unique: When True, remove duplicate lines from the output.
    """
    cmd = ["sort"]
    if reverse:
        cmd.append("-r")
    if numeric:
        cmd.append("-n")
    if unique:
        cmd.append("-u")
    cmd.append(path)
    return run_command(cmd)


def count_unique_lines(path: str, show_count: bool = True) -> str:
    """Report or omit repeated lines in a sorted file.

    path: Path to the (sorted) file.
    show_count: When True, prefix each line with the number of occurrences.
    """
    cmd = ["uniq"]
    if show_count:
        cmd.append("-c")
    cmd.append(path)
    return run_command(cmd)


def cut_columns(path: str, delimiter: str, fields: str) -> str:
    """Extract specific columns from a delimited text file.

    path: Path to the file.
    delimiter: Column delimiter character, e.g. ':' or ','.
    fields: Field numbers to extract, e.g. '1,3' or '1-3'.
    """
    return run_command(["cut", "-d", delimiter, "-f", fields, path])


def count_lines_words_bytes(path: str) -> str:
    """Count lines, words, and bytes in a file.

    path: Path to the file.
    """
    return run_command(["wc", path])


def translate_characters(input_text: str, from_chars: str, to_chars: str) -> str:
    """Translate or delete characters in a string.

    input_text: The text to transform.
    from_chars: Characters to replace (source set).
    to_chars: Replacement characters (destination set).
    """
    result = subprocess.run(
        ["tr", from_chars, to_chars],
        input=input_text,
        capture_output=True,
        text=True,
    )
    return result.stdout


def replace_in_file(pattern: str, replacement: str, path: str, in_place: bool = False) -> str:
    """Replace all occurrences of a pattern in a file using sed.

    pattern: Regular expression pattern to replace.
    replacement: Replacement string.
    path: Path to the file.
    in_place: When True, edit the file in place.
    """
    script = f"s/{pattern}/{replacement}/g"
    cmd = ["sed"]
    if in_place:
        cmd.append("-i")
    cmd.extend([script, path])
    return run_command(cmd)


def awk_extract(program: str, path: str) -> str:
    """Process a text file with an awk program.

    program: An awk program string, e.g. '{print $2}' or '/pattern/ {print $0}'.
    path: Path to the file to process.
    """
    return run_command(["awk", program, path])


def join_files(file1: str, file2: str, field: int = 1) -> str:
    """Join two sorted files on a common field.

    file1: Path to the first sorted file.
    file2: Path to the second sorted file.
    field: Field number to join on (1-indexed).
    """
    return run_command(["join", "-1", str(field), "-2", str(field), file1, file2])


def diff_files(file1: str, file2: str, unified: bool = True) -> str:
    """Show the differences between two files.

    file1: Path to the first file.
    file2: Path to the second file.
    unified: When True, use unified diff format (easier to read).
    """
    cmd = ["diff"]
    if unified:
        cmd.append("-u")
    cmd.extend([file1, file2])
    return run_command(cmd, allow_nonzero=True)


def head_lines(path: str, lines: int = 10) -> str:
    """Show the first N lines of a file.

    path: Path to the file.
    lines: Number of lines to show.
    """
    return run_command(["head", "-n", str(lines), path])


def tail_lines(path: str, lines: int = 10) -> str:
    """Show the last N lines of a file.

    path: Path to the file.
    lines: Number of lines to show.
    """
    return run_command(["tail", "-n", str(lines), path])


def concatenate_files(paths: str) -> str:
    """Concatenate and display the contents of one or more files.

    paths: Space-separated list of file paths to concatenate.
    """
    return run_command(["cat"] + paths.split())
