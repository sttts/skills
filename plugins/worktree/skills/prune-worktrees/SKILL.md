---
name: prune-worktrees
description: "Clean up worktrees for merged branches. Triggers on 'prune worktrees', 'cleanup worktrees', 'remove merged worktrees'."
version: 0.2.4
---

# Prune Worktrees

Clean up worktrees whose branches have been merged on GitLab or GitHub.

## On Skill Load

Run the cleanup check automatically:

```bash
# 1. Detect remote type (GitLab or GitHub)
REMOTE_URL=$(git remote get-url origin)

if [[ "$REMOTE_URL" == *"gitlab"* ]]; then
  CLI="glab"
elif [[ "$REMOTE_URL" == *"github"* ]]; then
  CLI="gh"
else
  echo "Unknown remote type: $REMOTE_URL"
  exit 1
fi

# 2. List all worktrees (not just .git/checkouts/)
git worktree list
```

## Detection Logic

Use `git worktree list` to find all worktrees regardless of location. Skip the main worktree (first entry).

For each non-main worktree:

1. Get the path and branch from `git worktree list`
2. Check if a merged MR/PR exists for that branch:
   - **GitLab:** `glab mr list --merged --source-branch <branch>`
   - **GitHub:** `gh pr list --state merged --head <branch>`
3. If merged, mark for cleanup

Also check the **current worktree** - if we're on a branch that's been merged, flag it.

## Output Format

Present findings to user:

```
Worktree Cleanup Check
======================

Merged (safe to remove):
  /path/to/feature-123  (branch: feature-123, MR !45 merged)
  /path/to/fix-bug      (branch: fix-bug, PR #67 merged)

Not merged (keep):
  /path/to/wip-stuff    (branch: wip-stuff, no merged MR/PR)

Dirty (has uncommitted changes):
  /path/to/dirty-one    (branch: dirty-one, has uncommitted changes)
```

## Cleanup Commands

After user confirms, remove merged worktrees:

```bash
# For each confirmed worktree
git worktree remove <path>

# Prune stale worktree references
git worktree prune

# Optionally delete the remote branch if still exists
git push origin --delete <branch>
```

## Safety Rules

- **NEVER auto-delete** - always show list and ask for confirmation
- **NEVER delete worktrees with uncommitted changes** without warning
- **Check for uncommitted changes** before removing:
  ```bash
  git -C <worktree-path> status --porcelain
  ```
  If output is non-empty, warn user about uncommitted changes
- **Skip the main worktree** - never offer to remove the primary checkout

## Script

```bash
#!/bin/bash
set -euo pipefail

REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

# Detect CLI
if [[ "$REMOTE_URL" == *"gitlab"* ]]; then
  CLI="glab"
elif [[ "$REMOTE_URL" == *"github"* ]]; then
  CLI="gh"
else
  echo "Error: Cannot detect GitLab or GitHub from remote: $REMOTE_URL"
  exit 1
fi

echo "Checking worktrees for merged branches..."
echo

MERGED=()
UNMERGED=()
DIRTY=()
FIRST=true

# Parse git worktree list output: <path> <sha> [<branch>]
git worktree list | while read -r wt_path wt_sha wt_branch_raw; do
  # Skip main worktree (first entry)
  if $FIRST; then
    FIRST=false
    continue
  fi

  # Extract branch name from [branch] format
  branch="${wt_branch_raw#[}"
  branch="${branch%]}"

  # Skip detached HEAD
  if [[ "$branch" == "(detached" || -z "$branch" ]]; then
    UNMERGED+=("$wt_path (detached HEAD)")
    continue
  fi

  # Check for uncommitted changes
  if [[ -n $(git -C "$wt_path" status --porcelain 2>/dev/null) ]]; then
    DIRTY+=("$wt_path ($branch) - has uncommitted changes")
    continue
  fi

  # Check if branch has merged MR/PR
  if [[ "$CLI" == "glab" ]]; then
    merged=$($CLI mr list --merged --source-branch "$branch" 2>/dev/null | head -1)
  else
    merged=$($CLI pr list --state merged --head "$branch" 2>/dev/null | head -1)
  fi

  if [[ -n "$merged" ]]; then
    MERGED+=("$wt_path ($branch) - $merged")
  else
    UNMERGED+=("$wt_path ($branch)")
  fi
done

if [[ ${#MERGED[@]} -gt 0 ]]; then
  echo "MERGED (safe to remove):"
  for item in "${MERGED[@]}"; do
    echo "  $item"
  done
  echo
fi

if [[ ${#DIRTY[@]} -gt 0 ]]; then
  echo "DIRTY (has uncommitted changes - review first):"
  for item in "${DIRTY[@]}"; do
    echo "  $item"
  done
  echo
fi

if [[ ${#UNMERGED[@]} -gt 0 ]]; then
  echo "NOT MERGED (keep):"
  for item in "${UNMERGED[@]}"; do
    echo "  $item"
  done
  echo
fi

if [[ ${#MERGED[@]} -eq 0 ]]; then
  echo "No merged worktrees to clean up."
fi
```

Run this script, then ask the user which worktrees to remove.
