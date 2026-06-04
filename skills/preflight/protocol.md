# flightdeck protocol (reference)

> Loaded on demand by `preflight` (and referenced by `landing` / `walkaround`). This is the protocol "textbook": the data model, folder semantics, routing, authority order, write gate, and lifecycle. The operational entry ritual lives in [SKILL.md](SKILL.md).

## Core principle

`flightdeck/` is a directory convention organized by **when you read what** — a persistent workbench for AI-assisted coding. What earns a place is governed by the [write gate](#write-gate).

## Project rules (`rules.md`)

`flightdeck/rules.md` is a **mandatory** project-config file read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`, `status`). It is part of the **minimal contract** (`rules.md` + `cockpit.md`; plus `landed/HISTORY.md` under no-git) and must carry a `version` field (the deck-conformance version that drives migration detection).

As of **3.0**, `rules.md` carries just `version` plus free-prose house rules:

- `version` — required identity field (drives [migration detection](#migration-detection); not a behavior toggle). The **only** structured frontmatter field.
- **House rules** — free prose in two recommended subsections: `### Project conventions` (deck-local conventions) and `### Autonomy overrides` (behavioral overrides).

Everything that used to be a toggle is now **inferred from the environment** (`git`, `emit_agents_md`, `scripts`-runtime), decided by **skill judgment** (landing's archive call), or a **default that House Rules can override** (`commit`). The pre-3.0 keys (`git` · `emit_agents_md` · `disabled_gates` · `disabled_folders` · `model_invocable` · `status_auto` · `commit_mode`) are **read but ignored through 3.x and removed at 4.0** — a deck still carrying them keeps working; `walkaround` offers any structural migration (see [migration detection](#migration-detection)). Re-adding a structured toggle faces a high bar (per-project-varying + real-demand-now + not-inferable + not-foldable); almost everything belongs in House Rules, inference, or skill judgment instead. Full schema + ready-to-paste template: [templates.md § rules.md](templates.md#rulesmd).

## Rule resolution order

Every skill resolves each behavior in this order — **first hit wins**:

1. **House Rules override** (`rules.md` `### Autonomy overrides` segment) — if matched, use it and **skip inference**.
2. **Environment inference** — `git`: does deck root contain `.git`?; `emit_agents_md`: does deck root already have `AGENTS.md`?
3. **Built-in default** — `commit` = **local commit auto, push asks** (local commits are reversible — reset/amend; push is outward, so it stays gated); **all five rituals (`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`) self-invocable**; `status` auto-flips `start` (idea→active) and `done` (on approval) but **never archives** — whether a `done` artifact lands is `landing`'s cross-reference-aware judgment; `scripts` = **inferred** (use the bundled INDEX/verdict scripts when a `uv`/`python` runtime is reachable, else by hand). The one outward action (push) stays gated; everything reversible runs without asking.

(Pre-3.0 structured keys, when still present on a not-yet-migrated deck, are read between steps 1 and 2 — honored for 3.x compatibility, removed at 4.0.)

**deck root** = the directory containing `rules.md` (the parent of `flightdeck/`); if none is found, fall back to cwd **with a warning** (never silent — else a misconfigured run looks like it found a deck when it didn't).

**Override authority** (which config wins): **CLAUDE.md (project) > flightdeck House Rules (deck) > flightdeck defaults.** flightdeck always honors the project's own agent rules above its own House Rules.

**Behavioral-override matching:** within the literal `### Autonomy overrides` heading, skills match the standard phrases (table below) by **lenient (contiguous) substring** — not per-call semantic guessing (consistent + testable across models) — **skipping HTML-comment lines** (so a `<!-- migrated … -->` provenance note never mis-matches) and recognizing the **legacy Chinese** equivalents (right column). An ON phrase and its negated twin (default `status: auto start` vs the override `status: don't auto start`; `commit without asking` vs `don't auto-commit`) are distinguished by the inserted negation — the contiguous ON substring is absent from the OFF line, so they never cross-match. No `### Autonomy overrides` segment → fall back to tolerant whole-House-Rules reading. **Internal conflicts are the user's responsibility** — flightdeck never auto-resolves contradictory overrides (it may passively flag one, never silently pick).

**Standard-phrase table** (canonical English; migration emits exactly these; hand-written overrides recommended to match):

| Behavior | Standard phrase (canonical English) | Legacy Chinese (compat) |
| --- | --- | --- |
| commit confirm before the local commit (default is auto local) | `commit: ask` | `commit 先问我` |
| commit manually (never) | `don't auto-commit; leave changes for me / CI` | `不要自动 commit，留给我或 CI` |
| a status transition off (`start` — on by default) | `status: don't auto <transition>` | `status 不要自动 <transition>` |
| no git | `this deck doesn't use git; history in landed/HISTORY.md` | `本 deck 不走 git，历史记 landed/HISTORY.md` |
| has AGENTS.md but don't regen | `has AGENTS.md but don't auto-regen` | `有 AGENTS.md 但不要自动 regen` |

There is no self-invoke override (all five rituals always self-invoke), no `auto land` toggle (archiving is landing's judgment), no `run scripts` toggle (script use is inferred from runtime availability), and no `disabled_folders` (empty/unused folders are simply not flagged). The legacy `commit without asking` phrase still matches the new default (auto local commit) for compat.

## Migration detection

`MIGRATION.md` (repo root) carries frontmatter `current` (latest release) + `layout_need_update` (releases that changed deck structure). The deck's currency is computed as a machine **layout verdict** by `flightdeck_index.py --verdict` (fallback: read the same frontmatter + structural signals by hand). **`preflight` reads the verdict and only reports it; `walkaround` is the sole command that writes `version`** (bump or migration). The four verdicts:

- `current` → `version == current` and no structural signal → up to date; nothing to do.
- `compatible-behind` → `version < current` but no `layout_need_update` entry is newer → safe; **`walkaround` bumps** the deck's `version` to `current` (a number stamp; preflight never bumps).
- `structural-behind` → `version <` some `layout_need_update` entry (or no `version`/`rules.md`), or a pre-model-v4 structural signal is present → a migration applies → **`walkaround` offers it** (author-confirmed; never silent), pointing at the matching `MIGRATION.md` section.
- `malformed` → a required workflow frontmatter field is missing → reported by `walkaround` (CRITICAL) and guarded by `landing` (STOP before regen).

This replaces the pre-2.2 cockpit `**Layout**` string check. Purely additive releases never enter `layout_need_update`, so they never trigger a false migration prompt.

## Data model (folder = kind, frontmatter = status)

flightdeck has exactly two axes:
- **Folder = kind** (implicit; never written in frontmatter). Workflow kinds: `specs/` `plans/`. Knowledge kinds: `incidents/` `checklists/` `charts/`.
- **Frontmatter = status** (explicit, required) + knowledge routing fields (`when_to_read`/`applies_to`/`last_updated`) + a plan's optional `implements:`. The folder is the kind — files carry no type field.

See [templates.md](templates.md) for per-folder frontmatter templates. The full field set is the canonical table below.

## Frontmatter field reference (canonical)

This table is the **single source of truth** for every frontmatter / config field. `templates.md` (ready-to-paste blocks), `folder-semantics.md` (folder purpose), and `walkaround` (validation) defer here — they must not restate field semantics.

| Field | Applies to (kind) | Required? | Read by | Written by | walkaround |
| --- | --- | --- | --- | --- | --- |
| `status` | all workflow + knowledge | **required** | preflight/landing/status/walkaround | status/landing/user | Audit 1 |
| `summary` | workflow (specs/plans) | recommended | INDEX generation | status/landing/author | INFO if missing |
| `note` | workflow | optional | cockpit `## 进行中` row + walkaround render | author/status | rendered as `[note: …]`, not validated |
| `last_updated` | knowledge + workflow | knowledge **required**; workflow recommended | preflight (staleness) | status/landing (auto-bump) | knowledge: Audit 2; workflow: INFO |
| `implements` | plans | optional | reverse-lookup via `plans/INDEX.md` | author | Audit 4 (orphan INFO) |
| `supersedes` | workflow | optional | grep (reverse derived) | author/status | dangling-edge INFO (optional) |
| `related` | workflow | optional | grep | author | dangling-edge INFO (optional) |
| `when_to_read` | incidents/checklists/charts | **required** | preflight routing | author | Audit 2 |
| `applies_to` | incidents/checklists/charts | **required** | preflight routing | author | Audit 2 |
| `skip_when` | incidents/checklists | optional | match-time negative routing | author | not enforced |
| `recurrences` | incidents | optional (default 1) | INDEX-row render + promotion gate | landing/status (auto-bump on a clear recurrence) | int ≥ 1; ≈ 1 + `[Case N]` count |
| `superseded_by` | knowledge (when `status: superseded`) | **conditional** | redirect from dead-but-in-place file | author | Audit 3 |
| `version` | `rules.md` (root) | **required** (rules.md is mandatory) | preflight (verdict report) / landing (guard) / walkaround | launch (init) / **walkaround only** (bump + migrate) | Audit 10 |
| `git` · `emit_agents_md` · `disabled_gates` · `disabled_folders` · `model_invocable` · `status_auto` · `commit_mode` | `rules.md` (pre-3.0) | **removed in 3.0** — inferred / House-Rules / skill-judgment / default (see [Rule resolution order](#rule-resolution-order)); read but ignored for 3.x compat | all entry skills | — | — |

`cockpit.md` board fields (`Last updated` / `Active focus` / `## 进行中` / `## 下一步` / `## Hanging tasks`) are not YAML frontmatter. `## 进行中` is an AUTO region derived from `status: active` spec/plan; `## 下一步` is AI-maintained — see [templates.md § cockpit.md](templates.md#cockpitmd).

### Two deliberate asymmetries

**Supersession — edge (workflow) vs status pointer (knowledge).** Knowledge files stay in place (never archived): a reader can land on a dead-but-in-place file, so a *forward* `superseded_by` (required when `status: superseded`) redirects to the replacement. Workflow artifacts archive into `landed/` when done — the old one is history a reader rarely hits cold, so the new artifact carries a *backward* `supersedes` edge and the reverse ("who superseded me") is grep-derived, never stored. Two mechanisms, one principle each — do not unify.

**`last_updated` — required (knowledge) vs recommended + auto-bump (workflow).** Knowledge is found by grep-routing where stale advice is dangerous → required. Workflow is found via INDEX/cockpit → staleness matters less; recommended, and auto-bumped by `status`/`landing` to prevent rot.

## Status (label + recommended flow)

Fixed values, by kind:
- workflow (spec/plan): `idea / active / done / scrapped`
- knowledge: `active / obsolete / superseded`

Recommended flow (documentation, NOT enforced):

```
idea → active → done
any state → scrapped
knowledge: active → obsolete | superseded
```

- `idea` = unstarted thought / design (the to-start pool); only in `specs/INDEX`, **not** in cockpit. No date prefix.
- `active` = being worked on; **auto-appears in cockpit `## 进行中`**. The `idea→active` flip auto-adds the `YYYY-MM-DD-` prefix.
- `done` = complete, archived to `landed/`.
- `scrapped` = rejected / abandoned; stays in `specs/` (not archived), excluded from `specs/INDEX` — kept so the AI does not re-raise a settled-against direction.

The optional `note:` field carries the "why it hasn't moved" diagnostic (blocker / pending reason) that the merged `active` state would otherwise lose; cockpit + walkaround render it as `[note: …]`.

Status is just a label — the user edits it freely; at landing the AI may *suggest* the next typical status (per the recommended flow), applied only after the user confirms. walkaround flags odd values as INFO/warning, never blocks.

> **Legacy (pre-3.0, read for compat through 3.x):** the old 6-value workflow set (`pending / awaiting-review / blocked`, plus sketch `active`) remaps `pending → idea`, `awaiting-review → active`, `blocked → active` (+ a `note:` / cockpit line). `preflight` offers this migration; never silent.

## INDEX.md (per-folder + root)

Every artifact folder has an `INDEX.md` — a derived index of that folder's files: one row per file `[file](file) — status — one-line summary` (knowledge folders add `when_to_read`/`applies_to`). The `<!-- AUTO -->` region is machine-maintained (regenerated from each file's frontmatter); an optional hand area sits outside it. `specs/INDEX` groups by status (`待启动（idea）` / `进行中·完成（active·done）`) and skips `scrapped` — see [folder-semantics § specs/](folder-semantics.md#specs--designs).

The root `flightdeck/INDEX.md` is a sub-folder directory + global status summary (e.g. `specs/ — 3 (2 active, 1 done)`); it is a downgradeable component.

**Commands read the INDEX first and drill into individual files only on demand** — this is the main token saving (cost scales with folder count, not file count). landing regenerates only the INDEX of folders changed this session; walkaround does a full INDEX↔frontmatter consistency check.

## Folder map

```
flightdeck/
├── cockpit.md   rules.md   INDEX.md
├── specs/       INDEX.md   (idea / active / done / scrapped)
├── plans/       INDEX.md
├── incidents/   INDEX.md
├── checklists/  INDEX.md
├── charts/      INDEX.md   (may hold an imported external project tree)
└── landed/      (archive + HISTORY.md)
```

Reachability entries: `cockpit.md` / `INDEX.md` / `rules.md`. (No bundle README — multi-file topics live as several files in one folder, grouped via the INDEX hand area; only `charts/` may contain an external project subtree.)

**Which folder?** Classify by lifecycle: design / idea (started or not) → `specs/` (`status: idea` = unstarted); execution plan → `plans/`; evergreen operational reference → `checklists/`; imported external material → `charts/`; post-incident records → `incidents/`.

**Routing is graph-based, not filesystem-based.** A file is "active" only if reachable from an entry (`cockpit.md`, `INDEX.md`, or `rules.md`). **A file nothing links to effectively does not exist** — no session reads it. Custom folders / root files are allowed but MUST be reachable from an entry, or they are orphans.

## Routing — scenario triggers

| Scenario | Read first |
| --- | --- |
| Looking for next task | `cockpit.md` |
| Unsure about a design | `specs/` |
| Running tests / preparing commit | `checklists/` |
| Strange behavior / deja-vu bug | `incidents/` |
| Need outside perspective | `charts/` |
| Designing new feature | `specs/` (`status: idea`, flip to `active` when starting) |
| Breaking work into steps | `specs/` → write a `plans/` file |

**How to pick the right incident / checklist**: don't read every file. Both folders use frontmatter (`when_to_read` + `applies_to` + `last_updated`) — grep the metadata, only load full files whose triggers match the current task. Use `last_updated` to judge staleness. An optional `skip_when` field (negative routing — "when NOT to read this") lets a file pre-empt a false match (e.g. `skip_when: editing tests only` on a production-hardening checklist, so it stays silent during test-only work); absent is fine.

### Frontmatter requirements (hard-fail)

Incidents and checklists **MUST** carry frontmatter with `when_to_read`, `applies_to`, and `last_updated`. On a missing field: STOP, report the file path + missing fields to user, offer (a) add now or (b) delete the file. Silent skip = files invisible while their authors believe they're active. That is the worst failure mode for an advice system.

### Proactive incident resurfacing

Before starting a task whose description / file paths overlap with an incident's `applies_to` tags, surface it: "this touches `[tags]`, overlapping with [incidents/X.md](incidents/X.md) — worth a read first?". Recording a recurrence happens at the **other** end of the session: at landing, a **clear** same-incident match auto-appends `[Case N]` + bumps `recurrences` (see [exit-ritual § Step 5a](exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up)); an **ambiguous** match asks the user. Auto-counting is safe because the consequential step — *promotion* — stays user-gated.

## Source-of-truth precedence (when sources disagree)

Project agent rules > `rules.md` > `cockpit.md` > active folders (`specs/` `plans/` `incidents/` `checklists/` `charts/`) > `landed/`

`rules.md` sits just below the project's own agent rules: it governs how flightdeck skills behave. `cockpit.md` is the single operational entry below it.

> **"Project agent rules"** = your project's top-level AI instructions file — whatever your AI tool reads on every session.

## Design philosophy

> **Semantic clarity outranks thematic consistency.**

When naming or structuring decisions trigger a conflict between "fits the aviation metaphor" and "reads correctly", clarity wins. The flightdeck metaphor is used because it sharpens operational intent — *not* as a theme to be applied uniformly. `specs/` intentionally uses a neutral name because no aviation equivalent improves it. Future concepts face the same test.

Reject:
- aviation roleplay / sci-fi theming / meme interfaces / gamified agent cosplay
- "cute but unclear" terms (e.g., `/stuck → /request-vector` was rejected during rebrand — `/stuck` already reads correctly)
- forcing every new term into the metaphor

## Lifecycle

```
idea →(flip one field)→ active → done   →(land = move to landed/)
                                  scrapped (stays in specs/, not archived)
```

A spec starts `status: idea` (unstarted, no date prefix). Starting it is **just a field flip** `idea → active` (which auto-adds the `YYYY-MM-DD-` prefix and surfaces it in cockpit `## 进行中`) — no folder move, no relation-edge rewrite. Each plan carries optional `implements: specs/<x>.md`. `location` (active vs `landed/`) is derived from landing a done item. Folder says the kind; frontmatter `status` says the state.

A scrapped spec stays in `specs/` (marked `status: scrapped`), never archived to `landed/` and excluded from `specs/INDEX`; delete by hand at will.

**Knowledge lifecycle:** `active → obsolete | superseded` (set `superseded_by` when superseding). Landing knowledge is optional — files may stay in place indefinitely; no "to-land" reminder.

## Exit ritual

90% of exits are obvious — classify and write directly. Only truly ambiguous items invoke brainstorming. The full decision tree (classification heuristics, hanging-task gate, INDEX regeneration, cockpit update) lives in [exit-ritual.md](exit-ritual.md) and is run by `/flightdeck:landing`.

After classifying: update `cockpit.md` (`Last updated` + regen `## 进行中` from `status: active` + auto-write `## 下一步` + any `Hanging tasks` changes); append to `landed/HISTORY.md` when no-git; then commit locally per the commit default (auto local commit, **push asks**; skipped entirely under no-git). landing regenerates the INDEX of any folders changed this session.

## Ritual responsibilities — who owns what

Three entry rituals, three non-overlapping jobs — so no check is both everyone's and no-one's. When a check could belong to two rituals, this table decides:

| Ritual | Role | Writes? | Cockpit 80-line trim | INDEX | Deep per-file audit |
| --- | --- | --- | --- | --- | --- |
| `preflight` | read-only takeover at session start | no (reads layout verdict, reports only) — deckless redirects to /flightdeck:launch | reads only — passive note on git/layout drift | reads folder INDEX as catalog | no — audits belong to walkaround |
| `landing` | write the session's outcome | yes | **owns the trim** (proposes → confirms → edits) | regenerates changed folders' INDEX | no |
| `walkaround` | integrity audit on demand | version bump/migrate only (**sole version writer**); else proposes fixes, never auto-applies | flags `> 80` as INFO | full INDEX↔frontmatter check | **owns** status / orphan / dangling-ref / stray-file audits |

The 80-line cockpit trim is **landing's** (it is the only ritual that writes cockpit); `walkaround` only flags it; `preflight` never touches it.

## Write gate

`flightdeck/` records only content that **changes future behavior, influences decisions, or gets referenced repeatedly**. Session byproducts, debug logs, and chat play-by-plays do not qualify. Gate strictly.

## Templates

See [templates.md](templates.md) for `spec` / `plan` / `incident` / `checklist` / `cockpit.md` / `rules.md` / `HISTORY.md` / `INDEX.md` templates.

## Relation to project agent rules

| | Project agent rules | `flightdeck/` |
| --- | --- | --- |
| Loaded | every session | on demand |
| Contains | rules + trigger table + style | state + knowledge + history |
| When in conflict | wins | yields |

## Incident promotion gates

Multi-criterion gate evaluated by `landing`. An incident reaches the **checklist promotion gate** when ALL three hold:
1. `recurrences ≥ 3` (the frontmatter counter; ≈ 1 + `[Case N]` block count).
2. Cases recurred across **≥ 2 distinct sessions** (same-session triple-hits don't count).
3. Remediation pattern is **stable across cases** (the "next time avoid X" rule reads similarly across all cases — not 3 unrelated fixes papering over one symptom).

The `recurrences` frontmatter counter (auto-bumped at landing) plus the `[Case N]` block dates surface criteria 1–2; `recurrences` also renders into the `incidents/INDEX.md` row as `recur: N` (when > 1), so the gate is visible at catalog time without opening the file.

When the gate fires, `landing` prompts: "Promote `incidents/X.md` to `checklists/X.md`?". User confirms — promotion is **never automatic**.

A separate **project-rules upgrade gate** fires when a promoted incident continues to recur after promotion. Then add a one-liner to project agent rules and mark the incident `Status: upgraded → project rules`. Do not delete the incident.

## Common mistakes — STOP and reclassify

| Mistake | Fix |
| --- | --- |
| Same fact in cockpit + incident + spec | One authoritative source; others link via `[name](incidents/X.md)` |
| Scratch written into flightdeck/ | Transient scratch lives in project-root `tmp/` (gitignored), not flightdeck. |
| `incidents/` writes "forgot / careless" | Root cause must be a wrong assumption / wrong model / wrong process. |
| External review feedback saved as its own file | Raw feedback is transient → project-root `tmp/`; its disposition (adopt / reject / defer) folds into the reviewed spec's `## 评审纪要`. |
| Brainstorming where every knowledge item belongs | Heuristics catch 90%. Default-brainstorm is the failure mode. |
| Cockpit > 80 lines | Trim immediately — drop finished items, move design detail to the relevant `specs/` file; history is `git log` / `landed/HISTORY.md`, not cockpit. (Landing owns the trim — see [Ritual responsibilities](#ritual-responsibilities--who-owns-what).) |
| Bumping `Last updated` on every commit / typo / grep | Signal pollution. Only bump on 4 triggers in exit-ritual.md `Cockpit update`. |
| Incident / checklist without required frontmatter | STOP, report file path + missing fields. Add or delete before proceeding. |
| Incident / checklist with `last_updated` > 1 year in a fast-moving project | Likely stale advice. Bump after re-verifying or flip to `status: obsolete`. |
| "Save in case it's useful later" | No. Gate strictly. |

## Authoring new artifacts

Producing a new deck artifact (spec / plan / incident / checklist / chart) — including from an external authoring skill (brainstorming / writing-plans) — goes through **`/flightdeck:new`** (script: `scripts/flightdeck_new.py`), which stamps the correct per-kind frontmatter + naming and regenerates INDEX/cockpit. The full contract (kind→folder, naming, per-kind frontmatter, default status, slug rule) lives in `skills/new/SKILL.md` — the single authority, so the shape is never re-derived from scattered docs. **Shell-first**: create the shell via `new` first, then write the body into the returned path; do not hand-derive a path or write to `docs/`.

## Cross-references

The flightdeck convention describes WHAT to write and WHERE; the tool that produces the content is up to you (hand-write, use any AI skill, or ad-hoc LLM).

**Optional companions** (Claude Code with the `superpowers` plugin installed):
- `superpowers:brainstorming` → produces well-structured designs that fit `specs/`; hand the design off to `/flightdeck:new spec` (shell-first) so frontmatter/naming/regen are stamped, not re-derived.
- `superpowers:writing-plans` → produces task lists that fit `plans/` (via `/flightdeck:new plan`). Plan files use `- [ ]` checkboxes for executing-plans tracking; **flightdeck does not require flipping these** — progress lives in `cockpit.md` + commit log.

These are convenient but **not required** — flightdeck accepts content from any source.

The `flightdeck/` directory structure is **tool-agnostic** — any AI assistant can follow these conventions via project-level instructions. See `adapters/` for per-tool install paths.
