"""flightdeck deck initializer — copy the full-layout scaffold + seed the cockpit.

The mechanical part of preflight Branch-0 first-time-setup: deterministically copy
`scaffolds/full/flightdeck/` into `<target>/flightdeck/` (verbatim — preserves the
`rules.md` comments, which hand re-authoring drops; see the scaffold-ships-verbatim
incident) and substitute the cockpit placeholders. As of 3.0 first-run is zero-prompt:
preflight just detects a runtime and calls this — no git check, interview, or AGENTS.md
question. `--focus`/`--next` default to `(set me)` placeholders the user fills later.

flightdeck keeps **no history-log file** under any git mode: the landing record is the
moved files in `archive/` (+ `git log` on git-backed decks). `archive/` itself is created
on demand at first land, so the scaffold ships no `archive/` and init writes no log.

Refuses if the deck already exists. Pure stdlib; run with `uv run` or `python`.
"""

import argparse
import datetime
import shutil
import sys
from pathlib import Path

SCAFFOLD = Path(__file__).resolve().parent.parent / "scaffolds" / "full" / "flightdeck"

_ACTIVE = "<FOCUS — one coarse thread label + spec/plan link, filled by preflight first-time-setup>"
_NEXT = "<FIRST_NEXT_ITEM — single concrete action + plan link, filled by preflight first-time-setup>"


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
        "YYYY-MM-DD · [who] · Stage: <lifecycle stage>",
        f"{date} · {user} · Stage: deck initialized",
    )
    text = text.replace(_ACTIVE, focus)
    text = text.replace(_NEXT, next_item)
    cockpit.write_text(text, encoding="utf-8")

    return deck


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Scaffold a flightdeck deck (full layout + 2-file contract)."
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
    print(f"created deck at {deck} (full layout, 2-file contract)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
