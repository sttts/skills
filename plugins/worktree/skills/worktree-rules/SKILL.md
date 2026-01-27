---
name: Git Worktree Rules
description: This skill should be used when the user mentions "worktree", "worktrees", "create worktree", or asks about working in a separate branch directory.
version: 0.1.0
---

# Git Worktree Rules

These rules apply whenever working with git worktrees.

## Directory Location

- MUST create worktrees inside `.git/checkouts/` directory.

## Critical Restrictions

- MUST NEVER leave a worktree once working in it. Do all work there.
- MUST NEVER touch main when working in a worktree. This is critical.
- MUST NEVER delete a worktree before confirming its content is merged.
- MUST NEVER mark a task as completed until the branch is merged (merging happens outside the worktree).
