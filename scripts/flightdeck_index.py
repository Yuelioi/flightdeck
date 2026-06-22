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
import hashlib
import json
import os
import re
import subprocess
import unicodedata
import sys
from collections import Counter
from pathlib import Path

STATUS_ORDER = ["idea", "active", "done"]

# Signature normalization: strip volatile tokens (path/line/timestamp/hex/uuid/long int)
# while keeping semantic ones (e.g. a quoted key) — `KeyError: 'summary'` and `'title'`
# must stay distinct. The full ruleset lives here; the test suite
# (SignatureNormalizeTest) is the contract — change the tests before the rules.
_VOLATILE = [
    (re.compile(r"\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b"), "_UUID_"),
    (re.compile(r"0x[0-9a-fA-F]+"), "_HEX_"),
    (re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}\S*)?"), "_TIME_"),
    (re.compile(r"[A-Za-z]:\\[^\s:]+|(?:/[\w.\-]+){2,}"), "_PATH_"),
    (re.compile(r"\bline\s+\d+\b", re.I), "line _N_"),
    (re.compile(r"\b\d{4,}\b"), "_N_"),
]


def normalize_symptom(s):
    out = (s or "").strip()
    for pat, repl in _VOLATILE:
        out = pat.sub(repl, out)
    return re.sub(r"\s+", " ", out).strip()


def signature_fingerprint(symptom, error_type=""):
    """Primary fingerprint = error_type + normalized symptom. `where` is **not** part
    of the fingerprint (spec: symptom+error_type are primary, where is the
    secondary/tiebreak the caller uses to disambiguate multiple hits)."""
    key = f"{(error_type or '').strip()}\n{normalize_symptom(symptom)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


PROJECT_MARKER = "<!-- flightdeck:project-specific -->"


def _strip_frontmatter(text):
    """Body after a leading ---fenced frontmatter block (whole text when none)."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1:])
    return text


def shared_region(text):
    """Master-owned region: frontmatter-stripped body up to PROJECT_MARKER; the
    whole body when the marker is absent (pure-shared file)."""
    body = _strip_frontmatter(text)
    idx = body.find(PROJECT_MARKER)
    return body if idx == -1 else body[:idx]


def _normalize_shared(s):
    """Canonicalize for fingerprint compare: NFC, LF, strip per-line trailing
    whitespace, drop trailing blank lines."""
    s = unicodedata.normalize("NFC", s).replace("\r\n", "\n").replace("\r", "\n")
    s = "\n".join(line.rstrip() for line in s.split("\n"))
    return s.rstrip("\n")


def shared_fingerprint(text):
    """12-hex sha1 of the normalized shared region (signature_fingerprint regime)."""
    norm = _normalize_shared(shared_region(text))
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def _split_frontmatter(text):
    """Return (frontmatter_incl_fences_or_'', body)."""
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "".join(lines[:i + 1]), "".join(lines[i + 1:])
    return "", text


def pull_shared(consumer_text, master_text):
    """Mechanical splice: keep consumer frontmatter + PROJECT_MARKER + project
    section, replace the shared region with the master's body."""
    fm, body = _split_frontmatter(consumer_text)
    master_body = _strip_frontmatter(master_text)
    idx = body.find(PROJECT_MARKER)
    if idx == -1:
        return fm + master_body
    tail = body[idx:]                       # marker + project section
    shared = master_body.rstrip("\n") + "\n\n"
    return fm + shared + tail


