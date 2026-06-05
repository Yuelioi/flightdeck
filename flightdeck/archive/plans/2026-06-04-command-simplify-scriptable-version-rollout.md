---
status: done
summary: 实施 spec：脚本层(layout_verdict + format_row 健壮性, TDD) → 5 skill 改(删 Gate / 智能 landing / commit 默认 / verdict 接线) → protocol + scaffold 模板 → MIGRATION + dogfood rules → 验证(pytest / --check / walkaround / reload dogfood) + 发布提醒
last_updated: 2026-06-04
implements: archive/specs/2026-06-04-command-simplify-scriptable-version-design.md
---

# 命令简化 + 版本检查脚本化 — 实施

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 flightdeck 的自治面收敛到"好默认 + 推断 + 判断"，并把版本/布局落后判定从"AI 读散文"降为一次廉价脚本 verdict。

**Architecture:** 先在 `scripts/flightdeck_index.py` 落一个纯函数 `layout_verdict(deck)`（机器事实，TDD），再让 5 个 skill 删掉 self-invoke Gate、接线 verdict、并改行为（智能 landing 归档 / commit 本地自调-push 先问 / 空文件夹宽容）；最后改 protocol、scaffold 模板、MIGRATION、dogfood rules，跑全套验证。

**Tech Stack:** Python 3.8+ 纯 stdlib（`unittest`，`uv run`）；Markdown skill/scaffold/doc 文件。

**实施约定（每个 commit 都遵守）：**
- commit body 用**中文**（见 `flightdeck/checklists/commits.md`）。
- 多行 commit message 不要用 Bash 工具传 PowerShell here-string（见 `flightdeck/incidents/powershell-herestring-in-bash-tool.md`）——本计划所有 commit 用**单行** `-m` 消息规避。
- 脚本一律 `uv run`（dogfood House Rule）。

---

## Phase 1 — 脚本层：`layout_verdict` + `format_row` 健壮性（TDD）

所有改动在 `scripts/flightdeck_index.py`，测试在 `scripts/tests/test_flightdeck_index.py`。运行测试统一用：
`uv run -m pytest scripts/tests/test_flightdeck_index.py -v`（或 `uv run scripts/tests/test_flightdeck_index.py` 走 unittest main）。

### Task 1: `format_row` 缺字段不再崩

**Files:**
- Modify: `scripts/flightdeck_index.py:32-52`（`format_row`）
- Test: `scripts/tests/test_flightdeck_index.py`（`FormatRowTest` 类内追加）

- [ ] **Step 1: 写失败测试** — 在 `FormatRowTest` 末尾追加：

```python
    def test_summary_kind_missing_summary_does_not_raise(self):
        # 缺 summary 的 workflow 文件不应让 regen 崩；用可见哨兵占位。
        row = format_row("specs", "foo.md", {"status": "active"})
        self.assertIn("foo.md", row)
        self.assertIn("⚠", row)

    def test_summary_kind_missing_status_does_not_raise(self):
        row = format_row("specs", "foo.md", {"summary": "x"})
        self.assertIn("foo.md", row)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k missing -v`
Expected: FAIL（`KeyError: 'summary'` / `'status'`）

- [ ] **Step 3: 改实现** — 把 `format_row` 里所有 `fm['status']` / `fm['summary']` / `fm['when_to_read']` / `fm['applies_to']` 直取改为带哨兵的 `.get`：

```python
def format_row(kind, filename, fm):
    """Render one folder-INDEX row for an artifact, by folder kind."""
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
        if kind == "incidents":
            try:
                n = int(fm.get("recurrences", "1"))
            except (TypeError, ValueError):
                n = 1
            if n > 1:
                row += f" {DASH} recur: {n}"
        return row
    raise ValueError(f"unknown folder kind: {kind}")
```

- [ ] **Step 4: 跑测试确认通过（含原有 FormatRow 测试不回归）**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k FormatRow -v`
Expected: 全部 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "fix(flightdeck): format_row 缺 summary/status 不再 KeyError，用哨兵占位"
```

### Task 2: `layout_verdict` — 结构信号 → `structural-behind`

