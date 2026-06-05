---
status: done
summary: 在 landing 加 checkpoint 轻量子路径（task 边界只同步看板·不提交）+ plan 正文 current 指针；纯 skill 散文改，脚本层零改动
last_updated: 2026-06-06
implements: archive/specs/2026-06-06-execution-checkpoint.md
---

# 执行检查点（checkpoint）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 flightdeck 加一个「task 边界自动同步看板、不走收尾重活、不提交」的轻量 checkpoint，让用户随时可关对话、下次 `/flightdeck:preflight` 干净接手、上下文不丢。

**Architecture:** checkpoint = **完整 landing 的子集**，落成 `landing` skill 的一条轻量 **mode**（不是新用户命令）。它只做 landing 第 4 步看板同步的两件事——刷新 cockpit `## 下一步` + 推进 active plan 正文的 `## Progress` `current:` 指针——并**落盘即止**（不分类知识、不 regen INDEX、不归档、不 smoke-check、不 commit）。canonical 定义写在 `skills/preflight/exit-ritual.md`（protocol textbook 的家），其余 skill 引它。`## 进行中` 仍是 AUTO、plan 仍 `active`，`current:` 指针只活在 plan **正文**而非 frontmatter，故脚本层 `flightdeck_index.py` **零改动**。

**Tech Stack:** 纯 Markdown skill 散文（`skills/` 下的 SKILL.md / exit-ritual.md / protocol.md / templates.md / folder-semantics.md）。无代码、无 pytest 改动；验证靠**跨文件一致性 grep + 一次 dogfood 走查**。

## Progress

current: done — ready to land（5 task 全部完成；5 处 skill 一致、锚点全解析、脚本零改动经 index 复跑实证）

**约束（来自 memory / House Rules）**：本仓库**只 commit、绝不 push**；中文 commit body；改 skill 后按 `checklists/local-plugin-testing.md` resync 到 plugin 缓存才能 live 复验。

---

### Task 1: 在 exit-ritual.md 写下 checkpoint 的 canonical 定义

**Files:**
- Modify: `skills/preflight/exit-ritual.md`（在 `## Cockpit update — what changes` 段之后、`## Land Routine` 段之前插入新段；并改 `## 下一步` 自动写时机那句 + `When to update mid-session` 那句）

- [ ] **Step 1: 在 `## Cockpit update — what changes` 段末尾（`**When to update mid-session:**` 那段）后面、`**Length check before exit:**` 之前，插入新的 `## Checkpoint` 段**

把现有这句（约 line 258）：

