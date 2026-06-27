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
*right now* and recover from `cockpit.md` as the chooser, then the chosen
`work/<topic>/index.md` as the topic handoff. The same bar holds when you execute under
another workflow (executing-plans, a subagent loop, an external task runner): that
workflow's own ledger is **not** the deck; an engaged session still owes both the chosen
topic index and the cockpit index a current state at each milestone.

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
- **Efforts.** If a `work/<topic>/` finished this turn, first compress `index.md` so the
  finished package explains done/current/verified/not-done, then move the whole folder to
  `~/.flightdeck/projects/<slug>/archive/<topic>/` (location is state). "Done" is a judgement: when
  the work reads as finished, **say in your turn report that you're archiving it** (so the
  user can object next turn) rather than archiving silently. Otherwise leave it in `work/`.
- **Topic handoff.** Rewrite the active `work/<topic>/index.md` whenever the topic state,
  next step, read pointers, blockers/open questions, or progress changed. Keep it short:
  state, next, `## Read now`, `## Read if`, progress, verification, and open questions.
  If the turn read or created a knowledge body that future continuation depends on, add that
  path to `index.md ## Read now` or `## Read if`; if a listed dependency no longer applies,
  remove it.
- **cockpit.md.** Rewrite it to reflect now, in the canonical skeleton (`Focus:` +
  `## In flight` + `## Next` + `## Open questions`). Keep it small — it's the project
  index / chooser, not the topic notebook.
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

An active effort's working artifacts live together under `work/<topic>/`. The only required
entry file is `index.md`; everything else is read on demand from its pointers:

```text
work/<topic>/
  index.md
  design.md   optional
  plan.md     optional
  plans/      optional
  notes.md    optional scratch
```

`index.md` is the topic handoff board: update it whenever a new session would need a fresh
state, next action, blocker, key fact, progress summary, or read pointer to continue.
`design.md` holds long why / approach / tradeoffs only when the topic needs that surface.
`plan.md` is fine for a single current plan; when a long spec is split into staged plans,
put them under `plans/` and point `index.md ## Next` / `## Read now` at the current stage.

Recommended `index.md` shape:

```markdown
# Index — <topic>

## State

## Next

## Read now

- plans/08-final-cleanup.md
- knowledge/<domain>/<file>.md

## Read if

- design.md — if a step conflicts with the settled design
- plans/01-auth-model.md — if auth decisions need archaeology

## Progress

Done:
- plans/01-auth-model.md

Current:
- plans/08-final-cleanup.md

Verified:
- ...

## Open questions
```

The read sections are dependency locks, not discovery mechanisms. Use the header map from
preflight to decide what belongs there while planning. During execution, read the bodies or
plans listed under `## Read now`; read `## Read if` entries only when their condition is
true. Add new entries when newly discovered knowledge or a newly selected plan becomes
required for future continuation.

Do not point an active topic directly at `~/.flightdeck/knowledge/...`. Global knowledge is
allowed to inform the work, but if the topic needs it for recovery, first materialize the
relevant content into project-local `flightdeck/knowledge/<domain>/...` (copy, summary, or
project-specific adaptation) and point the topic index at that local file. This avoids
breaking active recovery when global knowledge is merged, renamed, or reorganized.

Sibling workflows or spec-generators that default their output elsewhere must be pointed at
this folder or relocated into it before continuing. Do not leave active effort artifacts as
`work/<topic>.md`, `work/<topic>-plan.md`, `work/<topic>-spec.md`, split top-level files, or
a side `docs/` tree. A project's own finished/reference docs can still live in `docs/`;
this is about the *active* effort's working artifacts.

When the effort is **done**, compress `index.md ## Progress` into a final status summary
and move the whole `work/<topic>/` to
`~/.flightdeck/projects/<slug>/archive/<topic>/` (location is state; `<slug>` = the
project's absolute path with `/`, `\`, `:` replaced by `-`). Say in your turn report that
you're archiving it. An **unstarted** idea lives in
`~/.flightdeck/projects/<slug>/ideas/<topic>/` as a light seed, usually `idea.md`, not a
full active package.

To start an idea, move or copy its seed into `work/<topic>/`, then create `index.md` and any
needed supporting files. Do not let an unstarted idea masquerade as active work by giving it
a full handoff board while it is still cold.

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
Global knowledge should follow the same domain-folder and routing-header conventions as
project knowledge (`~/.flightdeck/knowledge/<domain>/...`). Existing root-level global
files can keep working as subscribed compatibility paths, but new global knowledge should be
placed under a domain.

- **Shadowing.** Conflict on the same relpath: the **local file shadows the global one
  entirely (replace, not merge)** → deterministic, zero-maintenance, two preflights give
  the same result. To extend a global file, read both yourself; the file-level rule stays
  replace. A subscribed global path that's missing/renamed → preflight emits one soft
  warning and continues; it does not fail.
- **Topic dependency boundary.** `briefing.md ## Subscriptions` admits global knowledge
  into the routing map; it is not a topic dependency file. Active topic `index.md` read
  pointers should reference local topic files or project-local `flightdeck/knowledge/...`.
  When a topic needs a global note, materialize it locally before adding the pointer.
- **Missing global path recovery.** If a subscribed global knowledge path cannot be loaded,
  re-read the current project's `briefing.md` before calling it dead; the briefing is the
  source of truth and may have changed. A missing path from a topic index is a protocol
  drift: topic indexes should not point at global paths directly, so materialize or remove
  the dependency instead of treating it as a subscription repair.
- **Global path migration.** Moving, renaming, or deleting `~/.flightdeck/knowledge/...`
  can break other decks. Do not perform it as a normal walkaround confirmation. Before a
  dedicated global migration, discover likely subscribers by walking
  `~/.flightdeck/projects/<slug>/`, deriving the live project path from each slug, and
  reading each project's current `flightdeck/briefing.md`. Repoint live subscriptions first,
  keep any legacy root-level path as compatibility while any verified briefing references
  it, and only then remove the old path.
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
one-liner headers are loaded up front and the bodies stay on demand. It is **a convention,
an action you perform** — not an installed command: you run the grep yourself. The map helps
write or repair `index.md ## Read now` / `## Read if`; it does not authorize reading every
knowledge body.

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
