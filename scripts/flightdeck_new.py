"""flightdeck_new.py — create a new deck artifact with correct frontmatter + naming + regen.

The mechanical "authoring entry": instead of an agent re-deriving where a spec/plan/
incident/checklist/chart goes, what frontmatter it needs, and remembering to regen the
INDEX/cockpit, this stamps it deterministically. Mirrors flightdeck_init.py. Pure stdlib.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

import flightdeck_index  # sibling in scripts/; reused for regen after create

KIND_FOLDER = {
    "spec": "specs",
    "plan": "plans",
    "incident": "incidents",
    "checklist": "checklists",
    "chart": "charts",
}
WORKFLOW = {"spec", "plan"}
KNOWLEDGE = {"incident", "checklist", "chart"}
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
_DEFAULT_STATUS = {
    "spec": "idea", "plan": "idea",
    "incident": "active", "checklist": "active", "chart": "active",
}


def _frontmatter(kind, status, date, summary, implements, when_to_read, applies_to):
    lines = ["---", f"status: {status}"]
    if kind in WORKFLOW:
        if summary:
            lines.append(f"summary: {summary}")
        if status != "idea":            # idea-stage workflow omits last_updated (convention)
            lines.append(f"last_updated: {date}")
        if implements:
            lines.append(f"implements: {implements}")
    else:                               # knowledge — routing fields required
        lines.append(f"when_to_read: {when_to_read}")
        lines.append(f"applies_to: [{', '.join(applies_to)}]")
        lines.append(f"last_updated: {date}")
    lines.append("---")
    return "\n".join(lines)


def new(deck, kind, slug, title, status=None, summary="", implements=None,
        when_to_read=None, applies_to=None, date=None, regen=True):
    """Create one deck artifact; return its Path. Raises ValueError/FileExistsError."""
    if kind not in KIND_FOLDER:
        raise ValueError(f"unknown kind: {kind!r} (one of: {', '.join(sorted(KIND_FOLDER))})")
    if not slug or not SLUG_RE.match(slug):
        raise ValueError(
            f"illegal slug: {slug!r} — must match ^[a-z0-9-]+$ "
            "(lowercase ascii / digits / hyphens, e.g. new-artifact-entrypoint)"
        )
    if not title:
        raise ValueError("title is required")
    if kind in KNOWLEDGE and (not when_to_read or not applies_to):
        raise ValueError(f"{kind} requires --when-to-read and --applies-to (required routing fields)")
    if implements and kind not in WORKFLOW:
        raise ValueError(f"--implements is workflow-only; not valid for kind {kind!r}")

    date = date or datetime.date.today().isoformat()
    status = status or _DEFAULT_STATUS[kind]

    folder = Path(deck) / KIND_FOLDER[kind]
    filename = f"{slug}.md" if status == "idea" else f"{date}-{slug}.md"
    path = folder / filename
    if path.exists():
        raise FileExistsError(f"artifact already exists: {path}")

    fm = _frontmatter(kind, status, date, summary, implements, when_to_read, applies_to)
    path.write_text(f"{fm}\n\n# {title}\n", encoding="utf-8")

    if regen:
        flightdeck_index.main([str(deck)])
    return path