**Files:**
- Modify: `scripts/flightdeck_index.py`（在 `version_mismatch` 附近，约 :218 后新增常量 + 函数）
- Test: `scripts/tests/test_flightdeck_index.py`（新增 `LayoutVerdictTest` 类）

- [ ] **Step 1: 写失败测试** — 新增类（注意 fixture 要带一个合法 `rules.md version: 3.0`，避免被版本分支抢先判定）：

```python
class LayoutVerdictTest(unittest.TestCase):
    def _deck(self, root, version="3.0"):
        deck = Path(root)
        (deck / "rules.md").write_text(
            f"---\nversion: {version}\n---\n", encoding="utf-8"
        )
        specs = deck / "specs"
        specs.mkdir()
        (specs / "2026-06-01-a.md").write_text(
            "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
        )
        (deck / "cockpit.md").write_text(
            "# Cockpit\n## 进行中\n<!-- AUTO:inprogress -->\n\n<!-- /AUTO -->\n## 下一步\n",
            encoding="utf-8",
        )
        return deck

    def test_sketches_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "sketches").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_debriefs_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "debriefs").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_retired_status_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "specs" / "2026-06-02-b.md").write_text(
                "---\nstatus: awaiting-review\nsummary: y\n---\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_cockpit_missing_auto_region_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "cockpit.md").write_text(
                "# Cockpit\n## Next session\n- do thing\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k LayoutVerdict -v`
Expected: FAIL（`AttributeError: module ... has no attribute 'layout_verdict'`）

- [ ] **Step 3: 实现结构信号部分** — 在 `version_mismatch` 上方新增常量与函数（先只覆盖结构分支，版本/malformed 占位为 `current` 由后续 Task 补全）：

```python
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


def _structural_signal(deck):
    deck = Path(deck)
    if (deck / "sketches").is_dir() or (deck / "debriefs").is_dir():
        return True
    if any(fm.get("status") in RETIRED_STATUSES for fm in _workflow_fms(deck)):
        return True
    cockpit = deck / "cockpit.md"
    if cockpit.is_file() and "<!-- AUTO:inprogress -->" not in cockpit.read_text(encoding="utf-8"):
        return True
    return False


def layout_verdict(deck):
    """Machine verdict on a deck's layout currency.

    One of: 'structural-behind' | 'malformed' | 'compatible-behind' | 'current'.
    Read-only. Version data comes from MIGRATION.md frontmatter (not prose).
    """
    if _structural_signal(deck):
        return "structural-behind"
    return "current"
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k LayoutVerdict -v`
Expected: 4 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): layout_verdict 结构信号判定（sketches/debriefs/retired/cockpit）"
```

### Task 3: `layout_verdict` — 版本号比对（structural / compatible / current）

**Files:**
- Modify: `scripts/flightdeck_index.py`（`layout_verdict`）
- Test: `scripts/tests/test_flightdeck_index.py`（`LayoutVerdictTest` 追加）

- [ ] **Step 1: 写失败测试** — 追加（依赖 bundled MIGRATION.md：`current=3.0`，`layout_need_update=[2.2, 3.0]`）：

```python
    def test_version_below_need_entry_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="2.3")  # 2.3 < 3.0（need 项）
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_no_version_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "rules.md").write_text("---\n---\n", encoding="utf-8")  # 无 version
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_current_version_clean_is_current(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="3.0")
            self.assertEqual(flightdeck_index.layout_verdict(deck), "current")
