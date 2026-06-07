---
status: done
summary: 把 end-of-turn soft-landing(知识落盘+「已保存」标记、不commit不归档、landing 幂等)铺进 exit-ritual/landing/protocol/status 4 个 skill + session-flow dogfood doc 的逐文件实施步骤
last_updated: 2026-06-07
implements: specs/2026-06-06-end-of-turn-soft-landing.md
---

# soft-landing 落地实施 Implementation Plan

> **Done（completed, archived）**——soft-landing 已 ship（commit `14c5a92`）。其 spec `specs/2026-06-06-end-of-turn-soft-landing` 的 *what* 仍有效、保持 active；本 rollout 仅作完成归档（非被取代）。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 spec `2026-06-06-end-of-turn-soft-landing` 定义的 soft-landing(end-of-turn 知识增量 → 自动知识+状态落盘 +「已保存」标记;不 commit、不归档;landing 幂等只补差集)铺进 flightdeck 的 skill 文档层。

**Architecture:** 纯文档工程——改 4 个 skill markdown(`exit-ritual` 为 source of truth,其余引用它)+ 1 篇 dogfood doc。不改脚本(`--archivable` 已实现)。soft-landing 是 landing 在"无 done"时的自然形态 + 标记,复用现有 Step 2–4,不新增机制。

**Tech Stack:** flightdeck skill markdown;`scripts/flightdeck_index.py`(只读校验)、`scripts/flightdeck_lint.py`(dangling-ref 校验)。

**约定(全 plan 通用):**
- **语言**:skill prose 是英文 → 插入文本给英文草稿(措辞可按邻近风格微调,不是 placeholder);**「已保存」标记保持中文**,对齐 flightdeck 既有中文 board(`## 进行中`/`## 下一步`)。
- **commit**:本仓库 commit 由 landing 管、**never push**。逐 task 改完跑 checkpoint(推进下方 `current:` 指针),**不在 task 末尾单独 commit**;全部完成后 Task 9 单次 `/flightdeck:landing` 提交(践行本 spec "不碎 commit")。
- **每个 task 的"验证"**(文档无单测):①`flightdeck_lint.py flightdeck` 无新 finding(尤其 dangling-ref);②插入的跨文件锚点目标真实存在(`grep` 标题);③关键术语跨文件一致(`soft-landing`/`signal 3`/`💾 上下文已保存`);④读改动节确认逻辑通顺、与 spec 对应节一致。
- **死链警惕**:见 incident `skill-prose-links-into-dogfood-deck` —— 在 skill prose 加任何 `[text](#anchor)` 前,先确认锚点存在。

## Progress

current: Task 1 — exit-ritual: signal 3

---

### Task 1: exit-ritual.md —— Land-readiness 加 signal 3

**Files:**
- Modify: `skills/preflight/exit-ritual.md` —— § Land-readiness check(现 `- **signal 1**` / `- **signal 2**` 列表 + `Mechanics:`)

- [ ] **Step 1: 在 signal 1/2 后插入 signal 3 条目**

在 `- **signal 2** — at session entry, git status shows ≥ 5 changed files …` 这一条之后插入:

