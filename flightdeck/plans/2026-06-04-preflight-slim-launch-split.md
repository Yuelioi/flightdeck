---
status: active
summary: 实现 preflight 瘦身 + 拆出 /flightdeck:launch——新建 launch skill（搬 setup.md）、重写 preflight（重定向 Branch-0 / 删重复检查 / 2 列 catalog / 被动 git 表 / 版本 bump 优先级）、删 setup.md、改两条 description、交叉引用 doc-sweep；验证靠现有 pytest + index --check + dogfood + walkaround。清单自动发现无需注册，CHANGELOG 留发布时写
last_updated: 2026-06-04
implements: specs/2026-06-04-preflight-slim-launch-split-design.md
---

# preflight 瘦身 + 拆出 /flightdeck:launch — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 preflight 的「首次建 deck」拆成独立的 `/flightdeck:launch`，并将 preflight 瘦成纯接管（读 cockpit/INDEX → 报下一步 + 精简 catalog 预热 + 被动 git/版本提示），删掉与 walkaround 重复的检查。

**Architecture:** flightdeck 的命令即 `skills/<name>/SKILL.md`（清单 `"skills": "./skills/"` 目录指针**自动发现**，无需注册）。本计划是 **markdown skill + 文档** 的编辑：无新 Python 代码（launch 复用 `scripts/flightdeck_init.py` 不变）。因此「测试」= 现有 `pytest scripts/tests/` 仍绿 + `flightdeck_index.py --check` 干净 + 针对性 grep 确认无悬空引用 + 手工 dogfood，而非新写单测。

**Tech Stack:** Markdown（skill 正文）、JSON（清单，本计划不改）、Python stdlib 脚本（`flightdeck_init.py` / `flightdeck_index.py`，复用不改）、pytest。

---

## File Structure

- **Create** `skills/launch/SKILL.md` — 首次建 deck 的命令（搬 `setup.md` 正文 + 终态报告 + 拒绝条件）。
- **Rewrite** `skills/preflight/SKILL.md` — Branch-0 改重定向 + deckless 护栏；删迁移探测/catalog 体检/cockpit 漂移/阻塞 reconcile；catalog 降 2 列 + 脚注；git 降被动触发表；版本 bump 优先级；改 description；改 output format / Fallback / Don't do / 协议索引（去 setup.md）。
- **Delete** `skills/preflight/setup.md` — 内容已迁入 launch。
- **Edit (doc-sweep)** `skills/preflight/protocol.md`、`skills/preflight/folder-semantics.md`、`README.md`、`README.zh.md`、`adapters/claude/README.md`、`adapters/gemini/README.md` — 凡述 preflight「首次建 deck / setup.md / 接管即建」处改述。**不动** `MIGRATION.md` 历史段、**不动** `CHANGELOG.md`（见 Task 6 发布提醒）。

每个 Task 自成一个可独立审阅、可提交的变更。

---

## Task 1: 新建 `skills/launch/SKILL.md`

**Files:**
- Create: `skills/launch/SKILL.md`
- Reference (不改，复用): `scripts/flightdeck_init.py`、`scaffolds/full/flightdeck/`

- [ ] **Step 1: 写 `skills/launch/SKILL.md`**（完整内容如下，逐字写入）

