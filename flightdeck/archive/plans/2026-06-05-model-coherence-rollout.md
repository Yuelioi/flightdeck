---
status: done
summary: 实施模型理清 spec：脚本层(改名 charts→references/landed→archive、认 docs、knowledge 嵌套 INDEX-of-INDEXes、可归档 done 集、scrapped 分组、旧名结构信号, TDD) → lint/init/new → 模型文档(protocol/folder-semantics/templates/exit-ritual) → 4 skill 行为(status/landing/preflight/walkaround) → scaffold+MIGRATION+README → dogfood 迁移本仓库 + 全套验证 + 发布提醒
last_updated: 2026-06-05
implements: archive/specs/2026-06-05-model-coherence-mainstream-naming-design.md
---

# 模型理清 + 主流命名铁律 — 实施

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 [spec](../specs/2026-06-05-model-coherence-mainstream-naming-design.md) 落地——status⟂location 概念修复、done end-of-turn 防抖接力 landing、归档判据降为脚本可算的确定性结构边、数据文件夹改主流名（`charts→references`、`landed→archive`）+ 新增可嵌套 `docs/`、knowledge 按 area 嵌套撑大型项目。

**Architecture:** 先在 `scripts/flightdeck_index.py` 落确定性事实（改名常量、认 docs、knowledge 嵌套 INDEX-of-INDEXes、`archivable_done` 可归档集、scrapped 分组、旧名结构信号，TDD）；再让其余脚本（lint/init/new）认新结构；然后改模型文档（protocol/folder-semantics/templates/exit-ritual 是单一权威，skill 只指向）；再改 4 个 skill 行为；最后 scaffold + MIGRATION + README，并 dogfood 迁移本仓库、跑全套验证。

**Tech Stack:** Python 3.8+ 纯 stdlib（`unittest`，`uv run`）；Markdown skill/scaffold/doc 文件。

**实施约定（每个 commit 都遵守）：**
- commit body 用**中文**（见 `flightdeck/checklists/commits.md`）。
- 多行 commit message 不要用 Bash 工具传 PowerShell here-string（见 `flightdeck/incidents/powershell-herestring-in-bash-tool.md`）——本计划所有 commit 用**单行** `-m` 消息。
- 脚本一律 `uv run`（dogfood House Rule）。
- 测试统一：`uv run -m pytest scripts/tests/test_flightdeck_index.py -v`。
- **Phase 边界可独立 land**：每个 Phase 末尾状态自洽、可单独 review。
- `flightdeck/landed/`（迁移后 `flightdeck/archive/`）下的历史文件**一律不改**——它们是历史，rename 用 `git mv` 保留。

---

## Phase 1 — 脚本层 `flightdeck_index.py`（TDD）

所有改动在 `scripts/flightdeck_index.py`，测试在 `scripts/tests/test_flightdeck_index.py`。

### Task 1.1: 改名常量 + 认 docs（charts→references、加 docs/archive 概念）

**Files:**
- Modify: `scripts/flightdeck_index.py:20-29`（常量区）、`:120-127`（`charts_summary`）、`:214-215`（`REGEN_FOLDERS`）
- Test: `scripts/tests/test_flightdeck_index.py:27-39`（`ModelV4ConstantsTest`）

- [ ] **Step 1: 改测试断言新常量**（先改现有断言使其失败）——把 `ModelV4ConstantsTest` 替换为：

```python
class ModelConstantsTest(unittest.TestCase):
    def test_status_order_is_four_states(self):
        self.assertEqual(STATUS_ORDER, ["idea", "active", "done", "scrapped"])

    def test_summary_kinds(self):
        self.assertEqual(SUMMARY_KINDS, {"specs", "plans"})

    def test_knowledge_kinds_includes_docs(self):
        self.assertEqual(flightdeck_index.KNOWLEDGE_KINDS, {"checklists", "incidents", "docs"})

    def test_imported_kinds_is_references(self):
        self.assertEqual(flightdeck_index.IMPORTED_KINDS, {"references"})

    def test_folder_order_mainstream_names(self):
        self.assertEqual(
            FOLDER_ORDER, ["specs", "plans", "incidents", "checklists", "docs", "references"]
        )
        self.assertNotIn("charts", FOLDER_ORDER)
        self.assertNotIn("landed", FOLDER_ORDER)

    def test_nestable_kinds_are_knowledge(self):
        self.assertEqual(
            flightdeck_index.NESTABLE_KINDS, {"incidents", "checklists", "docs", "references"}
        )
```

并把文件顶部 import 块（`:9-22`）里的 `charts_summary` 改为 `imported_summary`，新增 `KNOWLEDGE_KINDS`。

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k Constants -v`
Expected: FAIL（`IMPORTED_KINDS`/`NESTABLE_KINDS` 不存在、`FOLDER_ORDER` 仍含 charts）

- [ ] **Step 3: 改实现** — 常量区（`:20-29`）改为：

```python
STATUS_ORDER = ["idea", "active", "done", "scrapped"]
DASH = "—"

SUMMARY_KINDS = {"specs", "plans"}                       # workflow，summary 行
KNOWLEDGE_KINDS = {"checklists", "incidents", "docs"}    # 自撰知识，auto-INDEX，knowledge 行
IMPORTED_KINDS = {"references"}                          # 外部导入，手维护 INDEX，"imported" 汇总
NESTABLE_KINDS = {"incidents", "checklists", "docs", "references"}  # 可按 area 嵌套（knowledge）

