---
name: prompt-recording
description: "Record prompts to git notes and MR/PR descriptions. Triggers on 'record prompt', 'prompt recording', 'log prompts'."
version: 0.2.4
---

# Prompt Recording

Record cleaned-up prompts attached to commits (via git notes) and MR/PR descriptions. Works with both GitLab (`glab`) and GitHub (`gh`).

## Storage

| Storage | Purpose | Visibility |
|---------|---------|------------|
| **Git notes** (`refs/notes/prompts`) | Per-commit prompt history | CLI only, must fetch explicitly |
| **MR/PR description** | High-level summary of whole conversation | Visible to all in GitLab/GitHub UI |

## On Skill Load

**FIRST:** Check if prompt recording is enabled for this repo:

```bash
ENABLED=$(git config --local --get claude.promptRecording 2>/dev/null || echo "")
```

**If `true`:** Prompt recording is already configured. **Skip setup, proceed directly to Workflow Instructions.** Do NOT re-run git config commands.

**If not set:** Ask the user:
> "Enable prompt recording for this repo? This records prompts to git notes and MR descriptions.
>
> **This is sticky** - will auto-activate in future sessions.
> To disable later: `git config --local --unset claude.promptRecording`"

- If yes: run the setup command below
- If no: exit skill (don't set config, user can invoke the skill again later)

**If `false`:** User previously declined. Ask if they want to enable now.

**Setup (run ONLY on first enable, not on every load):**

```bash
git config --local claude.promptRecording true && \
  (git config --get-all remote.origin.fetch | grep -q 'refs/notes/prompts' || git config --add remote.origin.fetch '+refs/notes/prompts:refs/notes/prompts') && \
  (git config --get notes.rewriteRef 2>/dev/null | grep -q 'refs/notes/prompts' || git config --add notes.rewriteRef refs/notes/prompts)
```

**Output on first enable:**
```
Prompt recording enabled for this repo.
- Prompts will be recorded to git notes on each commit
- MR/PR descriptions will include prompt documentation
- This setting is sticky (persists across sessions)
- To disable: git config --local --unset claude.promptRecording
```

## Workflow Instructions

### On Every `git commit`

Immediately after each commit, record the prompt that led to this change:

```bash
git notes --ref=prompts add HEAD -m '{"version":1,"timestamp":"2026-02-06T10:30:00Z","prompt":"<actionable prompt>"}'
```

**Format (JSON):**
```json
{
  "version": 1,
  "timestamp": "2026-02-06T10:30:00Z",
  "prompt": "Add input validation to the API endpoint using regex patterns. Validate email format, check required fields, return all errors at once instead of fail-fast."
}
```

The `prompt` field must be **what the user actually asked for** - not a summary, not what the agent decided. Only record what the user said.

### On `git push`

Push prompt notes along with code:

```bash
git push origin refs/notes/prompts
```

### On MR/PR Create or Update

Add/update the "Prompt Documentation" section in the MR/PR description body.

**IMPORTANT:** Before writing the MR description, read the **entire prompt note history** for all commits in the branch:

```bash
git log --show-notes=prompts origin/main..HEAD
```

This is critical when picking up an existing branch - integrate notes from previous sessions into the summary.

**GitLab:**
```bash
glab mr create --title "Title" --description "$(cat <<'EOF'
## Summary
...

## Prompt Documentation

> Add input validation to the user registration API. Validate email format, check required fields, return comprehensive error messages.

**Architecture prompts:**
> The validation must run in the API gateway, not in individual services.
This moved validation from per-service to a single enforcement point.

**Design prompts:**
> Don't use a validator library like go-playground/validator - avoid the dependency for these simple rules.
Kept the implementation self-contained with no new dependencies.

> Use compile-time regex, not runtime compilation - we need O(1) validation performance.
Changed from runtime regex.Compile to compile-time regexp.MustCompile.

> Return all validation errors at once instead of fail-fast - better UX when users see the complete picture.
Switched from early-return to collecting all errors before responding.

> Add custom error types for each validation failure so callers can do typed error handling.
Enabled typed error handling instead of string matching.

> Don't add async validation for external checks like "email exists" yet - adds complexity, defer until we actually need it.

**Iteration prompts:**
> Ensure 80%+ test coverage for the new validation code.

> Use table-driven tests for the validation edge cases.

> Follow the existing error handling patterns in the codebase.

*Co-developed with Claude*

## Test Plan
...
EOF
)"

# Or update existing MR
glab mr update <number> --description "..."
```

**GitHub:**
```bash
gh pr create --title "Title" --body "$(cat <<'EOF'
...same format...
EOF
)"

# Or update existing PR
gh pr edit <number> --body "..."
```

## Commands Reference

```bash
# View prompts for a commit
git notes --ref=prompts show HEAD
git log --show-notes=prompts

# View prompts for MR commits
git log --show-notes=prompts origin/main..HEAD

# Fetch notes from remote (if not auto-configured)
git fetch origin refs/notes/prompts:refs/notes/prompts
```

## Cleanup Guidelines

### For Git Notes `prompt` Field

Write an actionable prompt that could be given to another agent to achieve the same result. Not a summary or description - an actual prompt.

**Good:**
- `"Add retry logic to the HTTP client with exponential backoff, max 3 retries, initial delay 100ms"`
- `"Refactor the validation module to use a strategy pattern, extract each validator into its own class"`

**Bad:**
- `"Implemented retry logic for better resilience"` (this is a summary, not a prompt)
- `"Fixed the bug"` (not actionable)

### For MR/PR Description

**Only record what the user actually said.** Do NOT invent prompts for things the agent decided on its own.

Write as **actual prompts in user voice** - instructions the user gave. When condensing multiple exchanges into one prompt, it should still read like something the user said or could have said, not like an agent describing what happened. This builds trust that proper prompting was done.

**Bad modality:** "User showed analysis from another agent where design discussions were lost" (agent voice, describing events)
**Good modality:** "How can we capture the design discussions that get lost in plan mode?" (user voice, actionable)

**Include (only things the user actually said):**
- The initial task prompt (as the user said it)
- Architecture constraints ("the CRD must be served by the apiserver, not the host cluster") - these are often the most valuable prompts because they shaped fundamental design decisions
- Corrections and rejections - when the user rejected an agent's approach and redirected ("don't use the helm chart, do X instead") - record both what was rejected and why
- Design direction the user gave ("use X instead of Y because...")
- What the user said NOT to do

**After each quoted prompt, add a one-line context sentence** explaining what this changed or constrained in the implementation. Bare quotes are meaningless without context.

**Do NOT include:**
- Things the agent figured out or decided autonomously
- Implementation details the agent chose without being asked
- Prompts the agent "would have needed" but the user never gave
- **References to local files** (e.g., "Follow plan in session-name.md") - these are useless to reviewers
- Raw back-and-forth conversation
- Mechanical steps (retry CI, fix linter, bump version, rebase, resolve merge conflicts)
- Debugging steps and error messages
- Code snippets
- Meta-commentary ("we discussed...", "it was decided...")

**Plans and plan mode:**
- **NEVER reference local plan files** (e.g., "Follow plan in cheerful-imagining-karp.md") - these are meaningless outside the session
- **Every user rejection or redirection during plan mode is a design prompt** - these are often the most important prompts because they explain WHY the implementation looks the way it does. Record them all.
- If using an issue tracker, persist the plan there first, then reference the issue
- If no issue tracker, inline the plan in the MR description

### ALWAYS Remove

- Swearing and inappropriate language
- Personal data (names, emails unless public)
- Proprietary or confidential data
- Credentials, secrets, API keys

## MR/PR Description Format

The Prompt Documentation section enables someone to understand "what prompts and instructions produced this MR and why these decisions were made."

**IMPORTANT:** Only record prompts the user actually gave. Do NOT fabricate prompts for agent-initiated decisions. If the agent decided something on its own (e.g., chose a library, picked an approach), that's not a prompt - omit it. This faithfulness is what builds trust.

**Review before finalizing:** Go through the conversation and extract only what the user said:
- The initial task prompt (the user's actual words)
- Constraints or requirements the user explicitly stated
- Corrections the user made ("no, do X instead")
- Explicit decisions about what NOT to do

```markdown
## Prompt Documentation

> Create a skill to record prompts to git notes and MR descriptions. Make it work with both GitLab and GitHub. Use git notes for per-commit history and MR description for a high-level session summary.

**Design prompts:**
> Use hybrid storage: git notes are for CLI tooling and per-commit detail, MR description is for team visibility.
Split storage between per-commit notes and MR-level summary.

> Don't dump per-commit notes into the MR - write a single integrated summary that keeps it readable.

> Make it standalone and opt-in for testing - don't integrate with the issue tracker yet.
Kept the skill independent so it can be tested without the full workflow.

**Iteration prompts:**
> The prompt field must be actionable - something you could give to another agent to achieve the same result, not a summary.

> When picking up an existing branch, read the entire prompt note history and integrate previous sessions into the summary.

*Co-developed with Claude*
```
