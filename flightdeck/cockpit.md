# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-02 by 月离 (v2.1.0 shipped — model_invocable soft gate + flightdeck:status ritual; soft-config & status-lifecycle artifacts landed)
**Active focus**: flightdeck 2.1 shipped — `model_invocable` soft gate (rules.md) replaced the `disable-model-invocation` hard switch; new 5th ritual `flightdeck:status` (lifecycle auto-flip via `status_auto`). Layout still 1.2.
**Layout**: 1.2

## Next session

1. Execute [plans/2026-06-02-metadata-model-implementation-plan.md](plans/2026-06-02-metadata-model-implementation-plan.md) (implements the 3 stacked specs). Phase 0 stand up the canonical field table in protocol.md → Phase 1 version→rules.md + migration detection → Phase 2 workflow frontmatter enrichment → Phase 3 dogfood backfill + release. Order is a hard dependency. Use subagent-driven-development / executing-plans.
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
