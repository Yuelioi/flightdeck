# flightdeck — deep protocol

Read on demand when the micro-core's one-liners aren't enough. The micro-core (two
verbs + layout + invariants) lives in [SKILL.md](SKILL.md), loaded on entry; this
file is loaded only when you need the detail below.

## Persist (turn end)

The micro-core's second verb, spelled out. Persist runs at the **end of an execution
turn** — one that did real work or moved the board. A pure conversation /
clarification turn that changed nothing persists nothing. Persist applies for the
rest of any session in which you ran preflight; a session that never runs preflight
is not engaged (nothing auto-loads, nothing auto-saves — "engaged" is just normal
conversation history, not an injected flag).

At turn end, in order:

- **Knowledge** — apply the write gate (below). Anything that passes (a decision, a
  bug + root cause, a reusable procedure, a trap) → write it in place under
  `knowledge/<domain>/` with a routing header. Nothing passes → write nothing.
- **Efforts** — if a `work/<effort>/` finished this turn, move it out to
  `~/.flightdeck/projects/<slug>/archive/` (location is state; `<slug>` see § Cold tier).
  "Done" is a judgement:
  when the work reads as finished, **say in your turn report that you're archiving it**
  (so the user can object next turn) rather than archiving silently. Otherwise leave
  it in `work/`.
- **cockpit.md** — rewrite it to reflect now, in the **canonical skeleton**: a
  `Focus:` line + `## In flight` (active `work/` efforts) + `## Next` (next concrete
  action) + `## Open questions` (blocked / waiting / undecided — the nuanced states
  that have no folder). Those four are the minimum; extra sections are fine. It's a
  light convention (same weight as the routing header), not a YAML schema — no status
  field, no `Updated:` line (git knows when/who). Keep it small — it's the recovery
  payload.
- **commit** — `git commit` the project repo with a one-line summary of the turn's
  increment. **One commit per turn** (mid-turn writes batch into it; the noise of
  per-turn commits is the accepted price of zero-loss — squash later if you care). If
  the turn moved the board but produced no new knowledge, the cockpit rewrite is
  itself a real change → commit it ("nothing new to save, board current"). Only a turn
  that changed *nothing* commits nothing. No git repo → no commit and no zero-loss:
  say so once ("no git repo — zero-loss not active") so the user isn't assuming a
  guarantee that isn't on; that's why launch points you to `git init`.

## Work efforts

An effort in `work/` is **one file or one folder — never both**. A lightweight effort is
a single `work/<effort>.md`. A multi-artifact effort is a folder `work/<effort>/` that
keeps everything for it in one place — a brainstorming `design.md`, a `plan.md`
(superpowers' writing-plans output drops in as-is; flightdeck doesn't re-stamp it), plus
any notes or checks. Don't scatter one effort's design and plan across a top-level file
**and** a separate folder — co-locating an effort's artifacts is the whole point. The
`- [ ]` checkboxes inside a plan belong to executing-plans; flightdeck doesn't touch them.

## Cold tier (`~/.flightdeck`)

A plain global directory, **not** git — outside the zero-loss guarantee. Two kinds of
thing live here:

- `knowledge/` — **genuinely cross-project** knowledge: a comment-style guide, a commit
  checklist — what any project would consult. Projects opt in by listing a path under it
  in their `uses.md`. Don't park one project's research here.
- `projects/<slug>/` — **one project's** cold store: `archive/` (efforts moved out of
  `work/` when done) and `ideas/` (unstarted, out of the project view).

`<slug>` is the project's **absolute path with `/`, `\`, and `:` replaced by `-`** — e.g.
`E:\projects\tools\flightdeck` → `E--projects-tools-flightdeck`. Keying on the full path,
not the basename, keeps two same-named projects from colliding; it's the same scheme
Claude Code uses for `~/.claude/projects/`.

