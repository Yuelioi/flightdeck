# flightdeck — operations

Load on demand: the procedures behind the concepts. Definitions are
[concepts.md](concepts.md); the every-turn loop is [SKILL.md](SKILL.md). Read a section
here when you're about to do that thing.

## Persist (turn end), expanded

The SKILL.md verb spelled out. Persist runs at the end of an execution turn — one that did
real work or moved the board. A pure conversation / clarification turn that changed nothing
persists nothing.

**Don't let the cockpit lag a long run.** The trigger is every turn that moved the board —
and a single effort can span many turns. Persist at each completed batch / milestone, not
only when the whole effort wraps: the bar is that someone could close the conversation
*right now* and recover from `cockpit.md` alone. The same bar holds when you execute under
another workflow (executing-plans, a subagent loop, an external task runner): that
workflow's own ledger is **not** the cockpit; an engaged session still owes the cockpit a
current `Focus` / `## In flight` at each milestone.

In order:

- **Scan for knowledge — scan first, every turn; a forcing step, not a reflex you hope
  fires.** Run the write gate over what the turn produced and *classify*, first match
  wins: a bug + root cause → a trap or fix note; a repeated procedure → a checklist; a
  decision + why → a design note; imported external material → a reference. Anything that
  passes → write it **now**, in place under `knowledge/<domain>/` with a routing header —
  at the moment of learning, not batched to effort-end (deferred knowledge is the learning
  that ends up in a gitignored scratch file and never graduates). "Nothing qualified" is
  legitimate — but you reach it by scanning on purpose, and you **report** it (the landing
  line), so a flatline of empty scans is visible rather than silent.
- **Efforts.** If a `work/<effort>/` finished this turn, move it out to
  `~/.flightdeck/projects/<slug>/archive/` (location is state). "Done" is a judgement: when
  the work reads as finished, **say in your turn report that you're archiving it** (so the
  user can object next turn) rather than archiving silently. Otherwise leave it in `work/`.
- **cockpit.md.** Rewrite it to reflect now, in the canonical skeleton (`Focus:` +
  `## In flight` + `## Next` + `## Open questions`). Keep it small — it's the recovery
  payload.