```markdown
---
name: launch
description: Use when explicitly creating a flightdeck deck for the first time in a project that has none — copies the full-layout scaffold and seeds cockpit.md (zero prompts), then stops. Refuses if cockpit.md already exists. Triggered by /flightdeck:launch.
---

# Flightdeck Launch — first-time deck creation

The **one-time** command that brings a flightdeck deck into existence. Run `/flightdeck:launch` in a project that has **no `flightdeck/cockpit.md`**. It creates the deck with **zero prompts** — running it *is* the consent to create one — then stops. From then on, every working session starts with `/flightdeck:preflight` (which takes the read path).

`launch` is the only flightdeck command that scaffolds. `preflight` no longer creates a deck — in a deckless project it just points here and stops.

**Do not inspect the repo** (no `ls`, no reading `package.json`, no `git ls-files`). The scaffold is fixed; nothing about it depends on the project's contents.

## Refuse if a deck already exists

If `flightdeck/cockpit.md` already exists, this project already has a deck → **refuse** and redirect: "Deck already exists (`flightdeck/cockpit.md`). Run `/flightdeck:preflight` to take over." The bundled `flightdeck_init.py` enforces the same predicate (`(deck / "cockpit.md").exists()` → `FileExistsError`), so the fast path refuses automatically; the redirect target is the same `cockpit.md` test preflight uses, so there is no half-init dead-end.

## Run this

1. **Detect a Python runtime** — silently try `uv --version` (preferred) or `python --version`. This is the only probe; don't announce it.
2. **Create the deck — copy the scaffold verbatim.**
   - **Fast path** (a runtime is reachable): run the bundled initializer against the current dir, e.g. `uv run <flightdeck-pkg>/scripts/flightdeck_init.py . --user <user> --date <today>` — **no `--focus`/`--next`** (there is no interview). It copies `scaffolds/full/flightdeck/` into `./flightdeck/` (every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md`) and stamps name/date/user in one deterministic step. `Active focus` / `## 下一步` ship as `(set me)` placeholders. It also **silently removes `landed/HISTORY.md` when the deck root has `.git`** — that file is the no-git history substrate (`git log` is the history otherwise), so a git project never gets the dead file. Being a verbatim copy it **cannot re-author or drop the `rules.md` comments** — which hand-copying does. Refuses if `cockpit.md` already exists.
   - **Fallback** (no runtime): copy by hand from `../../scaffolds/full/flightdeck/` into `./flightdeck/` — **copy, do NOT re-author** (this is what preserves the `rules.md` comments) — then substitute today's date / project name / `<user>` into `cockpit.md`, leaving the `<ACTIVE_FOCUS …>` / `<FIRST_NEXT_ITEM …>` placeholders as `(set me)`. **If the deck root has `.git`, delete the copied `landed/HISTORY.md`** (git log is the history); keep it only for a no-git deck.
   - Either way: the scaffold `rules.md` `version` should equal `MIGRATION.md` `current` — bump it if the scaffold is behind.
3. **STOP** — report one line (below) and hand off. The next `/flightdeck:preflight` takes the read path.

## Final report (one line + optional hints)

> ✈ Deck created at `flightdeck/` (full layout, version `<v>`). Fill `Active focus` / `## 下一步` in `cockpit.md` when you start — or just run `/flightdeck:preflight`.
> Tune autonomy in `flightdeck/rules.md` → `### Autonomy overrides` (a commented catalog is there: auto-landing, auto-commit, no-git, run-scripts…). Defaults are safe — `landing` is manual; nothing archives or commits without you.
> Optional, anytime: `git init` (if you want history) · `/flightdeck:emit-agents-md` (cross-tool AGENTS.md bridge). Created it by mistake? Delete `flightdeck/`.

## Why zero prompts (3.0)

The git-init offer, the 2-question interview, and the AGENTS.md opt-in were all dropped to make first-run a **single deterministic copy** — the slow, chatty old flow was the complaint that drove this. git presence is simply *inferred* later on the read path (no prompt); the cockpit fields are placeholders the user fills when real work starts (or `landing` derives them); AGENTS.md stays opt-in via its own command.
```

- [ ] **Step 2: 确认 launch 自动可用 + 脚本测试仍绿**

Run: `uv run pytest scripts/tests/test_flightdeck_init.py -v`
Expected: PASS（launch 复用脚本未改，初始化测试不受影响）

- [ ] **Step 3: dogfood — 临时空目录建 deck**

```bash
mkdir -p /tmp/fd-launch-test && uv run scripts/flightdeck_init.py /tmp/fd-launch-test --user tester --date 2026-06-04 && ls /tmp/fd-launch-test/flightdeck && rm -rf /tmp/fd-launch-test
```
Expected: `flightdeck/` 含 cockpit.md / rules.md / INDEX.md 及各文件夹；命令成功。

- [ ] **Step 4: Commit**

```bash
git add skills/launch/SKILL.md
git commit -m "feat(flightdeck): 新增 /flightdeck:launch 首次建 deck 命令"
```

---

## Task 2: 重写 `skills/preflight/SKILL.md`

**Files:**
- Rewrite: `skills/preflight/SKILL.md`（整文件替换为下列内容）

- [ ] **Step 1: 用以下完整内容替换 `skills/preflight/SKILL.md`**

```markdown
---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — reads INDEX/cockpit and reports the next step, warms the routing catalog, and gives a passive note on obvious git/version misalignment. No deck (no cockpit.md) → points to /flightdeck:launch and stops. Triggered by /flightdeck:preflight.
---

