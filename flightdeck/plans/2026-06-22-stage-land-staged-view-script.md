---
status: active
summary: Script foundation for stage/land: named-marker multi-AUTO-region support + regen_cockpit_staged (done-not-archived workflow + stale-with-verify knowledge) + scaffold ## Staged section + .js byte-parity twin.
last_updated: 2026-06-22
implements: specs/2026-06-22-stage-land-lifecycle.md
---

# Plan 1: ## Staged derived-view script foundation

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development 或 superpowers:executing-plans，逐 task 执行。步骤用 `- [ ]` 勾选。

**Goal:** 给 cockpit 增加一个**派生**的 `## Staged (awaiting land)` 视图——聚合 done-not-archived workflow + stale-with-verify 知识——作为 stage/land 模型「阀门前暂存口」的可见落点。纯脚本地基，不碰任何 skill 散文。

**Architecture:** cockpit 当前只有一个 AUTO 区（`inprogress`），`replace_auto_block` 用「首个 `<!-- AUTO:`」定位。加第二个区（`staged`）必须先把 AUTO 定位改成**按 marker 名**精确匹配，再加一个 `regen_cockpit_staged` 派生函数并挂进 regen 入口。所有改动同步到 byte-parity 的 `.js` 孪生。

**Tech Stack:** Python 3.8+ stdlib（`scripts/flightdeck_index.py`）、Node（`scripts/flightdeck_index.js` 孪生）、unittest（`scripts/tests/`）、uv。

## Global Constraints

- **byte-parity 孪生：** `scripts/flightdeck_index.py` 与 `scripts/flightdeck_index.js` 是 byte-parity 双胞胎。**任何 `.py` 改动必须同步 `.js`**，由 `scripts/tests/test_parity.py` 验收（Task 4 专门做）。
- **测试命令：** `uv run pytest scripts/tests/`（单测）；parity：`uv run pytest scripts/tests/test_parity.py`。
- **派生视图只读 frontmatter，不做判断**（脚本计算事实，判断留模型）。Pending Review 是手写 sign-off 队列、不可派生 → **不并入** `## Staged`（修正 spec staging-area 段「待 sign-off 项并入」的措辞，Task 3 一并回写 spec）。
- **发布面英文：** scaffold cockpit 的 section heading（`## Staged (awaiting land)`）+ AUTO 标记英文。
- **提交：** 本地 commit（conventional，见 `checklists/commits.md`），不 push。
- **`KNOWLEDGE_KINDS = {"checklists", "incidents", "docs"}`**（`references` 不在内）；`DASH = "—"`；`AUTO_END = "<!-- /AUTO -->"`。

---

### Task 1: AUTO 定位改为按命名 marker（解锁同文件多 AUTO 区）

**Files:**
- Modify: `scripts/flightdeck_index.py`（`replace_auto_block` ~234-238；main regen 循环 ~841；`index_drift` ~689）
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Produces: `_marker_of(block) -> str`（取 block 开头的 `<!-- AUTO:<name> -->`）；`extract_auto_block(text, marker) -> str`（取 text 中该命名区的当前切片）；`replace_auto_block(text, new_block) -> str`（按 new_block 的 marker 名替换对应区，其余原样）。

- [ ] **Step 1: 写失败测试**

加到 `scripts/tests/test_flightdeck_index.py`：

