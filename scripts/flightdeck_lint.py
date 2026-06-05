"""flightdeck mechanical layer — lint (pure stdlib).

Runs the deterministic, mechanical subset of the walkaround audit and emits
findings as JSON for the model to read and narrate. Covered audits (the
"compute facts" half — see the operation inventory in
flightdeck/specs/2026-06-03-scriptable-mechanical-layer-design.md):

  - status legality        (walkaround Audit 1)
  - orphan plan            (walkaround Audit 4)
  - INDEX ↔ folder drift   (walkaround Audit 5, reuses flightdeck_index)
  - dangling references    (walkaround Audit 7)
  - stray files            (walkaround Audit 8, conservative subset)

Judgment-bearing audits (knowledge classification, migration decisions,
AGENTS.md semantic drift, the full stray-file reachability call) stay in the
model — the script never decides, only reports.

Runnable as `uv run flightdeck_lint.py <deck>` or `python flightdeck_lint.py <deck>`
— pure stdlib, so uv has nothing to install.
"""

# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import argparse
import json
import re
import sys
from pathlib import Path

import flightdeck_index
from flightdeck_index import (
    KNOWLEDGE_KINDS,
    IMPORTED_KINDS,
    NESTABLE_KINDS,
    parse_frontmatter,
)

# Legal status values per artifact kind (model-v4 §1; mirrors walkaround Audit 1).
WORKFLOW_STATUSES = {"idea", "active", "done"}
KNOWLEDGE_STATUSES = {"active", "obsolete", "superseded"}

WORKFLOW_FOLDERS = ("specs", "plans")
# KNOWLEDGE_KINDS = {"checklists", "incidents", "docs"}  — from flightdeck_index
# IMPORTED_KINDS  = {"references"}                       — from flightdeck_index
# NESTABLE_KINDS  = {"incidents", "checklists", "docs", "references"} — from flightdeck_index
KNOWLEDGE_FOLDERS = tuple(KNOWLEDGE_KINDS)
KNOWN_FOLDERS = {"specs", "plans"} | KNOWLEDGE_KINDS | IMPORTED_KINDS | {"archive"}
KNOWN_ROOT_FILES = {"cockpit.md", "INDEX.md", "rules.md"}

# structural-edit guard — required structural blocks per known file (label, regex).
# A multi-line Edit whose old_string spans a heading can silently drop it; no
# link/anchor check catches a *missing* heading. Scope is deliberately narrow
# (cockpit.md only): its blocks anchor the landing/status AUTO regen, so dropping
# one breaks regeneration — the highest-value, lowest-false-positive case. The
# list mirrors the canonical cockpit.md template (preflight/templates.md), minus
# any deck-specific section (e.g. dogfood's `## Note on dogfooding`).
REQUIRED_SECTIONS = {
    "cockpit.md": [
        ("## 进行中", re.compile(r"(?m)^##\s+进行中\s*$")),
        ("<!-- AUTO:inprogress -->", re.compile(r"<!--\s*AUTO:inprogress\s*-->")),
        ("<!-- /AUTO -->", re.compile(r"<!--\s*/AUTO\s*-->")),
        ("## 下一步", re.compile(r"(?m)^##\s+下一步\s*$")),
        ("## Hanging tasks", re.compile(r"(?m)^##\s+Hanging tasks\s*$")),
    ],
}

# `[text](target)` — capture the target only; titles/spaces handled by the caller.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Fenced code blocks (``` or ~~~, matched run length) and inline code spans.
# Stripped before link extraction so prose *examples* of link syntax aren't
# mistaken for real cross-references.
FENCE_RE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$")
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")


def _strip_code(text):
    """Remove fenced code blocks and inline code spans from markdown text."""
    text = FENCE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def _finding(audit, severity, path, message):
    return {"audit": audit, "severity": severity, "path": str(path), "message": message}


