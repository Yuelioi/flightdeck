---
status: active
summary: 把'验证非阻塞+preflight瘦身'spec逐文件落地：相位1 脚本TDD（flightdeck_index.py 加 --verify-pending 子命令 + format_row 按 verify 渲染 ⚠未验证/⚠待复核 + 测试）→相位2 治理文案契约（protocol/templates 定 verify 字段语义、stale 拓宽、done 语义、per-kind 通过失败）→相位3 仪式 skill（exit-ritual 门重写+扫描浮出、landing 3a3c+archivable、status done+verify、preflight 扫描+瘦身C+docs计数D）→相位4 套用 hook spec+plan 打 verify+归档清看板 + resync 后新会话 live 实证（停地板）
last_updated: 2026-06-08
implements: specs/2026-06-08-nonblocking-verify-preflight-slim.md
---

# 验证非阻塞 + preflight 瘦身 rollout（逐文件实施）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实施。脚本任务（Phase 1）走 TDD（失败测试先行）；编辑任务（Phase 2–3）是 markdown 文案改写，**不伪造 pytest**——闸为 `flightdeck_index.py --check` + `flightdeck_lint.py` 全绿 + `git diff` 逐条人工核「改的是措辞、不是规则」。

**Goal:** 把 `specs/2026-06-08-nonblocking-verify-preflight-slim` 落地——验证由阻塞门降为非阻塞的 `verify` 锚点字段（有字段=欠验证、值=怎么验，随文件进 archive、扫描确定性重建待验证清单），并给 preflight 输出瘦身（INDEX 仍读、只显计数、docs 载入）。

**Architecture:** 一个可选 frontmatter 字段 `verify`（非状态，与 status 联读）贯穿知识件（`stale + verify`）与工作流件（`done + verify`）；真相源在文件 frontmatter，cockpit/preflight 待验证清单是 `flightdeck_index.py --verify-pending` 的派生扫描。次序 = 自底向上：先脚本（可 TDD、被文案引用）→ 再治理契约（protocol/templates）→ 再仪式 skill 体（引用前两者）→ 最后套用首个对象 + resync 后 live 实证。

**Tech Stack:** Python `scripts/flightdeck_index.py`（新增 `--verify-pending` + 改 `format_row`）；pytest（`scripts/tests/test_flightdeck_index.py`）；`flightdeck_index.py --check` + `flightdeck_lint.py` 为编辑任务的闸；skills/ markdown 文案。

**关键前置事实（spec 已核，2026-06-08）：**
- `format_row(kind, filename, fm)`：`SUMMARY_KINDS={specs,plans}` 在 `:119-120` 早 return（**不经** stale 标记）；`KNOWLEDGE_KINDS={checklists,incidents,docs}` 在 `:136` 才 `if status=="stale": row="⚠ "+row`。两处都要按 `fm.get("verify")` 改。
- `parse_frontmatter` 是「一行一个 `key: value`」——`verify: <一行怎么验>` 解析为字符串，无需改解析器；index regen 只重写 INDEX/cockpit 的 AUTO 区、**不碰源文件 frontmatter**，故 `verify` 字段天然被保留。
- 子命令体例：`--archivable`/`--advance-candidates`/`--match-signature` 都在 `main()` 里「`if args.X: 打印每行; return 0`」，新增 `--verify-pending` 照搬。
- `verify` 字段语义（spec A 定）：**有字段=欠验证；值=一行怎么验；无字段=已验证/无需验证**。`verify` 是 status 的附加标记、须联读，**非第四状态**。
- 待验证清单**源在文件**：preflight 报告由 `--verify-pending` 现扫现得，**不读 cockpit 文本**（故「改 cockpit 后清单不变」成立）。

## Progress

current: **Task 1.1 — flightdeck_index.py 加 `--verify-pending` 子命令（TDD）。** 全 Phase 未起。

> **复选框说明**：步骤 `- [ ]` 仅供执行者本地跟踪，不回勾、不当缺陷修（看板只认 cockpit `## 进行中` + 本 Progress 指针）。

