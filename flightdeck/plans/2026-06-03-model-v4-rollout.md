---
status: active
implements: specs/2026-06-03-model-v4-folder-state-cockpit-design.md
summary: model-v4 分 6 phase 实施——数据模型真相源 → flightdeck_index 扩展(+测试) → 4 skill 行为 → scaffolds/emit/MIGRATION → dogfood 迁移本仓库 → 验证收尾；并入 3.0
last_updated: 2026-06-03
---

# model-v4 模型重构 实施计划（并入 3.0）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐 task 实施。步骤用 `- [ ]` 复选框跟踪。

**Goal:** 把 flightdeck 从「人机协作」模型重构为「AI 全自动驱动」模型——folder 7→5、状态 6→4、cockpit 由 active 状态自动派生。

**Architecture:** 真相源文档先行（protocol/folder-semantics/templates/exit-ritual）→ 机械层脚本（flightdeck_index.py 扩展 + 测试）→ 四个 skill 行为对齐 → scaffold/emit/MIGRATION → 最后迁移并 dogfood 本仓库自己的 deck。每 phase 末单次提交。

**Tech Stack:** Markdown skill 文档 + Python stdlib 脚本（`flightdeck_index.py`）+ pytest。

**任务类型约定：** 本仓库的"实现"分两类——
- **代码型**（`flightdeck_index.py` 及其测试）：给出具体测试 + 实现代码。
- **文档型**（skill `.md` prose）：给出**段落级改动规格**（删哪段 / 加什么语义 / 关键定句），执行者据规格写流畅 prose——规格已无需再做设计决策，不是占位符。

**依据 spec：** `specs/2026-06-03-model-v4-folder-state-cockpit-design.md`（§ 编号下引用其条款）。

---

## Phase 0 — 数据模型真相源（先行，后续全部引用它）

**Files:**
- Modify: `skills/preflight/protocol.md`
- Modify: `skills/preflight/folder-semantics.md`
- Modify: `skills/preflight/templates.md`
- Modify: `skills/preflight/exit-ritual.md`

- [ ] **0.1 protocol.md — 数据模型与状态**
  - `## Status`：workflow 状态集改为 `idea / active / done / scrapped`；流转图改 `idea → active → done`，`任意 → scrapped`；删 `pending/awaiting-review/blocked`。knowledge 状态不变。
  - `## Data model`：workflow kinds 改为 `specs/ plans/`（删 `sketches/`）；knowledge kinds `incidents/ checklists/ charts/`（删 `debriefs/`）。
  - `## Frontmatter field reference`：删 `reviewed`（debriefs）行；新增**可选 `note:`**（workflow，承载"为什么没动"诊断；spec §1.2）；`summary`/`last_updated` 不变。
  - `## Folder map`：5 folder（specs/plans/incidents/checklists/charts + landed）。
  - `## Lifecycle`：`idea →(改一个字段)→ active → done`；删"promote = 移文件"表述。
  - **验证**：grep 确认 protocol 内无残留 `pending|awaiting-review|blocked|debriefs|reviewed:`（除迁移/兼容说明段）。

- [ ] **0.2 folder-semantics.md — folder 用途**
  - 删 `### sketches/` 段；在 `### specs/` 段加："idea 态 = 未启动想法（无日期前缀），`idea→active` 补 `YYYY-MM-DD-`；scrapped 留原位、不归档（spec §1.4）"。
  - 删 `### debriefs/` 段；在文首"删减说明"或 specs 段注明：外部反馈走根 `tmp/`（用户习惯，flightdeck 不规定），disposition 落进对应 spec 的 `## 评审纪要`（spec §3）。
  - 决策表 / folder 树 / anti-patterns 表：去掉 sketches、debriefs 行。
  - `specs/INDEX` 状态分组规则（spec §1.4 评审 D）：待启动（idea）/ 进行中·完成（active·done）两组，scrapped 不出现。
  - **验证**：folder 树与 protocol §Folder map 一致（5 folder）。

- [ ] **0.3 templates.md — 模板**
  - 删 `sketch` / `debrief` 模板块；spec 模板 frontmatter 示例 `status: idea`（或注明 idea/active/done/scrapped）+ 可选 `note:`。
  - cockpit 模板改新结构（spec §2.2）：`Active focus` + `## 进行中`（含 `<!-- AUTO:inprogress -->…<!-- /AUTO -->`）+ `## 下一步` + `## Hanging tasks`。
  - **验证**：cockpit 模板的 AUTO 标记与 Phase 1 脚本生成的标记字符串一致。

