"""
version_control/tools.py — Tools for managing Git repositories.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def git_init(path: str = ".") -> str:
    """Initialise a new Git repository.

    path: Directory to initialise. Defaults to the current directory.
    """
    return run_command(["git", "init", path])


def git_clone(url: str, destination: str = None, depth: int = None) -> str:
    """Clone a remote Git repository.

    url: URL of the repository to clone.
    destination: Local directory name. Defaults to the repository name.
    depth: If set, create a shallow clone with this many commits.
    """
    cmd = ["git", "clone"]
    if depth:
        cmd.extend(["--depth", str(depth)])
    cmd.append(url)
    if destination:
        cmd.append(destination)
    return run_command(cmd)


def git_status(path: str = ".") -> str:
    """Show the working tree status of a Git repository.

    path: Path to the repository. Defaults to the current directory.
    """
    return run_command(["git", "-C", path, "status"])


def git_add(path: str = ".", files: str = ".") -> str:
    """Stage files for the next commit.

    path: Path to the repository.
    files: Space-separated list of files to stage, or '.' for all changes.
    """
    return run_command(["git", "-C", path, "add"] + files.split())


def git_commit(path: str = ".", message: str = "Update") -> str:
    """Record staged changes to the repository.

    path: Path to the repository.
    message: Commit message.
    """
    return run_command(["git", "-C", path, "commit", "-m", message])


def git_push(path: str = ".", remote: str = "origin", branch: str = "main") -> str:
    """Push commits to a remote repository.

    path: Path to the repository.
    remote: Name of the remote, e.g. 'origin'.
    branch: Branch to push.
    """
    return run_command(["git", "-C", path, "push", remote, branch])


def git_pull(path: str = ".", remote: str = "origin", branch: str = "main") -> str:
    """Fetch and integrate changes from a remote repository.

    path: Path to the repository.
    remote: Name of the remote.
    branch: Branch to pull.
    """
    return run_command(["git", "-C", path, "pull", remote, branch])


def git_log(path: str = ".", lines: int = 10, oneline: bool = True) -> str:
    """Show the commit history.

    path: Path to the repository.
    lines: Number of recent commits to show.
    oneline: When True, show each commit on a single line.
    """
    cmd = ["git", "-C", path, "log", f"-{lines}"]
    if oneline:
        cmd.append("--oneline")
    return run_command(cmd)


def git_diff(path: str = ".", staged: bool = False) -> str:
    """Show changes between the working tree and the index, or between commits.

    path: Path to the repository.
    staged: When True, show staged (indexed) changes rather than unstaged.
    """
    cmd = ["git", "-C", path, "diff"]
    if staged:
        cmd.append("--staged")
    return run_command(cmd)


def git_branch(path: str = ".", create: str = None, delete: str = None) -> str:
    """List, create, or delete branches.

    path: Path to the repository.
    create: Name of a new branch to create.
    delete: Name of a branch to delete.
    """
    cmd = ["git", "-C", path, "branch"]
    if create:
        cmd.append(create)
    elif delete:
        cmd.extend(["-d", delete])
    return run_command(cmd)


def git_checkout(path: str = ".", branch: str = None, create: bool = False) -> str:
    """Switch branches or restore working tree files.

    path: Path to the repository.
    branch: Branch name to check out.
    create: When True, create the branch if it does not exist (-b flag).
    """
    cmd = ["git", "-C", path, "checkout"]
    if create:
        cmd.append("-b")
    if branch:
        cmd.append(branch)
    return run_command(cmd)


def git_merge(path: str = ".", branch: str = None) -> str:
    """Merge a branch into the current branch.

    path: Path to the repository.
    branch: Name of the branch to merge.
    """
    return run_command(["git", "-C", path, "merge", branch])


def git_stash(path: str = ".", action: str = "push") -> str:
    """Stash or restore uncommitted changes.

    path: Path to the repository.
    action: 'push' to stash changes, 'pop' to restore the most recent stash.
    """
    return run_command(["git", "-C", path, "stash", action])


def git_tag(path: str = ".", name: str = None, message: str = None) -> str:
    """List or create tags.

    path: Path to the repository.
    name: Tag name to create. If omitted, lists all tags.
    message: Annotated tag message. If omitted, creates a lightweight tag.
    """
    cmd = ["git", "-C", path, "tag"]
    if name:
        if message:
            cmd.extend(["-a", name, "-m", message])
        else:
            cmd.append(name)
    return run_command(cmd)


def git_remote(path: str = ".", action: str = "show", name: str = "origin", url: str = None) -> str:
    """Manage remote repository connections.

    path: Path to the repository.
    action: 'show' to list remotes, 'add' to add a new remote, 'remove' to delete one.
    name: Remote name.
    url: Remote URL (required for 'add' action).
    """
    cmd = ["git", "-C", path, "remote"]
    if action == "show":
        cmd.extend(["show", name])
    elif action == "add" and url:
        cmd.extend(["add", name, url])
    elif action == "remove":
        cmd.extend(["remove", name])
    return run_command(cmd)