```

> 说明：当前 `current=3.0` 且 `3.0 ∈ layout_need_update`，所以任何 `< 3.0` 都判 structural；`compatible-behind`（版本 < current 但不 < 任何 need 项）只有在将来 current 越过最高 need 项时才出现。为锁定该逻辑，加一个**注入式**单元测试，不依赖真实 MIGRATION：

```python
    def test_compatible_behind_logic(self):
        # 直接验证比对逻辑：current=3.1, need=[2.2, 3.0], deck=3.0 → compatible
        self.assertEqual(
            flightdeck_index._classify_version("3.0", "3.1", ["2.2", "3.0"]),
            "compatible-behind",
        )
        self.assertEqual(
            flightdeck_index._classify_version("2.5", "3.0", ["2.2", "3.0"]),
            "structural-behind",
        )
        self.assertEqual(
            flightdeck_index._classify_version("3.0", "3.0", ["2.2", "3.0"]),
            "current",
        )
        self.assertEqual(
            flightdeck_index._classify_version(None, "3.0", ["2.2", "3.0"]),
            "structural-behind",
        )
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k "LayoutVerdict and (version or compatible or current)" -v`
Expected: FAIL（`_classify_version` 不存在 / 版本分支未实现）

- [ ] **Step 3: 实现版本分类 + 接入 `layout_verdict`** — 新增 `_classify_version`，并在 `layout_verdict` 里在结构信号之后调用：

```python
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
```

把 `layout_verdict` 改为：

```python
def layout_verdict(deck):
    if _structural_signal(deck):
        return "structural-behind"
    current, need = _migration_layout()
    deck_v = _fm_field(Path(deck) / "rules.md", "version")
    return _classify_version(deck_v, current, need)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k LayoutVerdict -v`
Expected: 全部 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): layout_verdict 版本号比对（structural/compatible/current）"
```

### Task 4: `layout_verdict` — `malformed`（缺必需字段）

**Files:**
- Modify: `scripts/flightdeck_index.py`（`layout_verdict`）
- Test: `scripts/tests/test_flightdeck_index.py`（`LayoutVerdictTest` 追加）

- [ ] **Step 1: 写失败测试** — 追加：

```python
    def test_missing_summary_on_current_deck_is_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="3.0")
            (deck / "specs" / "2026-06-02-bad.md").write_text(
                "---\nstatus: active\n---\n", encoding="utf-8"  # 缺 summary
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "malformed")

    def test_scrapped_missing_summary_not_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="3.0")
            (deck / "specs" / "2026-05-01-r.md").write_text(
                "---\nstatus: scrapped\n---\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "current")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k malformed -v`
Expected: FAIL（返回 `current` 而非 `malformed`）

- [ ] **Step 3: 实现** — 在 `layout_verdict` 里、版本分类**之前**插入 malformed 检查（仅当结构信号通过后才查；malformed 优先于 compatible/current，但结构落后优先于 malformed）：

```python
def layout_verdict(deck):
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
```

- [ ] **Step 4: 跑测试确认通过（整类回归）**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k LayoutVerdict -v`
Expected: 全部 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): layout_verdict malformed 判定（缺必需 workflow 字段）"
```

### Task 5: `--verdict` CLI flag（skill 快路入口）

**Files:**
- Modify: `scripts/flightdeck_index.py`（`main`，:267-306）
- Test: `scripts/tests/test_flightdeck_index.py`（新增 `VerdictCliTest`）

- [ ] **Step 1: 写失败测试**

```python
class VerdictCliTest(unittest.TestCase):
    def test_verdict_flag_prints_and_writes_nothing(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "rules.md").write_text("---\nversion: 3.0\n---\n", encoding="utf-8")
            specs = deck / "specs"
            specs.mkdir()
            (specs / "2026-06-01-a.md").write_text(
                "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
            )
            (deck / "cockpit.md").write_text(
                "## 进行中\n<!-- AUTO:inprogress -->\n\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--verdict"])
            self.assertEqual(rc, 0)
            self.assertIn("current", buf.getvalue().strip())
            # 只读：不应创建 INDEX.md
            self.assertFalse((deck / "INDEX.md").exists())
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -k Verdict -v`
Expected: FAIL（`unrecognized arguments: --verdict`）

- [ ] **Step 3: 实现** — 在 `main` 的 argparse 加 flag，并在 `version_mismatch` 守卫**之前**处理（verdict 只读，不受版本守卫限制）：

```python
    ap.add_argument(
        "--verdict",
        action="store_true",
        help="print the deck's layout verdict (current/compatible-behind/structural-behind/malformed) and exit",
    )
    args = ap.parse_args(argv)

    if args.verdict:
        print(layout_verdict(args.deck))
        return 0

    mismatch = version_mismatch(args.deck)
    ...
```

- [ ] **Step 4: 跑测试确认通过 + 全文件回归**

Run: `uv run -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全部 PASS（含原有用例无回归）

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): flightdeck_index 加 --verdict 只读子命令"
```

