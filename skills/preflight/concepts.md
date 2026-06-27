# flightdeck — concepts

Load on demand: the definitions behind [SKILL.md](SKILL.md). This file says what each
thing *is*; how to operate on them is [operations.md](operations.md).

## The layout

```
<project>/flightdeck/   warm tier — git-tracked, committed each turn
  cockpit.md   project index: Focus + ## In flight + ## Next + ## Open questions
  briefing.md  stable, human-owned — ## Conventions + ## Subscriptions
  work/        active topic packages, one folder per topic
  knowledge/   routed future-behavior knowledge, nested by domain

~/.flightdeck/   cold tier — a plain global dir, NOT git (the global / "mother" store)
  knowledge/     cross-project knowledge, domain-routed like project knowledge
  projects/<slug>/  one project's cold store: archive/<topic>/ + ideas/<topic>/
                    <slug> = project abs path, separators / \ : → -  (collision-proof)
```

## cockpit.md — the project index

The volatile "where do I go next" file: rewritten every turn, kept small. It is an
index, not the place for topic detail. The bar is that someone could close the
conversation right now, run preflight, and know which `work/<topic>/context.md` to read
without reading git. Canonical skeleton — `Focus:` (usually a `work/<topic>/` path) +
`## In flight` (active topic packages) + `## Next` (next concrete action or topic
context pointer) + `## Open questions` (only blocked / waiting / undecided questions
that cross topics or belong at project level). Those four are the minimum; extra
sections are fine when they stay index-like. A light convention, not a YAML schema — no
status field, no `Updated:` line (git knows when/who).

## briefing.md — the stable rules

Human-owned, read first on entry. Two sections, no frontmatter:

- `## Conventions` — this deck's house rules + AI-maintenance preferences, in plain prose.
- `## Subscriptions` — one `~/.flightdeck`-relative path per line; what this deck pulls in
  from the global tier (empty = standalone).

Stable across turns. persist never rewrites it — only the AI maintaining a rule on your
request, or you, edits it.

## topic work package — context, design, plan, progress

An active effort in `work/` is always a **topic package** — one folder per topic, with
stable entry files:

```text
work/<topic>/
  context.md    topic recovery payload: state, next, blockers, key facts
  design.md     why + approach + tradeoffs
  plan.md       current main execution plan
  progress.md   compressed progress summary, not a step log
  plans/        optional alternate, superseded, or branch plans
  notes.md      optional scratch; clear or fold before archiving
```

`context.md` is the first file preflight reads after cockpit for the active topic. It must
be short enough to restore the thread quickly, and concrete enough to continue without the
old chat. `design.md` is the decision surface. `plan.md` is the single current mainline;
additional plans live under `plans/` and are named for their purpose. `progress.md` is a
rolling summary of done/current/verified/not-done, not a chronological transcript.

Do not create top-level `work/<topic>.md` efforts, split sibling plan/spec files, or side
`docs/` working trees for active effort artifacts. Effort package files are reached from
cockpit and preflight, not routed through knowledge — so they carry **no routing header**.

## knowledge — the three kinds + the routing header

Persistent, routed-on-relevance, nested by domain (`knowledge/git/commit-style.md`,
`knowledge/storage/sqlite/wal-mode.md` — as deep as the domain needs). Every file opens
with a **routing header** ended by a `---`; routing reads only the header (cheap), so it
must stand on its own:

    # <title>

    SUMMARY: <one line — what this is>
    READ WHEN: <when a session should route here>
    RECHECK WHEN: <optional — what it tracks; re-verify when that changes>

    ---

    <free-form body>

The title line picks the kind:

- `# <title>` — a decision / reference note
- `# ⚠ <title>` — a trap (a pitfall to avoid hitting again)
- `# <X> checklist` — repeatable steps

Leave a blank line **before** the `---` (and after the title), or the last header line and
the `---` parse together as a setext heading and the terminator vanishes on render.
Knowledge is *resident*: present = valid, deleted = dead. No lifecycle, no status. Place
knowledge under a domain folder (`knowledge/<domain>/...`); avoid root-level piles as the
library grows.

## warm vs cold — the two tiers

- **warm** = the project's `flightdeck/` — git-tracked, committed each turn, inside the
  zero-loss guarantee. cockpit + briefing + work topic packages + knowledge live here.
- **cold** = `~/.flightdeck`, the plain global "mother" store — NOT git, outside the
  guarantee. It holds two things: cross-project `knowledge/` (genuinely universal, opted
  into via a briefing `## Subscriptions` line), and `projects/<slug>/` with
  `archive/<topic>/` (completed topic packages moved out of `work/`) + `ideas/<topic>/`
  (unstarted seeds, out of the project view).

**Location is state.** There is no status field; a thing's tier and folder say whether it's
active (`work/`), done (cold `archive/<topic>/`), or parked (cold `ideas/<topic>/`).

## cold project store — archive and ideas

Cold project storage is deliberately outside the zero-loss guarantee and outside normal
preflight loading. It is kept for recovery-by-choice, not session continuity.

- `~/.flightdeck/projects/<slug>/archive/<topic>/` holds a completed topic package moved
  out of `work/<topic>/`. Preserve its shape (`context.md`, `design.md`, `plan.md`,
  `progress.md`, optional `plans/` / notes) so later archaeology has the whole effort
  together. Before moving, compress `progress.md` enough that the archive explains what
  finished and what was verified.
- `~/.flightdeck/projects/<slug>/ideas/<topic>/` holds an unstarted topic seed. Keep it
  light: usually `idea.md` (problem / why it matters / activation trigger / rough notes).
  Do not create a full `context.md` / `plan.md` until the idea is promoted into active
  `work/<topic>/`; otherwise parked ideas look like live recovery payloads.
- To start an idea, move or copy it into `work/<topic>/`, then create the active package
  entry files (`context.md`, `design.md`, `plan.md`, `progress.md`) from the seed. Location
  changes the state; no status field is added.

## global knowledge

Global knowledge under `~/.flightdeck/knowledge/` follows the same routing-header and
domain-folder rules as project knowledge. It is for genuinely cross-project behavior:
commit conventions, command-running rules, reusable tool procedures, framework traps that
apply beyond one repo.

Prefer `~/.flightdeck/knowledge/<domain>/...` and subscribe to either a domain directory or
a specific file from `briefing.md`. Legacy root-level global files may still be subscribed
for compatibility, but new global knowledge should not grow a root pile.
