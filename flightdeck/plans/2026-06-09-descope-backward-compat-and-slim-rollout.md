---
status: active
summary: 把 de-scope spec 逐文件落地：相位1 删向后兼容子系统（flightdeck_index.py 删 verdict/version 6 函数 + --verdict 子命令 + version_mismatch 守卫，TDD 同步删测试；MIGRATION.md 200 行史→极简戳；legacy/pre-3.0 处理）→相位2 命令职责重划（preflight 删 step1/4/4a 收敛纯读零写、landing 剥 version/verdict 留 stale 单仪式、walkaround 删 migration 审查聚焦本版内）→相位3 incidents 吸纳-退役（逐条 triage：可设计防范/仅可警示，吸纳进必经路径后翻 obsolete，过时删）→相位4 热/冷预算扫尾（注入≤25行/preflight SKILL≤45/walkaround≤80 + 冷路径上限 + cockpit 软上限）；每相位测试绿+regen clean+before/after token，行为恢复验收，可逐相位 git revert
last_updated: 2026-06-09
implements: specs/2026-06-09-descope-backward-compat-and-slim.md
---

# flightdeck 3.0 大瘦身 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 砍掉 flightdeck 整个向后兼容/迁移/版本校验子系统（3.0 = 格式基线第 0 版），把校验收归 walkaround、preflight 变纯读零写、incidents 吸纳退役、热/冷路径按预算瘦身——大幅压低每会话固定成本与单次 /preflight 成本，恢复载荷零损失。

**Architecture:** 四相位顺序执行，各自独立 commit（可逐相位 `git revert`）。相位 1 是脚本层（TDD：删函数 + 同步删测试 + grep 断言无悬挂引用 + 全 deck regen clean）。相位 2–4 是 skill prose（确定性删除/迁移 + grep 断言 + `wc -m` before/after + 行为恢复验收），最终 prose 在执行时按预算就地重写，本计划给出**删什么/迁到哪/怎么验**而非预烤字符串。

**Tech Stack:** Python 3（`uv run pytest`）、`scripts/flightdeck_index.py`、markdown skill 文件、git、`wc -m` / `grep` 作度量与断言。

**前置铁律（每相位都遵守）：**
- 每相位末：`uv run pytest scripts/tests/` 全绿 + `uv run scripts/flightdeck_index.py flightdeck`（regen/lint clean）+ 记录改动文件 `wc -m` before/after。
- 本仓库 **只本地 commit，绝不 push**（House Rule + 用户铁律）。
- dual-shell 仓库：多行 commit message 用 `git commit -F <file>` 或 PowerShell here-string，**不要**在 Bash 工具里塞 PowerShell here-string（见 incident `powershell-herestring-in-bash-tool`）。
- 「校验」只迁不灭：删的是**跨版本**校验；**本版内**完整性审查迁去 walkaround，不删。

---

## File Structure（改动地图）

**相位 1 — 脚本层：**
- Modify: `scripts/flightdeck_index.py` — 删 `_migration_layout` / `_vtuple` / `_structural_signal` / `_classify_version` / `layout_verdict` / `version_mismatch` 六函数；删 `RETIRED_STATUSES` 常量、`_workflow_fms`（若删后无引用）；删 `--verdict` 子命令与 `main()` 里的 `version_mismatch` refuse 守卫。
- Modify: `scripts/tests/test_flightdeck_index.py` — 删上述函数对应测试（约 line 424–561 区段：`test_refuses_..._version_mismatch` / 全部 `layout_verdict` 断言 / `_classify_version` 断言 / `test_verdict_flag_...`）。
- Modify: `MIGRATION.md` — 200 行迁移史 → 极简 stub（保留 `current: 3.0` 供发布管线；删 `layout_need_update` 与全部迁移表）。
- Modify: `scripts/flightdeck_lint.py` — 删唯一 1 处 verdict/version 引用（若有）。
- Verify-only: `scripts/bump_version.py`（确认仍能更新 MIGRATION.md `current`，不依赖被删字段）。

