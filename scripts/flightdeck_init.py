"""flightdeck deck initializer — copy the full-layout scaffold + seed the cockpit.

The mechanical part of preflight Branch-0 first-time-setup: deterministically copy
`scaffolds/full/flightdeck/` into `<target>/flightdeck/` (verbatim — preserves the
`rules.md` comments, which hand re-authoring drops; see the scaffold-ships-verbatim
incident) and substitute the cockpit placeholders. As of 3.0 first-run is zero-prompt:
preflight just detects a runtime and calls this — no git check, interview, or AGENTS.md
question. `--focus`/`--next` default to `(set me)` placeholders the user fills later.

It also silently detects the deck's git mode: if `<target>/.git` exists, the copied
`archive/HISTORY.md` is removed — `git log` is the history for git-backed decks, so the
file is kept only for no-git decks (where it is the git-log substitute). Avoids shipping
a permanently-dead file into every git project.

Post-copy, `docs/INDEX.md` is created if absent — the scaffold predates the docs/ folder
(added in 3.0); this ensures all decks get it without waiting for scaffolds/full update.

Refuses if the deck already exists. Pure stdlib; run with `uv run` or `python`.
"""

import argparse
import datetime
import shutil
import sys
from pathlib import Path

SCAFFOLD = Path(__file__).resolve().parent.parent / "scaffolds" / "full" / "flightdeck"

_ACTIVE = "<ACTIVE_FOCUS — filled by preflight first-time-setup>"
_NEXT = "<FIRST_NEXT_ITEM — filled by preflight first-time-setup>"


def init(target, name, user, date, focus, next_item):
    """Copy the scaffold into <target>/flightdeck/ and seed cockpit.md."""
    deck = Path(target) / "flightdeck"
    if (deck / "cockpit.md").exists():
        raise FileExistsError(f"deck already exists: {deck / 'cockpit.md'}")
    shutil.copytree(SCAFFOLD, deck)

    cockpit = deck / "cockpit.md"
    text = cockpit.read_text(encoding="utf-8")
    text = text.replace("[project name]", name)
    text = text.replace(
        "YYYY-MM-DD by [who] (one-line state)", f"{date} by {user} (deck initialized)"
    )
    text = text.replace(_ACTIVE, focus)
    text = text.replace(_NEXT, next_item)
    cockpit.write_text(text, encoding="utf-8")

    # docs/ is new in 3.0 and not yet in scaffolds/full (Task 5.1 will add it there).
    # Create it here so every initialized deck gets the folder immediately.
    docs_index = deck / "docs" / "INDEX.md"
    if not docs_index.exists():
        docs_index.parent.mkdir(parents=True, exist_ok=True)
        docs_index.write_text(
            "# docs INDEX\n\n_Reference documentation and write-ups._\n\n| File | Summary |\n|------|---------||\n",
            encoding="utf-8",
        )

    # HISTORY.md is the no-git history substrate (the git-log stand-in). A git-backed
    # deck uses `git log` instead, so drop the copied file — keeping it would be a
    # permanently-dead file. It survives only for no-git decks.
    # NOTE: scaffold still uses `archive/` name; Task 5.1 renames scaffolds/full.
    # Until then we handle both old (landed/) and new (archive/) locations.
    if (Path(target) / ".git").exists():
        (deck / "archive" / "HISTORY.md").unlink(missing_ok=True)
        (deck / "landed" / "HISTORY.md").unlink(missing_ok=True)

    return deck


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Scaffold a flightdeck deck (full layout + 3-file contract)."
    )
    ap.add_argument("target", nargs="?", default=".", help="project dir (deck created at <target>/flightdeck/)")
    ap.add_argument("--name", help="project name for the cockpit header (default: target dir name)")
    ap.add_argument("--user", default="unknown", help="author name for 'Last updated'")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")
    ap.add_argument("--focus", default="(set me)", help="cockpit Active focus")
    ap.add_argument("--next", dest="next_item", default="(set me)", help="first Next-session item")
    args = ap.parse_args(argv)

    name = args.name or Path(args.target).resolve().name
    date = args.date or datetime.date.today().isoformat()
    try:
        deck = init(args.target, name, args.user, date, args.focus, args.next_item)
    except FileExistsError as e:
        print(f"refused: {e}")
        return 2
    print(f"created deck at {deck} (full layout, 3-file contract)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