---

## Phase 2 — Skill 改造（删 Gate + 接线 verdict + 行为变更）

> 每个 skill 任务统一节奏：① Read 整文件定位；② Edit；③ Grep 校验该改的没了/新文案在；④ commit。markdown 无单元测试，校验靠 Grep + 通读。

### Task 6: `emit-agents-md` 删 Gate

**Files:**
- Modify: `skills/emit-agents-md/SKILL.md`

- [ ] **Step 1: Read** `skills/emit-agents-md/SKILL.md` 全文，定位 model-invocation Gate 段（标题含 "Gate" / "model-invocation" / "self-invoke"）。
- [ ] **Step 2: Edit** — 删除整个 Gate 段及其在目录/步骤里的交叉引用句；保留其余流程。
- [ ] **Step 3: 校验**

Run（Grep 工具，pattern 区分大小写）：`self-invoke|model-invocation|model_invocable` in `skills/emit-agents-md/SKILL.md`
Expected: 无命中（0 结果）

- [ ] **Step 4: commit**

```bash
git add skills/emit-agents-md/SKILL.md
git commit -m "refactor(flightdeck): emit-agents-md 删 self-invoke Gate"
```

### Task 7: `status` 删 Gate + 删 `status: auto land` 分支

**Files:**
- Modify: `skills/status/SKILL.md`

- [ ] **Step 1: Read** 全文。定位：(a) Gate 段（"Restricted only if ... `status: don't self-invoke`"）；(b) 触发表里 `land` 行（"User approved / signed off → done → land ... opt-in `land` ... House Rule `status: auto land`"）。
- [ ] **Step 2: Edit** —
  - 删 Gate 段（status 一律可自调）。
  - 触发表删除 `land` 那一行的"opt-in / House Rule `status: auto land`"机制；归档改由 landing 智能判断承接。把该行替换为说明："`done` 后是否归档由 `/flightdeck:landing` 按交叉引用智能判断，status 不再管归档"。
  - 保留 `status: don't auto start` 这一可选 override（idea→active 仍默认自动，可关）。
- [ ] **Step 3: 校验**

Run: `self-invoke|auto land|status_auto` in `skills/status/SKILL.md`
Expected: `self-invoke`、`auto land` 无命中；`don't auto start` 仍在。

- [ ] **Step 4: commit**

```bash
git add skills/status/SKILL.md
git commit -m "refactor(flightdeck): status 删 Gate + 删 auto-land 分支（归档归 landing 判断）"
```

### Task 8: `preflight` 重写（Gate / Branch-0 / step1 verdict / 宽容 / run-scripts 推断）

**Files:**
- Modify: `skills/preflight/SKILL.md`

- [ ] **Step 1: Read** 全文，定位：Gate 段、Branch-0 段、step 1 的版本处理（silent bump / structural 提示 / 版本比较）、fallback 里 `disabled_folders`、`run scripts` 字样。
- [ ] **Step 2: Edit** —
  - **删 Gate 段**整段。
  - **Branch-0 瘦成一行**：把"deck 存在检查 + 一堆戒律"替换为单句降级——"若 `flightdeck/cockpit.md` 不存在 → 输出一行 `No flightdeck deck here — run /flightdeck:launch`，STOP。"删掉"读 nothing else / 别长成 installer / 迁移探测"等戒律文字。
  - **step 1 版本处理改为只读上报**：删 silent bump、删版本号比较散文；改为——"（`run scripts` 推断可用时）跑 `flightdeck_index.py <deck> --verdict`；verdict ≠ `current` → 上报一行 `ℹ deck 落后（<verdict>）— run /flightdeck:walkaround`。preflight **不 bump、不迁移**。无脚本运行时：读 `MIGRATION.md` frontmatter（`current`/`layout_need_update`，非散文）+ 自查结构信号，得同一 verdict。"
  - **空/未用文件夹宽容**：fallback/catalog 里凡因 `disabled_folders` 抑制的逻辑删掉；空文件夹当非问题、不提示。删 `disabled_folders` 读取。
  - **`run scripts` 改推断**：凡"House Rule `run scripts` 开则…"的条件，改为"检测到 `uv`/`python` 可达则走脚本快路，否则手动兜底"。
