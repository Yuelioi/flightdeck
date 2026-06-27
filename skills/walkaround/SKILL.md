---
name: walkaround
description: Use when explicitly invoking the flightdeck repair pass — sweeps the deck against the current shape and fixes what's off (cockpit vs reality, malformed topic packages, orphaned work, duplicate traps, missing routing headers, root-level knowledge piles, done-but-not-archived work, dead subscriptions, knowledge flatline), and migrates an older-shaped deck to the current form. Triggered by /flightdeck:walkaround.
---

## What this is

flightdeck has no mechanical self-corrector — no schema / INDEX / sync / status machine;
routing, freshness, and the write gate all ride on AI judgement + convention. So a deck can
end up not matching the current shape two ways, and **walkaround is the one pass that fixes
both**:

- **a usage slip** — a step was skipped: a knowledge file with no routing header, an effort
  left in `work/` after it finished, a malformed topic package, a cockpit that no longer
  matches reality. → Fix it.
- **an older shape** — the deck predates the current form (`INDEX.md`, YAML frontmatter,
  kind-folders, recorded config). → Migrate it.

There is no separate "drift" to chase and no separate migrate command: a deck either matches
the current shape or it gets brought to it. What the current shape *is* lives in
[../preflight/concepts.md](../preflight/concepts.md) (definitions) and
[../preflight/operations.md](../preflight/operations.md) (procedures) — walkaround checks
against those, it doesn't restate them.

Before sweeping, first read the project's `flightdeck/briefing.md`, then read those two
protocol files enough to hold the current shape. `briefing.md` is the project's rulebook:
honor its `## Conventions` for language, gates, repo-specific constraints, and maintenance
preferences while running the walkaround, and use its `## Subscriptions` as the source of
truth for subscription checks. If `briefing.md` is missing or malformed, flag that as a
finding before continuing with best judgement. walkaround is a repair pass against the live
project rules plus the live protocol, not a stale copy of either.

## Safety — how it writes

walkaround repairs, so it writes. Two postures, chosen by risk:

- **Mechanical & lossless → apply, then report what you changed.** Adding a missing routing
  header, moving a finished effort to the cold archive, deleting an `INDEX.md`, stripping
  YAML frontmatter, repointing a stale cockpit line, creating or repairing a topic
  `index.md` from nearby content, moving a root-level knowledge file into an obvious domain.
- **Lossy or a judgement call → propose, don't apply.** Merging two near-duplicate traps,
  deciding which topic an orphaned folder belongs to, splitting a mixed-topic work file,
  splitting mixed-domain knowledge, removing a dead subscription.
- **Never delete content you can't place.** Unknown material is folded into the nearest home
  and flagged — never dropped.

## Run this — sweep and fix

Go check by check. The cockpit is free-form prose, so these are read-by-judgement, not
field-matching. For each finding: mark severity (`⚠` / `i`), then **fix** it (mechanical) or
**propose** the fix (lossy), per the safety postures above.

1. **Cockpit shape + reality.** It should carry the canonical skeleton (`Focus:` +
   `## In flight` + `## Next` + `## Open questions`) — note (`i`) a missing section. Then
   reality: does `## In flight` match what's in `work/`? Flag (`⚠`) topics the cockpit
   claims that aren't in `work/`, a `work/` topic the cockpit never mentions, a
   focus/next that points at a topic package but bypasses `index.md`, and a focus/next
   pointing at something already moved to the cold store. → Fix: repoint/rewrite the
   cockpit line (mechanical).
2. **Topic package shape.** Each active `work/<topic>/` should carry `index.md`; `design.md`,
   `plan.md`, `plans/`, and notes are optional supporting files. Flag top-level `work/*.md`
   effort files, split sibling files such as `*-plan.md` / `*-spec.md`, active spec/plan
   output parked outside `work/`, or a topic whose `index.md` lacks useful `## Next` /
   `## Read now` pointers. → Fix: when the topic is clear, create `work/<topic>/`, move
   long design/spec content to `design.md`, move long or staged plans to `plan.md` or
   `plans/`, and summarize state / next / progress / read pointers in `index.md`. If a
   legacy package has `context.md` and `progress.md`, merge their durable content into
   `index.md` and remove the old files after verifying nothing is lost. If multiple topics
   are mixed in one file, propose the split.
3. **Orphaned work.** Each `work/<topic>/` should be reachable from the cockpit (focus /
   next / in-flight). Flag a folder the cockpit never mentions — lost, or
   finished-but-unrecorded. → Fix: if clearly finished, archive it (mechanical); if it's
   unclear what it is or where it belongs, propose.
4. **Duplicate traps.** Two `# ⚠ <title>` files describing the same pitfall (same domain,
   near-identical symptom) → recurrence should re-read the existing trap, not spawn a copy
   (see operations.md § Incidents). → Propose a merge (lossy).
