#!/usr/bin/env python3
"""Render and validate a self-contained visual code-review dashboard."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DIFF_RE = re.compile(r"^diff --git a/(.+) b/(.+)$")
VALID_SEVERITIES = {"P0", "P1", "P2", "P3", "note"}
VALID_SIDES = {"old", "new"}
VALID_MARKER_KINDS = {"relevant", "risk", "test", "out"}
VALID_TEST_TONES = {"required", "existing", "neutral"}
VALID_HEAT_LEVELS = {"high", "medium", "low"}


class ReviewError(ValueError):
    pass


def slug(value: str) -> str:
    return re.sub(r"^-|-$", "", re.sub(r"[^A-Za-z0-9]+", "-", value))


def require_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ReviewError(f"{field} must be a non-empty string")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ReviewError(f"{field} must be an array")
    return value


def github_pr_changes_url(source_url: str) -> str:
    """Normalize a GitHub pull-request URL to its current changes view."""
    parsed = urlsplit(source_url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {"github.com", "www.github.com"}:
        return ""
    match = re.fullmatch(r"/([^/]+)/([^/]+)/pull/(\d+)(?:/(?:files|changes))?/?", parsed.path)
    if not match:
        return ""
    changes_path = f"/{match.group(1)}/{match.group(2)}/pull/{match.group(3)}/changes"
    return urlunsplit((parsed.scheme, parsed.netloc, changes_path, "", ""))


def github_diff_anchors(source_url: str, files: list[dict[str, Any]]) -> dict[str, str]:
    """Return GitHub PR file anchors keyed by the post-change path."""
    changes_url = github_pr_changes_url(source_url)
    if not changes_url:
        return {}
    return {
        item["path"]: f"{changes_url}#diff-{hashlib.sha256(item['path'].encode('utf-8')).hexdigest()}"
        for item in files
    }


def parse_diff(raw: str) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    targets: set[str] = set()
    line_keys: set[tuple[str, str, int]] = set()
    current: dict[str, Any] | None = None
    old_line = new_line = 0

    for number, line in enumerate(raw.replace("\r\n", "\n").replace("\r", "\n").split("\n"), 1):
        if line.startswith("diff --git "):
            match = DIFF_RE.match(line)
            if not match:
                raise ReviewError(f"diff line {number}: malformed file header")
            current = {
                "path": match.group(2),
                "additions": 0,
                "deletions": 0,
            }
            files.append(current)
            targets.add(f"file-{slug(current['path'])}")
            continue

        if current is None:
            if line.strip():
                raise ReviewError(f"diff line {number}: content before first file header")
            continue

        if line.startswith("@@"):
            match = HUNK_RE.match(line)
            if not match:
                raise ReviewError(f"diff line {number}: malformed hunk header")
            old_line = int(match.group(1))
            new_line = int(match.group(3))
            continue

        if line.startswith(("index ", "--- ", "+++ ", "new file mode ", "deleted file mode ", "similarity index ", "rename from ", "rename to ")):
            continue

        file_slug = slug(current["path"])
        if line.startswith("+"):
            current["additions"] += 1
            line_keys.add((current["path"], "new", new_line))
            targets.add(f"line-{file_slug}-new-{new_line}")
            new_line += 1
        elif line.startswith("-"):
            current["deletions"] += 1
            line_keys.add((current["path"], "old", old_line))
            targets.add(f"line-{file_slug}-old-{old_line}")
            old_line += 1
        elif line.startswith(" "):
            line_keys.add((current["path"], "old", old_line))
            line_keys.add((current["path"], "new", new_line))
            targets.add(f"line-{file_slug}-old-{old_line}")
            targets.add(f"line-{file_slug}-new-{new_line}")
            old_line += 1
            new_line += 1
        elif line.startswith("\\") or not line:
            continue
        else:
            raise ReviewError(f"diff line {number}: unsupported unified-diff row {line[:40]!r}")

    if not files:
        raise ReviewError("diff contains no files")

    return {
        "files": files,
        "changed_files": len(files),
        "additions": sum(item["additions"] for item in files),
        "deletions": sum(item["deletions"] for item in files),
        "targets": targets,
        "line_keys": line_keys,
    }


def register_id(ids: set[str], item_id: Any, field: str) -> str:
    value = require_string(item_id, field)
    if value in ids:
        raise ReviewError(f"duplicate id {value!r}")
    ids.add(value)
    return value


def validate_links(links: Any, field: str, targets: set[str]) -> None:
    for index, link in enumerate(require_list(links, field)):
        if not isinstance(link, dict):
            raise ReviewError(f"{field}[{index}] must be an object")
        require_string(link.get("label"), f"{field}[{index}].label")
        target = require_string(link.get("target"), f"{field}[{index}].target")
        if target not in targets:
            raise ReviewError(f"{field}[{index}].target references unknown id {target!r}")


def validate_spec(spec: dict[str, Any], diff: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise ReviewError("review spec must be a JSON object")
    if spec.get("version", 1) != 1:
        raise ReviewError("only review spec version 1 is supported")
    require_string(spec.get("title"), "title")

    findings = require_list(spec.get("findings"), "findings")
    flows = require_list(spec.get("flows", []), "flows")
    file_map = require_list(spec.get("file_map", []), "file_map")
    matrix = require_list(spec.get("test_matrix", []), "test_matrix")
    references = require_list(spec.get("references", []), "references")
    code_blocks = require_list(spec.get("code_blocks", []), "code_blocks")

    ids = {
        "review-summary",
        "findings-overview",
        "scope-visual-review",
        "test-matrix",
        "logical-flows",
        "file-map",
        "agent-fix-prompt",
        "references",
        "diff-root",
    }
    ids.update(diff["targets"])

    for index, item in enumerate(findings):
        if not isinstance(item, dict):
            raise ReviewError(f"findings[{index}] must be an object")
        register_id(ids, item.get("id"), f"findings[{index}].id")
    for index, item in enumerate(flows):
        if not isinstance(item, dict):
            raise ReviewError(f"flows[{index}] must be an object")
        register_id(ids, item.get("id"), f"flows[{index}].id")
    for index, item in enumerate(references):
        if not isinstance(item, dict):
            raise ReviewError(f"references[{index}] must be an object")
        register_id(ids, item.get("id"), f"references[{index}].id")
    for index, item in enumerate(code_blocks):
        if not isinstance(item, dict):
            raise ReviewError(f"code_blocks[{index}] must be an object")
        register_id(ids, item.get("id"), f"code_blocks[{index}].id")

    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        severity = require_string(finding.get("severity"), f"{prefix}.severity")
        if severity not in VALID_SEVERITIES:
            raise ReviewError(f"{prefix}.severity must be one of {sorted(VALID_SEVERITIES)}")
        require_string(finding.get("title"), f"{prefix}.title")
        require_string(finding.get("body"), f"{prefix}.body")
        file_path = require_string(finding.get("file"), f"{prefix}.file")
        side = require_string(finding.get("side"), f"{prefix}.side")
        if side not in VALID_SIDES:
            raise ReviewError(f"{prefix}.side must be old or new")
        line = finding.get("line")
        if not isinstance(line, int) or line < 1:
            raise ReviewError(f"{prefix}.line must be a positive integer")
        if (file_path, side, line) not in diff["line_keys"]:
            raise ReviewError(f"{prefix} points outside the diff: {file_path}:{side}:{line}")
        validate_links(finding.get("links", []), f"{prefix}.links", ids)

    for index, flow in enumerate(flows):
        prefix = f"flows[{index}]"
        require_string(flow.get("title"), f"{prefix}.title")
        require_string(flow.get("description", ""), f"{prefix}.description", allow_empty=True)
        for step_index, step in enumerate(require_list(flow.get("steps", []), f"{prefix}.steps")):
            if not isinstance(step, dict):
                raise ReviewError(f"{prefix}.steps[{step_index}] must be an object")
            require_string(step.get("title"), f"{prefix}.steps[{step_index}].title")
            target = require_string(step.get("target"), f"{prefix}.steps[{step_index}].target")
            if target not in ids:
                raise ReviewError(f"{prefix}.steps[{step_index}].target references unknown id {target!r}")

    for index, mapped in enumerate(file_map):
        prefix = f"file_map[{index}]"
        if not isinstance(mapped, dict):
            raise ReviewError(f"{prefix} must be an object")
        require_string(mapped.get("path"), f"{prefix}.path")
        total = mapped.get("total_lines")
        if not isinstance(total, int) or total < 1:
            raise ReviewError(f"{prefix}.total_lines must be a positive integer")
        for marker_index, marker in enumerate(require_list(mapped.get("markers", []), f"{prefix}.markers")):
            marker_prefix = f"{prefix}.markers[{marker_index}]"
            if not isinstance(marker, dict):
                raise ReviewError(f"{marker_prefix} must be an object")
            line = marker.get("line")
            if not isinstance(line, int) or line < 1:
                raise ReviewError(f"{marker_prefix}.line must be a positive integer")
            kind = marker.get("kind", "relevant")
            if kind not in VALID_MARKER_KINDS:
                raise ReviewError(f"{marker_prefix}.kind must be one of {sorted(VALID_MARKER_KINDS)}")
            target = require_string(marker.get("target"), f"{marker_prefix}.target")
            if target not in ids:
                raise ReviewError(f"{marker_prefix}.target references unknown id {target!r}")

    for index, row in enumerate(matrix):
        prefix = f"test_matrix[{index}]"
        if not isinstance(row, dict):
            raise ReviewError(f"{prefix} must be an object")
        require_string(row.get("case"), f"{prefix}.case")
        require_string(row.get("expected"), f"{prefix}.expected")
        require_string(row.get("status"), f"{prefix}.status")
        tone = row.get("tone", "neutral")
        if tone not in VALID_TEST_TONES:
            raise ReviewError(f"{prefix}.tone must be one of {sorted(VALID_TEST_TONES)}")
        file_path = require_string(row.get("file"), f"{prefix}.file")
        side = require_string(row.get("side"), f"{prefix}.side")
        if side not in VALID_SIDES:
            raise ReviewError(f"{prefix}.side must be old or new")
        line = row.get("line")
        if not isinstance(line, int) or line < 1:
            raise ReviewError(f"{prefix}.line must be a positive integer")
        if (file_path, side, line) not in diff["line_keys"]:
            raise ReviewError(f"{prefix} points outside the diff: {file_path}:{side}:{line}")

    for index, reference in enumerate(references):
        prefix = f"references[{index}]"
        require_string(reference.get("path"), f"{prefix}.path")
        require_string(reference.get("summary"), f"{prefix}.summary")
        code = require_string(reference.get("code"), f"{prefix}.code")
        code_lines = code.split("\n")
        highlighted = require_list(reference.get("highlight_lines"), f"{prefix}.highlight_lines")
        if not highlighted:
            raise ReviewError(f"{prefix}.highlight_lines must contain at least one line")
        seen_highlights: set[int] = set()
        for highlight_index, line in enumerate(highlighted):
            if not isinstance(line, int) or isinstance(line, bool) or line < 1:
                raise ReviewError(f"{prefix}.highlight_lines[{highlight_index}] must be a positive integer")
            if line > len(code_lines):
                raise ReviewError(
                    f"{prefix}.highlight_lines[{highlight_index}] points past the {len(code_lines)}-line snippet"
                )
            if line in seen_highlights:
                raise ReviewError(f"{prefix}.highlight_lines contains duplicate line {line}")
            seen_highlights.add(line)
        if min(seen_highlights) == 1 or max(seen_highlights) == len(code_lines):
            raise ReviewError(f"{prefix}.code must include context before and after highlighted lines")
        back_target = reference.get("back_target")
        if back_target is not None and back_target not in ids:
            raise ReviewError(f"{prefix}.back_target references unknown id {back_target!r}")

    for index, block in enumerate(code_blocks):
        prefix = f"code_blocks[{index}]"
        file_path = require_string(block.get("file"), f"{prefix}.file")
        side = require_string(block.get("side"), f"{prefix}.side")
        if side not in VALID_SIDES:
            raise ReviewError(f"{prefix}.side must be old or new")
        start_line = block.get("start_line")
        end_line = block.get("end_line")
        if not isinstance(start_line, int) or isinstance(start_line, bool) or start_line < 1:
            raise ReviewError(f"{prefix}.start_line must be a positive integer")
        if not isinstance(end_line, int) or isinstance(end_line, bool) or end_line < start_line:
            raise ReviewError(f"{prefix}.end_line must be an integer at or after start_line")
        if (file_path, side, start_line) not in diff["line_keys"]:
            raise ReviewError(f"{prefix}.start_line points outside the diff: {file_path}:{side}:{start_line}")
        if (file_path, side, end_line) not in diff["line_keys"]:
            raise ReviewError(f"{prefix}.end_line points outside the diff: {file_path}:{side}:{end_line}")
        heat = require_string(block.get("heat"), f"{prefix}.heat")
        if heat not in VALID_HEAT_LEVELS:
            raise ReviewError(f"{prefix}.heat must be one of {sorted(VALID_HEAT_LEVELS)}")
        require_string(block.get("summary"), f"{prefix}.summary")

    normalized = dict(spec)
    normalized.setdefault("version", 1)
    normalized.setdefault("subtitle", "")
    normalized.setdefault("source_url", "")
    normalized.setdefault("revision", "")
    normalized.setdefault("status", f"{len(findings)} findings")
    normalized.setdefault("summary", "")
    normalized.setdefault("scope", {"in": [], "out": []})
    normalized.setdefault("agent_prompt", "")
    normalized.setdefault("validation_note", "")
    normalized.setdefault("code_blocks", [])
    normalized["derived"] = {
        "changed_files": diff["changed_files"],
        "additions": diff["additions"],
        "deletions": diff["deletions"],
        "files": diff["files"],
        "github_changes_url": github_pr_changes_url(normalized["source_url"]),
        "github_diff_anchors": github_diff_anchors(normalized["source_url"], diff["files"]),
    }
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="review JSON specification")
    parser.add_argument("--diff", type=Path, required=True, help="unified diff")
    parser.add_argument("--output", type=Path, help="output HTML path")
    parser.add_argument("--template", type=Path, help="override HTML template")
    parser.add_argument("--validate-only", action="store_true", help="validate without writing HTML")
    args = parser.parse_args()

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        raw_diff = args.diff.read_text(encoding="utf-8")
        parsed = parse_diff(raw_diff)
        normalized = validate_spec(spec, parsed)
        if args.validate_only:
            print(json.dumps({
                "ok": True,
                "changed_files": parsed["changed_files"],
                "additions": parsed["additions"],
                "deletions": parsed["deletions"],
                "findings": len(normalized["findings"]),
            }))
            return 0
        if args.output is None:
            raise ReviewError("--output is required unless --validate-only is used")
        template = args.template or Path(__file__).resolve().parent.parent / "assets" / "review-template.html"
        html = template.read_text(encoding="utf-8")
        placeholder = "__REVIEW_DATA_JSON__"
        if html.count(placeholder) != 1:
            raise ReviewError(f"template must contain exactly one {placeholder} placeholder")
        payload = dict(normalized)
        payload["diff"] = raw_diff
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        rendered = html.replace(placeholder, encoded)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote {args.output} ({parsed['changed_files']} files, {len(normalized['findings'])} findings)")
        return 0
    except (OSError, json.JSONDecodeError, ReviewError) as exc:
        print(f"visual-review: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