```markdown
**When to update mid-session:** after any commit that changes user-perceivable state, refresh `## 下一步` before starting the next task — don't wait for landing.
```

改写为（把它升级成 checkpoint 的正式名字）：

```markdown
**When to update mid-session — this is the *checkpoint*:** at every plan / plan-task boundary, refresh `## 下一步` and advance the plan's `## Progress` `current:` pointer **before** starting the next task — don't wait for landing. This lightweight board-sync has a name and a home: see [§ Checkpoint](#checkpoint--lightweight-board-sync-subpath).
```

- [ ] **Step 2: 紧接 `## Land Routine` 段之前，新增整段 `## Checkpoint`**

```markdown
## Checkpoint — lightweight board-sync subpath

A **checkpoint** is the cheapest possible status-write: it keeps the persisted board (`cockpit.md` + the active plan file) equal to *actual* progress, so a user can close the conversation at any plan-task boundary and the next `/flightdeck:preflight` resumes on a true picture — no lost context. It is **a strict subset of landing**: landing = checkpoint + the wrap-up heavy lifting (knowledge-classify, INDEX regen, archive, smoke-check, commit).

**Trigger (AI self-invoke — not a hook):** a plan or plan-task **finishes**. Trivial edits do **not** trigger (avoid noise commits/churn). This extends the "rituals self-invoke" trigger point from *session-wrap only* to *also task boundaries*; it is the AI deciding to run landing's light mode, never a harness-timed hook (stays inside [docs/why-no-hooks.md](../../docs/why-no-hooks.md)).

**Action — exactly two board writes, then stop:**
1. Refresh cockpit `## 下一步` to the next concrete single action (the next task).
2. Advance the active plan's `## Progress` `current:` pointer to the next task.

Both are **disk writes only**. A checkpoint **does NOT**: classify new knowledge · regen any INDEX · archive a `done` item · run the smoke-check · bump `Last updated` for a non-milestone task · **commit**.

**Why no commit (the two orthogonal axes):** "close-and-reopen with context intact" rides on the **board being on disk**, not on git — `preflight` reads the *files*, regardless of commit state. So a checkpoint syncs the board (cheap, every task, uncommitted) while **commit stays a deliberate, separate axis** (landing or a milestone), avoiding a trail of noise commits. (If a checkpoint *does* coincide with a milestone worth a commit, a local commit is still within the default — reversible; push always asks.)

**Reuse, don't fork:** a checkpoint's two writes are the *same* `## 下一步` / `## Progress` logic landing's Step 4 uses — there is one implementation. `landing` simply has a `checkpoint` mode that runs Step 4's board-sync and skips Steps 1–3 and 5–7 (see [landing SKILL.md § Modes](../landing/SKILL.md#modes--full-vs-checkpoint)).
```

- [ ] **Step 3: 改 `## 下一步` 自动写时机那句（约 line 252）**

把：

```markdown
**`## 下一步` is auto-written by landing** (and on `idea→active` / a completed milestone). Its content is the next concrete **single** action — either (i) start an idea from the to-start pool, or (ii) advance an active artifact. `preflight` reads it but does not rewrite it (a stale entry is corrected at the next write point).
```

改为（补上 checkpoint 触发点）：

```markdown
**`## 下一步` is auto-written by landing** (and on `idea→active` / a completed milestone / **a plan-task checkpoint** — see [§ Checkpoint](#checkpoint--lightweight-board-sync-subpath)). Its content is the next concrete **single** action — either (i) start an idea from the to-start pool, or (ii) advance an active artifact. `preflight` reads it but does not rewrite it (a stale entry is corrected at the next write point).
```

- [ ] **Step 4: 一致性自检（grep）**

Run:
```bash
git -C E:/projects/tools/flightdeck grep -n "checkpoint\|Checkpoint" -- skills/preflight/exit-ritual.md
```
Expected: 新 `## Checkpoint` 段 + 两处引用都在；段内锚点 `#checkpoint--lightweight-board-sync-subpath` 与标题 slug 一致（标题 `## Checkpoint — lightweight board-sync subpath` → GitHub slug `checkpoint--lightweight-board-sync-subpath`，破折号成对保留）。

- [ ] **Step 5: Commit**

```bash
git -C E:/projects/tools/flightdeck add skills/preflight/exit-ritual.md
git -C E:/projects/tools/flightdeck commit -F- <<'EOF'
feat(flightdeck): exit-ritual 写下 checkpoint 的 canonical 定义

checkpoint = 完整 landing 的子集：plan/task 边界只同步看板
（下一步 + plan current 指针）、落盘即止、默认不提交。
触发=AI 自调 landing 轻量 mode（非 hook），琐碎改不触发。
新增 ## Checkpoint 段 + 把 mid-session 那句升级成正式名字。
EOF
```

---

### Task 2: 加 plan 正文「当前 task」指针约定（templates + folder-semantics）

**Files:**
- Modify: `skills/preflight/templates.md`（`## plan frontmatter` 段后补 plan **正文** `## Progress` 约定）
- Modify: `skills/preflight/folder-semantics.md`（`plans/` 段补 `current:` 指针 + checkpoint 关系）

- [ ] **Step 1: 在 templates.md 的 `## plan frontmatter` 段（约 line 69–81）代码块之后，紧接 `---` 分隔线之前，插入 plan 正文约定**

```markdown

**Plan body — progress pointer (`## Progress`).** A plan tracks execution progress with a single **pointer**, not per-task checkboxes:

```markdown
## Progress

current: Task 3 — wire the checkpoint subpath into landing SKILL.md
```

- `current:` names the next-to-execute (or in-progress) task. A **checkpoint** advances it at each plan-task boundary (see [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath)); cockpit `## 下一步` quotes it.
- It lives in the plan **body**, not frontmatter — so `flightdeck_index.py` does not parse it and `## 进行中` stays a pure `status: active` projection (no script change).
- When every task is finished, `current:` reads `done — ready to land` and the plan flips `status: done`.
```

- [ ] **Step 2: 在 folder-semantics.md 的 `plans/` 段补一句**

Run (先定位 plans/ 段):
```bash
git -C E:/projects/tools/flightdeck grep -n "plans/" -- skills/preflight/folder-semantics.md
```

在 `plans/` 段描述末尾补：

```markdown
A plan body carries a `## Progress` block with a `current:` pointer to the next-to-execute task; checkpoints advance it at task boundaries and cockpit `## 下一步` quotes it (see [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath)). The pointer is body-only — it is **not** a frontmatter field and does not enter any INDEX.
```

- [ ] **Step 3: 一致性自检**

Run:
```bash
git -C E:/projects/tools/flightdeck grep -n "Progress\|current:" -- skills/preflight/templates.md skills/preflight/folder-semantics.md
```
Expected: 两文件都出现 `## Progress` / `current:` 约定，且都链到 exit-ritual 的 Checkpoint 锚点（与 Task 1 标题 slug 一致）。

- [ ] **Step 4: Commit**

```bash
git -C E:/projects/tools/flightdeck add skills/preflight/templates.md skills/preflight/folder-semantics.md
git -C E:/projects/tools/flightdeck commit -F- <<'EOF'
feat(flightdeck): plan 正文加 ## Progress current 指针约定

plan 用单一 current 指针（非 checkbox）记进度，活在正文不入
frontmatter→脚本零改动、## 进行中 仍纯 status 投影。checkpoint
在 task 边界推进它，cockpit 下一步引它。templates + folder-semantics 同步。
EOF
```

---

### Task 3: 把 checkpoint 子路径接进 landing SKILL.md（Modes）

**Files:**
- Modify: `skills/landing/SKILL.md`（开头加 `## Modes` 段；并在 checklist 顶注明 checkpoint mode 只跑第 4 步）

- [ ] **Step 1: 在 `# Flightdeck Landing` 标题段（约 line 6–12 的 use 列表）之后、`## Run this checklist`（约 line 14）之前，插入 `## Modes` 段**

```markdown
## Modes — full vs checkpoint

`landing` runs in one of two modes; the AI picks by the trigger:

| | **full** (default) | **checkpoint** (lightweight) |
|---|---|---|
| Trigger | session wrap · `/flightdeck:landing` · end-of-turn `done`-flip | **plan / plan-task boundary** (AI self-invoke) |
| Runs | the whole checklist (Steps 0–7) | **only Step 4's board-sync** — refresh `## 下一步` + advance the active plan's `## Progress` `current:` pointer |
| Skips | nothing | knowledge-classify (2) · INDEX regen (3) · archive (3a) · AGENTS.md (5) · smoke-check (6) · **commit (7)** |
| Commit | local auto (push asks) | **none** (board on disk is enough; durability deferred to a full landing / milestone) |

A checkpoint is a **strict subset of a full landing** — same Step-4 board-sync implementation, no fork. Canonical definition + rationale: [exit-ritual § Checkpoint](../preflight/exit-ritual.md#checkpoint--lightweight-board-sync-subpath). When in doubt (is this a task boundary or a session wrap?), a full landing is always safe — checkpoint is the cheaper option, never a required one.
```

- [ ] **Step 2: 在 `## Run this checklist` 段引子里点明 checkpoint 走法**

把（约 line 16）：

```markdown
The full rules + rationale live in [exit-ritual.md](../preflight/exit-ritual.md). Skeleton:
```

改为：

```markdown
The full rules + rationale live in [exit-ritual.md](../preflight/exit-ritual.md). The checklist below is **full mode**; in **checkpoint mode** run **only Step 4** (board-sync) and stop — skip every other step. Skeleton:
```

- [ ] **Step 3: 一致性自检**

Run:
```bash
git -C E:/projects/tools/flightdeck grep -n "checkpoint\|Modes\|board-sync" -- skills/landing/SKILL.md
```
Expected: `## Modes` 表 + checkpoint 只跑 Step 4 的说明都在；链到 exit-ritual Checkpoint 锚点正确。

- [ ] **Step 4: Commit**

```bash
git -C E:/projects/tools/flightdeck add skills/landing/SKILL.md
git -C E:/projects/tools/flightdeck commit -F- <<'EOF'
feat(flightdeck): landing 加 checkpoint 子路径（Modes: full vs checkpoint）

checkpoint mode 只跑第 4 步看板同步（刷新下一步 + 推进 plan
current 指针）、跳过分类/INDEX/归档/smoke/commit。复用同一
Step-4 实现不分叉；触发=plan/task 边界 AI 自调。引 exit-ritual 定义。
EOF
```

---

### Task 4: 在 protocol.md 收口 checkpoint 概念（lifecycle + 职责表 + 下一步触发）

**Files:**
- Modify: `skills/preflight/protocol.md`（`## Lifecycle` 补一句 · `## Ritual responsibilities` 框住 checkpoint 是 landing 的轻量写 · `## 下一步` 是 landing 写那处补触发点）

- [ ] **Step 1: 在 `## Lifecycle` 段（约 line 259–270）的 plan 那句后补一句 checkpoint**

把（约 line 266）句末：

```markdown
... `location` (active vs `archive/`) is derived from landing a done item. Folder says the kind; frontmatter `status` says the state.
```

后面紧接补一句：

```markdown
 While a plan is `active`, **checkpoints** keep the board synced at each plan-task boundary (cockpit `## 下一步` + the plan's `## Progress` `current:` pointer, disk-write only, no commit) — the lightweight subset of landing that makes a mid-plan close-and-reopen lossless. See [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath).
```

- [ ] **Step 2: 在 `## Ritual responsibilities` 表（约 line 282–288）的 `landing` 行 Role 单元补 checkpoint**

把 `landing` 行的 Role 文字 `write the session's outcome` 改为：

```markdown
write the session's outcome (full mode); board-sync only (checkpoint mode at task boundaries)
```

并在表后补一句澄清（紧接 line 288 那句 `The 80-line cockpit trim is **landing's**...` 之后）：

```markdown
Checkpoint is **landing's lightweight mode**, not a fourth ritual — it reuses landing's Step-4 board-sync and writes nothing else (no INDEX, no archive, no commit). `preflight` stays read-only; checkpoint never runs at entry.
```

- [ ] **Step 3: 同步「`## 下一步` 由谁写」那处（grep 定位）**

Run:
```bash
git -C E:/projects/tools/flightdeck grep -n "下一步.*auto\|auto.*下一步\|下一步\` is AI-maintained\|AI-maintained" -- skills/preflight/protocol.md
```
若有「`## 下一步` is AI-maintained / auto-written by landing」类描述（约 line 97 / 252 区），在其括注的触发场景里补上 `/ at a plan-task checkpoint`，与 exit-ritual.md Step 3 的改法一致。无则跳过。

- [ ] **Step 4: 一致性自检（全树）**

Run:
```bash
git -C E:/projects/tools/flightdeck grep -rn "checkpoint" -- skills/
```
Expected: exit-ritual（定义+引用）· landing（Modes）· templates（Progress）· folder-semantics（plans）· protocol（lifecycle+职责）五处一致，所有锚点都指向 `exit-ritual.md#checkpoint--lightweight-board-sync-subpath`。无指向不存在锚点的死链。

- [ ] **Step 5: Commit**

```bash
git -C E:/projects/tools/flightdeck add skills/preflight/protocol.md
git -C E:/projects/tools/flightdeck commit -F- <<'EOF'
feat(flightdeck): protocol 收口 checkpoint（lifecycle + 职责表 + 下一步触发）

lifecycle 补「active plan 靠 checkpoint 保持看板同步」；职责表把
checkpoint 框成 landing 的轻量 mode（非第四仪式，preflight 仍只读）；
下一步触发场景补 plan-task checkpoint。至此五处 skill 引用一致。
EOF
```

---

### Task 5: 一致性终审 + dogfood 走查 + landing

**Files:**
- 只读复核全部已改 skill；按 `flightdeck/checklists/local-plugin-testing.md` resync；用一个临时 active plan 走一遍 checkpoint。

- [ ] **Step 1: 终审——重读五处改动，查矛盾**

逐一重读 Task 1–4 改过的段落，对照 spec `flightdeck/specs/2026-06-06-execution-checkpoint.md` 的「已定方向」三条 + 「落地范围」三条，确认：
- 形态 = landing 子路径 ✓ · 进度 = current 指针 ✓ · 不提交 ✓
- `## 进行中` 未被改、未引入新 frontmatter 字段、脚本未改 ✓
- 无与 `why-no-hooks`（checkpoint 是 AI 自调非 hook）或「landing 写 outcome」职责的冲突 ✓

- [ ] **Step 2: resync 到 plugin 缓存（live 复验前置）**

按 `flightdeck/checklists/local-plugin-testing.md` 把工作树同步进 plugin 缓存（robocopy + build-stamp + `.current`）。Expected: 缓存里的 `skills/landing/SKILL.md` / `skills/preflight/exit-ritual.md` 含本次新段。

- [ ] **Step 3: dogfood——模拟一次 checkpoint**

在本 dogfood deck 造一个临时 active plan（或直接用本 plan 自身），给它一个 `## Progress` `current: Task N`。模拟「Task N 完成」：自调 landing 的 checkpoint mode，确认它**只**：刷新 cockpit `## 下一步` 指向 Task N+1、把 plan `current:` 推进到 Task N+1；**未**产生 commit、**未**改 INDEX、**未**归档。
Run（确认无提交、无 INDEX 改动）:
```bash
git -C E:/projects/tools/flightdeck status --short -- flightdeck/
```
Expected: 仅 cockpit.md + 该 plan 文件有改动；INDEX.md 不在改动列表；无新 commit 产生（checkpoint 不提交）。

- [ ] **Step 4: 关-开接手验证（核心卖点）**

不 commit 的前提下，`/flightdeck:preflight` 复核：报出的 `## 下一步` = Task N+1（与 plan `current:` 一致）。Expected: preflight 干净接手到真实进度，证明「随时可关、上下文不丢」靠看板落盘而非 git 成立。

- [ ] **Step 5: 收尾——回滚临时 dogfood 痕迹，跑 landing**

撤掉 Step 3 造的临时进度（若用真 plan，把 `current:` 复位）。然后 `/flightdeck:landing`（full mode）正式收尾本特性：flip 本 plan → done、flip spec → done、regen INDEX/cockpit、本地 commit（push 不做——本仓库只 commit）。

---

## Self-Review

- **Spec coverage**：spec 的「设计：checkpoint=看板同步」表 → Task 1/3 落成；「触发判据」→ Task 1 Step 2 + Task 3 Modes；「为什么不破规矩」三条 → Task 4 职责表 + lifecycle；「落地形态/已定方向」三条 → Task 1（exit-ritual 家）+ Task 2（current 指针）+ 全程不提交。**无遗漏**。
- **No placeholders**：每步给出实际待插入的 Markdown 块与确切文件/段落定位；grep 命令带预期输出。
- **一致性**：所有锚点统一指向 `exit-ritual.md#checkpoint--lightweight-board-sync-subpath`（Task 4 Step 4 全树 grep 兜底）；`current:` 在 templates 与 folder-semantics 同名；`## Progress` 命名前后一致。
- **脚本零改动**断言由「`current:` 在 plan 正文、`## 进行中` 仍 AUTO」保证——Task 5 Step 3 的 `git status` 验证 INDEX 不变即复核了这一点。