- [ ] **0.4 exit-ritual.md — landing 决策树**
  - 删分类 `(e) 外部反馈 → debriefs/`；删 hanging-task 的"debrief disposition 未完成"阻塞门。
  - 状态映射进 landing：suggest 下一状态用新 4 态流。
  - `## Cockpit update`：`## 进行中` 为 AUTO 派生（不手写）；`## 下一步` 由 landing 全自动写（spec §2.2 协议：启动 idea / 推进 active 续作；触发 = landing + idea→active + 里程碑）。
  - `Active focus`（会话主线，粗）vs `## 下一步`（具体单步动作）定义（spec §2.2 评审 F）。
  - Land Routine：状态由 6→4；其余移文件/改边逻辑不变。
  - **验证**：exit-ritual 内无残留 debrief/disposition 门、无旧状态值。

- [ ] **0.5 Commit**
```
git add skills/preflight/protocol.md skills/preflight/folder-semantics.md skills/preflight/templates.md skills/preflight/exit-ritual.md
git commit -m "docs(flightdeck): model-v4 Phase 0 — 数据模型真相源（状态 6→4、folder 7→5、删 debriefs）"
```

---

## Phase 1 — flightdeck_index.py 扩展 + 测试

**Files:**
- Modify: `scripts/flightdeck_index.py`
- Test: `tests/test_flightdeck_index.py`（若不存在则 Create；先确认现有测试路径）

- [ ] **1.1 先跑现有测试，确认基线**
  - Run: `uv run -m pytest tests/ -q`（或仓库现有测试命令）。Expected: 全绿（改之前的基线）。

- [ ] **1.2 写失败测试：状态集 + folder 集**
  - 在测试文件加：`STATUS_ORDER == ["idea","active","done","scrapped"]`；`SUMMARY_KINDS == {"specs","plans"}`；`FOLDER_ORDER == ["specs","plans","incidents","checklists","charts"]`；`"debriefs" not in FOLDER_ORDER`。
  - Run: 失败（仍是旧常量）。

- [ ] **1.3 改常量 + 删 debriefs 分支**
  - `STATUS_ORDER = ["idea", "active", "done", "scrapped"]`
  - `SUMMARY_KINDS = {"specs", "plans"}`（删 sketches）
  - `KNOWLEDGE_KINDS = {"checklists", "incidents"}`（不变）
  - `FOLDER_ORDER = ["specs", "plans", "incidents", "checklists", "charts"]`（删 debriefs、sketches）
  - `format_row`：删除 `if kind == "debriefs":` 整个分支。
  - Run 1.2 测试：通过。

- [ ] **1.4 写失败测试：specs INDEX 按状态分组 + 跳过 scrapped**
  - 构造临时 specs/ 含 idea/active/done/scrapped 各一，断言 `regen_folder_index` 输出：分两组（待启动 idea / 进行中·完成 active·done），scrapped 行不出现，组内 active·done 按日期降序、idea 按字母序。
  - Run: 失败。

- [ ] **1.5 实现 specs 分组**
  - 在 `regen_folder_index`：当 `kind == "specs"` 时，先按 status 分桶；`scrapped` 跳过；产出带 `### 待启动（idea）` / `### 进行中·完成` 两个子标题的 AUTO 体（标题在 AUTO 区内，便于脚本重生）。其余 folder 维持单列。
  - 排序：active·done `sorted(..., reverse=True)`（文件名日期降序）；idea `sorted()` 字母序。
  - Run 1.4：通过。

- [ ] **1.6 写失败测试：cockpit `## 进行中` AUTO 区生成**
  - 断言新函数 `regen_cockpit_inprogress(deck)` 从 `specs/` + `plans/` 中 `status == "active"` 的文件派生 `<!-- AUTO:inprogress -->\n- [file](specs/file) — summary[ — [note: …]]\n<!-- /AUTO -->`；无 active 时体为空。`note` 字段存在时在行尾加 `— [note: …]`。
  - Run: 失败（函数不存在）。

