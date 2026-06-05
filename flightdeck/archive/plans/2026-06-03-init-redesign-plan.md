---
status: done
summary: 分 P0–P4 实施 init 重做：删 minimal scaffold、install/preflight 统一 copy-the-scaffold、git 检测+AGENTS opt-in、可跳过演示式 onboarding 教程（带 safe-to-delete 标记+幂等 cleanup）、walkaround 容忍空 INDEX；末尾单 commit
last_updated: 2026-06-03
implements: landed/specs/2026-06-03-init-redesign-single-scaffold-design.md
---

# init 重做 + 单一 scaffold 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans 或 subagent-driven-development，逐任务实施。步骤用 `- [ ]`。

**Goal:** 把 flightdeck 初始化统一为「copy 单一 `scaffolds/full/` + 交互」，删掉 minimal 变体，加 git 检测 / AGENTS.md opt-in / 可跳过的演示式上手教程。

**Architecture:** 编辑 markdown skill 指令；scaffold 按 `<skill-base>/../../scaffolds/full/` 解析（插件已含 scaffolds，已核实）。"测试" = reload 插件后在**干净目录** dogfood 首次建档全程。

**Tech Stack:** flightdeck 技能（`skills/preflight/*`、`skills/walkaround/SKILL.md`）、`scaffolds/`、`install.sh`/`install.ps1`、README。

**提交策略:** 全程不分提交，P0–P4 完成 + dogfood 通过后**单 commit**（独立于 3.0 工作流）。各 Phase 末 dogfood 为 review 检查点。

**依赖:** 建立在 3.0 之上（scaffold rules.md 已是 3.0 英文）。本计划**取代** 3.0 里 preflight 内联现写 rules.md 的首次建档段。

---

## Phase 0 — 删 minimal + 安装器收敛（低风险）

### Task 0.1：删除 `scaffolds/minimal/`

**Files:** Delete `scaffolds/minimal/`（整树）

- [ ] `git rm -r scaffolds/minimal`。
- [ ] **Verify:** `ls scaffolds/` → 只剩 `full/`。

### Task 0.2：`install.sh` / `install.ps1` —— `--scaffold` warn+ignore，总是 full

**Files:** Modify `install.sh`、`install.ps1`

- [ ] 读两个安装脚本，定位 `--scaffold` / `-Scaffold` 解析与 minimal 分支。
- [ ] 改为：保留旗标解析但**忽略其值**，若传入打印一行 `warning: --scaffold is deprecated (3.x) and ignored; the full layout is always installed; the flag is removed in 4.0`，然后**总是 copy `scaffolds/full/`**。删 minimal 复制分支。
- [ ] **Verify:** `bash install.sh --scaffold=minimal --help` 之类不报错；脚本里不再 cp minimal。`grep -n "minimal" install.sh install.ps1` → 仅在 warn 文案/注释。

### Task 0.3：README 更新

**Files:** Modify `README.md`、`README.zh.md`

- [ ] 删 `--scaffold=minimal|full` 双选项说明，改为"安装器总是铺全布局；`--scaffold` 旗标 3.x 弃用（warn+ignore）、4.0 删"。
- [ ] init 段（"With no flightdeck/cockpit.md yet, /flightdeck:preflight asks to create one..."）更新为新流程：git 检测 → copy 全布局 → 两问 interview → AGENTS.md 询问 → 可跳过教程。
- [ ] **Verify:** `grep -n "scaffold=minimal" README.md README.zh.md` → 无（除弃用说明）。

---

## Phase 1 — scaffold cockpit 占位符（让 interview 能替换）

### Task 1.1：`scaffolds/full/flightdeck/cockpit.md` 加明确占位符

**Files:** Modify `scaffolds/full/flightdeck/cockpit.md`

- [ ] 确保 cockpit 含可被首次建档替换的占位符，正文形如：

  ```markdown
  # Cockpit — <project name>

  **Last updated**: <YYYY-MM-DD> by <user>
  **Active focus**: <ACTIVE_FOCUS — filled by preflight first-time-setup>

  ## Next session

  1. <FIRST_NEXT_ITEM — filled by preflight first-time-setup>

  ## Hanging tasks

  - (none)
  ```

- [ ] **Verify:** `grep -n "ACTIVE_FOCUS\|FIRST_NEXT_ITEM" scaffolds/full/flightdeck/cockpit.md` → 命中两处。

---

## Phase 2 — 重写 preflight 首次建档为 copy-the-scaffold

### Task 2.1：替换 preflight SKILL.md 的 First-time setup（Branch-0 分支）

