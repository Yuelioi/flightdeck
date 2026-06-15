---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — reads INDEX/cockpit and reports the next step, warms the routing catalog, and gives a passive note on obvious git misalignment. No deck (no cockpit.md) → points to /flightdeck:launch and stops. Triggered by /flightdeck:preflight.
---

## Run this checklist exactly  _(read-only session-entry — protocol textbook: [protocol.md](protocol.md))_

0. **Deck existence.** If `flightdeck/cockpit.md` absent → print "No flightdeck deck here — run `/flightdeck:launch` to create one." and **STOP**.
1. **Read `flightdeck/rules.md`.** Resolve config per [protocol § Rule resolution order](protocol.md#rule-resolution-order). Infer git per that order (ancestor `.git` + deck not gitignored; a deck `### Rules` no-git entry → skip step 4).
2. **Read `flightdeck/cockpit.md`** (full) — note `Last updated`, `Active focus`, `## In Progress`, `## Next`, `## Key Context`. Do **not** rewrite anything.
3. **Catalog warm-up (READ ≠ DISPLAY).** Read `flightdeck/checklists/INDEX.md`, `flightdeck/incidents/INDEX.md` fully, and `flightdeck/docs/INDEX.md` top-level only — all fully into context (routing intact); display counts only; do NOT drill sub-folders or individual files. **待验证 scan:** run `flightdeck_index.py <deck> --verify-pending` (fallback: grep `verify:` across deck + `archive/`); render each as `⚠未验证: <file> — <怎么验>`. See [protocol § 验证非阻塞](protocol.md#验证非阻塞-non-blocking-verification).
4. **Passive git note (skip when no-git).** Run `git branch --show-current` + `git status --short`. Emit one non-blocking line only if: branch token clearly mismatches `Active focus` → `⚠ git state looks off (branch ≠ Active focus) — review before continuing`; or detached HEAD → same pattern. All other git state: say nothing.
5. **Report item #1, then STOP.** State `## Next` in one sentence, then emit the standardized **`─── 🛫 preflight ───` banner** (see Output format) carrying `[Stage]` + `[Next]` item #1 + the read-only / "say go" line. Do not load task files or start execution. In-banner final line (skip under no-git): if ≥ 5 changed files under `flightdeck/` → `⚠ N unlanded changes since last land — consider /flightdeck:landing`.

## Fallback when `## Next` is empty

Don't auto-start. Search in order and present candidates: (1) `plans/INDEX.md` — `active` rows first; `done`-but-unlanded → offer to land; (2) `specs/INDEX.md` — `active` designs not yet planned; (3) `specs/INDEX.md` `Backlog (idea)` pool — ask which to start.

## Output format

**Prose first** — cockpit + catalog + any debt:

```
Cockpit (Last updated: …; Active focus: …)
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
- Don't auto-pick a fallback; don't bump `Last updated`; don't grep codebase for tasks.
- **preflight 零写入** — all writes belong to landing/walkaround.

## Protocol knowledge (load on demand)

- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — landing ritual + Land-readiness check _(first-time deck creation: `/flightdeck:launch`)_
