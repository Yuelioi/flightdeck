---
status: done
implements: specs/2026-06-02-soft-config-model-invocation-design.md
---

# Soft-Config `model_invocable` — Downshift the Hard `disable-model-invocation` Switch — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the four ritual skills' load-time `disable-model-invocation: true` frontmatter with a per-project run-time `model_invocable` soft gate in `rules.md`, defaulting to "all manual" so every existing project behaves exactly as before.

**Architecture:** Two layers. **Layer 1 (platform):** delete `disable-model-invocation: true` from the four Claude `SKILL.md` files so the platform stops hiding them — this is the only place that field exists (Gemini/Codex/Cursor manifests carry no per-skill switch). **Layer 2 (skill body):** add an identical, tool-agnostic "Step 0 — model-invocation gate" to each ritual body that reads `rules.md`'s `model_invocable` list and refuses model self-invocation unless the ritual is opted in. Because the gate lives in the shared `SKILL.md` body, it ships to every platform for free. Default `model_invocable: []` ⇒ behavior identical to today.

**Tech Stack:** Plain Markdown skill files + YAML frontmatter (no build, no test runner). "Tests" here = `git grep` consistency checks + behavioral smoke-checks of actual skill invocation. Commits are per-task.

**Scope (from the spec):** This plan lands **only** `model_invocable`. The backlog keys `cockpit_max_lines` / `staleness_days` and the SessionStart-hook idea are explicitly **out of scope** (YAGNI — defer until a real need appears). `Layout` version stays hard-coded (protocol contract, never per-project).

**Affected files (map):**
- `skills/landing/SKILL.md` · `skills/preflight/SKILL.md` · `skills/walkaround/SKILL.md` · `skills/emit-agents-md/SKILL.md` — delete hard switch, add gate.
- `skills/preflight/templates.md` (`§ rules.md` schema) · `skills/preflight/protocol.md` (toggle enumeration) · `scaffolds/full/flightdeck/rules.md` (new key + comment) — define the new toggle.
- `README.md` · `README.zh.md` (line ~272) — rewrite the "Every command carries `disable-model-invocation: true`" sentence.
- `adapters/{claude,gemini,codex,cursor}/README.md` — record the per-platform call-source mode + note the gate ships via shared body.

---

## Task 1: Spike — per-platform call-source detectability

The gate needs to let an **explicit user `/flightdeck:<ritual>`** through while refusing a silent **model self-invoke**. Whether a platform lets the skill body tell these apart decides "formal mode" (user slash always allowed) vs "degraded mode" (manual-only unless opted in, even for user slash). **This fork affects only adapter documentation — the gate text in Task 3 is written to degrade gracefully and is identical either way.** This task records the per-platform mode so users know what to expect.

**Files:**
- Modify: `adapters/claude/README.md`, `adapters/gemini/README.md`, `adapters/codex/README.md`, `adapters/cursor/README.md` (add a "Call-source detection" note each)

- [ ] **Step 1: Record the Claude Code signal (already observed)**

In Claude Code, a user-typed slash injects a `<command-name>/flightdeck:<ritual></command-name>` (and `<command-message>`) marker into the turn; a model self-invoke via the Skill tool does **not** (it surfaces only a "Launching skill:" tool result). So Claude Code = **formal mode**: the gate's "explicit user slash" branch is detectable. Add to `adapters/claude/README.md` under a new `## Call-source detection (model_invocable gate)` section:

```markdown
## Call-source detection (model_invocable gate)

**Mode: formal.** Claude Code injects a `<command-name>/flightdeck:<ritual></command-name>`
marker when the user types the slash, and omits it on a model self-invoke (Skill tool).
The Step-0 gate keys off this marker: explicit user invocations are always allowed;
model self-invocation is allowed only when the ritual is listed in `rules.md`
`model_invocable`. Default (`model_invocable: []`) ⇒ identical to the old
`disable-model-invocation: true`.
```

- [ ] **Step 2: Investigate Gemini / Codex / Cursor**

For each of the three, check the adapter manifest + any available platform docs for (a) a per-skill manual-only switch (there is none — confirm) and (b) whether a user-vs-model call-source signal reaches the skill body. Treat "unknown / not exposed" as **degraded mode**. Add to each of `adapters/gemini/README.md`, `adapters/codex/README.md`, `adapters/cursor/README.md`:

```markdown
## Call-source detection (model_invocable gate)

**Mode: degraded (until verified).** This platform's manifest carries no per-skill
manual-only switch — the `disable-model-invocation` field is Claude-Code-only — so the
soft gate ships via the shared `SKILL.md` body. Whether this platform lets the skill body
distinguish a user invocation from a model self-invoke is **unverified**; until confirmed,
the gate runs degraded: a ritual NOT in `rules.md` `model_invocable` is treated as
manual-only and will prompt even on an explicit user invocation. Opt in per-project with
`model_invocable: [<ritual>]`. Flip this note to "formal" with a transcript when verified.
```

- [ ] **Step 3: Commit**

```bash
git add adapters/claude/README.md adapters/gemini/README.md adapters/codex/README.md adapters/cursor/README.md
git commit -m "docs(adapters): record per-platform call-source mode for model_invocable gate"
```

---

## Task 2: Define the `model_invocable` toggle (schema + scaffold + protocol)

Define the new key everywhere the toggle set is documented, **before** any skill references it.

**Files:**
- Modify: `skills/preflight/templates.md` (`§ rules.md`)
- Modify: `scaffolds/full/flightdeck/rules.md`
- Modify: `skills/preflight/protocol.md:13`
- Modify: `skills/preflight/folder-semantics.md:87`

- [ ] **Step 1: Add the key to the scaffold `rules.md`**

In `scaffolds/full/flightdeck/rules.md`, add the new key to the frontmatter (after `disabled_gates`):

```yaml
disabled_gates: []        # e.g. [debrief-disposition]
model_invocable: []       # rituals the model may self-invoke; [] = all manual (/flightdeck:<x> only). e.g. [landing]
```

- [ ] **Step 2: Add the key to the `templates.md` rules.md template + table**

In `skills/preflight/templates.md`, add the same frontmatter line to the `## rules.md` code template, then add a row to the toggle table and update the "closed set" sentence.

Code template — add after `disabled_gates: []`:

```markdown
model_invocable: []       # rituals the model may self-invoke; [] = all manual. e.g. [landing]
```

Table — add this row after the `disabled_gates` row:

```markdown
  | `model_invocable` | list | `[]` | Rituals (`landing`/`preflight`/`walkaround`/`emit-agents-md`) the model may self-invoke via the skill tool. `[]` = all manual (explicit `/flightdeck:<x>` only). Each ritual's Step-0 gate enforces it. |
```

Sentence — change line 26 from:

```markdown
- **Closed toggle set** — only these four keys are honored. An unknown key is ignored with a one-line warning (typos must not silently change behavior):
```

to:

```markdown
- **Closed toggle set** — only these five keys are honored. An unknown key is ignored with a one-line warning (typos must not silently change behavior):
```

- [ ] **Step 3: Add the toggle to `protocol.md` enumeration**

In `skills/preflight/protocol.md:13`, change:

```markdown
Toggles: `git` · `emit_agents_md` · `disabled_folders` · `disabled_gates`. Full schema + degradation rules: [templates.md § rules.md](templates.md#rulesmd).
```

to:

```markdown
Toggles: `git` · `emit_agents_md` · `disabled_folders` · `disabled_gates` · `model_invocable`. Full schema + degradation rules: [templates.md § rules.md](templates.md#rulesmd).
```

- [ ] **Step 4: Sync the toggle enumeration in `folder-semantics.md`**

In `skills/preflight/folder-semantics.md:87`, change the toggle list from:

```markdown
Read first by every entry skill. Carries a closed set of toggles (`git`, `emit_agents_md`, `disabled_folders`, `disabled_gates`) plus free-prose house rules. Absent = defaults (git on, emit on, all folders active). Full schema: [templates.md § rules.md](templates.md#rulesmd).
```

to:

```markdown
Read first by every entry skill. Carries a closed set of toggles (`git`, `emit_agents_md`, `disabled_folders`, `disabled_gates`, `model_invocable`) plus free-prose house rules. Absent = defaults (git on, emit on, all folders active, all rituals manual). Full schema: [templates.md § rules.md](templates.md#rulesmd).
```

- [ ] **Step 5: Verify the key is defined consistently**

Run: `git grep -n "model_invocable" -- skills/ scaffolds/`
Expected: matches in `scaffolds/full/flightdeck/rules.md`, `skills/preflight/templates.md` (template line + table row), `skills/preflight/protocol.md`, and `skills/preflight/folder-semantics.md`. No skill body references yet (those come in Task 3).

