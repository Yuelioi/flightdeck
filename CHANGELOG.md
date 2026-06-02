# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] — 2026-06-03

Autonomy release: new decks ship full-auto, a `commit_mode` landing policy, and a more robust Land Routine. Additive and backward-compatible — existing decks keep their current behavior and `version` silently advances 2.2 → 2.3 on the next `preflight` (no migration).

### Added
- **`commit_mode` rules.md toggle** (`manual` / `confirm` / `auto`, default `confirm`) — controls landing's commit step independently of `git` and `model_invocable`: `manual` never commits, `confirm` asks (the pre-2.3 behavior), `auto` commits unprompted. Applies only when `git: true`. Removes the last manual checkpoint for a headless run.
- **Full-auto defaults for new decks** — scaffolds (`minimal` + `full`) and `preflight` first-time-setup now write `model_invocable: [preflight, landing, walkaround, emit-agents-md, status]` + `status_auto: [start, land]` + `commit_mode: confirm`, so a freshly created deck drives status/landing itself out of the box (commit stays the one confirm-gated step). The gate fallback is unchanged (absent / empty = manual), so existing and hand-made decks are unaffected.

### Changed
- **Land Routine rewritten to collect-then-migrate** — landing now builds the full old→`landed/` remap for the entire land set *before* moving, then rewrites `implements` / `supersedes` / `related` across the active tree **and** the moved set. Fixes dangling edges when co-landing a mutual-reference cluster (the old inbound-only pass missed intra-set edges).
- **Docs** — README / README.zh gain a Configuration section documenting the full `rules.md` surface + an autonomous-operation guide; Roadmap de-staled to 2.x; TEST_PLAN gains 2.1 / 2.2 points; the Claude adapter install/uninstall now lists the `status` skill.

### Migration
- Additive / opt-in — `layout_need_update` unchanged (stays `[2.2]`); no deck migration. `version` silently bumps 2.2 → 2.3 on next `preflight`. To adopt full-auto on an existing deck, add the keys to `flightdeck/rules.md` (or re-scaffold). Reinstall/sync the plugin-cache copy to load the updated skills. See [MIGRATION.md](MIGRATION.md).

## [2.2.0] — 2026-06-03

Metadata-model consolidation + workflow frontmatter enrichment, with the deck-conformance version relocated into a now-mandatory `rules.md`. **Existing decks need a one-time migration** — see [MIGRATION.md](MIGRATION.md) (2.1 → 2.2).

### Added
- **Workflow frontmatter enrichment** — sketches/specs/plans gain recommended `summary` + `last_updated` and optional `supersedes` / `related` edges. `summary` drives the INDEX row (rows now derive purely from frontmatter); `last_updated` is auto-bumped by `status`/`landing`; relation edges are forward-only (reverse is grep-derived). ([spec](flightdeck/specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md))
- **Canonical frontmatter field table** in `protocol.md` — single source of truth; `templates.md` / `folder-semantics.md` / `walkaround` defer to it instead of restating field semantics. ([spec](flightdeck/specs/2026-06-02-metadata-model-consolidation-design.md))
- **walkaround Audits 11–12** — aggregated INFO for missing workflow `summary`/`last_updated`, plus dangling `supersedes`/`related` edge detection.

### Changed
- **`rules.md` is now mandatory** and carries the deck-conformance `version:` — part of the minimal 3-file contract (`rules.md` + `cockpit.md` + `landed/HISTORY.md`). `preflight`/`walkaround` compare it against `MIGRATION.md` (`current` + `layout_need_update`) to detect migrations. ([spec](flightdeck/specs/2026-06-02-version-in-rules-migration-detection-design.md))
- **The `` `**Layout**` `` line is removed from `cockpit.md`** — the version now lives in `rules.md`; cockpit is pure focus.
- **INDEX rows derive from `summary`**, and `landing` rewrites inbound `supersedes`/`related` edges to the `landed/` prefix on archive.

## [2.1.0] — 2026-06-02

Soft-config gating + a new high-frequency status ritual. Additive and opt-in — `flightdeck/` Layout stays 1.2; default behavior is unchanged.

