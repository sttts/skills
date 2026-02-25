---
name: worktree-workflow
description: "Opinionated worktree workflow with .git/checkouts convention. Load explicitly with /worktree-workflow."
version: 0.2.5
user_invocable: true
---

# Worktree Workflow

Opinionated workflow for git worktrees using `.git/checkouts/` convention.

**This skill must be explicitly loaded** - it does not auto-trigger.

## Convention

All worktrees are created in `.git/checkouts/`:

```bash
git worktree add .git/checkouts/<branch> -b <branch>
cd .git/checkouts/<branch>
```

Benefits:
- Keeps worktrees organized in one place
- Hidden from IDE file explorers (inside .git)
- Easy to find and clean up

## Rules

When this workflow is active:

- **Create worktrees in `.git/checkouts/`** - consistent location
- **Stay in the worktree** - don't cd back to main checkout
- **Don't touch main** - work only on feature branch
- **Don't delete before merge** - confirm MR/PR is merged first
- **Don't mark task complete before merge** - merging happens after push

## Setup

Enable for a repo:

```bash
git config --local claude.worktrees true
mkdir -p .git/checkouts
```

Disable:

```bash
git config --local --unset claude.worktrees
```

## Creating a Worktree

```bash
git worktree add .git/checkouts/<branch> -b <branch>
cd .git/checkouts/<branch>
# All work happens here
```

## Cleanup

Use `/prune-worktrees` to check for merged branches and clean up.

Manual cleanup:

```bash
git worktree remove .git/checkouts/<branch>
git worktree prune
```