- [ ] **Step 3: 校验**

Run: `self-invoke|disabled_folders|silent bump|Branch-0` in `skills/preflight/SKILL.md`
Expected: `self-invoke`/`disabled_folders` 无命中；Branch-0 仅剩降级一行（无戒律段）。
Run: `--verdict|walkaround` 应出现在 step 1。

- [ ] **Step 4: commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "refactor(flightdeck): preflight 删 Gate/Branch-0 戒律，step1 改 verdict 只读上报 + 宽容空文件夹"
```

### Task 9: `landing` 重写（Gate / verdict 守卫 / 智能归档 / commit / run-scripts）

**Files:**
- Modify: `skills/landing/SKILL.md`

- [ ] **Step 1: Read** 全文，定位：Gate 段、INDEX 再生（Step 5/fast path）、Land Routine/归档段、commit 段、`run scripts` 字样。
- [ ] **Step 2: Edit** —
  - **删 Gate 段**。
  - **加 verdict 前置守卫**：在跑任何 regen 之前——"先取 verdict（脚本 `--verdict` 或手动）；若 `structural-behind` / `malformed` → 干净 STOP，报 `先 run /flightdeck:walkaround 迁移后再 land`，不 regen。"
  - **智能归档**（替原 `status: auto land` 机制）：归档判断写成——"对每个 `status: done` 工件：整簇完成且**无 `active` 工件交叉引用它** → 归档进 `landed/`；仍被 active 引用 / 同簇未完 → 留原地（done-but-unlanded）。"删掉任何依赖 `status: auto land` House Rule 的条件。
  - **commit 默认翻转**：commit 段改为——"默认：自写 message 后**本地 commit 自调**（可逆、非外发，无需先问）；**push 永远先问**。override（`commit: ask` / `don't auto-commit`）仍生效，授权链 CLAUDE.md > rules House Rule。"
  - **`run scripts` 改推断**（同 Task 8）。
- [ ] **Step 3: 校验**

Run: `self-invoke|auto land|run scripts` in `skills/landing/SKILL.md`
Expected: `self-invoke`/`auto land` 无命中。
Run: `verdict|structural-behind|本地 commit|push` 应出现。

- [ ] **Step 4: commit**

```bash
git add skills/landing/SKILL.md
git commit -m "refactor(flightdeck): landing 删 Gate + verdict 守卫 + 智能归档 + commit 本地自调/push 先问"
```

### Task 10: `walkaround` 重写（Gate / 消费 verdict / 唯一版本写者 / 宽容）

**Files:**
- Modify: `skills/walkaround/SKILL.md`

- [ ] **Step 1: Read** 全文，定位：Gate 段、版本/迁移 Audit（Audit 10）、orphan/`disabled_folders` 逻辑。
- [ ] **Step 2: Edit** —
  - **删 Gate 段**。
  - **消费 verdict + 确立唯一版本写者**：版本/迁移 Audit 改为——"取 verdict（脚本 `--verdict` 或手动）：`compatible-behind` → **bump** `rules.md` `version` 到 `current`（这是 walkaround 的写）；`structural-behind` → 执行迁移动作（参 MIGRATION）；`malformed` → 报具体缺字段。**walkaround 是唯一写 `version` 的命令。**"
  - **空/未用文件夹宽容**：orphan/缺失审计里凡靠 `disabled_folders` 抑制的，改为"空文件夹不报问题；仅内容明显放错位置时 INFO/询问"。删 `disabled_folders` 读取。
- [ ] **Step 3: 校验**

Run: `self-invoke|disabled_folders` in `skills/walkaround/SKILL.md`
Expected: 无命中。
Run: `verdict|唯一写|bump` 应出现。