### Added
- **`model_invocable` rules.md toggle** — per-project soft gate replacing the global `disable-model-invocation` hard switch on the four entry skills. Default `[]` = all manual (identical to before); opt a ritual into model self-invocation with e.g. `model_invocable: [landing]`. ([spec](flightdeck/landed/specs/2026-06-02-soft-config-model-invocation-design.md))
- **5th ritual `/flightdeck:status`** — high-frequency, model-invocable lifecycle auto-flip of a single artifact's `status:` + its INDEX row (forward-only; never touches cockpit/commit). ([spec](flightdeck/landed/specs/2026-06-02-status-lifecycle-skill-design.md))
- **`status_auto` rules.md toggle** — opt-in list controlling which *optional* status transitions (`start`, `land`) the `status` skill auto-applies; core `create→pending` / `finish→awaiting-review` are always automatic.
- **rules.md key admission policy** — a 4-point gate in `protocol.md` governing when a new toggle may be added (anti-sprawl).

### Changed
- The four entry skills no longer carry `disable-model-invocation`; self-invocation is gated by `model_invocable` (default-off). The gate ships in the shared `SKILL.md` body, so it reaches every platform.
- **Land procedure extracted** into a single shared `## Land Routine` anchor in `exit-ritual.md`; `landing` and `status` are two invocation paths over one implementation.
- `preflight` now surfaces `done`-but-unlanded artifacts in any folder (not just plans).

### Migration
- Additive / opt-in — Layout stays 1.2; existing decks need no changes. To adopt the new automation, add the opt-in keys to `flightdeck/rules.md`. Reinstall/sync the plugin-cache copy so the new ritual loads. See [MIGRATION.md](MIGRATION.md).

## [2.0.0] — 2026-06-02

Entry-layer collapse: one explicit entry skill, no auto-load. (Unrelated to the abandoned work-items "2.0" line — this 2.0 is purely about the entry model; `flightdeck/` layout is unchanged at 1.2.)

### Removed
- **Auto-loaded `workflow` skill** and the **SessionStart hook** — flightdeck is now manual-only. `/flightdeck:workflow` no longer exists.

### Changed
- **`/flightdeck:preflight` is the single entry point** — it initializes `flightdeck/` when absent (no `cockpit.md`), otherwise reconciles + reports (unchanged read behavior). Protocol knowledge moved into `skills/preflight/` (`protocol.md` + relocated companions).
- **Empty-`Next session` fallback unified** (`specs/` + `plans/` + `sketches/`), fixing a prior workflow/preflight divergence.

### Migration
- `flightdeck/` decks need no changes — Layout stays 1.2. Run `/flightdeck:preflight` explicitly at session start. See [MIGRATION.md](MIGRATION.md).

## [1.3.0] — 2026-06-01

### Added
- **Layout version stamp** — cockpit headers carry `**Layout**: <ver>`; `preflight` and `walkaround` compare it against the current layout version instead of always scanning for legacy 1.x filenames. Healthy decks pass silently; unstamped decks fall back to the (now-frozen) legacy-marker check. Never migrates silently.

## [1.2.0] — 2026-06-01

Refinement of 1.1.x: explicit metadata, derived-index reads, folder renames, and a streamlined cockpit. This is deletion + clarity, not a new model — 1.1.x installs migrate with a straight folder rename and adding `status:` frontmatter. See [MIGRATION.md](MIGRATION.md).

### Added
- **Explicit `status:` frontmatter** (required on every artifact) — replaces location-implicit state. Each file now declares its own lifecycle state directly; folder location is no longer the source of truth.
- **Per-folder `INDEX.md`** + root **`flightdeck/INDEX.md`** derived index (file / status / one-line summary). Entry skills read INDEX first to orient without loading every artifact — saves tokens and speeds up preflight.
- **`plans/`** folder with optional **`implements:`** frontmatter pointing to the spec a plan executes.
- **`sketches/`** and **`specs/`** retained and clarified in the folder-choice decision table.
- **`debriefs/`** folder (replaces `safety-reviews/`) for post-incident retrospectives.

