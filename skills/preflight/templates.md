# Templates

Reusable file templates for `flightdeck/` files. Each template has a strict structure — deviation typically means the file should live in a different folder or be deleted.

> **Field semantics are canonical in [protocol.md § Frontmatter field reference](protocol.md#frontmatter-field-reference-canonical).** This file holds ready-to-paste blocks + per-template authoring rules; it does not redefine what a field *means* or which kinds require it.

---

## rules.md

```markdown
---
version: 3.0             # REQUIRED — flightdeck release this deck conforms to; drives migration detection
disabled_folders: []     # the one structured toggle: listed folders never suggested / not flagged as orphans
---

## House rules

### Project conventions

Deck-local flightdeck conventions only (e.g. "specs written in Chinese", "do not use charts/").
General project conventions (code style, "branch before committing") belong in CLAUDE.md / AGENTS.md, NOT here.

### Autonomy overrides

Omit = defaults (commit confirm · all rituals self-invocable · status_auto fully on ·
git & emit inferred from `.git` / `AGENTS.md` presence). To activate one, **delete its `<!-- -->` wrapper** — commented lines are skipped by phrase-matching:
<!-- commit without asking -->
<!-- landing: don't self-invoke; I run it manually -->
<!-- this deck doesn't use git; history in landed/HISTORY.md -->
<!-- has AGENTS.md but don't auto-regen -->
<!-- run scripts with uv run -->   <!-- runtime is any of: uv run · python3 · python · a pinned path -->
```

### Rules

- **Mandatory file** — part of the minimal 3-file contract (`rules.md` + `cockpit.md` + `landed/HISTORY.md`). Must exist and carry `version`. Omitted `disabled_folders` defaults `[]`; all behavior not pinned here resolves via [protocol § Rule resolution order](protocol.md#rule-resolution-order) (House Rules override → environment inference → built-in default).
- **`version` is deck identity, not a toggle.** It records the flightdeck release this deck conforms to; `preflight`/`walkaround` compare it against `MIGRATION.md` (`current` + `layout_need_update`) to detect migrations.
- **One structured toggle (3.0).** Only `disabled_folders` remains structured:

  | Key | Type | Default | Effect |
  | --- | --- | --- | --- |
  | `disabled_folders` | list | `[]` | Listed folders never suggested by fallback/exit classification; not flagged as orphans by `walkaround`. |

- **Everything else is inference / default / House Rules** (canonical resolution in protocol):
  - `git` → inferred from deck root `.git` presence; House Rule `this deck doesn't use git; history in landed/HISTORY.md` overrides.
  - `emit_agents_md` → `landing` auto-regen **only if** deck root already has `AGENTS.md`; explicit `/flightdeck:emit-agents-md` **always** creates. **Asymmetry**: from a no-`AGENTS.md` start, only the explicit command can bootstrap it. House Rule `has AGENTS.md but don't auto-regen` opts a deck out while keeping the file.
  - `commit` → defaults `confirm`; House Rules `commit without asking` (auto) / `don't auto-commit; leave changes for me / CI` (manual). Under no-git there is no commit regardless.
  - ritual self-invocation → defaults **on**; House Rule `<ritual>: don't self-invoke; I run it manually` restricts one.
  - `status_auto` → defaults `start` + `land` **on**; House Rule `status: don't auto <transition>` restricts one.
  - `scripts` → defaults **manual** (INDEX regen / consistency checks done by hand). House Rule `run scripts [with <runtime>]` opts into the bundled `flightdeck_index.py` fast path; the markdown path is always the valid fallback, so a runtime-less tool loses only speed. Runs code → a higher-trust action → opt-in, never on by default. See [exit-ritual § Script fast path](exit-ritual.md#script-fast-path-optional-accelerator).
- **House rules are now authoritative** (升级 from advisory): the `### Autonomy overrides` segment overrides flightdeck defaults — but stays below the project's own agent rules (**CLAUDE.md > House Rules > defaults**). General project conventions belong in CLAUDE.md, not here. House Rules internal conflicts are the user's responsibility (no auto-resolution).
- **Compatibility**: pre-3.0 keys (`git`/`emit_agents_md`/`disabled_gates`/`model_invocable`/`status_auto`/`commit_mode`) are **read and honored through 3.x**, removed at 4.0; `preflight` offers to migrate a deck still carrying them.
- **Malformed YAML or unparseable frontmatter** → warn and fall back to all defaults; never hard-fail.
- **Read first**: every entry skill reads `rules.md` before acting and resolves behavior per Rule resolution order.

---

## spec frontmatter

```markdown
---
status: idea          # idea / active / done / scrapped (idea = unstarted, no date prefix; flip to active to start)
summary: <one-line gist>     # recommended; single-line plain text — no | [ ] or newlines (use commas/dashes). Drives the INDEX row.
last_updated: YYYY-MM-DD     # recommended; auto-bumped by status/landing on a real change (not typos)
note: <one-line diagnostic>  # optional; "why it hasn't moved" (blocker / pending reason). Rendered in cockpit 进行中 + walkaround as [note: …]
supersedes: <path>           # optional; forward edge to the workflow artifact this replaces (path relative to flightdeck root)
related: [<path>, ...]       # optional; weak links — shared premise / blast-radius, NOT supersedes or implements
---
```

(An idea-stage spec usually carries only `status: idea` + `summary`; the rest are for longer-lived active specs.)

---

## plan frontmatter

```markdown
---
status: active               # idea / active / done / scrapped
summary: <one-line gist>     # recommended; single-line plain text — no | [ ] or newlines. Drives the INDEX row.
last_updated: YYYY-MM-DD     # recommended; auto-bumped by status/landing
note: <one-line diagnostic>  # optional; "why it hasn't moved". Rendered in cockpit 进行中 + walkaround as [note: …]
implements: specs/<x>.md     # optional; path relative to flightdeck root; absent → walkaround flags "orphan plan"
supersedes: <path>           # optional; forward edge to the artifact this replaces
related: [<path>, ...]       # optional; weak cross-links
---
```

---

## knowledge frontmatter — incident / checklist / chart

```markdown
---
status: active            # active / obsolete / superseded
when_to_read: <one-line trigger>
applies_to: [<tag>, ...]
last_updated: YYYY-MM-DD
# superseded only: superseded_by: <path>
# optional (incidents/checklists): skip_when: <one-line "when NOT to read this">
# incidents only: recurrences: 1   # auto-bumped at landing on a clear recurrence; renders to INDEX as `recur: N` when > 1
---
```

---

## INDEX.md — per folder

```markdown
# <folder>/ — INDEX

<!-- AUTO:<folder> -->
- [<file>](<file>) — <status> — <one-line summary>
<!-- /AUTO -->

<!-- optional hand-maintained area (grouping notes for multi-file topics); AI does not touch -->
```

For a workflow row (`specs/` `plans/`) the `<one-line summary>` is the file's `summary` frontmatter, copied verbatim (with `|` pipe-escaped) — the row is **derived from `summary`**, not hand-written; see [exit-ritual.md § INDEX regeneration](exit-ritual.md#index-regeneration--scope-rules) for the row-building rule. A file with no `summary` produces a row with the summary segment omitted. Rows in `incidents/` `checklists/` `charts/` add `when_to_read` / `applies_to`. `implements`, `supersedes`, `related`, `note` do NOT go into the INDEX. (`specs/INDEX` groups its AUTO region by status and skips `scrapped` — see [folder-semantics § specs/](folder-semantics.md#specs--designs).)

---

## INDEX.md — root (flightdeck/INDEX.md)

```markdown
# flightdeck — INDEX

<!-- AUTO:root -->
- specs/ — 5 (1 idea, 2 active, 2 done)
- plans/ — 2 (2 active)
- incidents/ — 1 active
- checklists/ — 1 active
- charts/ — 2 projects imported
<!-- /AUTO -->
```

---

## status flow (recommended, not enforced)

Status values (by kind) + the recommended transition arrows are canonical in [protocol § Status](protocol.md#status-label--recommended-flow) — not restated here.

---

## incident-report body

```markdown
# <one-line topic>

**Symptom**: How the user / test / build actually observed it. Error text verbatim.

**Root cause** (FORBIDDEN: "forgot", "careless", "didn't notice" — must be a wrong assumption / wrong model / wrong process):
I assumed X, but in reality Y.

**Lesson**: The specific next-time action. Not "be careful". Concrete behavior or check.

---

## [Case 2]   ← Appended on recurrence. DO NOT create a new file.

**Symptom**: ...
**Root cause**: ...
**Lesson**: ...
```

### Rules

- **One file per topic.** A recurrence appends `## [Case N]` (with its session date) **and** bumps the `recurrences` frontmatter counter. **Landing does this automatically** on a clear same-incident match (ambiguous → asks first); `recurrences` renders into the INDEX row as `recur: N`, so the count + the `[Case N]` dates (the promotion-gate inputs) are visible without opening the file.
- **Forbidden root causes**: "forgot", "careless", "didn't notice", "rushed". These hide the real model error.
- **Status field**:
  - `active` — still applies to the current codebase
  - `obsolete` — the underlying constraint no longer exists (framework upgraded, code removed). Keep the file as history but mark.
  - `superseded` — folded into your project agent rules. Note the upgrade: `status: superseded → project-rules §<section>`. Do not delete.
- **Promotion path**: incident reports promote in two stages — first to `checklists/` (after a 3-criterion gate at `landing`), then to project agent rules (only if the checklist is also ignored and the incident continues to recur). Full gate criteria in [protocol.md § Incident promotion gates](protocol.md#incident-promotion-gates).
- **Frontmatter `when_to_read` + `applies_to` are REQUIRED** (not optional). An incident report without them fails the routing check and is reported as a hanging task. They let AI grep for relevance without loading the full file — same pattern as skill SKILL.md `description`. Examples:
  - `when_to_read: "before designing a recursive parser"` / `applies_to: [parser, recursion, stack-depth]`
  - `when_to_read: "before adding a new migration"` / `applies_to: [migration, schema, postgres]`
  - Keep tags **short and concrete** — `[parser, recursion]` beats `[code-quality, architecture]`. Generic tags don't help AI choose.
- **Frontmatter `last_updated`**: bump on every meaningful change (Case append / status flip / advice rewrite). Lets AI judge staleness: a `last_updated` 2 years ago about a removed module is probably obsolete — promote to `status: obsolete` or delete. Lets users sort by recency when triaging.

---

## checklist body

```markdown
# <topic> checklist

## When to follow this

<2-3 line description of the situation this checklist handles>

## Steps

1. <command or check>
2. <command or check>
3. ...

## Verification

- <how to confirm each step worked>

## Common pitfalls

- <known trap and how to avoid it>
```

### Rules

- **One file per topic** (e.g. `verify.md`, `release.md`, `re-fixture.md`).
- **Frontmatter `when_to_read` + `applies_to` are REQUIRED** (not optional). A checklist without them fails the routing check — same hard-fail rule as incident reports. See [protocol.md § Frontmatter requirements](protocol.md#frontmatter-requirements-hard-fail).
- **Frontmatter `last_updated`**: bump every time the checklist content actually changes (not for typo fixes). Lets AI / users judge staleness: a build checklist last touched 2 years ago in a fast-moving project is suspect.
- **Promotion rule**: a process becomes a checklist **on the second occurrence**. First time is ad-hoc; second time is the pattern worth recording.
- **No date prefix** — checklists are stable resources, not log entries.

---

## spec body (idea stage)

```markdown
# <rough idea>

<one-line gist; flip status idea → active when it's worth starting>
```

### Rules

- An idea-stage spec (`status: idea`) is a one-liner — no date prefix, no `implements:`. Starting it = flip `status: idea → active` (auto-adds the `YYYY-MM-DD-` prefix); a fuller design body grows in once active.
- If an idea has been sitting > 6 months and no trigger has fired, consider `status: scrapped` (stays in `specs/`, excluded from INDEX). An idea that never finds its moment is not high-signal.

---

## External review feedback (no template)

There is **no debrief template** — `debriefs/` was removed. External review feedback is transient: keep the raw text in project-root `tmp/` (gitignored), then fold the **disposition** (adopt / reject / defer) into the reviewed spec's own `## 评审纪要` section. The raw feedback is discarded once dispositioned. See [folder-semantics § External review feedback](folder-semantics.md#external-review-feedback-no-folder).

---

## cockpit.md

```markdown
# Cockpit — <project>

**Last updated**: YYYY-MM-DD by <who> (<one-line state summary>)
**Active focus**: <current main thread, 5–15 words>

## 进行中

<!-- AUTO:inprogress -->
- [<spec/plan>](<path>) — <one-line summary> [note: <if present>]
<!-- /AUTO -->

## 下一步

<next concrete single action — start an idea, or advance an active artifact>

## Hanging tasks

- [ ] <open item blocking a clean landing>
```

### Rules

- **`## 进行中` is an AUTO region** — derived from every `status: active` spec/plan (same `<!-- AUTO -->` mechanism as INDEX, regenerated by `status` / `landing`). **Do not hand-edit** it; a hand edit is overwritten on the next regen. The literal marker is `<!-- AUTO:inprogress -->` … `<!-- /AUTO -->` (Phase 1's `flightdeck_index.py` emits exactly this string). Each row mirrors the INDEX row format; if a file carries `note:`, append `[note: …]`.
- **`## 下一步` is the next concrete *single* action** — AI-maintained, auto-written at landing (and on `idea→active` / a milestone). It is finer-grained than `Active focus` (the coarse session main thread): the two do not overlap. The user adjusts it by directing the AI, not by hand-editing.
- **Length cap: 80 lines hard ceiling.** Past 80, trim immediately. `## 进行中` is AUTO and usually short; piled-up `active` is itself a focus-loss signal (walkaround INFO, never blocks).
- **`Active focus` is current state**, not history.
- **Hanging tasks block landing** — resolve, or explicitly defer with a date.
- **History does not live in cockpit.** Durable record = `landed/` archive + `git log` (+ `landed/HISTORY.md` when `git: false`). A landed artifact leaves `## 进行中` automatically; it is not logged in cockpit.
- **No metric tracking duplicated elsewhere** — link to the single source.
- **No version stamp in cockpit.** The deck-conformance version lives in `rules.md` `version:`; migration detection compares it against `MIGRATION.md` (`current` + `layout_need_update`). cockpit is pure focus.

---

## landed/HISTORY.md

```markdown
# History — <project>

<!-- Add-only landing log: one line per landing, newest first. Never edit or delete past entries.
     Required when rules.md sets git: false; optional otherwise.
     Lives under landed/ — outside the routing graph; never read at session start. -->

- YYYY-MM-DD — <what landed this session>; next: <pointer to the 下一步 action>
```

### Rules

- **One line per landing**, newest first. Never edit or delete past entries (add-only). No multi-line entries — link to the archived artifact for detail.
- **Required only when `git: false`** (no commit log). Git projects may keep it but `git log` is authoritative.
- **Never read at session start** — it is reference for retrospectives / no-git staleness checks only.

---

## Cross-folder reference syntax

When one file references another, use a markdown link with a one-word hook:

```markdown
Known trap: [v2-aelayer structure](incidents/v2-aelayer-structure.md)
Procedure: [verify before commit](checklists/verify.md)
Decision: [why we chose splice over rewrite](landed/specs/2025-12-01-write-strategy.md)
```

Why this matters:
- The reader (human or AI) can jump straight to the source of truth.
- Single authoritative location — no duplication.
- When the linked file moves, the broken link is visible and fixable.

**Forbidden**: pasting facts inline that exist elsewhere ("we use splice not rewrite because..."). Link, do not copy.

---

## Spec evolution markers (optional convention)

When amending a long-lived spec — especially **backlog specs** that gain items over multiple sessions, or **specs revised after review disposition** (external feedback folded into the spec's `## 评审纪要`) — mark new / modified / removed items with prefix tags so the change history is grep-able and merge-friendly:

- **`ADDED:`** — new item or section.
- **`MODIFIED:`** — existing item changed. Note the old + new state inline if the change isn't self-evident.
- **`REMOVED:`** — item dropped. Strike-through (`~~text~~`) or comment-out rather than deleting outright, so the audit trail survives.

Example from a revised backlog spec:

```
- ADDED: B7 — cache layer with TTL on read-heavy endpoints.
- MODIFIED: B3 — switched from polling to webhook (was: 5s poll loop).
- REMOVED: ~~B5 server-side rendering~~ (rejected after benchmarks; rejected approach noted in commit log).
```

### Rules

- **Optional.** Small one-shot specs (single-session, no review round) don't need delta markers. The cost of adding them outweighs the benefit at that scale.
- **Apply only to substantive changes.** Typo fixes don't earn a marker; an item's scope shifting does.
- **REMOVED keeps history.** Strike-through preserves the audit trail; outright deletion makes it impossible to see "what we considered and rejected". The audit trail is the whole point.
- **Markers compose with `status:` frontmatter.** A spec can be `status: active` (with a `note:` blocker reason) AND have an `ADDED:` line in its body. Status applies to the artifact; markers apply to items within.