# 主流命名后的 root-INDEX 顺序（设计读序，非字母序）。
FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "docs", "references"]
```

把 `charts_summary`（`:120-127`）改名 `imported_summary` 并泛化（`references/` 仍是手维护导入）：

```python
def imported_summary(folder):
    """references/（旧 charts/）是手维护的外部导入，按条目数汇总。"""
    idx = (Path(folder) / "INDEX.md").read_text(encoding="utf-8")
    start = idx.index("<!-- AUTO:")
    end = idx.index(AUTO_END)
    n = sum(1 for line in idx[start:end].splitlines() if line.startswith("- "))
    return f"{n} project imported"
```

`REGEN_FOLDERS`（`:214-215`）改为排除 IMPORTED_KINDS（references INDEX 手维护）：

```python
# references/ 的 INDEX 手维护（外部导入）；只它的 root 行派生。
REGEN_FOLDERS = [name for name in FOLDER_ORDER if name not in IMPORTED_KINDS]
```

- [ ] **Step 4: 跑测试确认通过 + 全文件回归**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: Constants PASS；其余仍引用 `charts_summary` 的测试会 FAIL（下一步修）。先确保 Constants 绿。

- [ ] **Step 5: 修测试里残留的 charts 引用** — 把 test 文件里 import 的 `charts_summary` → `imported_summary`，并把任何构造 `charts/` 的 fixture 改 `references/`（`-k Root` / `-k summary` 相关用例）。重跑全文件：

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全 PASS

- [ ] **Step 6: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "refactor(flightdeck): index 常量改主流名（charts→references、加 docs/KNOWLEDGE_KINDS/NESTABLE_KINDS）"
```

### Task 1.2: root INDEX 认 docs（status 行）+ references（imported 行）

**Files:**
- Modify: `scripts/flightdeck_index.py:129-140`（`regen_root_index`）
- Test: `scripts/tests/test_flightdeck_index.py`（`RootIndexTest` 追加/改）

- [ ] **Step 1: 写失败测试** — 追加：

```python
class RootIndexDocsTest(unittest.TestCase):
    def _deck(self, root):
        deck = Path(root)
        for k in ("specs", "plans", "incidents", "checklists", "docs", "references"):
            (deck / k).mkdir()
        (deck / "docs" / "arch.md").write_text(
            "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
            encoding="utf-8",
        )
        (deck / "references" / "INDEX.md").write_text(
            "# references\n<!-- AUTO:references -->\n- [rfc.md](rfc.md)\n<!-- /AUTO -->\n", encoding="utf-8"
        )
        (deck / "INDEX.md").write_text(
            "# INDEX\n<!-- AUTO:root -->\n\n<!-- /AUTO -->\n", encoding="utf-8"
        )
        return deck

    def test_root_has_docs_status_row_and_references_imported_row(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            block = flightdeck_index.regen_root_index(deck)
            self.assertIn("docs/ — 1 active", block)
            self.assertIn("references/ — 1 project imported", block)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k RootIndexDocs -v`
Expected: FAIL（references 行用了 folder_summary 而非 imported；或 docs 缺）

- [ ] **Step 3: 改实现** — `regen_root_index`（`:129-140`）把 charts 特判改 IMPORTED_KINDS：

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k RootIndexDocs -v`
Expected: PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): root INDEX 认 docs（status 行）+ references（imported 行）"
```

### Task 1.3: specs/INDEX 增 `### 已否决（scrapped）` 分组

**Files:**
- Modify: `scripts/flightdeck_index.py:169-183`（`_specs_grouped_body`）
- Test: `scripts/tests/test_flightdeck_index.py`（`SpecsGroupedTest` 追加）

- [ ] **Step 1: 写失败测试**

```python
class SpecsScrappedGroupTest(unittest.TestCase):
    def test_scrapped_listed_in_own_group(self):
        with tempfile.TemporaryDirectory() as d:
            specs = Path(d) / "specs"
            specs.mkdir()
            (specs / "idea-x.md").write_text("---\nstatus: idea\nsummary: i\n---\n", encoding="utf-8")
            (specs / "2026-06-01-a.md").write_text("---\nstatus: active\nsummary: a\n---\n", encoding="utf-8")
            (specs / "2026-05-01-dead.md").write_text("---\nstatus: scrapped\nsummary: d\n---\n", encoding="utf-8")
            block = flightdeck_index.regen_folder_index(specs)
            self.assertIn("### 待启动（idea）", block)
            self.assertIn("### 进行中·完成（active·done）", block)
            self.assertIn("### 已否决（scrapped）", block)
            self.assertIn("2026-05-01-dead.md", block)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k Scrapped -v`
Expected: FAIL（scrapped 当前被排除）

- [ ] **Step 3: 改实现** — `_specs_grouped_body` 末尾追加 scrapped 分组：

```python
def _specs_grouped_body(folder, names):
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
```

（`folder_summary` 仍排除 scrapped——root 计数不含已否决，与 spec 一致；scrapped 仅在 specs/INDEX 单列可见。）

- [ ] **Step 4: 跑测试确认通过 + specs 类回归**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k "Specs or Scrapped" -v`
Expected: 全 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): specs/INDEX 增 已否决（scrapped）分组（可见但隔离待启动池）"
```

### Task 1.4: `archivable_done` — 确定性可归档集（无 active 入边）

**Files:**
- Modify: `scripts/flightdeck_index.py`（`_workflow_fms` 附近新增）
- Test: `scripts/tests/test_flightdeck_index.py`（新增 `ArchivableDoneTest`）

- [ ] **Step 1: 写失败测试**

