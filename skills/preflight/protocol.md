# flightdeck protocol (reference)

> Loaded on demand by `preflight` (and referenced by `landing` / `walkaround`). This is the protocol "textbook": the data model, folder semantics, routing, authority order, write gate, and lifecycle. The operational entry ritual lives in [SKILL.md](SKILL.md).

## Core principle

`flightdeck/` is a directory convention organized by **when you read what** — a persistent workbench for AI-assisted coding. Write strictly: only content that changes future behavior, influences decisions, or gets referenced repeatedly.

## Project rules (`rules.md`)

`flightdeck/rules.md` is an **optional** project-config file read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`, `status`). It carries a closed set of structured toggles plus free-prose house rules. Absent file = defaults (git on, emit on, all folders/gates active, all rituals manual).

Toggles: `git` · `emit_agents_md` · `disabled_folders` · `disabled_gates` · `model_invocable` · `status_auto`. Full schema + degradation rules: [templates.md § rules.md](templates.md#rulesmd).

### Key admission policy (anti-sprawl)

The toggle set is **closed**: an unknown key is ignored with a one-line warning, so config never grows by accident (a typo can't add behavior). It grows only by a deliberate decision — and a proposed new key MUST pass **all four** of these, or it does not belong in `rules.md`:

1. **Per-project varying** — it encodes a preference/policy that genuinely differs from project to project, not a universal default everyone would set the same way.
2. **Not a protocol contract** — it is NOT a structural contract. Layout version, the `<!-- AUTO -->` region mechanics, graph-reachability rules, folder kinds, and the *semantics* of the existing toggles stay hard-coded. `rules.md` tunes behavior; it never redefines the protocol.
3. **Real demand now** — a concrete project has actually hit the wall (YAGNI). No speculative keys: park the idea in a spec backlog until a real need appears (e.g. `cockpit_max_lines` / `staleness_days` remain backlog precisely because nothing has needed them yet).
4. **Not foldable** — it cannot be expressed through an existing key. No redundant or overlapping toggles.

A key that fails any point is either hard-coded protocol, a backlog item, or redundant — not a `rules.md` toggle.

When `git: false`, skills skip all git reconcile/commit steps and use `landed/HISTORY.md` for the staleness check and history. When a folder is in `disabled_folders`, it is never suggested and never flagged as an orphan. Honor house-rules prose, but it cannot override the four toggles or the project's own agent rules.

## Data model (folder = kind, frontmatter = status)

flightdeck has exactly two axes:
- **Folder = kind** (implicit; never written in frontmatter). Workflow kinds: `sketches/` `specs/` `plans/`. Knowledge kinds: `incidents/` `checklists/` `charts/` `debriefs/`.
- **Frontmatter = status** (explicit, required) + knowledge routing fields (`when_to_read`/`applies_to`/`last_updated`) + a plan's optional `implements:`. The folder is the kind — files carry no type field.

See [templates.md](templates.md) for per-folder frontmatter templates.

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

After classifying: update `cockpit.md` (`Last updated` + `Next session` + any `Hanging tasks` changes); append to `landed/HISTORY.md` when `git: false`; then commit (unless `git: false`). landing regenerates the INDEX of any folders changed this session.

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