5. **Missing / empty routing headers.** Every knowledge file — local `knowledge/` **and any
   subscribed global file** — must open with a routing header (`# <title>` + `SUMMARY:` +
   `READ WHEN:`, ended by `---`). Flag (`⚠`) any missing the header or the `---` terminator
   (won't route); flag (`i`) an empty `SUMMARY:`/`READ WHEN:`, or a `---` with no blank line
   above it (parses as a setext heading; the terminator vanishes on render). → Fix: add /
   repair the header, deriving `SUMMARY` / `READ WHEN` from the file (mechanical).
6. **Knowledge domain shape.** Knowledge should live under `knowledge/<domain>/...`, not as
   a root-level pile, while keeping kind encoded by title (`#`, `# ⚠`, `checklist`) rather
   than by kind folders. → Fix: when the domain is obvious, move the file under the matching
   domain folder; if the file mixes domains, propose a split.
7. **Cold project store shape.** `archive/<topic>/` should contain completed topic packages;
   `ideas/<topic>/` should contain light unstarted seeds, usually `idea.md`, not full active
   recovery packages. → Fix: if an archived package is missing `index.md`, add a short
   final handoff from the contents; if an idea already has active-package files, propose
   promotion into `work/<topic>/` or reduction to an idea seed.
8. **Done but not archived.** A finished effort should be moved out of `work/` into
   `~/.flightdeck/projects/<slug>/archive/<topic>/`. Flag a `work/` effort whose cockpit notes /
   contents read as done but that still sits in `work/` (location is state). → Fix: move it
   (mechanical).
9. **Subscription health + topic dependency boundary.** For each path in `briefing.md`'s
   `## Subscriptions`: flag (`⚠`) a `~/.flightdeck/…` path that's missing or renamed (dead
   subscription); flag (`i`) one whose target was already vendored into the repo (copy + live
   subscription double up). Re-read the current `briefing.md` before calling a subscribed
   global path dead; the briefing is the source of truth. Local-shadows-global is by-design
   — don't flag it. A subscribed global knowledge file that still lives directly under
   `~/.flightdeck/knowledge/` is a legacy compatibility path: report it as (`i`), but do
   **not** include it in ordinary "execute proposed fixes" cleanup. Moving / renaming /
   deleting global knowledge requires a dedicated global subscription migration: discover
   likely subscribers from `~/.flightdeck/projects/<slug>/`, verify their live project
   briefings, repoint them, keep the old path until no verified briefing references it, then
   remove it.

   Then inspect active topic `index.md` read pointers. Flag (`⚠`) any `## Read now` /
   `## Read if` entry that points directly at `~/.flightdeck/knowledge/...` or otherwise
   depends on a global knowledge path for recovery. → Fix: materialize the relevant content
   into project-local `flightdeck/knowledge/<domain>/...` and repoint the topic index there;
   if the materialization would be lossy or unclear, propose it instead.
10. **Knowledge flatline inside the flightdeck boundary.** persist's knowledge scan is the one sub-action
   with no turn-to-turn forcing function, so it's the first thing a slipping session drops.
   Glance at recent commit subjects (`git log --oneline -20`): if a run clearly caught bugs /
   made decisions / hit traps yet `knowledge/` saw no add or update across that span, flag
   (`⚠`) the flatline — learnings likely never crystallized. Stay inside the flightdeck
   boundary by default: local `flightdeck/`, the project's cold store under
   `~/.flightdeck/projects/<slug>/`, and subscribed global knowledge under `~/.flightdeck/`.
   Do **not** sweep sibling workflow scratch such as `.superpowers/` or `tmp/` unless a
   flightdeck file (`cockpit.md`, a topic `index.md`, `briefing.md`, or knowledge) explicitly
   points there. If such a pointer exists, inspect only the referenced path, mine any
   write-gate hit into `knowledge/`, and propose clearing the scratch rather than doing it
   automatically.
11. **Older shape → migrate.** If the deck carries old-form structure, fold it to the current
   shape **by what each thing is, never losing content**:
   - kind-folders (`specs/` `plans/` `checklists/` `docs/` `incidents/`) → regroup into
     `knowledge/<domain>/` by subject; an active plan/spec → `work/<topic>/design.md` /
     `plan.md` or `plans/` plus `work/<topic>/index.md`; a done one → `archive/<topic>/`;
     an unstarted one → `ideas/<topic>/idea.md`.
   - delete `INDEX.md`; strip YAML frontmatter and replace it with a routing header.
   - recorded config (`version` / `runtime` / `agents_md` / toggles) → drop it.
   - vendored shared copies → subscribe to the master in `## Subscriptions` and delete the
     local copy (fold any project-specific addition into the local file or `briefing.md` first).
   - dangling body cross-links after moves aren't load-bearing (routing never follows them) →
     repoint the valuable ones, leave the rest.
   Structural moves are mechanical; anything that risks losing content → propose.

## Output

Prose list grouped by check: each line `⚠`/`i` + path + what was wrong + **what you did**
(fixed) or **what you propose** (lossy). End with a tally — `N fixed · M proposed`, or
`clean` when the deck already matched. If there are proposed fixes, ask whether to execute
the listed proposed cleanup / migration now; if the user says yes, continue directly with
those fixes while still respecting the safety posture above. Close with the banner
`─── 🔧 walkaround ───` (it pairs with launch's `🛠️`, preflight's `🛫`, and landing's `🛬`).
