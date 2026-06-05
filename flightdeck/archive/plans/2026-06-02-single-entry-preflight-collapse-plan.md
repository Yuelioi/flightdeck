---
status: done
implements: landed/specs/2026-06-02-single-entry-preflight-collapse-design.md
---

# 单入口塌缩（preflight 取代 workflow）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 删除自动加载的 `workflow` skill 与整个 SessionStart hook，把协议知识并入 `preflight`，使 `/flightdeck:preflight` 成为唯一入口（无 cockpit 则初始化、有则只读对账），并把工具版本升到 2.0.0。

**Architecture:** 纯 markdown / 配置改动（flightdeck 无运行代码，skill = AI 跟随的检查单）。先搬迁 + 新建 `preflight/` 下的知识文件，重写 `preflight/SKILL.md`，再删 `workflow/` 与 `hooks/`，最后扫一遍文档/清单同步并升版本。验证 = `rg` 断言 + 通读（本仓库无自动化测试，沿用 `TEST_PLAN.md` 风格）。

**Tech Stack:** Markdown、JSON manifest、bash/ps1 安装脚本；验证靠 Grep 断言 + 人工通读。

**Conventions for this plan:**
- 「当前 layout 版本」常量保持 **`1.2`**（本次不动布局）。
- 提交在每个 Task 末尾；当前在 `main`，**Task 0 先开分支**。
- 删除断言的「允许命中名单」= `CHANGELOG.md` / `MIGRATION.md` / `flightdeck/`（含 `landed/`、本 spec/plan 自身）。

---

### Task 0: 开工作分支

**Files:** （无文件改动）

- [ ] **Step 1: 从 main 建分支**

Run:
```bash
git switch -c feat/single-entry-preflight
```
Expected: `Switched to a new branch 'feat/single-entry-preflight'`

- [ ] **Step 2: 提交已就绪的 spec + plan + INDEX**

Run: `git status --short`
Expected: 显示未提交的 `flightdeck/specs/2026-06-02-*.md`、`flightdeck/plans/2026-06-02-*.md`、`flightdeck/specs/INDEX.md`、`flightdeck/INDEX.md`（plan 文件本步生成后一并提交）。先提交它们：
```bash
git add flightdeck/specs/2026-06-02-single-entry-preflight-collapse-design.md flightdeck/plans/2026-06-02-single-entry-preflight-collapse-plan.md flightdeck/specs/INDEX.md flightdeck/INDEX.md
git commit -m "docs(spec+plan): single-entry preflight collapse (2.0 design + plan)"
```

---

### Task 1: 搬迁三个 companion 到 preflight/

**Files:**
- Move: `skills/workflow/exit-ritual.md` → `skills/preflight/exit-ritual.md`
- Move: `skills/workflow/folder-semantics.md` → `skills/preflight/folder-semantics.md`
- Move: `skills/workflow/templates.md` → `skills/preflight/templates.md`

- [ ] **Step 1: git mv 三个文件**

Run:
```bash
git mv skills/workflow/exit-ritual.md skills/preflight/exit-ritual.md
git mv skills/workflow/folder-semantics.md skills/preflight/folder-semantics.md
git mv skills/workflow/templates.md skills/preflight/templates.md
```
Expected: 无报错。

- [ ] **Step 2: 验证迁移**

Run: `ls skills/preflight/`
Expected: 含 `SKILL.md exit-ritual.md folder-semantics.md templates.md`。`skills/workflow/` 现在只剩 `SKILL.md`。

- [ ] **Step 3: Commit**

```bash
git add -A skills/
git commit -m "refactor(skills): move workflow companions into preflight/"
```

---

### Task 2: 新建 `skills/preflight/protocol.md`（承载原 workflow 协议知识）

**Files:**
- Create: `skills/preflight/protocol.md`

- [ ] **Step 1: 从 `skills/workflow/SKILL.md` 抽取协议知识到 protocol.md**