### Changed
- **Folder renames** (breaking for existing installs, one-line fix): `incident-reports/` → `incidents/`, `safety-reviews/` → `debriefs/`, `flight-plans/` → `plans/`. Canonical folder set is now `sketches/ specs/ plans/ incidents/ checklists/ charts/ debriefs/` + `landed/`.
- **Cockpit is pure focus** — `## Active focus` / `## Next session` / `## Hanging tasks` only. The artifact-list section is gone; artifact state is now tracked via `status:` frontmatter and INDEX, not a cockpit list.
- **`README` → `INDEX` naming** within conventions and scaffolds. Folder = kind (implicit) + explicit `status:` replaces the old README-as-index idea.
- **Conventions doc** and scaffold templates updated throughout for the new folder names and `status:` field.

### Removed
- `manifest.md` and `logbook.md` — replaced by INDEX reads and `git log`; session scratch lives in project-root `tmp/`.
- `kneeboard/` folder — removed; no replacement needed.

## [1.1.1] — 2026-05-30

Reliability + clarity hardening of the four entry skills, driven by multi-model review of each skill's instructions. No new capabilities — backward-compatible.

### Changed
- **preflight** — now reports the first "Next session" item and **stops** (read-only recon); executing it is the next turn, not folded into the entry ritual. Catalog reads tightened: `Glob` real paths (never guess filenames), frontmatter-only reads in one batch (never full-file / duplicate). Trimmed verbosity and the executor-facing `workflow` cross-link.
- **walkaround** — Audit 8 (AGENTS.md drift) replaces the unexecutable "mentally re-run the recipe" with a concrete field-by-field comparison; Audit 1 adds frontmatter *value* validation (ISO date / list shapes); Audit 3 strips `#fragment`s and verifies files only; the "report once" dedup between Audits 1/9/10 became an explicit skip condition; Audit 6 flags only on high confidence; stray-files no longer false-flag assets/structured-data; absent target folders report ✅ N/A.
- **landing** — the length check is now non-destructive (move overflow to logbook/manifest, confirm before removing) and fires right after step 3, not after commit; step 5's AGENTS.md trigger corrected (`In flight` lives in `manifest.md`, not cockpit); "no new knowledge is a valid outcome"; blocking hanging tasks pause the ritual; opaque `gate (g)` reference made self-contained.
- **emit-agents-md** — step 5 replaces the unexecutable "re-run Steps 1-4 / byte-identical" with a real structural self-check (no second write); dropped the `verbatim` vs link-rewrite contradiction; link rewriting explicitly covers `./` / `../`; "no markers" footer omission made intentional; background stats tagged as non-content.

### Added
- **`checklists/version-bump.md`** — flightdeck now dogfoods its own checklist convention for releases: the five manifests + CHANGELOG that must stay in sync, semver level guidance, and the tag/push step.

## [1.1.0] — 2026-05-30

### Added
- **Bundles** — a first-class concept for multi-file topics: a subfolder with a `README.md` contract (`bundle: true` + `reading_order` + routing frontmatter) plus detail leaves that inherit the README's routing and carry no routing fields of their own. One routing boundary per bundle (no nesting). See `skills/workflow/folder-semantics.md` and design `flightdeck/landed/specs/2026-05-30-bundles-and-routing-graph-design.md`.
- **Routing graph model** — folder-semantics now states flightdeck is graph-routed, not filesystem-routed: a file unreachable from any entry (cockpit / INDEX / manifest / bundle README) effectively does not exist. Custom folders/root files are allowed but must be reachable.
- **Folder-choice decision table** — sketches (idea) vs specs (design to implement) vs checklists (evergreen operational reference) vs charts (imported external material). `checklists/` re-described as authored operational reference; no `references/` folder.
- **Optional `skip_when` frontmatter** — negative routing ("when NOT to read this") for checklists / incident-reports / bundle READMEs.
- **Walkaround** — extended Audit 1 for bundle contracts (README required, leaves must not carry routing fields, `reading_order` match), plus new Audit 9 (orphan / unreachable files + INDEX prompt) and Audit 10 (stray files); 10 audits total.
- **preflight routing catalog** — `/flightdeck:preflight` now reads + parses the frontmatter of `checklists/` / `incident-reports/` flat files and bundle `README.md`s (recursively, excluding `landed/`) and prints a grouped catalog (`[Checklists]` / `[Incident reports]` / `[Bundles]` / `[Malformed bundles]`) with `when_to_read` + `applies_to` + `last_updated`, so routed triggers are in context at entry. Know-what-exists only (not read-all, not a `walkaround` substitute); leaves excluded; unparseable / missing-`when_to_read` / missing-`bundle:true` files surfaced with `⚠` markers rather than dropped. See `flightdeck/landed/specs/2026-05-30-preflight-routing-catalog-design.md`.

