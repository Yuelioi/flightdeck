---
status: done
implements: landed/specs/2026-06-01-layout-version-migration-detection-design.md
---

# Layout 版本号驱动迁移检测 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 cockpit 头里一行 `**Layout**: 1.2` 取代「到处数 1.x 旧文件名」的存在性检测——健康 deck 静默放行，旧/缺号 deck 仍先问后迁。

**Architecture:** 纯 markdown 改动（flightdeck 无代码，skill = AI 跟随的检查单）。在 cockpit 模板 + 两个 scaffold + 本项目 cockpit 各加一行版本戳；把 `preflight` 第 1 步与 `walkaround` Audit 10 改成「读版本号 → 三岔」，缺号回退到那份**冻结的** 6 项旧标记清单。`never-migrate-silently` 全程保留。

**Tech Stack:** Markdown；验证靠 Grep 断言 + 通读 skill 流程（本项目无自动化测试，行为验证对照 `TEST_PLAN.md` 风格）。

**Conventions for this plan:**
- 「当前 layout 版本」常量 = **`1.2`**，在 preflight / walkaround 两处措辞一律写 "The current layout version is **1.2**."
- 版本戳行紧跟 `**Active focus**` 之后：`**Layout**: 1.2`。
- 提交只在本计划要求时；当前在 `main`，**第一步先开分支**（Task 0）。

---

### Task 0: 开工作分支

**Files:** （无文件改动）

- [ ] **Step 1: 从 main 建分支**

Run:
```bash
git switch -c feat/layout-version-detection
```
Expected: `Switched to a new branch 'feat/layout-version-detection'`

- [ ] **Step 2: 确认起点干净**

Run: `git status --short`
Expected: 仅显示上一轮已落的 spec + INDEX 改动（若已提交则为空）。若 spec/INDEX 尚未提交，先提交它们：
```bash
git add flightdeck/specs/2026-06-01-layout-version-migration-detection-design.md flightdeck/specs/INDEX.md flightdeck/INDEX.md flightdeck/cockpit.md
git commit -m "docs(spec): layout-version-driven migration detection design"
```

---

### Task 1: cockpit 模板加版本戳 (`templates.md`)