```markdown
- **signal 3** — at end-of-turn (the AI is about to return control to the user), the session has a **knowledge increment**: a new, not-yet-persisted, write-gated knowledge item (see [§ Write gate](protocol.md#write-gate) — changes future behavior / influences decisions / referenced repeatedly; transient byproducts don't count). A **state-only** increment (cockpit `## 进行中` / `## 下一步` / `Active focus`, or plan-task progress, with **no** new knowledge) routes to **checkpoint**, not soft-landing.
```

- [ ] **Step 2: 在 `Mechanics:` 列表里加 signal 3 的机制(动作 + 时序 + 去重)**

在 Mechanics 列表中,signal 1/2 机制之后插入:

```markdown
- **signal 3 fires a *soft-landing*** — full landing's Steps 2–4 (classify knowledge · regen changed-folder INDEX · update cockpit board), with **no commit, no archive, no promotion gate**. It is landing's no-`done` natural form + a visible marker. **Timing is pinned: persist → print the 「已保存」marker → end the turn** (never "reply then persist"). The marker spec is in [§ Checkpoint](#checkpoint--lightweight-board-sync-subpath) (三档 table) / [§ Cockpit update](#cockpit-update--what-changes).
- **soft-landing dedup is stateless — the board itself is the watermark.** A turn that already ran a full landing (a `done` flip's end-of-turn debounce) does **not** also soft-land (one turn, one landing path). Knowledge already on disk reads back `already clean` → no-op. If a checkpoint already ran at a plan-task boundary this turn, only a **knowledge increment produced after that checkpoint (checkpoint-done → turn-end window)** re-triggers soft-landing; a checkpoint at turn's end leaves an empty window → silent. **No `last_checkpoint_time` / turn-id is stored** — already-persisted content self-detects as clean.
```

- [ ] **Step 3: 验证**

Run: `uv run scripts/flightdeck_lint.py flightdeck`
Expected: `{"findings": []}`(无 dangling-ref)。
再 `grep -n "Write gate" skills/preflight/protocol.md` 确认 `#write-gate` 锚点存在;`grep -rn "signal 3" skills/preflight/exit-ritual.md` 确认两处(条目 + 机制)一致。

- [ ] **Step 4: checkpoint** —— 把本 plan `current:` 指针推进到 `Task 2`,刷新 cockpit `## 下一步`(disk-only,不 commit)。

---

### Task 2: exit-ritual.md —— § Checkpoint 旁加"三档同源"+ soft-landing 定义

**Files:**
- Modify: `skills/preflight/exit-ritual.md` —— § Checkpoint(`## Checkpoint — lightweight board-sync subpath`,line ~262)

- [ ] **Step 1: 在 § Checkpoint 开头插入三档同源表 + soft-landing 定义**

在 `## Checkpoint — lightweight board-sync subpath` 标题正文之前(或紧随首段)插入:

```markdown
**Three tiers, one landing.** `checkpoint` ⊂ `soft-landing` ⊂ `full landing` — same machinery, different trigger + range (not three rituals):

| Tier | Essence | Trigger | Range | commit / archive |
|---|---|---|---|---|
| **checkpoint** | save **state** | plan-task boundary / end-of-turn state-only increment | board only (`## 下一步` + plan `current:`), disk-only | none |
| **soft-landing** | save **state + knowledge** | end-of-turn with a **knowledge increment** (signal 3) | checkpoint + classify knowledge + regen changed INDEX | **neither** |
| **full landing** | + **advance lifecycle** | `done` / explicit `/flightdeck:landing` | soft-landing + archive done + promotion gate | + local commit + archive |

`soft-landing` carries **no commit and no archive** — both are "traceable tails" deferred to a full landing (durability rides on files being on disk; `preflight` reads files, not git). See [§ Land-readiness signal 3](#land-readiness-check).
```

- [ ] **Step 2: 验证**

Run: `uv run scripts/flightdeck_lint.py flightdeck` → `{"findings": []}`。
`grep -n "Three tiers" skills/preflight/exit-ritual.md` 确认插入;确认 `#land-readiness-check` / `#checkpoint--lightweight-board-sync-subpath` 锚点(由 Task 1 Step 2 引用)互指无死链。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 3`。

---

### Task 3: exit-ritual.md ——「已保存」标记格式 + 沉默规则

**Files:**
- Modify: `skills/preflight/exit-ritual.md` —— § Cockpit update — what changes(line ~235;`## 下一步` 自动写那段之后)

- [ ] **Step 1: 新增「已保存」标记小节**

在 § Cockpit update 末尾(Length check 小节之前)插入:

```markdown
### The 「已保存」(saved) marker — soft-landing's visible signal

When a **soft-landing** runs (signal 3), end the turn with this marker so the user knows it is safe to close the conversation:

​```
──────────── 💾 上下文已保存 ────────────
知识 + 状态已落盘 · 现在关闭对话不会丢失
已落:<最多 3 个文件名;更多写「等 N 个文件」> · cockpit 已更新
下次 /flightdeck:preflight 干净接手
​```

- Wording is deliberately **「已保存 / 已落盘」, never "LANDED / 已归档 / 已完成"** — soft-landing does not archive and may not be `done`; the marker must not collide with `done ≠ archived`.
- Line 3 is a one-line check summary: **at most 3 filenames**, overflow → "等 N 个文件"; **no commit hash** (soft-landing does not commit).
- **Silence rule:** with no knowledge increment (pure Q&A / exploration, or state-only → checkpoint) → **print nothing**. Known trade-off: the user cannot distinguish "nothing to persist" from "AI missed it"; accepted to avoid noise.
```

(注:草稿里 ​``` 的零宽字符仅为在本 plan 内转义代码围栏——落地时写成正常三反引号。)

- [ ] **Step 2: 验证**

`grep -n "已保存" skills/preflight/exit-ritual.md` 确认标记块存在且为中文;`flightdeck_lint.py flightdeck` → `{"findings": []}`。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 4`。

---

### Task 4: exit-ritual.md —— 自评 done 安全阀(规则→例子)

**Files:**
- Modify: `skills/preflight/exit-ritual.md` —— § Classification heuristics 附近 / 新增小节(承接 spec §3)

- [ ] **Step 1: 新增"自评 done 安全阀"小节**

在 § Classification heuristics 之后(或 § Hanging tasks 之前)插入:

```markdown
## Self-asserting `done` — safety valve (pure-do tasks only)

soft-landing may flip `done` itself **only** for a pure-do, no-verify task. The boundary is **rule-first, examples-second** (avoid the "list = exhaustive" trap):

- **Rule:** anything that will be **mechanically executed by AI or scripts, where a misjudgment is not easily noticed**, is **needs-verify** (AI must NOT self-assert `done`).
- **Examples (non-exhaustive):** any external-system change (open PR, deploy, write DB, send email…); governance / data-model edits (`protocol.md`, `rules.md`, `AGENTS.md`, frontmatter fields, script contracts).
- When self-asserting `done`, the AI **must print a verdict line**: `[判定: <reason>; 无需验证; 自动 done]` — making the call observable and auditable.
- Self-asserting `done` is a **state write only** — soft-landing still does **not** archive (archival stays full landing's). Misjudgment is cheap: `done` is one frontmatter field the user can flip back, and no commit/move was produced.
```

- [ ] **Step 2: 验证**

`grep -n "safety valve" skills/preflight/exit-ritual.md` 确认;`flightdeck_lint.py flightdeck` → `{"findings": []}`;读该节确认与 spec §3 一致(规则在前、AGENTS.md 在例子里)。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 5`。

---

### Task 5: landing/SKILL.md —— Modes 表加 soft-landing 第三档

**Files:**
- Modify: `skills/landing/SKILL.md` —— `## Modes — full vs checkpoint`(line 14–25)

- [ ] **Step 1: 把两列 Modes 表改成三档,并补 soft-landing 行**

将标题改为 `## Modes — full · soft-landing · checkpoint`,并把现有 full/checkpoint 两列表替换为含 soft-landing 的版本:

```markdown
`landing` runs in one of three modes; the AI picks by the trigger (`checkpoint ⊂ soft-landing ⊂ full`):

| | **full** (default) | **soft-landing** | **checkpoint** |
|---|---|---|---|
| Trigger | session wrap · `/flightdeck:landing` · end-of-turn `done`-flip | **end-of-turn with a knowledge increment** (signal 3) | plan / plan-task boundary · end-of-turn state-only |
| Runs | the whole checklist (Steps 0–7) | Steps 2–4 (classify knowledge · regen changed INDEX · cockpit board) + 「已保存」marker | only Step 4's board-sync |
| Skips | nothing | archive (3a) · promotion gate (3z) · smoke-check (6) · **commit (7)** | everything except Step 4 |
| Commit / archive | local commit (push asks) + archive | **neither** (durability deferred to full landing) | none |

soft-landing is landing's **no-`done` natural form** — Steps 2–4 with no commit/archive, plus the 「已保存」marker; canonical definition + signal 3 trigger + stateless dedup: [exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check) and [§ Checkpoint 三档 table](../preflight/exit-ritual.md#checkpoint--lightweight-board-sync-subpath). landing 幂等: re-running full after a soft-landing only fills the diff (commit + archive + promotion gate); already-persisted Steps 2–4 self-detect `already clean`.
```

同步把 line 25 那句 "A checkpoint is a **strict subset of a full landing**…" 保留,并在其后补一句 soft-landing 同理(strict subset, no fork)。

- [ ] **Step 2: 验证**

`flightdeck_lint.py flightdeck` → `{"findings": []}`;确认引用的两个 exit-ritual 锚点存在;`grep -n "soft-landing" skills/landing/SKILL.md` 术语与 exit-ritual 一致。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 6`。

---

### Task 6: protocol.md —— Lifecycle + House Rule 表收口 signal 3

**Files:**
- Modify: `skills/preflight/protocol.md` —— Standard-phrase table(line 44–52)与 Lifecycle(line ~259)

- [ ] **Step 1: House Rule 标准短语表加"关闭 soft-landing"降级行**

在 Standard-phrase table(line 44–52)末尾加一行:

```markdown
| soft-landing at end-of-turn off (signal 3; on by default) | `landing: don't soft-land at end-of-turn` | `landing 结尾不自动落盘` |
```

并在表后 `There is no self-invoke override…` 那段不需要改(soft-landing 不是 toggle 机制,只是一条降级 House Rule)。

- [ ] **Step 2: Lifecycle 段补一句 signal 3**

在 `## Lifecycle` 的 end-of-turn 说明附近(现有 `done → landing` debounce 处)加一句:

```markdown
Beyond the `done`-triggered landing, an **end-of-turn knowledge increment** auto-runs a **soft-landing** (signal 3 — Steps 2–4 + 「已保存」marker, no commit/archive); default-on, downgradable via House Rule `landing: don't soft-land at end-of-turn`. See [exit-ritual § Land-readiness](exit-ritual.md#land-readiness-check).
```

- [ ] **Step 3: 验证**

`flightdeck_lint.py flightdeck` → `{"findings": []}`;`grep -n "soft-land" skills/preflight/protocol.md` 确认两处(表 + Lifecycle);确认 `landing: don't soft-land at end-of-turn` 短语与 Task 5/7 引用一致(逐字相同,因为 House Rule 匹配是 contiguous substring)。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 7`。

---

### Task 7: status/SKILL.md —— 交代 signal 3 不经 status + cockpit diff 复用

**Files:**
- Modify: `skills/status/SKILL.md` —— Step 7 — land-readiness (signal 1)(line 73–80)

- [ ] **Step 1: 在 Step 7 末尾加一句:signal 3 不经 status**

在 Step 7 的 "Edge-triggered by the flip itself…" 之后插入:

```markdown
**signal 3 (end-of-turn soft-landing) does NOT go through `status`.** It is the AI's own end-of-turn self-invoke when a knowledge increment exists (see [exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check)); `status` only emits **signal 1** (this flip → `done`). When soft-landing判定 a state-only increment, its cockpit "actual change" test **reuses this skill's `## 进行中` diff logic** (Step 5a — re-derive from current `status: active`), not a new diff.
```

- [ ] **Step 2: 验证**

`flightdeck_lint.py flightdeck` → `{"findings": []}`;`grep -n "signal 3" skills/status/SKILL.md` 确认;读确认未与 status"不碰 cockpit 其余区"原则矛盾(soft-landing 是 AI 自调、非 status 动作,措辞已划清)。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 8`。

---

### Task 8: dogfood —— session-flow.md 纳入 soft-landing +「已保存」标记

**Files:**
- Modify: `flightdeck/docs/session-flow.md` —— 主干图 + 三个岔口/分叉表

- [ ] **Step 1: 主干图加 soft-landing 节点**

在主干图 [执行] 与 [接缝/done] 之间,或"三个岔口"处,加入 end-of-turn soft-landing 一支(中文,与该 doc 风格一致),要点:
- end-of-turn 有**知识增量** → 自动 soft-landing(知识+状态落盘,不 commit/不归档)→ 输出 `💾 上下文已保存` 标记;
- 纯状态增量 → checkpoint 静默;无增量 → 沉默;
- 强调:这条让"长会话干完活、用户离开"也能上下文不丢、且用户看得到「已保存」信号。

- [ ] **Step 2: 分叉表补一行**

在"可能发生 vs 可能不发生"分叉表加:
```markdown
| 长会话干完活、用户离开,有新知识 | end-of-turn 自动 soft-landing 落盘 + 打「已保存」标记,可安全关闭 |
```

- [ ] **Step 3: 验证**

`flightdeck_index.py flightdeck`(session-flow 是 deck 内文件,确认 INDEX 行不被破坏 → `already clean` 或正常 regen);`flightdeck_lint.py flightdeck` → `{"findings": []}`(doc 内 `[spec-lifecycle.md](...)` 等链接仍有效)。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 9`。

---

### Task 9: 全局一致性验证 + landing 收尾

**Files:**
- Read-only 校验 + `/flightdeck:landing`

- [ ] **Step 1: 跨文件术语一致性 grep**

逐项确认措辞跨文件统一(否则 House Rule 匹配 / 锚点会断):
```bash
grep -rn "soft-land" skills/ flightdeck/docs/session-flow.md
grep -rn "signal 3" skills/
grep -rn "已保存" skills/ flightdeck/docs/
grep -rn "don't soft-land at end-of-turn" skills/   # House Rule 短语逐字一致
```
Expected: `soft-landing` 拼写统一;`signal 3` 在 exit-ritual/landing/protocol/status 一致;House Rule 短语在 protocol(定义)与任何引用处逐字相同。

- [ ] **Step 2: 脚本校验**

Run:
```bash
uv run scripts/flightdeck_index.py flightdeck --check
uv run scripts/flightdeck_lint.py flightdeck
```
Expected: index `--check` 无 drift;lint `{"findings": []}`。

- [ ] **Step 3: 锚点存活核对**

对本 plan 新增的每个 `[text](#anchor)` / `(../preflight/exit-ritual.md#anchor)`,`grep` 目标标题确认锚点真实存在(见 incident `skill-prose-links-into-dogfood-deck`)。重点:`#land-readiness-check`、`#checkpoint--lightweight-board-sync-subpath`、`#cockpit-update--what-changes`、`#write-gate`。

- [ ] **Step 4: landing 收尾(单次提交)**

Run `/flightdeck:landing`:把 spec+plan 一并推进(此 plan `done` → 触发 spec co-advance 对账 → spec+plan 作为 cluster 归档),更新 cockpit/INDEX,**单次本地 commit(never push)**。commit message:中文 body,遵循 `checklists/commits.md`;多行串经 `git commit -F` 或 heredoc(**不**用 PowerShell here-string 过 Bash tool,见 incident `powershell-herestring-in-bash-tool`)。

- [ ] **Step 5: (部署,可选)** resync skill 改动进 plugin 缓存并重载(见 cockpit `## 下一步` 与 checklist `local-plugin-testing`),live 复验 soft-landing 在下个会话生效。此步是部署、不属本 plan 的文件改动验收。

---

## 备注:为什么不逐 task commit

本 plan 的实施本身就是 flightdeck 自洽 dogfood——用 checkpoint(每 task 推进 `current:` 指针、disk-only)在中途保持可恢复,末尾单次 landing 提交。这与本 plan 实现的 spec 精神一致:**易失靠落盘(checkpoint 指针在盘上)、commit 是 full landing 的尾巴、不碎 commit**。
