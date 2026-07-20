---
name: flightdeck
description: Keep long-running repository work understandable and resumable across fresh AI sessions with a small Markdown work desk. Use when the user asks to start durable work, continue or recover prior work, save progress, finish work, list resumable work, or maintain project knowledge for future sessions. Do not use for ordinary short tasks that do not need a durable handoff.
---

# Flightdeck

Use ordinary Markdown as the source of truth. Read and edit it with the host's normal file and Git
tools. Do not create hidden state, private checkpoints, receipts, revision records, or a parallel
workflow graph.

## Route the request

Read the matching reference completely before acting:

- New durable work: [start.md](references/start.md)
- Continue, recover, or list work: [continue.md](references/continue.md)
- Save progress or hand off the current session: [save.md](references/save.md)
- Finish or stop work: [finish.md](references/finish.md)
- Route a specialist output: [route-output.md](references/route-output.md)
- Explore a clear Goal whose route is uncertain: [wayfinding.md](references/wayfinding.md)
- Upgrade an older or divergent workspace: [upgrade.md](references/upgrade.md)

After starting or continuing a Work, apply the save guidance whenever the session reaches a durable
milestone or is about to end. Do not interrupt useful work merely to perform ceremony.

## Repository model

```text
flightdeck/
  deck.md
  work/<work-id>/
    index.md
    context.md
    plan.md          # optional ordered completion rollup
    slices/          # only durable detail expanded from Plan items
    references/      # optional outputs owned by this Work
  knowledge/<subject>/<topic>.md
```

`index.md` is the compact recovery root and authority for Goal, lifecycle Status, Current, Next, and
the current execution pointer. `context.md` holds stable goal-specific meaning. An optional
`plan.md` owns ordered stage and Slice completion; every Slice expands one linked Plan item and owns
only its local execution detail.

Keep `deck.md` tiny: one Open Work list, exactly one Focus marker when any Work is Open, and a few
stable project links at most. Focus is navigation, not Work status. A repository-wide `CONTEXT.md`
remains at the root when another convention owns it.

## Boundaries

- Write at most three local links required for the immediate action directly into Next. Recovery
  already reads the Work page, required context, and existing Plan; keep all other links lazy under
  References. Do not create a separate `Read now` routing section.
- A Slice is a deliverable and verifiable unit whose detail must survive a fresh session or commit.
  Keep Steps inside a Slice and create another Work only when a subgoal has independent Goal,
  Context, Current, and Next. Do not create maps, blocker registries, ticket mirrors, or a second
  completion rollup beside the Plan.
- Use [route-output.md](references/route-output.md) for specialist work. Supported Work-scoped
  documents belong to their owning Work; source changes, external-system records, and unsupported
  outputs stay at their natural location and are linked.
- Write Knowledge as concise, positive guidance organized by subject. Use headings, examples, and
  source links when useful. Do not add routing fields, kinds, revisions, histories, traps, or
  recheck metadata.
- Keep failed attempts in Work progress while relevant. Promote only reusable conclusions into
  Knowledge; put enforceable rules in tests or validators.
- Treat one top-level AI session as the repository's Flightdeck operator. It may coordinate child
  agents but must consolidate their results into the authoritative Work documents. Do not add
  cross-session locks, claims, or merge protocols.
- Treat Git as the repository's history. Do not commit, push, tag, or publish unless the user asks
  or the repository's explicit workflow requires it.

Prefer repairing clear omissions in these human documents over rejecting them for schema errors.
When reality and the handoff disagree, inspect the repository, explain the drift, and update the
visible documents at the next authorized save.
