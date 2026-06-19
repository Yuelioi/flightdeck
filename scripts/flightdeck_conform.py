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

import re
import sys
from pathlib import Path

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

# in-scope folder name → kind
FOLDER_KIND = {
    "specs": "spec", "plans": "plan", "incidents": "incident",
    "checklists": "checklist", "references": "reference", "docs": "doc",
}


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
    """Prune one in-scope, kind-bearing file. Writes only when ``apply``."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    new_text, removed = prune_frontmatter(text, kind)
    if apply and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return Changes(path, removed=removed)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    # CLI wired in a later task.
    return 0


if __name__ == "__main__":
    sys.exit(main())