def parse_signature(text):
    """Parse the `## Signature` block's key:value lines into a dict (keys
    symptom/error_type/where/trigger). Returns {} when no block. Backticks and
    surrounding whitespace are stripped from values."""
    m = re.search(r"^##\s+Signature\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return {}
    sig = {}
    for line in m.group(1).splitlines():
        lm = re.match(r"\s*-\s*(symptom|error_type|where|trigger)\s*:\s*(.*)$", line)
        if lm:
            sig[lm.group(1)] = lm.group(2).strip().strip("`").strip()
    return sig


def match_signature(deck, symptom, error_type=""):
    """Return incidents with the same primary fingerprint (including
    status:obsolete — regression detection depends on it). Scans every .md under
    incidents/ and archive/incidents/ (nested areas too, rglob); files without a
    ## Signature block are skipped (they go through the AI fuzzy layer).
    Each hit is {path (deck-relative), status, where}."""
    fp = signature_fingerprint(symptom, error_type)
    hits = []
    deck = Path(deck)
    scan_roots = [deck / "incidents", deck / "archive" / "incidents"]
    seen = set()
    for root in scan_roots:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            if p.name == "INDEX.md":
                continue
            resolved = p.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = p.read_text(encoding="utf-8")
            sig = parse_signature(text)
            if not sig.get("symptom"):
                continue
            if signature_fingerprint(sig["symptom"], sig.get("error_type", "")) == fp:
                hits.append({
                    "path": str(p.relative_to(deck)).replace("\\", "/"),
                    "status": parse_frontmatter(text).get("status", ""),
                    "where": sig.get("where", ""),
                })
    return hits


DASH = "—"  # em dash — the INDEX row delimiter

SUMMARY_KINDS = {"specs", "plans"}                       # workflow, summary rows
KNOWLEDGE_KINDS = {"checklists", "incidents", "docs"}    # self-authored knowledge, auto-INDEX, knowledge rows
IMPORTED_KINDS = {"references"}                          # externally imported, hand-maintained INDEX, "imported" rollup
NESTABLE_KINDS = {"incidents", "checklists", "docs", "references"}  # nestable by area (knowledge)

# root-INDEX order after canonical naming (design reading order, not alphabetical).
FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "docs", "references"]


