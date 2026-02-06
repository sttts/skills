---
name: prune-worktrees
description: "Clean up worktrees for merged branches. Triggers on 'prune worktrees', 'cleanup worktrees', 'remove merged worktrees'."
version: 0.2.2
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

# 2. List all worktrees in .git/checkouts/
WORKTREES_DIR=".git/checkouts"
if [[ ! -d "$WORKTREES_DIR" ]]; then
  echo "No worktrees directory found."
  exit 0
fi
```

## Detection Logic

For each worktree in `.git/checkouts/`:

1. Get the branch name from the worktree
2. Check if a merged MR/PR exists for that branch:
   - **GitLab:** `glab mr list --state merged --source-branch <branch>`
   - **GitHub:** `gh pr list --state merged --head <branch>`
3. If merged, mark for cleanup

## Output Format

Present findings to user:

```
Worktree Cleanup Check
======================

Merged (safe to remove):
  .git/checkouts/feature-123  (branch: feature-123, MR !45 merged)
  .git/checkouts/fix-bug      (branch: fix-bug, PR #67 merged)

Not merged (keep):
  .git/checkouts/wip-stuff    (branch: wip-stuff, no merged MR/PR)

Untracked (no remote branch):
  .git/checkouts/local-only   (branch: local-only, not pushed)
```

## Cleanup Commands

After user confirms, remove merged worktrees:

```bash
# For each confirmed worktree
git worktree remove .git/checkouts/<name>

# Prune stale worktree references
git worktree prune

# Optionally delete the remote branch if still exists
git push origin --delete <branch>
```

## Safety Rules

- **NEVER auto-delete** - always show list and ask for confirmation
- **NEVER delete untracked worktrees** - user may have unpushed work
- **Check for uncommitted changes** before removing:
  ```bash
  git -C .git/checkouts/<name> status --porcelain
  ```
  If output is non-empty, warn user about uncommitted changes

## Script

```bash
#!/bin/bash
set -euo pipefail

WORKTREES_DIR=".git/checkouts"
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

# Detect CLI
if [[ "$REMOTE_URL" == *"gitlab"* ]]; then
  CLI="glab"
  MR_CMD="mr"
elif [[ "$REMOTE_URL" == *"github"* ]]; then
  CLI="gh"
  MR_CMD="pr"
else
  echo "Error: Cannot detect GitLab or GitHub from remote: $REMOTE_URL"
  exit 1
fi

if [[ ! -d "$WORKTREES_DIR" ]]; then
  echo "No worktrees found in $WORKTREES_DIR"
  exit 0
fi

echo "Checking worktrees for merged branches..."
echo

MERGED=()
UNMERGED=()
DIRTY=()

for dir in "$WORKTREES_DIR"/*/; do
  [[ -d "$dir" ]] || continue
  name=$(basename "$dir")
  branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

  # Check for uncommitted changes
  if [[ -n $(git -C "$dir" status --porcelain 2>/dev/null) ]]; then
    DIRTY+=("$name ($branch) - has uncommitted changes")
    continue
  fi

  # Check if branch has merged MR/PR
  if [[ "$CLI" == "glab" ]]; then
    merged=$($CLI mr list --state merged --source-branch "$branch" 2>/dev/null | head -1)
  else
    merged=$($CLI pr list --state merged --head "$branch" 2>/dev/null | head -1)
  fi

  if [[ -n "$merged" ]]; then
    MERGED+=("$name ($branch) - $merged")
  else
    UNMERGED+=("$name ($branch)")
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