---

## File Structure

**修改（脚本）：**
- `scripts/flightdeck_index.py` — 新增 `verify_pending(deck)` + `--verify-pending` 子命令；改 `format_row` 两分支按 `verify` 渲染。
- `scripts/tests/test_flightdeck_index.py` — 扩用例（不新建文件）。

**修改（治理契约）：**
- `skills/preflight/protocol.md` — `verify` 字段语义 + `done` 语义补充 + `stale` 含义拓宽 + 非阻塞原则 + per-kind 通过/失败规则。
- `skills/preflight/templates.md` — frontmatter 模板加可选 `verify`；`stale` 定义文案；同步 `scaffolds/full/`（若其含相应模板）。

**修改（仪式 skill 体）：**
- `skills/preflight/exit-ritual.md` — needs-verify 门重写（A）+ 扫描式待验证浮出（B）+ 验证通过/失败 per-kind if-else。
- `skills/landing/SKILL.md` — 3a/3c 串 `done+verify` 与扫描浮出；`--archivable` 照常归档带 `verify` 的 `done`；soft-landing 不再被「要验证」挡。
- `skills/status/SKILL.md` — `done` 翻转加「+ verify」分支与判定行。
- `skills/preflight/SKILL.md` — catalog 阶段加 `--verify-pending` 扫描 → 待验证报告；输出瘦身（C，只显计数）；docs 计数（D）。

**数据（Phase 4）：** `specs/2026-06-07-hook-primary-refactor.md` + `plans/2026-06-07-hook-primary-refactor-rollout.md` 加 `verify: 相位4 各家 live 实证`、翻 `done`、归档。

---

## Phase 1 — 脚本基座（本会话 TDD）

> 脚本是文案的依赖底座，先做。两个 Task 都失败测试先行。

### Task 1.1: `--verify-pending` 子命令 + `verify_pending()`

**Files:**
- Modify: `scripts/flightdeck_index.py`（加函数 + argparse 分支）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试** — 临时 deck 放两个带 `verify` 的文件（一个 active 知识件、一个 archive 工作流件）+ 一个不带的，断言扫描只列出带 `verify` 的、且带出「怎么验」值、跨 active+archive：

```python
def test_verify_pending_scans_active_and_archive(tmp_path):
    deck = tmp_path / "flightdeck"
    (deck / "checklists").mkdir(parents=True)
    (deck / "archive" / "specs").mkdir(parents=True)
    (deck / "checklists" / "foo.md").write_text(
        "---\nstatus: stale\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-08\nverify: 跑一遍 foo 流程\n---\n# foo\n", encoding="utf-8")
    (deck / "archive" / "specs" / "bar.md").write_text(
        "---\nstatus: done\nsummary: bar\nverify: 相位4 各家 live 实证\n---\n# bar\n", encoding="utf-8")
    (deck / "checklists" / "clean.md").write_text(
        "---\nstatus: active\nwhen_to_read: y\napplies_to: [b]\nlast_updated: 2026-06-08\n---\n# clean\n", encoding="utf-8")
    rows = flightdeck_index.verify_pending(str(deck))
    assert rows == [("archive/specs/bar.md", "相位4 各家 live 实证"),
                    ("checklists/foo.md", "跑一遍 foo 流程")]
```

- [ ] **Step 2: 跑测试确认失败** — `uv run pytest scripts/tests/test_flightdeck_index.py::test_verify_pending_scans_active_and_archive -v` → FAIL（`verify_pending` 未定义）。

- [ ] **Step 3: 实现 `verify_pending`**（放在 `match_signature` 附近，复用 `parse_frontmatter`）：

```python
def verify_pending(deck):
    """(path, verify-note) for every artifact carrying a `verify` field,
    across the active tree AND archive/ — the待验证 source of truth.
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
    return sorted(set(out))
```

