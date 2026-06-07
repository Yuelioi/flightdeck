---
status: done
summary: 把 write-gate-examples spec 落地的逐文件实施——protocol § Write gate 加自立 skip-list 负例 + 一对 ✅/❌ 写不写示例；exit-ritual 加独立 ### body 质量小节（记实质结果/变更非过程元叙述 + 自立 fact + 承重字面量 + 一对 ✅/❌ 怎么写 + 跨类一行）；hook-primary-refactor spec 加边界注记一行；纯 prose 不动脚本/数据模型，人工结构闸 + ≤~25 行软护栏验收
last_updated: 2026-06-07
implements: specs/2026-06-07-write-gate-examples.md
---

# 写门操作化落地实施 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 spec `2026-06-07-write-gate-examples` 定义的写门操作化指引落地——`protocol § Write gate` 锐化「该不该写」（自立 skip-list 负例 + 一对 ✅/❌ 写不写示例），`exit-ritual` 加独立 `### body 质量` 小节锐化「写下来的怎么写」（记实质结果/变更非过程元叙述 + 自立 fact + 承重字面量 + 一对 ✅/❌ + 跨类一行），并在 hook-primary-refactor spec 加一行边界注记防漂移。

**Architecture:** 纯 prose 工程——只改 `skills/preflight/protocol.md`、`skills/preflight/exit-ritual.md` 两处 prose + 在一个 spec 加边界注记一行。**不动**脚本、数据模型、status 语义、frontmatter 契约、folder 分类。skills/ 改动对所有 deck 共享（`scaffolds/full/` 只 ship deck，不含这两文件），无副本同步。

**Tech Stack:** flightdeck skill markdown；`scripts/flightdeck_index.py`（只读校验）、`scripts/flightdeck_lint.py`（dangling-ref 校验）。

**约定（全 plan 通用）:**
- **语言**：skill prose 是英文 → 插入文本给**英文草稿**（spec 正文里的 ✅/❌ 示例是中文表意，落地渲染为英文以对齐既有 skill 语言；内容/语义照 spec）。措辞可按邻近段风格微调，不是 placeholder。
- **示例形式**：统一用 `✅`/`❌` 符号（不混用 "GOOD/BAD" 文字标签，spec 已定）。gate 处 = ✅写/❌不写；body 处 = ✅怎么写好/❌怎么写糟。
- **不串层（防回归原始错位）**：gate 两例都答「够不够格进 deck」；body 两例是「同一条该写的知识写好 vs 写糟」。
- **commit**：本仓库 commit 由 landing 管、**never push**。逐 task 改完跑 checkpoint（推进下方 `current:` 指针，disk-only），**不在 task 末尾单独 commit**；全部完成后 Task 4 单次 `/flightdeck:landing` 提交。
- **死链警惕**：见 incident `skill-prose-links-into-dogfood-deck` —— 在 skill prose 加任何 `[text](#anchor)` 前先确认锚点存在（本 plan 改动**不引入新跨文件链接**，但若复用现有锚点须先核）。
- **软护栏**：两处新增**宜 ≤ ~25 非空行**，仅"是否堆砌"提示参考、**非硬闸**（spec §测试/验收）。

## Progress

current: done — Task 1–3 实施完成（protocol § Write gate / exit-ritual body 质量 / refactor 边界注记），Task 4 验收过（index --check clean、三处 grep 确认、软护栏 ≪25 行），待 landing 收尾

---

### Task 1: protocol.md —— § Write gate 加 skip-list 负例 + ✅/❌ 写不写示例

**Files:**
- Modify: `skills/preflight/protocol.md` —— `## Write gate`（line 297–299，现仅一段抽象标准）

实现 spec 改动点 1。**现有段（line 299）原句不动**，在其**之后**追加一个自立 Skip 清单（含两条「不算 skip」边界）+ 一对 ✅/❌ 写不写示例。

- [ ] **Step 1: 在现有标准段后插入 Skip 清单 + 边界**

在 `## Write gate` 现有段落（`... Gate strictly.`）之后插入英文草稿：

