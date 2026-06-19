"""flightdeck deck formatter — conform a deck to the canonical schema (pure stdlib).

Mechanical pass: across every active deck file, delete frontmatter fields that
are not in that kind's legal set; stamp rules.md recorded-config; append missing
canonical sections to cockpit.md / rules.md (append-only — never deletes or
relabels a body, that destructive/judgment reshaping is the /flightdeck:conform
AI pass). Prints a missing-required worklist for the AI pass to fill.

Scope: cockpit.md, rules.md, and non-archive .md under specs/ plans/ incidents/
checklists/ docs/ references/. archive/ and stray folders are never touched.

Runnable as `uv run flightdeck_conform.py <deck>` or `python flightdeck_conform.py <deck>`.

Field-set source of truth: skills/preflight/protocol.md (Frontmatter field
reference) + templates.md per-kind schema. The sets below are pinned by
test_flightdeck_conform.py — changing a set is an intentional, reviewed edit.
"""

# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import argparse
import re
import sys
from pathlib import Path

from flightdeck_index import IMPORTED_KINDS, parse_frontmatter

# A frontmatter field line: a key at column 0 followed by a colon. Indented
# continuations, blank lines, and comments do not match and are kept verbatim.
_FIELD_RE = re.compile(r"^([A-Za-z_][\w-]*):")

# kind → full set of legal frontmatter fields (required + every optional).
# A field not in a file's kind set is deleted by the formatter.
LEGAL_FIELDS = {
    "spec": {"status", "summary", "last_updated", "note", "supersedes",
             "related", "graduate", "verify"},
    "plan": {"status", "summary", "last_updated", "note", "implements",
             "supersedes", "related", "verify"},
    "incident": {"status", "when_to_read", "applies_to", "last_updated",
                 "summary", "when_to_update", "skip_when", "recurrences",
                 "resolved_by", "verify"},
    "checklist": {"status", "when_to_read", "applies_to", "last_updated",
                  "summary", "when_to_update", "skip_when", "verify", "synced"},
    "reference": {"status", "when_to_read", "applies_to", "last_updated",
                  "summary", "when_to_update", "verify"},
    "doc": {"status", "when_to_read", "applies_to", "last_updated", "summary",
            "when_to_update", "verify", "synced"},
    "rules": {"version", "runtime", "agents_md"},
}

# kind → fields whose absence is reported on the worklist for the AI pass to fill.
REQUIRED_FIELDS = {
    "spec": {"status", "summary"},
    "plan": {"status", "summary"},
    "incident": {"status", "when_to_read", "applies_to", "last_updated"},
    "checklist": {"status", "when_to_read", "applies_to", "last_updated"},
    "reference": {"status", "when_to_read", "applies_to", "last_updated"},
    "doc": {"status", "when_to_read", "applies_to", "last_updated"},
    "rules": {"version"},
}

# folder name → kind (for kind_of routing / the legal-field lookup).
FOLDER_KIND = {
    "specs": "spec", "plans": "plan", "incidents": "incident",
    "checklists": "checklist", "references": "reference", "docs": "doc",
}

# Folders the mechanical pass actually walks. `references/` is excluded: it is an
# IMPORTED_KIND (externally imported, hand-maintained — same reason
# flightdeck_index never regenerates its INDEX), and decks vendor whole upstream
# repos there whose frontmatter (jupytext/kernelspec/name/…) is not ours to prune.
WALK_FOLDERS = [f for f in FOLDER_KIND if f not in IMPORTED_KINDS]


def kind_of(deck, path):
    """Map a deck file to its kind, or None if out of scope.

    `rules.md` → "rules"; a file under a known folder → that folder's kind
    (nested areas resolve to the top folder's kind). Returns None for
    cockpit.md (no frontmatter — owned by the AI pass), anything under
    archive/, any stray-folder file, and any path outside the deck.
    """
    deck = Path(deck)
    path = Path(path)
    try:
        rel = path.relative_to(deck)
    except ValueError:
        return None
    parts = rel.parts
    if "archive" in parts:
        return None
    if len(parts) == 1:
        return "rules" if parts[0] == "rules.md" else None
    return FOLDER_KIND.get(parts[0])