def _artifact_files(folder):
    """Top-level *.md in a folder, excluding INDEX.md (no recursion).

    Non-recursive on purpose: `references/` may hold imported external project
    trees whose nested files are not flightdeck artifacts (walkaround Audit 1).
    NESTABLE_KINDS (incidents/checklists/docs/references) may have <area>/
    sub-directories — only the top-level *.md are treated as artifacts.
    """
    return sorted(p for p in folder.glob("*.md") if p.name != "INDEX.md")


def audit_status(deck):
    """Audit 1 — every active-tree artifact must carry a legal `status`."""
    deck = Path(deck)
    findings = []
    for folders, legal in (
        (WORKFLOW_FOLDERS, WORKFLOW_STATUSES),
        (KNOWLEDGE_FOLDERS, KNOWLEDGE_STATUSES),
    ):
        for name in folders:
            folder = deck / name
            if not folder.is_dir():
                continue
            for f in _artifact_files(folder):
                status = parse_frontmatter(f.read_text(encoding="utf-8")).get("status")
                if not status:
                    findings.append(
                        _finding("status", "CRITICAL", f, f"{name}/{f.name} missing required `status`")
                    )
                elif status not in legal:
                    findings.append(
                        _finding(
                            "status",
                            "WARNING",
                            f,
                            f"{name}/{f.name} has illegal status `{status}` (legal: {sorted(legal)})",
                        )
                    )
    return findings


def audit_orphan_plans(deck):
    """Audit 4 — a plan with no `implements:` is an INFO nudge."""
    deck = Path(deck)
    folder = deck / "plans"
    if not folder.is_dir():
        return []
    findings = []
    for f in _artifact_files(folder):
        if not parse_frontmatter(f.read_text(encoding="utf-8")).get("implements"):
            findings.append(
                _finding(
                    "orphan-plan",
                    "INFO",
                    f,
                    f"plans/{f.name} has no `implements:` — link a spec or confirm standalone",
                )
            )
    return findings


def _drift_target_path(deck, label):
    """Map an index_drift label to the file it names."""
    if label == "root":
        return deck / "INDEX.md"
    if label == "cockpit":
        return deck / "cockpit.md"
    return deck / label / "INDEX.md"  # a folder INDEX


def audit_index_consistency(deck):
    """Audit 5 — INDEX AUTO blocks must match the artifact frontmatter."""
    deck = Path(deck)
    return [
        _finding(
            "index-consistency",
            "WARNING",
            _drift_target_path(deck, label),
            f"INDEX drift: `{label}` is stale — regenerate with flightdeck_index.py",
        )
        for label in flightdeck_index.index_drift(deck)
    ]


def _clean_target(target):
    """Normalise a markdown link target for filesystem resolution.

    Returns the path part (fragment stripped, angle-brackets removed) or None
    when the link is not a resolvable local path (URL, anchor-only, absolute).
    """
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if target.startswith("#"):
        return None
    if "://" in target or target.startswith("mailto:"):
        return None
    if target.startswith("/"):
        return None
    path_part = target.split("#", 1)[0].strip()
    # a markdown link may carry a title: (path "title") — drop it
    if " " in path_part:
        path_part = path_part.split(" ", 1)[0]
    return path_part or None


def audit_dangling_refs(md_files):
    """Audit 7 — every relative `[text](path)` link must resolve to a file."""
    findings = []
    for f in md_files:
        f = Path(f)
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for raw in LINK_RE.findall(_strip_code(text)):
            path_part = _clean_target(raw)
            if path_part is None:
                continue
            if not (f.parent / path_part).exists():
                findings.append(
                    _finding("dangling-ref", "CRITICAL", f, f"{f.name} -> {raw.strip()} (target file missing)")
                )
    return findings


