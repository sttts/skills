---
name: worktree
description: "Git worktree commands and usage. Triggers on 'worktree', 'worktrees', 'create worktree', 'git worktree'."
version: 0.2.3
---

# Git Worktrees

Git worktrees allow working on multiple branches simultaneously in separate directories.

## Commands

### Create a worktree

```bash
# Create worktree with new branch
git worktree add <path> -b <new-branch>

# Create worktree for existing branch
git worktree add <path> <existing-branch>
```

### List worktrees

```bash
git worktree list
```

### Remove a worktree

```bash
# Remove worktree (directory must be clean)
git worktree remove <path>

# Force remove (even if dirty)
git worktree remove --force <path>
```

### Prune stale references

```bash
git worktree prune
```

## Common Patterns

### Feature branch worktree

```bash
git worktree add ../feature-123 -b feature-123
cd ../feature-123
# work on feature
```

### Hotfix while preserving current work

```bash
git worktree add ../hotfix -b hotfix/urgent-fix origin/main
cd ../hotfix
# fix the issue
git push
cd -
git worktree remove ../hotfix
```

### Review a PR/MR locally

```bash
git worktree add ../review-pr-456 origin/feature-branch
cd ../review-pr-456
# review code
cd -
git worktree remove ../review-pr-456
```

## Tips

- Each worktree has its own working directory and index
- You cannot have the same branch checked out in multiple worktrees
- Worktrees share the same `.git` objects - efficient disk usage
- Use `git worktree lock <path>` to prevent accidental removal