Imported external material (RFC / competitor clones, vendored docs) is **not** a protocol
slot — keep it wherever suits you: in the project (`.gitignore` it if it's heavy and you
want it live-viewable but uncommitted), or in the cold store. The protocol doesn't define
or manage a `references/` location; it's your call.

## Write gate

The micro-core rule: record only what changes how you act later, or that you'll
look up again. Concrete calls:

- RECORD: a bug + its root cause; a decision and why; a reusable procedure; a
  trap you'd otherwise hit again.
- SKIP: "ran the tests, they passed"; "explored the API, found nothing useful";
  "reran the build after a flake"; a log of steps with no durable conclusion.
- Borderline → ask: would a future session, cold, act differently for having
  this written? If no, skip.

## Incidents (traps)

A trap is a knowledge file whose title opens `# ⚠ <title>`, living in the domain
it belongs to. No fingerprint, no recurrence counter.

- On hitting a pitfall: write a `# ⚠ <title>` trap, placed by **scope** — project-
  specific → project `knowledge/<domain>/`; general lesson → `~/.flightdeck/knowledge/<domain>/`.
- On hitting it again: grep finds the existing trap → re-read it. Don't spawn a
  second copy. *Do* update it in place if your understanding changed (new root cause,
  better workaround) — "do not rewrite" means no duplicate, not frozen content.
- Once the fix is stable: crystallize it into a same-domain checklist
  (`# <X> checklist`), then delete the trap — git keeps the history for a project
  trap; a cold trap in `~/.flightdeck` just goes (unversioned). Location encodes
  scope, not count.

## uses.md shadowing

`uses.md` is a plain list — one `~/.flightdeck/`-relative path per line (a directory
entry subscribes the whole subtree; `#` comments; no YAML). preflight folds these
global files/dirs into the routing tree alongside local `knowledge/`.

- Conflict on the same relpath: the **local file shadows the global one entirely
  (replace, not merge)** → deterministic, zero-maintenance, two preflights give the
  same result. To extend a global file, read both yourself; the file-level rule
  stays replace.
- A subscribed global path that's missing/renamed: preflight emits one soft
  warning and continues — it does not fail.

## Vendoring

References to `~/.flightdeck` make the repo non-self-contained. When you need the
repo portable or shippable, **vendor**: snapshot the referenced global file into the
repo as a copy (a frozen reference), and drop the `uses.md` subscription for it. This
is opt-in and on-demand — the default is live subscription, no copy.

## Derived listing

When walking the tree to route and `ls` + filenames aren't enough to decide which
knowledge files are relevant, run a transient `derive-listing <area>`: grep each
file's routing header and print a one-shot relevance directory to context. The
trigger is AI judgment — filenames alone won't decide — not a count or threshold.
`derive-listing` is a **convention, an action you perform** — not an installed
command: you run the grep yourself (ripgrep below, or whatever your environment has).

What to surface per file: its path, title (`# …`, keeping the `⚠` / `checklist`
glyph), `SUMMARY:`, and `READ WHEN:` — the routing-decision lines of the header,
i.e. everything above the first `---`. Omit `RECHECK WHEN:` (that's freshness, not
relevance) and the free-form body.

`<area>` is just a path, so this works the same on a local `knowledge/<domain>/`
or a `uses`-subscribed `~/.flightdeck/knowledge/…` subtree.

Reference recipe — `AREA` is the directory you're routing into (ripgrep if you have
it, otherwise any grep; this is one way, not a fixed command):

```sh
rg --no-heading -N -g '*.md' '^(# |SUMMARY:|READ WHEN:)' AREA/
```

It prints, per file, `path:line` for the title + labelled header lines — a flat
directory to scan. It surfaces the `READ WHEN:` label but not keywords on its `-`
bullet lines; for the full header (bullets included) read the file's block — the
lines above its first `---`, i.e. the top of the file, so it's cheap. The recipe is
a first glance, not a contract, and it doesn't constrain the header format — bullets
under `READ WHEN:` are fine.

It is **never written to disk** — transient, zero-maintenance, zero-drift.
