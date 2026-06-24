---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — loads the protocol, reads cockpit.md / rules.md / uses.md, walks the deck tree (ls + grep) for what the task needs, and reports the next step. Nothing is injected; not running preflight = flightdeck not engaged. Triggered by /flightdeck:preflight.
---

## Run this — read-only session entry

The protocol you load on entry is the **micro-core** below; the deep details load on
demand from [protocol.md](protocol.md).

0. **Deck existence.** If `flightdeck/cockpit.md` is absent → print "No flightdeck
   deck here — create `flightdeck/cockpit.md` to start one." and **STOP**.
1. **Read `flightdeck/cockpit.md`** (full) — the recovery payload, read first: note
   focus + next, the in-flight efforts (whatever is in `work/`), and open questions.
   Do **not** rewrite it on entry.
2. **Read `flightdeck/rules.md`** (project house rules — single file, stable) and
   **`flightdeck/uses.md`** (one `~/.flightdeck`-relative path per line this project
   subscribes to; `#` comments). Fold each subscribed global path into the routing
   tree alongside local `knowledge/`. Local shadows global on the same relpath
   (replace, not merge); a subscribed path that's missing/renamed → one soft warning,
   continue (never fail). See [protocol.md](protocol.md) § uses.md shadowing.
3. **Walk the tree for what the task needs (lazy).** Default load = cockpit.md only;
   everything else is on demand. `ls` the deck (`work/`, `knowledge/<domain>/`, the
   subscribed global subtrees). When `ls` + filenames aren't enough to judge
   relevance, perform a transient *derive-listing* of that area — run the grep over
   routing headers yourself (see [protocol.md](protocol.md) § Derived listing); it's a
   convention, not an installed command, and prints to context only (never to disk).
4. **Passive git note.** `git branch --show-current` + `git status --short`, with a
   glance at the last few commit subjects (`git log --oneline -5`). Emit one
   non-blocking line only if reality clearly diverges from the cockpit focus — the
   branch *or* the recent commits are plainly about something else (a sign the last
   session moved the board without persisting, e.g. it ran under another workflow) —
   or on a detached HEAD. Otherwise say nothing.
5. **Report the next step, then STOP.** State the cockpit's next action in one
   sentence and emit the `─── 🛫 preflight ───` banner (`[Next]` + the read-only /
   "say go" line). Do NOT load task files or start execution.

## Not engaged unless you run this

Nothing auto-fires and nothing is injected: if you never run preflight this session,
flightdeck isn't engaged — no protocol loaded, nothing auto-persists, and just
looking around the tree costs nothing. Turn-end **persist** (rewrite cockpit, write
knowledge in place, commit the project repo) only applies once preflight has loaded
the protocol this session.

## Fallback when the cockpit names no next action

Don't auto-start. Surface candidates: active efforts in `work/` first; then ideas in
`~/.flightdeck/projects/<slug>/ideas/` (`<slug>` = the project's path-slug, see
[protocol.md](protocol.md) § Cold tier). Ask which to start.

---

# flightdeck (micro-core)

Two verbs:
- **preflight** (on request — you run `/flightdeck:preflight`): load this
  protocol, read `cockpit.md`, `rules.md` and `uses.md`, then walk the tree (`ls`
  + grep) for what's needed. Default load = cockpit.md only, rest lazy. Nothing is
  injected, it never auto-fires — skip preflight this session and it's
  disengaged (nothing auto-persists); looking around is free.
- **persist** (automatic — each turn / completed batch that moves the board):
  rewrite `cockpit.md`, write knowledge in place, `git commit` the project repo, then
  print a one-line `─── 🛬 landing ───` confirmation of what was saved (pairs with
  preflight's `🛫`; it's a confirmation, **not** a command). Keep the cockpit current
  enough to recover from it alone, without reading git — don't defer it to the end of
  a long run. A **work** effort is done when you move it out of `work/` to the cold
  store; git log records it left.

Plus one audit command — **walkaround** (on request): sweep for drift
(cockpit vs reality, orphaned work, duplicate traps, missing headers). The only
trust-but-verify net; nothing mechanical self-corrects.

Layout:
    <project>/flightdeck/   warm tier — git-tracked, committed each turn
      cockpit.md   Focus line + ## In flight + ## Next + ## Open questions
                   (canonical skeleton, extra sections fine; rewritten each turn)
      rules.md     project house rules — read on preflight, stable
      uses.md      one global path per line this project subscribes to
      work/        in-flight multi-step efforts (one file or folder each);
                   an effort's spec/design/plan live in work/<effort>/, not a side docs/ tree
      knowledge/   persistent — nested by domain; type via title line
    ~/.flightdeck/   cold tier — plain global dir, NOT git
      knowledge/     cross-project knowledge — genuinely universal (consulted via uses)
      projects/<slug>/  one project's cold store: archive/ + ideas/
                        <slug> = project abs path, separators / \ : → -  (collision-proof)

Invariants:
- **Location is state.** In the project = live; moved into `~/.flightdeck` = cold
  (done/parked). No status field: in `work/` = active, moved out = done.
  Knowledge (`knowledge/`) is *resident*, not work: present = valid, deleted =
  dead — no lifecycle. Nuanced states (blocked/reviewing/waiting) live in cockpit
  prose, not folders.
- **Routing header** (the one lightweight convention, no YAML schema). Every
  knowledge file opens with a header ended by `---`: a title (`# <title>`; pitfall
  `# ⚠ <title>`; checklist `# <X> checklist`), then `SUMMARY:` (one line), `READ
  WHEN:` (when to route here), optional `RECHECK WHEN:` (what it tracks — re-verify
  when that changes). Below `---`: free-form body. Routing reads only the header
  (cheap); freshness = mtime + body + RECHECK WHEN. **Leave a blank line before the
  `---`** (and one after the title) — without it the last header line and the `---`
  parse together as a setext heading, so the terminator vanishes on render. Canonical
  shape:

      # <title>

      SUMMARY: <one line>
      READ WHEN: <when to route here>

      ---

      <free-form body>
- **Write gate.** Record only what will change how you act later, or that you'll
  look up again. Skip: one-off logs; a build that passed; exploration that found
  nothing; a re-run that added nothing.
- **Zero-loss covers the recovery payload** (cockpit.md + rules.md + work +
  knowledge — all warm, all in git): persist commits the repo every turn;
  `cockpit.md` must answer what you're doing / where you are / next / open
  questions. The cold store is kept but unversioned — out of the guarantee.

Depth (`protocol.md`, read on demand): write-gate examples, incident
scope+crystallize rule, uses shadowing, vendoring, derived-listing.