- [ ] **Step 4: 接 argparse**（在 `--changed-since-anchor` 同区加 flag + 在 main 的 if 链里加分支，照 `--match-signature` 体例打 `path<TAB>note`）：

```python
ap.add_argument("--verify-pending", action="store_true",
                help="print (path<TAB>verify-note) for every artifact carrying a `verify` field, across active+archive; read-only")
```
```python
    if args.verify_pending:
        for path, note in verify_pending(args.deck):
            print(f"{path}\t{note}")
        return 0
```

- [ ] **Step 5: 跑测试确认通过** — 同 Step 2 命令 → PASS。
- [ ] **Step 6: Commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(index): --verify-pending 子命令——扫 active+archive 的 verify 字段（待验证真相源）"
```

### Task 1.2: `format_row` 按 `verify` 渲染 `⚠未验证` / `⚠待复核`

**Files:**
- Modify: `scripts/flightdeck_index.py:119-138`（`format_row`）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试** — 覆盖三态：知识件 `stale+verify`→`⚠未验证`、知识件 `stale` 单独→`⚠待复核`、工作流件 `done+verify`→`⚠未验证`：

```python
def test_format_row_verify_vs_stale_markers():
    # 知识件：stale + verify → ⚠未验证
    r1 = flightdeck_index.format_row("checklists", "a.md",
        {"status": "stale", "when_to_read": "x", "applies_to": "[a]", "verify": "跑一遍"})
    assert r1.startswith("⚠未验证 ")
    # 知识件：stale 单独（过期）→ ⚠待复核
    r2 = flightdeck_index.format_row("checklists", "b.md",
        {"status": "stale", "when_to_read": "x", "applies_to": "[a]"})
    assert r2.startswith("⚠待复核 ")
    # 工作流件：done + verify → ⚠未验证
    r3 = flightdeck_index.format_row("specs", "c.md",
        {"status": "done", "summary": "s", "verify": "相位4 实证"})
    assert r3.startswith("⚠未验证 ")
    # 工作流件：done 干净 → 无标记
    r4 = flightdeck_index.format_row("specs", "d.md", {"status": "done", "summary": "s"})
    assert not r4.startswith("⚠")
```

- [ ] **Step 2: 跑测试确认失败** — FAIL（当前只有 `⚠ `、且工作流分支早 return 不加标记）。

- [ ] **Step 3: 改 `format_row`** — 工作流分支（`:119-120`）加 verify 标记：

```python
    if kind in SUMMARY_KINDS:
        row = f"{link} {DASH} {status} {DASH} {fm.get('summary', '⚠ summary 缺失')}"
        if fm.get("verify"):
            row = "⚠未验证 " + row
        return row
```
知识分支把 `:136-137` 改为按 verify 区分：

```python
        if fm.get("verify"):
            row = "⚠未验证 " + row
        elif status == "stale":
            row = "⚠待复核 " + row
        return row
```

- [ ] **Step 4: 跑测试确认通过** — PASS。
- [ ] **Step 5: 全量回归** — `uv run pytest scripts/tests/ -v` 全绿（旧用例若断言旧 `⚠ ` 字样，按新语义更新——属预期，不是回归）。
- [ ] **Step 6: Commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(index): format_row 按 verify 渲染 ⚠未验证/⚠待复核（stale 两义分流，含工作流行）"
```

---

## Phase 2 — 治理文案契约（编辑型；闸 = --check + lint + diff 自检）

> protocol/templates 是 skill 体引用的真相源，先于 Phase 3。本相位无 pytest——每 Task 收尾跑 `uv run scripts/flightdeck_index.py flightdeck --check` + `uv run scripts/flightdeck_lint.py flightdeck` 全绿，并 `git diff` 逐条确认「加的是 verify 契约、改的不是既有数据模型」。

### Task 2.1: `protocol.md` —— verify 字段语义 + done/stale + 非阻塞原则 + per-kind

**Files:** Modify `skills/preflight/protocol.md`