def audit_stray(deck):
    """Audit 8 (conservative subset) — unknown dirs / unreachable root .md.

    Only the unambiguous, low-false-positive cases: an unknown top-level
    directory, and a root-level `.md` that is neither a known entry file nor
    linked from one. The fuzzier sub-checks (stray files inside known folders,
    non-.md assets) are left to the model — they need judgment.

    NESTABLE_KINDS (incidents/checklists/docs/references) may contain <area>/
    sub-directories as organisational partitions — those subdirs are not stray.
    """
    deck = Path(deck)
    linked = set()
    for name in KNOWN_ROOT_FILES:
        entry = deck / name
        if not entry.is_file():
            continue
        for raw in LINK_RE.findall(entry.read_text(encoding="utf-8")):
            path_part = _clean_target(raw)
            if path_part:
                linked.add((entry.parent / path_part).resolve())
    findings = []
    for child in sorted(deck.iterdir()):
        if child.is_dir():
            if child.name not in KNOWN_FOLDERS:
                findings.append(
                    _finding("stray", "WARNING", child, f"unknown directory `{child.name}/` under deck root")
                )
            else:
                # For nestable kinds, check their immediate subdirectories:
                # <area>/ subdirs are legitimate organisational partitions, not stray.
                if child.name in NESTABLE_KINDS:
                    for sub in sorted(child.iterdir()):
                        if sub.is_dir():
                            # area partition — skip (not stray)
                            pass
                        # files inside nestable folders are handled by audit_status
        elif child.suffix == ".md" and child.name not in KNOWN_ROOT_FILES:
            if child.resolve() in linked:
                continue
            findings.append(
                _finding("stray", "WARNING", child, f"orphan `{child.name}` at deck root — link from an entry or remove")
            )
    return findings


def audit_required_structure(deck):
    """structural-edit guard — assert known files still carry their required
    structural blocks (REQUIRED_SECTIONS). Catches the "silent structure loss"
    a multi-line Edit causes when its old_string swallows a heading / AUTO
    anchor and the new_string fails to restore it. A missing file is skipped
    (deckless / not-yet-created is handled elsewhere).
    """
    deck = Path(deck)
    findings = []
    for filename, blocks in REQUIRED_SECTIONS.items():
        f = deck / filename
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        for label, pattern in blocks:
            if not pattern.search(text):
                findings.append(
                    _finding(
                        "required-structure",
                        "CRITICAL",
                        f,
                        f"{filename} missing required block `{label}` — a multi-line Edit may have dropped it",
                    )
                )
    return findings


def _collect_md(deck, repo_root):
    """Markdown files for the dangling-ref scan: deck active tree + repo-root top level.

    `archive/` is excluded (history is not held to current-state rules), matching
    the general walkaround "don't audit archive/" principle.
    """
    deck = Path(deck)
    files = [p for p in deck.rglob("*.md") if "archive" not in p.relative_to(deck).parts]
    if repo_root is not None:
        files += list(Path(repo_root).glob("*.md"))
    return files


def lint(deck, repo_root=None):
    """Run every mechanical audit and return the aggregated findings list."""
    deck = Path(deck)
    findings = []
    findings += audit_status(deck)
    findings += audit_required_structure(deck)
    findings += audit_orphan_plans(deck)
    if (deck / "INDEX.md").is_file():
        findings += audit_index_consistency(deck)
    findings += audit_dangling_refs(_collect_md(deck, repo_root))
    findings += audit_stray(deck)
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Lint a flightdeck deck; emit the mechanical-audit findings as JSON."
    )
    ap.add_argument("deck", help="path to the flightdeck/ deck root")
    ap.add_argument(
        "--repo-root",
        default=None,
        help="repo root whose top-level *.md are also scanned for dangling refs "
        "(default: the deck's parent directory)",
    )
    args = ap.parse_args(argv)

    deck = Path(args.deck)
    repo_root = Path(args.repo_root) if args.repo_root else deck.parent
    findings = lint(deck, repo_root=repo_root)
    print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    blocking = any(f["severity"] in ("CRITICAL", "WARNING") for f in findings)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
