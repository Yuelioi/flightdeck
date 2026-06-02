# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (Land Routine rewritten to collect-then-migrate — builds a full land-set remap before moving, then rewrites `implements`/`supersedes`/`related` across active tree + moved set; fixes the co-land mutual-cluster gap hit while landing the 2.2.0 metadata-model artifacts)
**Active focus**: flightdeck 2.2.0 shipped — single canonical frontmatter field table; deck `version` now in the mandatory `rules.md` (3-file contract); workflow artifacts gain `summary`/`last_updated`/`supersedes`/`related` (INDEX rows derive from `summary`).

## Next session

1. Dogfood v2.2 on a real existing deck — run the 2.1→2.2 migration (add `rules.md` `version`, drop the cockpit `Layout` line) and exercise `summary`/`last_updated` auto-bump; classify friction at landing.
2. Reassess deferred folders — see [sketches/v1x-deferred-ideas.md](sketches/v1x-deferred-ideas.md).
3. **Cut 2.2.1** to publish the Land Routine collect-then-migrate fix (run [checklists/version-bump.md](checklists/version-bump.md)): bump `rules.md` / `MIGRATION.md` `current`, marketplace, tag. Skill-behavior change only — **no** deck migration (`layout_need_update` untouched).

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.

---

**Cockpit hygiene** (skill: workflow):
- **80 lines hard ceiling.** Cockpit is operational, not archival. History lives in `git log` / `landed/HISTORY.md`.
- `Last updated` bumps ONLY when: Next session changes / Active focus shifts / a major task completes / an artifact lands.
- Finished items leave `Next session`; they are not logged in cockpit.
- Artifact state is tracked via `status:` frontmatter + the folder `INDEX.md` files, not here.