- [ ] **Step 6: Commit**

```bash
git add skills/preflight/templates.md skills/preflight/protocol.md skills/preflight/folder-semantics.md scaffolds/full/flightdeck/rules.md
git commit -m "feat(rules): add model_invocable toggle to rules.md schema, scaffold, protocol, folder-semantics"
```

---

## Task 3: Remove the hard switch + add the Step-0 gate to all four rituals

Delete `disable-model-invocation: true` from each `SKILL.md` frontmatter and insert the identical gate at the very top of each ritual's checklist (right where it already reads `rules.md`). The gate text is **one shared block**, substituting `<ritual>` per file.

**The canonical gate block** (substitute `<ritual>` = `landing` / `preflight` / `walkaround` / `emit-agents-md`):

```markdown
## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` and look at its `model_invocable` list (absent key or `[]` = empty).

- If **`<ritual>` is in `model_invocable`** → allowed; continue this ritual normally.
- Else (`<ritual>` not listed):
  - If you can tell this run was an **explicit user `/flightdeck:<ritual>`** invocation (e.g. the platform injected a `<command-name>` marker for it) → allowed; continue.
  - Otherwise — you reached this skill by **model self-invocation** (skill tool), **or you cannot tell the call source** → **STOP immediately.** Report: "`<ritual>` is manual-only in this project. To let the model self-invoke it, add `model_invocable: [<ritual>]` to `flightdeck/rules.md`." Run no further step.

This gate defaults to manual-only: with no `model_invocable` key, behavior is identical to the former `disable-model-invocation: true`. (Tool-agnostic — ships to every platform via this body. See the adapter READMEs for per-platform formal/degraded mode.)
```

**Files:**
- Modify: `skills/landing/SKILL.md` · `skills/preflight/SKILL.md` · `skills/walkaround/SKILL.md` · `skills/emit-agents-md/SKILL.md`

- [ ] **Step 1: `skills/emit-agents-md/SKILL.md`** — delete the `disable-model-invocation: true` frontmatter line (line 4). Then insert the gate block (with `<ritual>` = `emit-agents-md`) immediately **above** the existing `### Step 0: Read \`flightdeck/rules.md\``. Renumber nothing — the existing "Step 0" can stay; the gate is the new pre-step. To avoid two "Step 0"s, rename the existing `### Step 0: Read \`flightdeck/rules.md\`` to `### Step 0a: Apply \`flightdeck/rules.md\` toggles` and title the gate `## Step 0 — model-invocation gate (run before any other step)`.

- [ ] **Step 2: `skills/landing/SKILL.md`** — delete `disable-model-invocation: true` (line 3). Insert the gate block (`<ritual>` = `landing`) at the very top of the checklist, immediately before the existing `0. **Read \`flightdeck/rules.md\`...** ` item.

- [ ] **Step 3: `skills/preflight/SKILL.md`** — delete `disable-model-invocation: true` (line 3). Insert the gate block (`<ritual>` = `preflight`) immediately before "## Run this checklist exactly" / step 0 of that checklist. Note preflight's own "Branch-0 — deck existence" must still run first **within** the ritual; the model-invocation gate is the outer guard that decides whether the ritual runs at all, so it precedes Branch-0.

- [ ] **Step 4: `skills/walkaround/SKILL.md`** — delete `disable-model-invocation: true` (line 3). Insert the gate block (`<ritual>` = `walkaround`) at the very top of its checklist, alongside its existing `rules.md` read.

- [ ] **Step 5: Verify no hard switch remains and four gates exist**

Run: `git grep -n "disable-model-invocation" -- skills/`
Expected: **no matches** (the field is gone from all four active skills; historical mentions in `flightdeck/landed/` and `CHANGELOG.md` are out of scope and untouched).

Run: `git grep -c "model-invocation gate" -- skills/`
Expected: one match in each of the four `SKILL.md` files.

- [ ] **Step 6: Commit**

```bash
git add skills/landing/SKILL.md skills/preflight/SKILL.md skills/walkaround/SKILL.md skills/emit-agents-md/SKILL.md
git commit -m "feat(skills): replace disable-model-invocation hard switch with rules.md model_invocable gate"
```

---

## Task 4: Rewrite the README mechanism sentences