def format_row(kind, filename, fm):
    """Render one folder-INDEX row for an artifact, by folder kind.

    Missing required fields are rendered with a visible sentinel rather than
    raising, so a malformed file never crashes a regen.
    """
    link = f"- [{filename}]({filename})"
    status = fm.get("status", "?")
    if kind in SUMMARY_KINDS:
        row = f"{link} {DASH} {status} {DASH} {fm.get('summary', '⚠ summary missing')}"
        if fm.get("verify"):
            row = "⚠ unverified " + row
        return row
    if kind in KNOWLEDGE_KINDS:
        row = (
            f"{link} {DASH} {status} {DASH} "
            f"when_to_read: {fm.get('when_to_read', '⚠ missing')} {DASH} "
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
        if fm.get("verify"):
            row = "⚠ unverified " + row
        elif status == "stale":
            row = "⚠ pending-review " + row
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


def _marker_of(block):
    """The opening `<!-- AUTO:<name> -->` tag of an AUTO block — lets a file with
    multiple AUTO regions (cockpit's inprogress + staged) update only the match."""
    i = block.index("<!-- AUTO:")
    return block[i : block.index(" -->", i) + len(" -->")]


def extract_auto_block(text, marker):
    """The current `<marker>…<!-- /AUTO -->` slice of text (for drift comparison)."""
    start = text.index(marker)
    end = text.index(AUTO_END, start) + len(AUTO_END)
    return text[start:end]


def replace_auto_block(text, new_block):
    """Swap the **named** `<!-- AUTO:<name> -->…<!-- /AUTO -->` region, keeping the
    rest. The marker name is read from new_block, so a multi-region file updates
    only the matching region."""
    marker = _marker_of(new_block)
    start = text.index(marker)
    end = text.index(AUTO_END, start) + len(AUTO_END)
    return text[:start] + new_block + text[end:]


def _area_row(area_dir):
    """One area row in a top-level INDEX: link + purpose + last_updated (from the area/INDEX.md frontmatter)."""
    idx = area_dir / "INDEX.md"
    fm = parse_frontmatter(idx.read_text(encoding="utf-8")) if idx.is_file() else {}
    purpose = fm.get("purpose", "⚠ purpose missing")
    updated = fm.get("last_updated", "—")
    return f"- [{area_dir.name}/]({area_dir.name}/INDEX.md) {DASH} {purpose} {DASH} last_updated: {updated}"


def regen_folder_index(folder):
    """Regenerate the `<!-- AUTO:<kind> -->` block for one deck folder.

    Most folders list rows alphabetically by filename (the canonical order; the
    pre-script hand-append order is NOT reproducible from the filesystem).

    `specs/` is special (model-v4 §1.4): idea files are timeless (no date
    prefix) and would sort badly mixed with the dated active/done files, so the
    block is split into two in-AUTO subgroups — `### Backlog (idea)` (idea,
    alphabetical) and `### Active · Done` (active/done, by filename
    date descending). A rejected spec is deleted outright (3.0), not parked — so
    there is no scrapped/tombstone group.

    Nestable knowledge folders (NESTABLE_KINDS) with subdirectories produce an
    INDEX-of-INDEXes: one area row per subdirectory (purpose + last_updated from
    the area's INDEX.md frontmatter), followed by any loose .md files at the top
    level. Without subdirectories, falls back to the flat behavior.
    """
    folder = Path(folder)
    kind = folder.name
    if kind == "specs":
        names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
        return f"<!-- AUTO:{kind} -->\n{_specs_grouped_body(folder, names)}\n{AUTO_END}"
    subdirs = sorted((d for d in folder.iterdir() if d.is_dir()), key=lambda p: p.name)
    if kind in NESTABLE_KINDS and subdirs:
        rows = [_area_row(d) for d in subdirs]
        row_kind = kind if kind in KNOWLEDGE_KINDS else "checklists"
        top_files = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
        if kind in KNOWLEDGE_KINDS:   # obsolete is bound for archive (archivable_obsolete), not the routing rows; stale stays but carries ⚠
            top_files = [n for n in top_files
                         if parse_frontmatter((folder / n).read_text(encoding="utf-8")).get("status") != "obsolete"]
        rows += [format_row(row_kind, n, parse_frontmatter((folder / n).read_text(encoding="utf-8"))) for n in top_files]
        return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    if kind in KNOWLEDGE_KINDS:   # obsolete is bound for archive (archivable_obsolete), not the routing rows; stale stays but carries ⚠
        names = [n for n in names
                 if parse_frontmatter((folder / n).read_text(encoding="utf-8")).get("status") != "obsolete"]
    row_kind = kind if kind in (SUMMARY_KINDS | KNOWLEDGE_KINDS) else "checklists"
    rows = [format_row(row_kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8"))) for name in names]
    return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"


def _specs_grouped_body(folder, names):
    """Render the specs AUTO body as status-grouped subsections (see caller)."""
    fms = {name: parse_frontmatter((folder / name).read_text(encoding="utf-8")) for name in names}
    ideas = sorted(n for n in names if fms[n].get("status") == "idea")
    active_done = sorted((n for n in names if fms[n].get("status") in ("active", "done")), reverse=True)
    groups = []
    if ideas:
        groups.append("### Backlog (idea)\n" + "\n".join(format_row("specs", n, fms[n]) for n in ideas))
    if active_done:
        groups.append("### Active · Done\n" + "\n".join(format_row("specs", n, fms[n]) for n in active_done))
    return "\n\n".join(groups)


INPROGRESS_SUMMARY_MAX = 80  # In Progress rows render only a truncated summary head; full text stays in the spec frontmatter


def _truncate_inprogress_summary(summary):
    """In Progress row render: take the first line, truncate + ellipsis past the cap (deterministic, no judgment)."""
    head = (summary or "").splitlines()[0] if summary else ""
    if len(head) > INPROGRESS_SUMMARY_MAX:
        head = head[:INPROGRESS_SUMMARY_MAX].rstrip() + "…"
    return head


def regen_cockpit_inprogress(deck):
    """Regenerate the cockpit `<!-- AUTO:inprogress -->` block (model-v4 §2).

    cockpit is a status projection of the active set: the `## In Progress` region is
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
            summary = _truncate_inprogress_summary(fm.get("summary", "⚠ summary missing"))
            row = f"- [{name}]({kind}/{name}) {DASH} {summary}"
            if fm.get("note"):
                row += f" {DASH} [note: {fm['note']}]"
            rows.append(row)
    body = "\n".join(rows)
    return f"<!-- AUTO:inprogress -->\n{body}\n{AUTO_END}"


def regen_cockpit_staged(deck):
    """Regenerate the cockpit `<!-- AUTO:staged -->` block — the stage/land
    "awaiting land" view (specs/2026-06-22-stage-land-lifecycle.md).

    Derived (never hand-written) from two frontmatter-decidable classes:
      - done-not-archived workflow: specs/plans with status:done still in the
        source folder (archive/ is never scanned by these globs);
      - stale-with-verify knowledge: incidents/checklists/docs with status:stale
        AND a `verify` field (the "newly produced, pending review" sense).
    Pending Review stays a separate hand-maintained section (sign-off is human
    judgment, not derivable). Empty body when nothing is staged.
    """
    deck = Path(deck)
    done_rows, knowledge_rows = [], []
    for kind in ("specs", "plans"):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for name in sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md"):
            fm = parse_frontmatter((folder / name).read_text(encoding="utf-8"))
            if fm.get("status") == "done":
                summary = _truncate_inprogress_summary(fm.get("summary", "⚠ summary missing"))
                done_rows.append(f"- [{name}]({kind}/{name}) {DASH} {summary}")
    for kind in sorted(KNOWLEDGE_KINDS):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for p in sorted(folder.rglob("*.md")):
            if p.name == "INDEX.md":
                continue
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("status") == "stale" and fm.get("verify"):
                rel = str(p.relative_to(deck)).replace("\\", "/")
                knowledge_rows.append(f"- [{p.name}]({rel}) {DASH} verify: {fm['verify']}")
    groups = []
    if done_rows:
        groups.append("### Done (awaiting land)\n" + "\n".join(done_rows))
    if knowledge_rows:
        groups.append("### Knowledge (pending review)\n" + "\n".join(knowledge_rows))
    body = "\n\n".join(groups)
    return f"<!-- AUTO:staged -->\n{body}\n{AUTO_END}"


# references/ keeps a hand-maintained INDEX (externally imported); only its root row is derived.
REGEN_FOLDERS = [name for name in FOLDER_ORDER if name not in IMPORTED_KINDS]


def _fm_field(path, field):
    try:
        return parse_frontmatter(Path(path).read_text(encoding="utf-8")).get(field)
    except OSError:
        return None


def _active_inbound_targets(deck):
    """Set of target paths any status:active artifact in the deck points at via a structured edge (implements:)."""
    deck = Path(deck)
    targets = set()
    for kind in ("specs", "plans") + tuple(sorted(KNOWLEDGE_KINDS)):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for p in folder.rglob("*.md"):       # rglob: covers nested areas
            if p.name == "INDEX.md":
                continue
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("status") != "active":
                continue
            for field in ("implements",):
                v = fm.get(field)
                if v:
                    targets.add(v.strip())
    return targets


def archivable_done(deck):
    """Done workflow artifacts (specs/plans) with no active inbound edge pointing at them — safe to archive, deterministic and reproducible."""
    deck = Path(deck)
    blocked = _active_inbound_targets(deck)
    result = []
    for kind in ("specs", "plans"):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.md")):
            if p.name == "INDEX.md":
                continue
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("status") != "done":
                continue
            rel = f"{kind}/{p.name}"
            if rel not in blocked:
                result.append(rel)
    return sorted(result)


def archivable_obsolete(deck):
    """status:obsolete knowledge artifacts (incidents/checklists/docs) — dead and
    awaiting archival. Symmetric to archivable_done: obsolete is the knowledge-side
    drained state of done, with no pinning concept (superseded_by is retired), so a
    match can go straight into archive/. Deterministic and reproducible."""
    deck = Path(deck)
    result = []
    for kind in sorted(KNOWLEDGE_KINDS):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for p in sorted(folder.rglob("*.md")):
            if p.name == "INDEX.md":
                continue
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("status") == "obsolete":
                result.append(str(p.relative_to(deck)).replace("\\", "/"))
    return sorted(result)


def spec_advance_candidates(deck):
    """active spec whose implementing plans are ALL done (≥1 done, no active/idea
    plan still pointing at it) — the plans finished but the spec lags behind.
    landing confirm-gated offers to advance such a spec to `done` (it never flips
    a second artifact itself). Deterministic, read-only; returns spec paths
    relative to deck, sorted. Reuses the `implements:` edge, orthogonal to the
    archivable (done-archival) and recurrence (incident-signature) sweeps."""
    deck = Path(deck)
    plans = deck / "plans"
    if not plans.is_dir():
        return []
    by_spec = {}  # spec_rel -> set of implementing-plan statuses
    for p in sorted(plans.glob("*.md")):
        if p.name == "INDEX.md":
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        target = fm.get("implements")
        if target:
            by_spec.setdefault(target.strip(), set()).add(fm.get("status", ""))
    result = []
    for spec_rel, statuses in by_spec.items():
        spec_path = deck / spec_rel
        if not spec_path.is_file():
            continue
        if parse_frontmatter(spec_path.read_text(encoding="utf-8")).get("status") != "active":
            continue
        # all implementing plans done (≥1 done, nothing still active/idea)
        if "done" in statuses and statuses <= {"done"}:
            result.append(spec_rel)
    return sorted(result)


def last_anchor_ref(deck):
    """The most recent commit SHA carrying a Flightdeck-Sync trailer (the last exit-ritual anchor), or None."""
    try:
        out = subprocess.run(
            ["git", "-C", str(deck), "log", "-1", "--grep=Flightdeck-Sync", "--format=%H"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def changed_since_anchor(deck):
    """Paths changed since the anchor (committed + uncommitted working tree),
    relative to the repo root. No anchor → degrade to working-tree changes
    (first run / no history still yields a signal)."""
    anchor = last_anchor_ref(deck)
    paths = set()
    try:
        cmds = [["status", "--porcelain"]]
        if anchor:
            cmds.append(["diff", "--name-only", f"{anchor}..HEAD"])
        for cmd in cmds:
            out = subprocess.run(["git", "-C", str(deck), *cmd],
                                 capture_output=True, text=True, check=True).stdout
            for line in out.splitlines():
                p = line[3:].strip() if cmd[0] == "status" else line.strip()
                if p:
                    paths.add(p)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return sorted(paths)


def verify_pending(deck):
    """(path, verify-note) for every artifact carrying a `verify` field,
    across the active tree AND archive/ — the pending-verification source of truth.
    Path is deck-relative, POSIX-slashed; sorted by path."""
    deck = Path(deck)
    out = []
    for p in deck.rglob("*.md"):
        if p.name == "INDEX.md":
            continue
        try:
            v = parse_frontmatter(p.read_text(encoding="utf-8")).get("verify")
        except OSError:
            continue
        if v:
            out.append((str(p.relative_to(deck)).replace("\\", "/"), v))
    return sorted(out)


def _resolve_master_root():
    """Resolve the shared-knowledge master deck root, or None.

    Fixed convention: ``~/.flightdeck``. To keep the master elsewhere, make
    ``~/.flightdeck`` a symlink or directory junction to it — ``is_dir()``
    follows both. Returns the path when it resolves to a directory, else None
    (the caller treats None as ``master-missing`` and skips gracefully)."""
    root = Path.home() / ".flightdeck"
    return root if root.is_dir() else None


def _norm_deck(p):
    """Canonical dedupe key for a consumer deck path: resolved, POSIX slashes."""
    return Path(p).resolve().as_posix()


def _read_consumers(fm):
    """Parse the `consumers` frontmatter value (single-line JSON array) into a
    list of strings. Returns [] when absent or unparseable."""
    raw = fm.get("consumers")
    if not raw:
        return []
    try:
        val = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return [str(x) for x in val] if isinstance(val, list) else []


def _write_consumers_line(text, consumers):
    """Return `text` with its frontmatter `consumers:` line set to a sorted,
    deduped single-line JSON array. Inserts the line before the closing `---`
    when absent. Assumes a leading `---`-fenced block exists."""
    payload = json.dumps(sorted(set(consumers)))
    lines = text.splitlines(keepends=True)
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return text
    for i in range(1, end):
        if lines[i].split(":", 1)[0].strip() == "consumers":
            lines[i] = f"consumers: {payload}\n"
            return "".join(lines)
    lines.insert(end, f"consumers: {payload}\n")
    return "".join(lines)


def register_consumer(master_root, relpath, deck):
    """Add `deck` (normalized) to master file `relpath`'s `consumers` list.
    Idempotent. Raises ValueError when `relpath` is not an existing file under
    `master_root` (the registration is a no-op then; callers warn, don't abort)."""
    target = Path(master_root) / relpath
    if not target.is_file():
        raise ValueError(f"not a master file: {relpath}")
    text = target.read_text(encoding="utf-8")
    consumers = _read_consumers(parse_frontmatter(text))
    consumers.append(_norm_deck(deck))
    target.write_text(_write_consumers_line(text, consumers), encoding="utf-8")
    return True


def list_consumers(master_root):
    """Union of every master shared file's `consumers`, normalized + sorted.

    Pure read: a deck whose dir is currently unreachable is **skipped from this
    result** but never removed from any file (network drive offline / unmounted
    / symlink target temporarily down must not be mistaken for permanent
    removal — that is `prune_consumers`'s job). Excludes archive/ and INDEX.md."""
    master_root = Path(master_root)
    seen = set()
    for p in master_root.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(master_root).parts:
            continue
        try:
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        for c in _read_consumers(fm):
            seen.add(_norm_deck(c))
    return sorted(c for c in seen if Path(c).is_dir())


def prune_consumers(master_root):
    """Remove, from every master file's `consumers`, decks that are *confirmed
    gone*: parent dir reachable (`is_dir()`) AND the deck itself neither
    `exists()` nor `os.path.lexists()`. The lexists() guard keeps a symlinked
    deck whose target is temporarily unreachable; a fully-unreachable parent
    (offline drive) means we cannot confirm removal, so we keep it. The ONLY
    mutating consumer op. Returns [(file_relpath, removed_deck), ...]."""
    master_root = Path(master_root)
    removed = []
    for p in master_root.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(master_root).parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        consumers = _read_consumers(parse_frontmatter(text))
        if not consumers:
            continue
        kept = []
        for c in consumers:
            cp = Path(c)
            confirmed_gone = cp.parent.is_dir() and not cp.exists() and not os.path.lexists(c)
            if confirmed_gone:
                removed.append((str(p.relative_to(master_root)).replace("\\", "/"), c))
            else:
                kept.append(c)
        if len(kept) != len(consumers):
            p.write_text(_write_consumers_line(text, kept), encoding="utf-8")
    return removed


def sync_status(deck):
    """Read-only shared-knowledge drift scan: for every artifact carrying
    `synced: true`, use its **own relpath** to find the same-path source under the
    master deck and compare the shared-region fingerprint, returning (state,
    relpath). Writes nothing.

    Master root resolution is in `_resolve_master_root` (fixed `~/.flightdeck`).
    The shared region is master-authoritative, so any fingerprint difference is
    `stale` (no timestamp-based direction split). States:
      in-sync         shared-region fingerprint equals the master's
      stale           shared regions differ → /flightdeck:sync can mechanically pull
      dangling        master root exists, but the same-relpath source is not a readable file (missing/type mismatch)
      master-missing  master root ~/.flightdeck does not exist → whole deck skipped gracefully
    Paths are deck-relative, POSIX-slashed; sorted by relpath. archive/ excluded."""
    deck = Path(deck)
    master_root = _resolve_master_root()
    master_ok = master_root is not None
    out = []
    for p in deck.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(deck).parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = parse_frontmatter(text)
        if str(fm.get("synced", "")).strip().lower() != "true":
            continue
        rel = str(p.relative_to(deck)).replace("\\", "/")
        if not master_ok:
            out.append(("master-missing", rel))
            continue
        master_file = master_root / rel
        if not master_file.is_file():
            out.append(("dangling", rel))
            continue
        master_text = master_file.read_text(encoding="utf-8")
        state = "in-sync" if shared_fingerprint(text) == shared_fingerprint(master_text) else "stale"
        out.append((state, rel))
    return sorted(out, key=lambda t: t[1])


def _index_targets(deck):
    """Yield (label, index_path, new_block) for every regenerable INDEX."""
    deck = Path(deck)
    for name in REGEN_FOLDERS:
        folder = deck / name
        if folder.is_dir():
            yield name, folder / "INDEX.md", regen_folder_index(folder)
            if name in NESTABLE_KINDS:
                for area in sorted(d for d in folder.iterdir() if d.is_dir()):
                    if (area / "INDEX.md").is_file() or any(area.glob("*.md")):
                        yield f"{name}/{area.name}", area / "INDEX.md", regen_folder_index(area)
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
            cur_block = extract_auto_block(current, _marker_of(new_block))
        except (OSError, ValueError):
            labels.append(label)
            continue
        if cur_block != new_block:
            labels.append(label)
    return labels


def main(argv=None):
    # Force UTF-8 stdout on Windows (locale codepage, e.g. gbk, would mojibake
    # CJK verify notes when stdout is piped/captured).  reconfigure() is
    # available on Python 3.7+ TextIOWrapper; guard for safety.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

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
        "--archivable",
        action="store_true",
        help="print the deck's archivable done set (one path per line) and exit; read-only",
    )
    ap.add_argument(
        "--advance-candidates",
        action="store_true",
        help="print active specs whose implementing plans are all done (one path per line) and exit; read-only",
    )
    ap.add_argument("--match-signature", metavar="SYMPTOM", default=None,
                    help="print incidents whose signature fingerprint matches SYMPTOM (read-only); status<TAB>path")
    ap.add_argument("--sig-error-type", metavar="TYPE", default="",
                    help="error_type to pair with --match-signature (optional)")
    ap.add_argument(
        "--changed-since-anchor",
        action="store_true",
        help="print paths changed since the last Flightdeck-Sync anchor commit (one per line); read-only",
    )
    ap.add_argument(
        "--verify-pending",
        action="store_true",
        help="print (path<TAB>verify-note) for every artifact carrying a `verify` field, across active+archive; read-only",
    )
    ap.add_argument(
        "--sync-status",
        action="store_true",
        help="print (state<TAB>relpath) for every artifact carrying `synced: true`, "
        "comparing the shared-region content fingerprint against the same-relpath source "
        "under ~/.flightdeck (read-only)",
    )
    ap.add_argument(
        "--sync-pull",
        action="store_true",
        help="apply mechanical shared-knowledge pull: replace each stale "
        "synced:true file's shared region with its master's (keeps frontmatter + "
        "project section). With --check: report only (would-pull<TAB>relpath), exit 1 if any stale.",
    )
    ap.add_argument(
        "--register-consumer", nargs=2, metavar=("DECK", "RELPATH"), default=None,
        help="register consumer DECK as a consumer of master file RELPATH (idempotent); "
        "DECK path is resolve()-normalized; RELPATH must be an existing master file",
    )
    ap.add_argument(
        "--list-consumers", action="store_true",
        help="print each registered consumer deck (union across master files), reachable dirs only; read-only",
    )
    ap.add_argument(
        "--prune-consumers", action="store_true",
        help="remove consumer entries whose deck dir is confirmed gone (parent reachable, neither exists nor lexists); "
        "the ONLY mutating consumer op",
    )
    args = ap.parse_args(argv)

    if args.archivable:
        for rel in sorted(set(archivable_done(args.deck)) | set(archivable_obsolete(args.deck))):
            print(rel)
        return 0

    if args.advance_candidates:
        for rel in spec_advance_candidates(args.deck):
            print(rel)
        return 0

    if args.match_signature is not None:
        for h in match_signature(args.deck, args.match_signature, args.sig_error_type):
            print(f"{h['status']}\t{h['path']}")
        return 0

    if args.changed_since_anchor:
        for p in changed_since_anchor(args.deck):
            print(p)
        return 0

    if args.verify_pending:
        for path, note in verify_pending(args.deck):
            print(f"{path}\t{note}")
        return 0

    if args.sync_status:
        for state, path in sync_status(args.deck):
            print(f"{state}\t{path}")
        return 0

    if args.register_consumer is not None:
        deck_arg, rel = args.register_consumer
        try:
            register_consumer(args.deck, rel, deck_arg)
            print(f"registered\t{_norm_deck(deck_arg)}\t{rel}")
            return 0
        except ValueError as e:
            print(f"register failed: {e}", file=sys.stderr)
            return 1

    if args.list_consumers:
        for c in list_consumers(args.deck):
            print(c)
        return 0

    if args.prune_consumers:
        for rel, c in prune_consumers(args.deck):
            print(f"pruned\t{rel}\t{c}")
        return 0

    if args.sync_pull:
        master_root = _resolve_master_root()
        if master_root is None:
            return 0                       # master-missing → graceful no-op
        pending = False
        for state, rel in sync_status(args.deck):
            if state != "stale":
                continue
            pending = True
            if args.check:
                print(f"would-pull\t{rel}")
                continue
            cpath = Path(args.deck) / rel
            new = pull_shared(cpath.read_text(encoding="utf-8"),
                              (master_root / rel).read_text(encoding="utf-8"))
            cpath.write_text(new, encoding="utf-8")
            print(f"pulled\t{rel}")
        return 1 if (args.check and pending) else 0

    drift = []
    for label, path, new_block in _index_targets(args.deck):
        try:
            current = path.read_text(encoding="utf-8")
            cur_block = extract_auto_block(current, _marker_of(new_block))
        except (OSError, ValueError):
            # missing INDEX.md or no AUTO block: counts as drift; when not --check, create a minimal INDEX
            drift.append(label)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {label} — INDEX\n\n{new_block}\n", encoding="utf-8")
            continue
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
