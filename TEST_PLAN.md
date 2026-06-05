# Test plan (moved)

Moved to [`flightdeck/archive/specs/2026-05-23-v1.0-release-gate.md`](flightdeck/archive/specs/2026-05-23-v1.0-release-gate.md) on 2026-05-25 — the flightdeck project now dogfoods its own `flightdeck/`.

This stub remains so links from `README.md` / `README.zh.md` / `CHANGELOG.md` still resolve. Edit the spec, not this file.

## 1.2 test points

- **status frontmatter**: every artifact carries a valid `status`; `walkaround` flags a missing one (CRITICAL) and an out-of-range value (WARNING).
- **INDEX consistency**: each folder's `INDEX.md` (plus root `flightdeck/INDEX.md`) matches the files on disk; `landing` regenerates only the changed folders' INDEX.
- **Migration**: a synthetic 1.1.x layout (`manifest.md` / `logbook.md` / `kneeboard/` / `flight-plans/` / `incident-reports/` / `safety-reviews/`) triggers the 1.1.x→1.2 detection in `preflight`/`walkaround`; an idempotent re-run skips already-migrated artifacts.
- **walkaround**: the 10 audits surface illegal status, INDEX↔folder drift, missing `superseded_by`, orphan plan (INFO), and legacy 1.x paths.
- **rules.md**: `git: false` makes `landing` skip the commit step and append `landed/HISTORY.md`; `disabled_folders` suppresses orphan flags; `disabled_gates` skips the `debrief-disposition` gate.
- **emit-agents-md**: renders Current focus / Next session / Hanging tasks from `cockpit.md`.

## 2.0 test points

- **Single entry**: `/flightdeck:preflight` is the only entry skill; there is no `workflow` skill and no startup hook (nothing loads on session start).
- **Branch-0 init-or-read**: in a directory with no `flightdeck/cockpit.md`, `/flightdeck:preflight` runs the First-time-setup interview and writes `cockpit.md` (with `**Layout**: 1.2`), then stops. With a `cockpit.md` present, it takes the read path (layout check → reconcile → catalog → report).
- **Existence before layout**: the deck-existence check runs before the layout-version check (no attempt to read a `**Layout**` line when there is no cockpit).
- **Companion paths**: `landing` / `walkaround` / `emit-agents-md` resolve their companion links under `skills/preflight/` (the old companion location is gone, no stale links remain).

## 2.1 test points

- **`model_invocable` soft gate**: the four entry skills no longer carry `disable-model-invocation`; self-invocation is allowed only when `rules.md` `model_invocable` lists the ritual. Default (`[]`) = manual-only, identical to before; an explicit user slash is always allowed.
- **`status` ritual**: `/flightdeck:status` flips one artifact's `status:` + its INDEX row (forward-only; never touches `cockpit.md` or commits). `status_auto: [start, land]` controls the *optional* `start`/`land` transitions; core `create→pending` / `finish→awaiting-review` stay automatic.
- **Shared Land Routine**: `landing` and `status` both call the single `## Land Routine` in `exit-ritual.md` — no reimplementation in either.
- **Done-but-unlanded**: declining the `status land` confirm leaves the artifact `done` but un-archived; `preflight` / `landing` surface it and offer to land later (never reverts `done`).

## 2.2 test points

- **`rules.md` mandatory + version**: `rules.md` is part of the minimal 3-file contract (`rules.md` + `cockpit.md` + `landed/HISTORY.md`) and carries `version:`. The `**Layout**` cockpit line is gone — `preflight` / `walkaround` read the version from `rules.md` and compare against `MIGRATION.md` (`current` + `layout_need_update`) for migration detection.
- **2.1→2.2 migration**: a deck with no `rules.md` `version` (or `< 2.2`) triggers a non-silent migration offer; the migration is idempotent (each step skips if already done).
- **Workflow frontmatter enrichment**: sketches/specs/plans gain recommended `summary` + `last_updated` and optional `supersedes` / `related`. INDEX rows derive purely from `summary`; `last_updated` auto-bumps on substantive change; reverse edges are grep-derived (no persisted `superseded_by`).
- **Land Routine collect-then-migrate**: landing a set builds the full old→`landed/` remap *before* moving, then rewrites `implements` / `supersedes` / `related` across the active tree **and** the moved set — so intra-set mutual references survive archival (no dangling edges after a co-landed cluster).
- **walkaround Audits 11–12**: aggregated INFO for missing workflow `summary` / `last_updated`; dangling `supersedes` / `related` edge detection (an edge into `landed/` is normal, not flagged).