### Changed
- **`reading_order` is now a reachability edge** — folder-semantics, `SKILL.md`, and walkaround Audit 9 all treat a bundle README's `reading_order` entries as routing edges to its leaves. A leaf listed in `reading_order` is reachable even without a prose body link, so well-formed bundles no longer false-positive as orphans; a leaf *missing* from `reading_order` is an orphan. Resolves a contradiction between the bundle contract (leaf list in frontmatter) and the orphan audit (links-only reachability).
- **Always-loaded `SKILL.md` now carries the core routing semantics** — the folder-choice decision table, graph-routing/reachability rule, bundle contract, and optional `skip_when` field are summarized in `SKILL.md` (previously only in the on-demand `folder-semantics.md`). Ensures models that don't load the companion still obey the conventions, across all platforms (Claude/Codex/Cursor load `skills/workflow/` directly; `GEMINI.md` @-includes both files).

## [1.0.0] — 2026-05-28

**Project renamed from `workshop` to `flightdeck`.** Aviation framing for operational discipline, continuity, and reliability. Single breaking-change window — post-v1.0 is additive-only.

See [MIGRATION.md](MIGRATION.md) for upgrade steps. Design rationale: [flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md](flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md).

### Renamed

- **Project**: workshop → flightdeck (plugin name, marketplace identifier, repo URL, install commands)
- **Folders**: `plans/` → `flight-plans/`, `playbooks/` → `checklists/`, `scars/` → `incident-reports/`, `reference/` → `charts/`, `critiques/` → `safety-reviews/`, `wip/` → `kneeboard/`. `specs/` and `sketches/` retained (no aviation equivalent improves them).
- **Skill modules**: `workshop-workflow/` → `workflow/`, `session-enter/` → `preflight/`, `session-exit/` → `landing/`, `doctor/` → `walkaround/`. `emit-agents-md/` unchanged.
- **Slash commands**: `/workshop:workshop-workflow` → `/flightdeck:workflow`, `/workshop:session-enter` → `/flightdeck:preflight`, `/workshop:session-exit` → `/flightdeck:landing`, `/workshop:doctor` → `/flightdeck:walkaround`, `/workshop:emit-agents-md` → `/flightdeck:emit-agents-md`. (Main skill module renamed `flightdeck-workflow` → `workflow` to avoid the awkward `/flightdeck:flightdeck-workflow` slash form — clean reads as `/flightdeck:workflow`.)

### Decomposed

- **`board.md` split into three files** separated by read-time:
  - `cockpit.md` — must-read every session entry (Active focus, Next session, Hanging tasks). **80-line hard ceiling.**
  - `manifest.md` — on-demand (In flight artifacts, Blockers). No ceiling.
  - `logbook.md` — rarely read (Recently finished FIFO 5, Deferred). Append-mostly history.

### Restructured

- **`*/finish/` archive subdirs promoted to top-level `landed/` umbrella**. Now `landed/flight-plans/` and `landed/specs/`. Eliminates the "active folder shadowing its own archive" inelegance.

### Surfaced

- **Governing principle** lifted from rebrand spec into `workflow/SKILL.md` and `AGENTS.md`: **"Semantic clarity outranks thematic consistency."** The metaphor is a tool, not a theme. Resist metaphor lock-in on future concepts.

### Repository

- GitHub repo renamed `Yuelioi/workshop` → `Yuelioi/flightdeck`. Auto-redirect in place. Plugin marketplace identifier updated across all 4 platforms.
- VERSION: 0.8.1 → 1.0.0.