把 `workflow/SKILL.md` 的**概念/协议**段落整块搬入新文件 `skills/preflight/protocol.md`，保留原文措辞，含这些节：`Core principle`、`Project rules (rules.md)`、`Data model`、`Status`、`INDEX.md`、`Folder map`、`Authority order`、`Design philosophy`、`Lifecycle`、`Write gate`、`Incident promotion gates`、`Common mistakes — STOP and reclassify`、`Relation to project agent rules`、`Cross-references`。文件头加：

```markdown
# flightdeck protocol (reference)

> Loaded on demand by `preflight` (and referenced by `landing` / `walkaround`). This is the protocol "textbook": the data model, folder semantics, authority order, write gate, and lifecycle. The operational entry ritual lives in [SKILL.md](SKILL.md).
```

companion 内部链接保持相对路径不变（`templates.md` / `exit-ritual.md` / `folder-semantics.md` 现在与 protocol.md 同目录，链接已正确）。

- [ ] **Step 2: 验证 protocol.md 覆盖关键节**

Run: `rg -n "^## (Core principle|Data model|Authority order|Write gate|Common mistakes)" skills/preflight/protocol.md`
Expected: 五节全部命中。

- [ ] **Step 3: Commit**

```bash
git add skills/preflight/protocol.md
git commit -m "feat(preflight): add protocol.md (former workflow knowledge)"
```

---

### Task 3: 重写 `skills/preflight/SKILL.md`（branch-0 + 统一 fallback + 协议索引）

**Files:**
- Modify: `skills/preflight/SKILL.md`

- [ ] **Step 1: 在 checklist 最前面加 branch-0（init-or-read）**

在现有 `## Run this checklist exactly` 的 step 0（读 rules）**之前**插入新的最前置步骤，措辞：

```markdown
0. **Branch-0 — deck existence (MUST run first; layout detection MUST NOT run before this).**
   Check whether `flightdeck/cockpit.md` exists (cockpit.md, not just the directory — it is flightdeck's minimal contract, so this also covers a half-initialized `flightdeck/` with no cockpit).

   - **`flightdeck/cockpit.md` does NOT exist** → run **First-time setup**: ask to create (minimal = just `cockpit.md`); on confirm, short interview (Active focus 5–15 words; first Next-session item); write `flightdeck/cockpit.md` from the template with today's date and `**Layout**: 1.2`. Then STOP — next `/preflight` takes the read path. Do NOT pre-create other folders.
   - **`flightdeck/cockpit.md` exists** → continue to the read path below (rules → layout check → reconcile → catalog → report).
```

把原有 step 编号顺延（rules 读取成为 branch-0 之后的第一步）。`Layout` 检测仍在「cockpit 存在」分支内、读 cockpit 之处。

- [ ] **Step 2: 统一空-Next-session fallback（修复与旧 workflow 的分歧）**

把 `## Fallback when "Next session" is empty` 段替换为合并版（含 specs/ + plans/ + sketches/）：

```markdown
## Fallback when "Next session" is empty

Don't auto-start anything. Search in order (a missing directory counts as empty), present candidates to the user:

1. `flightdeck/plans/` — surface `pending` / `blocked` / `active` plans (read `plans/INDEX.md`), most actionable first; a `done`-but-unlanded plan → offer to land it.
2. `flightdeck/specs/` — `active` / `pending` designs not yet planned (read `specs/INDEX.md`); ask which to turn into a plan.
3. `flightdeck/sketches/` — unstarted ideas (read `sketches/INDEX.md`); ask which (if any) to promote to a spec.
```

- [ ] **Step 3: 加「协议知识」索引指针**

在 SKILL.md 末尾加一节，把概念内容指向 companion（SKILL 只留操作）：

```markdown
## Protocol knowledge (load on demand)

The operational entry ritual is above. The protocol "textbook" lives in companions — read on demand:
- [protocol.md](protocol.md) — data model · status · INDEX · folder map · authority order · write gate · lifecycle · promotion gates · common mistakes
- [folder-semantics.md](folder-semantics.md) — what each folder holds; minimal-vs-full setup
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — the landing ritual (used by `/flightdeck:landing`)
```

- [ ] **Step 4: 更新 frontmatter description（含 init-or-read）**

把第 3 行 `description:` 改为反映新职责（单入口、无 deck 则初始化），例如结尾追加 `Initializes flightdeck/ when absent; otherwise reconciles and reports.`。保持 `disable-model-invocation: true`。