- [ ] **1.7 实现 regen_cockpit_inprogress + 接进 main**
  - 新函数 `regen_cockpit_inprogress(deck)`：遍历 specs+plans，取 active，行格式复用 INDEX 行（spec §7.1），链接含 folder 前缀（`specs/`、`plans/`），有 `note` 则追加 `{DASH} [note: {note}]`。
  - `main`：cockpit.md 作为额外 target——`_index_targets` 增产出 `("cockpit", deck/"cockpit.md", regen_cockpit_inprogress(deck))`（cockpit 用 `<!-- AUTO:inprogress -->` 标记，`replace_auto_block` 复用）。
  - Run 1.6：通过。

- [ ] **1.8 全测试 + 自检**
  - Run: `uv run -m pytest tests/ -q`。Expected: 全绿。
  - Run: `uv run scripts/flightdeck_index.py flightdeck --check`（此时 deck 尚未迁移，预期 DRIFT 或 version guard——记录，Phase 4 迁移后才应 clean）。

- [ ] **1.9 Commit**
```
git add scripts/flightdeck_index.py tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): model-v4 Phase 1 — index 脚本 4 态/5 folder、specs 分组、cockpit 进行中区生成"
```

---

## Phase 2 — 四个 skill 行为对齐

**Files:**
- Modify: `skills/status/SKILL.md`
- Modify: `skills/landing/SKILL.md`
- Modify: `skills/preflight/SKILL.md`
- Modify: `skills/walkaround/SKILL.md`

- [ ] **2.1 status**：合法状态 4 态；翻 `idea→active` 时（a）补 `YYYY-MM-DD-` 前缀、（b）调 index 脚本（或手动 fallback）重生 cockpit `## 进行中`；支持写/读 `note:`；翻 done/scrapped → Land Routine。**验证**：dogfood 一次 idea→active，确认 cockpit 进行中区出现该项。
- [ ] **2.2 landing**：删 debrief 分类(e)+disposition 门（引 Phase 0.4）；状态映射 4 态；全自动写 `## 进行中`（调脚本）+ `## 下一步`（按 §2.2 协议）；regen 改动文件夹 INDEX。**验证**：dogfood landing 一次，确认 `## 进行中`/`## 下一步` 自动更新、无 debrief 提示。
- [ ] **2.3 preflight**：读新 cockpit 结构（进行中/下一步）；step 2 迁移检测能识别未迁移 deck（旧 folder/状态）并提议 §4.1 迁移；fallback「待启动池」= `specs/` 中 idea；删 debriefs 路由/catalog。**验证**：在未迁移 deck 上跑 preflight，确认提议迁移；迁移后跑，确认读新结构无误。
- [ ] **2.4 walkaround**：删 debriefs 审计；状态合法值改 4 态；新增 cockpit `## 进行中` AUTO 区一致性检查（与脚本输出比对）；识别 `note:`；idea 文件不报"孤儿"。**验证**：迁移后 deck 跑 walkaround，0 假阳性。
- [ ] **2.5 Commit**
```
git add skills/status/SKILL.md skills/landing/SKILL.md skills/preflight/SKILL.md skills/walkaround/SKILL.md
git commit -m "feat(flightdeck): model-v4 Phase 2 — status/landing/preflight/walkaround 对齐 4 态 + cockpit 自动驱动"
```

---

## Phase 3 — scaffolds + emit-agents-md + MIGRATION

**Files:**
- Delete: `scaffolds/full/flightdeck/sketches/INDEX.md`、`scaffolds/full/flightdeck/debriefs/INDEX.md`（及空文件夹）
- Modify: `scaffolds/full/flightdeck/cockpit.md`、`scaffolds/full/flightdeck/INDEX.md`
- Modify: `skills/emit-agents-md/SKILL.md`
- Modify: `MIGRATION.md`

- [ ] **3.1 scaffold**：删 `sketches/` `debriefs/` 文件夹；cockpit.md 模板改新结构（`## 进行中` 含空 AUTO 区 + `## 下一步`）；root `INDEX.md` 去 debriefs/sketches 行（5 folder）。**验证**：`git rm -r` 两文件夹；新建一个临时 deck 跑 `flightdeck_index.py <tmpdeck> --check` 应 clean。
- [ ] **3.2 emit-agents-md**：cockpit 结构变更后，emit 从 `## 进行中`/`## 下一步` 取内容（原从 Next session）。**验证**：在迁移后的本仓库 deck 跑 emit，AGENTS.md 内容合理。
- [ ] **3.3 MIGRATION.md**：在 3.0 段补 model-v4 迁移步骤（spec §4.1）：sketches→specs(idea)、debriefs 删除+disposition 并入 spec、状态重映射(pending→idea / awaiting-review·blocked→active)、cockpit 插入 `## 进行中` 并首次 regen。`current` 保持 `3.0`，确认 `3.0 ∈ layout_need_update`。**验证**：preflight 在旧 deck 上能据此提议迁移（联动 2.3）。
- [ ] **3.4 Commit**
```
git add scaffolds/ skills/emit-agents-md/SKILL.md MIGRATION.md
git commit -m "feat(flightdeck): model-v4 Phase 3 — scaffold/emit/MIGRATION 跟进新模型"
```

