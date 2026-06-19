---
status: active
summary: 实现 cockpit-field-redesign：新字段结构（Updated 纯戳 / Focus 一行 / Pointers 行 / Next 单步+进度移plan / In Progress summary 截断 / Key Context / Pending / Hanging）落 templates+exit-ritual+protocol，scaffold 出新形状，flightdeck_index.py In Progress 截断渲染（TDD），walkaround 加 Audit 16，dogfood cockpit 重构验证。新写内容一律英文（蹭 i18n）。
last_updated: 2026-06-19
implements: specs/2026-06-19-cockpit-field-redesign.md
---

# Cockpit 字段重设计 rollout — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans（本 plan 在原会话内联执行——设计上下文全在对话里，禁止派 fresh subagent 重新推导）。Steps use `- [ ]`.

**Goal:** 把 cockpit 从「叙述字段漏入工作记录」重构为「纯恢复载荷：每字段是廉价投影或指针大小判断，记录回各自的家只留链接」。

**Architecture:** 真相源 = `exit-ritual.md` §Cockpit update（字段角色）+ `templates.md`（cockpit 模板）；脚本只做 In Progress summary 的确定性截断；scaffold/walkaround/landing/preflight 跟随。新字段顺序：`Updated · Focus · Pointers · ## Next · ## In Progress · ## Key Context · ## Pending Review · ## Hanging Tasks`。

**Tech Stack:** Python 3 stdlib（`flightdeck_index.py`）+ unittest（`scripts/tests/`）+ markdown skill prose（英文）。

**约束（贯穿全 plan）:** 所有新写/改写进 `skills/` `scaffolds/` 的内容**一律英文**（CLAUDE.md 已强化的发布面红线；本 plan 蹭这次重写顺带把碰到的段落英文化，减 i18n spec 返工）。

---

### Task 1: In Progress summary 截断渲染（D4，TDD）

**Files:**
- Modify: `scripts/flightdeck_index.py`（常量区 + `regen_cockpit_inprogress` line ~261）
- Test: `scripts/tests/test_flightdeck_index.py`（新增一个 test 方法）

- [ ] **Step 1: 写失败测试** — 加到 `test_flightdeck_index.py`（复用文件已有的 temp-deck 搭建风格；若无 helper 则内联建最小 deck）。

```python
def test_inprogress_truncates_long_summary(self):
    from flightdeck_index import regen_cockpit_inprogress
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "specs").mkdir()
        (deck / "cockpit.md").write_text(
            "# Cockpit\n## In Progress\n<!-- AUTO:inprogress -->\n<!-- /AUTO -->\n",
            encoding="utf-8")
        long_summary = "A" * 200  # 远超 80 字上限
        (deck / "specs" / "2026-06-19-x.md").write_text(
            f"---\nstatus: active\nsummary: {long_summary}\nlast_updated: 2026-06-19\n---\n# X\n",
            encoding="utf-8")
        block = regen_cockpit_inprogress(deck)
        row = [l for l in block.splitlines() if l.startswith("- [")][0]
        assert "…" in row, f"expected truncation ellipsis in: {row}"
        assert len(row) < 140, f"row too long, not truncated: {len(row)}"
        assert "(specs/2026-06-19-x.md)" in row, "link must survive truncation"
```

- [ ] **Step 2: 跑测试确认 FAIL**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_index.py -k inprogress_truncates -v`
Expected: FAIL（当前渲染完整 summary，无 `…`）。

- [ ] **Step 3: 实现截断** — `flightdeck_index.py` 常量区加上限，加 helper，改 row 拼接。

```python
# 常量区（SUMMARY_KINDS 附近）
INPROGRESS_SUMMARY_MAX = 80   # In Progress 行只渲染 summary 截断头部；全文留 spec frontmatter

def _truncate_inprogress_summary(summary):
    """In Progress 行渲染：取首行、超上限则截断 + ellipsis（确定性，非判断）。"""
    head = (summary or "").splitlines()[0] if summary else ""
    if len(head) > INPROGRESS_SUMMARY_MAX:
        head = head[:INPROGRESS_SUMMARY_MAX].rstrip() + "…"
    return head
```

改 `regen_cockpit_inprogress` 内（原 line ~261）:
```python
            summary = _truncate_inprogress_summary(fm.get("summary", "⚠ summary 缺失"))
            row = f"- [{name}]({kind}/{name}) {DASH} {summary}"
```

- [ ] **Step 4: 跑测试确认 PASS**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_index.py -k inprogress_truncates -v`
Expected: PASS。