**Files:**
- Modify: `skills/workflow/templates.md` (§ cockpit.md 模板, 约 262-263 行 + ### Rules 块)

- [ ] **Step 1: 模板加 `**Layout**` 行**

把模板块里：
```markdown
**Last updated**: YYYY-MM-DD by <who> (<one-line state summary>)
**Active focus**: <current main thread, 5–15 words>
```
改为：
```markdown
**Last updated**: YYYY-MM-DD by <who> (<one-line state summary>)
**Active focus**: <current main thread, 5–15 words>
**Layout**: 1.2
```

- [ ] **Step 2: ### Rules 加一条说明**

在 `### Rules` 列表里 `- **No metric tracking duplicated elsewhere** ...` 之后追加：
```markdown
- **`Layout` = the flightdeck layout version this deck conforms to.** Entry skills (`preflight`, `walkaround`) compare it against the current version to decide migration. New decks start at the current version; bump it only when migrating to a new layout (see [MIGRATION.md](../../MIGRATION.md)).
```

- [ ] **Step 3: 验证**

Run: `rg -n "Layout" skills/workflow/templates.md`
Expected: 至少两处命中——模板里的 `**Layout**: 1.2` 与 Rules 里的说明行。

- [ ] **Step 4: Commit**

```bash
git add skills/workflow/templates.md
git commit -m "feat(templates): add Layout version stamp to cockpit template"
```

---

### Task 2: 两个 scaffold cockpit 加版本戳

**Files:**
- Modify: `scaffolds/full/flightdeck/cockpit.md:4`
- Modify: `scaffolds/minimal/flightdeck/cockpit.md:4`

- [ ] **Step 1: full scaffold**

把（两文件当前头部相同）：
```markdown
**Last updated**: YYYY-MM-DD by [who] (one-line state)
**Active focus**: [current main thread]
```
改为：
```markdown
**Last updated**: YYYY-MM-DD by [who] (one-line state)
**Active focus**: [current main thread]
**Layout**: 1.2
```
对 `scaffolds/full/flightdeck/cockpit.md` 执行此改动。

- [ ] **Step 2: minimal scaffold**

对 `scaffolds/minimal/flightdeck/cockpit.md` 执行与 Step 1 完全相同的改动。

- [ ] **Step 3: 验证两处都带戳**

Run: `rg -n "Layout" scaffolds/full/flightdeck/cockpit.md scaffolds/minimal/flightdeck/cockpit.md`
Expected: 两个文件各一行 `**Layout**: 1.2`。

- [ ] **Step 4: Commit**

```bash
git add scaffolds/full/flightdeck/cockpit.md scaffolds/minimal/flightdeck/cockpit.md
git commit -m "feat(scaffolds): stamp new decks with Layout 1.2"
```

---

### Task 3: 本项目 cockpit 加版本戳 (dogfood)

**Files:**
- Modify: `flightdeck/cockpit.md:4`

- [ ] **Step 1: Active focus 行后插入版本戳**

在 `**Active focus**: flightdeck 1.2 — ...` 行之后、空行之前插入：
```markdown
**Layout**: 1.2
```

- [ ] **Step 2: 验证**

Run: `rg -n "Layout" flightdeck/cockpit.md`
Expected: 一行 `**Layout**: 1.2`。

- [ ] **Step 3: Commit**

```bash
git add flightdeck/cockpit.md
git commit -m "chore(dogfood): stamp own cockpit with Layout 1.2"
```

---

### Task 4: 重写 preflight 第 1 步为三岔

**Files:**
- Modify: `skills/preflight/SKILL.md:19-27`

- [ ] **Step 1: 替换整个步骤 1**

把现有的步骤 1（"**Detect 1.x layout (non-silent).**" 那段，含 6 项清单与其后的 "Tell the user..." 段落）整体替换为：

```markdown
1. **Check layout version (non-silent on mismatch).** Read the `**Layout**: <ver>` line in `flightdeck/cockpit.md`'s header. The current layout version is **1.2**.

   - **`Layout` == 1.2** → up to date; continue silently (report nothing for this step).
   - **`Layout` present but older (e.g. `1.1`)** → tell the user: "Layout `<ver>` detected — migrate to 1.2?" and follow [MIGRATION.md](../../MIGRATION.md). Do not proceed with the rest of the checklist until the user decides.
   - **No `Layout` line** (decks created before the stamp existed) → fall back to the legacy-marker presence check. If ANY of these exist:
     - `flightdeck/manifest.md` · `flightdeck/logbook.md` · `flightdeck/kneeboard/` · `flightdeck/flight-plans/` · `flightdeck/incident-reports/` · `flightdeck/safety-reviews/`

     → it is a 1.x deck: tell the user "1.x layout detected — migrate to 1.2?" and follow [MIGRATION.md](../../MIGRATION.md); do not proceed until they decide. If NONE exist → it is a pre-stamp 1.2 deck: offer to add `**Layout**: 1.2` to the cockpit header (ask first), then continue.

   Never migrate (or stamp) silently — always ask the user first.
```

- [ ] **Step 2: 验证三岔齐备 + 冻结清单仍在**

Run: `rg -n "Layout == 1.2|present but older|No .Layout. line|manifest.md|Never migrate \(or stamp\) silently" skills/preflight/SKILL.md`
Expected: 命中全部三岔标签、6 项清单中的 `manifest.md`、以及 never-silent 行。

- [ ] **Step 3: 通读确认行为**

Read `skills/preflight/SKILL.md` 步骤 1 整段。确认：健康 deck（Layout==1.2）此步**零输出**；缺号且无旧标记会 offer 补戳而**不静默跳过**；旧版/旧标记都走「先问后迁」。

- [ ] **Step 4: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "feat(preflight): version-driven layout check (silent when current, fallback when unstamped)"
```

---

### Task 5: walkaround Audit 10 改为版本感知

**Files:**
- Modify: `skills/walkaround/SKILL.md:122-133`

- [ ] **Step 1: 替换 Audit 10 整段**

把 `### 10. Legacy 1.x paths (WARNING)` 标题及其下到 "Only report once per path..." 行之前的全部内容，替换为：

```markdown
### 10. Layout version (WARNING / INFO)

Read the `**Layout**: <ver>` line in `flightdeck/cockpit.md`'s header. The current layout version is **1.2**.

- **`Layout` older than 1.2** (e.g. `1.1`) → **WARNING** — deck is on an old layout; point to [MIGRATION.md](../../MIGRATION.md).
- **No `Layout` line** → fall back to the legacy-marker presence check. If ANY of `flightdeck/manifest.md` · `flightdeck/logbook.md` · `flightdeck/kneeboard/` · `flightdeck/flight-plans/` · `flightdeck/incident-reports/` · `flightdeck/safety-reviews/` exist → **WARNING** — legacy 1.x deck; point to [MIGRATION.md](../../MIGRATION.md). If NONE exist → **INFO** — no `Layout` stamp; suggest adding `**Layout**: 1.2` to the cockpit header.
- **`Layout` == 1.2** → pass; report nothing.
```

保留其后的 "Only report once per path — do not also flag these as stray/orphan in Audit 8." 行不动。

- [ ] **Step 2: 更新顶部 description 措辞**

`skills/walkaround/SKILL.md` 第 3 行 frontmatter `description` 末尾 "...and legacy 1.x paths." 改为 "...and layout-version / legacy 1.x paths."（保持一句话描述与新 Audit 一致）。

- [ ] **Step 3: 验证**

Run: `rg -n "Layout version|older than 1.2|No .Layout. line|report once per path" skills/walkaround/SKILL.md`
Expected: 命中新标题、两条版本分支、以及保留的 "report once per path" 行。

- [ ] **Step 4: Commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "feat(walkaround): make Audit 10 layout-version aware (WARNING/INFO)"
```

---

### Task 6: CHANGELOG + INDEX 收尾

**Files:**
- Modify: `CHANGELOG.md` (顶部 Unreleased / 下一版本段)
- Modify: `flightdeck/plans/INDEX.md`
- Modify: `flightdeck/INDEX.md`

- [ ] **Step 1: CHANGELOG 记一条**

Read `CHANGELOG.md` 顶部。在最上方的「未发布 / 下一个 patch」段落（若无则新建 `## [Unreleased]`）加入：
```markdown
- **Layout version stamp** — cockpit headers carry `**Layout**: <ver>`; `preflight` and `walkaround` compare it against the current layout version instead of always scanning for legacy 1.x filenames. Healthy decks pass silently; unstamped decks fall back to the (now-frozen) legacy-marker check. Never migrates silently.
```

- [ ] **Step 2: 把本 plan 加进 plans/INDEX.md**

在 `flightdeck/plans/INDEX.md` 的 `<!-- AUTO:plans -->` 区追加：
```markdown
- [2026-06-01-layout-version-migration-detection-plan.md](2026-06-01-layout-version-migration-detection-plan.md) — active — Layout 版本号驱动迁移检测的实现计划
```

- [ ] **Step 3: 根 INDEX plans 计数 +1**

`flightdeck/INDEX.md` 把 `- plans/ — 1 active` 改为 `- plans/ — 2 active`。

- [ ] **Step 4: 验证 INDEX 一致**

Run: `rg -n "plans/ — 2 active|layout-version-migration-detection-plan" flightdeck/INDEX.md flightdeck/plans/INDEX.md`
Expected: 根 INDEX 显示 `plans/ — 2 active`；plans/INDEX 含本 plan 行。

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md flightdeck/plans/INDEX.md flightdeck/INDEX.md flightdeck/plans/2026-06-01-layout-version-migration-detection-plan.md
git commit -m "docs(changelog): record layout version stamp + index the plan"
```

---

### Task 7: 全量行为复核

**Files:** （无改动，纯复核）

- [ ] **Step 1: 确认旧的「无条件 6 项检查」已不在 preflight 顶层**

Run: `rg -n "Detect 1.x layout" skills/preflight/SKILL.md`
Expected: **无命中**（旧标题已被「Check layout version」取代）。

- [ ] **Step 2: 确认冻结清单只剩两处内联副本（preflight 兜底 + walkaround 兜底）**

Run: `rg -l "incident-reports/" skills/`
Expected: 仅 `skills/preflight/SKILL.md` 与 `skills/walkaround/SKILL.md`（均为缺号兜底，符合设计 §3 冻结-内联）。

- [ ] **Step 3: 三场景口头走查（对照 spec §2.2 / §2.3）**

通读 preflight 步骤 1 与 walkaround Audit 10，逐一确认：
  1. **健康 deck**（cockpit 有 `**Layout**: 1.2`）→ preflight 此步零输出、walkaround 通过。
  2. **1.1 deck**（`**Layout**: 1.1`）→ 两者都判旧版、指向 MIGRATION.md、preflight 先问后迁。
  3. **缺号 deck**：有旧标记 → 判 1.x（WARNING / 先问后迁）；无旧标记 → preflight offer 补戳、walkaround 给 INFO。

- [ ] **Step 4: （可选）跑一次 walkaround 自测**

如本会话条件允许，对本仓库 `flightdeck/`（现已带 `**Layout**: 1.2`）心算 Audit 10：应判定 `== 1.2 → pass`，不产生 legacy 警告。记录结果。

---

## 备注：未采纳的「更瘦」选项

设计 §3 的备选——把 6 项旧标记清单抽到 `MIGRATION.md` 单一来源、preflight/walkaround 仅引用——本计划**未采纳**（清单已冻结，内联副本不会腐化；抽取会让 AI 每次多读一遍 MIGRATION.md）。若日后仍想更瘦，再起独立小 plan。
