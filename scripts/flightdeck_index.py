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
import subprocess
import sys
from collections import Counter
from pathlib import Path

STATUS_ORDER = ["idea", "active", "done"]

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


def signature_fingerprint(symptom, error_type=""):
    """主指纹 = error_type + 归一化 symptom。where **不**进指纹（spec：symptom+error_type
    为主、where 为次/tiebreak，由调用方在多命中时区分）。"""
    key = f"{(error_type or '').strip()}\n{normalize_symptom(symptom)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def parse_signature(text):
    """抽 `## Signature` 块的 key:value 行为 dict（键 symptom/error_type/where/trigger）。
    无块返回 {}。值两端反引号/空白剥掉。"""
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
    """返回主指纹相同的 incident（含 status:obsolete——回归检测依赖）。
    扫 incidents/ 及 archive/incidents/ 全部 .md（含嵌套 area，rglob）；
    缺 ## Signature 的跳过（走 AI 模糊层）。
    每条 {path(相对 deck), status, where}。"""
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

SUMMARY_KINDS = {"specs", "plans"}                       # workflow，summary 行
KNOWLEDGE_KINDS = {"checklists", "incidents", "docs"}    # 自撰知识，auto-INDEX，knowledge 行
IMPORTED_KINDS = {"references"}                          # 外部导入，手维护 INDEX，"imported" 汇总
NESTABLE_KINDS = {"incidents", "checklists", "docs", "references"}  # 可按 area 嵌套（knowledge）

# 主流命名后的 root-INDEX 顺序（设计读序，非字母序）。
FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "docs", "references"]


def format_row(kind, filename, fm):
    """Render one folder-INDEX row for an artifact, by folder kind.

    Missing required fields are rendered with a visible sentinel rather than
    raising, so a malformed file never crashes a regen.
    """
    link = f"- [{filename}]({filename})"
    status = fm.get("status", "?")
    if kind in SUMMARY_KINDS:
        row = f"{link} {DASH} {status} {DASH} {fm.get('summary', '⚠ summary 缺失')}"
        if fm.get("verify"):
            row = "⚠未验证 " + row
        return row
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
        if fm.get("verify"):
            row = "⚠未验证 " + row
        elif status == "stale":
            row = "⚠待复核 " + row
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
        if kind in KNOWLEDGE_KINDS:   # obsolete 待排进 archive（archivable_obsolete），不进路由行；stale 进行但带 ⚠
            top_files = [n for n in top_files
                         if parse_frontmatter((folder / n).read_text(encoding="utf-8")).get("status") != "obsolete"]
        rows += [format_row(row_kind, n, parse_frontmatter((folder / n).read_text(encoding="utf-8"))) for n in top_files]
        return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    if kind in KNOWLEDGE_KINDS:   # obsolete 待排进 archive（archivable_obsolete），不进路由行；stale 进行但带 ⚠
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
        groups.append("### 待启动（idea）\n" + "\n".join(format_row("specs", n, fms[n]) for n in ideas))
    if active_done:
        groups.append("### 进行中·完成（active·done）\n" + "\n".join(format_row("specs", n, fms[n]) for n in active_done))
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


def _active_inbound_targets(deck):
    """deck 内任何 status:active 工件经结构化边（implements:）指向的目标路径集。"""
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
            for field in ("implements",):
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


def archivable_obsolete(deck):
    """status:obsolete 的 knowledge 工件（incidents/checklists/docs）——已死·待归档，
    与 archivable_done 对称：obsolete 是 knowledge 版 done 排水态，无钉扣概念
    （superseded_by 已退役），扫到即可排进 archive/。确定性、可复现。"""
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
    """最近一个带 Flightdeck-Sync trailer 的 commit SHA（上次退出仪式锚点），无则 None。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(deck), "log", "-1", "--grep=Flightdeck-Sync", "--format=%H"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def changed_since_anchor(deck):
    """自锚点以来变动的路径（committed + 工作树未提交），相对 repo 根。
    无锚点 → 退化成工作树改动（首跑/无历史仍给信号）。"""
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
    across the active tree AND archive/ — the 待验证 source of truth.
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
            cur_block = current[current.index("<!-- AUTO:") : current.index(AUTO_END) + len(AUTO_END)]
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