```python
class NamedAutoRegionTest(unittest.TestCase):
    TWO = (
        "head\n"
        "<!-- AUTO:inprogress -->\nOLD-IP\n<!-- /AUTO -->\n"
        "mid\n"
        "<!-- AUTO:staged -->\nOLD-ST\n<!-- /AUTO -->\n"
        "tail\n"
    )

    def test_replace_targets_named_region_only(self):
        new = "<!-- AUTO:staged -->\nNEW-ST\n<!-- /AUTO -->"
        out = flightdeck_index.replace_auto_block(self.TWO, new)
        self.assertIn("OLD-IP", out)        # inprogress 区不动
        self.assertIn("NEW-ST", out)        # staged 区被替换
        self.assertNotIn("OLD-ST", out)

    def test_replace_inprogress_leaves_staged(self):
        new = "<!-- AUTO:inprogress -->\nNEW-IP\n<!-- /AUTO -->"
        out = flightdeck_index.replace_auto_block(self.TWO, new)
        self.assertIn("NEW-IP", out)
        self.assertIn("OLD-ST", out)
        self.assertNotIn("OLD-IP", out)

    def test_extract_named_region(self):
        blk = flightdeck_index.extract_auto_block(self.TWO, "<!-- AUTO:staged -->")
        self.assertEqual(blk, "<!-- AUTO:staged -->\nOLD-ST\n<!-- /AUTO -->")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::NamedAutoRegionTest -v`
Expected: FAIL（`extract_auto_block` / `_marker_of` 未定义；旧 `replace_auto_block` 替换首个区，`test_replace_targets_named_region_only` 误删 inprogress）。

- [ ] **Step 3: 改实现**

`scripts/flightdeck_index.py`，把现有 `replace_auto_block`（234-238）替换为：

```python
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
```

然后把 main regen 循环里的 drift 比较（~841）和 `index_drift`（~689）两处相同的旧切片：

```python
cur_block = current[current.index("<!-- AUTO:") : current.index(AUTO_END) + len(AUTO_END)]
```

都改为按当前 `new_block` 的 marker 定位：

```python
cur_block = extract_auto_block(current, _marker_of(new_block))
```

- [ ] **Step 4: 跑测试确认通过 + 全套回归**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -v`
Expected: PASS（含 `NamedAutoRegionTest` 三条 + 原有 index 测试不回归——单 AUTO 区文件行为不变，因为 `_marker_of` 对单区取的就是那个区）。

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "refactor(index): locate AUTO regions by marker name, not first match"
```

---

### Task 2: `regen_cockpit_staged(deck)` 派生函数

**Files:**
- Modify: `scripts/flightdeck_index.py`（新函数，紧跟 `regen_cockpit_inprogress` ~342 之后）
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Consumes: `parse_frontmatter`、`_truncate_inprogress_summary`、`KNOWLEDGE_KINDS`、`DASH`、`AUTO_END`（均已存在）。
- Produces: `regen_cockpit_staged(deck) -> str`，返回 `<!-- AUTO:staged -->\n{body}\n<!-- /AUTO -->`。

- [ ] **Step 1: 写失败测试**

```python
class RegenStagedTest(unittest.TestCase):
    def _deck(self, files):
        d = Path(tempfile.mkdtemp())
        for rel, fm in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            front = "".join(f"{k}: {v}\n" for k, v in fm.items())
            p.write_text(f"---\n{front}---\n# x\n", encoding="utf-8")
        return d

    def test_done_workflow_and_stale_verify_knowledge(self):
        d = self._deck({
            "specs/a.md": {"status": "done", "summary": "did A"},
            "specs/b.md": {"status": "active", "summary": "doing B"},
            "incidents/c.md": {"status": "stale", "verify": "run repro X"},
            "incidents/e.md": {"status": "stale"},
            "incidents/f.md": {"status": "active"},
        })
        blk = flightdeck_index.regen_cockpit_staged(d)
        self.assertIn("[a.md](specs/a.md)", blk)       # done workflow 入
        self.assertNotIn("b.md", blk)                   # active workflow 不入
        self.assertIn("[c.md](incidents/c.md)", blk)    # stale+verify 知识入
        self.assertIn("verify: run repro X", blk)
        self.assertNotIn("e.md", blk)                   # stale 无 verify 不入
        self.assertNotIn("f.md", blk)                   # active 知识不入

    def test_empty_when_nothing_staged(self):
        d = self._deck({"specs/b.md": {"status": "active", "summary": "x"}})
        blk = flightdeck_index.regen_cockpit_staged(d)
        self.assertEqual(blk, "<!-- AUTO:staged -->\n\n<!-- /AUTO -->")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::RegenStagedTest -v`