### Deferred to v1.1+

These were considered for v1.0 but punted to keep scope contained. Revisit when real usage demands each:

- `briefing/` (domain context / glossary)
- `blackbox/` (raw session-log persistence)
- `crew-handover/` (human ↔ human / cross-AI handoff)
- `experiments/` (long-running probes — already a `future expansion slot`)
- Automated migration skill (manual `MIGRATION.md` was sufficient for user base = 1)

## [0.8.1] — 2026-05-26

Patch release: README clarity + bootstrap UX + content cleanup. No protocol changes.

### Added

- **Bootstrap behavior in `workshop-workflow` skill**: when invoked in a project without `workshop/`, the skill now asks to create one, runs a short Active focus / Next session interview, and writes `workshop/board.md` directly. No more `install.sh --scaffold=minimal` round-trip required for Claude Code users.
- **Slash commands table** in README (EN + ZH) — all 5 commands listed with auto-load behavior and one-line purpose. Replaces the scattered "Force-invoke" + "Explicit slash commands (v0.5.0+)" sections.

### Changed

- **README "Day 1" section** simplified to `/workshop:workshop-workflow` flow. The clone + `install.sh` path remains documented as the fallback for non-Claude tools.
- **`workshop-workflow` skill** decoupled from `superpowers` plugin. Cross-references reframed as "Optional companions" — workshop is self-contained and accepts content from any source. Scenario triggers, exit-ritual heuristics, and folder-semantics no longer prescribe `superpowers:*` skills.
- **Trims**: SKILL.md dropped redundant prose Transitions table (Mermaid covers it), "Why semi-implicit" paragraph, "Backlog specs" edge case, "Proactive scar resurfacing" explanation. Common mistakes merged with Red flags. Net auto-load token cost down ~20%.
- **CHANGELOG** compressed: v0.3–v0.5 entries reduced to 1–2 lines each; "Known limitations" sections folded; per-commit citations dropped.
- **Archived plan** `workshop/plans/finish/2026-05-25-v0.6-cleanup.md` compressed from 789 → 39 lines (step-by-step Edit prescriptions removed; outcome summary retained).

### Fixed

- **README.md** had a duplicate `🇨🇳 中文用户` Chinese-link line inside the `## Install` section (original top-of-file placement + middle convenience link both rendered). Removed the duplicate.
- **`exit-ritual.md`** "Red flags" and "Common rationalizations" tables had significant overlap with `SKILL.md` Common mistakes; the two exit-ritual tables removed (one cross-link added instead).

## [0.8.0] — 2026-05-26

Lifecycle deepening. State-machine depth and protocol-drift surfacing — QoL polish landed before the v1.0 format freeze.

### Added

- **`/workshop:doctor` slash skill** (`skills/doctor/SKILL.md`) — audits a workshop for protocol drift across 8 categories: scars/playbooks frontmatter, stale wip, dangling internal references, orphan scars, board ↔ folder lifecycle mismatch, stale Blockers entries, Recently finished length, AGENTS.md regeneration drift. Severity: CRITICAL / WARNING / INFO. Never auto-fixes — surfaces drift; author decides.
- **OpenSpec-style spec evolution markers** (`ADDED:` / `MODIFIED:` / `REMOVED:`) — optional convention documented in `skills/workshop-workflow/templates.md` for long-lived backlog specs.
- **wip Pre-write checklist** in `skills/workshop-workflow/templates.md` — two-question hard gate before creating any new `wip/` file. Prose discipline, not programmatic enforcement.

### Changed

- **Scar promotion gate** is now multi-criterion: `[Case N] count ≥ 3` AND `≥ 2 distinct sessions` AND remediation pattern stable across cases. Two-stage path: first to `playbooks/`, then to project rules only if the playbook keeps getting ignored.
- **`Recently finished` auto-trim** is enforced, not advisory. `exit-ritual.md` wording tightened to "MUST enforce" / "not author-discretion".
- **session-exit Step 5** ("Check scar→playbook promotion gate (wrap-up)") added after the commit decision.

## [0.7.0] — 2026-05-26

