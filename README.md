# Flightdeck

Flightdeck is an AI-first Markdown work desk for long-running repository work. A fresh session can
recover one goal, its current truth, the next action, stable context, execution detail, and relevant
links without relying on prior chat.

The shipped product is Markdown plus host manifests. There is no server, CLI, database, schema,
generator, private checkpoint graph, or generated state.

## The model

```text
flightdeck/
  deck.md
  work/<work-id>/
    index.md
    context.md
    plan.md          # optional completion rollup
    slices/          # only durable detail expanded from Plan items
    references/      # optional Work-owned outputs
  knowledge/<subject>/<topic>.md
```

- `deck.md` contains one Open Work list, exactly one Focus marker when the list is non-empty, and a
  few stable project links. Focus is navigation, not lifecycle state.
- `index.md` is the recovery root and authority for Goal, Status, Current, Next, and the current
  execution pointer. Work is `Open`, `Finished`, or `Stopped`.
- `context.md` contains stable goal-specific facts, constraints, decisions, and terms.
- `plan.md` is optional. It owns ordered stage and Slice completion without duplicating Work state.
- A Slice holds a durable deliverable or decision whose detail must survive a fresh session or
  commit. Steps stay inside it; every Slice is linked from one Plan item.
- `knowledge/` is the demand-grown project operating playbook: current positive practices reusable
  across future Work.

Finished and Stopped Work stays at its stable path but leaves the deck's Open Work list.

## Natural-language operation

Tell the AI what you want in ordinary language: start durable work, continue a named or focused
goal, save before switching sessions, or finish or stop the Work. Flightdeck decides which visible
documents need maintenance.

Recovery reads the selected Work page and required context, an existing low-resolution Plan, at
most three local links embedded directly in Next, and live Git state. It also inspects Knowledge
subject/topic paths and reads only guidance relevant to the current action. Other Work, Slices,
References, and unrelated Knowledge remain lazy.

Save rewrites only documents whose recovery meaning materially changed. It never stages, commits,
pushes, tags, branches, or creates a private Git checkpoint.

## Complex and uncertain Work

Use a Plan only when the goal needs meaningful stages or acceptance checks. Add a Slice only when a
Plan item needs its own durable Current and Next.

When the Goal is clear but the route is not, an optional Wayfinding phase resolves one linked
Decision Slice at a time. `Not yet specified` may hold uncertainty that cannot yet be formulated;
Delivery Slices remain separate so deciding an implementation never counts as delivering it.

## Specialist outputs

Flightdeck routes supported Work-scoped domain context, decisions, research, specifications,
reviews, and execution breakdown into the owning Work. Source changes, external-system records,
temporary files, and unsupported outputs stay at their authoritative location and are linked.

Project-wide vocabulary remains in root `CONTEXT.md`; architectural decisions remain in
`docs/adr/`. Handoff is an ordinary Flightdeck save, not another document protocol.

## Knowledge

Knowledge is the demand-grown project operating playbook, with one independently applicable
positive practice per organic subject path such as `flightdeck/knowledge/ui/form-errors.md`. It is
neither broad project memory nor an enforceable rule store.

Before executing a new or recovered action, Work proactively checks for relevant Knowledge without
waiting for the user to name the library. It reads relevant existing Work links first, then inspects
subject/topic paths and searches headings only within plausible subjects before reading matching
guidance. Path inspection is routine, but unrelated bodies remain lazy. Guidance advises judgment;
ordinary consultation is not logged, and a link persists only when a fresh session still needs it.
Promote only verified, plausibly reusable, self-contained conclusions. Rewrite or remove disproven
guidance, leaving unresolved research in Work. Do not add a required taxonomy, index, kind,
activation or routing field, revision, history, stale flag, recheck ledger, or trap collection.

## Operating boundary

Flightdeck assumes one top-level AI session operates a repository at a time. That session may
coordinate child agents but consolidates their results into the authoritative Work documents.
Flightdeck provides no cross-session locks, claims, or compatibility protocol.

## Local plugin use

The self-contained package under `plugins/flightdeck` serves Codex and Claude from one shared skill
tree. In this repository's Codex marketplace:

```text
codex plugin add flightdeck@flightdeck-local
```

For direct Claude Code development loading:

```text
claude --plugin-dir plugins/flightdeck
```

## Documentation

- [Format and writing guide](docs/format.md)
- [Upgrade an older or divergent workspace](docs/upgrade.md)
- [Complete example deck](examples/deck/README.md)
- [Architecture decisions](docs/adr/)
- [Contributing](.github/CONTRIBUTING.md) and [security](.github/SECURITY.md)
- [中文说明](README.zh.md)

Flightdeck is MIT licensed.
