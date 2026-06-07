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

3. **Catalog warm-up (priming, NOT audit).** Read the folder INDEX files so the session knows what routed knowledge exists — do NOT glob individual files or read per-file frontmatter, and do NOT audit them:
   - Read `flightdeck/checklists/INDEX.md` and `flightdeck/incidents/INDEX.md`. List each entry as **File + when_to_read (two columns only)** — drop `applies_to` / `status` (those live in the INDEX file; read on demand when a trigger matches). Append the footnote `(状态/合法性审计见 /flightdeck:walkaround)`.
   - Read `flightdeck/docs/INDEX.md` **(top-level only)**. `docs/` may nest into area sub-folders; preflight reads only the **top-level INDEX** (each row = one area or doc entry with a one-line purpose + `last_updated`). Do NOT drill into area sub-folders or individual doc bodies — load those on demand when the task calls for it.
   - **Do NOT** check status legality or INDEX↔folder consistency — that is `walkaround` (Audits 1/5). preflight only surfaces *what exists*.
   - `references/` is deliberately out of the catalog (imported external material is browsed on purpose, not surfaced every preflight).
   - `obsolete` knowledge (e.g. a root-fixed, retired incident) is **already absent from the catalog** — the INDEX `<!-- AUTO -->` region excludes it, so preflight reads no obsolete rows (it stays on disk + grep-able for regression detection, just out of active routing). No special handling needed here.
   - Do NOT drill into individual checklist/incident/doc files until a trigger matches at execution time (read folder INDEX only).

4. **Passive git/version note (non-blocking — skip git entirely when no-git).** Gather `git branch --show-current` + `git status --short` in one pass; emit a one-line note only when a row below triggers, never a blocking "Resolve which?" prompt:

   | Signal | Trigger? | Note |
   |---|---|---|
   | current branch token clearly mismatches `Active focus` | yes | `⚠ git state looks off (branch ≠ Active focus) — review before continuing` |
   | detached HEAD | yes | `⚠ git state looks off (detached HEAD) — review before continuing` |
   | layout verdict ≠ `current` (from step 1) | yes | `ℹ deck layout behind (<verdict>) — run /flightdeck:walkaround` |
   | uncommitted changes / ahead-behind / multiple stashes | no | (say nothing — day-to-day state, not preflight's concern) |

   Git-state notes say **"review before continuing"**, not "run walkaround" — walkaround is a read-only file audit and does not read live git. Only the **layout-verdict** note points at walkaround.

5. **Report item #1, then STOP.** Read-only recon doesn't fly the mission. State the `## 下一步` item in one sentence and hand off: "Preflight complete (read-only). Say 'go' to execute item #1." Do not load any file body or start the task — that's the next turn.

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

Routing catalog (know-what-exists — read on demand; status audit → /flightdeck:walkaround):

[Checklists]
| File | when_to_read |
|---|---|
| checklists/comments.md | before writing or editing any source-code comment |

[Incidents]
| File | when_to_read |
|---|---|
| incidents/parser-recursion.md | before designing a recursive parser |

[Docs]
| Area / File | 用途 | last_updated |
|---|---|---|
| docs/api-design/ | REST API 设计规范与决策记录 | 2026-05-20 |

(状态/合法性审计见 /flightdeck:walkaround)

下一步 (item #1): <item description>
关键上下文: <load-bearing literals from last session, if any — omit the line when - (none)>

Preflight complete (read-only). → Say "go" to execute item #1.
```

Omit any table group with no entries. If all three folder INDEX files are absent or empty, print `Routing catalog: (empty — no routed resources yet)`. Append any triggered git/version note from step 4 on its own line, and the Land-readiness line last.

## Don't do

- Don't create a deck — deckless → point at `/flightdeck:launch` and STOP (step 0).
- Don't write `version` or migrate — preflight only reads the layout verdict and reports it; bump/migration are `/flightdeck:walkaround`'s.
- Don't audit — status legality, INDEX↔folder consistency, cockpit drift, migration offers all belong to `/flightdeck:walkaround`.
- Don't run the blocking "Resolve which?" git reconcile — git divergence is a passive one-liner now.
- Don't auto-pick a fallback when `## 下一步` is empty — always ask.
- Don't bump `Last updated` — entry doesn't modify cockpit.
- Don't grep the codebase for "things to do" — cockpit.md is authoritative.
- Don't drill into individual checklist/incident/doc files or area sub-folders until a trigger matches at execution time (read folder INDEX only).

## Protocol knowledge (load on demand)

- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle · promotion gates · common mistakes
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout (full, always)
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — the landing ritual (run by `/flightdeck:landing`) + Land-readiness check

(First-time deck creation lives in `/flightdeck:launch`.)