**相位 2 — 命令 prose：**
- Modify: `skills/preflight/SKILL.md`（删 step 1 verdict、step 4 version note、整块 step 4a；改 step 0 为入场前置）。
- Modify: `skills/preflight/protocol.md`（删 19 处 verdict/version 段；§ Rule resolution order 去掉 layout verdict）。
- Modify: `skills/preflight/templates.md`（删 MIGRATION 模板段；rules.md 模板留极简 `version`）。
- Modify: `skills/landing/SKILL.md`（剥 version/verdict 2 处；stale 翻转保留为单仪式、注明机械路径重叠触发）。
- Modify: `skills/walkaround/SKILL.md`（删 migration/layout-version/version-bump 审查 20 处；聚焦本版内完整性 + 注明「只审不修，修复=regen」）。
- Modify: `skills/status/SKILL.md` / `skills/new/SKILL.md` / `skills/launch/SKILL.md` / `skills/emit-agents-md/SKILL.md`（各 1 处 verdict/version 残留清理）。
- Modify: `flightdeck/rules.md`（确认 `version: 3.0` 极简戳保留，删任何 pre-3.0 key 注释）。

**相位 3 — incidents：**
- Modify: 各 `flightdeck/incidents/*.md`（逐条 triage：吸纳点写入对应权威件后翻 `status: obsolete`，或过时直接删）。
- Modify: 吸纳落点（如 `skills/preflight/protocol.md` 某章节 / 对应 `SKILL.md` 祈使步 / `scripts/` 守卫 / `scaffolds/`）。
- Regen: landing 排空 `obsolete` 进 `flightdeck/archive/incidents/`。

**相位 4 — 预算：**
- Modify: `hooks/_context.sh`（注入 directive 文案压到 ≤ 25 行）。
- Modify: `skills/*/SKILL.md`（按各自上限收）。
- Modify: `skills/preflight/protocol.md` / `exit-ritual.md` / `templates.md` / `folder-semantics.md`（冷路径上限）。
- Modify: `flightdeck/cockpit.md`（恢复槽软上限自检）。

---

## 相位 1：删向后兼容子系统（脚本层，TDD）

> 删除式 TDD 的「红」= 先确认有引用/有测试在跑该行为；「绿」= 删后全套测试通过且 grep 无悬挂引用。逐函数删、逐步提交。

### Task 1.1：删 `main()` 的 version_mismatch refuse 守卫 + 其测试

**Files:**
- Modify: `scripts/flightdeck_index.py`（`main()` 内 version_mismatch 分支）
- Test: `scripts/tests/test_flightdeck_index.py::...test_refuses_and_writes_nothing_on_version_mismatch`（约 line 424）

- [ ] **Step 1：读现状定位。** `grep -n "version_mismatch" scripts/flightdeck_index.py` —— 找到 `main()` 里调用它来「版本不匹配则拒绝 regen」的分支，及函数定义（line 503）。确认 `main()` 中的调用点（refuse 守卫）。
- [ ] **Step 2：删测试。** 删 `test_refuses_and_writes_nothing_on_version_mismatch` 整个测试方法（line ~424 起，到下一个 `def test_` 前）。
- [ ] **Step 3：删 `main()` 守卫。** 删 `main()` 中 `version_mismatch(...)` 的调用与「mismatch → 打印拒绝 + return 非零」分支；保留正常 regen 路径。
- [ ] **Step 4：跑测试。** `uv run pytest scripts/tests/test_flightdeck_index.py -q` —— 期望全绿（删了测试 + 删了对应行为，无新失败）。
- [ ] **Step 5：commit。** `git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py` + `git commit -m "refactor(index): 删 version_mismatch regen 守卫（3.0=第0版无跨版本校验）"`

### Task 1.2：删 `--verdict` 子命令 + 其测试

**Files:**
- Modify: `scripts/flightdeck_index.py`（argparse `--verdict` 定义 + dispatch）
- Test: `scripts/tests/test_flightdeck_index.py::...test_verdict_flag_prints_and_writes_nothing`（约 line 545）