```python
class ArchivableDoneTest(unittest.TestCase):
    def _deck(self, root):
        deck = Path(root)
        (deck / "specs").mkdir()
        (deck / "plans").mkdir()
        return deck

    def test_done_spec_with_active_plan_implements_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "specs" / "2026-06-01-a.md").write_text("---\nstatus: done\nsummary: a\n---\n", encoding="utf-8")
            (deck / "plans" / "2026-06-02-p.md").write_text(
                "---\nstatus: active\nsummary: p\nimplements: specs/2026-06-01-a.md\n---\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.archivable_done(deck), [])

    def test_done_spec_with_no_active_inbound_is_archivable(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "specs" / "2026-06-01-a.md").write_text("---\nstatus: done\nsummary: a\n---\n", encoding="utf-8")
            (deck / "plans" / "2026-06-02-p.md").write_text(
                "---\nstatus: done\nsummary: p\nimplements: specs/2026-06-01-a.md\n---\n", encoding="utf-8"
            )
            self.assertEqual(
                flightdeck_index.archivable_done(deck),
                ["plans/2026-06-02-p.md", "specs/2026-06-01-a.md"],
            )
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k Archivable -v`
Expected: FAIL（`archivable_done` 不存在）

- [ ] **Step 3: 实现** — 新增（紧随 `_workflow_fms`）：

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k Archivable -v`
Expected: 2 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): archivable_done 确定性可归档集（无 active 入边 implements/superseded_by）"
```

### Task 1.5: `--archivable` CLI（landing 快路读取可归档集）

**Files:**
- Modify: `scripts/flightdeck_index.py:354-402`（`main`）
- Test: `scripts/tests/test_flightdeck_index.py`（`ArchivableCliTest`）

- [ ] **Step 1: 写失败测试**

```python
class ArchivableCliTest(unittest.TestCase):
    def test_archivable_flag_prints_paths_writes_nothing(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "2026-06-01-a.md").write_text("---\nstatus: done\nsummary: a\n---\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--archivable"])
            self.assertEqual(rc, 0)
            self.assertIn("specs/2026-06-01-a.md", buf.getvalue())
            self.assertFalse((deck / "INDEX.md").exists())
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k ArchivableCli -v`
Expected: FAIL（`unrecognized arguments: --archivable`）

- [ ] **Step 3: 实现** — argparse 加 flag，并在 `--verdict` 同位置（版本守卫前、只读）处理：

```python
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
```