**Files:** Modify `skills/preflight/SKILL.md`（Branch-0 First-time-setup 段，约现 step 0 的 "does NOT exist → First-time setup" 子步骤）

- [ ] 把"内联现写三文件 + Do NOT pre-create other folders"整段替换为 copy-the-scaffold 流程：

  ```markdown
  - **`flightdeck/cockpit.md` does NOT exist** → run **First-time setup**:
    1. **git check** — does deck root contain `.git`? If **no**: tell the user "no git here — flightdeck works, but staleness/history fall back to `landed/HISTORY.md`", and **offer to run `git init`? (y/N)**. If yes, run it. (Non-blocking either way.)
    2. Ask: **"Create a flightdeck deck here? (full layout + 3-file contract)"** — wait for confirmation.
    3. **Copy the scaffold verbatim** from `<this skill's base dir>/../../scaffolds/full/flightdeck/` into `./flightdeck/` — every folder + `INDEX.md` + the commented `rules.md` + `cockpit.md` + `landed/HISTORY.md`. **Copy, do not re-author** (this preserves the rules.md comments). Substitute today's date and the user into `cockpit.md`; `rules.md` `version` is already `<current>` in the scaffold — confirm it matches `MIGRATION.md` `current`, bump if the scaffold is behind.
    4. **Interview (2 Q)** → replace the cockpit placeholders: "Active focus — current main thread (5–15 words)?" → `<ACTIVE_FOCUS>`; "First 'next session' item — one concrete action?" → `<FIRST_NEXT_ITEM>`.
    5. **AGENTS.md** — ask "Generate AGENTS.md (cross-tool bridge from cockpit)? (Y/n)". If yes, run `/flightdeck:emit-agents-md`. (Opt-in; matches the 3.0 emit-on-presence rule — creating it now is the bootstrap.)
    6. **Tutorial** — ask "Run a 2-minute guided tour? It creates a throwaway sample and cleans it up. (y/N)". If yes, run [onboarding.md](onboarding.md); if no, skip.
    7. **Then STOP** — the next `/preflight` takes the read path below.
  ```

- [ ] 删掉旧的内联 `rules.md` fenced block（3.0 过渡版）与 "Do NOT pre-create other folders" 那句。
- [ ] **Verify:** `grep -n "Copy the scaffold verbatim\|Generate AGENTS.md\|guided tour" skills/preflight/SKILL.md` → 三处命中；`grep -n "Do NOT pre-create other folders" skills/preflight/SKILL.md` → 无。

### Task 2.2：`folder-semantics.md` 简化 minimal-vs-full

**Files:** Modify `skills/preflight/folder-semantics.md`

- [ ] 把"minimal vs full setup"一节改为："单一 `scaffolds/full/` 全布局；3-file 契约（`rules.md`+`cockpit.md`+`landed/HISTORY.md`）是**校验地板**（缺则 walkaround CRITICAL），不再是 scaffold 变体。全布局下**缺文件夹**才是异常，空文件夹/空 INDEX 正常。"
- [ ] **Verify:** `grep -n "minimal vs full\|minimal-vs-full" skills/preflight/folder-semantics.md` → 无（或仅历史说明）。

---

## Phase 3 — onboarding 教程

### Task 3.1：新增 `skills/preflight/onboarding.md`

**Files:** Create `skills/preflight/onboarding.md`

- [ ] 写演示式教程（AI 做 + 旁白，用户敲 "next" 推进；样例带 safe-to-delete 标记；cleanup 幂等）：

  ```markdown
  # Flightdeck onboarding — 2-minute guided tour

  A **demonstration** run: the AI creates a throwaway sample artifact, walks it through the
  full lifecycle narrating each step, then deletes it. The user just reads + says "next".
  Skippable; invoked only from `preflight` first-time setup. **Idempotent**: safe to re-run;
  detects and cleans any leftover sample first.

  ## Step 0 — clean any leftover sample
  If `specs/hello-flightdeck.md` OR `landed/specs/hello-flightdeck.md` exists (a prior
  interrupted tour), remove them + their INDEX rows first, then continue.

  ## Step 1 — create the sample (status: create→pending)
  Write `specs/hello-flightdeck.md`:
  ```​markdown
  ---
  status: pending
  summary: throwaway onboarding sample — safe to delete
  last_updated: <today>
  ---
  <!-- tutorial sample — safe to delete -->
  # Hello, flightdeck
  This file is a guided-tour sample. The tour will move it through the lifecycle and delete it.
  ```​
  Regenerate `specs/INDEX.md` + root count. **Narrate:** "Created a spec → `status` set it `pending`; a row appeared in `specs/INDEX.md`." → wait for "next".

  ## Step 2 — start (pending→active)
  Flip frontmatter `status: active`, bump `last_updated`, re-sync `specs/INDEX.md`.
  **Narrate:** "Beginning execution → `status` flips it `active` (default-on `start`)." → "next".

  ## Step 3 — finish (active→awaiting-review)
  Edit the body (add one line), flip `status: awaiting-review`, re-sync INDEX.
  **Narrate:** "Work done → `awaiting-review`, the signal it's ready to land." → "next".

  ## Step 4 — approve + land (awaiting-review→done→archived)
  Flip `status: done`; then run the shared **Land Routine** (exit-ritual.md#land-routine):
  move `specs/hello-flightdeck.md` → `landed/specs/`, remove its `specs/INDEX.md` row, recompute root.
  **Narrate:** "Approved → `done`, then **landed**: the file moved to `landed/specs/`, out of the
  active tree but kept as history." → "next".

  ## Step 5 — cleanup (restore a pristine deck)
  Delete `landed/specs/hello-flightdeck.md`; ensure no `hello-flightdeck` row remains in any INDEX;
  recompute root counts. **Narrate:** "Tour done — sample removed; your deck is the empty full
  layout, ready for real work. Run `/flightdeck:preflight` next session to resume."

  ## Don't do
  - Don't touch the user's real artifacts. The only file this tour creates/edits/deletes is
    `hello-flightdeck.md` (+ its landed copy + INDEX rows).
  - Don't commit. Don't bump cockpit `Last updated`.
  ```

  （注：上面 fenced 内的 `​` 零宽字符仅为在本 plan 里转义嵌套围栏；实写 onboarding.md 时用普通 ``` 。）

- [ ] **Verify:** `grep -n "tutorial sample — safe to delete\|guided tour\|Idempotent" skills/preflight/onboarding.md` → 命中。

### Task 3.2：preflight 引用 onboarding（已在 Task 2.1 step 6 接入）

- [ ] 确认 Task 2.1 的 "Tutorial" 步骤链接 `[onboarding.md](onboarding.md)` 正确（同目录）。
- [ ] 在 preflight SKILL.md 底部 "Protocol knowledge / 索引" 列表加一行：`- [onboarding.md](onboarding.md) — optional first-run guided tour (demonstration; auto-cleaned)`。
- [ ] **Verify:** `grep -n "onboarding.md" skills/preflight/SKILL.md` → ≥2 处（接入 + 索引）。

---

## Phase 4 — walkaround 容忍空 INDEX + dogfood

### Task 4.1：walkaround 不把空 INDEX / 空文件夹报成异常

**Files:** Modify `skills/walkaround/SKILL.md`

- [ ] 找到 orphan/stray/empty 相关 audit，明确："全布局下文件夹+空 `INDEX.md` 是正常初始态；**空但存在**的文件夹/INDEX 不报。仅**缺**已知文件夹时报（缺文件夹才是异常）。"
- [ ] **Verify:** `grep -n "empty INDEX\|空" skills/walkaround/SKILL.md`（确认有容忍说明）。

### Task 4.2：dogfood（reload 后）

- [ ] reload/重装插件到含本改动的版本。
- [ ] 在**干净空目录**跑 `/flightdeck:preflight`：验证 git 检测提醒（无 .git 时 offer git init）、copy 全布局（7 文件夹 + INDEX + **带注释**的 rules.md）、interview 替换占位符、AGENTS.md 询问、教程 offer。
- [ ] 跑教程：验证样例创建→pending→active→awaiting-review→done→land→cleanup，结束 deck 为空全布局、无 `hello-flightdeck` 残留。
- [ ] 中断教程再重跑：验证 Step 0 幂等清理。
- [ ] 跑 `/flightdeck:walkaround`：空 INDEX 不报异常。

---

## Self-Review（覆盖核对）

- spec §1 删 minimal / 单一 full / 校验地板 → Task 0.1 / 2.2 ✓
- spec §2 copy-the-scaffold + git 检测 + interview + AGENTS + 教程 offer → Task 2.1 ✓
- spec §3 onboarding 演示式 + 样例 spec + cleanup → Task 3.1 ✓
- spec §4 `--scaffold` 3.x warn+ignore → Task 0.2 ✓
- spec §5 影响文件（含 README）→ Task 0.3 / 2.x / 3.x / 4.1 ✓
- spec §6 copy 源相对 base / 空 INDEX 容忍 / 中断残留幂等清理 / 取代 3.0 inline → Task 2.1 / 3.1 / 4.1 ✓
- 占位符替换机制（spec 未显式，review 补）→ Task 1.1 ✓