- [ ] **Step 1：定位。** `grep -n "verdict" scripts/flightdeck_index.py` —— 找 argparse 里 `--verdict` 的 `add_argument` 与 `main()` 中 `if args.verdict:` dispatch（调用 `layout_verdict`）。
- [ ] **Step 2：删测试。** 删 `test_verdict_flag_prints_and_writes_nothing`（line ~545–561）。
- [ ] **Step 3：删 CLI。** 删 `--verdict` 的 `add_argument` 行 + `main()` 中其 dispatch 分支。保留 `--archivable`/`--verify-pending`/`--changed-since-anchor`/`--advance-candidates`/`--match-signature` 等非版本子命令。
- [ ] **Step 4：跑测试 + 冒烟。** `uv run pytest scripts/tests/ -q`（全绿）；`uv run scripts/flightdeck_index.py flightdeck --verdict` 期望报「unrecognized arguments」（确认子命令已消失）。
- [ ] **Step 5：commit。** `git commit -m "refactor(index): 删 --verdict 子命令"`

### Task 1.3：删 verdict/version 六函数 + 死常量 + 同步删测试

**Files:**
- Modify: `scripts/flightdeck_index.py`（line 330–515 区段，**保留** 350–450 的 `_workflow_fms`/`archivable_*`/`spec_advance_candidates`——先判其去留）
- Test: `scripts/tests/test_flightdeck_index.py`（line ~465–542 verdict/_classify_version 断言块）

- [ ] **Step 1：判依赖去留。** `grep -n "_workflow_fms\|RETIRED_STATUSES" scripts/flightdeck_index.py` —— `RETIRED_STATUSES` 仅 `_structural_signal` 用 → 随删；`_workflow_fms` 被 `_structural_signal`+`layout_verdict` 用，若**别处无引用**则随删（grep 确认）。
- [ ] **Step 2：删测试块。** 删 `test_flightdeck_index.py` 中所有 `layout_verdict(...)` 断言（line ~465–515）与 `_classify_version(...)` 断言（line ~520–532）、`test_...malformed`（line ~542）—— 即整个 verdict/版本分类测试簇。
- [ ] **Step 3：删函数。** 删 `_migration_layout`(333) / `_vtuple`(343) / `_structural_signal`(453) / `_classify_version`(468) / `layout_verdict`(483) / `version_mismatch`(503) 六函数；删 `RETIRED_STATUSES`(330)；若 Step 1 判定无引用则删 `_workflow_fms`(350)。**保留** `_active_inbound_targets`/`archivable_done`/`archivable_obsolete`/`spec_advance_candidates`/`last_anchor_ref`/`changed_since_anchor`。
- [ ] **Step 4：grep 断言无悬挂。** `grep -nE "layout_verdict|_classify_version|_structural_signal|version_mismatch|_migration_layout|_vtuple" scripts/` —— 期望**零命中**（含测试、含 lint 脚本）。若 `flightdeck_lint.py` 有 1 处引用，一并删。
- [ ] **Step 5：跑测试 + regen。** `uv run pytest scripts/tests/ -q`（全绿）；`uv run scripts/flightdeck_index.py flightdeck`（regen clean，无报错）。
- [ ] **Step 6：commit。** `git commit -m "refactor(index): 删 verdict/version 校验六函数 + 死常量（向后兼容子系统脚本层清零）"`

### Task 1.4：MIGRATION.md 200 行史 → 极简 stub（保发布管线）

**Files:**
- Modify: `MIGRATION.md`
- Verify: `scripts/bump_version.py`（确认仍可更新 `current`）

