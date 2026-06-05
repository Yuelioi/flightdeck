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
    "chart": "references",
    "doc": "docs",
}
WORKFLOW = {"spec", "plan"}
KNOWLEDGE = {"incident", "checklist", "chart", "doc"}
DATELESS = {"doc"}   # always <slug>.md, never date-prefixed (standing reference)
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
_DEFAULT_STATUS = {
    "spec": "idea", "plan": "idea",
    "incident": "active", "checklist": "active", "chart": "active", "doc": "active",
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
        if summary:
            lines.append(f"summary: {summary}")
        lines.append(f"when_to_read: {when_to_read}")
        lines.append(f"applies_to: [{', '.join(applies_to)}]")
        lines.append(f"last_updated: {date}")
        if kind == "incident":
            lines.append("resolved_by:")     # 空=未根治；填 commit/test = 退役依据
    lines.append("---")
    return "\n".join(lines)


_INCIDENT_BODY = """# {title}

## Signature
- symptom: `<报错原文 / 可观测症状>`
- error_type: <异常类型/错误码 或 —>
- where: <函数/文件/子系统>
- trigger: <什么动作/场景引发>

## 症状/复现

## 根因

## 修法

## Cases
- {date_placeholder} 首次
"""


def _body_scaffold(kind, title):
    if kind == "incident":
        return _INCIDENT_BODY.format(title=title, date_placeholder="YYYY-MM-DD")
    return f"# {title}\n"


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
    if kind in WORKFLOW and not summary:
        raise ValueError(f"{kind} requires --summary (drives the INDEX row; required by flightdeck_index)")
    if kind in KNOWLEDGE and (not when_to_read or not applies_to):
        raise ValueError(f"{kind} requires --when-to-read and --applies-to (required routing fields)")
    if implements and kind not in WORKFLOW:
        raise ValueError(f"--implements is workflow-only; not valid for kind {kind!r}")

    date = date or datetime.date.today().isoformat()
    status = status or _DEFAULT_STATUS[kind]

    folder = Path(deck) / KIND_FOLDER[kind]
    filename = f"{slug}.md" if (status == "idea" or kind in DATELESS) else f"{date}-{slug}.md"
    path = folder / filename
    if path.exists():
        raise FileExistsError(f"artifact already exists: {path}")

    fm = _frontmatter(kind, status, date, summary, implements, when_to_read, applies_to)
    body = _body_scaffold(kind, title)
    path.write_text(f"{fm}\n\n{body}", encoding="utf-8")

    if regen:
        flightdeck_index.main([str(deck)])
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Create a new flightdeck deck artifact (frontmatter + naming + INDEX/cockpit regen)."
    )
    ap.add_argument("deck", help="path to the flightdeck/ deck root")
    ap.add_argument("kind", choices=sorted(KIND_FOLDER))
    ap.add_argument("--slug", required=True, help="filename slug: ^[a-z0-9-]+$")
    ap.add_argument("--title", required=True, help="human title (becomes the H1)")
    ap.add_argument("--status", default=None,
                    choices=["idea", "active", "done", "obsolete", "superseded"])
    ap.add_argument("--summary", default="", help="one-line gist (drives the INDEX row)")
    ap.add_argument("--implements", default=None, help="workflow only: specs/<x>.md")
    ap.add_argument("--when-to-read", dest="when_to_read", default=None)
    ap.add_argument("--applies-to", dest="applies_to", default=None, help="comma-separated tags")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (default: today; override for backfill)")
    args = ap.parse_args(argv)

    applies = [t.strip() for t in args.applies_to.split(",")] if args.applies_to else None
    try:
        path = new(args.deck, args.kind, slug=args.slug, title=args.title,
                   status=args.status, summary=args.summary, implements=args.implements,
                   when_to_read=args.when_to_read, applies_to=applies, date=args.date)
    except (ValueError, FileExistsError) as e:
        print(f"refused: {e}")
        return 2

    status = args.status or _DEFAULT_STATUS[args.kind]
    print(f"created {args.kind} at {path}")
    if args.kind in WORKFLOW and status == "idea":
        print("INDEX updated; cockpit unchanged (status=idea)")
    elif args.kind in WORKFLOW:
        print("INDEX + cockpit (## 进行中) updated")
    else:
        print("folder INDEX updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
