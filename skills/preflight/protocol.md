# flightdeck protocol (reference)

> Loaded on demand by `preflight` (and referenced by `landing` / `walkaround`). This is the protocol "textbook": the data model, folder semantics, routing, authority order, write gate, and lifecycle. The operational entry ritual lives in [SKILL.md](SKILL.md).

## Core principle

`flightdeck/` is a directory convention organized by **when you read what** — a persistent workbench for AI-assisted coding. Write strictly: only content that changes future behavior, influences decisions, or gets referenced repeatedly.

## Project rules (`rules.md`)

`flightdeck/rules.md` is a **mandatory** project-config file read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`, `status`). It is part of the **minimal 3-file contract** (`rules.md` + `cockpit.md` + `landed/HISTORY.md`) and must carry a `version` field (the deck-conformance version that drives migration detection).

As of **3.0**, `rules.md` carries only two structured fields plus free-prose house rules:

- `version` — required identity field (drives [migration detection](#migration-detection); not a behavior toggle).
- `disabled_folders` — the one surviving structured toggle: listed folders are never suggested and never flagged as orphans.
- **House rules** — free prose in two recommended subsections: `### Project conventions` (deck-local conventions) and `### Autonomy overrides` (behavioral overrides).

Everything that used to be a toggle is now **inferred from the environment** (`git`, `emit_agents_md`) or a **default that House Rules can override** (`commit` confirm, all rituals self-invocable, all `status_auto` transitions on). The pre-3.0 keys (`git` · `emit_agents_md` · `disabled_gates` · `model_invocable` · `status_auto` · `commit_mode`) are **read for compatibility through 3.x and removed at 4.0** — a deck still carrying them is honored, and `preflight` offers to migrate it (see [migration detection](#migration-detection)). Re-adding a structured toggle still faces a high bar (per-project-varying + real-demand-now + not-inferable + not-foldable); almost everything belongs in House Rules or inference instead. Full schema + ready-to-paste template: [templates.md § rules.md](templates.md#rulesmd).

## Rule resolution order

Every skill resolves each behavior in this order — **first hit wins**:

1. **House Rules override** (`rules.md` `### Autonomy overrides` segment) — if matched, use it and **skip inference**.
2. **Environment inference** — `git`: does deck root contain `.git`?; `emit_agents_md`: does deck root already have `AGENTS.md`?
3. **Built-in default** — `commit` = confirm; every ritual self-invocable; `status_auto` = `start` + `land` both on.

(Pre-3.0 structured keys, when still present on a not-yet-migrated deck, are read between steps 1 and 2 — honored for 3.x compatibility, removed at 4.0.)

**deck root** = the directory containing `rules.md` (the parent of `flightdeck/`); if none is found, fall back to cwd **with a warning** (never silent — else a misconfigured run looks like it found a deck when it didn't).

**Authority order** (when sources disagree): **CLAUDE.md (project) > flightdeck House Rules (deck) > flightdeck defaults.** flightdeck always honors the project's own agent rules above its own House Rules.

**Behavioral-override identification (穿针 — not a YAML toggle):**
- `### Autonomy overrides` is a **literal heading**; a skill matches the **standard phrases** (table below) within that segment by **lenient substring**, not per-call semantic guessing → consistent across models (Claude/Gemini/Copilot/Codex), testable.
- Matching **skips HTML-comment lines** (`<!-- ... -->`), so a `<!-- migrated from commit_mode:auto -->` provenance comment is never mis-matched.
- If the `### Autonomy overrides` segment is absent → fall back to whole-House-Rules semantic reading (tolerant; never errors).
- **Legacy-language compat**: the canonical phrases are English, but skills also recognize the **legacy Chinese equivalents** (right column) for decks authored before the English canon — same lenient-substring path.
- **House Rules internal conflicts are the user's responsibility.** flightdeck does **not** auto-resolve contradictory overrides (no last-match-wins); a skill may passively flag an obvious contradiction but never silently picks one.

**Standard-phrase table** (canonical English; migration emits exactly these; hand-written overrides recommended to match):

| Behavior | Standard phrase (canonical English) | Legacy Chinese (compat) |
| --- | --- | --- |
| commit automatically | `commit without asking` | `提交不必询问，直接 commit` |
| commit manually (never) | `don't auto-commit; leave changes for me / CI` | `不要自动 commit，留给我或 CI` |
| a ritual must not self-invoke | `<ritual>: don't self-invoke; I run it manually` | `<ritual> 不要自调，我手动跑` |
| a status transition off | `status: don't auto <transition>` | `status 不要自动 <transition>` |
| no git | `this deck doesn't use git; history in landed/HISTORY.md` | `本 deck 不走 git，历史记 landed/HISTORY.md` |
| has AGENTS.md but don't regen | `has AGENTS.md but don't auto-regen` | `有 AGENTS.md 但不要自动 regen` |

When a folder is in `disabled_folders`, it is never suggested and never flagged as an orphan.

## Migration detection

`MIGRATION.md` (repo root) carries frontmatter `current` (latest release) + `layout_need_update` (releases that changed deck structure). `preflight` (step 2) and `walkaround` (Audit 10) compare the deck's `rules.md` `version` against it — never silently migrating:

- `version == current` → up to date; continue silently.
- `version < current` **and** some `layout_need_update` entry is `> version` → a structural migration applies → **non-silent offer**, pointing at the matching `MIGRATION.md` section.
- `version < current` but no `layout_need_update` entry is newer → compatible; silently bump the deck's `version` to `current`.
- **No `version` (or no `rules.md`)** → treat as pre-stamp → run the existing-deck migration (create `rules.md` with `version`, ensure the 3-file contract, remove any legacy cockpit `**Layout**` line).

This replaces the pre-2.2 cockpit `**Layout**` string check. Purely additive releases never enter `layout_need_update`, so they never trigger a false migration prompt.

## Data model (folder = kind, frontmatter = status)

flightdeck has exactly two axes:
- **Folder = kind** (implicit; never written in frontmatter). Workflow kinds: `sketches/` `specs/` `plans/`. Knowledge kinds: `incidents/` `checklists/` `charts/` `debriefs/`.
- **Frontmatter = status** (explicit, required) + knowledge routing fields (`when_to_read`/`applies_to`/`last_updated`) + a plan's optional `implements:`. The folder is the kind — files carry no type field.

See [templates.md](templates.md) for per-folder frontmatter templates. The full field set is the canonical table below.

## Frontmatter field reference (canonical)

This table is the **single source of truth** for every frontmatter / config field. `templates.md` (ready-to-paste blocks), `folder-semantics.md` (folder purpose), and `walkaround` (validation) defer here — they must not restate field semantics.

| Field | Applies to (kind) | Required? | Read by | Written by | walkaround |
| --- | --- | --- | --- | --- | --- |
| `status` | all workflow + knowledge | **required** | preflight/landing/status/walkaround | status/landing/user | Audit 1 |
| `summary` | workflow (sketches/specs/plans) | recommended | INDEX generation | status/landing/author | INFO if missing |
| `last_updated` | knowledge + workflow | knowledge **required**; workflow recommended | preflight (staleness) | status/landing (auto-bump) | knowledge: Audit 2; workflow: INFO |
| `implements` | plans | optional | reverse-lookup via `plans/INDEX.md` | author | Audit 4 (orphan INFO) |
| `supersedes` | workflow | optional | grep (reverse derived) | author/status | dangling-edge INFO (optional) |
| `related` | workflow | optional | grep | author | dangling-edge INFO (optional) |
| `when_to_read` | incidents/checklists/charts | **required** | preflight routing | author | Audit 2 |
| `applies_to` | incidents/checklists/charts | **required** | preflight routing | author | Audit 2 |
| `skip_when` | incidents/checklists | optional | match-time negative routing | author | not enforced |
| `superseded_by` | knowledge (when `status: superseded`) | **conditional** | redirect from dead-but-in-place file | author | Audit 3 |
| `reviewed` | debriefs | **required** | links to the reviewed spec/topic | author | debrief check |
| `version` | `rules.md` (root) | **required** (rules.md is mandatory) | preflight/walkaround migration detection | preflight setup / auto-bump | Audit 10 |
| `disabled_folders` | `rules.md` | optional (defaulted `[]`) | all entry skills | user | — |
| `git` · `emit_agents_md` · `disabled_gates` · `model_invocable` · `status_auto` · `commit_mode` | `rules.md` (pre-3.0) | **removed in 3.0** — inferred / House-Rules / default (see [Rule resolution order](#rule-resolution-order)); read for 3.x compat only | all entry skills | — | — |

`cockpit.md` header lines (`Last updated` / `Active focus` / `Next session` / `Hanging tasks`) are board fields, not YAML frontmatter.

### Two deliberate asymmetries

**Supersession — edge (workflow) vs status pointer (knowledge).** Knowledge files stay in place (never archived): a reader can land on a dead-but-in-place file, so a *forward* `superseded_by` (required when `status: superseded`) redirects to the replacement. Workflow artifacts archive into `landed/` when done — the old one is history a reader rarely hits cold, so the new artifact carries a *backward* `supersedes` edge and the reverse ("who superseded me") is grep-derived, never stored. Two mechanisms, one principle each — do not unify.

**`last_updated` — required (knowledge) vs recommended + auto-bump (workflow).** Knowledge is found by grep-routing where stale advice is dangerous → required. Workflow is found via INDEX/cockpit → staleness matters less; recommended, and auto-bumped by `status`/`landing` to prevent rot.

## Status (label + recommended flow)

Fixed values, by kind:
- workflow (sketch/spec/plan): `pending / active / awaiting-review / blocked / done / scrapped` (a sketch only ever uses `active` / `scrapped`)
- knowledge: `active / obsolete / superseded`

Recommended flow (documentation, NOT enforced):

```
pending → active → awaiting-review → done
active ↔ blocked
any active state → scrapped
knowledge: active → obsolete | superseded
```

Status is just a label — the user edits it freely; at landing the AI may *suggest* the next typical status (per the recommended flow), applied only after the user confirms. walkaround flags odd values as INFO/warning, never blocks.

## INDEX.md (per-folder + root)

Every artifact folder (including `sketches/`) has an `INDEX.md` — a derived index of that folder's files: one row per file `[file](file) — status — one-line summary` (knowledge folders add `when_to_read`/`applies_to`). The `<!-- AUTO -->` region is machine-maintained (regenerated from each file's frontmatter); an optional hand area sits outside it.

The root `flightdeck/INDEX.md` is a sub-folder directory + global status summary (e.g. `specs/ — 3 (2 active, 1 done)`); it is a downgradeable component.

**Commands read the INDEX first and drill into individual files only on demand** — this is the main token saving (cost scales with folder count, not file count). landing regenerates only the INDEX of folders changed this session; walkaround does a full INDEX↔frontmatter consistency check.

## Folder map

```
flightdeck/
├── cockpit.md   rules.md   INDEX.md
├── sketches/    INDEX.md
├── specs/       INDEX.md
├── plans/       INDEX.md
├── incidents/   INDEX.md
├── checklists/  INDEX.md
├── charts/      INDEX.md   (may hold an imported external project tree)
├── debriefs/    INDEX.md
└── landed/      (archive + HISTORY.md)
```

Reachability entries: `cockpit.md` / `INDEX.md` / `rules.md`. (No bundle README — multi-file topics live as several files in one folder, grouped via the INDEX hand area; only `charts/` may contain an external project subtree.)

**Which folder?** Classify by lifecycle: uncommitted idea → `sketches/`; committed design to review → `specs/`; execution plan → `plans/`; evergreen operational reference → `checklists/`; imported external material → `charts/`; post-incident records → `incidents/`; retrospectives → `debriefs/`.

**Routing is graph-based, not filesystem-based.** A file is "active" only if reachable from an entry (`cockpit.md`, `INDEX.md`, or `rules.md`). **A file nothing links to effectively does not exist** — no session reads it. Custom folders / root files are allowed but MUST be reachable from an entry, or they are orphans.

## Routing — scenario triggers

| Scenario | Read first |
| --- | --- |
| Looking for next task | `cockpit.md` |
| Unsure about a design | `specs/` |
| Running tests / preparing commit | `checklists/` |
| Strange behavior / deja-vu bug | `incidents/` |
| Need outside perspective | `charts/` + `debriefs/` |
| Designing new feature | promote sketch → `specs/` |
| Breaking work into steps | `specs/` → write a `plans/` file |

**How to pick the right incident / checklist**: don't read every file. Both folders use frontmatter (`when_to_read` + `applies_to` + `last_updated`) — grep the metadata, only load full files whose triggers match the current task. Use `last_updated` to judge staleness. An optional `skip_when` field (negative routing — "when NOT to read this") lets a file pre-empt a false match; absent is fine.

### Frontmatter requirements (hard-fail)

Incidents and checklists **MUST** carry frontmatter with `when_to_read`, `applies_to`, and `last_updated`. On a missing field: STOP, report the file path + missing fields to user, offer (a) add now or (b) delete the file. Silent skip = files invisible while their authors believe they're active. That is the worst failure mode for an advice system.

### Proactive incident resurfacing

Before starting a task whose description / file paths overlap with an incident's `applies_to` tags, surface it: "this touches `[tags]`, overlapping with [incidents/X.md](incidents/X.md) — worth a read first?". Do NOT auto-increment `[Case N]` — that only happens on a real, user-confirmed recurrence.

## Authority order (when sources disagree)

Project agent rules > `rules.md` > `cockpit.md` > active folders (`specs/` `plans/` `incidents/` `checklists/` `charts/` `debriefs/`) > `landed/`

`rules.md` sits just below the project's own agent rules: it governs how flightdeck skills behave. `cockpit.md` is the single operational entry below it.

> **"Project agent rules"** = your project's top-level AI instructions file — whatever your AI tool reads on every session.

## Design philosophy

> **Semantic clarity outranks thematic consistency.**

When naming or structuring decisions trigger a conflict between "fits the aviation metaphor" and "reads correctly", clarity wins. The flightdeck metaphor is used because it sharpens operational intent — *not* as a theme to be applied uniformly. Two folders (`specs/`, `sketches/`) intentionally use neutral names because no aviation equivalent improves them. Future concepts face the same test.

Reject:
- aviation roleplay / sci-fi theming / meme interfaces / gamified agent cosplay
- "cute but unclear" terms (e.g., `/stuck → /request-vector` was rejected during rebrand — `/stuck` already reads correctly)
- forcing every new term into the metaphor

## Lifecycle

```
sketch → (promote = write the design) spec → plan
```

Each plan carries optional `implements: specs/<x>.md`. `location` (active vs `landed/`) is derived from landing a done/scrapped item. Folder says the kind; frontmatter `status` says the state.

A scrapped sketch stays in `sketches/` (marked `status: scrapped`), never archived to `landed/`; delete by hand at will.

**Knowledge lifecycle:** `active → obsolete | superseded` (set `superseded_by` when superseding). Landing knowledge is optional — files may stay in place indefinitely; no "to-land" reminder.

## Exit ritual

90% of exits are obvious — classify and write directly. Only truly ambiguous items invoke brainstorming. The full decision tree (classification heuristics, hanging-task gate, INDEX regeneration, cockpit update) lives in [exit-ritual.md](exit-ritual.md) and is run by `/flightdeck:landing`.

After classifying: update `cockpit.md` (`Last updated` + `Next session` + any `Hanging tasks` changes); append to `landed/HISTORY.md` when no-git; then commit per the commit override (`confirm` default; skipped entirely under no-git). landing regenerates the INDEX of any folders changed this session.

## Write gate

`flightdeck/` records only content that **changes future behavior, influences decisions, or gets referenced repeatedly**. Session byproducts, debug logs, and chat play-by-plays do not qualify. Gate strictly.

## Templates

See [templates.md](templates.md) for `sketch` / `spec` / `plan` / `incident` / `checklist` / `debrief` / `cockpit.md` / `rules.md` / `HISTORY.md` / `INDEX.md` templates.

## Relation to project agent rules

| | Project agent rules | `flightdeck/` |
| --- | --- | --- |
| Loaded | every session | on demand |
| Contains | rules + trigger table + style | state + knowledge + history |
| When in conflict | wins | yields |

## Incident promotion gates

Multi-criterion gate evaluated by `landing`. An incident reaches the **checklist promotion gate** when ALL three hold:
1. `[Case N] count ≥ 3` in the incident file.
2. Cases recurred across **≥ 2 distinct sessions** (same-session triple-hits don't count).
3. Remediation pattern is **stable across cases** (the "next time avoid X" rule reads similarly across all cases — not 3 unrelated fixes papering over one symptom).

When the gate fires, `landing` prompts: "Promote `incidents/X.md` to `checklists/X.md`?". User confirms — promotion is **never automatic**.

A separate **project-rules upgrade gate** fires when a promoted incident continues to recur after promotion. Then add a one-liner to project agent rules and mark the incident `Status: upgraded → project rules`. Do not delete the incident.

## Common mistakes — STOP and reclassify

| Mistake | Fix |
| --- | --- |
| Same fact in cockpit + incident + spec | One authoritative source; others link via `[name](incidents/X.md)` |
| Scratch written into flightdeck/ | Transient scratch lives in project-root `tmp/` (gitignored), not flightdeck. |
| `incidents/` writes "forgot / careless" | Root cause must be a wrong assumption / wrong model / wrong process. |
| `debriefs/` paste-only, no disposition | Disposition required (adopt / reject / defer). No disposition = hanging task. |
| Brainstorming where every knowledge item belongs | Heuristics catch 90%. Default-brainstorm is the failure mode. |
| Cockpit > 80 lines | Trim immediately — drop finished items, move design detail to the relevant `specs/` file; history is `git log` / `landed/HISTORY.md`, not cockpit. |
| Bumping `Last updated` on every commit / typo / grep | Signal pollution. Only bump on 4 triggers in exit-ritual.md `Cockpit update`. |
| Incident / checklist without required frontmatter | STOP, report file path + missing fields. Add or delete before proceeding. |
| Incident / checklist with `last_updated` > 1 year in a fast-moving project | Likely stale advice. Bump after re-verifying or flip to `status: obsolete`. |
| "Save in case it's useful later" | No. Gate strictly. |
| "I'll fill the debrief disposition next session" | No. Hanging task now. |

## Cross-references

The flightdeck convention describes WHAT to write and WHERE; the tool that produces the content is up to you (hand-write, use any AI skill, or ad-hoc LLM).

**Optional companions** (Claude Code with the `superpowers` plugin installed):
- `superpowers:brainstorming` → produces well-structured designs that fit `specs/`.
- `superpowers:writing-plans` → produces task lists that fit `plans/`. Plan files use `- [ ]` checkboxes for executing-plans tracking; **flightdeck does not require flipping these** — progress lives in `cockpit.md` + commit log.

These are convenient but **not required** — flightdeck accepts content from any source.

The `flightdeck/` directory structure is **tool-agnostic** — any AI assistant can follow these conventions via project-level instructions. See `adapters/` for per-tool install paths.