Expected: FAIL（`regen_cockpit_staged` 未定义）。

- [ ] **Step 3: 写实现**

`scripts/flightdeck_index.py`，紧跟 `regen_cockpit_inprogress` 之后加：

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::RegenStagedTest -v`
Expected: PASS（两条）。

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(index): add regen_cockpit_staged derived view"
```

---

### Task 3: 挂进 regen 入口 + cockpit 模板加 section + 回写 spec

**Files:**
- Modify: `scripts/flightdeck_index.py`（`_index_targets` ~672-674）
- Modify: `scaffolds/full/flightdeck/cockpit.md`（In Progress 之后加 `## Staged`）
- Modify: `flightdeck/cockpit.md`（本仓 dogfood，同样加 section）
- Modify: `flightdeck/specs/2026-06-22-stage-land-lifecycle.md`（修正「待 sign-off 项并入」）
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Consumes: `regen_cockpit_staged`（Task 2）、命名 marker 替换（Task 1）。

- [ ] **Step 1: 写失败 end-to-end 测试**

```python
class StagedEndToEndTest(unittest.TestCase):
    def test_main_regen_writes_both_regions_independently(self):
        d = Path(tempfile.mkdtemp())
        (d / "specs").mkdir()
        (d / "specs" / "a.md").write_text("---\nstatus: done\nsummary: did A\n---\n#x\n", encoding="utf-8")
        (d / "specs" / "b.md").write_text("---\nstatus: active\nsummary: doing B\n---\n#x\n", encoding="utf-8")
        (d / "cockpit.md").write_text(
            "# Cockpit\n\n## In Progress\n\n<!-- AUTO:inprogress -->\n\n<!-- /AUTO -->\n\n"
            "## Staged (awaiting land)\n\n<!-- AUTO:staged -->\n\n<!-- /AUTO -->\n",
            encoding="utf-8")
        flightdeck_index.main([str(d)])
        out = (d / "cockpit.md").read_text(encoding="utf-8")
        ip = flightdeck_index.extract_auto_block(out, "<!-- AUTO:inprogress -->")
        st = flightdeck_index.extract_auto_block(out, "<!-- AUTO:staged -->")
        self.assertIn("b.md", ip)         # active → inprogress
        self.assertNotIn("a.md", ip)
        self.assertIn("a.md", st)         # done → staged
        self.assertNotIn("b.md", st)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::StagedEndToEndTest -v`
Expected: FAIL（staged 区没被 regen——`_index_targets` 还没 yield 它，区内仍空）。

- [ ] **Step 3: 改 `_index_targets`**

`scripts/flightdeck_index.py`，把 cockpit yield（~672-674）：

```python
    cockpit = deck / "cockpit.md"
    if cockpit.is_file() and "<!-- AUTO:inprogress -->" in cockpit.read_text(encoding="utf-8"):
        yield "cockpit", cockpit, regen_cockpit_inprogress(deck)
```

替换为（一次读、两区各 yield；命名 marker 替换保证互不干扰）：

```python
    cockpit = deck / "cockpit.md"
    if cockpit.is_file():
        ctext = cockpit.read_text(encoding="utf-8")
        if "<!-- AUTO:inprogress -->" in ctext:
            yield "cockpit", cockpit, regen_cockpit_inprogress(deck)
        if "<!-- AUTO:staged -->" in ctext:
            yield "cockpit:staged", cockpit, regen_cockpit_staged(deck)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::StagedEndToEndTest -v`
Expected: PASS。

- [ ] **Step 5: scaffold + 本仓 cockpit 加 section**

`scaffolds/full/flightdeck/cockpit.md`，在 `## In Progress` 的 `<!-- /AUTO -->` 之后、`## Key Context` 之前插入：

