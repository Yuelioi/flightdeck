# Start work

Use this branch when the user wants repository work to survive future sessions.

1. Create durable Work when the user asks, the goal is likely to cross sessions or meaningful
   commits, a specialist document or independent context is needed, or rediscovery would be costly.
   Do not create Work for an ordinary short task.
2. Inspect the repository, `flightdeck/deck.md`, and existing `flightdeck/work/*/index.md` files.
   Reuse a matching Open Work instead of creating a duplicate.
3. Choose a short stable `work-id`. Create `flightdeck/`, `deck.md`, and the Work directory when
   absent. Ensure root `AGENTS.md` has one short provider-neutral instruction directing durable work
   through Flightdeck; preserve unrelated repository instructions.
4. Create `index.md` with Status `Open` and a real `context.md`. Write present project truth, not
   instructions to a future agent.
5. Add `plan.md` only for meaningful stages, acceptance checks, or uncertainty that a flat Next
   would lose. Create a Slice only when a linked Plan item needs durable local execution detail.
   If the Goal is clear but the route is not, read [wayfinding.md](wayfinding.md).
6. Add the Work to the deck's one Open Work list and mark it as the sole Focus. Preserve other Open
   Work and useful project links.
7. Write one executable Next action with at most three local links required to perform it. Other
   supporting material belongs under References and stays lazy.
8. Perform the main skill's bounded Knowledge check for the first action.
9. Report the Work's Goal and first Next, then begin the requested work.

The first Next action must be executable. Initial context should contain only facts, constraints,
terms, and decisions that a fresh session would otherwise have to rediscover.

Starting Work authorizes these repository-local Markdown changes. It does not authorize commits,
publication, remote writes, or relocating another skill's output.
