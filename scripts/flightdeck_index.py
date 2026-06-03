"""flightdeck mechanical layer — INDEX regeneration (pure stdlib).

See flightdeck/sketches/scriptable-mechanical-layer.md for the design.
Computes facts (regenerate INDEX from deck files); judgment stays in the model.
"""

import argparse
import sys
from pathlib import Path

DASH = "—"  # em dash — the INDEX row delimiter

SUMMARY_KINDS = {"specs", "plans", "sketches"}
KNOWLEDGE_KINDS = {"checklists", "incidents"}

# Canonical root-INDEX folder order (not alphabetical — a designed reading order).
FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "charts", "debriefs", "sketches"]


def format_row(kind, filename, fm):
    """Render one folder-INDEX row for an artifact, by folder kind."""
    link = f"- [{filename}]({filename})"
    if kind in SUMMARY_KINDS:
        return f"{link} {DASH} {fm['status']} {DASH} {fm['summary']}"
    if kind in KNOWLEDGE_KINDS:
        return (
            f"{link} {DASH} {fm['status']} {DASH} "
            f"when_to_read: {fm['when_to_read']} {DASH} applies_to: {fm['applies_to']}"
        )
    if kind == "debriefs":
        return (
            f"{link} {DASH} {fm['status']} {DASH} "
            f"reviewed: {fm['reviewed']} {DASH} {fm['last_updated']}"
        )
    raise ValueError(f"unknown folder kind: {kind}")


def parse_frontmatter(text):
    """Parse a leading `---`-fenced frontmatter block into a dict.

    Only the flightdeck subset is supported: one `key: value` per line.
    Returns {} when no frontmatter block is present.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


AUTO_END = "<!-- /AUTO -->"


def replace_auto_block(text, new_block):
    """Swap the single `<!-- AUTO:* -->…<!-- /AUTO -->` region, keeping the rest."""
    start = text.index("<!-- AUTO:")
    end = text.index(AUTO_END) + len(AUTO_END)
    return text[:start] + new_block + text[end:]


def folder_summary(folder):
    """`<count> <status>` for a deck folder's root-INDEX row.

    Status is the shared `status:` across artifacts, or "mixed" if they differ.
    """
    folder = Path(folder)
    names = [p for p in folder.glob("*.md") if p.name != "INDEX.md"]
    statuses = {
        parse_frontmatter(p.read_text(encoding="utf-8")).get("status", "")
        for p in names
    }
    descriptor = statuses.pop() if len(statuses) == 1 else "mixed"
    return f"{len(names)} {descriptor}"


def charts_summary(folder):
    """charts/ is hand-maintained external imports; summarise by entry count."""
    idx = (Path(folder) / "INDEX.md").read_text(encoding="utf-8")
    start = idx.index("<!-- AUTO:")
    end = idx.index(AUTO_END)
    n = sum(1 for line in idx[start:end].splitlines() if line.startswith("- "))
    return f"{n} project imported"


def regen_root_index(deck):
    """Regenerate the root `<!-- AUTO:root -->` block (one row per folder)."""
    deck = Path(deck)
    rows = []
    for name in FOLDER_ORDER:
        folder = deck / name
        if not folder.is_dir():
            continue
        summ = charts_summary(folder) if name == "charts" else folder_summary(folder)
        rows.append(f"- {name}/ {DASH} {summ}")
    body = "\n".join(rows)
    return f"<!-- AUTO:root -->\n{body}\n{AUTO_END}"


def regen_folder_index(folder):
    """Regenerate the `<!-- AUTO:<kind> -->` block for one deck folder.

    Rows are ordered alphabetically by filename (the canonical order; the
    pre-script hand-append order is NOT reproducible from the filesystem).
    """
    folder = Path(folder)
    kind = folder.name
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    rows = [
        format_row(kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8")))
        for name in names
    ]
    body = "\n".join(rows)
    return f"<!-- AUTO:{kind} -->\n{body}\n{AUTO_END}"


# charts/ folder INDEX is hand-maintained (external imports); only its root row is derived.
REGEN_FOLDERS = [name for name in FOLDER_ORDER if name != "charts"]


def _index_targets(deck):
    """Yield (label, index_path, new_block) for every regenerable INDEX."""
    deck = Path(deck)
    for name in REGEN_FOLDERS:
        folder = deck / name
        if folder.is_dir():
            yield name, folder / "INDEX.md", regen_folder_index(folder)
    yield "root", deck / "INDEX.md", regen_root_index(deck)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Regenerate flightdeck INDEX AUTO blocks from artifact frontmatter."
    )
    ap.add_argument("deck", help="path to the flightdeck/ deck root")
    ap.add_argument(
        "--check",
        action="store_true",
        help="report drift and write nothing; exit 1 if any INDEX is stale",
    )
    args = ap.parse_args(argv)

    drift = []
    for label, path, new_block in _index_targets(args.deck):
        current = path.read_text(encoding="utf-8")
        cur_block = current[current.index("<!-- AUTO:") : current.index(AUTO_END) + len(AUTO_END)]
        if cur_block == new_block:
            continue
        drift.append(label)
        if not args.check:
            path.write_text(replace_auto_block(current, new_block), encoding="utf-8")

    if args.check:
        print("DRIFT: " + ", ".join(drift) if drift else "clean")
        return 1 if drift else 0
    print("regenerated: " + ", ".join(drift) if drift else "already clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