- [ ] **Step 1: `verify` 字段语义**（落在 Frontmatter field reference / Status 区）：新增条目——`verify`：**status 的附加标记、非独立状态机、须与 status 联读**；**有字段=欠验证，值=一行「怎么验」，无字段=已验证/无需验证**；与 `note:`/`resolved_by:` 同级、可选。明确「不是第四状态」。
- [ ] **Step 2: `done` 语义**：把现「`done` = 用户签收、AI 不自评完成」补一句——needs-verify 的活 AI **可自断 `done` 但须挂 `verify: <怎么验>`**（不是静默通过，靠 preflight 反复浮出 + 可逆兜底）；no-verify 仍照旧。
- [ ] **Step 3: `stale` 含义拓宽**：`stale` 定义改为「**待复核：疑似过期 _或_ 新产出未验证**」，两来源由 `verify` 字段区分（有=未验证，无=`when_to_update` 命中的过期）。
- [ ] **Step 4: 非阻塞原则 + per-kind 通过/失败**：加一节「验证非阻塞」——可见性替代阻塞（前提：preflight 为标准必经入口，flightdeck 既有设计）；**验证通过**：删 `verify`——知识件同时 `stale→active`、工作流件留 `done`（随即可 `--archivable`）；**验证失败**：复活 `active`、`verify` 保留（无 `failed` 取值）。SKILL 须先识别 artifact 类型再动作。
- [ ] **Step 5: 闸** — `--check` + `lint` 全绿；`git diff skills/preflight/protocol.md` 确认 status 合法值集（workflow `idea/active/done`、knowledge `active/stale/obsolete`）**未变**、只加了 `verify` 附加标记。
- [ ] **Step 6: Commit** — `git commit -m "docs(protocol): verify 字段语义 + done/stale 拓宽 + 验证非阻塞 per-kind 规则"`

### Task 2.2: `templates.md` —— frontmatter `verify` 字段 + stale 文案

**Files:** Modify `skills/preflight/templates.md`（+ `scaffolds/full/` 若含模板）

- [ ] **Step 1:** spec/plan frontmatter 模板 + knowledge/docs frontmatter 模板各加一行可选注释：
  `# optional: verify: <一行怎么验>  — 有字段=欠验证（done/stale 上的附加标记，preflight 浮出待验证）；验证通过删字段`
- [ ] **Step 2:** 把模板里 `stale=疑似过期·待复核` 的注释改为 `stale=待复核（疑似过期 或 新产出未验证，由 verify 字段区分）`。两处（knowledge frontmatter + docs frontmatter）都改。
- [ ] **Step 3:** 若 `scaffolds/full/` 下有对应 frontmatter 样板/cockpit 模板，同步（`rg -l "stale=疑似过期" scaffolds skills`）。
- [ ] **Step 4: 闸** — `--check` + `lint` 全绿。
- [ ] **Step 5: Commit** — `git commit -m "docs(templates): frontmatter 加可选 verify 字段 + stale 两义文案"`

---

## Phase 3 — 仪式 skill 体（编辑型；同 Phase 2 三闸）

### Task 3.1: `exit-ritual.md` —— needs-verify 门重写 + 扫描浮出 + per-kind if-else

**Files:** Modify `skills/preflight/exit-ritual.md`（`:244-251` 自断 done 节 + `:253` 周边 + 3c 区）