```markdown
**Skip — gate these out (do NOT write):** empty status checks (`status` / `ls` that surfaced nothing); **a dependency install / build command that merely succeeded with no derived conclusion** (`npm/pip/uv install`, a green build by itself); **an exploration that concluded nothing** (searched, neither found nor ruled anything out); **a repeat that added no new information** (same op rerun without widening coverage / reaching a new conclusion / eliminating a new possibility); one-off logs and trial-and-error play-by-plays ("today's log is…" / "I tried 5 ways").

**Two boundaries — NOT skips, do write:** ① an exploration that yields an **exclusionary conclusion** ("X is not the root cause") is negative knowledge — **write it**; ② a repeat that **brings new coverage / a new conclusion** — **write it**.
```

- [ ] **Step 2: 紧接其后插入一对 ✅/❌「写不写」示例（每例挂钩 gate 三标准）**

```markdown
- ✅ write: "Cursor injection is fixed to `.cursor/rules/*.mdc` as the primary path (sessionStart proved unreliable)" — **influences future decisions, will be referenced repeatedly**.
- ❌ don't: "today's `--check` run printed clean" — a one-off status that changes no future behavior.
```

> 与 exit-ritual `(g) One-off → DO NOT WRITE` 同向但各自完整（spec 设计段）：本 Skip 清单是 `protocol` 写门的 canonical 负面清单（写任何工件前都过），(g) 是 `landing` 分类首匹配项——措辞各自自立、不交叉依赖阅读。**本 task 不改 (g)**。

- [ ] **Step 3: 验证**

- `uv run scripts/flightdeck_lint.py flightdeck` → `{"findings": []}`（无 dangling-ref）。
- 读 `## Write gate` 全节：确认原句未动、Skip 清单含**两条边界**、一对 ✅/❌ 都答「够不够格进 deck」（gate 层，不串到「怎么写」）。
- 软护栏：本节新增 ≤ ~25 非空行（超出则人工复看可否精简，非硬闸）。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 2`。

---

### Task 2: exit-ritual.md —— 加独立 `### 写工件 body 的质量` 小节

**Files:**
- Modify: `skills/preflight/exit-ritual.md` —— `## Classification heuristics`（line 94）下，**(h)（line 164–169）之后、`## AI-asks-user template`（line 170）之前**

实现 spec 改动点 2。落点 = **独立 `###` 小节，不插进 (a)–(h) 首匹配链**（那是门控触发链，不混入写作规范）。

- [ ] **Step 1: 在 (h) 之后、`## AI-asks-user template` 之前插入新 `###` 小节**

```markdown
### 写工件 body 的质量 — how to write what you keep

Once the gate says *keep it*, write the body so it is reusable:

- **Record the substantive result / change, not process meta-narration.** State the new fact or constraint about the system / your understanding directly — "`emit()` gained a Codex branch", "X failed because Y" — the statement stands on its own, **no** `implemented` / `discovered` verb prefix required. Do **not** write process meta-narration ("analyzed…", "investigated…", "currently looking at…"). The opposite of a good body is *process narration*, not "state vs change".
  > A verb table (implemented / fixed / decided / migrated) only **illustrates the shape of a good entry — it is not mandatory**; `discovered` / `decided` slip back into action-sentences, so prefer stating the result directly, and many valid statements ("`emit()` gained a Codex branch") need no leading verb at all.
- **Each fact stands alone** — no pronouns ("it" / "this"); readable out of context.
- **Carry the load-bearing literals** — filenames, function / symbol names, key values, error strings. Not "changed that function" but "`emit()` gained a Codex branch".
- **Examples + one cross-kind line:**
  - ✅ "`emit()` now branches injection fields per host (Claude / Codex / Gemini = `additionalContext`)"  ❌ "researched how each host differs in injection fields"
  - Decisions / incidents likewise: record "chose Z over the alternatives because of constraint Y" / "X failed because Y" — **not** "discussed several options".

> Layering vs cockpit `## 关键上下文` (a later, separate item): that is cockpit's **recovery slot**; this block is the **body of a knowledge artifact**. Both stress load-bearing literals; different layers, cross-referenced, not duplicated.
```

- [ ] **Step 2: 验证**

- `uv run scripts/flightdeck_lint.py flightdeck` → `{"findings": []}`。
- `grep -n "写工件 body 的质量" skills/preflight/exit-ritual.md` 确认小节存在；确认它是 `###` 且位于 (h) 与 `## AI-asks-user template` 之间、**不在** (a)–(h) 编号链内（读上下确认编号链未被插断）。
- 读小节：确认①「记实质结果/变更，非过程元叙述」（不是"状态 vs 变更"）②动词表标注为示意非强制 ③一对 ✅/❌ + 跨类一行都答「同一条该写的知识怎么写」（body 层，不串到 gate）。
- 软护栏：本节 ≤ ~25 非空行。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 3`。

---

### Task 3: hook-primary-refactor spec —— 加边界注记一行（防漂移）

**Files:**
- Modify: `flightdeck/specs/2026-06-07-hook-primary-refactor.md` —— "文案层"（Phase 2 prose 重写所在段）

实现 spec「与 hook refactor 的边界」锚点。#1 与 refactor Phase 2 都碰 `protocol.md` / `exit-ritual.md`；#1 先定稿这几段，refactor Phase 2 按 section 标题锚点**跳过**。

- [ ] **Step 1: 在 refactor spec 的文案层加一行**

加（措辞贴该 spec 邻近风格，中/英按该 spec 主语言）：

```markdown
> 写门 / 分类启发 / body 质量段归 `write-gate-examples`（已落地），本轮不重写——Phase 2 按 section 标题锚点跳过 `protocol.md` 的 `## Write gate`、`exit-ritual.md` 的 `### 写工件 body 的质量` + `## Classification heuristics` 的 (a)–(h)。**Phase 2 不得移动 / 改名这三处标题**（只跳过、不重构）；真要动结构须在 refactor 内显式交接新锚点。
```

- [ ] **Step 2: 验证**

- `grep -n "write-gate-examples" flightdeck/specs/2026-06-07-hook-primary-refactor.md` 确认注记存在。
- `uv run scripts/flightdeck_index.py flightdeck`（refactor spec 是 deck 内文件，确认 INDEX/cockpit 行不被破坏 → `already clean` 或正常 regen）。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 4`。

---

### Task 4: 结构闸验收 + landing 收尾

**Files:**
- Read-only 校验 + `/flightdeck:landing`

- [ ] **Step 1: 结构闸（人工核，主体）**

逐项核（`rg` 仅辅助定位、不作通过判据，spec §验收）：
- ① `protocol § Write gate` 新增 = 自立 Skip 清单（含两条「不算 skip」边界）+ 一对 ✅/❌ **写不写**示例；
- ② `exit-ritual` 新增 = **独立 `###` 小节**（不在 (a)–(h) 链内）+ 一对 ✅/❌ **怎么写**示例 + **跨类一行**（decision/incident 同理）；
- ③ **对口自检**：gate 两例都是「够不够格进 deck」、body 两例都是「同一条该写的知识写好/写糟」，**不串层**；
- ④ **无外来概念**：两处都**不出现** 6-type / `<private>` / `concepts`。

- [ ] **Step 2: 脚本校验（必要非充分——只证 frontmatter/INDEX，不证文案）**

```bash
uv run scripts/flightdeck_index.py flightdeck --check
uv run scripts/flightdeck_lint.py flightdeck
```
Expected: index `--check` 无 drift；lint `{"findings": []}`。

- [ ] **Step 3: 软护栏复看**

两处新增各 ≤ ~25 非空行（提示参考，非阻塞）；超出则人工判断可否精简。

- [ ] **Step 4: landing 收尾（单次提交）**

Run `/flightdeck:landing`：把 spec+plan 一并推进（此 plan `done` → 触发 spec co-advance 对账 → spec+plan 作为 cluster 归档），更新 cockpit/INDEX，**单次本地 commit（never push）**。commit message：中文 body，遵循 `checklists/commits.md`；多行串经 `git commit -F` 或 heredoc（**不**用 PowerShell here-string 过 Bash tool，见 incident `powershell-herestring-in-bash-tool`）。

- [ ] **Step 5: (部署，可选)** resync skill 改动进 plugin 缓存并重载（见 checklist `local-plugin-testing`），下个会话 live 复看写门指引生效。此步是部署、不属本 plan 的文件改动验收。

---

## 备注:为什么不逐 task commit

与本仓库 dogfood 一致——用 checkpoint（每 task 推进 `current:` 指针、disk-only）中途保持可恢复，末尾单次 landing 提交。纯 prose 改动、三 task 紧凑，碎 commit 无收益。
