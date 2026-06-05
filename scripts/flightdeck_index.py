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
import re
import sys
from collections import Counter
from pathlib import Path

STATUS_ORDER = ["idea", "active", "done", "scrapped"]

# 签名归一化：剥掉易变 token（路径/行号/时间戳/hex/uuid/长整数），但保留语义 token
# （如引号包裹的 key）——`KeyError: 'summary'` 与 `'title'` 必须区分。完整规则在此，
# 测试套件（SignatureNormalizeTest）是契约；调整规则须先改测试。
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

DASH = "—"  # em dash — the INDEX row delimiter

SUMMARY_KINDS = {"specs", "plans"}                       # workflow，summary 行
KNOWLEDGE_KINDS = {"checklists", "incidents", "docs"}    # 自撰知识，auto-INDEX，knowledge 行
IMPORTED_KINDS = {"references"}                          # 外部导入，手维护 INDEX，"imported" 汇总
NESTABLE_KINDS = {"incidents", "checklists", "docs", "references"}  # 可按 area 嵌套（knowledge）

# 主流命名后的 root-INDEX 顺序（设计读序，非字母序）。
FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "docs", "references"]


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


def imported_summary(folder):
    """references/ 是手维护的外部导入，按条目数汇总。"""
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
        summ = imported_summary(folder) if name in IMPORTED_KINDS else folder_summary(folder)
        rows.append(f"- {name}/ {DASH} {summ}")
    body = "\n".join(rows)
    return f"<!-- AUTO:root -->\n{body}\n{AUTO_END}"


