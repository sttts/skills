# Review specification

The renderer accepts one UTF-8 JSON object. Only `title` and `findings` are required; all other fields are optional.

## Top-level fields

```json
{
  "version": 1,
  "title": "PR #123 · fix(component): summary",
  "subtitle": "main ← feature · commit abc123",
  "source_url": "https://github.com/org/repo/pull/123/files",
  "revision": "abc123",
  "github_collapsed_files": ["path/to/large-diff.go"],
  "status": "2 findings",
  "summary": "One-sentence review outcome.",
  "scope": {
    "in": ["Behavior owned by this change"],
    "out": ["Behavior owned elsewhere"]
  },
  "findings": [],
  "flows": [],
  "file_map": [],
  "code_blocks": [],
  "test_matrix": [],
  "references": [],
  "agent_prompt": "Concise implementation prompt.",
  "validation_note": "Static review only; tests not run."
}
```

For a GitHub pull request, set `source_url` to the PR, `/files`, or `/changes`
page. The renderer normalizes direct review links to GitHub's `/files` view.
The renderer derives each changed file's GitHub `diff-<sha256(path)>` anchor and
the corresponding `L<line>` or `R<line>` target. The dashboard uses these for
hover `+` buttons and direct links from findings, cases, annotations, and file
headers. Other source providers retain the generic source link.

List a changed path in `github_collapsed_files` when GitHub initially renders
that file behind `Load diff` (including large or generated diffs). GitHub has
not created its `L`/`R` line elements at that point, so the dashboard links to
the existing file anchor and tells the reviewer to load the diff and then use
the named old/new line. Do not emit a knowingly dead exact-line anchor.

## Findings

Every finding must point to a line present in the unified diff.
Findings are the review's defects and risks. The dashboard renders them first,
separately from scope boundaries, validation cases, and explanatory flows.

```json
{
  "id": "finding-stale-restore",
  "severity": "P1",
  "title": "Preserved data overrides a live deletion",
  "body": "Explain the triggering input, causal path, and user-visible consequence.",
  "file": "path/to/file.go",
  "side": "new",
  "line": 551,
  "links": [
    {"label": "logical flow", "target": "flow-live-source"},
    {"label": "restore helper", "target": "ref-restore-helper"}
  ]
}
```

`severity` accepts `P0`, `P1`, `P2`, `P3`, or `note`. Use `side: "old"` only for deleted lines.

## Logical flows

Use flows for causal paths with multiple locations.
Flows explain findings; they are not additional findings and are not repeated
as sidebar navigation.

```json
{
  "id": "flow-live-source",
  "title": "Deleted live mount returns",
  "description": "The preserved payload is consulted before origin reconstruction.",
  "steps": [
    {"label": "Step 1", "title": "Restore runs", "code": "restorePreserved(...) ", "target": "finding-stale-restore"},
    {"label": "Step 2", "title": "Gate passes", "code": "matches(firstCache)", "target": "ref-restore-helper"}
  ]
}
```

## File minimap

`total_lines` and marker `line` place clickable marks proportionally. Files need not be present in the diff.

```json
{
  "path": "path/to/file.go",
  "label": "core conversion",
  "total_lines": 2500,
  "markers": [
    {"line": 551, "label": "restore ordering", "target": "finding-stale-restore", "kind": "risk"},
    {"line": 2200, "label": "origin tests", "target": "ref-tests", "kind": "test"}
  ]
}
```

Marker `kind` accepts `relevant`, `risk`, `test`, or `out`.

## Code blocks, heatmap, and 10,000-foot rail

Use one `code_blocks` entry per larger logical diff block. The same entry drives
a 5 px heat bar at the far left of its line-number gutters and one sentence in
the right-side 10,000-foot rail.

```json
{
  "id": "block-restore-ordering",
  "file": "path/to/file.go",
  "side": "new",
  "start_line": 530,
  "end_line": 570,
  "heat": "high",
  "summary": "Merges preserved and live mounts, with the live-source precedence decided here."
}
```

`heat` accepts `high` (red: must inspect), `medium` (yellow: worth a look), or
`low` (green: routine). `start_line` and `end_line`
must both be rendered lines on the selected diff side. Keep `summary` to one
sentence and describe what the block does, not a line-by-line restatement.

## Test matrix

Test-matrix rows are validation cases, not findings. Every row must link to the
exact changed line whose behavior the case validates.

```json
{
  "case": "same key from both sources",
  "expected": "one merged entry",
  "status": "missing",
  "tone": "required",
  "file": "path/to/file.go",
  "side": "new",
  "line": 551
}
```

`tone` accepts `required`, `existing`, or `neutral`. `side` accepts `old` or
`new`; the selected `file`/`side`/`line` must exist in the unified diff.

## Reference snippets

```json
{
  "id": "ref-restore-helper",
  "path": "path/to/file.go",
  "lines": "920–930",
  "summary": "The gate checks only the first preserved cache.",
  "code": "func restorePreserved(...) {\n    before()\n    decisiveCheck()\n    after()\n}",
  "highlight_lines": [3],
  "back_target": "flow-live-source"
}
```

`highlight_lines` contains one-based line numbers within `code`, not source-file
line numbers. Include real source context on both sides of the highlighted lines;
normally two to four lines per side are enough. The renderer requires at least
one highlighted line and visible context before and after the highlighted range.
The dashboard inserts `summary` immediately after the last highlighted line in a
neutral gray inline annotation card. This is supporting evidence, not a finding.

## Output behavior

The renderer derives additions, deletions, changed files, diff line anchors, and file navigation from the unified diff. It rejects:

- malformed hunk headers;
- duplicate IDs;
- findings whose file/side/line is absent from the diff;
- test-matrix rows without an exact file/side/line diff anchor;
- reference snippets without valid highlighted lines and surrounding context;
- code blocks with invalid ranges or unsupported heat levels;
- links to unknown spec IDs;
- unsupported severities, sides, marker kinds, or test tones.