```markdown
## Staged (awaiting land)

<!-- AUTO:staged -->

<!-- /AUTO -->
```

`flightdeck/cockpit.md`（本仓）同样在 `## In Progress` 区之后插入相同 section（dogfood：下次 regen 即填充）。

- [ ] **Step 6: 回写 spec 修正措辞**

`flightdeck/specs/2026-06-22-stage-land-lifecycle.md`，`## staging area 在 cockpit 的呈现` 段的派生三类列表里，把「待 sign-off 项（原 Pending Review 并入）」改为：

```markdown
- （**不并入**）Pending Review 是手写 sign-off 队列、不可 frontmatter 派生，保持独立 section。
```

- [ ] **Step 7: 跑全套 + commit**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -v`
Expected: PASS（全绿）。

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py scaffolds/full/flightdeck/cockpit.md flightdeck/cockpit.md flightdeck/specs/2026-06-22-stage-land-lifecycle.md
git commit -m "feat(cockpit): wire ## Staged derived section into regen + scaffold"
```

---

### Task 4: `.js` 孪生同步 + byte-parity 绿

**Files:**
- Modify: `scripts/flightdeck_index.js`（镜像 Task 1–3 的 `.py` 改动）
- Test: `scripts/tests/test_parity.py`（验收，不新增）

**Interfaces:**
- Produces: `.js` 与 `.py` 对 同一 deck 的 regen 输出 byte-equal。

- [ ] **Step 1: 先读 `.js` 对应函数，确认命名/风格**

Run: 读 `scripts/flightdeck_index.js` 里 `replaceAutoBlock` / `regenCockpitInprogress` / `indexTargets`（或等价命名）三处，照搬其现有风格（驼峰、字符串处理）。

- [ ] **Step 2: 镜像 Task 1（命名 marker 定位）到 `.js`**

把 `.js` 的 `replaceAutoBlock` 改成按 new_block 的 marker 名定位（对应 `.py` 的 `_marker_of` + `extract_auto_block` + `replaceAutoBlock`）；同步 main regen 循环 / drift 比较里取「首个 AUTO」的等价代码，改成按 marker 名取。

- [ ] **Step 3: 镜像 Task 2（`regenCockpitStaged`）到 `.js`**

加 `regenCockpitStaged(deck)`，逻辑与 `.py` 的 `regen_cockpit_staged` 逐行对应（done workflow + stale-with-verify 知识、分组渲染、相同的 row 字符串）。

- [ ] **Step 4: 镜像 Task 3（双 yield）到 `.js`**

`.js` 的 `indexTargets` 里 cockpit 部分改成 inprogress + staged 各 yield 一次。

- [ ] **Step 5: 跑 parity + 全套**

Run: `uv run pytest scripts/tests/test_parity.py -v`
Expected: PASS（`.py`/`.js` 对同一 deck 输出 byte-equal）。
Run: `uv run pytest scripts/tests/` —— 全套绿（确认无回归；`test_hooks.py` 在 WSL bash 遮蔽 Git Bash 时失败=环境噪音，见 `incidents/wsl-bash-shadows-git-bash-in-tests.md`，非本 plan 引入）。

- [ ] **Step 6: commit**

```bash
git add scripts/flightdeck_index.js
git commit -m "feat(index): mirror ## Staged + named-marker changes into .js twin"
```

---

## 完成标志

- cockpit 有 `## Staged (awaiting land)` section，`<!-- AUTO:staged -->` 由脚本派生 done-not-archived workflow + stale-with-verify 知识；
- 同文件双 AUTO 区（inprogress + staged）各自独立 regen，互不干扰；
- `.py`/`.js` byte-parity 绿；全套测试绿；
- spec 的「Pending Review 并入」措辞已修正为「不并入」。

**不在本 plan 内**（后续）：取消 signal-1 自动 archive、commit 移 stage、三层散文→stage/land 重写、signal 体系重设计、walkaround 翻转（plan 2 / plan 3）。