def _area_row(area_dir):
    """顶层 INDEX 里一个 area 的行：链接 + 用途 + last_updated（取 area/INDEX.md frontmatter）。"""
    idx = area_dir / "INDEX.md"
    fm = parse_frontmatter(idx.read_text(encoding="utf-8")) if idx.is_file() else {}
    purpose = fm.get("purpose", "⚠ purpose 缺失")
    updated = fm.get("last_updated", "—")
    return f"- [{area_dir.name}/]({area_dir.name}/INDEX.md) {DASH} {purpose} {DASH} last_updated: {updated}"


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
        rows += [format_row(row_kind, n, parse_frontmatter((folder / n).read_text(encoding="utf-8"))) for n in top_files]
        return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    row_kind = kind if kind in (SUMMARY_KINDS | KNOWLEDGE_KINDS) else "checklists"
    rows = [format_row(row_kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8"))) for name in names]
    return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"


def _specs_grouped_body(folder, names):
    """Render the specs AUTO body as status-grouped subsections (see caller)."""
    fms = {name: parse_frontmatter((folder / name).read_text(encoding="utf-8")) for name in names}
    ideas = sorted(n for n in names if fms[n].get("status") == "idea")
    active_done = sorted((n for n in names if fms[n].get("status") in ("active", "done")), reverse=True)
    scrapped = sorted(n for n in names if fms[n].get("status") == "scrapped")
    groups = []
    if ideas:
        groups.append("### 待启动（idea）\n" + "\n".join(format_row("specs", n, fms[n]) for n in ideas))
    if active_done:
        groups.append("### 进行中·完成（active·done）\n" + "\n".join(format_row("specs", n, fms[n]) for n in active_done))
    if scrapped:
        groups.append("### 已否决（scrapped）\n" + "\n".join(format_row("specs", n, fms[n]) for n in scrapped))
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
            row = f"- [{name}]({kind}/{name}) {DASH} {fm.get('summary', '⚠ summary 缺失')}"
            if fm.get("note"):
                row += f" {DASH} [note: {fm['note']}]"
            rows.append(row)
    body = "\n".join(rows)
    return f"<!-- AUTO:inprogress -->\n{body}\n{AUTO_END}"


# references/ 的 INDEX 手维护（外部导入）；只它的 root 行派生。
REGEN_FOLDERS = [name for name in FOLDER_ORDER if name not in IMPORTED_KINDS]


def _fm_field(path, field):
    try:
        return parse_frontmatter(Path(path).read_text(encoding="utf-8")).get(field)
    except OSError:
        return None


RETIRED_STATUSES = {"pending", "awaiting-review", "blocked"}


def _migration_layout():
    """(current, [need_update]) read from bundled MIGRATION.md frontmatter."""
    mig = Path(__file__).resolve().parent.parent / "MIGRATION.md"
    fm = parse_frontmatter(mig.read_text(encoding="utf-8"))
    current = (fm.get("current") or "").split("#")[0].strip() or None
    raw = (fm.get("layout_need_update") or "[]").split("#")[0]
    need = [v.strip() for v in raw.strip().strip("[]").split(",") if v.strip()]
    return current, need


def _vtuple(v):
    try:
        return tuple(int(x) for x in str(v).strip().split("."))
    except (ValueError, AttributeError):
        return None


def _workflow_fms(deck):
    """Yield parsed frontmatter dicts for every spec/plan file (skip INDEX)."""
    for kind in ("specs", "plans"):
        folder = Path(deck) / kind
        if folder.is_dir():
            for p in folder.glob("*.md"):
                if p.name != "INDEX.md":
                    yield parse_frontmatter(p.read_text(encoding="utf-8"))


def _active_inbound_targets(deck):
    """deck 内任何 status:active 工件经结构化边（implements:/superseded_by）指向的目标路径集。"""
    deck = Path(deck)
    targets = set()
    for kind in ("specs", "plans") + tuple(sorted(KNOWLEDGE_KINDS)):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for p in folder.rglob("*.md"):       # rglob：覆盖嵌套 area
            if p.name == "INDEX.md":
                continue
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("status") != "active":
                continue
            for field in ("implements", "superseded_by"):
                v = fm.get(field)
                if v:
                    targets.add(v.strip())
    return targets


def archivable_done(deck):
    """无 active 入边指向的 done workflow 工件（specs/plans）——可安全归档，确定性、可复现。"""
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


def _structural_signal(deck):
    """True if the deck shows any pre-3.0-coherence structural signal."""
    deck = Path(deck)
    if (deck / "charts").is_dir() or (deck / "landed").is_dir():
        return True  # 旧主流前名 → 需改名迁移（charts→references / landed→archive）
    if (deck / "sketches").is_dir() or (deck / "debriefs").is_dir():
        return True
    if any(fm.get("status") in RETIRED_STATUSES for fm in _workflow_fms(deck)):
        return True
    cockpit = deck / "cockpit.md"
    if cockpit.is_file() and "<!-- AUTO:inprogress -->" not in cockpit.read_text(encoding="utf-8"):
        return True
    return False


def _classify_version(deck_v, current, need):
    """Pure version-number classifier (no filesystem)."""
    dv = _vtuple(deck_v)
    if deck_v is None or dv is None:
        return "structural-behind"  # 无 version / 不可解析 → 需迁移
    for n in need:
        nv = _vtuple(n)
        if nv and dv < nv:
            return "structural-behind"
    cv = _vtuple(current)
    if cv and dv < cv:
        return "compatible-behind"
    return "current"


def layout_verdict(deck):
    """Machine verdict on a deck's layout currency.

    One of: 'structural-behind' | 'malformed' | 'compatible-behind' | 'current'.
    Read-only. Version data comes from MIGRATION.md frontmatter (not prose).
    """
    if _structural_signal(deck):
        return "structural-behind"
    current, need = _migration_layout()
    deck_v = _fm_field(Path(deck) / "rules.md", "version")
    vclass = _classify_version(deck_v, current, need)
    if vclass == "structural-behind":
        return vclass
    # 版本不落后 → 再查 malformed（缺必需 workflow 字段）
    for fm in _workflow_fms(deck):
        if fm.get("status") == "scrapped":
            continue
        if "status" not in fm or "summary" not in fm:
            return "malformed"
    return vclass


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
            if name in NESTABLE_KINDS:
                for area in sorted(d for d in folder.iterdir() if d.is_dir()):
                    if (area / "INDEX.md").is_file() or any(area.glob("*.md")):
                        yield f"{name}/{area.name}", area / "INDEX.md", regen_folder_index(area)
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
    ap.add_argument(
        "--verdict",
        action="store_true",
        help="print the deck's layout verdict (current/compatible-behind/structural-behind/malformed) and exit",
    )
    ap.add_argument(
        "--archivable",
        action="store_true",
        help="print the deck's archivable done set (one path per line) and exit; read-only",
    )
    args = ap.parse_args(argv)

    if args.verdict:
        print(layout_verdict(args.deck))
        return 0

    if args.archivable:
        for rel in archivable_done(args.deck):
            print(rel)
        return 0

    mismatch = version_mismatch(args.deck)
    if mismatch and not args.force:
        print(
            f"version guard: deck version {mismatch[0]} != script expects {mismatch[1]}; "
            "regenerate by hand (manual fallback) or pass --force"
        )
        return 2

    drift = []
    for label, path, new_block in _index_targets(args.deck):
        try:
            current = path.read_text(encoding="utf-8")
            cur_block = current[current.index("<!-- AUTO:") : current.index(AUTO_END) + len(AUTO_END)]
        except (OSError, ValueError):
            # 缺 INDEX.md 或无 AUTO 块：算 drift；非 --check 时新建一个最小 INDEX
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
