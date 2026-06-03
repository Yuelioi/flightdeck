---
current: 3.0
layout_need_update: [2.2, 3.0]   # releases requiring a deck migration; deck.version < any listed (or no version) → non-silent migration offer
---

# Migration

This document records breaking migrations for the maintainer's reference.

> **Migration detection reads this frontmatter.** `current` = latest release; `layout_need_update` = releases that changed deck structure. `preflight`/`walkaround` compare a deck's `rules.md` `version` against it: version below any `layout_need_update` entry (or no `version` at all) → non-silent migration offer; otherwise preflight silently bumps the deck's `version` to `current`. (Replaces the old cockpit `**Layout**` string check.)

## 2.3 → 3.0 — rules.md simplification (BREAKING)

3.0 dissolves the structured toggle set. `rules.md` keeps only `version` + `disabled_folders` + free-prose House Rules; `git`/`emit_agents_md` become **environment inference**, and `commit`/`model_invocable`/`status_auto` become **defaults overridable via the House-Rules `### Autonomy overrides` segment**. See [protocol § Rule resolution order](skills/preflight/protocol.md#rule-resolution-order).

**Compatibility:** pre-3.0 keys are **read and honored through all of 3.x**; removed at 4.0.

**Migration (`preflight` offers it; never silent):** on a deck with `version < 3.0` or any removed key still present, `preflight` proposes rewriting `rules.md`:

1. Set `version: 3.0`, keep `disabled_folders`.
2. Translate each **non-default** removed value into a House-Rules `### Autonomy overrides` standard phrase (canonical English), each prefixed with a `<!-- migrated from <key>:<value> -->` provenance comment (never delete the comment — it shows provenance).
3. Drop keys left at their default (they're now the default — nothing to carry).

**Translation table** (non-default → standard phrase):

| Removed key/value | House Rule (`### Autonomy overrides`, canonical English) |
|---|---|
| `commit_mode: auto` | `commit without asking` |
| `commit_mode: manual` | `don't auto-commit; leave changes for me / CI` |
| `model_invocable` omits a ritual | `<ritual>: don't self-invoke; I run it manually` |
| `status_auto` omits `start`/`land` | `status: don't auto <transition>` |
| `git: false` | `this deck doesn't use git; history in landed/HISTORY.md` |
| `emit_agents_md: false` **and** deck has `AGENTS.md` | `has AGENTS.md but don't auto-regen` |
| `emit_agents_md: false` **and** no `AGENTS.md` | (drop — inference already equivalent; **expected**, not a lost-config bug) |
| `disabled_gates: [...]` | (drop — removed in 3.0; if genuinely used, convert per-gate to prose or keep a warning) |

After rewriting, **reinstall/sync the plugin-cache copy** to load the 3.0 skills.

## 2.2 → 2.3 — autonomy defaults + `commit_mode` (additive, no migration)

2.3 is **purely additive**. Existing decks need no changes — `preflight` silently bumps `rules.md` `version` 2.2 → 2.3 on entry (2.3 is not in `layout_need_update`, so no prompt).

| Area | Affected? |
|---|---|
| `commit_mode` toggle | **New** — optional; default `confirm` = the pre-2.3 behavior (ask before committing) |
| New-deck scaffold / first-time-setup | **Changed** — now writes full-auto `model_invocable` / `status_auto` + `commit_mode: confirm` |
| Gate fallback (absent / empty `model_invocable`) | **No** — still manual; existing and hand-made decks unaffected |
| existing toggles / contract | **No** — `git` / `emit_agents_md` / `disabled_*` / `model_invocable` / `status_auto` unchanged |

**To adopt on an existing deck (optional):** add `commit_mode:` and/or expand `model_invocable` / `status_auto` in `flightdeck/rules.md`. Nothing is required. Reinstall/sync the plugin-cache copy to load the updated skills.

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

> **Note (frontmatter enrichment):** 2.2 also adds the recommended workflow fields `summary` / `last_updated` and the optional edges `supersedes` / `related`. These are optional and need no migration — **except**: if your existing `INDEX.md` rows carry hand-written summaries, backfill `summary:` into each artifact's frontmatter **before the next `landing`/`status` run**. Those rituals regenerate the `<!-- AUTO -->` rows purely from frontmatter, so a row whose file has no `summary` loses its summary segment (the hand-written text is not preserved).

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