- [ ] **Step 5: 长度检查（≤ ~300 行）**

Run: `(Get-Content skills/preflight/SKILL.md | Measure-Object -Line).Lines`（pwsh）/ `wc -l skills/preflight/SKILL.md`（bash）
Expected: ≤ ~300。若超出，把仍属「概念」的段落移入 `protocol.md`，SKILL 只留操作步骤 + 索引。

- [ ] **Step 6: 验证 branch-0 与 fallback**

Run: `rg -n "Branch-0|MUST run first|cockpit.md does NOT exist|Fallback when|specs/INDEX.md" skills/preflight/SKILL.md`
Expected: 命中 branch-0 标签、existence 分支、合并后的 fallback（含 specs/）。

- [ ] **Step 7: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "feat(preflight): branch-0 init-or-read, unified fallback, protocol index"
```

---

### Task 4: 删除 `skills/workflow/`

**Files:**
- Delete: `skills/workflow/SKILL.md`（目录现已只剩它）

- [ ] **Step 1: 删除目录**

Run:
```bash
git rm -r skills/workflow
```
Expected: 删除 `skills/workflow/SKILL.md`。

- [ ] **Step 2: 验证已无 workflow skill 目录**

Run: `ls skills/`
Expected: `preflight landing walkaround emit-agents-md`（无 `workflow`）。

- [ ] **Step 3: Commit**

```bash
git add -A skills/
git commit -m "refactor(skills): delete workflow skill (folded into preflight)"
```

---

### Task 5: 重指其余 skill 的 companion 链接

**Files:**
- Modify: `skills/landing/SKILL.md`
- Modify: `skills/walkaround/SKILL.md`
- Modify: `skills/emit-agents-md/SKILL.md`

- [ ] **Step 1: 全量替换 `../workflow/` → `../preflight/`（三文件各自改完即验）**

逐文件把所有 `../workflow/` 路径改为 `../preflight/`（涉及 `exit-ritual.md` / `folder-semantics.md` / `templates.md`）。**每改完一个文件立即跑局部断言**：

Run（每文件一次）: `rg -n "\.\./workflow/" skills/landing/SKILL.md`
Expected: 无命中（改完后）。对 `walkaround` / `emit-agents-md` 同理。

- [ ] **Step 2: 确认三 skill 自足（不依赖 preflight 已跑）**

通读三文件开头：landing 显式 link `../preflight/exit-ritual.md`（其规则正文所在）；walkaround / emit-agents-md 自带或显式加载所需 companion。确认没有「假设 workflow 已注入」的措辞；若有，改为显式 link 到 `../preflight/protocol.md` 对应节。

- [ ] **Step 3: 验证三文件无残链**

Run: `rg -l "\.\./workflow|skills/workflow" skills/`
Expected: 无命中。

- [ ] **Step 4: Commit**

```bash
git add skills/landing/SKILL.md skills/walkaround/SKILL.md skills/emit-agents-md/SKILL.md
git commit -m "refactor(skills): repoint companion links to preflight/"
```

---

### Task 6: 删除整个 hook

**Files:**
- Delete: `hooks/session-start`
- Delete: `hooks/run-hook.cmd`
- Delete: `hooks/hooks.json`

- [ ] **Step 1: 删除 hooks 目录**

Run:
```bash
git rm -r hooks
```
Expected: 删除三文件。

- [ ] **Step 2: 验证无 hook 残留引用**

Run: `rg -l "session-start|SessionStart|run-hook" . --glob '!flightdeck/charts/**'`
Expected: 仅可能命中 `CHANGELOG.md` / 历史 `landed/` / 本 spec/plan；`hooks/`、`skills/`、manifest 均无命中。

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor: remove SessionStart hook (manual-only entry)"
```

---

### Task 7: 同步 manifest / GEMINI.md / 安装脚本

**Files:**
- Modify: `GEMINI.md:1-4`
- Modify: `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.cursor-plugin/plugin.json`（keyword）
- Modify: `install.ps1:7`、`install.sh:4`

- [ ] **Step 1: GEMINI.md 重指 import**

