# Folder semantics

Reference for every `flightdeck/` subdirectory: what it holds, naming convention, lifecycle, and links to related folders.

## Deck layout (3.x: full, always)

As of 3.x, both `preflight` first-time setup and `install --scaffold` lay the **full layout** — every folder with its `INDEX.md`, plus the 3-file contract. There is no longer a minimal/full choice (the `scaffolds/minimal` variant was removed).

| Concept | What it means |
| --- | --- |
| **Full layout** (what init creates) | all folders (`sketches/ specs/ plans/ incidents/ checklists/ charts/ debriefs/ landed/`), each with its `INDEX.md`, + `cockpit.md` + `rules.md` + `landed/HISTORY.md` |
| **3-file contract** (validation floor) | `rules.md` + `cockpit.md` + `landed/HISTORY.md` must exist (walkaround CRITICAL if missing) — the *floor*, not a scaffold variant |

**Empty is the normal initial state.** A freshly scaffolded deck has empty folders + empty `INDEX.md` files — expected, not an anti-pattern. Under the full layout a **missing** known folder is the anomaly (walkaround flags it); an **empty-but-present** folder / `INDEX.md` is fine and never flagged. (This reverses the pre-3.x "add folders on demand" guidance.)

## Routing model

**Flightdeck is graph-routed, not filesystem-routed.** A file is "active" only if it is reachable from some entry — `cockpit.md`, `INDEX.md`, or `rules.md`. **A file not reachable from any entry effectively does not exist** (no session will ever read it). `walkaround` audits reachability.

Reachability edges are markdown links from an entry. Custom folders / root files are allowed — flightdeck favors extensible conventions over a locked taxonomy — **but they must be reachable from an entry**, or `walkaround` flags them as orphans.

## Which folder? (decision table)

Classify by lifecycle — the folder is the kind, so files carry no type field:

| What you have | Goes in |
| --- | --- |
| Uncommitted idea (not yet ready to act on) | `sketches/` |
| Design to review or implement | `specs/` |
| Implementation plan (optionally `implements:` a spec) | `plans/` |
| Bug + root cause worth not repeating | `incidents/` |
| Repeated procedure (second run = pattern) | `checklists/` |
| Imported external material (competitor code, RFCs, articles) | `charts/` |
| External review / AI critique + disposition | `debriefs/` |

The common mistake is keeping an evergreen reference in `specs/` or `plans/`. A spec/plan is a *design or plan you intend to build and then archive*; an evergreen standard you consult repeatedly belongs in `checklists/`. (`checklists/` = authored operational reference; `charts/` = imported external material — keep that split clear.)

## The folders + entry files

```
flightdeck/
├── cockpit.md          # The single must-read entry (≤80 lines): focus / next / hanging
├── rules.md            # Mandatory file (3-file contract); content optional — read first by every entry skill
├── INDEX.md            # Root index: subfolder directory + global status summary
│
├── sketches/           # Uncommitted ideas (status: active / scrapped)
│   └── INDEX.md
├── specs/              # Designs to review or implement
│   └── INDEX.md
├── plans/              # Implementation plans (carry optional implements:)
│   └── INDEX.md
├── incidents/          # Post-incident records (bugs + root cause)
│   └── INDEX.md
├── checklists/         # Operational reference (procedures, conventions, standards)
│   └── INDEX.md
├── charts/             # Imported external material (may hold an external project tree)
│   └── INDEX.md
├── debriefs/           # External review feedback + disposition
│   └── INDEX.md
│
└── landed/             # Archive umbrella — mirrors source structure on demand
    └── HISTORY.md      # Landing log, newest first (required when rules.md git: false)
```

## Entry files

### `cockpit.md` — the single must-read

**The only required file.** Read first, updated last. Hard ceiling: **80 lines**.

The 80-line ceiling is cognitive-load engineering for the human + AI reading cockpit at every session start — treat it as a load-bearing constraint, not a style preference.

Contains:
- `Last updated: YYYY-MM-DD by <who> (<one-line>)`
- `Active focus: <current main thread>`
- `## Next session` — 1–5 concrete items.
- `## Hanging tasks` — open items blocking a clean landing (hand-maintained; decoupled from INDEX auto-summaries).

`cockpit.md` is the pure focus layer: "what am I working on now". Status visibility is delegated to INDEX — look at the relevant folder's INDEX (or the root INDEX) to see the full picture.

### `rules.md` — project config (mandatory file, optional content)

