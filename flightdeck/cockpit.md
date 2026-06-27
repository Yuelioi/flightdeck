# Cockpit — flightdeck (the flightdeck project itself)

Focus: work/ai-native-redesign/ — AI-native cutover, now past the `index.md` handoff migration and carrying local knowledge cleanup plus cache sync follow-up.

## In flight

- work/ai-native-redesign/ — current reset effort. Choose this topic, then read `index.md`; it points at the current stale-knowledge cleanup and cache sync step.

## Next

Verify and commit the stale-knowledge cleanup, then sync both Claude and Codex plugin caches. Release steps (CHANGELOG, version bump, push) remain gated by explicit user approval.

## Open questions

- Release version remains undecided; current package version is `3.0.0-alpha.5`.
- `git push` remains explicitly gated by user approval.

## House pointers

Rules → briefing.md · preferences → project agent instructions · active topic → work/ai-native-redesign/index.md · knowledge → knowledge/<domain>/ · cold archive/ideas → ~/.flightdeck

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. Users running flightdeck in their own projects see their own deck, not this one.
