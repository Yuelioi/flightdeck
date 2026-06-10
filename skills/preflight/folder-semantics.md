# Folder semantics

Reference for every `flightdeck/` subdirectory: what it holds, naming convention, lifecycle, and links to related folders.

## Deck layout (3.x: full, always)

As of 3.x, both `/flightdeck:launch` (first-time deck creation) and `install --scaffold` lay the **full layout** — every folder with its `INDEX.md`, plus the minimal contract files. There is no longer a minimal/full choice (the `scaffolds/minimal` variant was removed).

| Concept | What it means |
| --- | --- |
| **Full layout** (what init creates) | all folders (`specs/ plans/ incidents/ checklists/ docs/ references/`), each with its `INDEX.md`, + `cockpit.md` + `rules.md`. `archive/` is created on demand at first land — not pre-shipped |
| **Minimal contract** (validation floor) | `rules.md` (+ `version`) + `cockpit.md` must exist — the *floor*, not a scaffold variant (a legal deck always has them: `launch` copies the scaffold verbatim) |

**Empty is the normal initial state.** A freshly scaffolded deck has empty folders + empty `INDEX.md` files — expected, not an anti-pattern. Under the full layout a **missing** known folder is the anomaly (walkaround flags it); an **empty-but-present** folder / `INDEX.md` is fine and never flagged. (This reverses the pre-3.x "add folders on demand" guidance.)

## Routing model

**Flightdeck is graph-routed, not filesystem-routed.** A file is "active" only if it is reachable from some entry — `cockpit.md`, `rules.md`, or a folder `INDEX.md`. **A file not reachable from any entry effectively does not exist** (no session will ever read it). `walkaround` audits reachability.

Reachability edges are markdown links from an entry. Custom folders / root files are allowed — flightdeck favors extensible conventions over a locked taxonomy — **but they must be reachable from an entry**, or `walkaround` flags them as orphans.

## Which folder? (decision table)

Classify by lifecycle — the folder is the kind, so files carry no type field:

| What you have | Goes in |
| --- | --- |
| Idea / design — unstarted (`status: idea`, no date prefix) or active to implement | `specs/` |
| Implementation plan (optionally `implements:` a spec) | `plans/` |
| Bug + root cause worth not repeating | `incidents/` |
| Repeated procedure / convention you *execute* (second run = pattern) | `checklists/` |
| Self-authored, resident, explanatory knowledge — "how the system works / why it's built this way" (architecture, design rationale, subsystem overviews) | `docs/` |
| Imported external material (competitor code, RFCs, articles) | `references/` |
| External review / AI critique | disposition folds into the reviewed spec's `## 评审纪要`; raw feedback → project-root `tmp/` |

The common mistake is keeping an evergreen reference in `specs/` or `plans/`. A spec/plan is a *design or plan you intend to build and then archive*; an evergreen resource you consult repeatedly belongs in a knowledge folder. The split among the knowledge folders: `checklists/` = process / conventions you **execute**; `docs/` = explanatory knowledge you **read to understand**; `references/` = imported external material. Keep those distinctions clear.

## The folders + entry files

```
flightdeck/
├── cockpit.md          # The single must-read entry (≤80 lines): focus / next / hanging
├── rules.md            # Mandatory file (minimal contract); content optional — read first by every entry skill
│
├── specs/              # Designs & ideas (status: idea / active / done)
│   └── INDEX.md
├── plans/              # Implementation plans (carry optional implements:)
│   └── INDEX.md
├── incidents/          # Post-incident records (bugs + root cause)
│   └── INDEX.md
├── checklists/         # Process / conventions you execute (knowledge)
│   └── INDEX.md
├── docs/               # Self-authored resident technical knowledge — how/why the system works
│   └── INDEX.md
├── references/         # Imported external material (may hold an external project tree)
│   └── INDEX.md
│
└── archive/            # Archive umbrella — created on demand at first land; mirrors source structure
```

## Entry files

### `cockpit.md` — the single must-read

**The only required file.** Read first, updated last. Hard ceiling: **80 lines**.

The 80-line ceiling is cognitive-load engineering for the human + AI reading cockpit at every session start — treat it as a load-bearing constraint, not a style preference.

Contains:
- `Last updated: YYYY-MM-DD by <who> (<one-line>)`
- `Active focus: <current main thread>`
- `## 进行中` — AUTO region derived from every `status: active` spec/plan (machine-maintained; not hand-written).
- `## 下一步` — the next concrete single action (AI-maintained, auto-written at landing).
- `## Hanging tasks` — open items blocking a clean landing (hand-maintained; decoupled from INDEX auto-summaries).

