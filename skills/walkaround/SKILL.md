---
name: walkaround
description: Use when explicitly invoking the flightdeck integrity audit — a read-only, on-demand sweep for drift the new form has no mechanism to self-correct: cockpit vs reality, orphaned work, duplicate traps, missing routing headers, done-but-not-archived. The only trust-but-verify net. Triggered by /flightdeck:walkaround.
---

## Why this exists

The new form drops every mechanical self-corrector (no schema/INDEX/sync/status
machine). Stale, routing, recurrence, write-gate are all on AI judgement + convention.
**walkaround is the only trust-but-verify net** — a read-only, on-demand sweep a human
runs to catch where the AI drifted. It writes nothing; it reports findings for you to
act on. Nothing here self-heals.

## Run this — read-only audit

Sweep the deck and report each finding with a severity (`⚠` warn / `i` info). Fix
nothing; this is a report. The cockpit is free-form prose, so these checks are
**read-by-judgement**, not field-matching — that's the point of a trust-but-verify
net: a second pair of eyes reading what's actually there, not a schema validator.

1. **Cockpit shape + reality.** The cockpit should carry the canonical skeleton
   (`Focus:` + `## In flight` + `## Next` + `## Open questions`) — flag (`i`) a missing
   section. Then check reality: does `## In flight` match what's actually in `work/`?
   Flag (`⚠`) efforts the cockpit claims that aren't in `work/`, and a focus/next that
   points at something already moved to the cold store.
2. **Orphaned work.** Each `work/<effort>/` should be reachable from the cockpit
   (named in focus / next / in-flight). Flag any effort folder the cockpit never
   mentions — it's either lost or finished-but-not-recorded.
3. **Duplicate traps.** Two `# ⚠ <title>` trap files describing the same pitfall (same
   domain, near-identical title/symptom) → flag; recurrence should re-read the existing
   trap, not spawn a copy (see [../preflight/protocol.md](../preflight/protocol.md) § Incidents).
4. **Missing / empty routing headers.** Every knowledge file — local `knowledge/`
   **and any `uses`-subscribed global file** — must open with a routing header
   (`# <title>` + `SUMMARY:` + `READ WHEN:`, ended by `---`). Flag (`⚠`) any missing
   the header or the `---` terminator (won't route); flag (`i`) a header whose
   `SUMMARY:` or `READ WHEN:` is present but empty (routes to nothing useful), or
   whose `---` terminator sits directly under the last header line with no blank line
   above it (that line then parses as a setext heading and the terminator vanishes on
   render).
5. **Done but not archived.** A finished effort should be moved out of `work/` into
   `~/.flightdeck/projects/<x>/archive/`. Flag a `work/` effort whose cockpit notes /
   contents read as done but that still sits in `work/` (location is state — leaving it
   in `work/` says "still live").
6. **uses.md health.** For each line in `uses.md`: flag (`⚠`) a subscribed
   `~/.flightdeck/…` path that's missing or renamed (dead subscription); flag (`i`) a
   subscription whose target was already vendored into the repo (the copy + the live
   subscription now double up). Local-shadows-global is by-design, not drift — don't
   flag it.

## Output

Prose list of findings grouped by check, each line `⚠`/`i` + the path + one-sentence
what's-wrong + how to resolve. End with a one-line tally (`N warn · M info`), or
"clean" when nothing drifted. Recommend fixes; never apply them.