- [ ] **Step 1：确认管线依赖。** `grep -n "current\|layout_need_update\|MIGRATION" scripts/bump_version.py` —— 确认 bump 只改 `current:`（保留），不依赖 `layout_need_update`（可删）。
- [ ] **Step 2：重写 MIGRATION.md。** 替换为极简 stub：frontmatter 仅 `current: 3.0`（删 `layout_need_update`）；正文一段——「3.0 是格式基线（第 0 版）。3.0 之前无向后兼容；`flightdeck/rules.md` 的 `version` 是 deck 版本戳。当 3.1 改格式时，在此记录 3.0→3.1 迁移。」删除全部历史迁移表（1.1.x→…→3.0）。
- [ ] **Step 3：断言。** `wc -l MIGRATION.md` 期望 ≈ ≤ 12 行；`uv run scripts/flightdeck_index.py flightdeck`（确认无脚本再读 MIGRATION 报错）。
- [ ] **Step 4：commit。** `git commit -m "docs(migration): 200 行迁移史→极简基线 stub（3.0=第0版；保 current 戳供发布管线）"`

### Task 1.5：相位 1 收口——grep 总断言 + token 记录

- [ ] **Step 1：跨树 grep。** `grep -rnE "layout_verdict|compatible-behind|structural-behind|_migration_layout|version_mismatch|layout_need_update" scripts/ MIGRATION.md` —— 期望仅剩**无害**字面（无逻辑）。记录命中清单。
- [ ] **Step 2：全套测试。** `uv run pytest scripts/tests/ -q` 全绿。
- [ ] **Step 3：token 记录。** `wc -m scripts/flightdeck_index.py MIGRATION.md`（vs 基线，记 before/after 进 commit body 或 Progress）。
- [ ] **Step 4：相位 commit（若有零散改动）。** `git commit -m "chore(index): 相位1 收口——向后兼容脚本子系统清零"`

---

## 相位 2：命令职责重划（prose——校验只在 walkaround）

> 这些是 skill 散文编辑，无脚本/测试改动。每文件：确定性删除目标段 + grep 断言 + `wc -m` before/after。最终措辞执行时就地写，本计划定**删什么/留什么/迁到哪**。

### Task 2.1：preflight 收敛为纯读零写

**Files:** `skills/preflight/SKILL.md`

- [ ] **Step 1：删 step 1 layout verdict。** 删 step 1 中「Layout verdict（fast path `--verdict` / fallback MIGRATION）」整段；step 1 只留「读 rules.md（House Rules / git 推断）」。
- [ ] **Step 2：删 step 4 version note。** step 4 表格删「layout 落后 → walkaround」行（保留 branch≠focus / detached HEAD 行）。
- [ ] **Step 3：删整块 step 4a。** 删 step 4a「Retroactive safety net」全部三检查（(i) 补偿 stale / (ii) graduate 补偿 / (iii) obsolete 提醒）—— preflight 不再做任何补偿写入。
- [ ] **Step 4：改 step 0 为入场前置措辞。** step 0 保留「无 cockpit.md → 指向 /launch 并 STOP」，但措辞标注为**入场前置**（「此处有无 deck 可读」），删任何「within-deck 文件存在性兜底」语（如 rules.md「if present」改为直接「读 rules.md」）。
- [ ] **Step 5：删 Output format + Don't 列表里对应行。** Output format 删 verdict/version note 行；「Don't do」删「Don't write version / migrate」「the one allowed write」等已不适用条目（preflight 现零写）。
- [ ] **Step 6：断言。** `grep -nE "verdict|version|step 4a|allowed write|migrat" skills/preflight/SKILL.md` 期望仅剩无害提及；`wc -m skills/preflight/SKILL.md`（记 before 13554）。
- [ ] **Step 7：commit。** `git commit -m "docs(preflight): 收敛纯读零写——删 verdict 步/version note/整块 step 4a"`

### Task 2.2：preflight/protocol.md + templates.md 去 verdict

**Files:** `skills/preflight/protocol.md`、`skills/preflight/templates.md`

