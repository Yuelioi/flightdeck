---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — the single entry point. Initializes `flightdeck/` when absent (no cockpit.md); otherwise reconciles cockpit.md against repo state via root INDEX.md, loads a routing catalog from folder INDEX files, and reports the cockpit `## 下一步` item. Triggered by `/flightdeck:preflight`.
---

# Flightdeck Preflight

The **single explicit entry point** for flightdeck. Nothing loads on its own — you run `/flightdeck:preflight` at the start of a working session. It either **initializes** a new `flightdeck/` (when none exists) or **reconciles** the existing one against repo state and **reports** the next item, then stops. It does not execute the item; that's the next turn's job. Use it when:

- Starting a working session in a project that has (or should have) a `flightdeck/`.
- Re-anchoring a long session that has drifted away from the cockpit.
- You want a clean, read-only starting point before delegating to other skills.

The protocol "textbook" (data model, folder semantics, routing, write gate, lifecycle) is in [protocol.md](protocol.md) — load it on demand; see the index at the bottom.

## Gate — model-invocation check (run before the checklist)

Resolve `preflight` self-invocability per [protocol § Rule resolution order](protocol.md#rule-resolution-order). **Default (3.0): self-invocable — continue.** Restricted only if House Rules say `preflight: don't self-invoke` (or a pre-3.0 deck omits `preflight` from `model_invocable`): then an explicit user `/flightdeck:preflight` → continue; model self-invocation or unknown call source → **STOP immediately** and report "`preflight` is manual-only (House Rule). Remove the `preflight: don't self-invoke` line to allow self-invoke." Branch-0 (deck existence) still runs first.

## Run this checklist exactly

0. **Branch-0 — deck existence (MUST run first; layout detection MUST NOT run before this).**
   Check whether **`flightdeck/cockpit.md` exists** (cockpit.md, not merely the directory — it is flightdeck's minimal contract, so this also covers a half-initialized `flightdeck/` that has no cockpit).

   - **`flightdeck/cockpit.md` does NOT exist** → **first-time setup**: load [setup.md](setup.md) and run it (git check → confirm → 2-Q interview → scaffold-copy via `flightdeck_init.py` or by hand → AGENTS.md opt-in → STOP).
   - **`flightdeck/cockpit.md` exists** → continue to step 1 (read path).

1. **Read `flightdeck/rules.md`** if present. Resolve config per [protocol § Rule resolution order](protocol.md#rule-resolution-order): infer git from deck root `.git` (House Rule `this deck doesn't use git` overrides) — when no-git, skip step 4's git reconcile entirely; honor `disabled_folders` (don't suggest them in fallback). Pre-3.0 keys, if present, are honored for compat.

2. **Migration detection (non-silent).** Compare `rules.md` `version` against `MIGRATION.md` (`current` + `layout_need_update`) and act per [protocol § Migration detection](protocol.md#migration-detection): `== current` → continue; `< a layout_need_update` entry → offer that migration ([MIGRATION.md](../../MIGRATION.md)); older-but-compatible → silently bump `version` to `current`; no `version`/`rules.md` → offer the pre-2.2 migration; legacy 1.x markers (`manifest.md`/`logbook.md`/`kneeboard/`/…) → 1.x migration first. **Never apply a *structural* migration silently — always ask; a compatible version bump is the one allowed silent stamp.**

   **Unmigrated model-v4 deck (structural signals beyond `version`).** Independently of the version compare, if the deck shows pre-model-v4 structure — a `sketches/` or `debriefs/` folder still present, or any workflow file carrying a retired status (`pending` / `awaiting-review` / `blocked`, or a sketch's `active`), or a `cockpit.md` with a hand-written `## Next session` and no `## 进行中` AUTO region — **surface it and offer the model-v4 migration** (point at the matching [MIGRATION.md](../../MIGRATION.md) section; the concrete step-by-step lives there). Trigger + point only — do not perform the moves/remaps here. Never silent.

3. **Read `flightdeck/INDEX.md`** (root INDEX) once, in full — it carries the global status summary (counts per folder). Then **read `flightdeck/cockpit.md`** once, in full — focus on `Last updated`, `Active focus`, the `## 进行中` AUTO region (the active set), and the `## 下一步` action. These two reads together are the reconcile baseline; read each once and treat as cached for the rest of the ritual (no need to re-open). `preflight` **reads** `## 进行中` / `## 下一步` but never rewrites them — a stale `## 下一步` is corrected at the next landing / status write point, not here.

4. **(skip entirely when no-git — deck root has no `.git`, or a House Rule says so) Reconcile against repo state — heuristic signals, not hard checks.** Gather independently (parallel where supported): `git branch --show-current`, `git status --short`, `git stash list`, `git log -1 --format=%cs` (no-git: newest `landed/HISTORY.md` entry). These are **fuzzy** — a branch name rarely equals an `Active focus` sentence, so only surface a **clear** divergence, never a guessed equality.

5. **When a signal looks clearly off — surface as a question, never auto-act** (one per real divergence): branch vs `Active focus`; tree clean but cockpit says in-progress ("did it ship?"); stash not on cockpit ("pick up / drop / note?"); `Last updated` > ~14 days behind newest commit ("cockpit may be stale — refresh first?"). No divergence → say nothing.

6. **Load the routing catalog** (know-what-exists, NOT read-all). Read the folder INDEX files — do NOT glob individual files or read per-file frontmatter:
   - Read `flightdeck/checklists/INDEX.md` — it already lists each checklist's `when_to_read`, `applies_to`, and `status`.
   - Read `flightdeck/incidents/INDEX.md` — same structure for incident files.
   - If either INDEX is missing or obviously stale (file count in INDEX differs from root INDEX count), note it: "⚠ `<folder>/INDEX.md` missing or stale — walkaround owns the fix." This is non-blocking.
   - **Do NOT read individual checklist or incident files** at catalog time. The folder INDEX is the catalog. Only drill into an individual file when a trigger actually matches the current task (i.e. at execution time, not preflight time).
   - **`charts/` is deliberately out of the auto-routing catalog** — even though its files may carry `when_to_read`/`applies_to`, imported external material is browsed on purpose (the "need outside perspective" scenario), not surfaced every preflight, and a chart may be a large imported tree. `walkaround` still audits it.

7. **Status sanity (loaded folders only).** For the catalog folders just read (`checklists/`, `incidents/`), flag any INDEX row with a missing or illegal `status` for its kind (legal values: [protocol § Status](protocol.md#status-label--recommended-flow)). List all findings, then offer once "Fix all flagged?" — don't fix until confirmed. Global per-file audits across all folders belong to `walkaround`.

8. **All reconciled → report item #1, then STOP.** Read-only recon doesn't fly the mission. State the item in one sentence and hand off: "Preflight complete (read-only). Say 'go' to execute item #1." Do not load any file body or start the task — that's the next turn.

   **Land-readiness (signal 2), as the FINAL output line / a dedicated `## Land-readiness` block** (never mid-report): run the [Land-readiness check](exit-ritual.md#land-readiness-check) — if `git status` shows **≥ 5** changed files under `flightdeck/` (skip entirely under no-git), append "⚠ N unlanded changes since last land — consider `/flightdeck:landing`". Below the threshold, say nothing.

## Fallback when `## 下一步` is empty

Don't auto-start anything. Search in order (a missing directory counts as empty), present candidates to the user:

1. `flightdeck/plans/` — surface `active` plans (read `plans/INDEX.md`), most actionable first; a `done`-but-unlanded plan → offer to land it.
2. `flightdeck/specs/` — `active` designs not yet turned into a plan (read `specs/INDEX.md`); ask which to plan next.
3. `flightdeck/specs/` **to-start pool** — `status: idea` specs (the `待启动（idea）` group in `specs/INDEX.md`); ask which (if any) to start (flip `idea → active`). Ideas are *not* orphans and not in cockpit — this fallback is their surfacing point.

> **Done-but-unlanded (any folder):** an artifact whose `status: done` but which still sits in its source folder (not yet under `landed/`) is *done-but-unlanded* — the `status` skill produces these when its `land` confirm is declined. Offer to land it via the [Land Routine](exit-ritual.md#land-routine). This applies to `specs/`, `plans/`, and any workflow folder, not just plans.

## Output format

Report concisely:

```
Root INDEX: specs/ — 2 (1 active, 1 done) | plans/ — 1 active | incidents/ — 1 active | checklists/ — 2 active
Cockpit reconciled (Last updated: 2026-05-25; Active focus: <X>; tree clean)

Routing catalog (from folder INDEX files — know-what-exists, not read-all):

[Checklists]
| File | when_to_read | applies_to | status |
|---|---|---|---|
| checklists/comments.md | before writing or editing any source-code comment | comments, code-style | active |

[Incidents]
| File | when_to_read | applies_to | status |
|---|---|---|---|
| incidents/parser-recursion.md | before designing a recursive parser | parser, recursion | active |

[Catalog notes]  (omitted when clean)
- ⚠ incidents/INDEX.md missing — walkaround owns the fix

下一步 (item #1): <item description>

Preflight complete (read-only). Catalog is know-what-exists only — NOT a substitute for /flightdeck:walkaround, and does not mean these files were read. Bodies load on demand, when execution begins and a trigger matches.

→ Say "go" to execute item #1.
```

Omit any table group with no entries. If both folder INDEX files are absent or empty, print `Routing catalog: (empty — no routed resources yet)`.

Or if blocked:

```
Reconcile flagged:
- <mismatch 1>
- <mismatch 2>

Resolve which?
```

## Don't do

- Don't auto-pick a fallback when `## 下一步` is empty — always ask.
- Don't bump `Last updated` — entry doesn't modify cockpit (first-time setup is the one exception).
- Don't grep the codebase for "things to do" — cockpit.md is authoritative.
- Don't drill into individual files until a trigger matches at execution time (read folder INDEX only).

## Protocol knowledge (load on demand)

The operational entry ritual is above. The protocol "textbook" lives in companions — read on demand:

- [setup.md](setup.md) — first-time setup (run by Branch-0 when no deck exists)
- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle · promotion gates · common mistakes
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout (full, always)
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — the landing ritual (run by `/flightdeck:landing`) + Land-readiness check