- [ ] **Step 5: 全量回归**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -q`
Expected: 全绿（截断不破坏既有 In Progress 断言；若某既有测试 assert 了完整长 summary，按截断语义同步改它——只改测试期望，不退实现）。

- [ ] **Step 6: Commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(index): truncate In Progress summary render (cockpit-field-redesign D4)"
```

---

### Task 2: cockpit 模板新结构（templates.md，英文）

**Files:**
- Modify: `skills/preflight/templates.md`（cockpit 模板段 + 各字段 Rules 注释 + `summary` 字段长度上限文案）

- [ ] **Step 1:** 把 cockpit 模板改成新字段顺序与角色（英文）。模板骨架：

```
# Cockpit — <project>
Updated: <date> · <author> · Stage: <lifecycle>

Focus: <one-line thread label, ≤~100 chars> → <current spec/plan link>

Pointers: config → rules.md · conventions → <file> · artifacts → folder INDEXes · history → archive/

## Next
<single concrete next action> → <plan link>   (progress detail lives in the plan's ## Progress)

## In Progress
<!-- AUTO:inprogress -->
<!-- /AUTO -->

## Key Context
- (none)

## Pending Review
- (none)

## Hanging Tasks
- (none)
```

- [ ] **Step 2:** 每字段 Rules 注释（英文，钉角色 + 软上限 + 越界禁令）：
  - `Updated`: timestamp + author + Stage only. **No changelog** — history is `git log` + commit + spec/plan body.
  - `Focus`: one coarse thread label + link. **No goal / criteria / method / invariants** — those live in the spec body (invariants → `rules.md`). ≤~100 chars.
  - `Pointers`: thin navigation anchors only, never content. Hand-maintained (not AUTO).
  - `## Next`: the single next concrete action + plan link. **Progress checklists / 依据 lists / milestone links move to the plan's `## Progress`** — not loaded every ritual.
  - `## In Progress`: AUTO projection of `status:active`; renders a truncated summary head (≤80 chars) + link.
  - `## Key Context` / `## Pending Review` / `## Hanging Tasks`: per accumulator spec lifecycle (this plan only sets structure/order).
- [ ] **Step 3:** `summary` 字段文案加软上限（英文）：a row descriptor, not an abstract — keep `summary` to ≤~1–2 lines / ~200 chars; In Progress + INDEX both render it every session.
- [ ] **Step 4: Verify** — `rg -n 'Pointers|Focus:|Updated:' skills/preflight/templates.md` 命中新结构；新写段无中文（旧段中文留 i18n spec 清）。
- [ ] **Step 5: Commit** — `git commit -m "feat(templates): new cockpit field structure + role rules (field-redesign D1-D5)"`

---

### Task 3: 字段角色真相源 + 越界检查（exit-ritual.md，英文）

**Files:**
- Modify: `skills/preflight/exit-ritual.md` §Cockpit update（line ~327-359 区）

- [ ] **Step 1:** 重写 §Cockpit update 的字段表与各字段段落，落 D1（Updated 纯戳）/ D2（Focus 一行+链接）/ D3（Next 单步、进度移 plan `## Progress`）/ D5（Pointers 行定义）。措辞与 Task 2 模板一致（英文）。
- [ ] **Step 2:** §Length check 扩展为「角色越界检查」：现「行数 + 逐字段密度」基础上加——`Updated` 含 changelog / `Focus` 含 goal-criteria-method / `Next` 含 progress-checklist → 非阻塞提示 + 门控 trim（把越界内容路由回家：changelog→git、progress→plan、criteria→spec）。
- [ ] **Step 3: Verify** — `rg -n 'role|Focus|Pointers|progress' skills/preflight/exit-ritual.md` 命中；语义与 Task 2 不矛盾（人读对账）。
- [ ] **Step 4: Commit** — `git commit -m "feat(exit-ritual): cockpit field roles + role-creep length check (field-redesign)"`

---

### Task 4: protocol 字段语义 + 指针vs记录边界（protocol.md，英文）

**Files:**
- Modify: `skills/preflight/protocol.md`（cockpit 字段语义段，`## Key Context is the recovery slot` 附近）

- [ ] **Step 1:** 补 `Pointers` 行定义 + 一句「pointer vs record」边界原则：cockpit materializes only irreducible judgment + one cheap projection (In Progress); records live in git / plan `## Progress` / spec body / rules / INDEX, cockpit only links.
- [ ] **Step 2:** `Focus`（原 Active focus）/ `Next` 语义与 exit-ritual 对齐（英文）；In Progress 段补「renders truncated summary head」。
- [ ] **Step 3: Verify** — `rg -n 'pointer|Pointers|truncated' skills/preflight/protocol.md` 命中。
- [ ] **Step 4: Commit** — `git commit -m "feat(protocol): pointer-vs-record boundary + Pointers field semantics (field-redesign)"`