- [ ] **Step 1：protocol.md 删 verdict 段。** `grep -n "verdict\|MIGRATION\|migrat\|layout_need\|compatible-behind\|structural-behind" skills/preflight/protocol.md`（19 处）；删「Layout verdict / 版本校验 / 迁移」相关章节；§ Rule resolution order 删 layout verdict 提及（保留 git 推断 + House Rule 顺序）；保留 `verify` 非阻塞、status、INDEX、folder map 等。
- [ ] **Step 2：templates.md 去 MIGRATION 模板。** 删 MIGRATION.md 模板段；rules.md 模板留极简 `version: 3.0` + House Rules（删 pre-3.0 key 注释 / `layout` 行）。
- [ ] **Step 3：断言 + 记录。** 两文件 grep 仅剩无害提及；`wc -m`（before：protocol 53522 / templates 24042）。
- [ ] **Step 4：commit。** `git commit -m "docs(preflight): protocol/templates 去 verdict/migration/version 校验段"`

### Task 2.3：landing 剥 version/verdict，stale 留单仪式

**Files:** `skills/landing/SKILL.md`、`skills/preflight/exit-ritual.md`

- [ ] **Step 1：landing 删 version/verdict。** `grep -n "verdict\|version\|migrat" skills/landing/SKILL.md`（2 处）；删「layout guard / version bump / 迁移」相关；保留 landing 核心：分类知识、regen 变动 INDEX、回写 cockpit、堵 hanging、smoke、本地 commit（push 问）。
- [ ] **Step 2：stale 翻转标注机械路径触发。** 在 landing（及 exit-ritual 对应段）确认 `when_to_update → stale` 翻转保留，并把措辞改为**机械路径重叠触发**（`--changed-since-anchor` ∩ `applies_to`，不读 doc 全文）+ 注明这是退场单仪式（preflight 入场半边已删）。删 exit-ritual 里任何指向 preflight 4a 补偿的双仪式措辞。
- [ ] **Step 3：断言 + 记录。** grep 仅剩无害；`wc -m`（landing before 一栏、exit-ritual before 44371）。
- [ ] **Step 4：commit。** `git commit -m "docs(landing): 剥 version/verdict，stale 收敛为退场单仪式（机械路径触发）"`

### Task 2.4：walkaround 删 migration 审查，聚焦本版内完整性

**Files:** `skills/walkaround/SKILL.md`

- [ ] **Step 1：定位。** `grep -n "verdict\|migrat\|layout-version\|version-bump\|legacy\|compatible-behind\|structural-behind" skills/walkaround/SKILL.md`（20 处）。
- [ ] **Step 2：删跨版本审查。** 删 migration offer / layout-version 审查 / version-bump 提示 / legacy 路径（charts→references、landed→archive）检测 / pre-3.0 key 审查。**保留**本版内完整性审查：cockpit/rules/specs/plans/incidents/checklists/docs status 合法性、INDEX↔folder 一致（含嵌套）、cockpit `## 进行中` AUTO 一致、孤儿 plan、死链、stray 文件、AGENTS.md drift、INFO（done-but-unlanded / 缺 summary/last_updated / 悬挂 supersedes/related）。
- [ ] **Step 3：加「只审不修」注。** walkaround 浮出漂移但不改；标注修复路径 = 确定性 regen（`flightdeck_index.py` 或 landing）。
- [ ] **Step 4：断言 + 记录。** `grep` migration 词零命中（除无害）；`wc -l skills/walkaround/SKILL.md`（before 233，目标见相位 4）。
- [ ] **Step 5：commit。** `git commit -m "docs(walkaround): 删跨版本 migration 审查，聚焦本版内完整性（只审不修）"`

### Task 2.5：其余 SKILL.md verdict/version 残留清理

**Files:** `skills/status/SKILL.md`、`skills/new/SKILL.md`、`skills/launch/SKILL.md`、`skills/emit-agents-md/SKILL.md`、`skills/preflight/folder-semantics.md`、`flightdeck/rules.md`