Read first by every entry skill. As of 3.0 it carries `version` + `disabled_folders` + free-prose house rules (`### Project conventions` + `### Autonomy overrides`). Most behavior is inferred (git/emit from `.git` / `AGENTS.md` presence) or defaulted and overridden via the `### Autonomy overrides` segment — see [protocol § Rule resolution order](protocol.md#rule-resolution-order). The **file** is mandatory (part of the 3-file contract — `walkaround` CRITICAL if missing) and must carry `version`; its **content** is optional — a minimal `rules.md` = full-auto defaults. Full schema: [templates.md § rules.md](templates.md#rulesmd).

### `INDEX.md` — root index

The root `flightdeck/INDEX.md` is a subfolder directory plus global status summary, generated from each subfolder's `INDEX.md`. Example:

```markdown
# flightdeck — INDEX

<!-- AUTO:root -->
- specs/ — 3 (2 active, 1 done)
- plans/ — 2 (1 active, 1 blocked)
- incidents/ — 1 active
- checklists/ — 1 active
- charts/ — 2 imported
- debriefs/ — 1 active
- sketches/ — 4
<!-- /AUTO -->
```

Note: `charts/` rows show a file/project count and "imported" rather than a status count, because imported external files do not carry uniform flightdeck frontmatter.

The root INDEX is a **downgradeable component** — if the project finds per-folder INDEXes sufficient and the root INDEX underused, it may be removed without affecting the model.

### `landed/HISTORY.md` — landing log

Lives under `landed/`, so it is **outside the routing graph** (never read at session start). An **add-only** log (never edit or delete past entries), one line per landing, **newest first**.

**Required when `rules.md` sets `git: false`** (no commit log to lean on); optional otherwise.

## INDEX.md (per-folder)

Every artifact folder — including `sketches/` — has its own `INDEX.md`. This is the derived index for that folder: one row per file showing file, status, and a one-line summary. `incidents/`, `checklists/`, `charts/` rows add `when_to_read` / `applies_to`; `debriefs/` rows instead show the reviewed spec/topic + date (no trigger routing).

Structure:

```markdown
# specs/ — INDEX

<!-- AUTO:specs -->
- [2026-06-01-auth-redesign.md](2026-06-01-auth-redesign.md) — active — redesign the auth layer for OAuth2
- [2026-05-10-billing.md](2026-05-10-billing.md) — done — billing module spec
<!-- /AUTO -->

<!-- Optional hand area: grouping notes, multi-file topic labeling, etc. AI does not touch this. -->
```

Rules (canonical elsewhere — pointers, not restated here):
- **Row format** + the build-from-frontmatter-never-body rule → [exit-ritual § Row format](exit-ritual.md#row-format--how-each-auto-row-is-built-single-source-of-truth) (the bundled `flightdeck_index.py` implements it).
- **Regeneration scope** (landing = changed folders only; walkaround = full check) + the **read-INDEX-first** token saving → [protocol § INDEX](protocol.md).
- The hand area **outside** `<!-- AUTO -->` is never touched by the AI.

## Folder details

> Per-folder frontmatter **blocks** live in [templates.md](templates.md); field **semantics** (required-ness, who reads/writes) are canonical in [protocol.md § Frontmatter field reference](protocol.md#frontmatter-field-reference-canonical). The sections below describe folder *purpose* and *lifecycle* only.

### `sketches/` — uncommitted ideas

Unstarted ideas waiting for a trigger. `status: active` or `scrapped`. **The folder is the kind — files carry no type field; no `implements:`.**

Naming: `<topic>.md` (no date prefix — ideas are timeless until acted on).

**Promote** a sketch to a spec when it becomes actionable: move `sketches/foo.md → specs/foo.md` and set `status: pending`. The sketch leaves `sketches/` on promotion.

**Scrap** a sketch (`status: scrapped`) when the idea is abandoned. A scrapped sketch stays in `sketches/` (marked `status: scrapped`); it is **never archived to `landed/`**. Delete by hand at will — `walkaround` does not flag deletions of scrapped sketches.

Transient session scratch belongs at project-root `tmp/` (gitignored), not here.

### `specs/` — designs

Committed design documents to review or implement. A spec captures the *what* and *why* of a change; it is the output of the brainstorming / design stage.

Naming: `YYYY-MM-DD-<topic>.md` (date helps order by recency; specs are time-bound designs).

The folder is the kind — files carry no type field. No `implements:` (that goes on the plan side).

Lifecycle: when a spec is done and all its plans are complete, `land` it — move to `landed/specs/foo.md`. The spec leaves the active routing set but its history is preserved.

### `plans/` — implementation plans

Task-level breakdowns of how to execute a spec (or a standalone piece of work). Plans carry the optional `implements:` back-reference to the spec they execute.

Naming: `YYYY-MM-DD-<topic>.md`.

`implements:` is a single unidirectional reference. To see which plans implement a given spec, read `plans/INDEX.md` — do NOT add a reverse `implemented_by:` field to the spec.

A plan without `implements:` is valid but `walkaround` surfaces an INFO ("orphan plan — no spec linked").

### `incidents/` — post-incident records

Mistakes worth not repeating. Format strictly enforces useful root cause (template in [templates.md](templates.md#incident-report-body)).

Naming: `<topic>.md` (no date prefix — incident reports are reference, not log).

Recurrence rule: same incident happens again → **append `## [Case N]`** to existing file. Do not create a new file. Repeated recurrence (≥3 times or single severe case) → promote one-liner to your project agent rules.

`last_updated` must be bumped on each Case append or status flip (per the canonical field table).

### `checklists/` — procedures

Authored **operational reference**: reusable checklists, conventions, and reference standards worth consulting more than once.

Naming: `<topic>.md` (no date prefix — checklists are stable resources).

Promotion rule: a process becomes a checklist the **second** time you run it. First time = ad-hoc. Second time = pattern.

`status: obsolete` = the external constraint no longer exists; `status: superseded` = a newer checklist replaces this one (set `superseded_by`). Both may stay in place indefinitely — no automatic "to-land" reminder.

### `charts/` — external material

External docs, competitor source code, RFCs, blog posts, etc. — a single place for "where do I find that thing".

Naming: `<source>-<topic>.md` (e.g. `boltframe-shape-layer.md`, `rfc-6749.md`).

**Imported external project tree**: `charts/` is the only folder where a subdirectory is permitted. When importing an entire external project (competitor code, an RFC suite, a large article series), place it at `charts/<project>/` and add a `charts/<project>/INDEX.md` as a human-readable guide to the project's contents. The root `charts/INDEX.md` row for that project shows project count + "imported" rather than a status count (imported files do not carry uniform flightdeck frontmatter).

### `debriefs/` — external review feedback

Raw feedback from reviewers (other AIs, colleagues) + your **disposition** (adopt / reject / defer).

Naming: `YYYY-MM-DD-<spec-or-topic>-<reviewer>.md`.

Retrieved by the spec/topic reviewed + date (`reviewed:` field), not by a trigger — so no `when_to_read`/`applies_to`.

Disposition rule: no debrief can exist in `debriefs/` without a disposition section. If disposition is incomplete, add a hanging task to `cockpit.md` ("finish disposition of `<file>`") and do not close the session.

### `landed/` — archive umbrella

Top-level archive for completed or retired work. `landed/` **mirrors any source folder on demand** — create the matching subdirectory the first time you archive something of that kind.

- `landed/specs/` — specs archived after the work is done.
- `landed/plans/` — plans archived after execution.
- `landed/incidents/`, `landed/checklists/`, `landed/charts/`, `landed/debriefs/` — obsolete-but-historical reference moved out of the active set.
- `landed/HISTORY.md` — append-only landing log.

Archiving vs `status: obsolete/superseded`: flip `status` to keep a dead file in place (still reachable, marked dead); **move to `landed/`** to remove it from the active routing set while preserving history. Archived files lose to current state in [source-of-truth precedence](protocol.md#source-of-truth-precedence-when-sources-disagree). Routing already excludes everything under `landed/`.

Archived files are **exempt from status and INDEX audits** — `walkaround` does not check `landed/`.

## Multi-file topics — no subfolders

When one topic needs several files (a multi-chapter reference, a large spec), keep **all files in the same folder**. Group them in that folder's `INDEX.md` hand area (outside the `<!-- AUTO -->` region) with a label like `### Auth redesign (3 files)`.

**Do NOT create subfolders inside `specs/`, `plans/`, `incidents/`, `checklists/`, or `debriefs/`.** Subfolders reintroduce the "what kind is the subfolder" question and break the flat routing model.

The sole exception is `charts/`: an imported external project may carry its own directory tree — see the `charts/` section above.

## README → INDEX

Within flightdeck conventions, always use `INDEX.md` — never `README.md`. `INDEX.md` precisely communicates "directory navigation" (as opposed to "project introduction").

The repository-root `README.md` (the GitHub project intro) is a standard project file and is **not affected** by this rule.

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
| --- | --- | --- |
| Empty subdirs created to "establish the convention" | Pressure to fill → low-signal writes | Minimal setup; add folders on demand |
| Same fact duplicated across folders | Drift → trust collapses | One authoritative source; others link |
| Incident report files named `2026-05-23-bug.md` | Date noise; impossible to find by topic | Use `<topic>.md` |
| `tmp/` placed inside `flightdeck/` | Junk gets committed | `tmp/` lives at project root, gitignored |
| Subfolders inside `specs/` / `plans/` / `incidents/` / `checklists/` / `debriefs/` | Breaks flat routing; "what kind is the subfolder?" | Keep all files in the folder; group in INDEX hand area |
| Using `README.md` inside flightdeck conventions | Bundle README approach retired | Use `INDEX.md` (repo-root `README.md` is unaffected) |
| Plan with no `implements:` and no explanation | Orphan plan is invisible to spec→plan tracing | Add `implements:` or note "standalone" in the plan body |
| Checklist or incident without `when_to_read` | Invisible to skill routing | Add `when_to_read` frontmatter |