# Flightdeck Preflight

The **session-entry takeover** for flightdeck. Run `/flightdeck:preflight` at the start of a working session: it reads the cockpit, reports the next item, and stops — **read-only**. It does **not** create decks (that is `/flightdeck:launch`) and does **not** audit deck integrity (that is `/flightdeck:walkaround`). Use it when:

- Starting a working session in a project that already has a `flightdeck/`.
- Re-anchoring a long session that has drifted away from the cockpit.

The protocol "textbook" (data model, folder semantics, routing, write gate, lifecycle) is in [protocol.md](protocol.md) — load it on demand; see the index at the bottom.

## Run this checklist exactly

0. **Branch-0 — deck existence (MUST run first, before the Gate and before reading anything).**
   Check whether **`flightdeck/cockpit.md` exists** (cockpit.md, not merely the directory — it is flightdeck's minimal contract).

   - **Does NOT exist** → report one line: "No flightdeck deck here — run `/flightdeck:launch` to create one." then **STOP**. Read nothing else: no `rules.md`, no repo listing, no `git`, no migration probe. (Deckless = immediate stop — this guardrail keeps preflight from re-growing into an installer. Deck creation lives in `/flightdeck:launch`.)
   - **Exists** → continue to the Gate, then step 1.

## Gate — model-invocation check (after Branch-0, before step 1)

Resolve `preflight` self-invocability per [protocol § Rule resolution order](protocol.md#rule-resolution-order). **Default (3.0): self-invocable — continue.** Restricted only if House Rules say `preflight: don't self-invoke` (or a pre-3.0 deck omits `preflight` from `model_invocable`): then an explicit user `/flightdeck:preflight` → continue; model self-invocation or unknown call source → **STOP immediately** and report "`preflight` is manual-only (House Rule). Remove the `preflight: don't self-invoke` line to allow self-invoke."

1. **Read `flightdeck/rules.md`** if present. Resolve config per [protocol § Rule resolution order](protocol.md#rule-resolution-order): infer git from deck root `.git` (House Rule `this deck doesn't use git` overrides — when no-git, skip step 4's git note); honor `disabled_folders` (don't suggest them in fallback). Pre-3.0 keys, if present, are honored for compat.

   **Version handling (two mutually exclusive branches — the only write preflight makes):** compare `rules.md` `version` against `MIGRATION.md` (`current` + `layout_need_update`); preflight and walkaround read the **same** list, so the verdict agrees.
   - **Compatible-behind** (`version < current` **and** not `< any layout_need_update` entry) → **silently bump `version` to `current`. No message.** (Protocol's one allowed silent stamp.)
   - **Structural-behind** (`version <` some `layout_need_update` entry, or no `version`/`rules.md`) → **do NOT bump.** Emit the passive note in step 4 (`ℹ deck version is structurally behind — run /flightdeck:walkaround for the migration`). The migration itself is walkaround's job (Audit 10); preflight never offers or performs it.

2. **Read `flightdeck/INDEX.md`** (root INDEX) once, in full — the global status summary (counts per folder). Then **read `flightdeck/cockpit.md`** once, in full — focus on `Last updated`, `Active focus`, the `## 进行中` AUTO region (the active set), and the `## 下一步` action. These are the reconcile baseline; read each once and treat as cached. `preflight` **reads** `## 进行中` / `## 下一步` but never rewrites them — a stale `## 下一步` is corrected at the next landing / status write point, not here.

3. **Catalog warm-up (priming, NOT audit).** Read the folder INDEX files so the session knows what routed knowledge exists — do NOT glob individual files or read per-file frontmatter, and do NOT audit them:
   - Read `flightdeck/checklists/INDEX.md` and `flightdeck/incidents/INDEX.md`. List each entry as **File + when_to_read (two columns only)** — drop `applies_to` / `status` (those live in the INDEX file; read on demand when a trigger matches). Append the footnote `(状态/合法性审计见 /flightdeck:walkaround)`.
   - **Do NOT** check status legality or INDEX↔folder consistency — that is `walkaround` (Audits 1/5). preflight only surfaces *what exists*.
   - `charts/` is deliberately out of the catalog (imported external material is browsed on purpose, not surfaced every preflight).
   - Do NOT drill into individual checklist/incident bodies — only when a trigger matches at execution time.

4. **Passive git/version note (non-blocking — skip git entirely when no-git).** Gather `git branch --show-current` + `git status --short` in one pass; emit a one-line note only when a row below triggers, never a blocking "Resolve which?" prompt:

   | Signal | Trigger? | Note |
   |---|---|---|
   | current branch token clearly mismatches `Active focus` | yes | `⚠ git state looks off (branch ≠ Active focus) — review before continuing` |
   | detached HEAD | yes | `⚠ git state looks off (detached HEAD) — review before continuing` |
   | structural-behind version (from step 1) | yes | `ℹ deck version is structurally behind — run /flightdeck:walkaround for the migration` |
   | uncommitted changes / ahead-behind / multiple stashes | no | (say nothing — day-to-day state, not preflight's concern) |

   Git-state notes say **"review before continuing"**, not "run walkaround" — walkaround is a read-only file audit and does not read live git. Only the **version** note points at walkaround.

5. **Report item #1, then STOP.** Read-only recon doesn't fly the mission. State the `## 下一步` item in one sentence and hand off: "Preflight complete (read-only). Say 'go' to execute item #1." Do not load any file body or start the task — that's the next turn.

   **Land-readiness as the FINAL output line** (skip under no-git): if `git status` shows **≥ 5** changed files under `flightdeck/`, append "⚠ N unlanded changes since last land — consider `/flightdeck:landing`". Below the threshold, say nothing.

## Fallback when `## 下一步` is empty

Don't auto-start anything. The data source is the **folder INDEX rows** (which carry `status`) — not file mtime, not a re-audit. Search in order (a missing directory counts as empty), present candidates to the user:

1. `flightdeck/plans/INDEX.md` — `active` rows, most actionable first; a `done`-but-unlanded plan → offer to land it.
2. `flightdeck/specs/INDEX.md` — `active` designs not yet turned into a plan; ask which to plan next.
3. `flightdeck/specs/INDEX.md` **to-start pool** — the `待启动（idea）` group; ask which (if any) to start (flip `idea → active`).

> **Done-but-unlanded (any folder):** an artifact whose `status: done` but still in its source folder is *done-but-unlanded*. Offer to land it via the [Land Routine](exit-ritual.md#land-routine).

## Output format

```
Root INDEX: specs/ — 2 (1 active, 1 done) | plans/ — 1 active | incidents/ — 1 active | checklists/ — 2 active
Cockpit (Last updated: 2026-05-25; Active focus: <X>)

Routing catalog (know-what-exists — read on demand; status audit → /flightdeck:walkaround):

[Checklists]
| File | when_to_read |
|---|---|
| checklists/comments.md | before writing or editing any source-code comment |

[Incidents]
| File | when_to_read |
|---|---|
| incidents/parser-recursion.md | before designing a recursive parser |

(状态/合法性审计见 /flightdeck:walkaround)

下一步 (item #1): <item description>

Preflight complete (read-only). → Say "go" to execute item #1.
```

Omit any table group with no entries. If both folder INDEX files are absent or empty, print `Routing catalog: (empty — no routed resources yet)`. Append any triggered git/version note from step 4 on its own line, and the Land-readiness line last.

## Don't do

- Don't create a deck — deckless → point at `/flightdeck:launch` and STOP (Branch-0).
- Don't audit — status legality, INDEX↔folder consistency, cockpit drift, migration offers all belong to `/flightdeck:walkaround`.
- Don't run the blocking "Resolve which?" git reconcile — git divergence is a passive one-liner now.
- Don't auto-pick a fallback when `## 下一步` is empty — always ask.
- Don't bump `Last updated` — entry doesn't modify cockpit.
- Don't grep the codebase for "things to do" — cockpit.md is authoritative.
- Don't drill into individual checklist/incident files until a trigger matches at execution time (read folder INDEX only).

## Protocol knowledge (load on demand)

- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle · promotion gates · common mistakes
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout (full, always)
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — the landing ritual (run by `/flightdeck:landing`) + Land-readiness check

(First-time deck creation lives in `/flightdeck:launch`.)
```

- [ ] **Step 2: 确认无悬空 setup.md 引用残留在 preflight SKILL**

Run: `grep -n "setup.md\|first-time setup\|Initializes\|bootstraps" skills/preflight/SKILL.md`
Expected: 无输出（已全部移除/改写）

- [ ] **Step 3: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "refactor(flightdeck): preflight 瘦成纯接管，Branch-0 改重定向至 launch"
```

---

## Task 3: 删除 `skills/preflight/setup.md`

**Files:**
- Delete: `skills/preflight/setup.md`

- [ ] **Step 1: 确认内容已迁入 launch**

Run: `grep -c "Detect a Python runtime" skills/launch/SKILL.md`
Expected: `1`（launch 已含 setup 正文）

- [ ] **Step 2: 删除文件**

```bash
git rm skills/preflight/setup.md
```

- [ ] **Step 3: 全仓库确认无指向 setup.md 的链接残留**

Run: `grep -rn "setup.md" skills/ README.md README.zh.md MIGRATION.md adapters/ docs/`
Expected: 无输出（Task 2 已移除 preflight 索引里的 setup.md 行；若 grep 命中，在 Task 4 一并改写）

- [ ] **Step 4: Commit**

```bash
git add -A skills/preflight/setup.md
git commit -m "chore(flightdeck): 删 preflight/setup.md（内容迁入 launch）"
```

---

## Task 4: 交叉引用 doc-sweep

把所有「preflight 首次建 deck / setup / 接管即建」的现状描述改述为「preflight 重定向 + `/flightdeck:launch` 建 deck」。**不动 `MIGRATION.md`**（历史段如实记录当时行为）。

**Files:**
- Modify: `skills/preflight/protocol.md`、`skills/preflight/folder-semantics.md`、`README.md`、`README.zh.md`、`adapters/claude/README.md`、`adapters/gemini/README.md`

- [ ] **Step 1: protocol.md — L220 routing 表去掉「first-time setup excepted」**

`skills/preflight/protocol.md:220`，把
`| `preflight` | read-only recon at session start | no (first-time setup excepted) | reads only — flags staleness, never trims | reads folder INDEX as catalog | no — only shallow root-count sanity |`
改为
`| `preflight` | read-only takeover at session start | no — deckless redirects to /flightdeck:launch | reads only — passive note on git/version drift | reads folder INDEX as catalog | no — audits belong to walkaround |`

- [ ] **Step 2: protocol.md — L90 version 来源行**

`skills/preflight/protocol.md:90`，把 `preflight setup / auto-bump`（version 的写入来源描述）改为 `launch (init) / preflight auto-bump`。

- [ ] **Step 3: folder-semantics.md — L7**

`skills/preflight/folder-semantics.md:7`，把 `both `preflight` first-time setup and `install --scaffold` lay the **full layout**` 改为 `both `/flightdeck:launch` and `install --scaffold` lay the **full layout**`.

- [ ] **Step 4: README.md — 改 4 处现状描述**

逐处改写（exact 行见下）：
- L26：`In a fresh one it bootstraps a deck in one step — zero prompts.` → `In a fresh one (no cockpit.md) it points you to /flightdeck:launch, which bootstraps a deck in one step — zero prompts.`
- L93：`You don't scaffold the deck by hand — /flightdeck:preflight creates it on first run.` → `You don't scaffold the deck by hand — run /flightdeck:launch once and it creates the deck.`
- L103：`On a brand-new project (no cockpit.md) it runs first-time setup instead: ...` → `On a brand-new project (no cockpit.md) preflight points you to /flightdeck:launch, which copies the scaffold in one deterministic step — zero prompts ...`（保留后半句的 zero-prompts / fill-fields 说明）。
- L111（命令表 preflight 行）：`The single entry point. Creates the deck when absent; otherwise reconciles cockpit.md against git and reports the next item.` → `Session-entry takeover — reconciles cockpit.md against git and reports the next item. Deckless → points to /flightdeck:launch.`；并在表中**新增一行** `| /flightdeck:launch | First-time deck creation — copies the scaffold, seeds cockpit.md (zero prompts). |`。
- L116（autonomy 句）：把可自调用列表 `preflight / walkaround / emit-agents-md / status` 保持不变（launch 是显式一次性命令，不进自调用默认；可加一句「launch 由用户显式运行」）。
- L189：`On entry, /flightdeck:preflight (and walkaround) read the deck version and offer a guided migration — never silent` → `On entry, /flightdeck:walkaround reads the deck version and offers a guided migration — never silent; preflight only flags a structurally-behind version and points there.`

- [ ] **Step 5: README.zh.md — 镜像 Step 4 的等价中文改写**

Run（先定位）: `grep -n "preflight\|首次\|创建.*deck\|setup\|迁移" README.zh.md`
对每个与 Step 4 对应的中文句子做等价改写：preflight 不再建 deck → 指向 `/flightdeck:launch`；命令表新增 launch 行；迁移 offer 归 walkaround、preflight 只提示。

- [ ] **Step 6: adapters/claude/README.md + adapters/gemini/README.md — 命令清单加 launch**

Run（先定位）: `grep -n "preflight\|walkaround\|landing\|status\|emit-agents" adapters/claude/README.md adapters/gemini/README.md`
在列出命令/skill 的清单处新增 `launch`（首次建 deck），并把任何「preflight 首次建 deck」的描述改述。Claude adapter 若有 install/uninstall 的 skill 列举，同步加 `launch`。

- [ ] **Step 7: 全仓库确认无悬空引用**

Run: `grep -rn "setup.md" skills/ README.md README.zh.md adapters/ docs/; echo "---"; grep -rn "preflight.*creates the deck\|preflight.*first-time setup\|bootstraps a deck" README.md README.zh.md skills/ adapters/`
Expected: 第一段无输出；第二段无遗漏的旧描述。

- [ ] **Step 8: Commit**

```bash
git add skills/preflight/protocol.md skills/preflight/folder-semantics.md README.md README.zh.md adapters/claude/README.md adapters/gemini/README.md
git commit -m "docs(flightdeck): 交叉引用改述 preflight 重定向 + launch 建 deck"
```

---

## Task 5: 全量验证 + dogfood

**Files:** 无（验证 only）

- [ ] **Step 1: 全脚本测试**

Run: `uv run pytest scripts/tests/ -q`
Expected: 全绿（无脚本改动，应与改前一致）

- [ ] **Step 2: index --check 干净**

Run: `uv run scripts/flightdeck_index.py flightdeck --check`
Expected: `clean`

- [ ] **Step 3: dogfood — deckless 重定向**

在临时空目录验证 preflight 的重定向语义（人工跑 `/flightdeck:preflight`，或核对 SKILL Branch-0 逻辑）：无 cockpit.md → 报「run /flightdeck:launch」+ STOP，**不读** rules/git/repo。
Expected: 仅一行重定向 + 停。

- [ ] **Step 4: dogfood — 本仓库瘦身后 preflight**

人工跑 `/flightdeck:preflight`（本仓库已有 deck）。
Expected: 读 INDEX/cockpit → 报下一步；catalog 两列 + 脚注；无阻塞互动；无迁移 offer；git/版本若正常则无提示。

- [ ] **Step 5: walkaround 干净**

人工跑 `/flightdeck:walkaround`（或 `uv run scripts/flightdeck_lint.py flightdeck`）。
Expected: 无 CRITICAL/WARNING 新增（确认 doc-sweep 没留悬空内部链接 → Audit 7）。

- [ ] **Step 6: 标记 plan 完成 + Commit（若验证有微调）**

验证全过后，将本 plan 与 spec 的 `status` 由 `active` 翻 `done`（经 `/flightdeck:status` 或手改 frontmatter + `flightdeck_index.py` 重生），不在此自动 land（按 House Rules，landing 手动）。

```bash
git add -A && git commit -m "test(flightdeck): preflight 瘦身 + launch 全量验证通过"
```

---

## Task 6: 发布提醒（不在本计划执行，记录给 release）

3.0 发布时（`flightdeck/checklists/version-bump.md` step 3 写 `## [3.0.0]` CHANGELOG 段），**必须**把这条用户行为变更写进 `Changed`：

> **preflight 不再自动建 deck** — deckless 目录下 preflight 现在指向新命令 `/flightdeck:launch` 并停止；首次建 deck 改用 `/flightdeck:launch`。preflight 的阻塞式 git reconcile 降级为被动一行提示；迁移探测/offer 收归 `/flightdeck:walkaround`。

本次**不**改 `CHANGELOG.md`（`bump_version.py --check` 要求顶部标题与清单 semver `2.3.0` 一致，提前加 3.0 段会破坏 `--check`）。

---

## Self-Review

**Spec coverage（逐节核对）：**
- A 新 launch + Branch-0 重定向 + 删 setup.md + 谓词对齐 + deckless 护栏 → Task 1 / Task 2(Step1 Branch-0) / Task 3 ✓
- B 保留项（读 rules/INDEX/cockpit、报下一步、catalog 2 列+脚注、git 被动表、版本 bump 优先级、fallback 数据源）+ 删除项（迁移探测/catalog 体检/cockpit 漂移/阻塞 reconcile）→ Task 2 整文件 ✓
- C 清单（自动发现，无需注册）+ 交叉引用改写 + CHANGELOG（发布时）+ 两条 description 定稿 → Task 4 / Task 6 / Task 1+2 frontmatter ✓
- D 不做项（不搬 git 对账进 walkaround、不改 walkaround Audit、不改 scaffold、不引入迁移）→ 计划中无相关任务，符合 ✓
- 验证（pytest + index --check + dogfood + walkaround + 隐式消费者核查）→ Task 5（隐式消费者：Task 4 Step7 grep 覆盖「无悬空引用」；applies_to/status 无输出消费者，INDEX 文件保留）✓

**Placeholder scan：** 两个 SKILL.md 给了完整逐字内容；doc-sweep 给了 exact old→new（有确切行的）+ grep 驱动转换规则（README.zh/adapters 因含未逐字读取的句子，用 grep+转换规则而非假占位，属合法机械改写指令）。无 TBD/TODO。

**Type/命名一致性：** 命令名统一 `/flightdeck:launch`；谓词统一 `cockpit.md` 存在性；description 与 SKILL frontmatter 一致；catalog 列定义（File + when_to_read）在 Task 2 正文与 output format 一致。