- [ ] **Step 1: 重写 `:244-251` needs-verify 门** — 从「needs-verify → AI 不许自断 done」改为「needs-verify → AI **可**自断 `done + verify: <怎么验>`」；判定行改 `[判定: <理由>; 待验证: <怎么验>; done + verify]`（no-verify 行不变）。保留「外发动作本身仍先问」的边界（只放宽标记，不放宽执行）。
- [ ] **Step 2: 待验证浮出（B）** — 在 land-readiness / 3c 区写明：待验证清单由 `flightdeck_index.py --verify-pending`（active+archive 全量扫描；实现可缓存、语义等价）现扫现得，**非读 cockpit 文本**；渲染按 `verify` 显 `⚠未验证: <file> — <怎么验>` vs 过期类 `⚠待复核: <file>`；归档件仍被扫出是有意为之（非阻塞+持续可见）。
- [ ] **Step 3: 验证通过/失败 per-kind if-else** — 明确：通过=删 `verify`（知识件再 `stale→active`、工作流件留 `done` 进 `--archivable`）；失败=`mv` 回 + 翻 `active` + 保留 `verify`；先识别 artifact 类型。
- [ ] **Step 4: 闸** — `--check` + `lint` 全绿；`rg -n "不许自断|不肯软着陆" skills/preflight/exit-ritual.md` 应为空（旧阻塞措辞已清）。
- [ ] **Step 5: Commit** — `git commit -m "docs(exit-ritual): needs-verify 门改非阻塞 verify + 扫描浮出 + per-kind 通过失败"`

### Task 3.2: `landing/SKILL.md` —— 3a/3c 串 verify + --archivable 照常归档

**Files:** Modify `skills/landing/SKILL.md`（`:39` 3c + `:41` 3a + soft-landing 描述）

- [ ] **Step 1:** 3c（stale 检测）补：除 `when_to_update` 命中的过期 stale 外，**新产出未验证落 `stale + verify`**；待验证渲染走 `--verify-pending`。
- [ ] **Step 2:** 3a：`done` 件若带 `verify` **照常**进 `--archivable`（marker 随文件进 archive）——不加例外（用户拍板：最合流程）；明确 soft-landing **不再**被「要验证」挡（needs-verify 现可自断 done+verify）。
- [ ] **Step 3:** 输出格式区（`:84-94`）加一行「待验证: [N 项 / none]（来自 --verify-pending）」。
- [ ] **Step 4: 闸** — `--check` + `lint` 全绿；`git diff` 确认 `--archivable` 边图判定（`implements`/`superseded_by` 入边）未被改动、只加了「带 verify 也归档」的说明。
- [ ] **Step 5: Commit** — `git commit -m "docs(landing): 3a/3c 串 done+verify、--archivable 照常归档、soft-landing 解除验证阻塞"`

### Task 3.3: `status/SKILL.md` —— done 翻转 + verify 分支

**Files:** Modify `skills/status/SKILL.md`

- [ ] **Step 1:** `done` 翻转描述加分支：needs-verify 时翻 `done` 并写 `verify: <怎么验>` + 打印判定行；no-verify 时照旧不带 verify。引用 protocol 的 verify 字段语义（不复述定义，链接之）。
- [ ] **Step 2: 闸** — `--check` + `lint` 全绿。
- [ ] **Step 3: Commit** — `git commit -m "docs(status): done 翻转支持 + verify 分支与判定行"`

### Task 3.4: `preflight/SKILL.md` —— 扫描待验证 + 输出瘦身C + docs计数D

**Files:** Modify `skills/preflight/SKILL.md`（`:25-31` catalog + 输出格式区）

- [ ] **Step 1: catalog 加扫描** — catalog warm-up 增一步：跑 `flightdeck_index.py --verify-pending`，把结果作为**待验证清单**纳入报告（源在文件、不读 cockpit）。
- [ ] **Step 2: 瘦身（C）** — 输出格式改为：folder INDEX **仍读进上下文**（路由 priming 不变），但**用户可见输出只给计数** `docs N · checklist N · incident N`，**删整张 when_to_read/用途/applies_to 表**的回显；when_to_read 命中再读。
- [ ] **Step 3: docs（D）** — docs 保持载入（已在 `:27`），展示并入计数。
- [ ] **Step 4:** 输出保留：cockpit 对账 + git/version 一行注 + **待验证清单** + next item。
- [ ] **Step 5: 闸** — `--check` + `lint` 全绿；对照 spec C/D 节人工核「读未减、显已瘦」。
- [ ] **Step 6: Commit** — `git commit -m "docs(preflight): 加 --verify-pending 待验证报告 + 输出瘦身只显计数 + docs 计数"`