- [ ] **Step 1：逐文件 grep。** `grep -rnE "verdict|version|migrat|layout_need|compatible-behind|legacy" skills/status/SKILL.md skills/new/SKILL.md skills/launch/SKILL.md skills/emit-agents-md/SKILL.md skills/preflight/folder-semantics.md`（各 1–2 处）。
- [ ] **Step 2：删残留。** 删每处跨版本 verdict/version/migration 提及；`launch` 若提「写 version」仅留「写极简 `version: 3.0` 戳」。`folder-semantics.md` 删 legacy 重命名（charts/landed）历史段。
- [ ] **Step 3：rules.md 核对。** 确认 `flightdeck/rules.md` 只剩 `version: 3.0` + House Rules，无 pre-3.0 key。
- [ ] **Step 4：相位 2 收口 + regen + 行为验收。** `uv run scripts/flightdeck_index.py flightdeck`（regen clean）；**行为恢复手测**：另起干净 shell 跑 `/flightdeck:preflight` 心智走查——确认仍能从 cockpit+INDEX 重建「下一步 + 关键上下文」、足以继续执行。
- [ ] **Step 5：commit。** `git commit -m "docs(skills): 清 status/new/launch/emit/folder-semantics 的 verdict/version 残留——相位2 收口"`

---

## 相位 3：incidents 吸纳 → 退役 → 清理

> 逐条 triage。判据见 spec §3：**可设计防范**（结构性消除 + 退役）/ **仅可警示**（吸纳进**必经路径**权威件后翻 obsolete）/ **过时**（删）/ **不可防范又无落点**（留活跃）。「吸纳完成」客观判据 = 警示落到热路径祈使必经步 or 对应命令必读 protocol 章节（非 appendix）。

### Task 3.1：incidents 逐条 triage 决策表

**Files:** `flightdeck/incidents/*.md`（9 条）

- [ ] **Step 1：列当前 9 条 + 各自分类。** 读 `flightdeck/incidents/INDEX.md`，对每条标注 triage 类别（可设计防范 / 仅可警示 / 过时 / 留活跃）与**吸纳落点文件**。初判（执行时复核）：
  - `2026-06-05-active-workflow-missing-summary-keyerror` → 可设计防范？（脚本是否已守卫 missing summary）→ 若已守卫则吸纳进 script-layer doc + 退役。
  - `2026-06-07-git-add-partial-stages-renamed-modified-file` → 仅可警示 → 吸纳进 `skills/landing/SKILL.md` Land Routine 祈使步。
  - `2026-06-07-windows-python-stub-board-sync-noop` → 仅可警示 → 吸纳进 `docs/cross-host-hooks.md` 或 hooks 注释必读处。
  - `2026-06-07-workflow-has-no-superseded-status` → **可能过时**（本 spec 删 verdict/version；若该坑讲的机制仍在则留，否则删）。
  - `gitignored-deck-git-mode-seam` → 仅可警示 → 吸纳进 protocol § git 推断。
  - `index-row-summary-delimiter` → 可设计防范？→ 吸纳进 protocol INDEX 行格式段。
  - `powershell-herestring-in-bash-tool` → 仅可警示（不可根除）→ 吸纳进 protocol/commits checklist 必读处（**本计划前置铁律已含此条**，落点 = `checklists/commits.md` or protocol commit 段）。
  - `scaffold-ships-verbatim` → 仅可警示 → 吸纳进 `skills/launch/SKILL.md` + `incident scaffold` 注。
  - `skill-prose-links-into-dogfood-deck` → 仅可警示 → 吸纳进 protocol/skill 作者约定段。
- [ ] **Step 2：用户确认决策表。** 把 Step 1 决策表呈给用户签收（删 vs 退役 vs 留活跃逐条），**有删除即先问**（删文件是不可逆外发性动作）。

### Task 3.2：执行吸纳（逐条，吸纳点先写）

**Files:** 各吸纳落点权威件 + 对应 `incidents/*.md`

