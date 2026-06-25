---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — loads this protocol, reads briefing.md (the rules) then cockpit.md (the recovery payload), walks the deck tree for what the task needs, and reports the next step. Nothing is injected; not running preflight = flightdeck not engaged. Triggered by /flightdeck:preflight.
---

**The iron law: every turn files what it learned, and nothing is lost when the
conversation switches.** Knowledge lands in the deck the moment it's produced; the deck —
committed each turn — is the recovery payload a fresh conversation reads to pick the work
up without loss. *File-as-you-go* and *recover-without-loss* are why flightdeck exists;
every rule below serves them.

## Priority

When guidance conflicts, later loses to earlier: **live user instruction > `CLAUDE.md`
(project instructions) > `briefing.md` (this deck's rules) > flightdeck defaults.** A deck
rule overrides a flightdeck default; a direct user request overrides everything.

## Loading (preflight) — read-only session entry

0. **Deck exists?** If `flightdeck/cockpit.md` is absent → print "No flightdeck deck here
   — create `flightdeck/cockpit.md` to start one." and **STOP**.
1. **Read `flightdeck/briefing.md` first — establish the rules.** `## Conventions` = this
   deck's house rules + AI-maintenance preferences; `## Subscriptions` = the
   `~/.flightdeck`-relative paths this project pulls in from the global tier. Fold each
   subscribed path into the routing tree alongside local `knowledge/`; local shadows
   global on the same relpath; a missing subscribed path → one soft warning, continue.
2. **Read `flightdeck/cockpit.md` — the recovery payload.** Note focus + next, the
   in-flight efforts (`work/`), open questions. Do **not** rewrite it on entry.
3. **Walk the tree for what the task needs (lazy).** Default load = briefing + cockpit
   only; everything else on demand. `ls` the deck (`work/`, `knowledge/<domain>/`, the
   subscribed global subtrees). When `ls` + filenames don't settle relevance, run a
   transient derived-listing (grep the routing headers — see operations.md); it prints to
   context only, never to disk.
4. **Reality note (cockpit ↔ git + work).** Two cheap cross-checks; one soft line each or
   silence, report-don't-fix:
   - *git:* `git branch --show-current` + `git status --short` + `git log --oneline -5`.
     One line only if reality clearly diverges from the cockpit focus (branch or recent
     commits plainly about something else — a sign the last session moved the board
     without persisting), or on a detached HEAD.
   - *work:* the `## In flight` from step 2 should match the effort folders from step 3.
     Flag an in-flight effort the cockpit names but `work/` lacks, or a `work/` effort the
     cockpit never mentions.
5. **Report the next step, then STOP.** State the cockpit's next action in one sentence and
   emit the `─── 🛫 preflight ───` banner (`[Next]` + the read-only / "say go" line). Do
   NOT load task files or start execution.

### Fallback when the cockpit names no next action

Don't auto-start. Surface candidates: active efforts in `work/` first; then ideas in
`~/.flightdeck/projects/<slug>/ideas/`. Ask which to start.

## Persist (every turn that moved the board) — automatic

At turn end, in order:

1. **Scan for knowledge — a real step, run every turn, not "when you remember."** Pass
   what the turn produced through the write gate (Invariants): a bug + root cause, a
   decision + why, a reusable procedure, a trap. Each hit is written **now**, in place
   under `knowledge/<domain>/` with a routing header — catching the learning *is* the
   trigger; don't defer it to effort-end. "Nothing qualified" is a valid outcome — but
   reached **on purpose**, by scanning, every turn.
2. **Rewrite `cockpit.md`** so the board recovers from it alone, without reading git.
3. **`git commit`** the project repo — one commit per turn.

Then print `─── 🛬 landing ───` that **always names the knowledge count, including zero**:
`cockpit ✓ · knowledge: 0 · commit a1b2c3d`. A string of `knowledge: 0` across turns is a
visible flatline, not silence — the heartbeat that makes a skipped scan obvious. No git
repo → `─── 🛬 landing ─── no git, not committed`. Full detail: operations.md.

## Invariants (load-bearing — keep in mind every turn)

- **Location is state.** In `work/` = active; moved into `~/.flightdeck` = cold
  (done/parked). No status field. Knowledge is resident: present = valid, deleted = dead.
- **Routing header.** Every knowledge file opens with a header ended by a `---`: a title
  (`# <title>`; trap `# ⚠ <title>`; checklist `# <X> checklist`), `SUMMARY:` (one line),
  `READ WHEN:` (when to route here), optional `RECHECK WHEN:`. Leave a blank line before
  the `---`. Routing reads only the header. Full anatomy + example: concepts.md.
- **Write gate.** Record only what changes how you'll act later, or that you'll look up
  again. Skip one-off logs, a passing build, fruitless exploration, a no-op rerun.
- **Zero-loss covers the recovery payload** (cockpit.md + briefing.md + work + knowledge,
  all warm, all git): persist commits every turn; cockpit alone must answer what you're
  doing / where you are / next / open questions. The cold store is unversioned — outside
  the guarantee.

## Not engaged unless you run this

Nothing auto-fires, nothing is injected. Skip preflight this session and flightdeck isn't
engaged — no protocol loaded, nothing auto-persists; looking around the tree costs
nothing. Turn-end persist applies only once preflight has loaded this protocol.

## More (load on demand)

- **[concepts.md](concepts.md)** — what spec / plan / knowledge / work effort / cockpit /
  briefing / the warm + cold (global) tiers actually are.
- **[operations.md](operations.md)** — how to write a spec/plan and where it ends up,
  archiving, the expanded persist, write-gate examples, incidents, subscription shadowing,
  vendoring, derived-listing.
