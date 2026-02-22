# Version Control (Git)

This skill covers using Git for source code management, collaboration, and release management. Git is the de-facto standard distributed version control system used in virtually every modern software project.

## Concepts

A **repository** (repo) is a directory that Git tracks. Every change is recorded as a **commit** — a snapshot of the entire project at a point in time, identified by a SHA-1 hash. Commits are linked in a directed acyclic graph, forming the project history.

A **branch** is a lightweight pointer to a commit. The default branch is usually called `main` or `master`. Branches allow parallel lines of development that can later be **merged** back together.

A **remote** is a named reference to a repository hosted elsewhere (e.g. GitHub, GitLab). `origin` is the conventional name for the primary remote. `git push` uploads local commits to the remote; `git pull` downloads and integrates remote commits.

## Tools Available

| Tool | Description |
|------|-------------|
| `git_init` | Initialise a new repository |
| `git_clone` | Clone a remote repository |
| `git_status` | Show working tree status |
| `git_add` | Stage files for commit |
| `git_commit` | Record staged changes |
| `git_push` | Push commits to a remote |
| `git_pull` | Fetch and merge remote changes |
| `git_log` | Show commit history |
| `git_diff` | Show uncommitted or staged changes |
| `git_branch` | List, create, or delete branches |
| `git_checkout` | Switch branches or restore files |
| `git_merge` | Merge a branch into the current branch |
| `git_stash` | Temporarily shelve uncommitted changes |
| `git_tag` | Create or list version tags |
| `git_remote` | Manage remote repository connections |

## Usage Examples

**Clone a repository and make a commit:**
```
git_clone(url="https://github.com/example/repo.git", destination="/opt/repo")
git_add(path="/opt/repo", files=".")
git_commit(path="/opt/repo", message="Initial configuration")
git_push(path="/opt/repo", remote="origin", branch="main")
```

**Create a feature branch and merge it:**
```
git_branch(path="/opt/repo", create="feature/new-config")
git_checkout(path="/opt/repo", branch="feature/new-config")
# ... make changes ...
git_checkout(path="/opt/repo", branch="main")
git_merge(path="/opt/repo", branch="feature/new-config")
```

## Skill Levels

**Entry** — Clone, add, commit, push, and pull; understand the working tree, index, and HEAD.

**Beginner** — Create and merge branches, resolve simple merge conflicts, use .gitignore.

**Intermediate** — Rebase, cherry-pick, use git bisect to find regressions, manage submodules.

**Advanced** — Write Git hooks, manage large monorepos, implement branching strategies (GitFlow, trunk-based development).