- [ ] **Step 1：对每条「吸纳」类——先写吸纳点。** 把该 incident 的教训以**一行祈使**（热路径）或**一段**（对应 protocol 章节）写进 Step-1 决策表确定的必经落点。
- [ ] **Step 2：验「会被读到」。** 确认落点是该命令必经路径（祈使步 / 必读章节），非 appendix；否则换落点。
- [ ] **Step 3：翻 obsolete。** 吸纳完成的 incident frontmatter `status: active → obsolete`（教训已进权威件，留盘 grep 防回归）。
- [ ] **Step 4：删过时项。** 「过时」类 incident（如确认讲已删机制的）`git rm`，commit body 记一行原因。
- [ ] **Step 5：commit（分批）。** 每吸纳一批 `git commit -m "docs(incidents): 吸纳 <slug> 教训进 <落点> + 翻 obsolete"`。

### Task 3.3：landing 排空 obsolete + regen

- [ ] **Step 1：确认 archivable。** `uv run scripts/flightdeck_index.py flightdeck --archivable`（应列出新翻的 obsolete incidents）。
- [ ] **Step 2：跑 landing 排空。** 经 `/flightdeck:landing` Land Routine 把 obsolete incidents `git mv` 进 `flightdeck/archive/incidents/`（注意 git mv 改名+改内容的 staging，见 incident `git-add-partial-...`）。
- [ ] **Step 3：regen + 断言。** `uv run scripts/flightdeck_index.py flightdeck`；`incidents/INDEX.md` 活跃数显著少于 9；archive 留盘可 grep。
- [ ] **Step 4：commit。** landing 自带 commit（`Flightdeck-Sync:` trailer）。记 incidents 活跃 before/after 数。

---

## 相位 4：热/冷预算扫尾（防再膨胀）

> 按预算就地压。每文件 `wc` before/after，达标即止；不达标继续下沉冷路径。

### Task 4.1：注入 directive ≤ 25 行

**Files:** `hooks/_context.sh`（注入正文）

- [ ] **Step 1：定位注入正文。** 读 `hooks/_context.sh` 里注入的 directive 文本块（每会话 SessionStart 吃）。
- [ ] **Step 2：压到 ≤ 25 行。** 只留最小祈使：入场 handoff、退场 soft-land 分类、board-sync 归属一句；解释/为什么下沉到 protocol（注入里给「详见 preflight protocol」指针）。
- [ ] **Step 3：断言。** `wc -l` 注入块 ≤ 25；`FLIGHTDECK_HOOK_DEBUG=1` 验注入仍完整投递（心智或实测）。
- [ ] **Step 4：commit。** `git commit -m "refactor(hooks): 注入 directive 压到 ≤25 行（热路径预算）"`

### Task 4.2：各 SKILL.md 按上限收

**Files:** `skills/preflight/SKILL.md`（≤ ~45 行）、`skills/walkaround/SKILL.md`（≤ ~80 行）、其余各 SKILL.md（执行时定上限）

- [ ] **Step 1：preflight/SKILL.md ≤ ~45 行。** 纯读+报告自然短；步骤化清单，细节指针指向 protocol。`wc -l`（before 123）。
- [ ] **Step 2：walkaround/SKILL.md ≤ ~80 行。** 删 migration 后已瘦；审查项列表化，每项细节指向 protocol。`wc -l`（before 233）。
- [ ] **Step 3：其余 SKILL.md。** landing/status/new/launch/emit 各定上限收（祈使清单化）。
- [ ] **Step 4：断言。** 每文件达标；`uv run scripts/flightdeck_index.py flightdeck` regen clean（skill 编辑不影响 deck，但跑一遍保险）。
- [ ] **Step 5：commit。** `git commit -m "refactor(skills): 各 SKILL.md 按热路径预算收（细节下沉 protocol）"`

### Task 4.3：冷路径上限 + cockpit 软上限

**Files:** `skills/preflight/protocol.md` / `exit-ritual.md` / `templates.md` / `folder-semantics.md`、`flightdeck/cockpit.md`

