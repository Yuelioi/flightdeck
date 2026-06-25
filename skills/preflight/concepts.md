# flightdeck — concepts

Load on demand: the definitions behind [SKILL.md](SKILL.md). This file says what each
thing *is*; how to operate on them is [operations.md](operations.md).

## The layout

```
<project>/flightdeck/   warm tier — git-tracked, committed each turn
  cockpit.md   Focus + ## In flight + ## Next + ## Open questions (rewritten each turn)
  briefing.md  stable, human-owned — ## Conventions + ## Subscriptions
  work/        active multi-step efforts (one file or one folder each)
  knowledge/   persistent, nested by domain; kind set by the title line

~/.flightdeck/   cold tier — a plain global dir, NOT git (the global / "mother" store)
  knowledge/     cross-project knowledge — genuinely universal (consulted via Subscriptions)
  projects/<slug>/  one project's cold store: archive/ + ideas/
                    <slug> = project abs path, separators / \ : → -  (collision-proof)
```

## cockpit.md — the recovery payload

The volatile "where am I" file: rewritten every turn, kept small. The bar is that someone
could close the conversation right now and recover from `cockpit.md` alone, without reading
git. Canonical skeleton — `Focus:` + `## In flight` (active `work/` efforts) + `## Next`
(next concrete action) + `## Open questions` (blocked / waiting / undecided — the nuanced
states that have no folder). Those four are the minimum; extra sections are fine. A light
convention, not a YAML schema — no status field, no `Updated:` line (git knows when/who).

## briefing.md — the stable rules

Human-owned, read first on entry. Two sections, no frontmatter:

- `## Conventions` — this deck's house rules + AI-maintenance preferences, in plain prose.
- `## Subscriptions` — one `~/.flightdeck`-relative path per line; what this deck pulls in
  from the global tier (empty = standalone).

Stable across turns. persist never rewrites it — only the AI maintaining a rule on your
request, or you, edits it.

## work effort — spec, plan, and the rest

An effort in `work/` is **one file or one folder, never both**:

- **spec / design** — the *why* and the *approach* for the effort.
- **plan** — the *steps*. The `- [ ]` checkboxes belong to whatever runs the plan (e.g.
  superpowers' executing-plans); flightdeck tracks the effort by its location, not by
  ticking boxes.

A multi-artifact effort is a folder `work/<effort>/` that keeps design + plan + notes
co-located. A trivial effort is a single `work/<effort>.md`. Effort files are reached from
the cockpit, not routed — so they carry **no routing header**.

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
Knowledge is *resident*: present = valid, deleted = dead. No lifecycle, no status.

## warm vs cold — the two tiers

- **warm** = the project's `flightdeck/` — git-tracked, committed each turn, inside the
  zero-loss guarantee. cockpit + briefing + work + knowledge live here.
- **cold** = `~/.flightdeck`, the plain global "mother" store — NOT git, outside the
  guarantee. It holds two things: cross-project `knowledge/` (genuinely universal, opted
  into via a briefing `## Subscriptions` line), and `projects/<slug>/` with `archive/`
  (efforts moved out of `work/` when done) + `ideas/` (unstarted, out of the project view).

**Location is state.** There is no status field; a thing's tier and folder say whether it's
active (`work/`), done (cold `archive/`), or parked (cold `ideas/`).
