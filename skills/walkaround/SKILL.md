---
name: walkaround
description: Use when explicitly invoking the flightdeck repair pass — sweeps the deck against the current shape and fixes what's off (cockpit vs reality, orphaned work, duplicate traps, missing routing headers, done-but-not-archived, dead subscriptions, knowledge flatline), and migrates an older-shaped deck to the current form. Triggered by /flightdeck:walkaround.
---

## What this is

flightdeck has no mechanical self-corrector — no schema / INDEX / sync / status machine;
routing, freshness, and the write gate all ride on AI judgement + convention. So a deck can
end up not matching the current shape two ways, and **walkaround is the one pass that fixes
both**:

- **a usage slip** — a step was skipped: a knowledge file with no routing header, an effort
  left in `work/` after it finished, a cockpit that no longer matches reality. → Fix it.
- **an older shape** — the deck predates the current form (`INDEX.md`, YAML frontmatter,
  kind-folders, recorded config). → Migrate it.

There is no separate "drift" to chase and no separate migrate command: a deck either matches
the current shape or it gets brought to it. What the current shape *is* lives in
[../preflight/concepts.md](../preflight/concepts.md) (definitions) and
[../preflight/operations.md](../preflight/operations.md) (procedures) — walkaround checks
against those, it doesn't restate them.

## Safety — how it writes

walkaround repairs, so it writes. Two postures, chosen by risk:

- **Mechanical & lossless → apply, then report what you changed.** Adding a missing routing
  header, moving a finished effort to the cold archive, deleting an `INDEX.md`, stripping
  YAML frontmatter, repointing a stale cockpit line.
- **Lossy or a judgement call → propose, don't apply.** Merging two near-duplicate traps,
  deciding which effort an orphaned folder belongs to, removing a dead subscription.
- **Never delete content you can't place.** Unknown material is folded into the nearest home
  and flagged — never dropped.

## Run this — sweep and fix

Go check by check. The cockpit is free-form prose, so these are read-by-judgement, not
field-matching. For each finding: mark severity (`⚠` / `i`), then **fix** it (mechanical) or
**propose** the fix (lossy), per the safety postures above.

1. **Cockpit shape + reality.** It should carry the canonical skeleton (`Focus:` +
   `## In flight` + `## Next` + `## Open questions`) — note (`i`) a missing section. Then
   reality: does `## In flight` match what's in `work/`? Flag (`⚠`) efforts the cockpit
   claims that aren't in `work/`, and a focus/next pointing at something already moved to the
   cold store. → Fix: repoint/rewrite the cockpit line (mechanical).
2. **Orphaned work.** Each `work/<effort>/` should be reachable from the cockpit (focus /
   next / in-flight). Flag a folder the cockpit never mentions — lost, or
   finished-but-unrecorded. → Fix: if clearly finished, archive it (mechanical); if it's
   unclear what it is or where it belongs, propose.
3. **Duplicate traps.** Two `# ⚠ <title>` files describing the same pitfall (same domain,
   near-identical symptom) → recurrence should re-read the existing trap, not spawn a copy
   (see operations.md § Incidents). → Propose a merge (lossy).
4. **Missing / empty routing headers.** Every knowledge file — local `knowledge/` **and any
   subscribed global file** — must open with a routing header (`# <title>` + `SUMMARY:` +
   `READ WHEN:`, ended by `---`). Flag (`⚠`) any missing the header or the `---` terminator
   (won't route); flag (`i`) an empty `SUMMARY:`/`READ WHEN:`, or a `---` with no blank line
   above it (parses as a setext heading; the terminator vanishes on render). → Fix: add /
   repair the header, deriving `SUMMARY` / `READ WHEN` from the file (mechanical).
5. **Done but not archived.** A finished effort should be moved out of `work/` into
   `~/.flightdeck/projects/<slug>/archive/`. Flag a `work/` effort whose cockpit notes /
   contents read as done but that still sits in `work/` (location is state). → Fix: move it
   (mechanical).
6. **Subscription health.** For each path in `briefing.md`'s `## Subscriptions`: flag (`⚠`) a
   `~/.flightdeck/…` path that's missing or renamed (dead subscription); flag (`i`) one whose
   target was already vendored into the repo (copy + live subscription double up).
   Local-shadows-global is by-design — don't flag it. → Propose the removal/repoint (lossy).
7. **Knowledge flatline + orphaned scratch.** persist's knowledge scan is the one sub-action
   with no turn-to-turn forcing function, so it's the first thing a slipping session drops.
   Glance at recent commit subjects (`git log --oneline -20`): if a run clearly caught bugs /
   made decisions / hit traps yet `knowledge/` saw no add or update across that span, flag
   (`⚠`) the flatline — learnings likely never crystallized. Then look for **orphaned scratch**
   (a sibling workflow's working dir left in the repo: `.superpowers/…`, a `tmp/` log) — often
   *where* the uncrystallized knowledge lives. → Fix: mine the scratch for write-gate hits and
   write them as knowledge (mechanical); propose clearing the scratch afterward.
8. **Older shape → migrate.** If the deck carries old-form structure, fold it to the current
   shape **by what each thing is, never losing content**:
   - kind-folders (`specs/` `plans/` `checklists/` `docs/` `incidents/`) → regroup into
     `knowledge/<domain>/` by subject; an active plan/spec → `work/<effort>/`; a done one →
     `archive/`; an unstarted one → `ideas/`.
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
`clean` when the deck already matched. Close with the banner `─── 🔧 walkaround ───`
(it pairs with launch's `🛠️`, preflight's `🛫`, and landing's `🛬`).
