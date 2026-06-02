<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 2.2.0 shipped — single canonical frontmatter field table; deck `version` now in the mandatory `rules.md` (3-file contract); workflow artifacts gain `summary`/`last_updated`/`supersedes`/`related` (INDEX rows derive from `summary`).

## Next session

1. Dogfood v2.2 on a real existing deck — run the 2.1→2.2 migration (add `rules.md` `version`, drop the cockpit `Layout` line) and exercise `summary`/`last_updated` auto-bump; classify friction at landing.
2. Reassess deferred folders — see [sketches/v1x-deferred-ideas.md](flightdeck/sketches/v1x-deferred-ideas.md).
3. **Land Routine gap** (surfaced this land): step 3 rewrites only *inbound* edges from the active tree, so co-landing a mutual-reference cluster leaves intra-batch edges dangling — I hand-fixed them this time. Decide: tighten the routine (also rewrite the landed file's own outbound edges to siblings) vs. leave to walkaround's dangling-edge audit.

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
