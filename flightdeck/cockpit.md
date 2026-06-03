# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (2.3.0 dogfooded end-to-end on a throwaway full-auto scratch deck — status auto-flip, observable `last_updated` bump, `commit_mode: auto`, and the collect-then-migrate co-land of a mutual spec↔plan cluster all verified; filed 3 follow-up findings: 1 incident + 2 sketches)
**Active focus**: flightdeck 2.3.0 shipped and now dogfood-verified (migration + full-auto feature surface both pass); remaining work is triaging the 3 dogfood findings and the deferred-folder backlog.

## Next session

1. Triage the 3 dogfood findings — fix the INDEX-row `—` delimiter collision ([incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)); decide whether [sketches/preflight-upgrade-nudge.md](sketches/preflight-upgrade-nudge.md) and [sketches/status-spec-lags-plan.md](sketches/status-spec-lags-plan.md) promote to specs or defer.
2. Reassess deferred folders — see [sketches/v1x-deferred-ideas.md](sketches/v1x-deferred-ideas.md).

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
