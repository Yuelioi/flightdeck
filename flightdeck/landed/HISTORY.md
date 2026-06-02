# History — flightdeck

<!-- Add-only landing log, newest first. One line per landing. Never edit or delete past entries.
     Required when rules.md sets git: false; optional otherwise. Never read at session start. -->

- 2026-06-02 — v2.1.0 shipped: `model_invocable` soft gate (rules.md) replaced the four rituals' `disable-model-invocation` hard switch; new 5th ritual `flightdeck:status` (lifecycle auto-flip, `status_auto` toggle, shared Land Routine). Additive / opt-in — Layout stays 1.2. soft-config + status-lifecycle spec & plan landed. next: spec the version→rules.md relocation + 3-file minimal contract + MIGRATION.md-driven migration detection (supersedes layout-version-migration-detection).
- 2026-06-02 — v2.0.0 shipped: single explicit `/flightdeck:preflight` entry (init-or-read); deleted the `workflow` skill + the SessionStart hook (manual-only, no auto-load); protocol folded into `skills/preflight/` (`protocol.md` + relocated companions); unified empty-`Next session` fallback. Layout unchanged (1.2) — user decks need no migration.
- 2026-06-02 — v1.3.0 landed: layout-version stamp + version-driven migration detection (`preflight`/`walkaround` compare cockpit's `**Layout**` line against the current layout version; legacy-marker check frozen as unstamped-deck fallback; never migrates silently). Layout schema stays 1.2 (no folder renames). Dogfooded several days; spec + plan archived.
- 2026-06-01 — migrated own `flightdeck/` to the 2.0 work-items layout (specs/+flight-plans/ → landed/work-items/; safe-reviews → landed/safety-reviews/; cockpit + AGENTS regenerated to 2.0); 2.0 ready to ship.
- 2026-06-01 — v2.0 built on branch `v2-entry-collapse-and-rules`: entry-layer collapse (single cockpit), `rules.md` customization, `## Plans` ledger, kneeboard removed, `landed/` generalized, `landed/HISTORY.md` added; next: review + release.
- 2026-05-28 — v1.0.0: flightdeck rebrand + board.md decomposition (cockpit/manifest/logbook), `*/finish/` → `landed/` umbrella, skill modules renamed.
- 2026-05-26 — v0.8.0: lifecycle deepening — doctor audit skill, scar→playbook promotion gate, wip pre-write checklist, OpenSpec delta markers, Recently-finished auto-trim (commit `325dcf1`).
- 2026-05-26 — v0.7.0: cross-tool reach — emit-agents-md skill + AGENTS.md dogfood, Cursor MDC fields, manifest schema verification, capability×tool matrix (commit `23685f7`).
- 2026-05-25 — v0.6.0: cleanup cut — SKILL.md de-dup, frontmatter hard-fail, Mermaid lifecycle diagram, wip TTL gate (commit `e9e0c85`).
- 2026-05-25 — v0.5.0: explicit session-enter / session-exit slash skills (commit `e926dec`).
