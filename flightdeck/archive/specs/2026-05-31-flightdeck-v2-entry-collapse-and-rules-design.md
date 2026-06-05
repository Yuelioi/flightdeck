# flightdeck v2 — entry-layer collapse + customization layer

**Date**: 2026-05-31
**Status**: design (pending plan)
**Version target**: 2.0.0 (breaking — removes files/folders; ships a guided migration)

## Why

Dogfooding flightdeck v1.x across real projects surfaced seven recurring frictions. They mostly trace to one root cause: **flightdeck got too heavy and its entry-layer seams are too fuzzy.** The `board.md → cockpit/manifest/logbook` split was made along *read-frequency*, but content cleaves along *category* (what-to-do / what's-open / what-happened / where-things-are), so the categories bleed across files and everything drifts back into `cockpit.md`.

The seven frictions:

1. `cockpit.md` accumulates content; not clear enough (despite the 80-line ceiling).
2. A spec spawns many flight-plans; progress isn't updated in time and has no single rollup view.
3. Unclear *when* to update `cockpit.md` on task completion (the rule is buried in `exit-ritual.md`, fired only at landing).
4. `kneeboard/` meaning is unclear; almost no project uses it (ceremony > value; competes with `tmp/`).
5. `landed/` only archives plans/specs — an obsolete checklist/incident-report has no archive path.
6. `INDEX.md` / `manifest.md` / `cockpit.md` have conflicting responsibilities (two "indexes," overlapping "what to do" vs "what's open").
7. No customization layer — skills hardcode assumptions (git exists, emit `AGENTS.md`, all folders/gates apply).

## Decisions (locked with user)

| # | Cluster | Decision |
| --- | --- | --- |
| A1 | Entry layer (#1/#3/#6) | Collapse to a single operational entry. `cockpit.md` is the only must-read; `INDEX.md` stays purely as the resource lookup. Remove `manifest.md` and `logbook.md`. |
| B1 | Multi-plan progress (#2) | The spec owns a `## Plans` ledger at its tail and is the rollup, using explicit state words (not checkboxes). `cockpit.Next session` points at the spec, not each plan. |
| C1 | kneeboard (#4) | Remove `kneeboard/` from the convention. Scratch lives in project-root `tmp/` (gitignored). Delete the `last_touched` rule and the landing-blocking gate. |
| C3 | landed (#5) | Generalize `landed/` to mirror any source folder on demand (`landed/checklists/`, `landed/incident-reports/`, `landed/charts/`, …). Archive obsolete-but-historical references instead of deleting them. |
| D | Customization (#7) | New optional `flightdeck/rules.md`: structured toggles + free-prose house rules, read first by every entry skill. |
| — | History (follow-up to A1) | Removing `logbook.md` leaned on `git log` as durable memory, but `rules.md` allows `git: false`. So keep an ultra-light `landed/HISTORY.md` (one line per landing). Required when `git: false`, optional otherwise. cockpit stays purely now/next. |

## New surface

```
flightdeck/
├── rules.md          # NEW (optional) — project config; read first by every entry skill
├── cockpit.md        # single must-read: do / open / blockers (≤80 lines)
├── INDEX.md          # resource lookup for checklists/ + incident-reports/ only
│
├── specs/            # design docs; multi-plan spec carries its own ## Plans ledger (B1)
├── flight-plans/     # implementation plans
│
├── checklists/       # operational reference (may be bundles)
├── incident-reports/ # lessons learned
├── charts/           # imported external material
│
├── sketches/         # unstarted ideas
├── safety-reviews/   # external review feedback + disposition
│
└── landed/           # archive umbrella — mirrors ANY source folder on demand (C3)
    ├── flight-plans/
    ├── specs/
    ├── checklists/        # NEW
    ├── incident-reports/  # NEW
    └── HISTORY.md         # NEW — append-only landing log (required when git:false)
```

Removed vs v1.x: `manifest.md`, `logbook.md`, `kneeboard/`. Entry/scratch concepts drop from 5 (cockpit/manifest/logbook/INDEX/kneeboard) to 3 (cockpit/INDEX/rules).

## Section 1 — Entry layer (A1)

`cockpit.md` is the single operational entry, ≤80 lines, fixed schema:

```markdown
# Cockpit — <project>
**Last updated**: YYYY-MM-DD by <who> (<one-line summary>)
**Active focus**: <current main thread, one line>

## Next session        # 1–5 concrete items
## In flight           # ONLY divergent-state rows (blocked / awaiting-review). Omit when empty.
## Blockers            # external waits. Omit when empty.
## Hanging tasks        # open items blocking a clean landing. Omit when empty.
```

- Old `manifest.In flight` (divergent-state rows only) and `Blockers` fold in as **sections that appear only when non-empty** — zero line cost on a healthy project, which is what kept manifest small to begin with.
- `INDEX.md` keeps its v1 purpose unchanged: scannable index of `checklists/` + `incident-reports/` (AUTO markers). It no longer competes with anything, because the other "index" (manifest) is gone.
- **No history file recreated in the routing graph.** Durable record = `landed/` archive + `git log` (+ `landed/HISTORY.md` when git is off). "Deferred" items become a `sketches/` file (real idea) or a `Next session` line (soon).

**#3 — when to update cockpit.** Promote the rule out of `exit-ritual.md` into the *during-session* scenario table AND the landing ritual:

> **After any commit that changes user-perceivable state, update `Next session` before starting the next task.** Pure exploration / grep / typo-fix never updates `Last updated`.

## Section 2 — Multi-plan progress (B1)

A spec that spawns multiple plans owns a ledger at its tail; the spec is the rollup. The ledger uses **explicit state words, not checkboxes** — a multi-plan spec routinely needs more than done/not-done, and `- [ ] plan — blocked` is a confusing double-representation. The states reuse the lifecycle vocabulary:

```markdown
## Plans
- 2026-06-01-foo-phase1-plan.md — landed
- 2026-06-03-foo-phase2-plan.md — active
- phase 3 (auth) — pending
- phase 4 (migration) — blocked: waiting on infra decision
```

States: `pending` / `active` / `blocked` / `awaiting-review` / `landed` (and `scrapped`) — the same set as the spec/plan lifecycle, so a plan's ledger word and its frontmatter `state:` never disagree. This deliberately does **not** use `- [ ]` checkboxes (consistent with v1's "checkboxes are not load-bearing" rule — they stay optional notation inside a plan file, never the rollup status mechanism).

`cockpit.Next session` points at the spec, not each plan — cockpit stays thin, and there is one place to see progress across the N plans. Single-plan specs do not need the ledger. This supersedes the v1 "progress lives in cockpit + commit log" guidance for the multi-plan case.

## Section 3 — Folders (C1, C3)

- **C1 — remove `kneeboard/`.** Scratch lives in project-root `tmp/` (gitignored). Delete: the `last_touched:` frontmatter requirement, the stale-kneeboard landing gate, and all kneeboard templates/anti-patterns. One fewer concept, one fewer gate.
- **C3 — generalize `landed/`.** Any source folder can be mirrored under `landed/` on demand (`landed/checklists/`, `landed/incident-reports/`, `landed/charts/`, …). An obsolete-but-historical reference is **archived** rather than deleted or left as a confusing in-place `status: obsolete` flip. Routing already excludes `landed/`, so reachability is unaffected. `status: obsolete` remains valid for "keep in place but mark dead"; archiving is the new option for "move out of the active set but don't lose it."

## Section 4 — Customization layer (D, #7)

`flightdeck/rules.md` (optional). **Every entry skill reads it first** and branches on it: `preflight`, `workflow`, `walkaround`, `landing`, `emit-agents-md`.

```markdown
---
git: true                 # false → skills skip all git reconcile/commit; landing uses HISTORY.md
emit_agents_md: true      # false → emit-agents-md is a no-op (reports disabled)
disabled_folders: []      # e.g. [charts, safety-reviews] → never suggested; not flagged as orphans
disabled_gates: []        # e.g. [awaiting-review-owner, safety-review-disposition]
---

## House rules
Free-prose conventions the AI must honor (e.g. "never auto-commit", "specs written in Chinese").
```

**Closed toggle set** (anything outside this set is ignored with a warning, so typos don't silently change behavior):

| Key | Type | Default | Effect when changed from default |
| --- | --- | --- | --- |
| `git` | bool | `true` | `false` → skip git branch/status/stash/log reconcile; never auto-commit; staleness check + history use `landed/HISTORY.md` instead of `git log`. |
| `emit_agents_md` | bool | `true` | `false` → `emit-agents-md` refuses and reports "disabled via rules.md". |
| `disabled_folders` | list | `[]` | Listed folders are never suggested by fallback/exit classification and are not flagged as orphans by `walkaround`. |
| `disabled_gates` | list | `[]` | Named gates are skipped. Known names: `awaiting-review-owner`, `safety-review-disposition`, `frontmatter-required`. |

**House rules** (free prose) are advisory project conventions; the AI honors them but they cannot redefine the closed toggle keys.

**Authority order** (rules.md inserts high, below project agent rules):

> project agent rules > `rules.md` > `cockpit.md` > active `flight-plans/` > active `specs/` > `checklists/` > `incident-reports/` > `landed/`

No `rules.md` = v2 defaults (git on, emit on, all folders/gates active) — purely additive for users who never create it.

## Section 5 — Migration (the breaking part)

Existing projects carry `manifest.md` / `logbook.md` / `kneeboard/`. `preflight` and `workflow` **detect the old layout and offer a one-time guided migration** (never silent):

1. `manifest.In flight` rows → `cockpit.In flight`; `manifest.Blockers` → `cockpit.Blockers`.
2. `logbook.Recently finished` → **never silently dropped.** It is often a higher-level history summary than the commit log. Offer to import it into `landed/HISTORY.md` (one history line per entry). Required when `git: false`; offered (default yes) when `git: true`.
3. `logbook.Deferred` → each becomes a `sketches/` file or a `cockpit.Next session` line (ask per item).
4. `kneeboard/*` → classify into a folder or delete (existing landing logic).
5. Delete `manifest.md`, `logbook.md`, and the emptied `kneeboard/`.

Detection marker: presence of any of the three removed paths. Migration is interactive and reversible (changes are staged, not committed, until the user confirms — unless `git: false`).

## Affected components (for the plan)

- `skills/workflow/SKILL.md` — entry checklist, folder map, authority order, lifecycle, common-mistakes table, templates ref, read-rules.md-first.
- `skills/workflow/folder-semantics.md` — remove manifest/logbook/kneeboard sections; add `rules.md` + `HISTORY.md`; generalize `landed/`; rewrite entry-files section.
- `skills/workflow/templates.md` — remove manifest/logbook/kneeboard templates; add `rules.md`, `HISTORY.md`; update cockpit template (In flight/Blockers folded in); add spec `## Plans` ledger template.
- `skills/workflow/exit-ritual.md` — board-update → cockpit; remove kneeboard gate; HISTORY append on `git: false`; `#3` update rule.
- `skills/preflight/SKILL.md` — read `rules.md` first; `git: false` branch; migration detection; remove stale-kneeboard step; INDEX-only catalog note; staleness check via HISTORY when git off.
- `skills/landing/SKILL.md` — HISTORY append; no kneeboard; `git: false` branch; `landed/` generalization; `#3` update rule.
- `skills/walkaround/SKILL.md` — entries = `cockpit.md` + `INDEX.md` + bundle READMEs (+ `rules.md`); honor `disabled_folders`; drop manifest/logbook.
- `skills/emit-agents-md/SKILL.md` — honor `emit_agents_md` + `git` toggles.
- `scaffolds/full/` — new surface (add `rules.md.example`? minimal stays cockpit-only); remove manifest/logbook/kneeboard; add `landed/HISTORY.md` placeholder.
- `scaffolds/minimal/` — unchanged (cockpit-only) — confirm.
- Release plumbing: `VERSION`, 5 plugin manifests, `CHANGELOG.md`, `MIGRATION.md`, `README.md`/`README.zh.md`, `AGENTS.md`/`GEMINI.md`, `TEST_PLAN.md` — per the version-bump checklist.

## Out of scope

- v1.1 deferred folders (`briefing/`, `blackbox/`, `crew-handover/`, `experiments/`) — separate reassessment.
- Reworking the spec/plan 6-state lifecycle beyond the B1 ledger addition.
- Any change to bundles, routing-graph mechanics, or the frontmatter-routing model.

## Open questions for plan stage

- Exact `rules.md` parse/validate behavior on unknown keys and malformed YAML (warn-and-default vs hard-fail).
- Whether `scaffolds/full` ships a populated `rules.md.example` or just documents it.
- `HISTORY.md` ordering (newest-first vs append-bottom) and exact line format.