Cross-tool reach. Workshop is portable beyond Claude Code — AGENTS.md emitter bridges to Codex CLI / Copilot / Cursor / Windsurf / Continue / Cody.

### Added

- **`/workshop:emit-agents-md` slash skill** (`skills/emit-agents-md/SKILL.md`) — regenerates `AGENTS.md` at repo root from `workshop/board.md` between fenced markers (`<!-- BEGIN: workshop -->` / `<!-- END: workshop -->`). Hand-authored content outside markers is preserved. Relative links from `board.md` get prefixed with `workshop/`.
- **`AGENTS.md` at repo root** — dogfood output of the emitter. Bridges to the cross-tool standard.
- **Optional Cursor MDC frontmatter fields** (`globs:` + `alwaysApply:`) on scar/playbook templates.
- **Capability × tool compatibility matrix** in `workshop/specs/2026-05-23-v1.0-release-gate.md`.
- **Community PR template** at `.github/PULL_REQUEST_TEMPLATE/manifest-verification.md`.
- **README "Why not just AGENTS.md?" section** (EN + ZH).

### Changed

- **`session-exit/SKILL.md`** gains step 5 (regenerate `AGENTS.md` if `board.md` changed); old Commit step becomes step 6.

### Known limitations

- Behavioral verification on Codex CLI / Cursor / Gemini CLI is out of scope; community PRs invited.
- `.codex-plugin/plugin.json` is functionally inert (Codex CLI has no plugin manifest format); workshop reaches Codex via emitted `AGENTS.md`.

## [0.6.0] — 2026-05-25

Internal consistency cut. No new user-facing features; deduplicates doctrine, hardens enforcement.

### Changed

- **De-duplicated `skills/session-exit/SKILL.md` against `exit-ritual.md`** — lifecycle table + (a)–(h) classification + `Last updated` triggers now live in one place; `session-exit/SKILL.md` is a thin entry-point.
- **Hard-fail on missing scars/playbooks frontmatter.** `when_to_read` + `applies_to` + `last_updated` are REQUIRED; workshop STOPs and reports missing fields instead of silent-skipping.
- **`wip/` TTL hard gate.** Wip files require `last_touched:` frontmatter; `session-enter` surfaces stale wip; `session-exit` BLOCKS until classified, deleted, or explicitly deferred with `defer_reason:`.

### Added

- **Mermaid lifecycle state diagram** in `skills/workshop-workflow/SKILL.md`.

### Migration from v0.5.x

- Add `when_to_read` + `applies_to` + `last_updated` to existing scars / playbooks (or delete the file). Otherwise v0.6+ STOPs and reports them.
- Add `last_touched:` to existing `wip/` files. Otherwise they count as stale and block session-exit.

## [0.5.0] — 2026-05-25

Two explicit slash-command skills exposing the workshop entry / exit rituals as one-command triggers: `/workshop:session-enter` (re-anchor mid-session) and `/workshop:session-exit` (clean wraps). Both `disable-model-invocation: true` — fire only on explicit slash.

## [0.4.0] — 2026-05-25

Dogfood refinements after 1 week of real use: `last_updated` frontmatter on scars/playbooks; proactive scar resurfacing when task overlaps with scar `applies_to` tags; per-review-point critique disposition tags; semi-implicit lifecycle (location = source of truth, frontmatter for divergent states); `Last updated` bump triggers pinned to 4 events.

## [0.3.0] — 2026-05-25

SessionStart hook auto-injects `workshop-workflow` when project has `workshop/`. Six-state lifecycle machine added. Board hygiene: 300-line hard ceiling, `Recently finished` capped at 5 (FIFO), per-entry summary ≤ 3 lines. Scars / playbooks require `when_to_read` + `applies_to` frontmatter.

## [0.2.0] — 2026-05-23

Multi-AI manifests: Claude Code plugin + self-hosted marketplace (tested); Codex CLI / Cursor / Gemini CLI manifests (untested). Chinese README mirror. Skill content made fully tool-neutral.

## [0.1.0] — 2026-05-23

Initial scaffold: `workshop-workflow` skill, adapters, scaffold templates, installers, RED-phase test plan.