`cockpit.md` is no longer a hand-maintained workspace — it is a **status projection** of the active set: `## 进行中` is derived from `status: active`, so an artifact is in cockpit iff it is active. Full structure + AUTO markers: [templates.md § cockpit.md](templates.md#cockpitmd).

### `rules.md` — project config (mandatory file, optional content)

Read first by every entry skill. As of 3.0 it carries just `version` + free-prose house rules (`### Project conventions` + `### Autonomy overrides`). Most behavior is inferred (git/emit/scripts from `.git` / `AGENTS.md` / runtime presence), decided by skill judgment (landing's archive call), or defaulted and overridden via the `### Autonomy overrides` segment — see [protocol § Rule resolution order](protocol.md#rule-resolution-order). The **file** is mandatory (part of the minimal contract) and must carry `version`; its **content** is optional — a minimal `rules.md` = the built-in defaults (local commit auto, push asks; all rituals self-invoke; landing archives by judgment). Full schema: [templates.md § rules.md](templates.md#rulesmd).

### No separate landing log

flightdeck keeps **no history-log file** under any git mode. The durable landing record is the moved files in `archive/` (+ `git log` on git-backed decks) — `preflight` reads files, not a journal. A no-git deck (e.g. a gitignored `flightdeck/`) loses nothing: the archived artifacts themselves are the history.

## INDEX.md (per-folder)

Every artifact folder has its own `INDEX.md`. This is the derived index for that folder: one row per file showing file, status, and a one-line summary. `incidents/`, `checklists/`, `docs/`, `references/` rows add `when_to_read` / `applies_to`. `specs/INDEX` groups its AUTO region by status — see [`specs/`](#specs--designs) below.

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

### `specs/` — designs

Design documents **and** unstarted ideas — one folder, status tells them apart. A spec captures the *what* and *why* of a change; it is the output of the brainstorming / design stage. An unstarted idea is just a spec at `status: idea`.

**`status: idea`** = an unstarted thought / design (the to-start pool). No date prefix — ideas are timeless until acted on (`<topic>.md`). Starting it is a single field flip `idea → active`, which **adds the `YYYY-MM-DD-` prefix** (date helps order active/done by recency) and surfaces it in cockpit `## 进行中`. No folder move, no relation-edge rewrite — that is the whole point of merging sketches in.

**Rejecting a spec** = the idea / design is abandoned, so the file is **deleted** (only on explicit user instruction — the AI never abandons work unilaterally). git log keeps the history; record the reason in the commit body. There is no `scrapped` status value, no tombstone, no `graveyard/` subfolder — `specs/` holds only live designs (idea / active / done).

The folder is the kind — files carry no type field. No `implements:` (that goes on the plan side).

Lifecycle: when a spec is done and all its plans are complete, `land` it — move to `archive/specs/foo.md`. The spec leaves the active routing set but its history is preserved.

**`specs/INDEX` status grouping**: idea files have no date prefix, so mixing them with the `YYYY-MM-DD-` active/done files would sort badly. The INDEX AUTO region **groups by status**: `待启动（idea）`, `进行中·完成（active·done）` — active/done by date descending, idea alphabetically.

### `plans/` — implementation plans

Task-level breakdowns of how to execute a spec (or a standalone piece of work). Plans carry the optional `implements:` back-reference to the spec they execute. A plan body carries a `## Progress` block with a `current:` pointer to the next-to-execute task; checkpoints advance it at task boundaries and cockpit `## 下一步` quotes it (see [exit-ritual § Checkpoint](exit-ritual.md#checkpoint--lightweight-board-sync-subpath)). The pointer is body-only — it is **not** a frontmatter field and does not enter any INDEX.

Naming: `YYYY-MM-DD-<topic>.md`.

`implements:` is a single unidirectional reference. To see which plans implement a given spec, read `plans/INDEX.md` — do NOT add a reverse `implemented_by:` field to the spec.

A plan without `implements:` is valid but `walkaround` surfaces an INFO ("orphan plan — no spec linked").

### `incidents/` — post-incident records

Mistakes worth not repeating. Format strictly enforces useful root cause (template in [templates.md](templates.md#incident-report-body)).

Naming: `<topic>.md` (no date prefix — incident reports are reference, not log).

Recurrence rule: same incident happens again → **append `## [Case N]`** to existing file. Do not create a new file. Repeated recurrence (≥3 times or single severe case) → promote one-liner to your project agent rules.

`last_updated` must be bumped on each Case append or status flip (per the canonical field table).

**Lifecycle (active → obsolete → revived):** an incident carries a `## Signature` block (grep + dedup anchor) and a `resolved_by` field. Its life:
- **active** = a live error worth resurfacing; routes normally and is matched by `--match-signature`.
- **obsolete (retirement)** = the root cause is permanently fixed. At landing, fill `resolved_by` (a commit SHA or test id) **and** flip `status: obsolete` as one deliberate act (landing prompts, never auto-flips). Obsolete then **drains to `archive/incidents/`** like any dead knowledge (obsolete = knowledge analog of workflow `done`); it stays **grep-able + still matched there** because `--match-signature` scans `archive/incidents/` too — so the archived entry remains the historical record *and* the regression tripwire. `obsolete` here = "fixed and retired", not "outdated/worthless".
- **revived (regression)** = a later signature hit lands on an obsolete entry in `archive/incidents/`. On confirmed regression, landing **un-archives it** (moves it back into `incidents/`), flips it back to `active`, clears `resolved_by`, and adds a Case noting the regression; `recurrences` keeps accumulating (lifetime count, never reset). Full sweep wiring: [landing § Recurrence sweep wiring](../landing/SKILL.md#recurrence-sweep-wiring); semantics: [protocol § Incident error-library lifecycle](protocol.md#incident-error-library-lifecycle).

### `checklists/` — procedures (you execute)

Authored **process / conventions you execute**: reusable checklists, conventions, and operational standards you *run through* more than once. (Process-type knowledge — contrast `docs/`, which is explanatory knowledge you *read to understand*.)

Naming: `<topic>.md` (no date prefix — checklists are stable resources).

Promotion rule: a process becomes a checklist the **second** time you run it. First time = ad-hoc. Second time = pattern.

`status: obsolete` = the external constraint no longer exists; a `supersedes:` edge on the newer checklist records the replacement for traceability. Obsolete checklists are drained to `archive/` by the ritual — no indefinite stay in the active area.

### `docs/` — technical knowledge (you read)

Self-authored, **resident, explanatory** technical knowledge about *this* project — "how the system works, why it's built this way": architecture, design rationale, subsystem overviews, module reference, lifecycle / philosophy. It fills the gap no other folder covered (`checklists/` is process, `references/` is imported); a root-level `docs/` outside flightdeck isn't read by preflight, so resident project knowledge lives here.

Four boundaries that keep it distinct:

| vs | Distinction | One-line test |
| --- | --- | --- |
| `docs/` vs `checklists/` | explanatory vs procedural | docs is what you **read to understand**; a checklist is what you **execute** |
| `docs/` vs `references/` | self-authored vs imported | docs is **ours**; references comes **from outside** |
| `docs/` vs `specs/` | resident vs one-shot | a spec is a *design you intend to build then archive* (`idea/active/done`); a doc *describes an already-built system* — resident, never archived on completion |

**Mixed-type tie-breaker** (e.g. `release-process.md` reads like both steps and knowledge): judge by **primary use** — mostly **step through it** → `checklists/`; mostly **read it to understand the system** → `docs/`. If one file is genuinely both and both halves matter, **split it in two** (steps → checklists, rationale → docs, cross-linked). Default leans to "execute" → checklists.

**docs/ vs an archived spec** (avoid two sources of truth): per the existing [source-of-truth precedence](protocol.md#source-of-truth-precedence-when-sources-disagree), the **active `docs/`** outranks an archived spec in `archive/`. After a feature ships, its spec lands in `archive/` (the frozen history) while the durable knowledge of *how it ultimately works* graduates into `docs/` (the current truth). This divergence is "history ≠ present", not drift — no `source_spec` / `graduated_from` field tracks the graduation (it's a human edit; trace origin via git history if needed).

**Graduate path**: structural design specs (`graduate: true`) land here after `done` — landing rewrites the spec body into a "current truth" doc and moves it into `docs/`; this is the primary route by which `docs/` grows. New entries from graduate should always carry `when_to_update` (the condition that invalidates this doc) so the ritual can auto-flip them `stale` when the relevant code changes.

Naming: `<topic>.md` (no date prefix — resident reference, same as checklists/incidents).

Frontmatter: the **knowledge** set (`status: active/stale/obsolete` + `when_to_read` + `applies_to` + `last_updated` + `summary` + optional `when_to_update`), so preflight can warm it in the routing catalog. `stale` = 待复核：疑似过期 或 新产出未验证（由 verify 字段区分）；`obsolete` = 已死·待归档排水态（knowledge 版的 workflow `done`），被仪式排入 `archive/`。

### `references/` — external material

External docs, competitor source code, RFCs, blog posts, etc. — a single place for "where do I find that thing".

Naming: `<source>-<topic>.md` (e.g. `boltframe-shape-layer.md`, `rfc-6749.md`).

**Imported external project tree**: when importing an entire external project (competitor code, an RFC suite, a large article series), place it at `references/<project>/` and add a `references/<project>/INDEX.md` as a human-readable guide to the project's contents. The root `references/INDEX.md` row for that project shows project count + "imported" rather than a status count (imported files do not carry uniform flightdeck frontmatter).

### External review feedback (no folder)

There is **no `debriefs/` folder**. External review feedback (other AIs, colleagues) is a **transient input**: keep the raw text in project-root `tmp/` (gitignored), read it, and fold its **disposition** (adopt / reject / defer) into the reviewed spec's own section — conventionally `## 评审纪要`. The raw feedback is discarded once dispositioned; only the decision survives, inside the spec it shaped.

`tmp/` itself is **the user's habit — flightdeck does not regulate its structure or cleanup**. flightdeck only mandates: external-feedback disposition lands in the reviewed spec. Where the raw input lives and how long it stays is up to the user.

### `archive/` — archive umbrella

Top-level archive for completed or retired work. `archive/` **mirrors any source folder on demand** — create the matching subdirectory the first time you archive something of that kind.

`archive/` is a **first-class structural container** (it mirrors the source kinds, and landing / index / migration treat it specially) — **but it is not itself a kind.** It does not answer "what kind of artifact is this" (the artifact keeps its own kind); it only answers "is it still in the active area?" — i.e. it is the `location` axis made concrete, orthogonal to `status`. The archived files themselves **are** the landing record — there is no separate log file.

- `archive/specs/` — specs archived after the work is done.
- `archive/plans/` — plans archived after execution.
- `archive/incidents/`, `archive/checklists/`, `archive/docs/`, `archive/references/` — obsolete-but-historical reference moved out of the active set.

Archiving vs `status: obsolete`: flip `status: obsolete` to signal "dead, awaiting archive" (still reachable, marked dead — knowledge analog of workflow `done`); the ritual then drains it to `archive/`. **Moving to `archive/`** removes it from the active routing set while preserving history. Archived files lose to current state in [source-of-truth precedence](protocol.md#source-of-truth-precedence-when-sources-disagree). Routing already excludes everything under `archive/`.

Archived files are **exempt from status and INDEX audits** — `walkaround` does not check `archive/`.

## Multi-file topics — nesting by axis

Nesting is decided **by axis**, not by per-folder exception:

- **Knowledge folders MAY nest by area.** `NESTABLE` = the four knowledge kinds: `incidents/`, `checklists/`, `docs/`, `references/`. Place files under `<folder>/<area>/` with its own `<folder>/<area>/INDEX.md`. A subdirectory is **only an organizational partition within the same kind — never another kind** (that would reintroduce the "what kind is the subfolder" question). Depth is not capped: every level carries its own `INDEX.md`, and the top-level `<folder>/INDEX.md` becomes an **INDEX-of-INDEXes** listing each area (each row carries a one-line purpose + `last_updated`); preflight reads only the top INDEX to know-what-exists and drills down on demand.
- **Workflow folders are strictly flat.** Do **NOT** create subfolders inside `specs/` or `plans/`. When one workflow topic needs several files (a large spec broken into chapters), keep them all in the same folder and group them in that folder's `INDEX.md` hand area (outside the `<!-- AUTO -->` region) with a label like `### Auth redesign (3 files)`.

**Why the split — drain vs accumulate.** Workflow is one-shot: once `done` it drains into `archive/`, so the active set stays capacity-bounded — flat + INDEX date-ordering is enough (group by feature via the INDEX hand area, not subdirectories). Knowledge is resident and only grows (never archived on completion), so it needs by-area nesting to stay navigable at scale.

## Organizing knowledge at scale (large projects)

On a large codebase the question is not "which folder" but "how does an AI find the *right* knowledge for the task in front of it, without loading an encyclopedia." There are four **shapes** of knowledge — each with a different job, home, and anti-drift mechanism. Picking the shape (not just the folder) is what keeps a big deck navigable.

| Shape | Form | Answers | Home | Stays fresh by |
| --- | --- | --- | --- | --- |
| **Golden path** | line (verb) | how to *do* a recurring task | `checklists/` | points to a canonical example + mechanism backstop |
| **Cross-cutting concern** | column (aspect) | how to get *one* concern right | `checklists/` or `docs/` | authored once + pushed into lint/wrappers |
| **Map** | plane (noun) | what *exists*, which to change | `docs/` | generated/checkable inventory |
| **Rationale** | point (why) | why it is built this way | `docs/` | thin, written on demand |

**Golden path = task-anchored spine.** Do **not** organize knowledge by topic ("everything about logging") — an AI arrives with a *task* ("add an endpoint"), not a topic. Author one entry per recurring task (`checklists/backend/add-endpoint.md`, `.../add-service.md`, `checklists/frontend/add-page.md`). Each entry owns only the *orchestration* — the order of steps — and **links out** at each step to the concern / map / example that step needs. One trigger match, one hop, everything pulled in. This is why routing (`when_to_read`) beats volume: the win is "this task fires exactly the 1–3 files it needs," not "the encyclopedia is complete."

**Cross-cutting concerns are columns, not repeated rows.** i18n, logging, auth, validation thread through *every* golden path. The trap is re-teaching them inside each path → the same rule duplicated across N files → drift (the #1 source of both the "too heavy" and "goes stale" failures). Factor by axis instead:

- Tasks are **rows** (golden paths) — they own order.
- Concerns are **columns** — authored **once** (e.g. `docs/backend/i18n.md` for the model + a short executable rule); every row only **references** the column.
- A **cell** (concern × task) is usually just the link. Add a line only for the *task-specific glue* that is genuine intersection knowledge (e.g. "service-layer i18n keys use prefix `services.<domain>.*`") — that line is not duplication, it belongs nowhere else.
- **Push the column down into enforcement where you can.** A concern guaranteed by a wrapper (`withLogging()`) or a lint rule (`no-literal`) needs *no* per-path instruction — the path only notes the mechanism exists so the AI doesn't hand-roll around it. The more enforced a concern is, the thinner every golden path becomes. `enforce > document`.

**Maps are nouns: generate the inventory, hand-write the judgment.** A subsystem map (`docs/backend/services.md`) answers "what exists / which one do I change," not "how." Split it the way `INDEX.md` itself splits (AUTO region + hand area):

- The **inventory** (the list of services / modules) is mechanically enumerable → generate it from the filesystem and **check it back against the filesystem** (an entry in code but not the map — or vice versa — is a CI failure, not silent rot). This filesystem cross-check is the only reliable defense against map drift; never hand-maintain the list.
- The **"which to touch when" judgment** (reverse-intuition routing: "send mail only via `NotifyService`," "rate-limiting lives in `middleware/`, not a service") is what code cannot express — the only part worth hand-writing.
- Maps cross-link to golden paths: the map locates the noun, the golden path verbs it. Don't restate the "how" inside a map.

**The throughline.** Making an AI fast on a large project is not writing a complete encyclopedia — it is building a *task → one-hop* routing net: the mechanical parts (inventories, uniform conventions) handed to generation and lint, and humans writing only what code can't — **order, choice, and why**. As with checklists and incidents, write a doc the **second** time an AI gets something wrong for lack of it: demand-driven, so the doc set stays bounded and every file earns its place.

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
| Subfolders inside `specs/` / `plans/` (workflow) | Breaks the flat, drain-into-`archive/` model | Keep all files in the folder; group in INDEX hand area (knowledge folders may nest by area — see [Multi-file topics](#multi-file-topics--nesting-by-axis)) |
| Subfolder under a knowledge folder that is *another kind* (e.g. `docs/checklists/`) | Reintroduces "what kind is the subfolder?" | A nested subdir is an **area within the same kind** only |
| Using `README.md` inside flightdeck conventions | Bundle README approach retired | Use `INDEX.md` (repo-root `README.md` is unaffected) |
| Plan with no `implements:` and no explanation | Orphan plan is invisible to spec→plan tracing | Add `implements:` or note "standalone" in the plan body |
| Knowledge file (incident / checklist / doc / reference) without `when_to_read` | Invisible to skill routing | Add `when_to_read` frontmatter |
| Re-teaching a cross-cutting concern (i18n / logging / auth) inside every golden path | Same rule duplicated across N files → drift | Author the concern once (a column); each path links to it + adds only task-specific glue |
| Organizing knowledge by topic for AI consumption ("all about X") | AI arrives with a task, not a topic — can't route to it | Anchor golden paths on tasks (verbs); anchor maps on nouns |
| Hand-maintaining a subsystem inventory (service / module list) | Goes stale the moment one is added | Generate the inventory + check it against the filesystem; hand-write only the "which when" judgment |