---

## Phase 4 — 套用首个对象 + resync 后 live 实证（停地板）

> 数据操作（打字段+归档）本会话可做；但「AI 按新门自动自断 done+verify、preflight 自动浮出」要 **resync 进缓存后的新会话**才生效。本相位过了才把本 spec+plan 自身翻 done。

### Task 4.1: 套用 hook spec+plan（清看板的现场验证）

**Files:** Modify `specs/2026-06-07-hook-primary-refactor.md` + `plans/2026-06-07-hook-primary-refactor-rollout.md`

- [ ] **Step 1:** 二者 frontmatter 加 `verify: 相位4 各家 live 实证`、`status` 翻 `done`（其实现 substantively 完成，仅欠 hook live 实证——正是 needs-verify 的范型）。
- [ ] **Step 2:** 跑 landing（或 `flightdeck_index.py flightdeck` + Land Routine）：`--archivable` 把二者归档进 `archive/`，`## 进行中` 清空。
- [ ] **Step 3: 现场断言** — `uv run scripts/flightdeck_index.py flightdeck --verify-pending` 列出这两件（+ 本 spec/plan，若也已打 verify）；cockpit `## 进行中` 不再含 hook 两件；`--check` + `lint` 全绿。
- [ ] **Step 4: Commit** — `git commit -m "chore(deck): hook spec+plan done+verify 归档（首个适用对象，看板清空）"`

### Task 4.2: resync + 新会话 live 实证（手动，非本会话内）

- [ ] **Step 1: resync** — 按 `checklists/local-plugin-testing.md` 同步工作树进插件缓存。
- [ ] **Step 2: 新会话跑 preflight，核 spec 验收四条**：① 待验证报告 = `--verify-pending` 输出**逐行一致**；② 手动改 cockpit 后重跑、清单**不变**（源在文件）；③ 输出已瘦身（只计数、无路由表刷屏）；④ 对某 `verify` 件删字段后重跑、它**退出**清单。
- [ ] **Step 3: 行为核** — 新会话里给一个 needs-verify 小活，确认 AI 自断 `done + verify` 并打印判定行、不再死锁 active；新写一个 checklist 未验证 → 落 `stale + verify` 渲染 `⚠未验证`。
- [ ] **Step 4: 全绿则收口** — 本 spec（`2026-06-08-nonblocking-verify-preflight-slim`）+ 本 plan 自身验证通过 → 删自身 `verify`、翻 `done`、归档；cockpit `## 下一步` 清。未过 → `flightdeck:new incident` 记症状，停地板不回退。

---

## Self-Review（写完对 spec 核）

- **Spec 覆盖**：A 验证非阻塞=Task 2.1（契约）+3.1（门）+3.3（status）✓；`verify` 锚点+扫描=1.1 ✓；stale 两义渲染=1.2 ✓；B 浮出=3.1+3.4 ✓；C 瘦身=3.4 ✓；D docs=3.4 ✓；per-kind 通过/失败=2.1+3.1 ✓；首个对象+live=4.1/4.2 ✓；可脚本验收（`--verify-pending` 逐行一致 + 退出队列）=1.1+4.2 ✓。
- **占位扫描**：Phase 2–3 编辑任务给的是「锚点 + 改成什么 + 闸」而非最终全文——这是 flightdeck 文案任务的既定粒度（同 hook-rollout Task 2.x），非占位；脚本任务（1.1/1.2）给了完整测试+实现代码。
- **类型/命名一致**：`verify`（字段名）、`verify_pending()`（函数）、`--verify-pending`（flag）、`⚠未验证`/`⚠待复核`（标记串）、`path<TAB>note`（子命令输出）各 Task 前后一致；`fm.get("verify")` 真值判定贯穿 1.2 与 1.1。
- **次序**：脚本(1)→契约(2)→skill 体(3)→套用(4)，引用方向单向不成环。
