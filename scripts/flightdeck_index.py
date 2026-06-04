"""flightdeck mechanical layer — INDEX regeneration (pure stdlib).

See flightdeck/specs/2026-06-03-scriptable-mechanical-layer-design.md for the design.
Computes facts (regenerate INDEX from deck files); judgment stays in the model.

Runnable as `uv run flightdeck_index.py <deck>` or `python flightdeck_index.py <deck>`
— pure stdlib, so uv has nothing to install.
"""

# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import argparse
import sys
from collections import Counter
from pathlib import Path

# Workflow status lifecycle order — drives the mixed-status root summary breakdown.
STATUS_ORDER = ["idea", "active", "done", "scrapped"]

DASH = "—"  # em dash — the INDEX row delimiter

SUMMARY_KINDS = {"specs", "plans"}
KNOWLEDGE_KINDS = {"checklists", "incidents"}

# Canonical root-INDEX folder order (not alphabetical — a designed reading order).
FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "charts"]


def format_row(kind, filename, fm):
    """Render one folder-INDEX row for an artifact, by folder kind.

    Missing required fields are rendered with a visible sentinel rather than
    raising, so a malformed file never crashes a regen (it is surfaced as a
    `malformed` verdict by `layout_verdict` instead).
    """
    link = f"- [{filename}]({filename})"
    status = fm.get("status", "?")
    if kind in SUMMARY_KINDS:
        return f"{link} {DASH} {status} {DASH} {fm.get('summary', '⚠ summary 缺失')}"
    if kind in KNOWLEDGE_KINDS:
        row = (
            f"{link} {DASH} {status} {DASH} "
            f"when_to_read: {fm.get('when_to_read', '⚠ 缺失')} {DASH} "
            f"applies_to: {fm.get('applies_to', '[]')}"
        )
        # incidents carry a recurrence counter; surface it in the catalog row when
        # it has fired (>1) so the promotion gate is visible without opening the file.
        if kind == "incidents":
            try:
                n = int(fm.get("recurrences", "1"))
            except (TypeError, ValueError):
                n = 1
            if n > 1:
                row += f" {DASH} recur: {n}"
        return row
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

    In `specs/`, `scrapped` files are skipped (model-v4 §1.4): they stay on disk
    but never show in the specs INDEX, so the root count must match the visible
    rows and exclude them too.
    """
    folder = Path(folder)
    names = [p for p in folder.glob("*.md") if p.name != "INDEX.md"]
    statuses = [
        parse_frontmatter(p.read_text(encoding="utf-8")).get("status", "")
        for p in names
    ]
    if folder.name == "specs":
        statuses = [s for s in statuses if s != "scrapped"]
    total = len(statuses)
    if total == 0:
        return "0"
    if len(set(statuses)) == 1:
        return f"{total} {statuses[0]}"
    counts = Counter(statuses)
    ordered = [s for s in STATUS_ORDER if counts.get(s)]
    ordered += [s for s in counts if s not in STATUS_ORDER]  # unknown statuses last
    parts = ", ".join(f"{counts[s]} {s}" for s in ordered)
    return f"{total} ({parts})"


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

    Most folders list rows alphabetically by filename (the canonical order; the
    pre-script hand-append order is NOT reproducible from the filesystem).

    `specs/` is special (model-v4 §1.4): idea files are timeless (no date
    prefix) and would sort badly mixed with the dated active/done files, so the
    block is split into two in-AUTO subgroups — `### 待启动（idea）` (idea,
    alphabetical) and `### 进行中·完成（active·done）` (active/done, by filename
    date descending). `scrapped` files stay on disk but never appear (they must
    not pollute the to-start pool, and the root count excludes them too).
    """
    folder = Path(folder)
    kind = folder.name
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    if kind == "specs":
        return f"<!-- AUTO:{kind} -->\n{_specs_grouped_body(folder, names)}\n{AUTO_END}"
    rows = [
        format_row(kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8")))
        for name in names
    ]
    body = "\n".join(rows)
    return f"<!-- AUTO:{kind} -->\n{body}\n{AUTO_END}"


def _specs_grouped_body(folder, names):
    """Render the specs AUTO body as status-grouped subsections (see caller)."""
    fms = {name: parse_frontmatter((folder / name).read_text(encoding="utf-8")) for name in names}
    ideas = [n for n in names if fms[n].get("status") == "idea"]
    active_done = [n for n in names if fms[n].get("status") in ("active", "done")]
    ideas.sort()  # idea: alphabetical (timeless, no date prefix)
    active_done.sort(reverse=True)  # active/done: filename date descending
    groups = []
    if ideas:
        rows = "\n".join(format_row("specs", n, fms[n]) for n in ideas)
        groups.append(f"### 待启动（idea）\n{rows}")
    if active_done:
        rows = "\n".join(format_row("specs", n, fms[n]) for n in active_done)
        groups.append(f"### 进行中·完成（active·done）\n{rows}")
    return "\n\n".join(groups)


def regen_cockpit_inprogress(deck):
    """Regenerate the cockpit `<!-- AUTO:inprogress -->` block (model-v4 §2).

    cockpit is a status projection of the active set: the `## 进行中` region is
    derived from every `status: active` spec/plan, walked specs-then-plans, each
    alphabetically by filename. Each row mirrors the INDEX row (link + summary),
    with the folder prefix in the link path; an optional `note:` is appended as
    ` — [note: …]`. Empty when nothing is active.
    """
    deck = Path(deck)
    rows = []
    for kind in ("specs", "plans"):
        folder = deck / kind
        if not folder.is_dir():
            continue
        names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
        for name in names:
            fm = parse_frontmatter((folder / name).read_text(encoding="utf-8"))
            if fm.get("status") != "active":
                continue
            row = f"- [{name}]({kind}/{name}) {DASH} {fm['summary']}"
            if fm.get("note"):
                row += f" {DASH} [note: {fm['note']}]"
            rows.append(row)
    body = "\n".join(rows)
    return f"<!-- AUTO:inprogress -->\n{body}\n{AUTO_END}"


# charts/ folder INDEX is hand-maintained (external imports); only its root row is derived.
REGEN_FOLDERS = [name for name in FOLDER_ORDER if name != "charts"]


def _fm_field(path, field):
    try:
        return parse_frontmatter(Path(path).read_text(encoding="utf-8")).get(field)
    except OSError:
        return None


def version_mismatch(deck):
    """Return (deck_version, script_version) if they disagree, else None.

    The script encodes a layout version; running it against a deck on a
    different version risks corrupting it. Compares the deck's `rules.md`
    `version` against the bundled `MIGRATION.md` `current`. Either side
    missing → no comparison (None).
    """
    deck_v = _fm_field(Path(deck) / "rules.md", "version")
    script_v = _fm_field(Path(__file__).resolve().parent.parent / "MIGRATION.md", "current")
    if deck_v and script_v and deck_v != script_v:
        return (deck_v, script_v)
    return None


def _index_targets(deck):
    """Yield (label, index_path, new_block) for every regenerable INDEX."""
    deck = Path(deck)
    for name in REGEN_FOLDERS:
        folder = deck / name
        if folder.is_dir():
            yield name, folder / "INDEX.md", regen_folder_index(folder)
    yield "root", deck / "INDEX.md", regen_root_index(deck)
    cockpit = deck / "cockpit.md"
    if cockpit.is_file() and "<!-- AUTO:inprogress -->" in cockpit.read_text(encoding="utf-8"):
        yield "cockpit", cockpit, regen_cockpit_inprogress(deck)


def index_drift(deck):
    """Return the labels of every INDEX target whose AUTO block is stale.

    Read-only (writes nothing) and version-guard-agnostic — drift detection is
    a comparison, not a regeneration. A target whose INDEX.md is missing or has
    no `<!-- AUTO -->` block counts as drift (its label is returned), mirroring
    walkaround's "missing INDEX" finding. Reused by `flightdeck_lint.py`.
    """
    labels = []
    for label, path, new_block in _index_targets(deck):
        try:
            current = path.read_text(encoding="utf-8")
            cur_block = current[current.index("<!-- AUTO:") : current.index(AUTO_END) + len(AUTO_END)]
        except (OSError, ValueError):
            labels.append(label)
            continue
        if cur_block != new_block:
            labels.append(label)
    return labels


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
    ap.add_argument(
        "--force",
        action="store_true",
        help="bypass the version guard (deck version != script version)",
    )
    args = ap.parse_args(argv)

    mismatch = version_mismatch(args.deck)
    if mismatch and not args.force:
        print(
            f"version guard: deck version {mismatch[0]} != script expects {mismatch[1]}; "
            "regenerate by hand (manual fallback) or pass --force"
        )
        return 2

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