- [ ] **Step 1：冷路径设上限。** 给 protocol/exit-ritual/templates/folder-semantics 各定字符上限（接住相位 2/3 下沉来的细节后，去重/合并重叠段，确保净瘦或持平——不准被砍内容在此处净膨胀）。
- [ ] **Step 2：cockpit 软上限自检。** 确认 `## 下一步` ≤ ~8 行、`## 关键上下文` ≤ ~6 行（软线；超则精简，非截断）；确认被砍内容**未回灌** cockpit/INDEX。
- [ ] **Step 3：断言。** `wc -m` 全套冷路径 + cockpit；对账被删散文没有净流回。
- [ ] **Step 4：commit。** `git commit -m "refactor(skills): 冷路径设上限 + cockpit 恢复槽软上限（防再膨胀）"`

### Task 4.4：终验收（spec 验收条目逐项核）

- [ ] **Step 1：token 总账。** `wc -m` 汇总：preflight 单次（SKILL+读取）vs 基线 ≈9k——确认下降一半量级；注入 vs ≈7k 基线下降。
- [ ] **Step 2：测试 + regen。** `uv run pytest scripts/tests/`（全绿）；`uv run scripts/flightdeck_index.py flightdeck`（regen/lint clean）。
- [ ] **Step 3：向后兼容逻辑清零。** `grep -rnE "layout_verdict|migrat|compatible-behind|structural-behind|layout_need" skills/ scripts/ MIGRATION.md` —— 仅剩无害字面（发布管线 / stub / 测试数据）。
- [ ] **Step 4：行为恢复验收。** 模拟「关闭 → 新开 preflight」，恢复出的上下文**足以继续执行 cockpit 指向的下一步**（针对有非空下一步的状态测）。失败 → `git revert` 对应相位、重审。
- [ ] **Step 5：incidents 收缩核对。** 活跃 incidents 数 << 9，无教训丢失（吸纳点 + archive grep 可验）。
- [ ] **Step 6：终 commit / landing。** 经 landing 收口，cockpit/INDEX 回写，记最终 before/after token 总账。

---

## Self-Review（plan vs spec 覆盖核对）

- **spec §1（砍子系统）** → 相位 1（Task 1.1–1.5：脚本六函数 + --verdict + version_mismatch + MIGRATION stub）+ 相位 2 Task 2.2/2.5（skill prose verdict 残留）。✅
- **spec §2（命令职责重划）** → 相位 2 Task 2.1（preflight 纯读零写）/ 2.3（landing 剥 version、stale 单仪式机械触发）/ 2.4（walkaround 聚焦本版内、只审不修）。✅
- **spec §3（incidents 吸纳退役）** → 相位 3（Task 3.1 triage 表 + 用户签收 / 3.2 吸纳先写落点再翻 obsolete / 3.3 landing 排空）。✅
- **spec §4（热/冷预算铁律）** → 相位 4（注入≤25 / preflight≤45 / walkaround≤80 / 冷路径上限 / cockpit 软上限）。✅
- **spec §5（假定良构 deck）** → 相位 2 Task 2.1 Step 4（step 0 入场前置、删 within-deck 兜底）。✅
- **spec 验收 + 回滚** → 相位 4 Task 4.4（token 总账 / 行为恢复验收 / grep 逻辑清零 / incidents 收缩）+ 各相位独立 commit 可 `git revert`。✅
- **保留项不误伤** → bump_version.py/version-bump.md（Task 1.4 Step 1 仅 verify）、`verify` 标记、`match_signature`（相位 1 显式保留清单）。✅
- **incidents 教训不丢**（含本计划依赖的 powershell-herestring / git-add-partial）→ 相位 3 吸纳点先写、验「会被读到」再退役；本计划「前置铁律」已内化这两条，正是吸纳落点之一。✅

**待执行时定的具体数值（非占位，是 plan→执行的合理延迟）**：各 SKILL.md/冷路径精确字符上限、incidents 逐条最终落点——相位 4 / 相位 3 执行时按 `wc` 实测与 triage 复核敲定。
