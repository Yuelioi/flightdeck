"""flightdeck_migrate.py — one-time 3.0 → new-form deck migrator (throwaway).

Mechanical pass only: classify each artifact by folder + status, move it to the new
layout (project work/ + knowledge/, cold ~/.flightdeck), drop INDEX files, strip
frontmatter. The semantic pass — synthesizing routing headers, regrouping knowledge
by domain, reshaping cockpit.md — is the AI's job, not this script.

Run-once-and-discard: once the 3.0 layout is gone the script has no use, so it is
Python-only (no js parity) and lives outside the maintained dual-impl set.

Discipline: destructive (mv/rm) → run `--check` first (writes nothing, lists the plan)
and leave a git commit before applying. Pure stdlib.
"""

import argparse
import re
import sys
from collections import namedtuple
from pathlib import Path

KNOWLEDGE_FOLDERS = ("checklists", "docs", "incidents", "references")
SOURCE_FOLDERS = ("specs", "plans", *KNOWLEDGE_FOLDERS, "archive")
_FIELD_RE = re.compile(r"^[A-Za-z0-9_-]+:")
_STATUS_RE = re.compile(r"^status:\s*(\S+)")

# A single planned operation. action ∈ {"move", "delete"}; dst is None for deletes.
Move = namedtuple("Move", "src action dst")


def _status(text):
    """Read the `status:` field from a leading frontmatter block, or None."""
    if not text.startswith("---"):
        return None
    for line in text.split("\n")[1:]:
        if line.strip() == "---":
            break
        m = _STATUS_RE.match(line)
        if m:
            return m.group(1)
    return None


def plan_moves(deck, cold_root, project):
    """Compute every planned move/delete for a 3.0 deck — pure, writes nothing.

    work/ + knowledge/ land under the project deck; cold-archive/cold-ideas land
    under cold_root/projects/<project>/. INDEX.md files are deleted. cockpit.md and
    rules.md (deck root) are never touched.
    """
    deck = Path(deck)
    cold_proj = Path(cold_root) / "projects" / project
    dest_root = {
        "work": deck / "work",
        "knowledge": deck / "knowledge",
        "cold-archive": cold_proj / "archive",
        "cold-ideas": cold_proj / "ideas",
    }
    moves = []
    for folder in SOURCE_FOLDERS:
        fdir = deck / folder
        if not fdir.is_dir():
            continue
        for src in sorted(fdir.glob("*.md")):
            if src.name == "INDEX.md":
                moves.append(Move(src, "delete", None))
                continue
            bucket = classify(folder, _status(src.read_text(encoding="utf-8")))
            moves.append(Move(src, "move", dest_root[bucket] / src.name))
    return moves


def migrate(deck, cold_root, project, check=False):
    """Run the mechanical migration. With check=True, only plan (write nothing).

    A move strips the moved file's frontmatter en route (the new form has none);
    a delete removes an INDEX.md. cockpit.md / rules.md are never in the plan.
    Returns the move plan either way.
    """
    moves = plan_moves(deck, cold_root, project)
    if check:
        return moves
    for m in moves:
        if m.action == "delete":
            m.src.unlink()
        else:
            m.dst.parent.mkdir(parents=True, exist_ok=True)
            body = strip_frontmatter(m.src.read_text(encoding="utf-8"))
            m.dst.write_text(body, encoding="utf-8")
            m.src.unlink()
    return moves


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="One-time 3.0 → new-form deck migrator (mechanical pass only). "
        "Run --check first and commit before applying — the moves are destructive."
    )
    ap.add_argument("deck", help="path to the flightdeck/ deck root")
    ap.add_argument("--check", action="store_true",
                    help="dry-run: print the move plan, write nothing")
    ap.add_argument("--cold-root", default=str(Path.home() / ".flightdeck"),
                    help="cold store root (default: ~/.flightdeck)")
    ap.add_argument("--project", default=None,
                    help="project name under cold-root/projects/ (default: deck's parent dir)")
    args = ap.parse_args(argv)

    deck = Path(args.deck)
    project = args.project or deck.resolve().parent.name
    moves = migrate(deck, args.cold_root, project, check=args.check)

    verb = "would " if args.check else ""
    for m in moves:
        if m.action == "delete":
            print(f"{verb}delete {m.src}")
        else:
            print(f"{verb}move   {m.src} -> {m.dst}")
    tail = " (dry-run, nothing written)" if args.check else ""
    print(f"--- {len(moves)} operation(s){tail}")
    return 0


def strip_frontmatter(text):
    """Drop a leading YAML frontmatter block; leave a frontmatter-less doc unchanged.

    Only the FIRST `---`…`---` block at the top is removed, and only when the line
    after the opening fence looks like a `key:` field — so a doc that opens with a
    horizontal rule, or a body `---` rule, is preserved.
    """
    lines = text.split("\n")
    if len(lines) >= 2 and lines[0].strip() == "---" and _FIELD_RE.match(lines[1]):
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


def classify(folder, status):
    """Return the destination bucket for an artifact given its source folder + status.

    Buckets: 'work' (live), 'knowledge' (resident), 'cold-archive', 'cold-ideas'.
    """
    if folder in KNOWLEDGE_FOLDERS:
        return "knowledge"
    if folder == "archive":
        return "cold-archive"
    if folder in ("specs", "plans"):
        if status == "active":
            return "work"
        if status == "idea":
            return "cold-ideas"
        if status == "done":
            return "cold-archive"
    raise ValueError(f"cannot classify folder={folder!r} status={status!r}")


if __name__ == "__main__":
    sys.exit(main())
