# Skills for Claude Code

Claude Code skills for local issue tracking with [beads](https://github.com/sttts/beads) and git worktree management.

## Installation

```bash
# Add the marketplace
/plugin marketplace add https://github.com/sttts/skills.git

# Install plugins
/plugin install beads
/plugin install worktree
```

## Plugins

### Beads Issue Tracking

Local issue tracking workflow integration using the [beads](https://github.com/sttts/beads) CLI.

**Triggers on:** `bd`, `beads`, `what's next`, `add task`, `add epic`, or issue tracking questions

**Requires:** `.beads` directory in project root (run `bd init` to create)

#### Features

- **Session priming** - Run `bd prime` at session start for AI-optimized context
- **Task discovery** - Ask "What's next?" to see in-progress and ready tasks
- **Issue creation** - Create tasks and epics with structured IDs
- **State management** - Track task status and link to PRs/MRs
- **Session completion** - Structured workflow for landing work safely

#### Issue ID Convention

Use the pattern `<prefix>-<epic>-<task>`:
- `prefix`: domain area (e.g., `infra`, `api`, `ui`)
- `epic`: one or two keywords for the epic
- `task`: one keyword for the specific task

```bash
# Create a task
bd create "Allow blueprints to run in plan only mode" --id infra-blueprint-planonly --type task

# Create an epic
bd create "Expose Terraform errors to conditions" --id infra-tferrors --type epic

# Create a task under an epic
bd create "Phase 1: Enable log subresource" --id infra-tferrors-logsub --type task --parent infra-tferrors
```

#### Session Completion Workflow

When ending a session, the skill ensures:
1. File issues for remaining work
2. Run quality gates (tests, linters, builds)
3. Update issue status
4. Push to remote (mandatory - work is not complete until pushed)
5. Label tasks with PR/MR URLs
6. Add handoff comments for the next agent

### Git Worktree Rules

Git worktree management guidance for isolated branch work.

**Triggers on:** `worktree`, `worktrees`, `create worktree`, or working in a separate branch directory

#### Rules

- Create worktrees inside `.git/checkouts/` directory
- Never leave a worktree once working in it
- Never touch main when working in a worktree
- Never delete a worktree before confirming content is merged
- Never mark a task as completed until the branch is merged

#### Usage with Beads

Every epic should have a dedicated worktree:

```bash
bd worktree create .git/checkouts/<branch-name>
```

## Usage Examples

```
# Start a session
bd prime

# Check what to work on
What's next?

# Create a new task
Add task: Implement user authentication

# Create a worktree for an epic
Create a worktree for the auth-refactor epic

# End a session
Land the plane
```

## Requirements

- [beads CLI](https://github.com/sttts/beads) installed and configured
- Git repository with worktree support

## License

MIT