把：
```
@./skills/workflow/SKILL.md
@./skills/workflow/folder-semantics.md
@./skills/workflow/templates.md
@./skills/workflow/exit-ritual.md
```
改为：
```
@./skills/preflight/SKILL.md
@./skills/preflight/protocol.md
@./skills/preflight/folder-semantics.md
@./skills/preflight/templates.md
@./skills/preflight/exit-ritual.md
```

- [ ] **Step 2: 三 manifest keyword `workflow` → `preflight`**

在三个 `plugin.json` 的 `keywords` 数组里把 `"workflow"` 改为 `"preflight"`（每文件一处）。

- [ ] **Step 3: 安装脚本注释去 workflow**

`install.ps1:7` 与 `install.sh:4` 把 "installs workflow + preflight + landing + walkaround + emit-agents-md" 改为 "installs preflight + landing + walkaround + emit-agents-md"。

- [ ] **Step 4: 验证**

Run: `rg -n "workflow" GEMINI.md install.ps1 install.sh .claude-plugin/plugin.json .codex-plugin/plugin.json .cursor-plugin/plugin.json`
Expected: 无命中。

- [ ] **Step 5: Commit**

```bash
git add GEMINI.md install.ps1 install.sh .claude-plugin/plugin.json .codex-plugin/plugin.json .cursor-plugin/plugin.json
git commit -m "chore: repoint Gemini imports + manifests + install scripts off workflow"
```

---

### Task 8: 重写 README.md / README.zh.md（去自动加载叙事）

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: TL;DR + Getting started**

去掉「protocol auto-loads / 协议自动加载」叙事，改为「`/flightdeck:preflight` 是唯一入口：无 deck 则初始化、有则读取 cockpit + 对账」。把现有 Getting started 那段 SessionStart hook 自动加载的描述删掉/改写；保留迁移那段（已指向 preflight），并改成「入场即运行 `/flightdeck:preflight`」。

- [ ] **Step 2: Slash 命令表**

删掉 `/flightdeck:workflow` 行与「✅ 自动加载 / via SessionStart hook」列内容；把 `preflight` 标为唯一入口（init-or-read）。其余 `landing` / `walkaround` / `emit-agents-md` 行保留。

- [ ] **Step 3: 架构 Mermaid 图**

去掉 `AGENTS`/hook 自动注入相关的「SessionStart 注入」边与 `Other AI tools ... read on session start` 中暗示自动的措辞（emit 仍保留）；移除任何 workflow 节点。

- [ ] **Step 4: 对比表**

把 `**Skill self-loading** trigger` / `**Skill 自加载**触发` 那一行删掉或改为 `**Single explicit entry**`（flightdeck = ✅ explicit）。

- [ ] **Step 5: 验证两 README 无自动加载残留**

Run: `rg -n "auto-load|auto-loads|自动加载|SessionStart|flightdeck:workflow" README.md README.zh.md`
Expected: 无命中。

- [ ] **Step 6: Commit**

```bash
git add README.md README.zh.md
git commit -m "docs(readme): single explicit /preflight entry; drop auto-load narrative"
```

---

### Task 9: 同步 adapters / scaffolds / AGENTS.md

**Files:**
- Modify: `adapters/claude/README.md`、`adapters/codex/README.md`、`adapters/cursor/README.md`、`adapters/gemini/README.md`（按命中改）
- Modify: `scaffolds/**`（按命中改）
- Modify: `AGENTS.md`（若存在且命中）

- [ ] **Step 1: 列出 adapters/scaffolds/AGENTS 的 workflow/auto 命中**

Run: `rg -n "workflow|auto-load|SessionStart|session-start" adapters scaffolds AGENTS.md`
Expected: 得到一份命中清单（逐处处理）。

- [ ] **Step 2: 逐处改写**

