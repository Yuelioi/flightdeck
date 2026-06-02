# Templates

Reusable file templates for `flightdeck/` files. Each template has a strict structure — deviation typically means the file should live in a different folder or be deleted.

> **Field semantics are canonical in [protocol.md § Frontmatter field reference](protocol.md#frontmatter-field-reference-canonical).** This file holds ready-to-paste blocks + per-template authoring rules; it does not redefine what a field *means* or which kinds require it.

---

## rules.md

```markdown
---
version: 2.2              # REQUIRED — flightdeck release this deck conforms to; drives migration detection (not a toggle)
git: true                 # false → skills skip all git reconcile/commit steps
emit_agents_md: true      # false → the emit-agents-md skill exits without writing
disabled_folders: []      # e.g. [charts, debriefs] → never suggested; not flagged as orphans
disabled_gates: []        # e.g. [debrief-disposition]
model_invocable: []       # rituals the model may self-invoke; [] = all manual. e.g. [landing]
status_auto: []           # optional status transitions; [] = none. add `start` (→active) / `land` (done+land)
---

## House rules

Free-prose project conventions every flightdeck skill must honor
(e.g. "never auto-commit", "specs written in Chinese", "do not create sketches/").
```

### Rules

- **Mandatory file** — part of the minimal 3-file contract (`rules.md` + `cockpit.md` + `landed/HISTORY.md`). Must exist and carry `version`. *Omitted toggle fields* still default (git on, emit on, all folders/gates active, all rituals manual) — only the file's existence + `version` are required, not every key.
- **`version` is deck identity, not a toggle.** It records the flightdeck release this deck conforms to; `preflight`/`walkaround` compare it against `MIGRATION.md` (`current` + `layout_need_update`) to detect migrations. It is NOT part of the closed toggle set and is exempt from the key-admission policy.
- **Closed toggle set** — only these six keys are honored. An unknown key is ignored with a one-line warning (typos must not silently change behavior):

  | Key | Type | Default | Effect when changed |
  | --- | --- | --- | --- |
  | `git` | bool | `true` | `false` → skip git branch/status/stash/log reconcile; never auto-commit; staleness + history use `landed/HISTORY.md`. |
  | `emit_agents_md` | bool | `true` | `false` → `emit-agents-md` refuses and reports "disabled via rules.md". |
  | `disabled_folders` | list | `[]` | Listed folders never suggested by fallback/exit classification; not flagged as orphans by `walkaround`. |
  | `disabled_gates` | list | `[]` | Named gates skipped. Known: `debrief-disposition`, `frontmatter-required`. |
  | `model_invocable` | list | `[]` | Rituals (`landing`/`preflight`/`walkaround`/`emit-agents-md`/`status`) the model may self-invoke via the skill tool. `[]` = all manual (explicit `/flightdeck:<x>` only). Each ritual's Step-0 gate enforces it. |
  | `status_auto` | list | `[]` | Optional lifecycle transitions the `status` skill may auto-apply once invoked. `[]` = none; the two core transitions (create→pending, finish→awaiting-review) are always automatic and are NOT in this list. Members: `start` (→active), `land` (done + confirm-gated land). |

- **`disabled_gates: [frontmatter-required]` is dangerous** — it makes routed files invisible to grep-routing. Warn the user when honoring it.
- **House rules are advisory prose** the AI honors, but they cannot redefine the six toggle keys.
- **Malformed YAML or unparseable frontmatter** → warn and fall back to all defaults; never hard-fail (a broken `rules.md` must not brick the entry ritual).
- **Read first**: every entry skill (`preflight`, `walkaround`, `landing`, `emit-agents-md`, `status`) reads `rules.md` before acting and branches on the toggles.

---

## spec / sketch frontmatter

```markdown
---
status: active        # spec: pending/active/awaiting-review/blocked/done/scrapped — sketch: active/scrapped only
---
```

---

## plan frontmatter

```markdown
---
status: active
implements: specs/<x>.md   # optional; path relative to flightdeck root; absent → walkaround flags "orphan plan"
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
---
```

---

## debrief frontmatter

```markdown
---
status: active            # active / obsolete / superseded
reviewed: specs/<x>.md    # the spec/topic this review covers
last_updated: YYYY-MM-DD
---
```

(A debrief is retrieved by the spec/topic it reviewed + date, not by a trigger — so no `when_to_read`/`applies_to`.)

---

## INDEX.md — per folder

```markdown
# <folder>/ — INDEX

<!-- AUTO:<folder> -->
- [<file>](<file>) — <status> — <one-line summary>
<!-- /AUTO -->

<!-- optional hand-maintained area (grouping notes for multi-file topics); AI does not touch -->
```

Rows in `incidents/` `checklists/` `charts/` add `when_to_read` / `applies_to`. `debriefs/` rows show reviewed spec + date. `implements` does NOT go into the INDEX.

---

## INDEX.md — root (flightdeck/INDEX.md)

```markdown
# flightdeck — INDEX

<!-- AUTO:root -->
- specs/ — 3 (2 active, 1 done)
- plans/ — 2 (1 active, 1 blocked)
- incidents/ — 1 active
- checklists/ — 1 active
- charts/ — 2 projects imported
- debriefs/ — 1 active
- sketches/ — 4
<!-- /AUTO -->
```

---

## status flow (recommended, not enforced)

```
pending → active → awaiting-review → done
active ↔ blocked
any active state → scrapped
knowledge: active → obsolete | superseded
```

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

- **One file per topic.** Recurrences append `## [Case N]`.
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

## sketch body

```markdown
# <rough idea>

<one-line gist; promote to a spec when it's worth starting>
```

### Rules

- Sketches have no status progression — they are either acted on (promote to a `spec`) or scrapped.
- If the sketch has been sitting > 6 months and no trigger has fired, consider scrapping. An idea that never finds its moment is not high-signal.

---

## debrief body

```markdown
# <spec or topic> — <reviewer> review

**Date**: YYYY-MM-DD
**Reviewer**: <name / model>
**Reviewed**: [link to the spec or artifact](../specs/YYYY-MM-DD-foo-design.md)

## Raw feedback

<Reviewer's full text — pasted verbatim. If summarized from a conversation, mark "(paraphrased by user)" at top.>

## Disposition (per review point — every point must carry a tag)

1. **[adopt]** <review point in 1 line> — <what specifically to change in the spec / code>
2. **[reject]** <review point in 1 line> — <one-line why>
3. **[defer]** <review point in 1 line> — <link to follow-up cockpit item / sketch / new spec>
4. **[adopt]** <next point> — <change>
   ...

(Every numbered point ends with `[adopt]` / `[reject]` / `[defer]`. No bare points.)
```

### Rules

- **Every review point carries exactly one of `[adopt]` / `[reject]` / `[defer]`.** No bullet may exist without a tag. A bullet without a tag = the file is incomplete.
- **Completion gate**: a debrief file is "complete" iff every numbered point has a tag. Incomplete file = exit-blocking hanging task in `cockpit.md` ("finish disposition of `debriefs/<file>`"). The hanging task does not clear until the file is complete.
- **`[defer]` must point somewhere**: link to a `cockpit.md` future-work item or a sketch. Defer without a target is silently lost — that's the failure mode the tag exists to prevent.
- **Long reviews (>1000 words)**: keep raw verbatim. Disposition section may grow long too — that's fine. The constraint is per-point tagging, not brevity.
- **Splitting one review point into multiple**: allowed (and encouraged when one bullet bundles `[adopt]` + `[defer]` halves). Just enumerate each as its own line.

---

## cockpit.md

```markdown
# Cockpit — <project>

**Last updated**: YYYY-MM-DD by <who> (<one-line state summary>)
**Active focus**: <current main thread, 5–15 words>

## Next session

1. <first concrete action — executable by reading cockpit only>
2. <second>

## Hanging tasks

- [ ] Finish disposition of [debriefs/...](debriefs/...)
```

### Rules

- **Length cap: 80 lines hard ceiling.** Past 80, trim immediately.
- **`Active focus` is current state**, not history.
- **Hanging tasks block landing** — resolve, or explicitly defer with a date.
- **History does not live in cockpit.** Durable record = `landed/` archive + `git log` (+ `landed/HISTORY.md` when `git: false`). A finished item leaves `Next session`; it is not logged in cockpit.
- **No metric tracking duplicated elsewhere** — link to the single source.
- **No version stamp in cockpit.** The deck-conformance version lives in `rules.md` `version:`; migration detection compares it against `MIGRATION.md` (`current` + `layout_need_update`). cockpit is pure focus.

---

## landed/HISTORY.md

```markdown
# History — <project>

<!-- Add-only landing log: one line per landing, newest first. Never edit or delete past entries.
     Required when rules.md sets git: false; optional otherwise.
     Lives under landed/ — outside the routing graph; never read at session start. -->

- YYYY-MM-DD — <what landed this session>; next: <pointer to next session item>
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

When amending a long-lived spec — especially **backlog specs** that gain items over multiple sessions, or **specs revised after debrief disposition** — mark new / modified / removed items with prefix tags so the change history is grep-able and merge-friendly:

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

- **Optional.** Small one-shot specs (single-session, no debrief round) don't need delta markers. The cost of adding them outweighs the benefit at that scale.
- **Apply only to substantive changes.** Typo fixes don't earn a marker; an item's scope shifting does.
- **REMOVED keeps history.** Strike-through preserves the audit trail; outright deletion makes it impossible to see "what we considered and rejected". The audit trail is the whole point.
- **Markers compose with `status:` frontmatter.** A spec can be `status: blocked` AND have an `ADDED:` line in its body. Status applies to the artifact; markers apply to items within.