- [ ] **Step 4: 跑测试确认通过 + 全文件回归**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): index 加 --archivable 只读子命令（landing 快路）"
```

### Task 1.6: 旧名结构信号（`charts/`/`landed/` 存在 → structural-behind）

**Files:**
- Modify: `scripts/flightdeck_index.py:255-265`（`_structural_signal`）
- Test: `scripts/tests/test_flightdeck_index.py`（`LayoutVerdictTest` 追加）

- [ ] **Step 1: 写失败测试** — 在 `LayoutVerdictTest`（用其 `_deck` helper）追加：

```python
    def test_legacy_charts_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "charts").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_legacy_landed_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "landed").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k "legacy_charts or legacy_landed" -v`
Expected: FAIL（返回 current）

- [ ] **Step 3: 实现** — `_structural_signal` 顶部加旧名探测：

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k LayoutVerdict -v`
Expected: 全 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): 旧名 charts//landed/ 存在判 structural-behind（驱动改名迁移）"
```

### Task 1.7: knowledge 嵌套 INDEX-of-INDEXes（撑大型项目）

> 最大单任务。nestable knowledge 文件夹含子目录(area)时，顶层 INDEX 列 area（带一句用途 + last_updated），各 area 自带 INDEX。无子目录时退化为现扁平行为。area 的用途/日期取自该 area `INDEX.md` 的 `purpose:`/`last_updated:` frontmatter（缺则用占位）。

**Files:**
- Modify: `scripts/flightdeck_index.py:143-166`（`regen_folder_index`）、`:320-331`（`_index_targets` 让嵌套 area 的 INDEX 也进 regen 目标）
- Test: `scripts/tests/test_flightdeck_index.py`（新增 `NestedIndexTest`）

- [ ] **Step 1: 写失败测试**

```python
class NestedIndexTest(unittest.TestCase):
    def test_top_index_lists_areas_with_purpose_and_date(self):
        with tempfile.TemporaryDirectory() as d:
            docs = Path(d) / "docs"
            (docs / "runtime").mkdir(parents=True)
            (docs / "runtime" / "INDEX.md").write_text(
                "---\npurpose: 运行时子系统\nlast_updated: 2026-06-05\n---\n"
                "# docs/runtime\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            (docs / "runtime" / "loop.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
                encoding="utf-8",
            )
            (docs / "INDEX.md").write_text("# docs\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            top = flightdeck_index.regen_folder_index(docs)
            self.assertIn("[runtime/](runtime/INDEX.md)", top)
            self.assertIn("运行时子系统", top)
            self.assertIn("2026-06-05", top)
            # area 自身 INDEX 也能 regen 出文件行
            area = flightdeck_index.regen_folder_index(docs / "runtime")
            self.assertIn("loop.md", area)

    def test_flat_docs_without_subdirs_behaves_flat(self):
        with tempfile.TemporaryDirectory() as d:
            docs = Path(d) / "docs"
            docs.mkdir()
            (docs / "arch.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
                encoding="utf-8",
            )
            (docs / "INDEX.md").write_text("# docs\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            block = flightdeck_index.regen_folder_index(docs)
            self.assertIn("arch.md", block)
            self.assertNotIn("INDEX.md](", block)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k Nested -v`
Expected: FAIL

- [ ] **Step 3: 实现** — 新增 area 行渲染 + 嵌套分支；改 `regen_folder_index`：

```python
def _area_row(area_dir):
    """顶层 INDEX 里一个 area 的行：链接 + 用途 + last_updated（取 area/INDEX.md frontmatter）。"""
    idx = area_dir / "INDEX.md"
    fm = parse_frontmatter(idx.read_text(encoding="utf-8")) if idx.is_file() else {}
    purpose = fm.get("purpose", "⚠ purpose 缺失")
    updated = fm.get("last_updated", "—")
    return f"- [{area_dir.name}/]({area_dir.name}/INDEX.md) {DASH} {purpose} {DASH} last_updated: {updated}"


def regen_folder_index(folder):
    folder = Path(folder)
    kind = folder.name
    if kind == "specs":
        names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
        return f"<!-- AUTO:{kind} -->\n{_specs_grouped_body(folder, names)}\n{AUTO_END}"
    # nestable knowledge with subdirectories → INDEX-of-INDEXes（area 行 + 任何顶层文件行）
    subdirs = sorted((d for d in folder.iterdir() if d.is_dir()), key=lambda p: p.name)
    if kind in NESTABLE_KINDS and subdirs:
        rows = [_area_row(d) for d in subdirs]
        # nestable 文件夹的 kind 用 KNOWLEDGE row（docs/incidents/checklists）；references 顶层文件少见，按 knowledge 容错
        row_kind = kind if kind in KNOWLEDGE_KINDS else "checklists"
        top_files = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
        rows += [format_row(row_kind, n, parse_frontmatter((folder / n).read_text(encoding="utf-8"))) for n in top_files]
        return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"
    # flat
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    row_kind = kind if kind in (SUMMARY_KINDS | KNOWLEDGE_KINDS) else "checklists"
    rows = [format_row(row_kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8"))) for name in names]
    return f"<!-- AUTO:{kind} -->\n" + "\n".join(rows) + f"\n{AUTO_END}"
```

> 注：`format_row` 现支持 `SUMMARY_KINDS`/`KNOWLEDGE_KINDS`；docs ∈ KNOWLEDGE_KINDS 已被它认。`references` 顶层文件按 knowledge 行容错（其 INDEX 实际手维护，少经此路）。

并让 `_index_targets`（`:320-331`）把 nestable area 的 INDEX 也纳入 regen——在 `for name in REGEN_FOLDERS` 循环内，对 nestable 文件夹递归其 area：

```python
def _index_targets(deck):
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
```

- [ ] **Step 4: 跑测试确认通过 + 全文件回归**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全 PASS（含 Nested + 原有扁平用例无回归）

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): knowledge 嵌套 INDEX-of-INDEXes（area 行带用途+last_updated；area INDEX 进 regen）"
```

---

## Phase 2 — 其余脚本认新结构（lint / init / new）

> 节奏：Read 定位 → Edit → 跑该脚本测试 → commit。

### Task 2.1: `flightdeck_lint.py` 认 references/archive/docs + scrapped 行

**Files:**
- Modify: `scripts/flightdeck_lint.py`
- Test: `scripts/tests/test_flightdeck_lint.py`

- [ ] **Step 1: Read** `scripts/flightdeck_lint.py` 全文 + `scripts/tests/test_flightdeck_lint.py`，定位硬编码 `charts`/`landed` 的常量与 Audit（status 合法性、stray、INDEX↔folder、`landed/` 终态）。
- [ ] **Step 2: Edit** —
  - 文件夹名集：`charts→references`、`landed→archive`、新增 `docs`（knowledge）。复用/对齐 `flightdeck_index` 的 `KNOWLEDGE_KINDS`/`IMPORTED_KINDS`/`NESTABLE_KINDS` 若已 import。
  - status 合法性：`docs` 走 knowledge 三态；`references` 顶层文件走 knowledge 三态（嵌套 area 同）。
  - stray/known-folders 集合更新为主流名 + `docs`；nestable 文件夹的 `<area>/` 子目录**不算 stray**。
  - `archive/`（旧 `landed/`）终态审计路径名更新。
  - scrapped specs 现在 specs/INDEX **有行**（`### 已否决`）——若 lint 复用 `flightdeck_index` 生成对比，自动跟随；若 lint 自带 specs 行检查，更新为"scrapped 在已否决组、不在待启动池"。
- [ ] **Step 3: 跑测试** — `uv run -m pytest scripts/tests/test_flightdeck_lint.py -v`；按新结构更新/补 fixture 直至全绿。
- [ ] **Step 4: commit**

```bash
git add scripts/flightdeck_lint.py scripts/tests/test_flightdeck_lint.py
git commit -m "refactor(flightdeck): lint 认 references/archive/docs + 嵌套 area + scrapped 行"
```

### Task 2.2: `flightdeck_init.py` scaffold 改主流名 + 建 docs/

**Files:**
- Modify: `scripts/flightdeck_init.py`
- Test: `scripts/tests/test_flightdeck_init.py`

- [ ] **Step 1: Read** 两文件，定位 scaffold 落盘的文件夹清单与断言（现含 `charts`/`landed`）。
- [ ] **Step 2: Edit** — 建 deck 时建 `references/`（非 charts）、`archive/`（非 landed）、新增 `docs/` + 各自 `INDEX.md`；`archive/HISTORY.md`（no-git 时，路径由 landed→archive）。
- [ ] **Step 3: 改测试断言** — 断言新 scaffold 含 `references/INDEX.md`/`archive/`/`docs/INDEX.md`，不含 `charts/`/`landed/`。`uv run -m pytest scripts/tests/test_flightdeck_init.py -v` 直至绿。
- [ ] **Step 4: commit**

```bash
git add scripts/flightdeck_init.py scripts/tests/test_flightdeck_init.py
git commit -m "refactor(flightdeck): init scaffold 改 references/archive + 建 docs/"
```

### Task 2.3: `flightdeck_new.py` 支持 docs kind

**Files:**
- Modify: `scripts/flightdeck_new.py`
- Test: `scripts/tests/test_flightdeck_new.py`

- [ ] **Step 1: Read** 两文件，定位 kind→folder 常量表与 chart→charts 映射。
- [ ] **Step 2: Edit** — kind 表把 `chart → references`（沿用旧 `chart` 关键词指向新 references 文件夹，或加 `reference` 关键词）、新增 `doc → docs`（知识类 frontmatter：`status: active` + `when_to_read` + `applies_to` + `last_updated` + `summary`）；docs 落 `flightdeck/docs/`（顶层；嵌套 area 由用户后续手建）。
- [ ] **Step 3: 跑测试** — 补 docs kind 用例，`uv run -m pytest scripts/tests/test_flightdeck_new.py -v` 绿。
- [ ] **Step 4: commit**

```bash
git add scripts/flightdeck_new.py scripts/tests/test_flightdeck_new.py
git commit -m "feat(flightdeck): /flightdeck:new 支持 doc kind + chart→references"
```

---

## Phase 3 — 模型文档（单一权威：protocol / folder-semantics / templates / exit-ritual）

> 这四份是模型的权威文本；skill 只指向它们。改动用 Read→Edit→Grep 校验→commit。

### Task 3.1: `protocol.md` — 正交轴 + 权威翻转表 + 接缝 + 命名铁律 + 确定性归档

**Files:** Modify `skills/preflight/protocol.md`

- [ ] **Step 1: Read** 全文，定位：`## Status (label + recommended flow)`（含第 112 行 `done = ... archived to landed/`）、folder map（`landed/`/`charts/`）、`## Rule resolution order` 标准短语表、source-of-truth precedence。
- [ ] **Step 2: Edit** —
  - **命名铁律**（新增小节）：航空名只留指令/仪式/cockpit；数据模型全主流。
  - **status⟂location**：改 `done = complete, archived to landed/` → `done = 工作完成；留在源文件夹直到 landing 把它归档进 archive/（done ≠ archived）`；新增"location 是一等派生概念（驱动路由 + 归档），非 frontmatter 字段"；`archived` 不是状态值。
  - **权威翻转表**：贴 spec ② 的表（含直跳 active、scrapped 仅用户显式、done 是 status/landing 接缝）。
  - **接缝**：done = landing 触发点；end-of-turn 防抖；归档判据 = 确定性结构边（`flightdeck_index` 算）。
  - **landing 自动触发**进 Rule resolution order（消除悬空引用）+ 标准短语表加 `landing: nudge on done, don't auto-run`。
  - folder map：`charts→references`、`landed→archive`、加 `docs/`；precedence 行 `landed→archive`；嵌套按轴（knowledge 可 / workflow 不可）。
- [ ] **Step 3: 校验**

Grep（在 `skills/preflight/protocol.md`）：`archived to landed|charts/` → 0 命中；`references/|archive/|docs/|location|end-of-turn|landing: nudge` → 命中。
- [ ] **Step 4: commit**

```bash
git add skills/preflight/protocol.md
git commit -m "docs(flightdeck): protocol 立命名铁律 + status⟂location + 权威翻转表 + 接缝 + 确定性归档 + 改名"
```

### Task 3.2: `folder-semantics.md` — 改名 + docs/ 段 + 按轴嵌套 + scrapped 可见

**Files:** Modify `skills/preflight/folder-semantics.md`

- [ ] **Step 1: Read** 全文（已知：`## Which folder?` 表、folder 树、各 folder 段、`## Multi-file topics — no subfolders`、scrapped 段、anti-patterns）。
- [ ] **Step 2: Edit** —
  - 全文 `charts→references`、`landed→archive`（含树、表、各段、Anti-pattern）。
  - `## Which folder?` 表：加 `docs/`（自撰常驻技术资料，解释性）；`checklists/` 描述去掉"reference"措辞，明确为"过程/规范（执行）"。
  - 新增 `### docs/ — 技术资料` 段（spec ④ 四条边界 + 混合型裁决判据 + 命名 `<topic>.md` + 知识类 frontmatter）。
  - `## Multi-file topics` 改为**按轴嵌套**：knowledge（incidents/checklists/docs/references）可按 area 子目录 + INDEX-of-INDEXes；workflow（specs/plans）严格扁平（理由：排空 vs 累积）。删"仅 charts 可嵌套"旧表述，扩为 NESTABLE_KINDS。
  - scrapped 段：改"排除出 INDEX" → "specs/INDEX 单列 `### 已否决（scrapped）` 分组（可见但不进待启动池）"。
  - `archive/` 段：补"一级结构容器但非 kind"。
- [ ] **Step 3: 校验**

Grep：`charts|landed/` → 仅剩 `archive/` 与历史说明；`docs/ —|已否决|按 area|INDEX-of-INDEXes` → 命中。
- [ ] **Step 4: commit**

```bash
git add skills/preflight/folder-semantics.md
git commit -m "docs(flightdeck): folder-semantics 改名 + docs/ 段 + 按轴嵌套 + scrapped 可见"
```

### Task 3.3: `templates.md` — docs frontmatter + 改名

**Files:** Modify `skills/preflight/templates.md`

- [ ] **Step 1: Read** 全文，定位 knowledge frontmatter 块、INDEX 模板、rules.md/cockpit 模板、`charts`/`landed` 字样。
- [ ] **Step 2: Edit** —
  - 加 `## docs frontmatter` 块（知识类：`status: active` + `when_to_read` + `applies_to` + `last_updated` + `summary`；嵌套 area 的 `INDEX.md` 额外可带 `purpose:` + `last_updated:`）。
  - 全文 `charts→references`、`landed→archive`。
  - 加 area `INDEX.md` 模板（`purpose:`/`last_updated:` frontmatter + `<!-- AUTO:<kind> -->`）。
- [ ] **Step 3: 校验**

Grep：`charts|landed` → 0（除历史说明）；`docs frontmatter|purpose:` → 命中。
- [ ] **Step 4: commit**

```bash
git add skills/preflight/templates.md
git commit -m "docs(flightdeck): templates 加 docs/area frontmatter + 改名 references/archive"
```

### Task 3.4: `exit-ritual.md` — Land Routine 改名+确定性+排空，分类启发式加 docs，接力 end-of-turn

**Files:** Modify `skills/preflight/exit-ritual.md`

- [ ] **Step 1: Read** 全文（已知：决策树、`## Classification heuristics`（含 (e) charts）、`## Land Routine`、`## Land-readiness check`、Row format 段）。
- [ ] **Step 2: Edit** —
  - **Land Routine**：目标 `landed/ → archive/`（全段路径）；**归档判据改为读 `flightdeck_index --archivable` 的确定性集**（不再"AI 读引用边判断"）；新增"**每次 landing 扫全部 done-in-place、排空已解除入边的**"；保留 remap-before-move 的边重写逻辑。
  - **分类启发式**：(e) `imported external → charts/` 改 `references/`；新增 (e2 或并入 c/b 旁)：`自撰常驻技术资料（架构/理念/子系统参考）→ docs/`（与 checklists 区分：读懂 vs 执行）。Row format 段 `charts→references` + 加 docs（knowledge 行）。
  - **Land-readiness / 接力**：signal 1 触发的自动 landing 明确为 **end-of-turn 防抖聚合**（本轮多个 done → 一次 landing）；写明兼容窗口内 layout guard 使自动归档暂停的后果。
  - 决策树 Step 2 (e) `charts→references`。
- [ ] **Step 3: 校验**

Grep：`landed/|charts/` → 仅历史说明；`archive/|--archivable|end-of-turn|docs/` → 命中。
- [ ] **Step 4: commit**

```bash
git add skills/preflight/exit-ritual.md
git commit -m "docs(flightdeck): exit-ritual Land Routine 改名+确定性归档+排空，分类加 docs，接力 end-of-turn"
```

---

## Phase 4 — Skill 行为（status / landing / preflight / walkaround）

### Task 4.1: `status` — done end-of-turn 接力 + 不手写归档

**Files:** Modify `skills/status/SKILL.md`

- [ ] **Step 1: Read** 全文，定位 Step 6（done 翻转）、Step 7（land-readiness）、Don't do、`landed/`/`charts/` 字样。
- [ ] **Step 2: Edit** —
  - Step 7：done 翻转默认在 **end-of-turn** 接力一次 landing（防抖；非每个 done 立即跑）；House Rule `landing: nudge on done, don't auto-run` 可降级。
  - Don't do 加：「不手写归档标签 / 不在没跑 landing 时宣称已归档（`archived` 非状态值）」。
  - `landed/→archive/`、`charts/→references/`。
- [ ] **Step 3: 校验** Grep：`landed/|charts/` → 0；`end-of-turn|archive` → 命中。
- [ ] **Step 4: commit** `git commit -m "refactor(flightdeck): status done 翻转 end-of-turn 接力 landing + 禁手写归档标签"`

### Task 4.2: `landing` — 确定性归档 + 排空 + end-of-turn 防抖 + docs 分类 + 降级 + 兼容窗口

**Files:** Modify `skills/landing/SKILL.md`

- [ ] **Step 1: Read** 全文，定位 Step 0a（layout guard）、Step 2（分类）、Step 3a（Land Routine 调用）、commit 段、`landed/`/`charts/` 字样。
- [ ] **Step 2: Edit** —
  - Step 3a 归档：调 Land Routine，**用 `flightdeck_index --archivable` 的确定性集**；**每次扫全部 done-in-place 排空**；不再"AI 读引用边判断"。
  - 默认接力为 **end-of-turn 防抖聚合**；补 `landing: nudge on done, don't auto-run` 降级口。
  - 分类启发式加 `docs/`（自撰常驻技术资料）。
  - 兼容窗口后果：未迁移 deck 上 done 接力撞 layout guard → 报"先迁移"、自动归档暂停（已知代价、非 bug）。
  - `landed/→archive/`、`charts/→references/`。
- [ ] **Step 3: 校验** Grep：`landed/|charts/` → 0；`--archivable|end-of-turn|docs/|nudge on done` → 命中。
- [ ] **Step 4: commit** `git commit -m "refactor(flightdeck): landing 确定性归档(--archivable)+排空全部done+end-of-turn防抖+docs分类+降级口+兼容窗口"`

### Task 4.3: `preflight` — docs 进 catalog 预热 + 改名

**Files:** Modify `skills/preflight/SKILL.md`

- [ ] **Step 1: Read** 全文，定位 step 3（catalog 预热：现读 checklists/INDEX + incidents/INDEX）、输出格式、`landed/`/`charts/` 字样。
- [ ] **Step 2: Edit** —
  - catalog 预热加读 `docs/INDEX.md`（**仅顶层**；嵌套时是 area 行带用途+last_updated）；输出格式加 `[Docs]` 表（File + 用途/area）。明确"只读顶层 INDEX、不读正文、按需 Read"。
  - land-readiness/版本路径 `landed/→archive/`；`charts/→references/`（catalog 注释里 charts 仍是"外部导入"语义 → 改 references）。
- [ ] **Step 3: 校验** Grep：`landed/|charts/` → 0；`docs/INDEX|Docs` → 命中。
- [ ] **Step 4: commit** `git commit -m "refactor(flightdeck): preflight catalog 预热加 docs/（顶层 INDEX）+ 改名 references/archive"`

### Task 4.4: `walkaround` — 认 docs/嵌套/新名 + scrapped 行 + done-but-unlanded INFO

**Files:** Modify `skills/walkaround/SKILL.md`

- [ ] **Step 1: Read** 全文（已读：13 Audits）。定位 Audit 1/2/5/6/8/10/description，`charts`/`landed` 共 25 处。
- [ ] **Step 2: Edit** —
  - 全文 `charts→references`、`landed→archive`（含 description、Audit 1/2/5/6/8 的 known-folders、Audit 6 `landed/`→`archive/` 终态）。
  - knowledge folder 集合加 `docs`（Audit 1/2 三态 + 路由字段）；**nestable 文件夹的 `<area>/` 子目录不算 stray（Audit 8）**，且 area 的 `INDEX.md` 缺失 = WARNING（Audit 5 扩到嵌套 area）。
  - Audit 5/8：scrapped specs 现在 specs/INDEX **有 `### 已否决` 行**——改"scrapped 无行是对的"为"scrapped 在已否决组有行；缺行才 WARNING；仍不进待启动池/root 计数"。
  - **新 Audit（或并入 10/现有）：done-but-unlanded** —— 列 `status: done` 仍在源文件夹、且被某 `active` 工件结构化入边指向的工件为 **INFO**（带阻挡它的 active 工件名）；无入边却未归档的 done 提示"可 land"。可复用 `flightdeck_index --archivable` 作快路。
  - Audit 10：旧 `charts/`/`landed/` 存在 → `structural-behind`（指向 MIGRATION 改名节）。
- [ ] **Step 3: 校验** Grep：`charts|landed/` → 仅 `archive/` 与历史；`docs|已否决|done-but-unlanded|archivable` → 命中。
- [ ] **Step 4: commit** `git commit -m "refactor(flightdeck): walkaround 认 docs/嵌套/新名 + scrapped 行 + done-but-unlanded INFO"`

---

## Phase 5 — scaffold + MIGRATION + README/CHANGELOG

### Task 5.1: scaffold 改主流名 + 建 docs/

**Files:** Modify `scaffolds/full/flightdeck/`（`charts/INDEX.md`→`references/INDEX.md`、`landed/`→`archive/`、新增 `docs/INDEX.md`）

- [ ] **Step 1:** `git mv scaffolds/full/flightdeck/charts scaffolds/full/flightdeck/references` 与 `git mv scaffolds/full/flightdeck/landed scaffolds/full/flightdeck/archive`。
- [ ] **Step 2: Edit** — `references/INDEX.md` 标题/AUTO 标记 `charts→references`；`archive/HISTORY.md` 标题 landed→archive；新建 `scaffolds/full/flightdeck/docs/INDEX.md`（`# docs — INDEX` + 空 `<!-- AUTO:docs -->`/`<!-- /AUTO -->`）；`scaffolds/full/flightdeck/INDEX.md` root AUTO 加 `docs/` 行、`charts→references`。
- [ ] **Step 3: 校验** — `uv run scripts/flightdeck_index.py scaffolds/full/flightdeck --check`（空 scaffold 应 clean 或仅预期空块）；Grep scaffold 下 `charts|landed` → 0。
- [ ] **Step 4: commit** `git commit -m "refactor(flightdeck): scaffold 改 references/archive + 建 docs/INDEX"`

### Task 5.2: `MIGRATION.md` 增改名结构迁移节

**Files:** Modify `MIGRATION.md`

- [ ] **Step 1: Read** frontmatter（`current: 3.0`/`layout_need_update: [2.2, 3.0]`）。
- [ ] **Step 2: Edit** —
  - frontmatter `layout_need_update` 保持含 `3.0`（本批是 3.0 内结构改名；`3.0 ∈ need` 已使结构信号触发非静默 offer——与 model-v4 同机制）。
  - 新增 `### 3.0 — 主流命名 + docs/（BREAKING，结构）` 节：`charts/ → references/`（`git mv` + INDEX 标题）、`landed/ → archive/`（`git mv` + `HISTORY.md` 路径 + 边的 `landed/`→`archive/` 前缀重写）、新增 `docs/`（纯新增，缺则 walkaround INFO 补建）；检测 = `charts/`/`landed/` 目录存在（结构信号）；walkaround 提供、非静默。
- [ ] **Step 3: 校验** Grep：`references/|archive/|docs/` 在新节命中；frontmatter 未破坏。
- [ ] **Step 4: commit** `git commit -m "docs(flightdeck): MIGRATION 增 3.0 主流命名迁移（charts→references/landed→archive/+docs）"`

### Task 5.3: README / README.zh / CHANGELOG 对齐

**Files:** Modify `README.md`、`README.zh.md`、`CHANGELOG.md`

- [ ] **Step 1: Read** 三文件中 `charts`/`landed` 段（folder 列表/示意）。
- [ ] **Step 2: Edit** — `charts→references`、`landed→archive`、folder 列表加 `docs/`（技术资料）；CHANGELOG 写 3.0 条目（主流命名铁律 / docs/ + 嵌套 / status⟂location / 确定性归档 / done end-of-turn 接力）。
- [ ] **Step 3: 校验** Grep 三文件：`charts|landed`（除历史链接）→ 0；`references|archive|docs` → 命中。
- [ ] **Step 4: commit** `git commit -m "docs(flightdeck): README 双语 + CHANGELOG 对齐主流命名 + docs/"`

---

## Phase 6 — dogfood 迁移本仓库 + 验证 + 发布提醒

### Task 6.1: 迁移本仓库 deck（charts→references / landed→archive / repo docs→flightdeck/docs）

> ⚠ **执行时与用户确认一处**：repo 根 `docs/`（architecture/philosophy/comparison/lifecycle/README）是公开文档、README 可能链接它。把它迁入 `flightdeck/docs/` 是 spec 既定动作，但会改公开文档位置——确认"移动 + 更新 README 链接" vs "改为只在 flightdeck/docs/ 放新文件"。

**Files:** `flightdeck/charts/`→`flightdeck/references/`、`flightdeck/landed/`→`flightdeck/archive/`、repo `docs/*`→`flightdeck/docs/`、`flightdeck/INDEX.md`、`flightdeck/rules.md`

- [ ] **Step 1:** `git mv flightdeck/charts flightdeck/references`；`git mv flightdeck/landed flightdeck/archive`。
- [ ] **Step 2:** 建 `flightdeck/docs/`，`git mv docs/architecture.md flightdeck/docs/` 等五文件进去（或按用户确认的方案）；为每个补知识类 frontmatter（`status: active` + `when_to_read` + `applies_to: [skills, ...]` + `last_updated: 2026-06-05` + `summary`）；建 `flightdeck/docs/INDEX.md`。若保留公开 `docs/`，则改为在 `flightdeck/docs/` 放一份样例 + 更新 README 链接——以确认方案为准。
- [ ] **Step 3:** 边的 `landed/`→`archive/` 前缀重写（grep `flightdeck/` 下 frontmatter `implements/supersedes/related/superseded_by` 值里 `landed/`）；`flightdeck/rules.md` `version` 不变（仍 3.0）。
- [ ] **Step 4: regen** — `uv run scripts/flightdeck_index.py flightdeck`（生成 references/archive 后的 root + docs INDEX + cockpit）。
- [ ] **Step 5: commit** `git commit -m "chore(flightdeck): dogfood 迁移 deck 到主流命名（charts→references/landed→archive）+ 建 flightdeck/docs"`

### Task 6.2: 全套自动验证

- [ ] **Step 1:** `uv run -m pytest scripts/tests/ -v` → 全绿。
- [ ] **Step 2:** `uv run scripts/flightdeck_index.py flightdeck --check` → `clean`。
- [ ] **Step 3:** `uv run scripts/flightdeck_index.py flightdeck --verdict` → `current`（迁移后无旧名结构信号）。
- [ ] **Step 4:** `uv run scripts/flightdeck_index.py flightdeck --archivable` → 人工核对输出与预期 done-but-unlanded 一致。
- [ ] **Step 5:** `uv run scripts/flightdeck_lint.py flightdeck` → 无 CRITICAL/WARNING（或仅 INFO）。
- [ ] **Step 6: commit（若 regen 产生变更）** `git commit -m "chore(flightdeck): regen + 全套验证通过（pytest/--check/--verdict/lint clean）"`

### Task 6.3: reload dogfood + 状态翻转 + 发布提醒（人工）

- [ ] **Step 1:** 按 `flightdeck/checklists/local-plugin-testing.md` 同步插件缓存、reload。
- [ ] **Step 2: 交互 dogfood**（reload 后）—
  - `/flightdeck:preflight`：catalog 报出 `docs/` area？
  - 翻一个 done：**end-of-turn 一次** landing？归档走 `--archivable` 确定性集？done-but-unlanded 留原地且 walkaround INFO 可见？
  - `/flightdeck:walkaround`：认 references/archive/docs、嵌套 area、scrapped 行。
  - 造一个 `charts/` 空目录验证 walkaround 报 structural-behind（验完删）。
- [ ] **Step 3: 翻状态** — dogfood 通过后，本 spec+plan + 同簇（model-v4 / scriptable / 命令简化 / preflight-slim / new-artifact）按计划一起 `done`，交 `/flightdeck:landing` 确定性归档。
- [ ] **Step 4: 发布提醒** — 按 `flightdeck/checklists/version-bump.md` 写 CHANGELOG + marketplace + tag + 合并 → main。**本步交用户/发布流程，计划不自动发布。**

---

## 自检（spec 覆盖核对）

- 铁律（航空名只留交互面）→ Task 3.1。
- ① status⟂location / done≠archived / location 一等 / archived 非状态 → Task 3.1, 4.1。
- ② 权威翻转表（直跳 active / scrapped 仅人工 + 可见分组 / done 接缝）→ Task 1.3, 3.1, 4.4。
- ③ 接缝 + end-of-turn 防抖 + 确定性归档(--archivable) + 排空全部 done + 失败路径/done≠检查 + 降级口 + 兼容窗口 → Task 1.4/1.5, 3.4, 4.1/4.2。
- ④ docs/ 语义 + 四边界 + 混合裁决 + 按轴嵌套 + INDEX-of-INDEXes + preflight 顶层只读 + 全景命名 → Task 1.1/1.2/1.7, 2.x, 3.2/3.3, 4.3/4.4。
- 改名 charts→references / landed→archive（脚本/文档/scaffold/dogfood）→ Task 1.1/1.6, 2.x, 3.x, 4.x, 5.1, 6.1。
- scrapped 可见分组 → Task 1.3, 3.2, 4.4。
- 旧名结构信号 + 迁移 → Task 1.6, 5.2, 6.1。
- 非目标（不加反向索引/来源字段、不让 workflow 嵌套、不预载知识正文）→ 由确定性 `archivable_done`（只读结构边）+ 按轴嵌套 + preflight 顶层只读 体现，无新增字段任务。
- 验证 + dogfood → Task 6.2, 6.3。
