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
index / chooser screen, not the place for topic detail. The bar is that someone could
close the conversation right now, run preflight, see the resumable `work/<topic>/`
choices, and choose one without reading git or any topic file. Canonical skeleton —
`Focus:` (usually a `work/<topic>/` path or project-wide focus) + `## In flight` (active
topic packages, each with a one-line next) + `## Next` (the project-level next choice) +
`## Open questions` (only blocked / waiting / undecided questions that cross topics or
belong at project level). Those four are the minimum; extra sections are fine when they
stay index-like. A light convention, not a YAML schema — no status field, no `Updated:`
line (git knows when/who).

## briefing.md — the stable rules

Human-owned, read first on entry. Two sections, no frontmatter:

- `## Conventions` — this deck's house rules + AI-maintenance preferences, in plain prose.
- `## Subscriptions` — one `~/.flightdeck`-relative path per line; what this deck pulls in
  from the global tier (empty = standalone).

Stable across turns. persist never rewrites it — only the AI maintaining a rule on your
request, or you, edits it.

## topic work package — index first, long files on demand

An active effort in `work/` is always a **topic package** — one folder per topic, with
one stable entry file and optional supporting files:

```text
work/<topic>/
  index.md      topic handoff board: state, next, progress, read pointers
  design.md     optional long design / spec / decision surface
  plan.md       optional current main execution plan
  plans/        optional alternate, staged, superseded, or branch plans
  notes.md      optional scratch; clear or fold into index before archiving
```

`index.md` is the first and only topic file read **after the user chooses that topic**. It
must be short enough to restore the thread quickly, and concrete enough to continue without
the old chat. It absorbs the old context/progress split: state, next, progress summary,
verification, open questions, and explicit read pointers live together under H2 sections.

Recommended `index.md` skeleton:

```markdown
# Index — <topic>

## State

## Next

## Read now

- plans/08-final-cleanup.md
- knowledge/coding/comments.md

## Read if

- design.md — if the next plan conflicts with settled design
- plans/01-auth-model.md — if auth decisions need archaeology

## Progress

## Open questions
```

`design.md`, `plan.md`, and `plans/` are not preloaded. They are supporting material read
only when `index.md` points at them or the current action makes a `## Read if` condition
true. `plans/` is not required when there is only one plan; when alternatives or staged
plans exist, name them by purpose or order (`08-final-cleanup.md`, `rollback.md`), and keep
`index.md ## Next` pointing at the current one.

Do not create top-level `work/<topic>.md` efforts, split sibling plan/spec files, or side
`docs/` working trees for active effort artifacts. Effort package files are reached from
cockpit and the topic index, not routed through knowledge — so they carry **no routing
header**.

## knowledge — headers for discovery, bodies for execution

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

Preflight reads knowledge **headers** to build the routing map, never full bodies. A
knowledge body is read only when a chosen topic / index / action needs it. `index.md
## Read now` and `## Read if` are the topic's dependency pointers: they record which
knowledge bodies were chosen from the header map, so the next session does not have to
infer the same dependencies again.

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
  out of `work/<topic>/`. Preserve its shape (`index.md`, optional `design.md`, `plan.md`,
  `plans/` / notes) so later archaeology has the whole effort together. Before moving,
  compress `index.md ## Progress` enough that the archive explains what finished and what
  was verified.
- `~/.flightdeck/projects/<slug>/ideas/<topic>/` holds an unstarted topic seed. Keep it
  light: usually `idea.md` (problem / why it matters / activation trigger / rough notes).
  Do not create a full `index.md` / plan set until the idea is promoted into active
  `work/<topic>/`; otherwise parked ideas look like live recovery payloads.
- To start an idea, move or copy it into `work/<topic>/`, then create the active package
  entry file (`index.md`) and any needed supporting files from the seed. Location changes
  the state; no status field is added.

## global knowledge

Global knowledge under `~/.flightdeck/knowledge/` follows the same routing-header and
domain-folder rules as project knowledge. It is for genuinely cross-project behavior:
commit conventions, command-running rules, reusable tool procedures, framework traps that
apply beyond one repo.

Prefer `~/.flightdeck/knowledge/<domain>/...` and subscribe to either a domain directory or
a specific file from `briefing.md`. Legacy root-level global files may still be subscribed
for compatibility, but new global knowledge should not grow a root pile.
Global knowledge is domain-routed, not topic-routed; `archive/<topic>/` and `ideas/<topic>/`
belong only under `~/.flightdeck/projects/<slug>/`.

Global knowledge moves are cross-project changes. A root-level global file is a compatibility
path, not a normal cleanup target: do not move, rename, or delete it just because one deck's
walkaround found it.

Global knowledge is discovery/input, not an active topic's recovery payload. If a topic
needs a global note to continue, first materialize the relevant content into the project's
warm `flightdeck/knowledge/<domain>/...` as a local note, summary, or project-specific
adaptation, then point `work/<topic>/index.md` at that local file. Topic `## Read now` /
`## Read if` pointers should not depend on `~/.flightdeck/knowledge/...` paths directly.
That keeps active recovery self-contained in the project git repo even if the mother store
is later reorganized.