`README.md:272` and `README.zh.md:272` currently claim every command carries the hard switch. Rewrite to the new soft-gate mechanism.

**Files:**
- Modify: `README.md:272` · `README.zh.md:272`

- [ ] **Step 1: `README.md`** — replace line 272:

From:
```markdown
Every command carries `disable-model-invocation: true` — they fire only on an explicit slash, never auto-triggered from conversation context. Nothing loads on session start.
```
To:
```markdown
By default the commands fire only on an explicit slash, never auto-triggered from conversation context, and nothing loads on session start. This is now a per-project soft gate: each ritual checks `flightdeck/rules.md`'s `model_invocable` list (default `[]` = all manual). Opt a ritual into model self-invocation with e.g. `model_invocable: [landing]`.
```

- [ ] **Step 2: `README.zh.md`** — replace line 272:

From:
```markdown
所有命令都带 `disable-model-invocation: true` —— 只在用户显式打 slash 时触发；会话开始不加载任何东西。
```
To:
```markdown
默认情况下，命令只在用户显式打 slash 时触发，不会从对话上下文自动触发，会话开始也不加载任何东西。这现在是一个 per-project 软门栓：每个仪式读 `flightdeck/rules.md` 的 `model_invocable` 列表（默认 `[]` = 全部手动）。要允许某仪式被模型自调，写如 `model_invocable: [landing]`。
```

- [ ] **Step 3: Verify**

Run: `git grep -n "disable-model-invocation" -- README.md README.zh.md`
Expected: **no matches**.

- [ ] **Step 4: Commit**

```bash
git add README.md README.zh.md
git commit -m "docs(readme): describe model_invocable soft gate (replaces disable-model-invocation prose)"
```

---

## Task 5: Final consistency sweep + acceptance check + install reminder

Run the spec's `§ 验证` acceptance criteria end-to-end and confirm nothing dangling.

**Files:** none modified (verification only), except an optional one-line note if a gap is found.

- [ ] **Step 1: No stray hard switch in active surface**

Run: `git grep -n "disable-model-invocation" -- skills/ README.md README.zh.md scaffolds/ adapters/`
Expected: **no matches** anywhere in the active surface.

- [ ] **Step 2: Toggle defined in all four schema homes**

Run: `git grep -l "model_invocable" -- skills/preflight/templates.md skills/preflight/protocol.md skills/preflight/folder-semantics.md scaffolds/full/flightdeck/rules.md`
Expected: all four paths listed.

- [ ] **Step 3: Behavioral smoke-check — default = old behavior**

In a scratch project (or this repo) with no `model_invocable` key in `rules.md`: attempt a **model self-invoke** of `landing` via the skill tool. Expected: the Step-0 gate STOPS and prints the "manual-only … add `model_invocable: [landing]`" message. Then type the explicit `/flightdeck:landing`. Expected (Claude Code / formal mode): the gate's user-slash branch allows it and the ritual proceeds.

- [ ] **Step 4: Behavioral smoke-check — opt-in works**

Set `model_invocable: [landing]` in `rules.md`. Attempt a model self-invoke of `landing`. Expected: gate allows it. Attempt a model self-invoke of `preflight` (not listed). Expected: gate STOPS with the preflight manual-only message. This confirms per-ritual granularity.

- [ ] **Step 5: Install-cache reminder**

Confirm/record in the commit message that source-repo edits do **not** take effect for users until the **plugin-cache copy is reinstalled/synced** (marketplace install path). This is a release note, not a code change.

- [ ] **Step 6: Final commit (if Step 3/4 surfaced a fix; else skip)**

```bash
git add -A
git commit -m "chore(model_invocable): consistency sweep + acceptance verification notes"
```

---

## Notes for the executor

- **Source-discrimination is the one genuine unknown** but it does **not** fork the gate text — the gate is written to allow explicit user invocation when detectable and degrade to manual-only-unless-opted-in when not. Task 1 only records which mode each platform is in.
- **Do not** touch `flightdeck/landed/**` or `CHANGELOG.md` historical mentions of `disable-model-invocation` — they are an accurate record of the old design.
- **Do not** add `cockpit_max_lines` / `staleness_days` — explicitly deferred backlog.
- This plan's sibling, `status-lifecycle-skill` (the 5th ritual), **depends on this one landing first** — it reuses this exact gate and the per-platform mode decided in Task 1. Do not start it until this plan is landed.
