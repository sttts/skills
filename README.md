# Skills for Claude Code and Codex

Plugins for local issue tracking with [beads](https://github.com/sttts/beads), git worktree management, prompt recording, cmux Codex subagents, and visual pull request reviews.

## Claude Code installation

```bash
# Add the marketplace
/plugin marketplace add https://github.com/sttts/skills.git

# Install plugins
/plugin install sttts-beads
/plugin install sttts-worktree
/plugin install sttts-prompt-recording
/plugin install sttts-cmux-codex
```

## Codex installation

```bash
codex plugin marketplace add sttts/skills
codex plugin add visual-review@sttts-skills
```

## Plugins

### visual-review

Create self-contained interactive HTML dashboards for deep pull request reviews. The dashboard includes correctness and safe-to-merge scores, code-smell indicators, interactive information-flow and finding diagrams, structured finding packages, API manifests, expandable full-context diffs, line-linked evidence, and per-finding fix prompts. Vendored graph libraries keep the artifact portable and offline-capable.

**Triggers on:** visual PR reviews, interactive review dashboards, GitHub-style annotated diffs, risk heatmaps, or requests to explain a pull request visually

**Codex only.**

### sttts-beads

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

### sttts-worktree

Git worktree management with three skills:

#### `/sttts-worktree:worktree` (auto-triggered)

Git worktree commands and usage reference.

**Triggers on:** `worktree`, `worktrees`, `create worktree`, `git worktree`

#### `/sttts-worktree:worktree-workflow` (explicit only)

Opinionated workflow using `.git/checkouts/` convention. Must be loaded explicitly.

- Create worktrees inside `.git/checkouts/`
- Stay in the worktree - don't cd back to main
- Never touch main when working in a worktree
- Never delete before confirming merge

Enable per-repo:
```bash
git config --local claude.worktrees true
```

#### `/sttts-worktree:prune-worktrees` (auto-triggered)

Clean up worktrees whose branches have been merged. Works with both GitLab (`glab`) and GitHub (`gh`).

**Triggers on:** `prune worktrees`, `cleanup worktrees`, `remove merged worktrees`

- Detects GitLab or GitHub from remote URL
- Checks each worktree branch for merged MR/PR
- Shows dirty/merged/unmerged status
- Asks for confirmation before removing

### sttts-prompt-recording

Record cleaned-up prompts attached to commits (via git notes) and MR/PR descriptions.

**Triggers on:** `record prompt`, `prompt recording`, `log prompts`

#### Features

- **Git notes** (`refs/notes/prompts`) - Per-commit prompt history in structured JSON
- **MR/PR description** - High-level "Prompt Documentation" section summarizing the whole conversation
- **Sticky opt-in** - Enable per-repo with `git config --local claude.promptRecording true`
- **Dual platform** - Works with both GitLab (`glab`) and GitHub (`gh`)

#### Prompt Philosophy

- Record **what the user actually asked for**, not what the agent decided
- Write prompts as **actionable instructions** that could reproduce the result
- Capture **architecture constraints** and **rejections** - these explain WHY
- Add context lines after each prompt explaining what it changed

#### Enable per-repo

```bash
git config --local claude.promptRecording true
```

### sttts-cmux-codex

Launch and manage loosely coupled Codex subagents in cmux columns.

**Triggers on:** `start cmux codex subagent`, `cmux codex session`, `codex cmux session`, launching a Codex subagent in cmux, or checking/tailing/focusing/closing a cmux subagent

#### Features

- Opens an independent Codex TUI session in a cmux column
- Creates/reuses `.codex/worktrees/<branch>` via the bundled `codex-worktree` wrapper
- Requires explicit `sttts-*` branch names and explicit base refs
- Tracks launched sessions so agents can request status, tail output, focus, or close them

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

# Clean up merged worktrees
/prune-worktrees

# Start a Codex cmux subagent
Start cmux codex subagent on branch sttts-investigate-foo to inspect issue #123

# Enable prompt recording
/prompt-recording

# End a session
Land the plane
```

## Requirements

- [beads CLI](https://github.com/sttts/beads) installed and configured (for sttts-beads)
- `glab` or `gh` CLI installed (for sttts-worktree prune)
- `cmux` and `codex` CLIs installed (for sttts-cmux-codex)
- Git repository

## License

MIT
