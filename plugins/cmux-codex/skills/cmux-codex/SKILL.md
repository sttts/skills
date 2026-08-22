---
name: cmux-codex
description: "Launch and manage loosely coupled cmux subagents: parallel interactive Codex sessions in cmux columns for user-given subtasks, using explicit sttts-* branches and the bundled codex-worktree wrapper. Use when the user says 'start cmux codex subagent', 'cmux codex session', 'codex cmux session', asks to launch a Codex subagent in cmux, or asks to start, check status, tail output, focus, or close a cmux subagent."
version: 0.2.9
---

# cmux Codex

Use this skill to launch a loosely coupled **cmux subagent**: a separate interactive Codex session in another cmux column for a subtask given by the user.

A cmux subagent is not a tightly managed in-process subagent. It is an independent Codex TUI session in another pane. Use it for parallel, loosely coupled work such as investigation, review, or a bounded implementation subtask that can run outside the parent agent's critical path.

## Launch

Run from the repository that should own the subagent worktree:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/cmux-codex column --branch sttts-some-task --base origin/main -- "prompt for the cmux subagent"
```

Rules:

1. `--branch` is required and must start with `sttts-`.
2. `--base` is required. Use `--base origin/main` unless the user gives another base.
3. The helper runs `git fetch origin` before resolving the base.
4. If the local branch already exists, it is reused.
5. If `origin/<branch>` exists and the local branch does not, the local branch is created from `origin/<branch>`.
6. Otherwise the branch is created from the explicit base.
7. The helper opens a new cmux terminal column and runs the bundled `${CLAUDE_PLUGIN_ROOT}/scripts/codex-worktree -w <branch> -- <prompt>` there.
8. After `codex-worktree` exits, the helper closes the cmux surface automatically so finished subagent tabs do not remain open.

The wrapper creates/reuses the standard worktree path:

```text
.codex/worktrees/<branch>
```

Useful launch options:

```bash
--direction right|left|up|down   # default: right
--model <model>
--profile <profile>
--sandbox <mode>
--add-dir <dir>
--no-focus                       # restore focus to the parent pane after launch
--dry-run                        # preview without fetch/branch/cmux actions
```

## Manage

Ask for status from a cmux subagent:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/cmux-codex status sttts-some-task
```

Read recent output without focusing or attaching:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/cmux-codex tail sttts-some-task -n 120
```

Focus the cmux subagent pane:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/cmux-codex focus sttts-some-task
```

Gracefully close the cmux subagent:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/cmux-codex close sttts-some-task
```

Default `close` sends an interrupt/exit request and then lets `codex-worktree` finish normally. If the wrapper shows its deletion prompt, the surface stays open for that prompt; after the wrapper exits, the launch command closes the cmux surface automatically. `close` does not answer the cleanup prompt automatically and does not force-delete a worktree or branch by itself.

List known cmux subagents:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/cmux-codex list
```

If the branch argument is omitted for status/tail/focus/close, the helper uses the most recently launched cmux subagent.

## Guardrails

- Do not launch without an explicit `sttts-*` branch and a prompt; ask the user if either is missing.
- Keep `--base` explicit. Prefer `origin/main`, after fetching origin.
- Treat cmux subagents as loosely coupled: give them bounded subtasks and do not depend on them for the next immediate step unless the user asked for parallel work.
- Use `status` before interrupting or closing a running cmux subagent.
- Do not use `codex exec`; this skill is for an interactive Codex TUI session in cmux.

## Requirements

- `cmux` CLI available on `PATH`, or pass `--cmux-bin`.
- `codex` CLI available on `PATH`, or set `CODEX_BIN`.