def prune_frontmatter(text, kind):
    """Drop frontmatter fields not in ``LEGAL_FIELDS[kind]``.

    Returns ``(new_text, removed)``. Field order is preserved, non-field lines
    (comments, blanks) are kept verbatim, and everything after the closing
    ``---`` is byte-for-byte unchanged. Text without a leading ``---`` block is
    returned untouched with an empty removal list.
    """
    legal = LEGAL_FIELDS[kind]
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != "---":
        return text, []
    out = [lines[0]]
    removed = []
    close = None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\n") == "---":
            close = idx
            break
        m = _FIELD_RE.match(lines[idx])
        if m and m.group(1) not in legal:
            removed.append(m.group(1))
            continue
        out.append(lines[idx])
    if close is None:
        # No closing fence — not a real frontmatter block; leave untouched.
        return text, []
    out.append(lines[close])
    out.extend(lines[close + 1:])
    return "".join(out), removed


# Canonical rules.md recorded-config: ordered (key, default) — runtime's default
# is filled from the detected/passed runtime at call time.
_RULES_STAMP = ("version", "runtime", "agents_md")
_RULES_DEFAULTS = {"version": "3.0", "agents_md": "off"}


def detect_runtime():
    """Recorded-config runtime probe: uv > python > node (launch's order)."""
    import shutil

    for name in ("uv", "python", "node"):
        if shutil.which(name):
            return name
    return "python"


def stamp_rules(text, runtime):
    """Add any missing recorded-config field to rules.md frontmatter.

    Inserts ``version``/``runtime``/``agents_md`` (in that canonical order) only
    when absent, appending them just before the closing fence so existing keys
    and their order are undisturbed. A file with no frontmatter block gains one.
    """
    defaults = dict(_RULES_DEFAULTS, runtime=runtime)
    lines = text.splitlines(keepends=True)
    has_fm = bool(lines) and lines[0].rstrip("\n") == "---"
    if not has_fm:
        block = "---\n" + "".join(
            "%s: %s\n" % (k, defaults[k]) for k in _RULES_STAMP
        ) + "---\n"
        return block + text
    close = None
    present = set()
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\n") == "---":
            close = idx
            break
        m = _FIELD_RE.match(lines[idx])
        if m:
            present.add(m.group(1))
    if close is None:
        return text
    additions = [
        "%s: %s\n" % (k, defaults[k]) for k in _RULES_STAMP if k not in present
    ]
    return "".join(lines[:close] + additions + lines[close:])


# Canonical section order for the two structure-managed root files. Append-only:
# the formatter
# only adds a missing heading + placeholder; deleting / relabeling sections is
# the /flightdeck:conform AI pass.
COCKPIT_SECTIONS = [
    "## Next", "## In Progress", "## Key Context",
    "## Pending Review", "## Hanging Tasks",
]
RULES_SECTIONS = ["## House rules", "### Project conventions", "### Rules"]

_INPROGRESS_SKELETON = "<!-- AUTO:inprogress -->\n- (none)\n<!-- /AUTO -->"


def _section_body(section):
    if section == "## In Progress":
        return _INPROGRESS_SKELETON
    return "- (none)"


def add_missing_sections(text, which):
    """Append any missing canonical section to cockpit.md / rules.md.

    ``which`` is ``"cockpit"`` or ``"rules"``. Detection is by exact heading
    line; a present heading is never duplicated or reordered. Returns
    ``(new_text, added)`` with the headings appended, in canonical order.
    """
    sections = COCKPIT_SECTIONS if which == "cockpit" else RULES_SECTIONS
    present = {ln.rstrip("\n") for ln in text.splitlines()}
    added = []
    out = text
    for section in sections:
        if section in present:
            continue
        if not out.endswith("\n"):
            out += "\n"
        if not out.endswith("\n\n"):
            out += "\n"
        out += "%s\n\n%s\n" % (section, _section_body(section))
        added.append(section)
    return out, added


class Changes:
    """Per-file conform result, accumulated as later passes are added."""

    def __init__(self, path, removed=None, stamped=None,
                 added_sections=None, missing_required=None):
        self.path = path
        self.removed = removed or []
        self.stamped = stamped or []
        self.added_sections = added_sections or []
        self.missing_required = missing_required or []

    @property
    def changed(self):
        return bool(self.removed or self.stamped or self.added_sections)


