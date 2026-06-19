---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — mechanically refreshes vendored shared-knowledge from the master (its one write; git-deck auto, non-git asks), reads INDEX/cockpit and reports the next step, warms the routing catalog, and gives a passive note on obvious git misalignment. No deck (no cockpit.md) → points to /flightdeck:launch and stops. Triggered by /flightdeck:preflight.
---

## Run this checklist exactly  _(read-only session-entry — protocol textbook: [protocol.md](protocol.md))_

0. **Deck existence.** If `flightdeck/cockpit.md` absent → print "No flightdeck deck here — run `/flightdeck:launch` to create one." and **STOP**.
1. **Read `flightdeck/rules.md`.** Resolve config per [protocol § Rule resolution order](protocol.md#rule-resolution-order).
1.5. **Shared-knowledge refresh (mechanical, pre-read).** A deterministic, zero-AI splice — a distinct mechanical layer (same category as the turn-end INDEX hook), not a judgment step; runs after rules-resolution, before the cockpit/catalog read. Using the recorded `runtime`, run the index script `<deck> --sync-pull`:
   - **git deck** → apply directly (reversible via git); if it pulled, report one line `↻ synced N shared file(s) from master`. Silent when nothing was stale.
   - **non-git deck** → run `--sync-pull --check` first (writes nothing; prints `would-pull` lines), show what would change, and **ask** before applying (irreversible — same discipline as conform).
   - `master-missing` (`~/.flightdeck` absent) or a broken recorded runtime → silent no-op.
   - **Escape hatch:** a deck `### Rules` entry (e.g. "sync: detect-only on entry") downgrades this to read-only `--sync-pull --check` + a one-line stale note (no auto-write), per the [Rule resolution order](protocol.md#rule-resolution-order).
   This is the **only** write preflight triggers, and it touches **only** vendored shared regions — preflight's own checklist (the steps below) stays zero-write.
2. **Read `flightdeck/cockpit.md`** (full) — note `Updated`, `Focus`, `## In Progress`, `## Next`, `## Key Context`. Do **not** rewrite anything.
3. **Catalog warm-up (READ ≠ DISPLAY).** Read `flightdeck/checklists/INDEX.md`, `flightdeck/incidents/INDEX.md` fully, and `flightdeck/docs/INDEX.md` top-level only — all fully into context (routing intact); display counts only; do NOT drill sub-folders or individual files. **pending-verify scan:** run the index script `<deck> --verify-pending` (call form per the recorded `runtime` — [protocol § Rule resolution order](protocol.md#rule-resolution-order)); render each as `⚠ unverified: <file> — <how to verify>`. If the recorded runtime is broken, append a non-blocking `⚠ recorded runtime broken` and continue read-only (skip the scan — preflight never repairs). See [protocol § Non-blocking verification](protocol.md#non-blocking-verification).
4. **Passive git note.** Run `git branch --show-current` + `git status --short`. Emit one non-blocking line only if: branch token clearly mismatches `Focus` → `⚠ git state looks off (branch ≠ Focus) — review before continuing`; or detached HEAD → same pattern. All other git state: say nothing.
5. **Report item #1, then STOP.** State `## Next` in one sentence, then emit the standardized **`─── 🛫 preflight ───` banner** (see Output format) carrying `[Stage]` + `[Next]` item #1 + the read-only / "say go" line. You MUST NOT load task files or start execution. In-banner final line: if ≥ 5 changed files under `flightdeck/` → `⚠ N unlanded changes since last land — consider /flightdeck:landing`. Also non-blocking (any git mode): if `## In Progress` lists > ~5 active threads → add `⚠ N active threads — consider parking/closing some` (focus-loss signal, never a block).

## Fallback when `## Next` is empty

Don't auto-start. Search in order and present candidates: (1) `plans/INDEX.md` — `active` rows first; `done`-but-unlanded → offer to land; (2) `specs/INDEX.md` — `active` designs not yet planned; (3) `specs/INDEX.md` `Backlog (idea)` pool — ask which to start.

## Output format

**Prose first** — cockpit + catalog + any debt:

```
↻ synced N shared file(s) from master   ← omit when nothing pulled / detect-only / master-missing
Cockpit (Updated: …; Focus: …)
Routing catalog (loaded into context; audit → /flightdeck:walkaround): docs N · checklist N · incident N
  ← omit zero-count kinds; if all folder INDEXes absent: "Routing catalog: (empty)"
Verify pending: ⚠ <file> — <how>   ← omit when scan empty
```

**Then the standardized banner, last** (per [protocol § Act-report-close loop](protocol.md#act-report-close-loop)):

```
─── 🛫 preflight ───
[Stage]   <lifecycle stage>
[Next]    item #1: …   (Key Context: … — omit when none)
Read-only — say "go" to execute item #1.   (⚠ N unlanded changes — consider /flightdeck:landing)
```

## Don't do

- Don't create a deck; don't audit (status legality, INDEX↔folder, migration) — that's `/flightdeck:walkaround`.
- Don't prompt "Resolve which?" for git divergence — passive one-liner only.
- Don't auto-pick a fallback; don't bump `Updated`; don't grep codebase for tasks.
- **preflight performs no *judgment* writes** — no `Updated` bump, no INDEX regen, no artifact/status writes; all such writes belong to landing/walkaround. The **sole** exception is the mechanical shared-knowledge refresh (Step 1.5), a deterministic splice that touches only vendored shared regions (and on a non-git deck only after you ask).

## Protocol knowledge (load on demand)

- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — landing ritual + Land-readiness check _(first-time deck creation: `/flightdeck:launch`)_
