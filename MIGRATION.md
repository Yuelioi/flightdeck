---
current: 2.2
layout_need_update: [2.2]   # releases requiring a deck migration; deck.version < any listed (or no version) → non-silent migration offer
---

# Migration

This document records breaking migrations for the maintainer's reference.

> **Migration detection reads this frontmatter.** `current` = latest release; `layout_need_update` = releases that changed deck structure. `preflight`/`walkaround` compare a deck's `rules.md` `version` against it: version below any `layout_need_update` entry (or no `version` at all) → non-silent migration offer; otherwise preflight silently bumps the deck's `version` to `current`. (Replaces the old cockpit `**Layout**` string check.)

## 2.1 → 2.2 — version stamp moves into rules.md (rules.md now mandatory)

2.2 relocates the deck-conformance version out of `cockpit.md`'s `**Layout**` line into a **mandatory** `flightdeck/rules.md` `version:` field, and makes `rules.md` part of the **minimal 3-file contract** (`rules.md` + `cockpit.md` + `landed/HISTORY.md`).

| Area | Affected? |
|---|---|
| `cockpit.md` `**Layout**` line | **Yes** — removed; version lives in `rules.md` now |
| `rules.md` | **Yes** — now mandatory; must carry `version` |
| `landed/HISTORY.md` | **Yes** — now part of the minimal contract (create if absent) |
| existing toggles / behavior | **No** — git / emit / disabled_* / model_invocable / status_auto unchanged |

**Migration (interactive, non-silent, idempotent)** — on a deck with no `rules.md` `version` (or `version` < 2.2):
1. Create `rules.md` if absent (defaults + `version: <current>`).
2. Add/refresh `version`.
3. Remove the `**Layout**` line from `cockpit.md`.
4. Ensure `landed/HISTORY.md` exists.

Each step skips if already done.

## 2.0 → 2.1 — model_invocable soft gate + status ritual

2.1 is **additive and opt-in** — nothing breaks. `flightdeck/` Layout stays 1.2, existing decks need no changes, and default behavior is identical to 2.0.

| Area | Affected? |
|---|---|
| deck data / `**Layout**` / `cockpit.md` | **No** — Layout stays 1.2 |
| existing slash commands | **No** — still manual by default |
| new automation | **Opt-in** via `flightdeck/rules.md` (see below) |

What's new (all default-off):

- The four entry skills (`preflight` / `landing` / `walkaround` / `emit-agents-md`) dropped the global `disable-model-invocation` hard switch for a per-project soft gate. Default `model_invocable: []` = all manual (identical to before). Opt a ritual into model self-invocation: `model_invocable: [landing]`.
- New 5th ritual `/flightdeck:status` auto-flips one artifact's lifecycle status. Self-invocation requires `model_invocable: [status]`; which *optional* transitions fire is controlled by `status_auto: [start, land]` (default `[]` = only `create→pending` / `finish→awaiting-review`).

**Action required:** none, unless you want the new automation — then add the opt-in keys to `flightdeck/rules.md`. After upgrading the plugin, **reinstall/sync the plugin-cache copy** so the new `status` ritual and keys load.

## 1.3 → 2.0 — single explicit entry

2.0 removes the auto-loaded `workflow` skill and the SessionStart hook. The entry is now a single explicit command, `/flightdeck:preflight` (it initializes `flightdeck/` when there is no `cockpit.md`, otherwise reconciles and reports).

| Area | Affected? |
|---|---|
| deck data / `**Layout**` / `cockpit.md` | **No** — your `flightdeck/` needs no changes (Layout stays 1.2) |
| slash command (`/flightdeck:workflow`) | **Yes** — removed; use `/flightdeck:preflight` |
| auto-load (SessionStart injection) | **Yes** — gone; nothing loads on session start |

**Action required:** users who relied on automatic SessionStart loading must explicitly run `/flightdeck:preflight` at the start of a working session — otherwise nothing happens on session start ("升级后怎么没反应了" is the expected-but-avoidable surprise). Why delete instead of merge: the auto-load duplicated preflight's reconcile (a double-run, not a complement) and the two entries had already drifted into different behavior (e.g. different empty-`Next session` fallbacks).

Protocol knowledge moved into `skills/preflight/` (`protocol.md` + the relocated `folder-semantics.md` / `templates.md` / `exit-ritual.md`). No user action — internal to the plugin.

## 1.1.x → 1.2

1.2 keeps the 1.x worldview (sketch / spec / plan / incident / checklist / chart / debrief) and adds two things: **explicit `status` metadata** on every artifact, and a **per-folder + root `INDEX.md`** derived index. `preflight`/`walkaround` detect the old layout (any of `manifest.md`, `logbook.md`, `kneeboard/`, `flight-plans/`, `incident-reports/`, `safety-reviews/`) and offer this **interactive, non-silent, idempotent** migration (each step skips if already done; unknown fields preserved):

1. **`manifest.md`** → fold non-trivial rows into `cockpit.md` (Active focus / Next session / Hanging tasks) or drop; delete `manifest.md`.
2. **`logbook.md`** → import `Recently finished` into `landed/HISTORY.md` (newest first); move `Deferred` to `sketches/` or `cockpit.Next session`; delete `logbook.md`.
3. **`kneeboard/`** → classify each file into a folder or delete; remove the empty dir. Session scratch now lives in project-root `tmp/` (gitignored).
4. **`flight-plans/` → `plans/`**. Each file: add `status:`; optionally add `implements: specs/<x>.md`.
5. **`incident-reports/` → `incidents/`**. Add `status:` (keep `when_to_read`/`applies_to`/`last_updated`).
6. **`safety-reviews/` → `debriefs/`**. Add `status:` + `reviewed: specs/<x>.md` + `last_updated` (no `when_to_read`/`applies_to`).
7. **`specs/` stays.** Add `status:` to each file.
8. **`checklists/` / `charts/` stay.** Add `status:` (knowledge folders keep their routing fields).
9. **`sketches/` stays.** Add `status: active` (or `scrapped`).
10. **Build `INDEX.md`** for every artifact folder + a root `flightdeck/INDEX.md` (the `<!-- AUTO -->` region derived from each file's frontmatter).
11. **cockpit**: drop any `## In flight` / `## Blockers`; pure focus (Active focus / Next session / Hanging tasks).
12. **Optional:** create `rules.md` for toggles.

### Old → new mapping

| 1.1.x | 1.2 |
|---|---|
| `manifest.md` | folded into `cockpit.md` (or dropped) |
| `logbook.md` | `landed/HISTORY.md` (+ `sketches/` for Deferred) |
| `kneeboard/` | removed; scratch → project-root `tmp/` |
| `flight-plans/` | `plans/` (+ `status`, + optional `implements`) |
| `incident-reports/` | `incidents/` (+ `status`) |
| `safety-reviews/` | `debriefs/` (+ `status`, + `reviewed`) |
| `specs/` | `specs/` (+ `status`) |
| `checklists/` / `charts/` / `sketches/` | unchanged paths (+ `status`) |
| location-implicit state | explicit `status:` field |
| (no index) | per-folder `INDEX.md` + root `flightdeck/INDEX.md` |