def conform_file(path, kind, apply):
    """Prune one in-scope, kind-bearing file + report any missing required field.

    Writes only when ``apply`` and the pruned text differs. ``missing_required``
    is computed against the post-prune frontmatter (pruning never removes a
    legal required field, but a file may simply lack one) for the AI worklist.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    new_text, removed = prune_frontmatter(text, kind)
    present = set(parse_frontmatter(new_text))
    missing = sorted(REQUIRED_FIELDS.get(kind, set()) - present)
    if apply and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return Changes(path, removed=removed, missing_required=missing)


def _scope_files(deck):
    """Yield ``(path, kind)`` for every in-scope, kind-bearing file.

    Walks the standard folders (incl. nested areas), skips ``INDEX.md`` and
    anything ``kind_of`` rejects (``archive/``, stray folders). Sorted by
    codepoint for deterministic, parity-safe output.
    """
    deck = Path(deck)
    for folder in WALK_FOLDERS:
        d = deck / folder
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md"), key=lambda q: str(q).replace("\\", "/")):
            if p.name == "INDEX.md":
                continue
            kind = kind_of(deck, p)
            if kind is not None:
                yield p, kind


def _relpath(deck, path):
    return Path(path).relative_to(deck).as_posix()


def run_conform(deck, apply, runtime):
    """Apply (or, when ``apply`` is False, plan) the mechanical pass.

    Returns ``(results, worklist)`` where ``results`` is a list of ``Changes``
    (cockpit, rules, then every kind file, sorted by relpath) and ``worklist``
    is a sorted list of ``(relpath, missing-required-field)`` for the AI pass.
    """
    deck = Path(deck)
    results = []

    cockpit = deck / "cockpit.md"
    if cockpit.is_file():
        text = cockpit.read_text(encoding="utf-8")
        new_text, added = add_missing_sections(text, "cockpit")
        if apply and new_text != text:
            cockpit.write_text(new_text, encoding="utf-8")
        results.append(Changes(cockpit, added_sections=added))

    rules = deck / "rules.md"
    if rules.is_file():
        text = rules.read_text(encoding="utf-8")
        pruned, removed = prune_frontmatter(text, "rules")
        present = set(parse_frontmatter(pruned))
        stamped = [k for k in _RULES_STAMP if k not in present]
        stamped_text = stamp_rules(pruned, runtime)
        new_text, added = add_missing_sections(stamped_text, "rules")
        if apply and new_text != text:
            rules.write_text(new_text, encoding="utf-8")
        results.append(
            Changes(rules, removed=removed, stamped=stamped, added_sections=added)
        )

    worklist = []
    for path, kind in _scope_files(deck):
        ch = conform_file(path, kind, apply)
        results.append(ch)
        rel = _relpath(deck, path)
        for field in ch.missing_required:
            worklist.append((rel, field))

    results.sort(key=lambda c: _relpath(deck, c.path))
    worklist.sort()
    return results, worklist


def _change_segments(ch):
    segs = []
    if ch.removed:
        segs.append("drop " + ",".join(ch.removed))
    if ch.stamped:
        segs.append("stamp " + ",".join(ch.stamped))
    if ch.added_sections:
        segs.append("add " + ",".join(ch.added_sections))
    return "; ".join(segs)


def main(argv=None):
    # Force UTF-8 stdout (Windows locale codepage would mojibake CJK worklist
    # notes when piped/captured); mirrors flightdeck_index.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(
        description="Conform a flightdeck deck to its canonical schema "
        "(mechanical pass: prune non-schema frontmatter, stamp rules "
        "recorded-config, append missing cockpit/rules sections)."
    )
    ap.add_argument("deck", help="path to the flightdeck/ deck root")
    ap.add_argument(
        "--check",
        action="store_true",
        help="dry-run: print the planned changes + AI worklist, write nothing, "
        "exit 1 if the deck is not fully conformant",
    )
    ap.add_argument(
        "--runtime",
        default=None,
        help="recorded runtime to stamp into rules.md (default: probe uv>python>node)",
    )
    args = ap.parse_args(argv)

    runtime = args.runtime or detect_runtime()
    deck = Path(args.deck)
    apply = not args.check
    results, worklist = run_conform(deck, apply, runtime)

    if args.check:
        for ch in results:
            if ch.changed:
                print("%s\t%s" % (_relpath(deck, ch.path), _change_segments(ch)))
        for rel, field in worklist:
            print("%s\t(missing) %s" % (rel, field))
        pending = any(ch.changed for ch in results) or bool(worklist)
        return 1 if pending else 0

    for rel, field in worklist:
        print("%s\t%s" % (rel, field))
    return 0


if __name__ == "__main__":
    sys.exit(main())
