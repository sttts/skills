---
name: detailed-pr-comments
description: Create detailed PR review comments when the user asks to "comment on the line", "post this inline", "poste das an die Zeile", or leave a detailed comment on the relevant changed line. Do not use for review-only analysis or short comments.
version: 0.2.10
---

# Detailed PR Comments

- Post the full context inline on the most relevant changed line.
- Include the trigger, failure path, impact, focused manifest snippets when applicable, and a small illustrative diff when the fix is local.
- Do not hide context in collapsed `<details>` sections. Structure long comments with concise, descriptive Markdown headings so the full reasoning remains visible and scannable.
- Include required regression tests when they materially help the review, unless the user asks to omit them.

Only write to the remote pull request when the user explicitly asks to post or publish the comment. Otherwise, return a draft.
