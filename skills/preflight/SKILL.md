---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — reads INDEX/cockpit and reports the next step, warms the routing catalog, and gives a passive note on obvious git/version misalignment. No deck (no cockpit.md) → points to /flightdeck:launch and stops. Triggered by /flightdeck:preflight.
---

# Flightdeck Preflight

The **session-entry takeover** for flightdeck. Run `/flightdeck:preflight` at the start of a working session: it reads the cockpit, reports the next item, and stops — **read-only**. It does **not** create decks (that is `/flightdeck:launch`) and does **not** audit deck integrity (that is `/flightdeck:walkaround`). Use it when:

- Starting a working session in a project that already has a `flightdeck/`.
- Re-anchoring a long session that has drifted away from the cockpit.

The protocol "textbook" (data model, folder semantics, routing, write gate, lifecycle) is in [protocol.md](protocol.md) — load it on demand; see the index at the bottom.

## Run this checklist exactly

0. **Deck existence (graceful degrade — run first).** If **`flightdeck/cockpit.md` does not exist**, report one line — "No flightdeck deck here — run `/flightdeck:launch` to create one." — and **STOP**. (preflight reads a deck; it does not create one. Whether a deck is healthy/valid is `/flightdeck:walkaround`.)

1. **Read `flightdeck/rules.md`** if present. Resolve config per [protocol § Rule resolution order](protocol.md#rule-resolution-order): infer git from deck root `.git` (House Rule `this deck doesn't use git` overrides — when no-git, skip step 4's git note). Pre-3.0 keys, if present, are read but ignored.

   **Layout verdict (read-only — preflight never writes version).** Get the deck's layout verdict: **fast path** (script runtime reachable — `uv`/`python`) `flightdeck_index.py <deck> --verdict`; **fallback** read `MIGRATION.md` frontmatter (`current` + `layout_need_update` — the YAML, not the prose) and self-check the structural signals, yielding the same verdict. If the verdict is **not `current`** (`compatible-behind` / `structural-behind` / `malformed`), emit the passive note in step 4 pointing at walkaround. preflight **never bumps `version` and never migrates** — every version write (bump or migration) is walkaround's (it reads the same verdict).

2. **Read `flightdeck/INDEX.md`** (root INDEX) once, in full — the global status summary (counts per folder). Then **read `flightdeck/cockpit.md`** once, in full — focus on `Last updated`, `Active focus`, the `## 进行中` AUTO region (the active set), the `## 下一步` action, and the `## 关键上下文` recovery slot (the load-bearing literals from last session, if any). These are the reconcile baseline; read each once and treat as cached. `preflight` **reads** `## 进行中` / `## 下一步` / `## 关键上下文` but never rewrites them — a stale `## 下一步` is corrected at the next landing / status write point, not here.

3. **Catalog warm-up (priming, NOT audit). READ ≠ DISPLAY.** Read the folder INDEX files so the session knows what routed knowledge exists — do NOT glob individual files or read per-file frontmatter, and do NOT audit them. **The READ is unchanged (priming is preserved — the AI must still know what exists, with each entry's `when_to_read` already in context for routing); only the user-visible OUTPUT is slimmed to COUNTS.** `when_to_read` is loaded on demand when a task triggers — but it is already in context for routing, so trimming the echo loses no discoverability.
   - Read `flightdeck/checklists/INDEX.md` and `flightdeck/incidents/INDEX.md` **fully into context** (entries with `when_to_read` — routing intact). **Display only counts** (see Output format); do NOT echo per-entry `when_to_read` / `applies_to` / `status` tables.
   - Read `flightdeck/docs/INDEX.md` **(top-level only) into context**. `docs/` may nest into area sub-folders; preflight reads only the **top-level INDEX** (each row = one area or doc entry with a one-line purpose + `last_updated`) — loaded for routing, displayed as a count. Do NOT drill into area sub-folders or individual doc bodies — load those on demand when the task calls for it.
   - **Do NOT** check status legality or INDEX↔folder consistency — that is `walkaround` (Audits 1/5). preflight only surfaces *what exists*.
   - `references/` is deliberately out of the catalog (imported external material is browsed on purpose, not surfaced every preflight).
   - `obsolete` knowledge (e.g. a root-fixed, retired incident) is **already absent from the catalog** — the INDEX `<!-- AUTO -->` region excludes it, so preflight reads no obsolete rows (it stays on disk + grep-able for regression detection, just out of active routing). No special handling needed here.
   - Do NOT drill into individual checklist/incident/doc files until a trigger matches at execution time (read folder INDEX only).
   - **待验证 report (derived from a deterministic scan, source = files not cockpit).** Run `flightdeck_index.py <deck> --verify-pending` (prints `path<TAB>note` for every artifact carrying `verify`, across the active tree + `archive/`). Render each scan row as `⚠未验证: <file> — <怎么验>` (the `<note>` is the row's how-to-verify value). Because the list is re-derived fresh from the `verify` fields on disk each preflight, a hand-edited or trimmed cockpit **cannot lose the debt**. This is the non-blocking verification marker — canonical contract: [protocol § 验证非阻塞](protocol.md#验证非阻塞-non-blocking-verification) + [exit-ritual § Step 3c](exit-ritual.md#decision-tree) (待验证 surfacing); do not restate it here. (No Python runtime → fall back to grepping `verify:` across the deck + `archive/` by hand.)

4. **Passive git/version note (non-blocking — skip git entirely when no-git).** Gather `git branch --show-current` + `git status --short` in one pass; emit a one-line note only when a row below triggers, never a blocking "Resolve which?" prompt:

   | Signal | Trigger? | Note |
   |---|---|---|
   | current branch token clearly mismatches `Active focus` | yes | `⚠ git state looks off (branch ≠ Active focus) — review before continuing` |
   | detached HEAD | yes | `⚠ git state looks off (detached HEAD) — review before continuing` |
   | layout verdict ≠ `current` (from step 1) | yes | `ℹ deck layout behind (<verdict>) — run /flightdeck:walkaround` |
   | uncommitted changes / ahead-behind / multiple stashes | no | (say nothing — day-to-day state, not preflight's concern) |

   Git-state notes say **"review before continuing"**, not "run walkaround" — walkaround is a read-only file audit and does not read live git. Only the **layout-verdict** note points at walkaround.

4a. **Retroactive safety net (preflight's ONE allowed write — compensating for landing-not-run).**

   Preflight is read-mostly. The single write it is **allowed** to perform is flipping affected knowledge artifacts to `stale` (an uncommitted frontmatter edit that the next landing commits). It does **not** write the anchor: the anchor is simply the most recent `Flightdeck-Sync:` trailer commit, and it advances **automatically at the next landing** (preflight makes no commit, so there is nothing for it to advance). No graduate, no drain — those are landing's moves. Preflight surfaces them but does NOT execute them automatically; the heavy moves stay landing's.

   Run the following three checks. Each is idempotent; already-correct state = no-op.

   **(i) Compensating stale check.**
   Run: `flightdeck_index.py <deck> --changed-since-anchor`
   (diffs from the last `Flightdeck-Sync:` anchor to HEAD plus worktree; catches sessions where landing didn't run).
   For each `docs/` + knowledge artifact whose `when_to_update` is semantically matched by any of those paths:
   - Auto-flip `status: stale` in its frontmatter (same auto-flip rule as exit-ritual — no pre-ask; idempotent). Re-running preflight is safe: already-`stale` = no-op, and the anchor only moves at the next landing's trailer commit.
   Fallback (no anchor or no Python runtime): diff this session's changed files visible in `git status` against `when_to_update` fields by hand.

   **(ii) Graduate compensation.**
   Scan `specs/` for any `graduate: true` spec whose `status` is `done` and that **still sits in `specs/`** (landing didn't finish the graduate move).
   - If found: surface it — "graduate 待完成: `specs/<file>` — landing 未完成此步骤，需执行 graduate 改写搬运。" Do NOT auto-graduate here; the rewrite is a judgment-heavy operation that belongs to landing.

   **(iii) Obsolete reminder.**
   Run: `flightdeck_index.py <deck> --archivable`
   If the output includes any `obsolete` knowledge artifact still in the active area:
   - Surface it — "待排空 (obsolete knowledge): `<file>` — 下次 landing 会自动归档。" Do not drain here; draining is landing's job.

   Include any findings from (i)–(iii) in the preflight output before the routing catalog. If all three checks are clean, omit the section silently.

5. **Report item #1, then STOP.** Read-only recon doesn't fly the mission. State the `## 下一步` item in one sentence and hand off: "🛫 Preflight complete (read-only). Say 'go' to execute item #1." Do not load any file body or start the task — that's the next turn.

   **Land-readiness as the FINAL output line** (skip under no-git): if `git status` shows **≥ 5** changed files under `flightdeck/`, append "⚠ N unlanded changes since last land — consider `/flightdeck:landing`". Below the threshold, say nothing.

## Fallback when `## 下一步` is empty

Don't auto-start anything. The data source is the **folder INDEX rows** (which carry `status`) — not file mtime, not a re-audit. Search in order (a missing directory counts as empty), present candidates to the user:

1. `flightdeck/plans/INDEX.md` — `active` rows, most actionable first; a `done`-but-unlanded plan → offer to land it.
2. `flightdeck/specs/INDEX.md` — `active` designs not yet turned into a plan; ask which to plan next.
3. `flightdeck/specs/INDEX.md` **to-start pool** — the `待启动（idea）` group; ask which (if any) to start (flip `idea → active`).

> **Done-but-unlanded (any folder):** an artifact whose `status: done` but still sits in its source folder is *done-but-unlanded*. Offer to land it via the [Land Routine](exit-ritual.md#land-routine). This applies to `specs/`, `plans/`, and any workflow folder.

## Output format

```
Root INDEX: specs/ — 2 (1 active, 1 done) | plans/ — 1 active | incidents/ — 1 active | checklists/ — 2 active
Cockpit (Last updated: 2026-05-25; Active focus: <X>)

Routing catalog (loaded into context — read on demand; status audit → /flightdeck:walkaround):
docs 3 · checklist 2 · incident 1

待验证:
⚠未验证: specs/2026-05-20-cross-host-hooks.md — 相位4 各家 live 实证

下一步 (item #1): <item description>
关键上下文: <load-bearing literals from last session, if any — omit the line when - (none)>

🛫 Preflight complete (read-only). → Say "go" to execute item #1.
```

The catalog line shows **counts only** (`docs N · checklist N · incident N`) — the folder INDEX files are still read in full into context (routing/priming unchanged); only the echo is trimmed (READ ≠ DISPLAY), so `when_to_read` / `applies_to` are in context for routing but not printed. A zero-count kind is omitted from the line; if all three folder INDEX files are absent or empty, print `Routing catalog: (empty — no routed resources yet)`. The **待验证** block lists every `--verify-pending` scan row as `⚠未验证: <file> — <怎么验>`; omit the block entirely when the scan is empty (the list is re-derived each preflight from the `verify` fields on disk, so it is never lost to a cockpit edit). Append any triggered git/version note from step 4 on its own line. Place any step 4a findings (stale flips, graduate reminders, obsolete reminders) **before** the routing catalog. The Land-readiness line is always last.

## Don't do

- Don't create a deck — deckless → point at `/flightdeck:launch` and STOP (step 0).
- Don't write `version` or migrate — preflight only reads the layout verdict and reports it; bump/migration are `/flightdeck:walkaround`'s.
- Don't audit — status legality, INDEX↔folder consistency, cockpit drift, migration offers all belong to `/flightdeck:walkaround`.
- Don't run the blocking "Resolve which?" git reconcile — git divergence is a passive one-liner now.
- Don't auto-pick a fallback when `## 下一步` is empty — always ask.
- Don't bump `Last updated` — entry doesn't modify cockpit.
- Don't grep the codebase for "things to do" — cockpit.md is authoritative.
- Don't drill into individual checklist/incident/doc files or area sub-folders until a trigger matches at execution time (read folder INDEX only).
- **Don't graduate specs or drain `obsolete` artifacts** — those are landing's moves. Preflight surfaces them (step 4a) and stops; execution happens at the next landing.
- **Don't write anything beyond the one allowed write** (step 4a: flip `stale`). Preflight does not write/advance the anchor (that happens at the next landing's `Flightdeck-Sync:` trailer). All other preflight actions are read-only.

## Protocol knowledge (load on demand)

- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle · promotion gates · common mistakes
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout (full, always)
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — the landing ritual (run by `/flightdeck:landing`) + Land-readiness check

(First-time deck creation lives in `/flightdeck:launch`.)