- [ ] **Step 4: commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "refactor(flightdeck): walkaround 删 Gate + 消费 verdict + 唯一版本写者 + 宽容空文件夹"
```

---

## Phase 3 — protocol + scaffold 模板

### Task 11: `protocol.md` 收敛（Rule resolution / 短语表 / 配置映射）

**Files:**
- Modify: `skills/preflight/protocol.md`

- [ ] **Step 1: Read** 全文，定位：`## Rule resolution order`、标准短语表、配置映射表（含 `disabled_folders` / `model_invocable` / `commit_mode` 行）、version 读/写归属描述。
- [ ] **Step 2: Edit** —
  - Rule resolution order：删 self-invoke 解析；`run scripts` 从 House-Rule 项移到**环境推断**列（与 git/emit 并列）。
  - 标准短语表：**删** self-invoke 行、`status: auto land` 行、`run scripts` 行；**保留** commit override 两行（`commit without asking` / `don't auto-commit`），但把"默认"注明为"本地 commit 自调 / push 先问"。
  - 配置映射表：删 `disabled_folders` 行（已移除）；更新 `version` 行——读由 preflight（只读上报）/landing（守卫）/walkaround（消费），**写仅 walkaround**；commit 行更新新默认。
  - `disabled_folders` 作为"唯一结构化 toggle"的描述删除（frontmatter 现仅 `version`）。
- [ ] **Step 3: 校验**

Run: `disabled_folders|self-invoke|auto land` in `skills/preflight/protocol.md`
Expected: 无命中（`commit` override 与 `don't auto start` 仍在）。

- [ ] **Step 4: commit**

```bash
git add skills/preflight/protocol.md
git commit -m "docs(flightdeck): protocol 删 self-invoke/disabled_folders/auto-land，run-scripts 转推断，commit 新默认"
```

### Task 12: scaffold `rules.md` 重做（速查表版）

**Files:**
- Modify: `scaffolds/full/flightdeck/rules.md`

- [ ] **Step 1: Read** 现文件确认当前内容。
- [ ] **Step 2: Edit** — 整文件替换为（与 spec ① 目标产物一致）：

```
---
version: 3.0
---

## House rules
<!-- 默认：本地 commit 自调(可 reset/amend) + push 先问 + landing 智能归档；脚本/ git / AGENTS 均自动推断。
     极少需要改；要改就在下方 heading 下打一行短语。可用短语：
       commit: ask | don't auto-commit
       status: don't auto start
       this deck doesn't use git | has AGENTS.md but don't auto-regen -->

### Project conventions

### Autonomy overrides
```

（注意：frontmatter 去掉 `disabled_folders`，仅剩 `version`。）

- [ ] **Step 3: 校验**

Run: `disabled_folders|don't self-invoke|──|MORE autonomous` in `scaffolds/full/flightdeck/rules.md`
Expected: 全部无命中。

- [ ] **Step 4: commit**

```bash
git add scaffolds/full/flightdeck/rules.md
git commit -m "refactor(flightdeck): scaffold rules.md 重做成速查表版（frontmatter 仅 version）"
```

---

## Phase 4 — MIGRATION + dogfood rules

### Task 13: `MIGRATION.md` 增节（行为变更，无新 layout_need_update）

**Files:**
- Modify: `MIGRATION.md`

- [ ] **Step 1: Read** 现文件，确认 frontmatter `current: 3.0` / `layout_need_update: [2.2, 3.0]` **不变**（本批改动是行为/配置，非结构，旧键读但忽略，无需新结构迁移项）。
- [ ] **Step 2: Edit** — 在 `## 2.3 → 3.0` 节内或紧随其后新增小节，要点：
  - 移除/转化清单：`model_invocable`（self-invoke 概念删，全员可自调）、`disabled_folders`（删，默认宽容）、`status_auto`/`auto land`（删，归档转 landing 智能判断）、`run scripts`（转环境推断）——**全部读但忽略**，无需用户动手。
  - **commit 安全默认变更（显著标注）**：旧"开箱啥都不 commit" → 新"本地 commit 自调 / push 先问"。override 仍在：CLAUDE.md / rules `commit: ask` / `don't auto-commit` 可改回。
  - 更新该节里"preflight 静默 bump"措辞 → "preflight 只读上报 verdict；**walkaround 唯一写 version**"。
  - 提示：升级后 reinstall/sync 插件缓存以加载新 skill。
- [ ] **Step 3: 校验**

Run: `本地 commit 自调|唯一写|读但忽略` in `MIGRATION.md`
Expected: 均出现。确认 frontmatter 两行未改。

- [ ] **Step 4: commit**

