<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 2.1 shipped — `model_invocable` soft gate (rules.md) replaced the `disable-model-invocation` hard switch; new 5th ritual `flightdeck:status` (lifecycle auto-flip via `status_auto`). Layout still 1.2.

## Next session

1. Spec the version→`rules.md` relocation: drop cockpit's `Layout` line, make `rules.md` mandatory (3-file minimal contract: rules + cockpit + HISTORY), add `version`; MIGRATION.md carries `current` + `layout_need_update` to drive migration detection. Supersedes the `layout-version-migration-detection` design; revises soft-config's "rules.md optional" stance.
2. Dogfood v2.1 on real projects — exercise `flightdeck:status` auto-flip + `model_invocable` opt-in; classify friction at landing.
3. Reassess deferred folders — see [sketches/v1x-deferred-ideas.md](flightdeck/sketches/v1x-deferred-ideas.md).

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
