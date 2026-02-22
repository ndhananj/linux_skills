"""
user_and_group/tools.py — Tools for managing Linux users, groups, and permissions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


def add_user(username: str, home_dir: str = None, shell: str = None, create_home: bool = True) -> str:
    """Create a new user account.

    username: The login name for the new user.
    home_dir: Path to the user's home directory. Defaults to /home/<username>.
    shell: Path to the user's login shell, e.g. '/bin/bash'.
    create_home: When True, create the user's home directory.
    """
    cmd = ["useradd"]
    if create_home:
        cmd.append("-m")
    if home_dir:
        cmd.extend(["-d", home_dir])
    if shell:
        cmd.extend(["-s", shell])
    cmd.append(username)
    return run_command(cmd)


def delete_user(username: str, remove_home: bool = False) -> str:
    """Delete a user account.

    username: The login name of the user to delete.
    remove_home: When True, also remove the user's home directory and mail spool.
    """
    cmd = ["userdel"]
    if remove_home:
        cmd.append("-r")
    cmd.append(username)
    return run_command(cmd)


def modify_user(username: str, new_name: str = None, new_shell: str = None, lock: bool = False, unlock: bool = False) -> str:
    """Modify a user account.

    username: The login name of the user to modify.
    new_name: New login name for the user.
    new_shell: New login shell for the user.
    lock: When True, lock the user's password (disable login).
    unlock: When True, unlock the user's password.
    """
    cmd = ["usermod"]
    if new_name:
        cmd.extend(["-l", new_name])
    if new_shell:
        cmd.extend(["-s", new_shell])
    if lock:
        cmd.append("-L")
    if unlock:
        cmd.append("-U")
    cmd.append(username)
    return run_command(cmd)


def set_password(username: str) -> str:
    """Set or change a user's password interactively.

    username: The login name of the user whose password to change.
    """
    return run_command(["passwd", username])


def add_group(groupname: str) -> str:
    """Create a new group.

    groupname: The name of the new group.
    """
    return run_command(["groupadd", groupname])


def delete_group(groupname: str) -> str:
    """Delete a group.

    groupname: The name of the group to delete.
    """
    return run_command(["groupdel", groupname])


def add_user_to_group(username: str, groupname: str) -> str:
    """Add a user to a supplementary group.

    username: The login name of the user.
    groupname: The name of the group to add the user to.
    """
    return run_command(["usermod", "-aG", groupname, username])


def list_groups(username: str = None) -> str:
    """List groups. If a username is given, list the groups that user belongs to.

    username: Optional login name to query group membership for.
    """
    if username:
        return run_command(["groups", username])
    return run_command(["cat", "/etc/group"])


def change_owner(path: str, owner: str, group: str = None, recursive: bool = False) -> str:
    """Change the owner (and optionally group) of a file or directory.

    path: Path to the file or directory.
    owner: New owner username.
    group: New group name. If omitted, only the owner is changed.
    recursive: When True, apply changes recursively to all contents.
    """
    cmd = ["chown"]
    if recursive:
        cmd.append("-R")
    spec = f"{owner}:{group}" if group else owner
    cmd.extend([spec, path])
    return run_command(cmd)


def change_permissions(path: str, mode: str, recursive: bool = False) -> str:
    """Change the permissions of a file or directory.

    path: Path to the file or directory.
    mode: Permission mode in symbolic (e.g. 'u+x', 'go-w') or octal (e.g. '755') notation.
    recursive: When True, apply changes recursively to all contents.
    """
    cmd = ["chmod"]
    if recursive:
        cmd.append("-R")
    cmd.extend([mode, path])
    return run_command(cmd)


def show_file_permissions(path: str) -> str:
    """Show the permissions, owner, and group of a file or directory.

    path: Path to the file or directory.
    """
    return run_command(["stat", path])


def set_umask(mask: str) -> str:
    """Display or set the file mode creation mask.

    mask: Octal mask value, e.g. '022'. If empty, the current mask is displayed.
    """
    if mask:
        return run_command(["bash", "-c", f"umask {mask}"])
    return run_command(["bash", "-c", "umask"])


def list_logged_in_users() -> str:
    """List all currently logged-in users."""
    return run_command(["who"])


def show_user_info(username: str) -> str:
    """Display information about a user account.

    username: The login name of the user to query.
    """
    return run_command(["id", username])
