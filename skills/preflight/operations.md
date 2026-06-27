# flightdeck — operations

Load on demand: the procedures behind the concepts. Definitions are
[concepts.md](concepts.md); the every-turn loop is [SKILL.md](SKILL.md). Read a section
here when you're about to do that thing.

## Persist (turn end), expanded

The SKILL.md verb spelled out. Persist runs at the end of an execution turn — one that did
real work or moved the board. A pure conversation / clarification turn that changed nothing
persists nothing.

**Don't let the deck lag a long run.** The trigger is every turn that moved the board —
and a single effort can span many turns. Persist at each completed batch / milestone, not
only when the whole effort wraps: the bar is that someone could close the conversation
*right now* and recover from `cockpit.md` + the active `work/<topic>/context.md` alone.
The same bar holds when you execute under another workflow (executing-plans, a subagent
loop, an external task runner): that workflow's own ledger is **not** the deck; an engaged
session still owes both the active topic context and the cockpit index a current state at
each milestone.

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
- **Efforts.** If a `work/<topic>/` finished this turn, move it out to
  `~/.flightdeck/projects/<slug>/archive/` (location is state). "Done" is a judgement: when
  the work reads as finished, **say in your turn report that you're archiving it** (so the
  user can object next turn) rather than archiving silently. Otherwise leave it in `work/`.
- **Topic recovery.** Rewrite the active `work/<topic>/context.md` whenever the topic state
  changed. Keep it short: state, next, blockers/open questions, and key facts. Update
  `progress.md` when execution progress changed; compress it into done/current/verified/not
  done rather than appending a transcript.
- **cockpit.md.** Rewrite it to reflect now, in the canonical skeleton (`Focus:` +
  `## In flight` + `## Next` + `## Open questions`). Keep it small — it's the project
  index, not the topic notebook.
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

## Writing a topic work package, and where it ends up

An active effort's working artifacts live together under `work/<topic>/` with stable names:

```text
work/<topic>/
  context.md
  design.md
  plan.md
  progress.md
  plans/
```

`context.md` is the topic recovery payload: update it whenever a new session would need a
fresh state, next action, blocker, or key fact to continue. `design.md` holds the why,
approach, tradeoffs, and settled decisions. `plan.md` is the current main execution plan,
including checklist output from another workflow. If there are multiple plausible plans,
keep the chosen one in `plan.md` and put the alternates under `plans/` with purpose names
(`rollback-plan.md`, `cookie-session-plan.md`). `progress.md` is a compressed status
summary; never use it as a chronological log.

Sibling workflows or spec-generators that default their output elsewhere must be pointed at
this folder or relocated into it before continuing. Do not leave active effort artifacts as
`work/<topic>.md`, `work/<topic>-plan.md`, `work/<topic>-spec.md`, split top-level files, or
a side `docs/` tree. A project's own finished/reference docs can still live in `docs/`;
this is about the *active* effort's working artifacts.

When the effort is **done**, move the whole `work/<topic>/` to
`~/.flightdeck/projects/<slug>/archive/` (location is state; `<slug>` = the project's
absolute path with `/`, `\`, `:` replaced by `-`). Say in your turn report that you're
archiving it. An **unstarted** idea lives in `~/.flightdeck/projects/<slug>/ideas/`.

## Write gate — concrete calls

The micro-core rule: record only what changes how you act later, or that you'll look up
again.

- RECORD in `knowledge/`: a bug + its root cause; a cross-topic or future-facing decision
  and why; a reusable procedure; a trap you'd otherwise hit again.
- RECORD in `work/<topic>/`: topic-local state, progress, unresolved implementation
  questions, and design details that would not change a future session outside that topic.
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

**Authoring side — the words you choose are the priority.** When you *write* a knowledge
file, its `READ WHEN:` phrasing and title glyph decide how preflight ranks it later — no
separate priority field exists, by design, so phrase the header to the tier you want. The
reader (preflight) elevates on a specific vocabulary; write to it:

- **To land *In force*** (a standing rule honoured every relevant turn): title it a
  `checklist`; write `READ WHEN:` **proactive + universal** — "before **any** \<routine
  action>", not a narrow case; voice `SUMMARY:` as a **directive** — "**Always** …",
  "**Never** … without …" — not a description ("notes on …"). The harder the rule, the
  more unconditional the words: *any / every / always / never / before* read as binding.
- **To leave *On call*** (a gotcha pulled at its trigger): open `# ⚠` and write
  `READ WHEN:` as the **symptom** — "when \<a failure shows>". This is not "lower value" —
  it is "read exactly when it bites" (defers, never discards).

Same content, opposite surfacing — a comment convention written "Always comment *why*, not
*what*; before editing any comment" binds every turn; the same lesson written "notes on a
case where a comment was wrong" sinks out of sight. Match the wording to how load-bearing
the knowledge actually is.

Reference recipe — `AREA` is the directory you're routing into (ripgrep if you have it,
otherwise any grep; one way, not a fixed command):

```sh
rg --no-heading -N -g '*.md' '^(# |SUMMARY:|READ WHEN:)' AREA/
```

It prints, per file, `path:line` for the title + labelled header lines — a flat directory to
scan. It surfaces the `READ WHEN:` label but not keywords on its `-` bullet lines; for the
full header read the file's top (the lines above its first `---`, so it's cheap). It is
**never written to disk** — transient, zero-maintenance, zero-drift.
