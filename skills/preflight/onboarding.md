# Flightdeck onboarding — 2-minute guided tour

A **demonstration** run: the AI creates a throwaway sample artifact, walks it through the full
lifecycle narrating each step, then deletes it. The user just reads and says "next". Skippable;
invoked only from `preflight` first-time setup (step 6). **Idempotent** — safe to re-run; it
detects and cleans any leftover sample first.

The ONLY file this tour creates / edits / deletes is `hello-flightdeck.md` (+ its landed copy +
its INDEX rows). Never touch the user's real artifacts. Do not commit. Do not bump cockpit `Last updated`.

## Step 0 — clean any leftover sample

If `specs/hello-flightdeck.md` OR `landed/specs/hello-flightdeck.md` exists (a prior interrupted
tour), delete them and remove any `hello-flightdeck` row from `specs/INDEX.md` / `landed/`'s index,
recompute the root `INDEX.md` counts — then continue.

## Step 1 — create the sample (status: create → pending)

Write `flightdeck/specs/hello-flightdeck.md`:

```markdown
---
status: pending
summary: throwaway onboarding sample, safe to delete
last_updated: <today>
---
<!-- tutorial sample — safe to delete -->

# Hello, flightdeck

This file is a guided-tour sample. The tour moves it through the lifecycle, then deletes it.
```

Regenerate `specs/INDEX.md` `<!-- AUTO -->` + the root `INDEX.md` count.
**Narrate:** "Created a spec → `status` set it `pending`; a row appeared in `specs/INDEX.md`." → wait for **next**.

## Step 2 — start (pending → active)

Flip frontmatter `status: active`, bump `last_updated`, re-sync `specs/INDEX.md`.
**Narrate:** "Beginning execution → `status` flips it `active` (the default-on `start` transition)." → **next**.

## Step 3 — finish (active → awaiting-review)

Add one line to the body, flip `status: awaiting-review`, re-sync `specs/INDEX.md`.
**Narrate:** "Work done → `awaiting-review` — the signal it's ready to land." → **next**.

## Step 4 — approve + land (awaiting-review → done → archived)

Flip `status: done`; then run the shared **[Land Routine](exit-ritual.md#land-routine)**: move
`specs/hello-flightdeck.md` → `landed/specs/`, remove its `specs/INDEX.md` row, recompute root counts.
**Narrate:** "Approved → `done`, then **landed**: the file moved to `landed/specs/` — out of the active
tree but kept as history." → **next**.

## Step 5 — cleanup (restore a pristine deck)

Delete `landed/specs/hello-flightdeck.md`; ensure no `hello-flightdeck` row remains in any `INDEX.md`;
recompute root counts.
**Narrate:** "Tour done — sample removed; your deck is the empty full layout, ready for real work.
Run `/flightdeck:preflight` next session to resume."

## Don't do

- Don't touch the user's real artifacts — only `hello-flightdeck.md` (+ its landed copy + INDEX rows).
- Don't commit; don't bump cockpit `Last updated`; don't regenerate `AGENTS.md`.
- If the user says "skip"/"stop" mid-tour, run Step 5 cleanup (or Step 0 on next run) so nothing is left behind.
