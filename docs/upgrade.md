# Upgrade a Flightdeck workspace

Flightdeck alpha.7 uses AI judgment instead of a version compatibility contract. There is no format
detector, schema, migration script, or guaranteed rename path for older pre-release workspaces.

## Inspect meaning before structure

Read the actual Deck, Work pages, context, plans, Slice-like documents, References, Knowledge,
repository instructions, and live Git state. Identify by meaning:

- independently focusable unresolved goals;
- lifecycle truth, Current, and executable Next;
- stable goal-specific context;
- ordered completion and durable local execution detail;
- useful supporting outputs and reusable guidance.

Do not infer truth from a claimed version or filename alone. Preserve ambiguous material and ask
before an irreversible choice.

## Reshape active recovery

For each genuinely durable goal, create or repair `flightdeck/work/<id>/index.md` and `context.md`.
Use `Open`, `Finished`, or `Stopped`; keep Focus only in the Deck's Open Work list. Embed at most
three immediate local links in Next instead of creating `Read now` metadata.

For complex Work, make `plan.md` the ordered completion rollup. Keep a Slice only when a linked Plan
item needs durable Outcome, Current, and Next. Remove duplicate maps, blocker registries, status
fields, artifact catalogs, receipts, revisions, and other competing authorities only after their
current value is represented.

## Route durable material

Move supported Work-scoped research, specifications, reviews, and decisions into the owning Work
when their output path is selectable. Keep source, external-system, temporary, and unsupported
outputs at their natural location and link them. Keep project-wide vocabulary in root `CONTEXT.md`,
ADRs in `docs/adr/`, and reusable positive guidance in `flightdeck/knowledge/`.

## Prove recovery

Open a fresh session and ask it to continue the focused Work. Confirm that it selects the right
Work, reads its page and context, understands the Plan rollup, follows only the links required by
Next, checks live Git state, and can take the next action without loading unrelated history.

Upgrade does not automatically stage, commit, push, tag, publish, rewrite Git history, or add a
compatibility runtime. Use normal repository backup policy before authorized destructive cleanup.
