---
name: visual-review
description: Create self-contained interactive HTML code-review dashboards from GitHub or GitLab pull requests, checked-out branch diffs, or supplied unified diffs. Use when Codex is asked for a visual PR review, a GitHub-style red/green diff with line annotations, linked logical flows, a 10,000-foot file minimap, scope or test matrices, or a reusable agent fix prompt.
---

# Visual Review

Produce a deep code review and render it as one portable HTML file with no external dependencies.

## Workflow

1. Read repository instructions from the active worktree before inspecting code.
2. Acquire the exact unified diff and immutable revision metadata.
   - Remote PR: use the repository CLI/API without checking out unless requested.
   - Current branch: diff against the actual merge base.
   - Supplied patch: preserve it verbatim.
3. Read changed code plus enough callers, types, tests, and invariants to support every finding. Do not run tests when the user requests a read-only review.
4. Write a review spec following [references/review-schema.md](references/review-schema.md). Keep prose concise and evidence-based.
5. Render the dashboard:

```bash
python3 <skill-dir>/scripts/render_review.py \
  --spec /absolute/path/review.json \
  --diff /absolute/path/review.diff \
  --output <workspace-artifact-dir>/<review-name>.html
```

   Resolve `<workspace-artifact-dir>` inside the active Codex workspace, not inside a temporary review worktree. Prefer a writable, VCS-ignored `.codex/reviews/`; otherwise use a writable, VCS-ignored workspace directory such as `tmp/codex-reviews/`. Confirm the chosen directory with `git check-ignore` when the workspace uses Git. The renderer creates the output directory when needed.
6. Re-run with `--validate-only` after edits. If a local headless browser exists, inspect the rendered page; otherwise rely on the renderer's structural, anchor, and annotation validation.
7. Return only a clickable Markdown file link to the workspace-local HTML artifact. Link the bare absolute `.html` path with no `#fragment`; Codex workspace file links with URL fragments may fail to open. Internal anchors remain available after the HTML file is open. Never hand off a final review from `/tmp`, `$TMPDIR`, `~/Library/Caches`, or any path outside the active workspace; those locations are temporary working storage only.

## Review contract

- Include the complete diff with old/new line numbers and GitHub-style red/green rows.
- Anchor each actionable finding to an exact changed line. Do not label the requested implementation itself as an additional finding; distinguish known scope from newly found defects.
- Render a findings overview immediately after the summary. Show severity, title, explanation, and a direct link to the annotated code before scope, validation cases, or logical flows.
- Keep dashboard concepts explicit and separate: findings are defects or risks; scope states review boundaries; validation cases describe how to prove behavior; logical flows explain multi-location causality. Never present these as peer lists without labels.
- Link multi-step behavior through flow cards and reference snippets when the bug crosses three or more locations.
- Keep logical flows in the main content only. Do not duplicate them as sidebar navigation.
- Make every internal anchor destination unmistakable: flash the actual destination on navigation and leave it visibly highlighted. Diff-line anchors must highlight the whole diff row, not only the line number, and clicking the current anchor again must retrigger the flash. Preserve a strong static highlight when reduced motion is requested.
- Make reference anchors focus the evidence rather than the outer reference container: center the inline reference annotation in the viewport and apply the anchor palette to both the decisive code lines and the annotation card. Do not rely on an outline around the full reference block.
- When `source_url` is a GitHub pull request, normalize direct review links to the current `/changes` view and derive exact diff anchors for changed files and old/new lines. Place a GitHub-style blue `+` button on the boundary between the number gutters and code, sized like GitHub's control. Reveal it only when the code cell is hovered or the button receives keyboard focus, not when the line numbers or another part of the row is hovered. Open the exact GitHub PR line in a new tab without replacing the local review; use both `target="_blank"` with `rel="noopener noreferrer"` and an explicit user-click `window.open(..., "_blank", "noopener,noreferrer")` handler because embedded app browsers may ignore the target attribute. Do not claim that this opens GitHub's comment editor: GitHub has no comment-form deep link, so the user must hover that line and click GitHub's own `+`; state this in the button tooltip. Keep the line number itself as the dashboard's internal anchor, and also expose direct PR links from finding summaries, inline annotations, validation cases, and file headers.
- Use the minimap for changed files, important callers/types/tests, and explicit out-of-scope areas.
- Define larger logical diff ranges once in `code_blocks`. Use `high`/red for code that must be inspected, `medium`/yellow for code worth a look, and `low`/green for routine changes. Render the heat as a 5 px bar at the far left of the number gutters; do not recolor the number or code backgrounds, because those already encode diff semantics.
- Render a right-side 10,000-foot rail beside each file diff from the same `code_blocks` data. Align one concise sentence with the start of each larger block; explain what the block does and avoid line-by-line narration or repeating findings.
- State what is in scope and out of scope when ownership spans multiple PRs.
- Make the agent fix prompt short. Include only non-obvious task constraints, behavior, and tests; do not repeat repository instructions that the agent will load from `AGENTS.md` or equivalent files.
- Report tests as unrun unless they were actually executed.
- Keep the final HTML review inside a writable, preferably VCS-ignored directory in the active workspace so the Codex app can open the file link reliably.
- Never post review comments, mutate the PR, or change source code unless the user separately requests it.

## Spec guidance

- Put findings in severity order (`P0` through `P3`, then notes).
- Use stable IDs for findings, flows, references, and scope sections so links remain meaningful.
- Prefer plain text with backticks for identifiers; the renderer escapes all content.
- Add exact validation cases to the matrix when coverage is part of the review. Every row must identify an exact changed code line with `file`, `side`, and `line`; link the row to that diff anchor.
- Keep reference snippets short and focused on the causal path, but include a few real source lines before and after the decisive code. Mark the decisive one-based snippet lines in `highlight_lines`; render them in light blue so evidence is distinguishable from context at a glance. Render the reference `summary` directly after the last highlighted line as a neutral gray annotation card with the same structure as P1/P2 inline annotations, but never present it as an additional finding.

The renderer and HTML template live in `scripts/render_review.py` and `assets/review-template.html`.
