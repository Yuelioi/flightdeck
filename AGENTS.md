<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 2.2.0 shipped — single canonical frontmatter field table; deck `version` now in the mandatory `rules.md` (3-file contract); workflow artifacts gain `summary`/`last_updated`/`supersedes`/`related` (INDEX rows derive from `summary`).

## Next session

1. Dogfood v2.2 on a real existing deck — run the 2.1→2.2 migration (add `rules.md` `version`, drop the cockpit `Layout` line) and exercise `summary`/`last_updated` auto-bump; classify friction at landing.
2. Reassess deferred folders — see [sketches/v1x-deferred-ideas.md](flightdeck/sketches/v1x-deferred-ideas.md).
3. **Cut 2.2.1** to publish the Land Routine collect-then-migrate fix (run [checklists/version-bump.md](flightdeck/checklists/version-bump.md)): bump `rules.md` / `MIGRATION.md` `current`, marketplace, tag. Skill-behavior change only — **no** deck migration (`layout_need_update` untouched).

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