---

## Phase 4 — 迁移本仓库 deck（dogfood）

**Files:** `flightdeck/` 本仓库 deck（spec §4.2）

- [ ] **4.1 sketch → spec(idea)**：`git mv flightdeck/sketches/v1x-deferred-ideas.md flightdeck/specs/v1x-deferred-ideas.md`；frontmatter `status: active → idea`（无日期前缀，保留）。
- [ ] **4.2 状态重映射**：本仓库现有 specs/plans 中 `pending → idea`（structural-edit-guard / preflight-silent-bump-nudge / status-spec-co-advance 已是 idea 候选）；`active` 保持（incident-recurrence-autocount / scriptable-mechanical-layer / model-v4 spec / 本 plan）。
- [ ] **4.3 删空文件夹**：`flightdeck/sketches/`（v1x 移走后空，含 INDEX）、`flightdeck/debriefs/`（本会话已空，含 INDEX）→ `git rm -r`。`landed/debriefs/` 历史保留。
- [ ] **4.4 cockpit 重构**：改成新结构（Active focus / `## 进行中` AUTO / `## 下一步` / Hanging tasks）；把现 Next session 的 active 工作落进 `## 进行中`（脚本生成）、其余下一步动作落 `## 下一步`。
- [ ] **4.5 regen + 校验**：`uv run scripts/flightdeck_index.py flightdeck`；再 `--check` 应 **clean**。
- [ ] **4.6 Commit**
```
git add flightdeck/
git commit -m "chore(flightdeck): model-v4 Phase 4 — 迁移本仓库 deck 到新模型"
```

---

## Phase 5 — 验证 + 收尾

- [ ] **5.1 全量 walkaround**：跑 `/flightdeck:walkaround`，预期 0 CRITICAL、0 假阳性（重点：idea 不报孤儿、cockpit AUTO 一致、无 debrief 残留）。
- [ ] **5.2 dogfood reload 行为验证**：走一遍 preflight（读新 cockpit）→ status（idea→active 带动 cockpit）→ landing（自动写进行中/下一步）。逐项确认 spec §2 机制成立。
- [ ] **5.3 复核 status-spec-co-advance**（spec §6）：确认 model-v4 是否已吸收"plan 推进不带动 spec"痛点。若已消解 → `status: scrapped` + 在 model-v4 spec §6 标注；否则保留为 idea。
- [ ] **5.4 更新 cockpit + 准备 3.0 发布**：cockpit `## 下一步` 指向 version-bump（`checklists/version-bump.md`）。本 plan 翻 `done`，随后 Land Routine 归档。
- [ ] **5.5 Commit**
```
git add flightdeck/
git commit -m "chore(flightdeck): model-v4 Phase 5 — 验证收尾、co-advance 复核、备发 3.0"
```

---

## 自审（spec 覆盖核对）

- spec §1 数据模型 → Phase 0.1/0.2 + Phase 1.3/1.5 ✓
- spec §1.2 note 字段 → Phase 0.1 + 1.6/1.7（cockpit 标注）+ 2.1/2.4 ✓
- spec §1.4 scrapped 归宿 + INDEX 分组 → Phase 1.4/1.5 ✓
- spec §2 cockpit 自动驱动 → Phase 1.6/1.7 + 2.1/2.2 + 0.4 ✓
- spec §3 删 debriefs → Phase 0（各文档）+ 1.3 + 2.2/2.3/2.4 + 3.1 + 4.3 ✓
- spec §4 迁移 → Phase 3.3（通用）+ Phase 4（本仓库）✓
- spec §5 影响盘点 → Phase 0/1/2/3 逐文件覆盖 ✓
- spec §6 co-advance 复核 → Phase 5.3 ✓
- spec §7 开放问题：Q1 行格式 → 1.7 复用 INDEX 行；Q2/Q3 DEFER 不实施（记录在 spec）✓