```bash
git add MIGRATION.md
git commit -m "docs(flightdeck): MIGRATION 记自治面收敛 + commit 默认变更（行为变更，无新结构项）"
```

### Task 14: dogfood `flightdeck/rules.md` 清理

**Files:**
- Modify: `flightdeck/rules.md`

- [ ] **Step 1: Read** 现文件。
- [ ] **Step 2: Edit** —
  - frontmatter 删 `disabled_folders`，仅留 `version: 3.0`。
  - 删 `### Autonomy overrides` 下四行 `... don't self-invoke; I run it manually` + 那条迁移注释。
  - 删 `run scripts with uv run`（已转推断）。
  - 保留 `### Project conventions` 的 dogfood 约定（applies_to 不得用 general 等）。
- [ ] **Step 3: 校验**

Run: `don't self-invoke|disabled_folders|run scripts` in `flightdeck/rules.md`
Expected: 全部无命中；`version: 3.0` 仍在。

- [ ] **Step 4: commit**

```bash
git add flightdeck/rules.md
git commit -m "chore(flightdeck): dogfood rules.md 清理（仅留 version + Project conventions）"
```

---

## Phase 5 — 验证 + dogfood + 发布提醒

### Task 15: 全套自动验证

**Files:** 无改动（验证）。

- [ ] **Step 1: 全测试**

Run: `uv run -m pytest scripts/tests/ -v`
Expected: 全绿（含 Phase 1 新增）。

- [ ] **Step 2: INDEX 一致性**

Run: `uv run scripts/flightdeck_index.py flightdeck --check`
Expected: `clean`

- [ ] **Step 3: verdict 自检**

Run: `uv run scripts/flightdeck_index.py flightdeck --verdict`
Expected: `current`

- [ ] **Step 4: lint（若存在）**

Run: `uv run scripts/flightdeck_lint.py flightdeck`（按其现有用法）
Expected: 无错误（或仅 INFO）。

- [ ] **Step 5: commit（若 regen 产生变更）**

```bash
git add -A
git commit -m "chore(flightdeck): regen + 验证通过（pytest/--check/--verdict clean）"
```

### Task 16: reload dogfood + 发布提醒（人工，交 walkaround 收口）

**Files:** 无代码改动。

- [ ] **Step 1: 同步插件缓存** — 按 `flightdeck/checklists/local-plugin-testing.md` 把工作树同步进 plugin-cache（robocopy / `.in_use` 等），reload。
- [ ] **Step 2: 交互 dogfood**（reload 后）—
  - `/flightdeck:preflight`：deckless 重定向？slim 接管？落后时一行 verdict 提示？无 silent bump？
  - `/flightdeck:landing`：verdict 守卫（造一个 malformed 文件验证 STOP）？智能归档判断？本地 commit 自调、push 先问？
  - `/flightdeck:walkaround`：消费 verdict？compatible-behind 时 bump？
- [ ] **Step 3: 翻状态** — dogfood 通过后，把本 spec + plan + 同簇 scriptable/model-v4 簇按计划一起 `done` 并 land（交 `/flightdeck:landing` 智能归档）。
- [ ] **Step 4: 发布提醒** — 按 `flightdeck/checklists/version-bump.md` 写 CHANGELOG（自治面收敛 / 智能 landing / **commit 默认变更** / 版本检查脚本化 / preflight 行为变更）+ marketplace + tag + 合并 → main。**本步交用户/发布流程，计划不自动发布。**

---

## 自检（spec 覆盖核对）

- spec ①（删 self-invoke / run-scripts 推断 / 删 disabled_folders / commit 翻默认 / status:auto-land→智能 / 模板）→ Task 6-12, 14。
- spec ②（verdict 脚本化 + 数据源 MIGRATION frontmatter + fast-path/fallback + format_row 健壮）→ Task 1-5, 8/9/10 的 verdict 接线。
- spec ③（preflight 只读上报 / landing 守卫 / walkaround 唯一写）→ Task 8, 9, 10, 11。
- spec ④（preflight 删 Branch-0 留一行）→ Task 8。
- 兼容（旧键读但忽略 + commit 默认显著标注）→ Task 13。
- 验证 → Task 15, 16。
