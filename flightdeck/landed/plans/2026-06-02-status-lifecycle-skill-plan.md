---
status: done
implements: specs/2026-06-02-status-lifecycle-skill-design.md
---

# Status-Lifecycle Skill (`flightdeck:status`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 5th flightdeck ritual `skills/status/SKILL.md` — a high-frequency, model-invocable skill that auto-flips a single artifact's `status:` frontmatter (and its INDEX row) at lifecycle moments, gated by two orthogonal rules.md toggles.

**Architecture:** Reuse the landed `model_invocable` gate (layer 1: may the model self-invoke `status`). Add one new rules.md key `status_auto` (layer 2: which *optional* transitions fire — `start`, `land`; the two reliable transitions are always-on). Extract the land procedure into a single shared `## Land Routine` anchor that both `landing` and `status` call (DRY). The skill is forward-only and never touches cockpit/commit.

**Tech Stack:** Plain Markdown skill files + YAML frontmatter. No build/test runner — "tests" = `git grep` consistency checks + desk-checks of skill prose; live behavioral checks are deferred to a plugin-cache reinstall (documented).

**Scope:** Only this skill + its config + the land-routine extraction + a small preflight wording check. **Out of scope:** wiring non-preflight rituals into `GEMINI.md` (pre-existing gap — landing/walkaround/emit aren't there either); backlog keys `cockpit_max_lines`/`staleness_days`.

**Affected files (map):**
- `skills/preflight/exit-ritual.md` — extract `## Land Routine` anchor; repoint Step 3a.
- `skills/preflight/templates.md` · `protocol.md` · `folder-semantics.md` · `scaffolds/full/flightdeck/rules.md` — define `status_auto` (6th key) + register `status` as a ritual / model_invocable value.
- `skills/status/SKILL.md` — **new** skill (the core).
- `skills/preflight/SKILL.md` — preflight fallback: confirm done-but-unlanded covers all folders.
- `README.md` · `README.zh.md` — 5th ritual + lifecycle section.
- `adapters/{claude,gemini,codex,cursor}/README.md` — note `status` via model_invocable; document GEMINI.md gap.

---

## Task 1: Extract the shared `## Land Routine` anchor (DRY foundation)

The spec's hard contract: "single implementation, single source of truth; `landing` and `status` are two invocation paths." Today the land steps are inline in `exit-ritual.md` Step 3a. Extract them into a referenceable anchor first, so Task 3 can point at it.

**Files:**
- Modify: `skills/preflight/exit-ritual.md` (Step 3a lines ~79-82; add `## Land Routine` before `## See also`)

- [ ] **Step 1: Add the `## Land Routine` section**

Insert this section immediately before the `## See also` line at the end of `skills/preflight/exit-ritual.md`:

```markdown
## Land Routine

The single source of truth for landing an artifact. Both `landing` (Step 3a above) and the `status` skill (`skills/status/SKILL.md`) MUST call this — do not reimplement it anywhere.

Given a `done` (or `scrapped`) artifact at `<folder>/<file>`:

1. Move it to `landed/<folder>/<file>`, mirroring source structure (e.g. `specs/foo.md → landed/specs/foo.md`). Create `landed/<folder>/` if absent.
2. Remove its row from `<folder>/INDEX.md`'s `<!-- AUTO -->` region, then recompute that folder's count line in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. No other folder is touched.
3. When `rules.md` sets `git: false`, append one line to `landed/HISTORY.md` (`YYYY-MM-DD — <what landed>; next: <pointer>`, newest first).

**There is a single implementation and a single source of truth. `landing` and `status` are merely two invocation paths.**
```

- [ ] **Step 2: Repoint Step 3a at the anchor**

In `skills/preflight/exit-ritual.md`, replace the Step 3a land lines:

```
         For done or scrapped artifacts, offer to land them:
         move to landed/ mirroring source structure
         (e.g. specs/foo.md → landed/specs/foo.md).
         Append a line to landed/HISTORY.md when git: false.
```

with:

```
         For done or scrapped artifacts, offer to land them via the
         single shared Land Routine (see "## Land Routine" below) —
         do not inline the move/INDEX/HISTORY steps here.
```

- [ ] **Step 3: Verify the anchor exists and is single-source**

Run: `git grep -n "## Land Routine" -- skills/preflight/exit-ritual.md`
Expected: one match. And `git grep -n "mirroring source structure" -- skills/preflight/` returns only the Land Routine occurrence (Step 3a no longer inlines it).

- [ ] **Step 4: Commit**

```bash
git add skills/preflight/exit-ritual.md
git commit -m "refactor(exit-ritual): extract shared Land Routine anchor (landing + status call one routine)"
```

---

## Task 2: Define `status_auto` toggle + register the `status` ritual

Add the 6th rules.md key in all schema homes, and add `status` to the `model_invocable` legal values + protocol ritual enumeration.

**Files:**
- Modify: `scaffolds/full/flightdeck/rules.md` · `skills/preflight/templates.md` · `skills/preflight/protocol.md` · `skills/preflight/folder-semantics.md`

- [ ] **Step 1: Scaffold `rules.md` — add the key**

In `scaffolds/full/flightdeck/rules.md`, add after the `model_invocable` line:

```yaml
status_auto: []           # optional status transitions the status skill may auto-apply; [] = none (core create→pending / finish→awaiting-review still auto). add `start` / `land`.
```

- [ ] **Step 2: `templates.md` — template line + table row + key count**

In `skills/preflight/templates.md`, add to the `## rules.md` code template (after the `model_invocable` line):

```markdown
model_invocable: []       # rituals the model may self-invoke; [] = all manual. e.g. [landing]
status_auto: []           # optional status transitions; [] = none. add `start` (→active) / `land` (done+land)
```

Change the closed-set sentence from "these five keys" to:

```markdown
- **Closed toggle set** — only these six keys are honored. An unknown key is ignored with a one-line warning (typos must not silently change behavior):
```

Add this row after the `model_invocable` table row:

```markdown
  | `status_auto` | list | `[]` | Optional lifecycle transitions the `status` skill may auto-apply once invoked. `[]` = none; the two core transitions (create→pending, finish→awaiting-review) are always automatic and are NOT in this list. Members: `start` (→active), `land` (done + confirm-gated land). |
```

Also update the `model_invocable` table row's example to mention `status` is a legal value (change "Rituals (`landing`/`preflight`/`walkaround`/`emit-agents-md`)" to include status):

```markdown
  | `model_invocable` | list | `[]` | Rituals (`landing`/`preflight`/`walkaround`/`emit-agents-md`/`status`) the model may self-invoke via the skill tool. `[]` = all manual (explicit `/flightdeck:<x>` only). Each ritual's Step-0 gate enforces it. |
```

- [ ] **Step 3: `protocol.md` — toggle enumeration + ritual list**

In `skills/preflight/protocol.md`, change the Toggles line to add `status_auto`:

```markdown
Toggles: `git` · `emit_agents_md` · `disabled_folders` · `disabled_gates` · `model_invocable` · `status_auto`. Full schema + degradation rules: [templates.md § rules.md](templates.md#rulesmd).
```

And update line 11's "read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`)" to add `status`:

```markdown
`flightdeck/rules.md` is an **optional** project-config file read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`, `status`). It carries a closed set of structured toggles plus free-prose house rules. Absent file = defaults (git on, emit on, all folders/gates active, all rituals manual).
```

- [ ] **Step 4: `folder-semantics.md` — toggle enumeration**

In `skills/preflight/folder-semantics.md:87`, change the toggle list to add `status_auto`:

```markdown
Read first by every entry skill. Carries a closed set of toggles (`git`, `emit_agents_md`, `disabled_folders`, `disabled_gates`, `model_invocable`, `status_auto`) plus free-prose house rules. Absent = defaults (git on, emit on, all folders active, all rituals manual). Full schema: [templates.md § rules.md](templates.md#rulesmd).
```

- [ ] **Step 5: Verify all homes carry the key + six-keys count**

Run: `git grep -l "status_auto" -- skills/preflight/templates.md skills/preflight/protocol.md skills/preflight/folder-semantics.md scaffolds/full/flightdeck/rules.md`
Expected: all four paths listed.
Run: `git grep -n "these six keys" -- skills/preflight/templates.md`
Expected: one match.

- [ ] **Step 6: Commit**

```bash
git add skills/preflight/templates.md skills/preflight/protocol.md skills/preflight/folder-semantics.md scaffolds/full/flightdeck/rules.md
git commit -m "feat(rules): add status_auto toggle (6th key) + register status ritual"
```

---

## Task 3: Create `skills/status/SKILL.md` (the core)

The new skill. Self-contained markdown the AI follows. No `disable-model-invocation`; reuses the landed gate; encodes artifact-confidence, the candidate description, forward-only state machine, INDEX sync, and done/land via the shared Land Routine.

**Files:**
- Create: `skills/status/SKILL.md`

- [ ] **Step 1: Write the full `skills/status/SKILL.md`**

Create `skills/status/SKILL.md` with exactly this content:

````markdown
---
name: status
description: Keep a flightdeck artifact's lifecycle status fresh and its folder INDEX row in sync. Identify the target artifact with high confidence (currently-edited file → current executing-plan → most-recent unambiguous creation); if none is unambiguous, do nothing. Always-auto (when self-invoked and `status` is in rules.md `model_invocable`): (1) right after writing a new file into `flightdeck/{specs,plans,sketches,…}` set `pending` (sketches → `active`); (2) in the reasoning moment just before a user-requested commit that finishes a plan/spec's work, set `awaiting-review`. Opt-in (only if the member is in rules.md `status_auto`): `start` → when beginning execution of a plan set `active`; `land` → when the user approves/signs off set `done`, then ask before archiving. Never fires on ordinary edits (typo/wording fixes); forward-only, never downgrades. Triggered automatically or by `/flightdeck:status`.
---

# Flightdeck Status — lifecycle auto-flip

The only **high-frequency, lightweight, model-invocable** flightdeck ritual. It keeps a single artifact's lifecycle `status:` honest mid-session, so state doesn't drift and the next `preflight` reads truth from the INDEX. It is complementary to `landing`, not a replacement: `landing` is the low-frequency batch wrap-up; `status` is the in-flight keep-fresh.

It **only** edits one artifact's frontmatter `status:` + that artifact's row in its folder `INDEX.md` (+ that folder's count in the root INDEX). When `land` is enabled it additionally archives via the shared Land Routine (confirm-gated). It does **not** touch `cockpit.md`, does **not** commit, does **not** run length / AGENTS.md regeneration.

## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` (absent file ⇒ treat every key as empty). Look at its `model_invocable` list (absent key or `[]` = empty).

- If **`status` is in `model_invocable`** → allowed; continue this ritual normally.
- Else (`status` not listed):
  - If you can tell this run was an **explicit user `/flightdeck:status`** invocation (e.g. the platform injected a `<command-name>` marker for it) → allowed; continue.
  - Otherwise — you reached this skill by **model self-invocation** (skill tool), **or you cannot tell the call source** → **STOP immediately.** Report: "`status` is manual-only in this project. To let the model self-invoke it, add `model_invocable: [status]` to `flightdeck/rules.md`." Run no further step.

This gate defaults to manual-only: with no `model_invocable` key (or no `rules.md`), behavior matches the former `disable-model-invocation: true`. Manual `/flightdeck:status` always bypasses this gate (it only restricts model self-invoke).

## Step 1 — read config

From the same `flightdeck/rules.md` read `status_auto` (a list; absent key, `[]`, or no `rules.md` ⇒ empty = no optional transitions). The two **core** transitions below run regardless of `status_auto`; the **opt-in** transitions run only if their member is present.

## Step 2 — identify the target artifact (confidence rule)

Every auto-flip needs to know **which** artifact. Resolve by priority:

1. The flightdeck artifact **being written/edited this turn**.
2. The plan **currently being executed** (executing-plans context).
3. The **most recently created** artifact this session, if unambiguous.
4. None uniquely determined → **do nothing**.

**If the target artifact cannot be identified with high confidence, status MUST NOT perform an automatic transition.** (Missing a flip is recoverable by `landing`/`preflight`; flipping the wrong artifact is hard to detect and forward-only cannot undo it.)

## Step 3 — transitions

| Trigger | Target | Class | Auto? |
|---|---|---|---|
| Wrote a **new artifact** into `flightdeck/{specs,plans,sketches,…}` | `pending` (sketches → `active`) | core | always |
| Bound work **finished / just before a user-requested commit** | `awaiting-review` | core | always |
| **Began executing** a plan | `active` | opt-in `status_auto:[start]` | only if enabled |
| User **approved / signed off** | `done` → land | opt-in `status_auto:[land]` | only if enabled; `done` auto, land confirm-gated |

- Fire only at **new-artifact writes** and **clear status-semantic moments** — never on ordinary edits (typo/wording fixes).
- For trigger #4, if `land` is **not** in `status_auto`, do nothing (leave it to `landing`) — do not set `done` either.

## Step 4 — forward-only state machine

- Chain: `pending → active → awaiting-review → done`. **Direct jumps allowed**: since `active` is opt-in, `finish` commonly does `pending → awaiting-review` skipping `active` — this is legal.
- **Forward-only / idempotent**: if the target status equals the current one or is *earlier* in the chain → **no-op** (never downgrade, never error). E.g. user manually set a new file to `active`; the create→pending trigger is a no-op.
- **sketches**: legal statuses are `active`/`scrapped` only; create sets `active`; sketches never enter the awaiting-review/done chain.
- `blocked` / `scrapped` are **explicit human** actions — never auto-set them.

## Step 5 — sync the INDEX

After flipping frontmatter, reuse landing's single-folder regeneration (see [exit-ritual.md § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules)):

1. Regenerate the affected folder's `INDEX.md` `<!-- AUTO -->` region in full (folders hold few files — cheap and deterministic; avoids fragile in-place +1/−1 count math).
2. Recompute **only that folder's** count line in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. Touch no other folder.

## Step 6 — done + land (only when `status_auto` includes `land`)

When the user approves and `land` is enabled:

1. **Set `done` automatically** — "review passed" is an asserted fact; do not ask to confirm `done` itself.
2. **Ask to confirm the archive** (destructive: moves files). On confirm → run the shared **[Land Routine](../preflight/exit-ritual.md#land-routine)** (do not reimplement it). On decline → leave the artifact at `done` **but un-archived** (done-but-unlanded); `preflight`/`landing` will surface and offer to land it later. **Never** revert `done` because the land confirm was declined.

## Don't do

- Don't touch `cockpit.md` (no `Last updated` bump, no sections) — status visibility lives in folder INDEX, not cockpit.
- Don't commit, don't run length checks or AGENTS.md regeneration.
- Don't downgrade a status; don't auto-set `blocked`/`scrapped`.
- Don't reimplement the land steps — call the shared Land Routine.
- Don't act when the target artifact is ambiguous.
````

- [ ] **Step 2: Verify the skill is well-formed and discoverable**

Run: `git grep -n "name: status" -- skills/status/SKILL.md`
Expected: one match (frontmatter present).
Run: `git grep -c "disable-model-invocation" -- skills/status/SKILL.md`
Expected: `0` (the new skill never carries the hard switch).
Confirm `.claude-plugin/plugin.json` still has `"skills": "./skills/"` (directory-based discovery — no manifest edit needed):
Run: `git grep -n "\"skills\"" -- .claude-plugin/plugin.json`
Expected: `"skills": "./skills/"`.

- [ ] **Step 3: Commit**

```bash
git add skills/status/SKILL.md
git commit -m "feat(status): add 5th ritual flightdeck:status (lifecycle auto-flip, model_invocable + status_auto)"
```

---

## Task 4: preflight done-but-unlanded awareness

The spec relies on `preflight` surfacing a `done`-but-unlanded artifact. preflight's fallback already offers to land a `done`-but-unlanded **plan**; confirm it isn't plan-only.

**Files:**
- Modify: `skills/preflight/SKILL.md` (fallback section)

- [ ] **Step 1: Inspect the current wording**

Run: `git grep -n "done.-but-unlanded\|unlanded\|done.-but" -- skills/preflight/SKILL.md`
Read the matched fallback bullet (it currently reads, under "Fallback when Next session is empty": "a `done`-but-unlanded plan → offer to land it").

- [ ] **Step 2: Generalize the wording to all folders**

In `skills/preflight/SKILL.md`, change the plans/ fallback bullet:

```markdown
1. `flightdeck/plans/` — surface `pending` / `blocked` / `active` plans (read `plans/INDEX.md`), most actionable first; a `done`-but-unlanded plan → offer to land it.
```

to add a general note right after that numbered fallback list (so it covers specs etc., which `status` can now leave done-but-unlanded):

```markdown
> **Done-but-unlanded (any folder):** an artifact whose `status: done` but which still sits in its source folder (not yet under `landed/`) is *done-but-unlanded* — the `status` skill produces these when its `land` confirm is declined. Offer to land it via the [Land Routine](exit-ritual.md#land-routine). This applies to `specs/`, `plans/`, and any workflow folder, not just plans.
```

- [ ] **Step 3: Verify**

Run: `git grep -n "Done-but-unlanded (any folder)" -- skills/preflight/SKILL.md`
Expected: one match.

- [ ] **Step 4: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "docs(preflight): surface done-but-unlanded artifacts in any folder (status land-decline)"
```

---

## Task 5: README (EN + ZH) — 5th ritual + lifecycle section

**Files:**
- Modify: `README.md` · `README.zh.md` (command table ~line 270 + the mechanism paragraph ~272)

- [ ] **Step 1: `README.md` — add the command row + lifecycle note**

In `README.md`, add a row to the command table after the `emit-agents-md` row:

```markdown
| `/flightdeck:status` | Auto-flip one artifact's lifecycle `status:` + its INDEX row (model-invocable; opt-in via `rules.md`). |
```

Then append after the existing soft-gate paragraph (the `model_invocable` one near line 272):

```markdown
`flightdeck:status` is the only model-invocable, high-frequency ritual: it keeps an artifact's status fresh mid-session. Enable self-invocation with `model_invocable: [status]`; choose which optional transitions auto-fire with `status_auto: [start, land]` (default: only `create→pending` and `finish→awaiting-review` are automatic).
```

- [ ] **Step 2: `README.zh.md` — same, translated**

Add the command-table row after the `emit-agents-md` row:

```markdown
| `/flightdeck:status` | 自动翻转单个 artifact 的生命周期 `status:` + 其 INDEX 行（model-invocable；经 `rules.md` opt-in）。 |
```

Append after the ZH soft-gate paragraph:

```markdown
`flightdeck:status` 是唯一可被模型自调的高频仪式：会话中途保持 artifact 状态新鲜。用 `model_invocable: [status]` 允许自调；用 `status_auto: [start, land]` 选择哪些可选转换自动触发（默认只有 `create→pending` 与 `finish→awaiting-review` 自动）。
```

- [ ] **Step 3: Verify**

Run: `git grep -n "flightdeck:status" -- README.md README.zh.md`
Expected: one match in each.

- [ ] **Step 4: Commit**

```bash
git add README.md README.zh.md
git commit -m "docs(readme): document the status ritual + two-layer config (EN + ZH)"
```

---

## Task 6: Cross-platform adapter notes

The gate ships via the shared `SKILL.md` body (Claude auto-discovers the new folder). Document `status`'s posture per platform; note the GEMINI.md gap explicitly so it isn't mistaken for an oversight.

**Files:**
- Modify: `adapters/claude/README.md` · `adapters/gemini/README.md`

- [ ] **Step 1: `adapters/claude/README.md` — note status is auto-discovered + gated**

Append to the `## Call-source detection (model_invocable gate)` section in `adapters/claude/README.md`:

```markdown

The 5th ritual `status` is auto-discovered from `skills/status/` (directory-based manifest) and goes through the same gate: it self-invokes only when `model_invocable` lists `status`. No manifest edit is needed to add it.
```

- [ ] **Step 2: `adapters/gemini/README.md` — document the GEMINI.md scope gap**

Append to `adapters/gemini/README.md` (under its existing notes):

```markdown
## Ritual coverage (GEMINI.md)

`GEMINI.md` `@`-includes only the **preflight** bundle (SKILL.md + protocol/folder-semantics/templates/exit-ritual). The non-preflight rituals — `landing`, `walkaround`, `emit-agents-md`, and now `status` — are **not** individually `@`-included, so their skill bodies aren't loaded on Gemini. This is a pre-existing, untested gap (the manifest is "behaviorally untested"), not specific to `status`. Wiring all rituals into `GEMINI.md` is tracked separately; `status` inherits the same posture as its siblings.
```

- [ ] **Step 3: Verify**

Run: `git grep -n "Ritual coverage (GEMINI.md)" -- adapters/gemini/README.md`
Expected: one match.

- [ ] **Step 4: Commit**

```bash
git add adapters/claude/README.md adapters/gemini/README.md
git commit -m "docs(adapters): note status auto-discovery (claude) + GEMINI.md ritual-coverage gap"
```

---

## Task 7: Consistency sweep + acceptance + install reminder

**Files:** none modified (verification only).

- [ ] **Step 1: Toggle + ritual registration sweep**

Run: `git grep -l "status_auto" -- skills/ scaffolds/`
Expected: `templates.md`, `protocol.md`, `folder-semantics.md`, `scaffolds/full/flightdeck/rules.md`, and `skills/status/SKILL.md`.
Run: `git grep -c "## Land Routine" -- skills/preflight/exit-ritual.md`
Expected: `1` (single source of truth).
Run: `git grep -n "Land Routine" -- skills/status/SKILL.md skills/preflight/SKILL.md`
Expected: both reference the same anchor (no reimplementation).

- [ ] **Step 2: Acceptance — desk-check against spec §验证**

Read `skills/status/SKILL.md` once end-to-end and confirm each spec verification bullet maps to skill text: gate (manual-only default / manual bypass / rules absent = empty); artifact-confidence "don't act if ambiguous"; core two always-on incl. `pending→awaiting-review` direct jump; `start`/`land` opt-in; `done` auto + land confirm-gated + decline ⇒ done-but-unlanded; forward-only no-op; no cockpit bump.

- [ ] **Step 3: Behavioral smoke-check (deferred — record, don't fake)**

The running skills load from the plugin **cache**, not this source — so live invocation here would exercise the old cache, not these edits. Record that the behavioral matrix (self-invoke blocked without `model_invocable:[status]`; opt-in transitions; done-but-unlanded on land-decline) is to be run **after reinstalling the plugin from this branch**. Do not claim a behavioral pass from this session.

- [ ] **Step 4: Install-cache reminder**

Note in the final report that users must reinstall/sync the plugin-cache copy for the new ritual + `status_auto` key to take effect (marketplace install path).

---

## Notes for the executor

- **Task 1 is the DRY foundation** — do it first so Tasks 3/4 reference a real `#land-routine` anchor.
- **One land routine, two callers**: `status` and `landing` both point at `exit-ritual.md#land-routine`; never inline the move/INDEX/HISTORY steps in `status`.
- **`status_auto` passes the rules.md admission policy** (per-project / not a contract / real demand / not foldable into `model_invocable`) — it's a legitimate 6th key, not creep.
- **Don't expand `GEMINI.md`** or backlog keys — explicitly out of scope.
- **Default-safe**: with no `rules.md` (or empty keys), `status` does nothing automatically — every existing project is unaffected.