---

### Task 5: scaffold 出新形状（scaffolds/full）

**Files:**
- Modify: `scaffolds/full/flightdeck/cockpit.md`

- [ ] **Step 1:** 把 scaffold cockpit 换成 Task 2 的新骨架（占位最小：空 Focus/Pointers/Next + 空 AUTO 块 + `(none)` 列表）。纯英文。
- [ ] **Step 2: Verify** — `rg -P '\p{Han}' scaffolds` 仍为空；字段顺序与 Task 2 一致。
- [ ] **Step 3: Commit** — `git commit -m "feat(scaffold): new-deck cockpit ships field-redesign structure"`

---

### Task 6: landing / preflight 引用跟随（英文）

**Files:**
- Modify: `skills/landing/SKILL.md`（Step 8 措辞）
- Modify: `skills/preflight/SKILL.md`（报告侧若需提示 Next 越界/Focus 段落化）

- [ ] **Step 1:** landing Step 8 引用新字段角色（不重述真相，指向 exit-ritual）；加「Next progress → plan `## Progress`」一句。英文。
- [ ] **Step 2:** preflight 报告侧（banner/Key Context 行）字段名跟随（Active focus → Focus）；若加越界提示则一行非阻塞。英文。
- [ ] **Step 3: Verify** — `rg -n 'Focus|Progress' skills/landing/SKILL.md skills/preflight/SKILL.md` 命中且与真相源一致。
- [ ] **Step 4: Commit** — `git commit -m "feat(landing,preflight): follow new cockpit field roles (field-redesign)"`

---

### Task 7: walkaround Audit 16（字段结构 conformance，英文）

**Files:**
- Modify: `skills/walkaround/SKILL.md`（Audits 段加 Audit 16；description frontmatter 补一句；「Run all 15」改「16」）

- [ ] **Step 1:** 加 **Audit 16** — cockpit field-structure / role conformance：flag non-standard sections / missing standard sections / field role-creep（Updated changelog · Focus paragraph-ized · Next progress-journal）as non-blocking INFO（surface-only，守 walkaround invariant，不修）。英文。
- [ ] **Step 2:** 改 `Run all 15 in order` → `16`；frontmatter description 末补 `cockpit field-structure conformance (Audit 16)`。
- [ ] **Step 3: Verify** — `rg -n 'Audit 16|field-structure|16 in order' skills/walkaround/SKILL.md` 命中。
- [ ] **Step 4: Commit** — `git commit -m "feat(walkaround): Audit 16 cockpit field-structure conformance (field-redesign)"`

---

### Task 8: dogfood 验证 + 本仓 cockpit 重构

**Files:**
- Modify: `flightdeck/cockpit.md`（本仓 dogfood，中文 OK——deck 内容随语言）

- [ ] **Step 1:** 按新结构重构本仓 cockpit：`Last updated` 括号 changelog 砍成纯 Stage；`Active focus` → 一行 `Focus` + 链接；加 `Pointers` 行；`## Next` 越界进度若有则移到对应 plan `## Progress`。Key Context/Pending Review 暂留（其瘦身归 accumulator spec，下个执行）。
- [ ] **Step 2:** `uv run scripts/flightdeck_index.py flightdeck` regen，确认 In Progress 截断生效、无脏块。
- [ ] **Step 3:** `wc -m flightdeck/cockpit.md`（重构前后对比，记净降）。
- [ ] **Step 4:** `uv run pytest scripts/tests/ -q` 全绿；`/flightdeck:walkaround` 自查（Audit 16 对本仓新结构应 clean 或仅剩 deck 语言 INFO）。
- [ ] **Step 5: Commit** — `git commit -m "refactor(dogfood): rebuild cockpit to field-redesign structure"`

---

## Self-review（对 spec 核一遍）

- D1 Updated→Task 2/3/8 · D2 Focus→Task 2/3/4/8 · D3 Next 进度移 plan→Task 2/3/6/8 · D4 summary 截断+上限→Task 1/2 · D5 Pointers→Task 2/3/4/8 · Audit 16→Task 7 · scaffold→Task 5。spec 落地面每项有对应 task，无缺口。
- 非目标守住：不删 In Progress（只截断渲染）、不加硬总预算（只提示+门控）、不碰 Key Context/Pending 生命周期（归 accumulator spec）。
- 命名一致：常量 `INPROGRESS_SUMMARY_MAX`、helper `_truncate_inprogress_summary`、字段名 `Focus`/`Pointers`/`## Next` 全 plan 统一。
