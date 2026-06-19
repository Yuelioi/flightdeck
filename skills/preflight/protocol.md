# flightdeck protocol (reference)

> Loaded on demand by `preflight` (and referenced by `landing` / `walkaround`). This is the protocol "textbook": the data model, folder semantics, routing, authority order, write gate, and lifecycle. The operational entry ritual lives in [SKILL.md](SKILL.md).

## Core principle

`flightdeck/` is a directory convention organized by **when you read what** — a persistent workbench for AI-assisted coding. What earns a place is governed by the [write gate](#write-gate).

## Naming iron-rule (metaphor vs mainstream)

The aviation metaphor is reserved for the **interaction surface** — slash commands, rituals, and the cockpit: `flightdeck` / `cockpit` / `preflight` / `walkaround` / `landing` / `launch` (including the every-session `cockpit.md` dashboard). The **data model — folders, statuses, fields — uses mainstream, ordinary names** a developer can guess cold. A newcomer who doesn't know the metaphor must still be able to guess what each folder / status / field is for.

Consequence: the two metaphor folder names became mainstream — `charts/ → references/`, `landed/ → archive/`. Status values are mainstream (`idea/active/done`, `active/stale/obsolete`). `flightdeck/` (the product root) and `cockpit.md` (interaction surface) keep their names. This rule outranks thematic consistency — see [Design philosophy](#design-philosophy).

## Project rules (`rules.md`)

`flightdeck/rules.md` is a **mandatory** project-config file read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`, `status`). It is part of the **minimal contract** (`rules.md` + `cockpit.md`) and must carry a `version` field — a static identity stamp written by `launch` at deck creation, deliberately kept as the 3.0→3.1 migration anchor; no ritual reads or bumps it at runtime.

`rules.md` carries `version` plus recorded-config fields (`runtime`: `uv|python|node`, stamped by launch; `agents_md`: `auto|off`) and free-prose house rules in two subsections:

- `### Project conventions` — deck-local conventions.
- `### Rules` — behavioral rules **the AI maintains from your natural-language requests** (free prose, not a fixed vocabulary). There is **no human toggle catalog**: instead of editing magic-string syntax, you tell the AI a persistent preference ("ask before committing") and the AI appends a free-prose rule here (noting source/date) and honors it. The AI is both author and reader, so the rule needs no canonical phrasing.

Everything else resolves from **built-in defaults** (see Rule resolution order). Full schema + ready-to-paste template: [templates.md § rules.md](templates.md#rulesmd).

## Rule resolution order

Every skill resolves each behavior in this order — **first hit wins**:

1. **Frontmatter field** — a recorded-config field in `rules.md` frontmatter (`runtime`, `agents_md`) read directly; no inference needed. **Frontmatter fields outrank conflicting `### Rules` prose** for the keys they cover (see [templates.md § rules.md](templates.md#rulesmd)).
2. **Deck rule** — a matching free-prose rule in `rules.md` `### Rules` (the AI reads and honors it; it overrides the default).
3. **Built-in default** — `commit` = **local commit auto, push asks** (local is reversible — reset/amend; push is outward, gated); **all five rituals (`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`) self-invocable**; `status` auto-flips `start` (idea→active) and `done` (on approval) but **never archives** (landing's cross-reference-aware judgment); **`landing` auto-runs on `done`** (debounced to once at end-of-turn). Reversible runs without asking; the one outward action (push) stays gated — see [Act-report-close loop](#act-report-close-loop).

There is **no environment-inference step** (3.0): `runtime` and `agents_md` are recorded frontmatter fields read at step 1 — never re-probed; `git` is a launch-enforced install precondition (launch's doctor offers `git init` and refuses if you decline or git is absent, then it holds at runtime), not a resolved item.

**deck root** = the directory containing `rules.md` (the parent of `flightdeck/`); if none is found, fall back to cwd **with a warning** (never silent — else a misconfigured run looks like it found a deck when it didn't).

**Override authority** (which config wins): **the project's agent instruction file (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`, per the running agent) > deck rules (`rules.md` `### Rules`) > flightdeck defaults.** flightdeck always honors the project's own agent rules above its own deck rules. Internal conflicts among deck rules are the user's responsibility — flightdeck never auto-resolves contradictory rules (it may passively flag one, never silently pick).

A deck rule is **free prose the AI interprets** — there is **no magic-string table, no lenient-substring matcher, no canonical-phrase requirement** (deleted in 3.0: the AI authors and reads its own rules, so a fixed vocabulary served no one). There is no self-invoke override (all five rituals always self-invoke), no `auto land` toggle (archiving is landing's judgment), no `runtime` toggle in `### Rules` (`runtime` is a required frontmatter field stamped by launch — not a free-prose setting), and no `disabled_folders` (empty folders are simply not flagged).

**Runtime dispatch (the `runtime` field).** The `runtime` frontmatter value (`uv` | `python` | `node`, stamped by `launch`) selects the **call form** for every bundled script: `uv run <pkg>/scripts/<name>.py` / `python <pkg>/scripts/<name>.py` / `node <pkg>/scripts/<name>.js` — the `.py` and `.js` are byte-parity twins sharing a basename stem. A script runtime is **mandatory in 3.0** — there is no hand-rebuild markdown fallback. A recorded runtime that cannot be found is a **hard failure** at the script step: surface `⚠ recorded runtime '<x>' not found — update rules.md (runtime:) or reinstall` and stop that step (never silently fall through to manual reconstruction). `preflight` stays read-only / zero-write even here — it does not repair; it appends a non-blocking `⚠ recorded runtime broken` note and continues its read-only report.

## Data model (folder = kind, frontmatter = status)

flightdeck has exactly two axes:
- **Folder = kind** (implicit; never written in frontmatter). Workflow kinds: `specs/` `plans/`. Knowledge kinds: `incidents/` `checklists/` `docs/` `references/`.
- **Frontmatter = status** (explicit, required) + knowledge routing fields (`when_to_read`/`applies_to`/`last_updated`) + a plan's optional `implements:`. The folder is the kind — files carry no type field.

**Nesting by axis:** knowledge kinds (`incidents/` `checklists/` `docs/` `references/`) **may nest by area** (`<folder>/<area>/` with its own `<folder>/<area>/INDEX.md`; a subdirectory is only an organizational partition within the *same* kind, never another kind). Workflow kinds (`specs/` `plans/`) are **strictly flat** — they drain into `archive/` after `done` so the active set never accumulates; group by feature via the INDEX hand area, not subdirectories.

See [templates.md](templates.md) for per-folder frontmatter templates. The full field set is the canonical table below.

## Frontmatter field reference (canonical)

This table is the **single source of truth** for every frontmatter / config field. `templates.md` (ready-to-paste blocks), `folder-semantics.md` (folder purpose), and `walkaround` (validation) defer here — they must not restate field semantics.

| Field | Applies to (kind) | Required? | Read by | Written by | walkaround |
| --- | --- | --- | --- | --- | --- |
| `status` | all workflow + knowledge | **required** | preflight/landing/status/walkaround | status/landing/user | Audit 1 |
| `summary` | workflow (specs/plans) | recommended | INDEX generation | status/landing/author | INFO if missing |
| `note` | workflow | optional | cockpit `## In Progress` row + walkaround render | author/status | rendered as `[note: …]`, not validated |
| `verify` | workflow (`done`) + knowledge (`stale`) | optional | preflight/landing/walkaround verify-debt scan + `flightdeck_index.py --verify-pending` | author/status/landing | present = owes verification, value = one-line how-to (see [verify field](#verify--the-verification-marker)) |
| `last_updated` | knowledge + workflow | knowledge **required**; workflow recommended | routing (staleness judgment) | status/landing (auto-bump) | knowledge: Audit 2; workflow: INFO |
| `implements` | plans | optional | reverse-lookup via `plans/INDEX.md` | author | Audit 4 (orphan INFO) |
| `supersedes` | workflow + knowledge | optional | grep (traceability only — NOT an archival-pinning edge) | author/status | dangling-edge INFO (optional) |
| `related` | workflow | optional | grep | author | dangling-edge INFO (optional) |
| `when_to_read` | incidents/checklists/docs/references | **required** | preflight routing | author | Audit 2 |
| `applies_to` | incidents/checklists/docs/references | **required** | preflight routing + landing stale detection (mixed list: plain words = routing tags; entries containing `/` = source paths, prefix-matched against changed paths) | author | Audit 2 |
| `when_to_update` | docs/references (knowledge) | recommended for graduate-out docs; optional otherwise | humans (the stale *reason*; runtime stale detection matches `applies_to` paths) | author (set at graduate time) | flag if absent on a graduate-tagged doc |
| `skip_when` | incidents/checklists | optional | match-time negative routing | author | not enforced |
| `recurrences` | incidents | optional (default 1) | INDEX-row render + promotion gate | landing/status (auto-bump on a clear recurrence) | int ≥ 1; ≈ 1 + `[Case N]` count |
| `graduate` | specs | optional | landing (graduate seam trigger) | author / AI (front-loads at creation or during active life) | — |
| `superseded_by` | knowledge | **retired in 3.0** — old `status: superseded` redirect field; no longer written; kept here as a tombstone so walkaround can flag live instances | — | — | flag if present on a non-archive file |
| `version` | `rules.md` (root) | **required** (rules.md is mandatory) | — (static identity stamp; future 3.0→3.1 migration anchor) | **launch only** (init) | — |
| `synced` | checklists/docs (vendored only) | optional (boolean marker, no path) | `/flightdeck:sync` + walkaround sync-drift (`flightdeck_index.py --sync-status`) | `sync` (stamped on initial vendoring / on `push` promote) | sync-drift audit: validate the relpath invariant (no source at the same relpath in the master store → `dangling`); absence **never** warns |
| `consumers` | checklists/docs (master-store files only) | master-store-only (stripped from consumer copies) | `/flightdeck:sync --fanout` (fan out to every registered consumer deck) | written by `--register-consumer`; cleaned by `--prune-consumers` | presence in a consumer copy → WARNING (illegal) |

`cockpit.md` board fields (`Updated` / `Focus` / `Pointers` / `## Next` / `## In Progress` / `## Key Context` / `## Pending Review` / `## Hanging Tasks`) are not YAML frontmatter. **Pointer-vs-record boundary:** cockpit materializes only irreducible judgment plus one cheap projection (`## In Progress`); records live in their homes — history → `git log`, progress → plan `## Progress`, goal/criteria/method → spec body, durable invariants → `rules.md`, knowledge → folder INDEXes — and cockpit only links to them. `## In Progress` is an AUTO region derived from `status: active` spec/plan (rendering a truncated summary head); `## Next` is AI-maintained — see [templates.md § cockpit.md](templates.md#cockpitmd).

### Supersession model

**`supersedes` edge (traceability-only, NOT archival-pinning).** The new artifact may carry `supersedes: <old-artifact>` pointing at the one it replaces — this is a traceability annotation for humans and grep, nothing more. It is **not** an archival-pinning edge: `flightdeck_index.py --archivable` does **not** include it in the blocking-inbound-edge set (only `implements:` pins). The old artifact's death is driven **independently** — by the user flipping it to `obsolete`, which the rituals then drain to `archive/`. Once archived, a `supersedes` pointer into `archive/` is a legal cold history pointer; no maintenance required.

**`superseded_by` is retired (3.0).** The old forward-redirect field (`superseded_by` required when `status: superseded`) was predicated on knowledge files staying in place indefinitely. Since `obsolete` is now a drain state (rituals move it to `archive/` — see [Status ⟂ location](#status--location-two-orthogonal-axes)), the dead file is no longer on disk long enough to need a redirect. `superseded_by` must not be written on new files; `walkaround` flags any live instance.

**`last_updated` — required (knowledge) vs recommended + auto-bump (workflow).** Knowledge is found by grep-routing where stale advice is dangerous → required. Workflow is found via INDEX/cockpit → staleness matters less; recommended, and auto-bumped by `status`/`landing` to prevent rot.

### `verify` — the verification marker

**`verify` is a status add-on marker, NOT a status and NOT a state machine.** It is read **together with** `status` (sibling to `note:` / `resolved_by:` / `when_to_update:`), never on its own. Presence/value/absence carry the whole contract:

- **present** = the artifact **owes verification** (substantively written/done, but not yet confirmed against reality);
- **value** = a one-line **how-to-verify** note (e.g. `verify: phase-4 live validation on each host`) — so the debt's *content* survives any cockpit edit/regen and the deterministic scan can re-surface it;
- **absent** = verified, or no verification needed.

Binary present/absent only — there is **no `verify: failed` value** (a failed verification revives the artifact and **keeps** `verify`; see [Non-blocking verification](#non-blocking-verification)). Optional; applies to a knowledge `stale` artifact (written-but-unverified) and a workflow `done` artifact (substantively-done-but-unverified). **It is not a 4th workflow status** — the status value sets are unchanged (workflow `idea/active/done`, knowledge `active/stale/obsolete`); `verify` only modifies how a given status reads. Every preflight/landing/walkaround re-surfaces the debt via a deterministic scan of the `verify` field across the active tree + `archive/` (`flightdeck_index.py --verify-pending`).

## Status ⟂ location (two orthogonal axes)

flightdeck separates **two independent axes** — the source of the historical "done = landed" confusion is collapsing them:

- **status** ∈ `{idea, active, done}` (workflow) — *which step the artifact reached*. Explicit frontmatter value.
- **location** ∈ `{source folder, archive/}` — *whether it's still in the active area*. **Derived, NOT a frontmatter field** (computed from "is it under `archive/`?"), **but a first-class concept**: it drives **routing** (`archive/` is excluded from the routing graph entirely) and **archival judgment** (landing decides whether a `done` item lands). Don't dismiss it as unimportant just because it isn't written down.

A `done` artifact has two legal locations: **done-but-unlanded** (still in `specs/`, because an `active` artifact still references it) or **done-and-archived** (moved into `archive/`).

**Invariants (hard):**
- `archived` / `landed` are **never status values** — no file ever writes `status: landed`.
- **Only landing's Land Routine may move anything into `archive/`.** status never archives.
- The AI **never** hand-writes an archival label, and **never** claims an item is archived without actually running landing.

One sentence: **status says "which step", location says "in the active area or not", and landing is the only mover.**

Fixed values, by kind:
- workflow (spec/plan): `idea / active / done`
- knowledge: `active / stale / obsolete`

(`superseded` is **deleted** as a knowledge status value — the old `superseded` + `superseded_by` redirect mechanism is retired; see [Supersession model](#supersession-model). Live `superseded` knowledge files should be re-evaluated: flip to `obsolete` and drain, or flip to `active` if still valid.)

Recommended flow (documentation, NOT enforced):

```
idea → active → done   (rejected = delete the file)
knowledge: active → stale (auto, ritual) → active (user-reviewed) | obsolete (user-confirmed dead)
          active → obsolete (user-confirmed dead, no stale step required)
```

`stale` = **pending-review: suspected outdated _or_ newly produced but unverified** — two sources distinguished by the [`verify` field](#verify--the-verification-marker): **has `verify`** = written-but-unverified; **no `verify`** = `when_to_update`-matched suspected-outdated. The status token is unchanged; only the meaning broadens.

- `idea` = unstarted thought / design (the to-start pool); only in `specs/INDEX`, **not** in cockpit. No date prefix.
- `active` = being worked on; **auto-appears in cockpit `## In Progress`**. The `idea→active` flip auto-adds the `YYYY-MM-DD-` prefix.
- `done` = work complete; stays in the source folder until the landing ritual archives it into `archive/` (**done ≠ archived**).
- **Rejected / abandoned** = the artifact is **deleted outright** (only on explicit user instruction). git log is the history, with a one-line reason in the commit body. There is no `scrapped` status value and no tombstone group.

### Status transition authority table (single source of truth)

This is the **one authoritative table** for automatic status flips. Other files (`status` SKILL, `exit-ritual`) point here and do not restate the rules.

Workflow chain: `idea → active → done`. Rejection **deletes** the file (no scrapped status).

**Workflow:**

| Trigger | Flip | Who | Auto? |
|---|---|---|---|
| Write a new spec/plan (capture only, not yet started) | →`idea` | status | always |
| Write a new spec/plan **and already working on it** | direct →`active` (legal skip past idea) | status | always |
| Start working on an existing idea | `idea→active` (+ `YYYY-MM-DD-` prefix + regen cockpit `## In Progress`) | status | default (a deck `### Rules` entry can disable) |
| User approves / signs off | `active→done` (flips `done` only, **does not archive**) | status / landing seam | always |
| A direction is rejected | **delete the file** (git log + commit-body reason) | **user-explicit instruction only** | **never auto** |

**Knowledge:**

| Trigger | Flip | Who | Auto? |
|---|---|---|---|
| Recent changed paths intersect doc's `applies_to` | `active→stale` (or no-op if already `stale`) | exit-ritual (landing/soft-landing) | **auto** (landing; idempotent) |
| User confirms doc is now current | `stale→active` | user-asserted only | **never auto** |
| Verify passes (knowledge `stale` + `verify`) | `stale→active` (+ drop `verify`) | SKILL (on user-performed verification) | **auto-on-pass** (verify-pass path only — see [Non-blocking verification](#non-blocking-verification)) |
| User confirms doc is dead / obsolete | `→obsolete` | user-asserted only | **never auto** |
| Ritual detects `obsolete` knowledge artifact | drain to `archive/` (location change, not a new status) | landing | **auto** (same drain logic as `done`) |

Iron rules:
- **Forward-only, idempotent** — if target ≤ current, no-op.
- `idea` carries **no date prefix**; `idea→active` is the **only** rename point and is **idempotent** (skip if the name already has a `^\d{4}-\d{2}-\d{2}-` prefix).
- **Rejecting** a workflow artifact **deletes the file** — only on explicit user instruction (the AI never abandons work unilaterally). git log preserves the history; record a one-line reason in the commit body. There is no `scrapped` status value, no tombstone, no `### Rejected` group.
- `done`'s trigger source (no-verify task) = **the user's asserted approval / sign-off** (an asserted fact). The AI does **not** self-assess completion or judge it from a smoke-check. **Unchanged.**
- **Needs-verify task:** the AI **may** self-assert `done`, but **must carry `verify: <how>`** — not a silent self-completion: the debt is re-surfaced every preflight and the write is reversible (one frontmatter field + `mv`). See [verify field](#verify--the-verification-marker) + [Non-blocking verification](#non-blocking-verification).
- Every flip bumps `last_updated` (bare `idea` excepted).

Knowledge kinds (`incidents/` `checklists/` `docs/` `references/`) use `active / stale / obsolete`. Automatic flips: the exit ritual (landing/soft-landing) intersects this turn's changed paths with each knowledge artifact's `applies_to` paths and auto-flips `status: stale` on a hit (idempotent — already-stale is a no-op); preflight neither detects nor flips stale (read-only, zero-write) — stale visibility rides the folder INDEX rows (`⚠`) it already loads. The `stale→active` reset and the `→obsolete` death-decision are **user-asserted only** — the AI does not self-certify either transition, consistent with the **no-verify** `→done` rule for workflow. Set `obsolete` by hand; landing drains it to `archive/`.

### The status / landing seam

`done` is the **single seam** between the lightweight `status` ritual and the heavy `landing` ritual:

- `idea→active` is light work — `status` does it alone.
- **`→done` = the "completion" moment = landing's trigger point.** Reaching `done` hands control to landing for wrap-up + archival decision. `status` itself still does not commit / archive — it recognizes completion and passes the baton.
- **End-of-turn debounce:** a `done` flip does **not** immediately run landing per-item; it marks "owes one landing" and runs landing **once before the AI returns control to the user** (end-of-turn — a *decidable* event, not an unimplementable "natural pause"), aggregating all of this turn's `done`s into the **same** landing. An explicit `/flightdeck:landing` is also a trigger. (See [landing auto-trigger](#rule-resolution-order) in Rule resolution order.)
- **Archival criterion = a deterministic structural edge** (not AI prose reading): a `done` artifact archives into `archive/` **iff no `active` artifact points at it via a structural edge** (`implements:` active plan → done spec). `supersedes` is traceability-only and is **NOT** a pinning edge — `flightdeck_index.py --archivable` does not include it in the blocking set. `flightdeck_index.py --archivable` computes the archivable-`done` set as a **reproducible fact** (same input → same conclusion); prose markdown links are for humans only and **don't enter the criterion**. Pointed-at by an active inbound edge → stays done-but-unlanded.
- **Drain, don't accumulate:** every landing rescans **all** `done`-in-place artifacts (not just this session's), sweeping away any whose inbound edges have cleared — so done-but-unlanded **drains automatically** and never lingers. Still-pointed-at ones are listed by `walkaround` as INFO (naming the **blocking active artifact**, not a vague "reason").
- **Landing failure does not roll back `done`.** `done` asserts **user approval**, not "landing's smoke-check passed" — the two are orthogonal. If landing fails mid-run (smoke-check error, script crash, interrupted session), the artifact stays `done` at its current location (done-but-unlanded); the next landing sweep picks it up. Never revert `status: done` on a landing failure.

The optional `note:` field carries the "why it hasn't moved" diagnostic (blocker / pending reason) that the merged `active` state would otherwise lose; cockpit + walkaround render it as `[note: …]`.

Status is just a label — the user edits it freely; at landing the AI **applies** the next typical status by judgment (per the recommended flow) and **reports it in the banner** — reversible, so no confirm gate (the user can undo; see [Act-report-close loop](#act-report-close-loop)). walkaround flags odd values as INFO/warning, never blocks.

### Non-blocking verification

Verification is a **non-blocking marker, not a blocking gate**. The old "needs-verify → AI may NOT self-assert `done`" gate is **removed**: the AI **may** self-assert `done` (workflow) or write `stale` (knowledge) carrying a [`verify`](#verify--the-verification-marker) note. Safety comes from **visibility** — every preflight re-surfaces the verify debt via a deterministic scan — **plus reversibility**, NOT from blocking. Premise: preflight is the standard, mandatory entry — flightdeck's existing "single explicit entry point" design.

**Per-kind pass/fail** — the SKILL must first identify the artifact's kind (knowledge vs workflow), then act:

| | verification **passes** | verification **fails** |
| --- | --- | --- |
| **knowledge** (`stale`) | drop `verify`; flip `stale → active` | revive to `active` (`mv` back from `archive/` if archived); **keep `verify`** |
| **workflow** (`done`) | drop `verify`; stays `done` → becomes `--archivable` | revive to `active` (`mv` back from `archive/` if archived); **keep `verify`** |

Fail keeps `verify` (re-do + re-verify) — binary present/absent only, no `verify: failed` value. Multiple verify-debt items are handled **one at a time, independently**.

## INDEX.md (per-folder + root)

Every artifact folder has an `INDEX.md` — a derived index of that folder's files: one row per file `[file](file) — status — one-line summary` (knowledge folders add `when_to_read`/`applies_to`). The `<!-- AUTO -->` region is machine-maintained (regenerated from each file's frontmatter); an optional hand area sits outside it. `specs/INDEX` groups by status (`Backlog (idea)` / `Active · Done`) — see [folder-semantics § specs/](folder-semantics.md#specs--designs).

There is **no root `flightdeck/INDEX.md`** — the folder INDEXes are the whole index layer; deck root holds only `cockpit.md` + `rules.md`.

**Commands read the INDEX first and drill into individual files only on demand** — this is the main token saving (cost scales with folder count, not file count). landing regenerates only the INDEX of folders changed this session; walkaround does a full INDEX↔frontmatter consistency check.

## Folder map

```
flightdeck/                  [product name — kept]
├── cockpit.md   rules.md   [cockpit.md = interaction surface — metaphor kept]
├── specs/       INDEX.md   (idea / active / done)              workflow · self-authored · flat
├── plans/       INDEX.md                                       workflow · self-authored · flat
├── incidents/   INDEX.md   bug post-mortems                    knowledge · resident · nestable
├── checklists/  INDEX.md   process / conventions (execution)     knowledge · resident · nestable
├── docs/        INDEX.md   self-authored technical knowledge ★ knowledge · resident · nestable
├── references/  INDEX.md   imported external material (was charts/) knowledge · imported · nestable
└── archive/     (was landed/)                                  location (not a kind)
```

`docs/` (★ new in 3.0) holds **self-authored, resident, explanatory** project technical knowledge — architecture, design rationale, subsystem overviews, lifecycle/philosophy. It is what you **read to understand**, vs `checklists/` (what you **execute**), `references/` (what comes from **outside**), and `specs/` (one-shot design intent that archives when built). `archive/` is a first-class structural container (mirrors source kinds, handled specially by landing/index) but is **not a kind** — it answers "in the active area or not", not "what artifact is this" (artifacts keep their own kind). The archived files themselves **are** the landing record — flightdeck keeps no separate history log.

Reachability entries: `cockpit.md` / `rules.md` / the folder `INDEX.md` files. (No bundle README — multi-file topics live as several files in one folder, grouped via the INDEX hand area; only `references/` may contain an imported external project subtree.)

**Which folder?** Classify by lifecycle: design / idea (started or not) → `specs/` (`status: idea` = unstarted); execution plan → `plans/`; evergreen operational reference (executed) → `checklists/`; self-authored technical knowledge (read to understand) → `docs/`; imported external material → `references/`; post-incident records → `incidents/`.

**Routing is graph-based, not filesystem-based.** A file is "active" only if reachable from an entry (`cockpit.md`, `rules.md`, or a folder `INDEX.md`). **A file nothing links to effectively does not exist** — no session reads it. Custom folders / root files are allowed but MUST be reachable from an entry, or they are orphans.

## Routing — scenario triggers

| Scenario | Read first |
| --- | --- |
| Looking for next task | `cockpit.md` |
| Unsure about a design | `specs/` |
| Running tests / preparing commit | `checklists/` |
| Strange behavior / deja-vu bug | `incidents/` |
| Understand how the system works / why it's built this way | `docs/` |
| Need outside perspective | `references/` |
| Designing new feature | `specs/` (`status: idea`, flip to `active` when starting) |
| Breaking work into steps | `specs/` → write a `plans/` file |

**How to pick the right knowledge file**: don't read every file. All knowledge folders (`incidents/` `checklists/` `docs/` `references/`) use frontmatter (`when_to_read` + `applies_to` + `last_updated`) — grep the metadata, only load full files whose triggers match the current task. Use `last_updated` to judge staleness. An optional `skip_when` field (negative routing — "when NOT to read this") lets a file pre-empt a false match (e.g. `skip_when: editing tests only` on a production-hardening checklist, so it stays silent during test-only work); absent is fine.

### Frontmatter requirements (hard-fail)

Knowledge files (incidents / checklists / docs / references) **MUST** carry frontmatter with `when_to_read`, `applies_to`, and `last_updated`. On a missing field: STOP, report the file path + missing fields to user, offer (a) add now or (b) delete the file. Silent skip = files invisible while their authors believe they're active. That is the worst failure mode for an advice system.

### Stale detection (`when_to_update` + `applies_to` paths, single on-exit ritual)

Knowledge artifacts may carry `when_to_update`: a concrete-change-event phrase ("what kind of change would make me wrong") — the human-facing *reason*, not a runtime condition. The runtime trigger is mechanical: the exit ritual intersects the changed paths with the artifact's `applies_to` **path entries** (the entries containing `/` — prefix match; plain-word tags are routing-only and never match a path); a hit auto-flips `status: stale` — no pre-ask (stale is reversible, local, purely a warning; "docs quietly lying" is the worst failure mode). A knowledge artifact that wants stale freshness must therefore list **at least one source-path entry** in `applies_to`; a tags-only artifact simply opts out of stale detection.

`stale` covers **two pending-review sources** — `when_to_update`-matched suspected-outdated (this section) **and** new-but-unverified knowledge (`stale` + [`verify`](#verify--the-verification-marker)). The `verify` field distinguishes them: present = unverified, absent = `when_to_update`-outdated. Both render in the catalog as `⚠` (the scan splits them — `⚠ pending-review` vs `⚠ unverified`).

**Detection runs only at the exit ritual (landing/soft-landing — the single on-exit ritual):** `--changed-since-anchor` emits the paths changed since the anchor plus worktree uncommitted changes; intersect them with each knowledge artifact's `applies_to` paths and flip `stale` on a hit. preflight neither detects nor flips stale (read-only, zero-write) — its only debt scan is `--verify-pending`; un-flipped stale waits for the next landing.

**Anchor:** the git ref recorded by the most recent exit-ritual (stored as a `Flightdeck-Sync:` trailer in the landing commit — a concrete recorded ref, never a guess). The anchor advances at each landing commit.

**Idempotency:** `stale` detection is idempotent — already-`stale` docs are a no-op.

**User-asserted exits only:** `stale→active` (after updating the doc to current truth) and `→obsolete` (confirming the doc is dead) are **both user-asserted**, consistent with the **no-verify** `→done` rule. The AI does not self-certify either direction — except via the verify-pass path (see [Non-blocking verification](#non-blocking-verification)), where the SKILL flips `stale→active` on a user-performed verification that passes.

### Proactive incident resurfacing

Before starting a task whose description / file paths overlap with an incident's `applies_to` tags, surface it: "this touches `[tags]`, overlapping with [incidents/X.md](incidents/X.md) — worth a read first?". Recording a recurrence happens at the **other** end of the session: at landing, a **clear** same-incident match auto-appends `[Case N]` + bumps `recurrences` (see [exit-ritual § Step 5a](exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up)); an **ambiguous** match asks the user. Auto-counting is safe because the consequential step — *promotion* — is reversible and surfaces in cockpit Pending Review for veto (see [Act-report-close loop](#act-report-close-loop)).

### Hit path — check the error library *before* writing a new incident

When you hit an error mid-session, **first check whether it is already known** before writing a fresh incident file — dedup's value is *prevention*, not after-the-fact cleanup:

1. **grep the raw error text** into `incidents/` (the `symptom` line in each `## Signature` block is the grep anchor), and/or run the deterministic signature match: `flightdeck_index.py <deck> --match-signature "<symptom>" [--sig-error-type <TYPE>]` (read-only; prints `status<TAB>path` per fingerprint hit).
2. **Matched an existing incident** → **append a `## [Case N]` rather than starting a new file**, and let landing's recurrence sweep do the bookkeeping. (Matched an `obsolete` entry → that's a candidate *regression* — see [Incident error-library lifecycle](#incident-error-library-lifecycle) below; do not silently re-append.)
3. **No match** → it is genuinely new; author the incident via `/flightdeck:new incident`, which scaffolds the `## Signature` block.

The fingerprint is computed from `symptom` (normalized) + `error_type` only — the author writes the human-readable `symptom`, never a hand-computed fingerprint. An incident with **no `## Signature`** block (legacy) is simply skipped by the deterministic layer and falls to the AI fuzzy layer at landing — both tracks coexist.

## Source-of-truth precedence (when sources disagree)

Project agent rules > `rules.md` > `cockpit.md` > active folders (`specs/` `plans/` `incidents/` `checklists/` `docs/` `references/`) > `archive/`

`rules.md` sits just below the project's own agent rules: it governs how flightdeck skills behave. `cockpit.md` is the single operational entry below it.

> **"Project agent rules"** = your project's top-level AI instructions file — whatever your AI tool reads on every session.

## Preconditions and boundaries

**Single active session.** This protocol assumes only one AI session runs preflight/exit-ritual against the same deck at a time. Concurrent-session conflict coordination (two sessions simultaneously editing frontmatter) is out of scope. Single-user, sequential use; if concurrent sessions are ever needed, a separate spec is required.

**`archive/` is cold storage, not a live routing input.** Artifacts drained to `archive/` are grep-able cold records — recurrence sweeps scan `archive/incidents/` for regression detection, and `supersedes` edges may point into `archive/` as valid cold history pointers. None of this makes `archive/` a live routing DB: it stays excluded from the routing graph. Only an explicit revival (un-archive + status flip) promotes a file back into the active area.

## Design philosophy

> **Semantic clarity outranks thematic consistency.**

When naming or structuring decisions trigger a conflict between "fits the aviation metaphor" and "reads correctly", clarity wins. The flightdeck metaphor is used because it sharpens operational intent — *not* as a theme to be applied uniformly. `specs/` intentionally uses a neutral name because no aviation equivalent improves it. Future concepts face the same test.

Reject:
- aviation roleplay / sci-fi theming / meme interfaces / gamified agent cosplay
- "cute but unclear" terms (e.g., `/stuck → /request-vector` was rejected during rebrand — `/stuck` already reads correctly)
- forcing every new term into the metaphor

## Lifecycle

```
idea →(flip one field)→ active → done   →(land = move to archive/)
                                  (rejected = delete the file)
```

A spec starts `status: idea` (unstarted, no date prefix). Starting it is **just a field flip** `idea → active` (which auto-adds the `YYYY-MM-DD-` prefix and surfaces it in cockpit `## In Progress`) — no folder move, no relation-edge rewrite. Each plan carries optional `implements: specs/<x>.md`. `location` (active vs `archive/`) is derived from landing a done item. Folder says the kind; frontmatter `status` says the state. While a plan is `active`, **checkpoints** keep the board synced at each plan-task boundary (cockpit `## Next` + the plan's `## Progress` `current:` pointer, disk-write only, no commit) — the lightweight subset of landing that makes a mid-plan close-and-reopen lossless. See [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath).

Beyond the `done`-triggered landing, an **end-of-turn knowledge increment** auto-runs a **soft-landing** (signal 3 — classify knowledge + regen changed INDEX + cockpit board, plus the **unified soft-landing banner** — see [Act-report-close loop](#act-report-close-loop) — no commit/archive); default-on, downgradable via a deck `### Rules` entry. See [exit-ritual § Land-readiness](exit-ritual.md#land-readiness-check).

A passive **turn-end hook** additionally regenerates the mechanical board AUTO regions (`## In Progress` + each `INDEX.md`) at every end-of-turn on every host that fires it (Claude/Codex `Stop`, Cursor `stop`, Gemini `AfterAgent`) — a deterministic enhancement that keeps those regions from going stale between landings. It never blocks, archives, or writes judgment fields (`## Next` / `Focus` / knowledge classification stay agent-driven); the protocol does **not** depend on it.

A **rejected** spec is **deleted** (only on explicit user instruction; git log keeps the history, the commit body records the reason). There is no `scrapped` status value or tombstone group.

**Knowledge lifecycle:** `active ⇄ stale → obsolete` (stale auto-flipped by ritual on `when_to_update` match; obsolete drained to `archive/` by ritual — same drain logic as workflow `done`). `obsolete` is the **knowledge analog of workflow `done`**: a terminal state meaning "dead, pending drain", not an in-place tombstone. **`obsolete`-not-yet-drained ≡ `done`-but-unlanded** — both drain automatically on next landing/preflight, never linger permanently.

**Graduate seam** (spec → docs, at landing): a spec with `graduate: true` that reaches `done` is, at landing, **rewritten body-and-all into a permanent `docs/` entry** (current-truth view) and the source `specs/` file is moved there — no archive twin. Two paths for knowledge reaching `docs/`: (a) **graduate** — a `graduate: true` done spec that covers a new structural domain → new `docs/` entry; (b) **direct update** — an existing `docs/` entry already owns the topic → update it in place (no graduate). Discriminator: if a `docs/` entry already covers the topic, update it; else graduate a new one. The `graduate: true` flag window = the whole active life of the spec (can be added at any point before landing; missed flag = user's responsibility, no completion-time re-detection fallback). Idempotency key = "`graduate: true` done spec **still in `specs/`**" — once moved, the trigger key is gone and re-runs are safe no-ops. Graduate runs only at landing; a missed window is caught by the next landing's rescan (Step 3b walks every `graduate: true` done spec still in `specs/`). Graduate-out docs must carry `when_to_read` / `applies_to` / `when_to_update`; omitting `when_to_update` opts the doc out of stale detection immediately.

## Exit ritual

90% of exits are obvious — classify and write directly. Only truly ambiguous items invoke brainstorming. The full decision tree (classification heuristics, hanging-task gate, INDEX regeneration, cockpit update) lives in [exit-ritual.md](exit-ritual.md) and is run by `/flightdeck:landing`.

After classifying: update `cockpit.md` (`Updated` + regen `## In Progress` from `status: active` + auto-write `## Next` + any `Hanging Tasks` changes); then commit locally per the commit default (auto local commit, **push asks**). landing regenerates the INDEX of any folders changed this session.

## Act-report-close loop

> Runtime contract for "AI acts, reports, you can close anytime" — reversible-auto · unified banner · lifecycle recovery. **Single source of truth**: `bootstrap.md` carries only the minimal runtime pointer; skills reference here, never restate.

### Reversible vs irreversible (the gate criterion)

**Criterion:** a change confined to deck files / local git, reversible by re-editing or a local git operation, is **reversible** → executes automatically, no confirm gate. A change that is **outward or irreversible** stays gated (ask first).

| Class | Examples | Behavior |
| --- | --- | --- |
| Reversible (auto) | `status` flip (idea→active, →done), `--advance-candidates`, incident→checklist promotion, `done` archival, applying a status suggestion, stale flip, cockpit section maintenance, local `git commit` | execute by judgment, no gate; report in the banner |
| Outward / irreversible (gated) | `git push`, publishing outward, calling an external service | ask first (red line) |

This table is the **single authority**; new actions classify by the criterion. A skill author must not reintroduce a confirm gate on a reversible action under another name. A reversible edit that **destroys user-handwritten content** (rewriting / mass-deleting cockpit notes) is still auto, but **must be reported explicitly in the banner** (never silent). `Hanging Tasks` is **not** a confirm gate (see below).

### Unified flow output (the banner)

Every flow turn = **prose first, then exactly one standardized banner at the very end**. Status / landing / recovery info always lands last, never mid-prose.

```
─── <icon> <flow> ───
<key info / recovery path, one per line>
```

- **icon + flow name** per the [Brand glyphs table](#brand-glyphs-per-command) (`preflight` 🛫 · `landing` / `soft landing` 🛬 · `new` ✍️ · `walkaround` 🔍 · `status` 🔄). Flow name + field labels are **structural English** (i18n); content after a label is in the user's working language.
- **"Turn" =** one user input → one complete AI response (including any internal multi-step actions). **One aggregated banner per turn**, not one per atomic action.
- **Trigger**: a turn that ran a flow or did real work emits a banner (`preflight` / `landing` / `soft landing` / `new` / `walkaround` / an execution turn). A **pure-conversation / clarification turn** (no flow, no deck change) emits none. "No change" = *a flow ran but produced no new knowledge* (still a banner) — not a pure-chat turn.
- **Nesting**: a flow nested in another (landing triggers soft-landing) emits only the **outermost** banner; inner `[Saved]` / `[Pending]` info is **merged (union)** in — "one banner" means aggregated into one, inner increments not dropped.
- **Failure**: a crashed / partial / failed flow **still emits a banner**, with a `[Failed]` line: failure point, what was persisted, how to resume.

**Field set:** always — `[Stage]` (recovery needs it) + the closing "you can close now" line. Conditional — `[Saved]` (knowledge persisted) / `[No change]` (no new knowledge), mutually exclusive; `[Pending]` **only when Pending Review is non-empty** (omit when empty, never an empty `[Pending]`); `[Failed]` (failure). Each flow's minimal field set lives with its SKILL (preflight ≥ `[Next]` + routing counts).

```
─── 🛬 soft landing ───
[Stage]     <lifecycle stage, see below>
[Saved]     specs/ +1 <file>; cockpit Next updated.        (or [No change])
[No change] No new knowledge this turn; board is current.
[Pending]   ⚠ N item(s) await verification: … → see cockpit Pending Review.
You can close / switch the conversation anytime — next preflight resumes from the board.
```

### Undo channel ("rollback")

One universal undo replaces per-action gates. The undo unit is **the most recent landing unit as a whole** — one `landing` / `checkpoint` commit, or this turn's uncommitted deck changes — not a file-level last change.

- **Cross-session recoverable**: target derived from git + the board, not conversation memory. Read `git log -1 --oneline`; a commit clearly tagged (`landing:` / `checkpoint:`) → revert that unit; **untagged / spans multiple turns / ambiguous → ask the user** (never force-guess). Makes "undo after closing the conversation" deterministically implementable.
- **Action**: reverse that unit's reversible changes (un-flip status / un-archive / local git revert / delete a just-promoted checklist). `push` is never in undo scope.
- **No undo stack**: the "most recent landing unit" is reconstructed from git + board.

### Lifecycle recovery (resumable after any interruption)

Work may stop at any stage and be interrupted; the banner `[Stage]` + the board must let the next preflight tell *where it is and how to continue*:

| Stage | Recovery anchor |
| --- | --- |
| brainstorming | no artifact yet; cockpit Focus / Next records "brainstorming X, asked up to …"; decided points incrementally soft-land into a spec |
| spec written | spec(active) in In Progress; Next = review → write plan |
| plan written | plan(active) in In Progress; Next = execute plan step N |
| plan partially done | Next = continue from the next unfinished step (plan `## Progress`); finished parts not redone |
| plan done, pending review | Pending Review entry recording "after verification passes: how to commit / next step" |
| review passed | trigger landing: flip done, archive, commit |
| ad-hoc (no spec/plan) | cockpit Next states "doing X, up to …"; reversible done + reported per the banner |

**Stage derivation (deterministic):** `[Stage]` = **plan status > spec status > cockpit Focus prose** (no-artifact brainstorm / ad-hoc stages fall to prose). With both a spec and a plan present, the plan's stage wins.

**Two recovery contexts (no conflict):** *preflight recovery* reads only cockpit + INDEX (the recovery payload) — no git, no conversation (keeps preflight read-only). *Undo* is a separate user-invoked action that may read git log + the board. "Recovery only reads the board" refers to the former.

**Guarantee scope:** zero-loss covers the **recovery payload (cockpit + INDEX + persisted artifacts)**, *not* un-persisted in-conversation reasoning. A long brainstorm bounds loss by landing decided points incrementally.

## Ritual responsibilities — who owns what

Three entry rituals, three non-overlapping jobs — so no check is both everyone's and no-one's. When a check could belong to two rituals, this table decides:

| Ritual | Role | Writes? | Cockpit 80-line trim | INDEX | Deep per-file audit |
| --- | --- | --- | --- | --- | --- |
| `preflight` | read-only takeover at session start | **no (zero writes)** — deckless redirects to /flightdeck:launch | reads only — passive note on git state | reads folder INDEX as catalog | no — audits belong to walkaround |
| `landing` | write the session's outcome (full mode); board-sync only (checkpoint mode at task boundaries) | yes | **owns the trim** (proposes → confirms → edits) | regenerates changed folders' INDEX | no |
| `walkaround` | integrity audit on demand | **no — audit-only, never fix** (proposes fixes, never auto-applies) | flags `> 80` as INFO | full INDEX↔frontmatter check | **owns** status / orphan / dangling-ref / stray-file audits |

The 80-line cockpit trim is **landing's** (it is the only ritual that writes cockpit); `walkaround` only flags it; `preflight` never touches it.

Checkpoint is **landing's lightweight mode**, not a fourth ritual — it reuses landing's cockpit board-sync step and writes nothing else (no INDEX, no archive, no commit). `preflight` stays read-only; checkpoint never runs at entry.

## Write gate

`flightdeck/` records only content that **changes future behavior, influences decisions, or gets referenced repeatedly**. Session byproducts, debug logs, and chat play-by-plays do not qualify. Gate strictly.

**Skip — gate these out (do NOT write):** empty status checks (`status` / `ls` that surfaced nothing); **a dependency install / build command that merely succeeded with no derived conclusion** (`npm/pip/uv install`, a green build by itself); **an exploration that concluded nothing** (searched, neither found nor ruled anything out); **a repeat that added no new information** (same op rerun without widening coverage / reaching a new conclusion / eliminating a new possibility); one-off logs and trial-and-error play-by-plays ("today's log is…" / "I tried 5 ways").

**Two boundaries — NOT skips, do write:** ① an exploration that yields an **exclusionary conclusion** ("X is not the root cause") is negative knowledge — **write it**; ② a repeat that **brings new coverage / a new conclusion** — **write it**.

- ✅ write: "Cursor injection is fixed to `.cursor/rules/*.mdc` as the primary path (sessionStart proved unreliable)" — **influences future decisions, will be referenced repeatedly**.
- ❌ don't: "today's `--check` run printed clean" — a one-off status that changes no future behavior.

(This Skip list is the write gate's canonical negative list — passed before authoring *any* artifact. It runs parallel to `landing`'s `exit-ritual` heuristic **(g) One-off → DO NOT WRITE**, which is the first-match item at *classification* time; same direction, each self-contained.)

## Templates

See [templates.md](templates.md) for `spec` / `plan` / `incident` / `checklist` / `docs` / `cockpit.md` / `rules.md` / `INDEX.md` templates.

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

When the gate fires, `landing` **promotes** `incidents/X.md` → `checklists/X.md` by judgment (reversible) and **surfaces it in cockpit Pending Review** for the user to veto (undo reverses it). No pre-confirm gate — promotion is a reversible deck action (see [Act-report-close loop](#act-report-close-loop)); the user retains the final say via Pending Review / undo.

A separate **project-rules upgrade gate** fires when a promoted incident continues to recur after promotion. Then add a one-liner to project agent rules and mark the incident `Status: upgraded → project rules`. Do not delete the incident.

## Incident error-library lifecycle

An incident is not just born and resurfaced — it can also be **retired** once its root cause is permanently fixed, and **revived** if the fix regresses. This is the "death" half of the error library; the "birth/use" half (Signature, fingerprint matching, hit path) lives under [routing](#routing--scenario-triggers) + [Proactive incident resurfacing](#proactive-incident-resurfacing).

### Retirement semantics (`resolved_by` + `status: obsolete`)

When an incident's root cause is permanently fixed (e.g. a guard test now prevents it), the incident is **retired**: fill `resolved_by` (a single reference — a commit SHA or a test id/path, e.g. `test_flightdeck_index.py::CockpitProjectionRobustnessTest`) **and** flip `status: obsolete`. These two are **one deliberate act**, performed at **landing** (the ritual that owns knowledge classification and retirement; `status` only touches workflow). Landing **auto-flips** when `resolved_by` is filled **and** the fix is confirmed (e.g. the guard test exists) — reversible, surfaced in cockpit Pending Review for veto; ambiguous (filled but unconfirmed) → left `active`, noted in Pending Review (see [Act-report-close loop](#act-report-close-loop)).

`obsolete` here means **"root cause fixed, retired from active routing, pending drain to archive/"** — it is **NOT "outdated / worthless"**. Knowledge status uses `active / stale / obsolete`; `obsolete` is the knowledge analog of workflow `done` (drain state — the ritual moves it to `archive/`).

### The obsolete dual path (drained to archive/, still grep-able cold)

`obsolete` only leaves the **active-recommendation routing** (excluded from the folder INDEX `<!-- AUTO -->` region and from the root knowledge count — zero session routing tokens). The ritual then **drains it to `archive/`** — same drain logic as workflow `done`. It is **not deleted**: an archived incident is still **on disk, still grep-able** in `archive/incidents/`, **and still entered into `--match-signature` / the landing recurrence sweep** (the sweep must scan `archive/incidents/` too — regression detection *depends* on retired incidents staying matchable). **Implementations must NOT hard-filter `obsolete` or `archive/` out of the match set.** A signature hit on an archived entry is the signal that a "fixed" bug may have come back — **revival = un-archive + flip back to `active`** (regression handling lives in [landing § Recurrence sweep wiring](../landing/SKILL.md#recurrence-sweep-wiring) — gated revival, never a silent re-append).

## Common mistakes — STOP and reclassify

| Mistake | Fix |
| --- | --- |
| Same fact in cockpit + incident + spec | One authoritative source; others link via `[name](incidents/X.md)` |
| Scratch written into flightdeck/ | Transient scratch lives in project-root `tmp/` (gitignored), not flightdeck. |
| `incidents/` writes "forgot / careless" | Root cause must be a wrong assumption / wrong model / wrong process. |
| External review feedback saved as its own file | Raw feedback is transient → project-root `tmp/`; its disposition (adopt / reject / defer) folds into the reviewed spec's `## Review notes`. |
| Brainstorming where every knowledge item belongs | Heuristics catch 90%. Default-brainstorm is the failure mode. |
| Cockpit > 80 lines | Trim immediately — drop finished items, move design detail to the relevant `specs/` file; history is `git log` + the `archive/` folder, not cockpit. (Landing owns the trim — see [Ritual responsibilities](#ritual-responsibilities--who-owns-what).) |
| Bumping `Updated` on every commit / typo / grep | Signal pollution. Only bump on 4 triggers in exit-ritual.md `Cockpit update`. |
| Incident / checklist without required frontmatter | STOP, report file path + missing fields. Add or delete before proceeding. |
| Incident / checklist with `last_updated` > 1 year in a fast-moving project | Likely stale advice. Bump after re-verifying or flip to `status: obsolete`. |
| "Save in case it's useful later" | No. Gate strictly. |

## Authoring new artifacts

Producing a new deck artifact (spec / plan / incident / checklist / reference / doc) — including from an external authoring skill (brainstorming / writing-plans) — goes through **`/flightdeck:new`** (script: `scripts/flightdeck_new.py`), which stamps the correct per-kind frontmatter + naming and regenerates INDEX/cockpit. The full contract (kind→folder, naming, per-kind frontmatter, default status, slug rule) lives in `skills/new/SKILL.md` — the single authority, so the shape is never re-derived from scattered docs. **Shell-first**: create the shell via `new` first, then write the body into the returned path; do not hand-derive a path or write to `docs/`.

## Brand glyphs (per command)

Every flightdeck command carries a brand emoji on its **runtime main report / completion line** (report line only — never in deck files, never in scaffolds). This is the **doc-level single source of truth** — each skill hard-codes its own glyph; a new command picks a glyph per this table. `✈️` (U+2708 + FE0F) is reserved as the project wordmark (README title) and is **not** a command glyph.

| Command | Glyph | codepoint | Meaning |
|---|---|---|---|
| launch | 🛠️ | U+1F6E0 FE0F | build the deck / first-time setup |
| preflight | 🛫 | U+1F6EB | pre-flight readiness |
| walkaround | 🔍 | U+1F50D | walkaround inspection / audit |
| new | ✍️ | U+270D FE0F | author a new artifact |
| status | 🔄 | U+1F504 | status transition |
| landing | 🛬 | U+1F6EC | land & archive |
| emit-agents-md | 🌉 | U+1F309 | cross-tool bridge |

Scope of force: a passive documentation convention, not program-enforced — changing a command's glyph requires manually syncing this table (preflight does not auto-validate it).

## Cross-references

The flightdeck convention describes WHAT to write and WHERE; the tool that produces the content is up to you (hand-write, use any AI skill, or ad-hoc LLM).

**Optional companions** (Claude Code with the `superpowers` plugin installed):
- `superpowers:brainstorming` → produces well-structured designs that fit `specs/`; hand the design off to `/flightdeck:new spec` (shell-first) so frontmatter/naming/regen are stamped, not re-derived.
- `superpowers:writing-plans` → produces task lists that fit `plans/` (via `/flightdeck:new plan`). Plan files use `- [ ]` checkboxes for executing-plans tracking; **flightdeck does not require flipping these** — progress lives in `cockpit.md` + commit log.

These are convenient but **not required** — flightdeck accepts content from any source.

The `flightdeck/` directory structure is **tool-agnostic** — any AI assistant can follow these conventions via project-level instructions. See `adapters/` for per-tool install paths.
