# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-02 by 月离 (v2.1.0 shipped — model_invocable soft gate + flightdeck:status ritual; soft-config & status-lifecycle artifacts landed)
**Active focus**: flightdeck 2.1 shipped — `model_invocable` soft gate (rules.md) replaced the `disable-model-invocation` hard switch; new 5th ritual `flightdeck:status` (lifecycle auto-flip via `status_auto`). Layout still 1.2.
**Layout**: 1.2

## Next session

1. Implement two pending designs in one `templates.md`/walkaround pass (both touch the same files): [version→rules.md relocation](specs/2026-06-02-version-in-rules-migration-detection-design.md) (drop `Layout` line, mandatory rules.md, 3-file contract, MIGRATION.md-driven detection) + [workflow-artifact frontmatter enrichment](specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md) (`summary` derives INDEX row, `last_updated`, `supersedes`/`related` edges). Open a plan each.
2. Dogfood v2.1 on real projects — exercise `flightdeck:status` auto-flip + `model_invocable` opt-in; classify friction at landing.
3. Reassess deferred folders — see [sketches/v1x-deferred-ideas.md](sketches/v1x-deferred-ideas.md).

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
