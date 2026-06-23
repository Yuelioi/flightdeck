---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — loads the protocol, reads cockpit.md / rules.md / uses.md, walks the deck tree (ls + grep) for what the task needs, and reports the next step. Nothing is injected; not running preflight = flightdeck not engaged. Triggered by /flightdeck:preflight.
---

<!-- DRAFT (sub-plan #4, redesign) — this is what skills/preflight/SKILL.md becomes
in the new form. It loads the micro-core as its protocol body and points to the deep
protocol.md on demand. Lives in work/ until the cutover; does not touch live skills/. -->

## Run this — read-only session entry

The protocol you load on entry is the **micro-core** (`micro-core.md` — two verbs
`preflight`/`persist` + one audit `walkaround`, the layout, and the invariants); the
deep details load on demand from `protocol.md`.

0. **Deck existence.** If `flightdeck/cockpit.md` is absent → print "No flightdeck
   deck here — create `flightdeck/cockpit.md` to start one." and **STOP**.
1. **Read `flightdeck/rules.md`** (project house rules — single file, stable) and
   **`flightdeck/uses.md`** (one `~/.flightdeck`-relative path per line this project
   subscribes to; `#` comments). Fold each subscribed global path into the routing
   tree alongside local `knowledge/`. Local shadows global on the same relpath
   (replace, not merge); a subscribed path that's missing/renamed → one soft warning,
   continue (never fail). See `protocol.md` § uses.md shadowing.
2. **Read `flightdeck/cockpit.md`** (full) — note focus + next, the in-flight efforts
   (whatever is in `work/`), and open questions. This is the recovery payload; do
   **not** rewrite it on entry.
3. **Walk the tree for what the task needs (lazy).** Default load = cockpit.md only;
   everything else is on demand. `ls` the deck (`work/`, `knowledge/<domain>/`, the
   subscribed global subtrees). When `ls` + filenames aren't enough to judge
   relevance, run a transient `derive-listing <area>` (grep routing headers; see
   `protocol.md` § Derived listing) — never written to disk.
4. **Passive git note.** `git branch --show-current` + `git status --short`. Emit one
   non-blocking line only if the branch clearly mismatches the cockpit focus, or on a
   detached HEAD. Otherwise say nothing.
5. **Report the next step, then STOP.** State the cockpit's next action in one
   sentence and emit the `─── 🛫 preflight ───` banner (`[Stage]` + `[Next]` +
   read-only / "say go"). Do NOT load task files or start execution.

## Not engaged unless you run this

Nothing auto-fires and nothing is injected: if you never run preflight this session,
flightdeck isn't engaged — no protocol loaded, nothing auto-persists, and just
looking around the tree costs nothing. Turn-end **persist** (rewrite cockpit, write
knowledge in place, commit the project repo) only applies once preflight has loaded
the protocol this session.

## Fallback when the cockpit names no next action

Don't auto-start. Surface candidates: active efforts in `work/` first; then ideas in
`~/.flightdeck/projects/<x>/ideas/`. Ask which to start.
