# User and Group Management

This skill provides tools for managing users and groups on a Linux system, including ownership and permissions.

## Concepts

- **User:** An account that can be used to log in to the system and access resources.
- **Group:** A collection of users that can be managed as a single entity.
- **Ownership:** Every file and directory has an owner and a group owner.
- **Permissions:** A set of rules that determine who can read, write, and execute a file.

## Tools

### `change_owner`

Changes the owner of a file or directory. This tool is a wrapper for the `chown` command.

**Usage:**

```python
def change_owner(path: str, owner: str, group: str = None, recursive: bool = False) -> None:
    """
    Changes the owner of a file or directory.

    Args:
        path: The path to the file or directory.
        owner: The new owner.
        group: The new group.
        recursive: Whether to change ownership recursively (chown -R).
    """
    pass
```

### `change_group`

Changes the group ownership of a file or directory. This tool is a wrapper for the `chgrp` command.

**Usage:**

```python
def change_group(path: str, group: str, recursive: bool = False) -> None:
    """
    Changes the group ownership of a file or directory.

    Args:
        path: The path to the file or directory.
        group: The new group.
        recursive: Whether to change ownership recursively (chgrp -R).
    """
    pass
```

### `change_permissions`

Changes the permissions of a file or directory. This tool is a wrapper for the `chmod` command.

**Usage:**

```python
def change_permissions(path: str, mode: str, recursive: bool = False) -> None:
    """
    Changes the permissions of a file or directory.

    Args:
        path: The path to the file or directory.
        mode: The new permissions (e.g., 'u+x', '755').
        recursive: Whether to change permissions recursively (chmod -R).
    """
    pass
```
