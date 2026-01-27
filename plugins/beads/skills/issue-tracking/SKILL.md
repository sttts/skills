---
name: Beads Issue Tracking
description: This skill should be used when the user mentions "bd", "beads", "what's next", "add task", "add epic", or asks about issue tracking. First check if a .beads directory exists in the project - if not, this skill does not apply.
version: 0.1.0
---

# Beads Issue Tracking

This skill provides workflow guidance for projects using the beads issue tracker.

## Activation

**Only apply these instructions when a `.beads` directory exists in the project root.** If no `.beads` directory is present, this skill does not apply.

## Session Start

Every session start, run `bd prime` to get AI-optimized workflow context.

## Checking What's Next

When the user asks "What's next?", run `bd ready --pretty` and propose the top items without asking for confirmation. Show a list like:

```
In-progress tasks:
- <task id>: <oneliner>
- ...

Ready tasks:
- <task id>: <oneliner>
- ...
```

## Creating Issues

Treat user phrases "Add task" and "Add epic" as instructions to use `bd create` with the appropriate type.

Use sensible keywords in task IDs following the pattern `<prefix>-<epic>-<task>`:
- `prefix`: domain area (e.g., `infra`, `api`, `ui`)
- `epic`: one or two keywords for the epic
- `task`: one keyword for the specific task

### Example Commands

```bash
# Create a task
bd create "Allow blueprints to run in plan only mode" --id infra-blueprint-planonly --type task

# Create an epic
bd create "Expose Terraform errors to conditions" --id infra-tferrors --type epic

# Create a task under an epic
bd create "Phase 1: Enable log subresource" --id infra-tferrors-logsub --type task --parent infra-tferrors
```

## Task State Management

Always set tasks in-progress when working on them, and close when finished.

Always put the MR/PR URL as label on tasks. When the user references a PR, use `bd list --label "<URL>"` to find the task.

## Epics

Every epic work MUST happen in a dedicated worktree. Create it with:

```bash
bd worktree create .git/checkouts/<branch-name>
```

Always use the same worktree and branch. Never divert without the user telling you.

## Landing the Plane (Session Completion)

**When ending a work session**, complete ALL steps below. Work is NOT complete until `git push` succeeds.

### Mandatory Workflow

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Push to remote** - This is mandatory:
   ```bash
   git pull --rebase
   bd sync
   git push origin <branch-name>
   git status  # MUST show "up to date with origin"
   ```
5. **Label** - Put the PR/MR URL on the task
6. **Clean up** - Clear stashes, prune remote branches
7. **Verify** - All changes committed AND pushed
8. **Hand off** - Add a `bd comments add <task-id> "HANDOFF: ..."` comment explaining what the next agent should do (e.g., check MR status, address feedback, close task)

### Critical Rules

- Work is NOT complete until `git push` succeeds
- Never stop before pushing - that leaves work stranded locally
- Never say "ready to push when you are" - push immediately
- If push fails, resolve and retry until it succeeds
- Only close a task when the MR is merged. Rather defer a task for an hour if uncertain.
- When deferring a task, ALWAYS add a handoff comment first: `bd comments add <task-id> "HANDOFF: ..."` explaining what the next agent should do
- Never leave the worktree unless asked. Only exception: switching to another epic or a task that already has a worktree.
- Never touch the main checkout without the user telling you.