- **commit.** `git commit` the project repo with a one-line summary of the turn's
  increment. **One commit per turn** (mid-turn writes batch into it). If the turn moved the
  board but produced no new knowledge, the cockpit rewrite is itself a real change → commit
  it ("nothing new to save, board current"). Only a turn that changed *nothing* commits
  nothing. No git repo → no commit and no zero-loss: say so once ("no git repo — zero-loss
  not active").
- **landing line.** Close persist with `─── 🛬 landing ───` + what changed. **Always name
  the knowledge count, including zero** — `cockpit ✓ · knowledge: 0 · commit a1b2c3d`,
  `… · knowledge: 1 · …`, or `… · knowledge: 0 · archived <effort> · …`. The zero is
  load-bearing: a string of `knowledge: 0` is the flatline that makes a skipped scan
  obvious — drop the segment when nothing was written and the omission hides. It pairs with
  preflight's `🛫` (entry ↔ persist). "landing" is only the name of this confirmation — not
  a command, not a separate ritual; there is no `/landing`. A turn that persisted nothing
  prints no landing line. No git repo → `─── 🛬 landing ─── no git, not committed`.

## Writing a spec / plan, and where it ends up

An effort's spec/design and plan live **together** in `work/<effort>/` — a brainstorming
`design.md`, a `plan.md` (superpowers' writing-plans output drops in as-is; flightdeck
doesn't re-stamp it), plus any notes or checks. Don't scatter one effort's design and plan
across a top-level file **and** a separate folder, and don't drop them into a side `docs/`
tree. Sibling workflows or spec-generators that default their output elsewhere → point them
at (or relocate into) `work/<effort>/`, so the deck (cockpit, routing, walkaround, the
done→cold move) can see it. A project's own finished/reference docs can still live in
`docs/`; this is about the *active* effort's working artifacts.

When the effort is **done**, move the whole `work/<effort>/` to
`~/.flightdeck/projects/<slug>/archive/` (location is state; `<slug>` = the project's
absolute path with `/`, `\`, `:` replaced by `-`). Say in your turn report that you're
archiving it. An **unstarted** idea lives in `~/.flightdeck/projects/<slug>/ideas/`.

## Write gate — concrete calls

The micro-core rule: record only what changes how you act later, or that you'll look up
again.

- RECORD: a bug + its root cause; a decision and why; a reusable procedure; a trap you'd
  otherwise hit again.
- SKIP: "ran the tests, they passed"; "explored the API, found nothing useful"; "reran the
  build after a flake"; a log of steps with no durable conclusion.
- Borderline → ask: would a future session, cold, act differently for having this written?
  If no, skip.

## Incidents (traps)

A trap is a knowledge file whose title opens `# ⚠ <title>`, living in the domain it belongs
to. No fingerprint, no recurrence counter.

- On hitting a pitfall: write a `# ⚠ <title>` trap, placed by **scope** — project-specific
  → project `knowledge/<domain>/`; general lesson → `~/.flightdeck/knowledge/<domain>/`.
- On hitting it again: grep finds the existing trap → re-read it. Don't spawn a second copy.
  *Do* update it in place if your understanding changed (new root cause, better workaround)
  — "do not rewrite" means no duplicate, not frozen content.
- Once the fix is stable: crystallize it into a same-domain checklist (`# <X> checklist`),
  then delete the trap — git keeps the history for a project trap; a cold trap just goes.
  Location encodes scope, not count.

## Subscriptions — shadowing & vendoring

`briefing.md`'s `## Subscriptions` is a plain list — one `~/.flightdeck/`-relative path per
line (a directory entry subscribes the whole subtree; HTML-comment notes; no YAML).
preflight folds these global files/dirs into the routing tree alongside local `knowledge/`.

- **Shadowing.** Conflict on the same relpath: the **local file shadows the global one
  entirely (replace, not merge)** → deterministic, zero-maintenance, two preflights give
  the same result. To extend a global file, read both yourself; the file-level rule stays
  replace. A subscribed global path that's missing/renamed → preflight emits one soft
  warning and continues; it does not fail.
- **Vendoring (opt-in).** References to `~/.flightdeck` make the repo non-self-contained.
  When you need the repo portable, vendor: snapshot the referenced global file into the repo
  as a frozen copy, and drop its `## Subscriptions` entry. Default is live subscription, no
  copy.

Imported external material (RFC / competitor clones, vendored docs) is **not** a protocol
slot — keep it wherever suits you: in the project (`.gitignore` it if heavy), or in the cold
store. The protocol doesn't define or manage a `references/` location; it's your call.

## Derived listing

The routing-header **map** preflight scans on every entry (SKILL.md step 3): run a transient
`derive-listing <area>` — grep each file's routing header and print a one-shot directory to
context. It runs at entry as a matter of course, not only when `ls` + filenames are
ambiguous: a `READ WHEN:` can't route you anywhere unless it's resident, so the cheap
one-liner headers are loaded up front and the bodies stay on demand. It is **a convention, an
action you perform** — not an installed command: you run the grep yourself.

Surface per file: its path, title (keeping the `⚠` / `checklist` glyph), `SUMMARY:`, and
`READ WHEN:` — everything above the first `---`. Omit `RECHECK WHEN:` (freshness, not
relevance) and the body. `<area>` is just a path, so this works the same on a local
`knowledge/<domain>/` or a subscribed `~/.flightdeck/knowledge/…` subtree.

**Rank the map; don't read it flat.** The `READ WHEN:` and the title glyph already tell you
how a file routes — no extra field needed. A header shaped *proactive* ("before \<a routine
action>", and `checklist` titles) is a convention you hold as a live constraint and honour
when that action comes up; one shaped *reactive* ("when \<a symptom / failure>", and `# ⚠`
traps) is a gotcha you note and whose body you pull only once the symptom actually appears.
Binding conventions (comment / commit rules and the like) stay foregrounded whatever the
task. This ranking is what keeps a large deck usable — a deck can be mostly reactive traps,
and foregrounding all of them as equal "must-read" rules would drown the few that bind; the
map is scanned whole, but only the proactive handful occupies attention.

**Surface it in standard tiers** (SKILL.md step 3) — the report makes the scan visible and
keeps the deferred tier on the radar rather than dropping it:

- **In force** — standing conventions binding this session (the proactive / `checklist`
  handful). Name them; these are honoured as the work touches their action.
- **On call** — everything else, indexed. Each is pulled the instant its `READ WHEN:`
  fires; surface it as a count by domain, not a dump.

*Ranking defers, it never discards.* A low-tier header is "read later, on its trigger," not
"ignored for good" — an `# ⚠` trap whose symptom never appears simply never needs reading,
but the moment the symptom shows it routes you straight there.

**Authoring side — the header's shape sets the tier.** When you *write* a knowledge file,
its `READ WHEN:` phrasing and title glyph decide how preflight will rank it later — no
separate priority field exists, by design. Want it honoured as a standing rule → phrase
`READ WHEN:` proactively ("before \<a routine action>") and title it a `checklist`. It's a
gotcha to pull on a symptom → phrase it reactively ("when \<a symptom / failure>") and open
`# ⚠`. Write the header for how you want the file to surface.

Reference recipe — `AREA` is the directory you're routing into (ripgrep if you have it,
otherwise any grep; one way, not a fixed command):

```sh
rg --no-heading -N -g '*.md' '^(# |SUMMARY:|READ WHEN:)' AREA/
```

It prints, per file, `path:line` for the title + labelled header lines — a flat directory to
scan. It surfaces the `READ WHEN:` label but not keywords on its `-` bullet lines; for the
full header read the file's top (the lines above its first `---`, so it's cheap). It is
**never written to disk** — transient, zero-maintenance, zero-drift.