- adapters/*/README.md：把「workflow 自动加载」描述改为「运行 `/flightdeck:preflight`」；Claude 适配器若描述 SessionStart hook，改为「2.0 起无 hook，显式 `/preflight`」。
- scaffolds：把 cockpit 模板等处 `skill: workflow` / `(skill: workflow)` 文案改为 `preflight`。
- AGENTS.md：若有 workflow/auto 提及，改为 preflight；其余 emit 内容不动。

- [ ] **Step 3: 验证**

Run: `rg -n "workflow|auto-load|SessionStart|session-start" adapters scaffolds AGENTS.md`
Expected: 无命中（或仅剩明确说明「2.0 移除」的句子）。

- [ ] **Step 4: Commit**

```bash
git add adapters scaffolds AGENTS.md
git commit -m "docs(adapters+scaffolds): sync to single-entry preflight"
```

---

### Task 10: MIGRATION.md + CHANGELOG.md + TEST_PLAN.md

**Files:**
- Modify: `MIGRATION.md`
- Modify: `CHANGELOG.md`
- Modify: `TEST_PLAN.md`

- [ ] **Step 1: MIGRATION 增「1.3 → 2.0」段 + 影响表**

在 MIGRATION.md 顶部加新段：

```markdown
## 1.3 → 2.0 — single explicit entry

2.0 removes the auto-loaded `workflow` skill and the SessionStart hook. The entry is now a single explicit command, `/flightdeck:preflight`.

| Area | Affected? |
|---|---|
| deck data / `**Layout**` / `cockpit.md` | No — your `flightdeck/` needs no changes (Layout stays 1.2) |
| slash command (`/flightdeck:workflow`) | Yes — removed; use `/flightdeck:preflight` |
| auto-load (SessionStart injection) | Yes — gone |

**Action required:** users who relied on automatic SessionStart loading must explicitly run `/flightdeck:preflight` at the start of a working session — otherwise nothing happens on session start. Why delete instead of merge: the auto-load duplicated preflight's reconcile (a double-run, not a complement) and the two entries had already drifted into different behavior.
```

- [ ] **Step 2: CHANGELOG `## [2.0.0]`**

在顶部加：

```markdown
## [2.0.0] — 2026-06-02

Entry-layer collapse: one explicit entry skill, no auto-load. (Unrelated to the abandoned work-items "2.0" line — this 2.0 is purely about the entry model.)

### Removed
- **Auto-loaded `workflow` skill** and the **SessionStart hook** — flightdeck is now manual-only. `/flightdeck:workflow` no longer exists.

### Changed
- **`/flightdeck:preflight` is the single entry** — initializes `flightdeck/` when absent (no `cockpit.md`), otherwise reconciles + reports (unchanged read behavior). Protocol knowledge moved into `skills/preflight/` (`protocol.md` + relocated companions).
- Empty-`Next session` fallback unified (specs/ + plans/ + sketches/), fixing a prior workflow/preflight divergence.

### Migration
- `flightdeck/` decks need no changes — Layout stays 1.2. Run `/flightdeck:preflight` explicitly at session start. See [MIGRATION.md](MIGRATION.md).
```

- [ ] **Step 3: TEST_PLAN 入口用例**

把任何提到「workflow 自动加载 / SessionStart」的用例改为「`/preflight` init-or-read 单入口」；新增一条：无 `cockpit.md` 时 `/preflight` 走 First-time setup。

- [ ] **Step 4: 验证**

Run: `rg -n "2.0.0|single explicit entry|preflight" CHANGELOG.md MIGRATION.md`
Expected: 命中新段。

- [ ] **Step 5: Commit**

```bash
git add MIGRATION.md CHANGELOG.md TEST_PLAN.md
git commit -m "docs(release): 2.0 migration + changelog + test plan"
```

---

### Task 11: 升版本号到 2.0.0

**Files:**
- Modify: `VERSION`
- Modify: `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.cursor-plugin/plugin.json`（`"version"`）

- [ ] **Step 1: VERSION**

把 `VERSION` 内容改为 `2.0.0`。

- [ ] **Step 2: 三 manifest version**

把三个 `plugin.json` 的 `"version": "1.3.0"` 改为 `"version": "2.0.0"`。

- [ ] **Step 3: 验证版本一致**

Run: `rg -n "2.0.0" VERSION .claude-plugin/plugin.json .codex-plugin/plugin.json .cursor-plugin/plugin.json`
Expected: 四处均为 2.0.0。

- [ ] **Step 4: Commit**

```bash
git add VERSION .claude-plugin/plugin.json .codex-plugin/plugin.json .cursor-plugin/plugin.json
git commit -m "chore(release): v2.0.0"
```

---

### Task 12: 全量「概念删除」断言 + 通读

**Files:** （无改动，纯复核）

- [ ] **Step 1: 删除断言（仅允许 CHANGELOG/MIGRATION/flightdeck 命中）**

Run: `rg -n "skills/workflow|\.\./workflow|flightdeck:workflow|SessionStart|session-start|run-hook" . --glob '!flightdeck/charts/**'`
Expected: 仅命中 `CHANGELOG.md` / `MIGRATION.md` / `flightdeck/`（landed/ 历史 + 本 spec/plan）。`skills/`、`hooks/`(已删)、manifest、README、adapters、scaffolds、安装脚本均无命中。

- [ ] **Step 2: 「auto-load / 自动加载」断言**

Run: `rg -n "auto-load|auto-loads|自动加载" . --glob '!flightdeck/charts/**'`
Expected: 仅 `CHANGELOG.md` / `MIGRATION.md` / `flightdeck/` 历史命中。

- [ ] **Step 3: 通读关键路径**

通读 `skills/preflight/SKILL.md` 一遍：确认 branch-0 在最前、existence 用 cockpit.md、Layout 检测在「存在」分支内、fallback 含 specs/、协议指针指向 protocol.md。确认 ls `skills/` 无 workflow、无 `hooks/`。

---

### Task 13: 落地（landing）spec + plan，更新 cockpit/INDEX/HISTORY，合并并推送

**Files:**
- Move: `flightdeck/specs/2026-06-02-*.md` → `flightdeck/landed/specs/`
- Move: `flightdeck/plans/2026-06-02-*.md` → `flightdeck/landed/plans/`
- Modify: `flightdeck/specs/INDEX.md`、`flightdeck/plans/INDEX.md`、`flightdeck/INDEX.md`、`flightdeck/cockpit.md`、`flightdeck/landed/HISTORY.md`

- [ ] **Step 1: spec/plan 置 done 并 git mv 入 landed/**

把两文件 frontmatter `status: active` → `status: done`；plan 的 `implements:` 改为 `landed/specs/2026-06-02-single-entry-preflight-collapse-design.md`；然后：
```bash
git mv flightdeck/specs/2026-06-02-single-entry-preflight-collapse-design.md flightdeck/landed/specs/2026-06-02-single-entry-preflight-collapse-design.md
git mv flightdeck/plans/2026-06-02-single-entry-preflight-collapse-plan.md flightdeck/landed/plans/2026-06-02-single-entry-preflight-collapse-plan.md
```

- [ ] **Step 2: INDEX 收尾**

`specs/INDEX.md` / `plans/INDEX.md` 删掉本 spec/plan 行；根 `flightdeck/INDEX.md` 把 specs/ 计数 -1（回到 1 active）。

- [ ] **Step 3: HISTORY + cockpit**

`landed/HISTORY.md` 顶部加：`- 2026-06-02 — v2.0.0: single explicit /preflight entry; deleted workflow skill + SessionStart hook; protocol folded into preflight/. Layout unchanged (1.2).`
`cockpit.md`：`Last updated` → 2026-06-02（v2.0.0 shipped）；`Active focus` → 反映 2.0 已发；`Next session` 视情况清理（去掉已完成项）。`**Layout**: 1.2` 不变。

- [ ] **Step 4: 提交 landing**

```bash
git add -A flightdeck/
git commit -m "chore(landing): land 2.0 single-entry collapse (spec+plan archived, cockpit/INDEX/HISTORY)"
```

- [ ] **Step 5: 合并回 main 并推送**

```bash
git switch main
git merge --no-ff feat/single-entry-preflight -m "merge: flightdeck 2.0 — single explicit preflight entry"
git push origin main
```
Expected: push 成功；远端 `main` 含 2.0.0。

- [ ] **Step 6: 打 tag（可选，若仓库惯例用 tag）**

```bash
git tag v2.0.0
git push origin v2.0.0
```
