# flightdeck protocol (reference)

> Loaded on demand by `preflight` (and referenced by `landing` / `walkaround`). This is the protocol "textbook": the data model, folder semantics, routing, authority order, write gate, and lifecycle. The operational entry ritual lives in [SKILL.md](SKILL.md).

## Core principle

`flightdeck/` is a directory convention organized by **when you read what** — a persistent workbench for AI-assisted coding. What earns a place is governed by the [write gate](#write-gate).

## Naming iron-rule (metaphor vs mainstream)

The aviation metaphor is reserved for the **interaction surface** — slash commands, rituals, and the cockpit: `flightdeck` / `cockpit` / `preflight` / `walkaround` / `landing` / `launch` (including the every-session `cockpit.md` dashboard). The **data model — folders, statuses, fields — uses mainstream, ordinary names** a developer can guess cold. A newcomer who doesn't know the metaphor must still be able to guess what each folder / status / field is for.

Consequence: the two metaphor folder names became mainstream — `charts/ → references/`, `landed/ → archive/`. Status values are mainstream (`idea/active/done`, `active/stale/obsolete`). `flightdeck/` (the product root) and `cockpit.md` (interaction surface) keep their names. This rule outranks thematic consistency — see [Design philosophy](#design-philosophy).

## Project rules (`rules.md`)

`flightdeck/rules.md` is a **mandatory** project-config file read **first** by every entry skill (`preflight`, `landing`, `walkaround`, `emit-agents-md`, `status`). It is part of the **minimal contract** (`rules.md` + `cockpit.md`) and must carry a `version` field (the deck-conformance version; `walkaround` is the sole writer).

As of **3.0**, `rules.md` carries just `version` plus free-prose house rules:

- `version` — required identity field (deck-conformance stamp; not a behavior toggle). The **only** structured frontmatter field.
- **House rules** — free prose in two recommended subsections: `### Project conventions` (deck-local conventions) and `### Autonomy overrides` (behavioral overrides).

Everything that used to be a toggle is now **inferred from the environment** (`git`, `emit_agents_md`, `scripts`-runtime), decided by **skill judgment** (landing's archive call), or a **default that House Rules can override** (`commit`). The pre-3.0 keys (`git` · `emit_agents_md` · `disabled_gates` · `disabled_folders` · `model_invocable` · `status_auto` · `commit_mode`) are **read but ignored through 3.x and removed at 4.0** — a deck still carrying them keeps working; `walkaround` offers any structural migration. Re-adding a structured toggle faces a high bar (per-project-varying + real-demand-now + not-inferable + not-foldable); almost everything belongs in House Rules, inference, or skill judgment instead. Full schema + ready-to-paste template: [templates.md § rules.md](templates.md#rulesmd).

## Rule resolution order

Every skill resolves each behavior in this order — **first hit wins**:

1. **House Rules override** (`rules.md` `### Autonomy overrides` segment) — if matched, use it and **skip inference**.
2. **Environment inference** — `git`: is the **deck** under version control? — `deck root` has (or is under) a `.git` **and** the deck is **not gitignored** (`git -C <deck> check-ignore .` returns empty). A gitignored `flightdeck/` — common when a project deliberately keeps its deck out of code history — is **no-git for deck operations** even though the surrounding repo has git: landing skips the commit step and never invokes git on deck files (plain `mv` for the land move; the repo's own tracked code is committed by its normal flow, which flightdeck doesn't touch). `emit_agents_md`: does deck root already have `AGENTS.md`?
3. **Built-in default** — `commit` = **local commit auto, push asks** (local commits are reversible — reset/amend; push is outward, so it stays gated); **all five rituals (`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`) self-invocable**; `status` auto-flips `start` (idea→active) and `done` (on approval) but **never archives** — whether a `done` artifact lands is `landing`'s cross-reference-aware judgment; **`landing` auto-runs on `done`** — a `done` flip relays into a landing run, debounced to **once at end-of-turn** (reversible → automatic; the downgrade `landing: nudge on done, don't auto-run` reverts to nudge-only); `scripts` = **inferred** (use the bundled `flightdeck_index.py` scripts when a `uv`/`python` runtime is reachable, else by hand). The one outward action (push) stays gated; everything reversible runs without asking.

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
| landing auto-run on `done` off (downgrade to nudge-only; on by default) | `landing: nudge on done, don't auto-run` | `landing 完成时只提示不自动跑` |
| no git | `this deck doesn't use git` | `本 deck 不走 git` |
| has AGENTS.md but don't regen | `has AGENTS.md but don't auto-regen` | `有 AGENTS.md 但不要自动 regen` |
| soft-landing at end-of-turn off (signal 3; on by default) | `landing: don't soft-land at end-of-turn` | `landing 结尾不自动落盘` |

There is no self-invoke override (all five rituals always self-invoke), no `auto land` toggle (archiving is landing's judgment), no `run scripts` toggle (script use is inferred from runtime availability), and no `disabled_folders` (empty/unused folders are simply not flagged). The legacy `commit without asking` phrase still matches the new default (auto local commit) for compat.

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
| `note` | workflow | optional | cockpit `## 进行中` row + walkaround render | author/status | rendered as `[note: …]`, not validated |
| `verify` | workflow (`done`) + knowledge (`stale`) | optional | preflight/landing/walkaround verify-debt scan + `flightdeck_index.py --verify-pending` | author/status/landing | present = owes verification, value = one-line how-to (see [verify field](#verify--the-verification-marker)) |
| `last_updated` | knowledge + workflow | knowledge **required**; workflow recommended | preflight (staleness) | status/landing (auto-bump) | knowledge: Audit 2; workflow: INFO |
| `implements` | plans | optional | reverse-lookup via `plans/INDEX.md` | author | Audit 4 (orphan INFO) |
| `supersedes` | workflow + knowledge | optional | grep (traceability only — NOT an archival-pinning edge) | author/status | dangling-edge INFO (optional) |
| `related` | workflow | optional | grep | author | dangling-edge INFO (optional) |
| `when_to_read` | incidents/checklists/docs/references | **required** | preflight routing | author | Audit 2 |
| `applies_to` | incidents/checklists/docs/references | **required** | preflight routing | author | Audit 2 |
| `when_to_update` | docs/references (knowledge) | recommended for graduate-out docs; optional otherwise | exit-ritual + preflight stale detection | author (set at graduate time) | flag if absent on a graduate-tagged doc |
| `skip_when` | incidents/checklists | optional | match-time negative routing | author | not enforced |
| `recurrences` | incidents | optional (default 1) | INDEX-row render + promotion gate | landing/status (auto-bump on a clear recurrence) | int ≥ 1; ≈ 1 + `[Case N]` count |
| `graduate` | specs | optional | landing (graduate seam trigger) | author / AI (front-loads at creation or during active life) | — |
| `superseded_by` | knowledge | **retired in 3.0** — old `status: superseded` redirect field; no longer written; kept here as a tombstone so walkaround can flag live instances | — | — | flag if present on a non-archive file |
| `version` | `rules.md` (root) | **required** (rules.md is mandatory) | landing (guard) / walkaround | launch (init) / **walkaround only** (bump + migrate) | Audit 10 |
| `git` · `emit_agents_md` · `disabled_gates` · `disabled_folders` · `model_invocable` · `status_auto` · `commit_mode` | `rules.md` (pre-3.0) | **removed in 3.0** — inferred / House-Rules / skill-judgment / default (see [Rule resolution order](#rule-resolution-order)); read but ignored for 3.x compat | all entry skills | — | — |

`cockpit.md` board fields (`Last updated` / `Active focus` / `## 进行中` / `## 下一步` / `## Hanging tasks`) are not YAML frontmatter. `## 进行中` is an AUTO region derived from `status: active` spec/plan; `## 下一步` is AI-maintained — see [templates.md § cockpit.md](templates.md#cockpitmd).

### Supersession model

**`supersedes` edge (traceability-only, NOT archival-pinning).** The new artifact may carry `supersedes: <old-artifact>` pointing at the one it replaces — this is a traceability annotation for humans and grep, nothing more. It is **not** an archival-pinning edge: `flightdeck_index.py --archivable` does **not** include it in the blocking-inbound-edge set (only `implements:` pins). The old artifact's death is driven **independently** — by the user flipping it to `obsolete`, which the rituals then drain to `archive/`. Once archived, a `supersedes` pointer into `archive/` is a legal cold history pointer; no maintenance required.

**`superseded_by` is retired (3.0).** The old forward-redirect field (`superseded_by` required when `status: superseded`) was predicated on knowledge files staying in place indefinitely. Since `obsolete` is now a drain state (rituals move it to `archive/` — see [Status ⟂ location](#status--location-two-orthogonal-axes)), the dead file is no longer on disk long enough to need a redirect. `superseded_by` must not be written on new files; `walkaround` flags any live instance.

**`last_updated` — required (knowledge) vs recommended + auto-bump (workflow).** Knowledge is found by grep-routing where stale advice is dangerous → required. Workflow is found via INDEX/cockpit → staleness matters less; recommended, and auto-bumped by `status`/`landing` to prevent rot.

### `verify` — the verification marker

**`verify` is a status附加标记, NOT a status and NOT a state machine.** It is read **together with** `status` (sibling to `note:` / `resolved_by:` / `when_to_update:`), never on its own. Presence/value/absence carry the whole contract:

- **present** = the artifact **owes verification** (substantively written/done, but not yet confirmed against reality);
- **value** = a one-line **how-to-verify** note (e.g. `verify: 相位4 各家 live 实证`) — so the debt's *content* survives any cockpit edit/regen and the deterministic scan can re-surface it;
- **absent** = verified, or no verification needed.

Binary present/absent only — there is **no `verify: failed` value** (a failed verification revives the artifact and **keeps** `verify`; see [验证非阻塞](#验证非阻塞-non-blocking-verification)). Optional; applies to a knowledge `stale` artifact (written-but-unverified) and a workflow `done` artifact (substantively-done-but-unverified). **It is not a 4th workflow status** — the status value sets are unchanged (workflow `idea/active/done`, knowledge `active/stale/obsolete`); `verify` only modifies how a given status reads. Every preflight/landing/walkaround re-surfaces the debt via a deterministic scan of the `verify` field across the active tree + `archive/` (`flightdeck_index.py --verify-pending`).

## Status ⟂ location (two orthogonal axes)

flightdeck separates **two independent axes** — the source of the historical "done = landed" confusion is collapsing them:

- **status** ∈ `{idea, active, done}` (workflow) — *which step the artifact reached*. Explicit frontmatter value.
- **location** ∈ `{源文件夹, archive/}` — *whether it's still in the active area*. **Derived, NOT a frontmatter field** (computed from "is it under `archive/`?"), **but a first-class concept**: it drives **routing** (`archive/` is excluded from the routing graph entirely) and **archival judgment** (landing decides whether a `done` item lands). Don't dismiss it as unimportant just because it isn't written down.

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

`stale` = **待复核：疑似过期 _或_ 新产出未验证** — two sources distinguished by the [`verify` field](#verify--the-verification-marker): **has `verify`** = written-but-unverified; **no `verify`** = `when_to_update`-matched suspected-outdated. The status token is unchanged; only the meaning broadens.

- `idea` = unstarted thought / design (the to-start pool); only in `specs/INDEX`, **not** in cockpit. No date prefix.
- `active` = being worked on; **auto-appears in cockpit `## 进行中`**. The `idea→active` flip auto-adds the `YYYY-MM-DD-` prefix.
- `done` = 工作完成；留在源文件夹直到 landing ritual 把它归档进 `archive/`（**done ≠ archived**）.
- **Rejected / abandoned** = the artifact is **deleted outright** (only on explicit user instruction). git log is the history, with a one-line reason in the commit body. There is no `scrapped` status value and no tombstone group.

### Status transition authority table (single source of truth)

This is the **one authoritative table** for automatic status flips. Other files (`status` SKILL, `exit-ritual`) point here and do not restate the rules.

Workflow chain: `idea → active → done`. Rejection **deletes** the file (no scrapped status).

**Workflow:**

| Trigger | Flip | Who | Auto? |
|---|---|---|---|
| Write a new spec/plan (capture only, not yet started) | →`idea` | status | always |
| Write a new spec/plan **and already working on it** | direct →`active` (legal skip past idea) | status | always |
| Start working on an existing idea | `idea→active` (+ `YYYY-MM-DD-` prefix + regen cockpit `## 进行中`) | status | default (House Rule `status: don't auto start` can disable) |
| User approves / signs off | `active→done` (flips `done` only, **does not archive**) | status / landing seam | always |
| A direction is rejected | **delete the file** (git log + commit-body reason) | **user-explicit instruction only** | **never auto** |

**Knowledge:**

| Trigger | Flip | Who | Auto? |
|---|---|---|---|
| Recent change matches doc's `when_to_update` | `active→stale` (or no-op if already `stale`) | exit-ritual (landing/soft-landing) | **auto** (landing; idempotent) |
| User confirms doc is now current | `stale→active` | user-asserted only | **never auto** |
| Verify passes (knowledge `stale` + `verify`) | `stale→active` (+ drop `verify`) | SKILL (on user-performed verification) | **auto-on-pass** (verify-pass path only — see [验证非阻塞](#验证非阻塞-non-blocking-verification)) |
| User confirms doc is dead / obsolete | `→obsolete` | user-asserted only | **never auto** |
| Ritual detects `obsolete` knowledge artifact | drain to `archive/` (location change, not a new status) | landing | **auto** (same drain logic as `done`) |

Iron rules:
- **Forward-only, idempotent** — if target ≤ current, no-op.
- `idea` carries **no date prefix**; `idea→active` is the **only** rename point and is **idempotent** (skip if the name already has a `^\d{4}-\d{2}-\d{2}-` prefix).
- **Rejecting** a workflow artifact **deletes the file** — only on explicit user instruction (the AI never abandons work unilaterally). git log preserves the history; record a one-line reason in the commit body. There is no `scrapped` status value, no tombstone, no `### 已否决` group.
- `done`'s trigger source (no-verify task) = **the user's asserted approval / sign-off** (an asserted fact). The AI does **not** self-assess completion or judge it from a smoke-check. **Unchanged.**
- **Needs-verify task:** the AI **may** self-assert `done`, but **must carry `verify: <how>`** — not a silent self-completion: the debt is re-surfaced every preflight and the write is reversible (one frontmatter field + `mv`). See [verify field](#verify--the-verification-marker) + [验证非阻塞](#验证非阻塞-non-blocking-verification).
- Every flip bumps `last_updated` (bare `idea` excepted).

Knowledge kinds (`incidents/` `checklists/` `docs/` `references/`) use `active / stale / obsolete`. Automatic flips: exit-ritual (landing/soft-landing) compares this turn's changes against `when_to_update` fields and auto-flips `status: stale` when a match is detected (idempotent — already-stale is a no-op); preflight surfaces unflipped stale debt (read-only — it does not write stale itself). The `stale→active` reset and the `→obsolete` death-decision are **user-asserted only** — the AI does not self-certify either transition, consistent with the **no-verify** `→done` rule for workflow. Set `obsolete` by hand; landing drains it to `archive/`.

### The status / landing seam

`done` is the **single seam** between the lightweight `status` ritual and the heavy `landing` ritual:

- `idea→active` is light work — `status` does it alone.
- **`→done` = the "completion" moment = landing's trigger point.** Reaching `done` hands control to landing for wrap-up + archival decision. `status` itself still does not commit / archive — it recognizes completion and passes the baton.
- **End-of-turn debounce:** a `done` flip does **not** immediately run landing per-item; it marks "owes one landing" and runs landing **once before the AI returns control to the user** (end-of-turn — a *decidable* event, not an unimplementable "natural pause"), aggregating all of this turn's `done`s into the **same** landing. An explicit `/flightdeck:landing` is also a trigger. (See [landing auto-trigger](#rule-resolution-order) in Rule resolution order.)
- **Archival criterion = a deterministic structural edge** (not AI prose reading): a `done` artifact archives into `archive/` **iff no `active` artifact points at it via a structural edge** (`implements:` active plan → done spec). `supersedes` is traceability-only and is **NOT** a pinning edge — `flightdeck_index.py --archivable` does not include it in the blocking set. `flightdeck_index.py --archivable` computes the archivable-`done` set as a **reproducible fact** (same input → same conclusion); prose markdown links are for humans only and **don't enter the criterion**. Pointed-at by an active inbound edge → stays done-but-unlanded.
- **Drain, don't accumulate:** every landing rescans **all** `done`-in-place artifacts (not just this session's), sweeping away any whose inbound edges have cleared — so done-but-unlanded **drains automatically** and never lingers. Still-pointed-at ones are listed by `walkaround` as INFO (naming the **blocking active artifact**, not a vague "reason").
- **Landing failure does not roll back `done`.** `done` asserts **user approval**, not "landing's smoke-check passed" — the two are orthogonal. If landing fails mid-run (smoke-check error, script crash, interrupted session), the artifact stays `done` at its current location (done-but-unlanded); the next landing sweep picks it up. Never revert `status: done` on a landing failure.

The optional `note:` field carries the "why it hasn't moved" diagnostic (blocker / pending reason) that the merged `active` state would otherwise lose; cockpit + walkaround render it as `[note: …]`.

Status is just a label — the user edits it freely; at landing the AI may *suggest* the next typical status (per the recommended flow), applied only after the user confirms. walkaround flags odd values as INFO/warning, never blocks.

### 验证非阻塞 (non-blocking verification)

Verification is a **non-blocking marker, not a blocking gate**. The old "needs-verify → AI may NOT self-assert `done`" gate is **removed**: the AI **may** self-assert `done` (workflow) or write `stale` (knowledge) carrying a [`verify`](#verify--the-verification-marker) note. Safety comes from **visibility** — every preflight re-surfaces the verify debt via a deterministic scan — **plus reversibility**, NOT from blocking. Premise: preflight is the standard, 必经 entry — flightdeck's existing "single explicit entry point" design.

**Per-kind pass/fail** — the SKILL must first 识别 the artifact's kind (knowledge vs workflow), then act:

| | verification **passes** | verification **fails** |
| --- | --- | --- |
| **knowledge** (`stale`) | drop `verify`; flip `stale → active` | revive to `active` (`mv` back from `archive/` if archived); **keep `verify`** |
| **workflow** (`done`) | drop `verify`; stays `done` → becomes `--archivable` | revive to `active` (`mv` back from `archive/` if archived); **keep `verify`** |

Fail keeps `verify` (re-do + re-verify) — binary present/absent only, no `verify: failed` value. Multiple verify-debt items are handled **one at a time, independently**.

## INDEX.md (per-folder + root)

Every artifact folder has an `INDEX.md` — a derived index of that folder's files: one row per file `[file](file) — status — one-line summary` (knowledge folders add `when_to_read`/`applies_to`). The `<!-- AUTO -->` region is machine-maintained (regenerated from each file's frontmatter); an optional hand area sits outside it. `specs/INDEX` groups by status (`待启动（idea）` / `进行中·完成（active·done）`) — see [folder-semantics § specs/](folder-semantics.md#specs--designs).

The root `flightdeck/INDEX.md` is a sub-folder directory + global status summary (e.g. `specs/ — 3 (2 active, 1 done)`); it is a downgradeable component.

**Commands read the INDEX first and drill into individual files only on demand** — this is the main token saving (cost scales with folder count, not file count). landing regenerates only the INDEX of folders changed this session; walkaround does a full INDEX↔frontmatter consistency check.

## Folder map

```
flightdeck/                  [product name — kept]
├── cockpit.md   rules.md   [cockpit.md = interaction surface — metaphor kept]
├── specs/       INDEX.md   (idea / active / done)              workflow · self-authored · flat
├── plans/       INDEX.md                                       workflow · self-authored · flat
├── incidents/   INDEX.md   bug post-mortems                    knowledge · resident · nestable
├── checklists/  INDEX.md   process / conventions (执行)         knowledge · resident · nestable
├── docs/        INDEX.md   self-authored technical knowledge ★ knowledge · resident · nestable
├── references/  INDEX.md   imported external material (旧 charts/) knowledge · imported · nestable
└── archive/     (旧 landed/)                                   location (not a kind)
```

`docs/` (★ new in 3.0) holds **self-authored, resident, explanatory** project technical knowledge — architecture, design rationale, subsystem overviews, lifecycle/philosophy. It is what you **read to understand**, vs `checklists/` (what you **execute**), `references/` (what comes from **outside**), and `specs/` (one-shot design intent that archives when built). `archive/` is a first-class structural container (mirrors source kinds, handled specially by landing/index) but is **not a kind** — it answers "in the active area or not", not "what artifact is this" (artifacts keep their own kind). The archived files themselves **are** the landing record — flightdeck keeps no separate history log.

Reachability entries: `cockpit.md` / `INDEX.md` / `rules.md`. (No bundle README — multi-file topics live as several files in one folder, grouped via the INDEX hand area; only `references/` may contain an imported external project subtree.)

**Which folder?** Classify by lifecycle: design / idea (started or not) → `specs/` (`status: idea` = unstarted); execution plan → `plans/`; evergreen operational reference (executed) → `checklists/`; self-authored technical knowledge (read to understand) → `docs/`; imported external material → `references/`; post-incident records → `incidents/`.

**Routing is graph-based, not filesystem-based.** A file is "active" only if reachable from an entry (`cockpit.md`, `INDEX.md`, or `rules.md`). **A file nothing links to effectively does not exist** — no session reads it. Custom folders / root files are allowed but MUST be reachable from an entry, or they are orphans.

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

### Stale detection (`when_to_update`, dual-ritual)

Knowledge artifacts may carry `when_to_update`: a concrete-change-event phrase ("what kind of change would make me wrong"). When a change hits a doc's trigger, the ritual auto-flips `status: stale` — no pre-ask (stale is reversible, local, purely a warning; "docs quietly lying" is the worst failure mode).

`stale` covers **两个待复核来源** — `when_to_update`-matched suspected-outdated (this section) **and** new-but-unverified knowledge (`stale` + [`verify`](#verify--the-verification-marker)). The `verify` field distinguishes them: present = unverified, absent = `when_to_update`-outdated. Both render in the catalog as `⚠` (the scan splits them — `⚠待复核` vs `⚠未验证`).

**Detection runs at both rituals (landing=primary, preflight=read-only compensating):**
- **Exit-ritual (landing/soft-landing)** — primary: at turn end, compare this turn's changes against each doc's `when_to_update`; auto-flip stale on a match.
- **preflight (entry, compensating — read-only)** — diff `anchor..HEAD` plus worktree uncommitted changes against `when_to_update` fields; surfaces `stale` debt without writing (preflight reads but does not flip — any un-flipped stale is resolved at the next landing).

**Anchor:** the git ref recorded by the most recent exit-ritual (stored as a `Flightdeck-Sync:` trailer in the landing commit, or a small pointer file — exact storage is implementation-specific but must be a concrete recorded ref, never a guess). preflight diffs from this anchor forward (read-only; the anchor advances at the next landing, not at preflight).

**Idempotency:** `stale` detection is idempotent — already-`stale` docs are a no-op. If landing already flipped it, preflight's re-check just confirms the same result without extra side-effects.

**User-asserted exits only:** `stale→active` (after updating the doc to current truth) and `→obsolete` (confirming the doc is dead) are **both user-asserted**, consistent with the **no-verify** `→done` rule. The AI does not self-certify either direction — except via the verify-pass path (see [验证非阻塞](#验证非阻塞-non-blocking-verification)), where the SKILL flips `stale→active` on a user-performed verification that passes.

### Proactive incident resurfacing

Before starting a task whose description / file paths overlap with an incident's `applies_to` tags, surface it: "this touches `[tags]`, overlapping with [incidents/X.md](incidents/X.md) — worth a read first?". Recording a recurrence happens at the **other** end of the session: at landing, a **clear** same-incident match auto-appends `[Case N]` + bumps `recurrences` (see [exit-ritual § Step 5a](exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up)); an **ambiguous** match asks the user. Auto-counting is safe because the consequential step — *promotion* — stays user-gated.

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

A spec starts `status: idea` (unstarted, no date prefix). Starting it is **just a field flip** `idea → active` (which auto-adds the `YYYY-MM-DD-` prefix and surfaces it in cockpit `## 进行中`) — no folder move, no relation-edge rewrite. Each plan carries optional `implements: specs/<x>.md`. `location` (active vs `archive/`) is derived from landing a done item. Folder says the kind; frontmatter `status` says the state. While a plan is `active`, **checkpoints** keep the board synced at each plan-task boundary (cockpit `## 下一步` + the plan's `## Progress` `current:` pointer, disk-write only, no commit) — the lightweight subset of landing that makes a mid-plan close-and-reopen lossless. See [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath).

Beyond the `done`-triggered landing, an **end-of-turn knowledge increment** auto-runs a **soft-landing** (signal 3 — classify knowledge + regen changed INDEX + cockpit board, plus 「已保存」marker, no commit/archive); default-on, downgradable via House Rule `landing: don't soft-land at end-of-turn`. See [exit-ritual § Land-readiness](exit-ritual.md#land-readiness-check).

A passive **turn-end hook** additionally regenerates the mechanical board AUTO regions (`## 进行中` + each `INDEX.md`) at every end-of-turn on every host that fires it (Claude/Codex `Stop`, Cursor `stop`, Gemini `AfterAgent`) — a deterministic enhancement that keeps those regions from going stale between landings. It never blocks, archives, or writes judgment fields (`## 下一步` / `Active focus` / knowledge classification stay agent-driven); the protocol does **not** depend on it. (Live-verified on Claude Code; Codex/Gemini/Cursor pending Phase 0 verification — those hosts meanwhile regen on the next `landing` / `status` / `checkpoint`.)

A **rejected** spec is **deleted** (only on explicit user instruction; git log keeps the history, the commit body records the reason). There is no `scrapped` status value or tombstone group.

**Knowledge lifecycle:** `active ⇄ stale → obsolete` (stale auto-flipped by ritual on `when_to_update` match; obsolete drained to `archive/` by ritual — same drain logic as workflow `done`). `obsolete` is the **knowledge analog of workflow `done`**: a terminal state meaning "dead, pending drain", not an in-place tombstone. **`obsolete`-not-yet-drained ≡ `done`-but-unlanded** — both drain automatically on next landing/preflight, never linger permanently.

**Graduate seam** (spec → docs, at landing): a spec with `graduate: true` that reaches `done` is, at landing, **rewritten body-and-all into a permanent `docs/` entry** (current-truth view) and the source `specs/` file is moved there — no archive twin. Two paths for knowledge reaching `docs/`: (a) **graduate** — a `graduate: true` done spec that covers a new structural domain → new `docs/` entry; (b) **direct update** — an existing `docs/` entry already owns the topic → update it in place (no graduate). Discriminator: if a `docs/` entry already covers the topic, update it; else graduate a new one. The `graduate: true` flag window = the whole active life of the spec (can be added at any point before landing; missed flag = user's responsibility, no completion-time re-detection fallback). Idempotency key = "`graduate: true` done spec **still in `specs/`**" — once moved, the trigger key is gone and re-runs are safe no-ops. Graduate is landing's primary path; preflight is the compensating path (catches landing-not-run windows). Graduate-out docs must carry `when_to_read` / `applies_to` / `when_to_update`; omitting `when_to_update` opts the doc out of stale detection immediately.

## Exit ritual

90% of exits are obvious — classify and write directly. Only truly ambiguous items invoke brainstorming. The full decision tree (classification heuristics, hanging-task gate, INDEX regeneration, cockpit update) lives in [exit-ritual.md](exit-ritual.md) and is run by `/flightdeck:landing`.

After classifying: update `cockpit.md` (`Last updated` + regen `## 进行中` from `status: active` + auto-write `## 下一步` + any `Hanging tasks` changes); then commit locally per the commit default (auto local commit, **push asks**; skipped entirely under no-git — no separate log is written, the moved `archive/` files are the record). landing regenerates the INDEX of any folders changed this session.

## Ritual responsibilities — who owns what

Three entry rituals, three non-overlapping jobs — so no check is both everyone's and no-one's. When a check could belong to two rituals, this table decides:

| Ritual | Role | Writes? | Cockpit 80-line trim | INDEX | Deep per-file audit |
| --- | --- | --- | --- | --- | --- |
| `preflight` | read-only takeover at session start | **no (zero writes)** — deckless redirects to /flightdeck:launch | reads only — passive note on git state | reads folder INDEX as catalog | no — audits belong to walkaround |
| `landing` | write the session's outcome (full mode); board-sync only (checkpoint mode at task boundaries) | yes | **owns the trim** (proposes → confirms → edits) | regenerates changed folders' INDEX | no |
| `walkaround` | integrity audit on demand | version bump/migrate only (**sole version writer**); else proposes fixes, never auto-applies | flags `> 80` as INFO | full INDEX↔frontmatter check | **owns** status / orphan / dangling-ref / stray-file audits |

The 80-line cockpit trim is **landing's** (it is the only ritual that writes cockpit); `walkaround` only flags it; `preflight` never touches it.

Checkpoint is **landing's lightweight mode**, not a fourth ritual — it reuses landing's Step-4 board-sync and writes nothing else (no INDEX, no archive, no commit). `preflight` stays read-only; checkpoint never runs at entry.

## Write gate

`flightdeck/` records only content that **changes future behavior, influences decisions, or gets referenced repeatedly**. Session byproducts, debug logs, and chat play-by-plays do not qualify. Gate strictly.

**Skip — gate these out (do NOT write):** empty status checks (`status` / `ls` that surfaced nothing); **a dependency install / build command that merely succeeded with no derived conclusion** (`npm/pip/uv install`, a green build by itself); **an exploration that concluded nothing** (searched, neither found nor ruled anything out); **a repeat that added no new information** (same op rerun without widening coverage / reaching a new conclusion / eliminating a new possibility); one-off logs and trial-and-error play-by-plays ("today's log is…" / "I tried 5 ways").

**Two boundaries — NOT skips, do write:** ① an exploration that yields an **exclusionary conclusion** ("X is not the root cause") is negative knowledge — **write it**; ② a repeat that **brings new coverage / a new conclusion** — **write it**.

- ✅ write: "Cursor injection is fixed to `.cursor/rules/*.mdc` as the primary path (sessionStart proved unreliable)" — **influences future decisions, will be referenced repeatedly**.
- ❌ don't: "today's `--check` run printed clean" — a one-off status that changes no future behavior.

(This Skip list is the write gate's canonical negative list — passed before authoring *any* artifact. It runs parallel to `landing`'s `exit-ritual` heuristic **(g) One-off → DO NOT WRITE**, which is the first-match item at *classification* time; same direction, each self-contained.)

## Templates

See [templates.md](templates.md) for `spec` / `plan` / `incident` / `checklist` / `cockpit.md` / `rules.md` / `INDEX.md` templates.

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

## Incident error-library lifecycle

An incident is not just born and resurfaced — it can also be **retired** once its root cause is permanently fixed, and **revived** if the fix regresses. This is the "death" half of the error library; the "birth/use" half (Signature, fingerprint matching, hit path) lives under [routing](#routing--scenario-triggers) + [Proactive incident resurfacing](#proactive-incident-resurfacing).

### Retirement semantics (`resolved_by` + `status: obsolete`)

When an incident's root cause is permanently fixed (e.g. a guard test now prevents it), the incident is **retired**: fill `resolved_by` (a single reference — a commit SHA or a test id/path, e.g. `test_flightdeck_index.py::CockpitProjectionRobustnessTest`) **and** flip `status: obsolete`. These two are **one deliberate act**, performed at **landing** (the ritual that owns knowledge classification and retirement; `status` only touches workflow). Landing **never auto-flips** on a filled `resolved_by` — at most it *prompts* "resolved_by is filled but still active — retire?".

`obsolete` here means **"root cause fixed, retired from active routing, pending drain to archive/"** — it is **NOT "outdated / worthless"**. Knowledge status uses `active / stale / obsolete`; `obsolete` is the knowledge analog of workflow `done` (drain state — the ritual moves it to `archive/`).

### The obsolete dual path (drained to archive/, still grep-able cold)

`obsolete` only leaves the **active-recommendation routing** (excluded from the folder INDEX `<!-- AUTO -->` region and from the root knowledge count — zero session routing tokens). The ritual then **drains it to `archive/`** — same drain logic as workflow `done`. It is **not deleted**: an archived incident is still **on disk, still grep-able** in `archive/incidents/`, **and still entered into `--match-signature` / the landing recurrence sweep** (the sweep must scan `archive/incidents/` too — regression detection *depends* on retired incidents staying matchable). **Implementations must NOT hard-filter `obsolete` or `archive/` out of the match set.** A signature hit on an archived entry is the signal that a "fixed" bug may have come back — **revival = un-archive + flip back to `active`** (regression handling lives in [landing § Recurrence sweep wiring](../landing/SKILL.md#recurrence-sweep-wiring) — gated revival, never a silent re-append).

## Common mistakes — STOP and reclassify

| Mistake | Fix |
| --- | --- |
| Same fact in cockpit + incident + spec | One authoritative source; others link via `[name](incidents/X.md)` |
| Scratch written into flightdeck/ | Transient scratch lives in project-root `tmp/` (gitignored), not flightdeck. |
| `incidents/` writes "forgot / careless" | Root cause must be a wrong assumption / wrong model / wrong process. |
| External review feedback saved as its own file | Raw feedback is transient → project-root `tmp/`; its disposition (adopt / reject / defer) folds into the reviewed spec's `## 评审纪要`. |
| Brainstorming where every knowledge item belongs | Heuristics catch 90%. Default-brainstorm is the failure mode. |
| Cockpit > 80 lines | Trim immediately — drop finished items, move design detail to the relevant `specs/` file; history is `git log` + the `archive/` folder, not cockpit. (Landing owns the trim — see [Ritual responsibilities](#ritual-responsibilities--who-owns-what).) |
| Bumping `Last updated` on every commit / typo / grep | Signal pollution. Only bump on 4 triggers in exit-ritual.md `Cockpit update`. |
| Incident / checklist without required frontmatter | STOP, report file path + missing fields. Add or delete before proceeding. |
| Incident / checklist with `last_updated` > 1 year in a fast-moving project | Likely stale advice. Bump after re-verifying or flip to `status: obsolete`. |
| "Save in case it's useful later" | No. Gate strictly. |

## Authoring new artifacts

Producing a new deck artifact (spec / plan / incident / checklist / chart) — including from an external authoring skill (brainstorming / writing-plans) — goes through **`/flightdeck:new`** (script: `scripts/flightdeck_new.py`), which stamps the correct per-kind frontmatter + naming and regenerates INDEX/cockpit. The full contract (kind→folder, naming, per-kind frontmatter, default status, slug rule) lives in `skills/new/SKILL.md` — the single authority, so the shape is never re-derived from scattered docs. **Shell-first**: create the shell via `new` first, then write the body into the returned path; do not hand-derive a path or write to `docs/`.

## Brand glyphs (per command)

每个 flightdeck 命令在其**运行时主报告/完成行**带一枚品牌 emoji（仅报告行，不进 deck 文件、不进 scaffolds）。这是**文档级单一真相源**——各 skill 硬编码自己那枚，新增命令照此表配字形。`✈️`（U+2708 + FE0F）保留作项目 wordmark（README 标题），**不**作命令字形。

| 命令 | 图标 | codepoint | 语义 |
|---|---|---|---|
| launch | 🛠️ | U+1F6E0 FE0F | 造甲板 / 首次建机 |
| preflight | 🛫 | U+1F6EB | 起飞前就绪 |
| walkaround | 🔍 | U+1F50D | 绕机巡检 / 审计 |
| new | ✍️ | U+270D FE0F | 新建工件 |
| status | 🔄 | U+1F504 | 状态流转 |
| landing | 🛬 | U+1F6EC | 着陆归档 |
| emit-agents-md | 🌉 | U+1F309 | 跨工具桥 |

效力边界：被动文档约定，无程序强制——改某命令字形须人工同步本表（preflight 不自动校验）。

## Cross-references

The flightdeck convention describes WHAT to write and WHERE; the tool that produces the content is up to you (hand-write, use any AI skill, or ad-hoc LLM).

**Optional companions** (Claude Code with the `superpowers` plugin installed):
- `superpowers:brainstorming` → produces well-structured designs that fit `specs/`; hand the design off to `/flightdeck:new spec` (shell-first) so frontmatter/naming/regen are stamped, not re-derived.
- `superpowers:writing-plans` → produces task lists that fit `plans/` (via `/flightdeck:new plan`). Plan files use `- [ ]` checkboxes for executing-plans tracking; **flightdeck does not require flipping these** — progress lives in `cockpit.md` + commit log.

These are convenient but **not required** — flightdeck accepts content from any source.

The `flightdeck/` directory structure is **tool-agnostic** — any AI assistant can follow these conventions via project-level instructions. See `adapters/` for per-tool install paths.
