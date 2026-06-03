---
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — the single entry point. Initializes `flightdeck/` when absent (no cockpit.md); otherwise reconciles cockpit.md against repo state via root INDEX.md, loads a routing catalog from folder INDEX files, and reports the first "next session" item. Triggered by `/flightdeck:preflight`.
---

# Flightdeck Preflight

The **single explicit entry point** for flightdeck. Nothing loads on its own — you run `/flightdeck:preflight` at the start of a working session. It either **initializes** a new `flightdeck/` (when none exists) or **reconciles** the existing one against repo state and **reports** the next item, then stops. It does not execute the item; that's the next turn's job. Use it when:

- Starting a working session in a project that has (or should have) a `flightdeck/`.
- Re-anchoring a long session that has drifted away from the cockpit.
- You want a clean, read-only starting point before delegating to other skills.

The protocol "textbook" (data model, folder semantics, routing, write gate, lifecycle) is in [protocol.md](protocol.md) — load it on demand; see the index at the bottom.

## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` and resolve per [protocol § Rule resolution order](protocol.md#rule-resolution-order). **Default (3.0): `preflight` is self-invocable** — continue.

- **Restricted** only if House Rules `### Autonomy overrides` says `preflight: don't self-invoke; I run it manually` (or a pre-3.0 deck's `model_invocable` list omits `preflight`):
  - explicit user `/flightdeck:preflight` (e.g. a `<command-name>` marker) → allowed; continue.
  - model self-invocation, or you cannot tell the call source → **STOP immediately.** Report: "`preflight` is manual-only in this project (House Rule). Remove the `preflight: don't self-invoke` line to allow model self-invoke." Run no further step.

(Tool-agnostic — ships to every platform via this body. See the adapter READMEs for per-platform formal/degraded mode.) Once past this gate, the checklist's **Branch-0 (deck existence) still runs first** within the ritual.

## Run this checklist exactly

0. **Branch-0 — deck existence (MUST run first; layout detection MUST NOT run before this).**
   Check whether **`flightdeck/cockpit.md` exists** (cockpit.md, not merely the directory — it is flightdeck's minimal contract, so this also covers a half-initialized `flightdeck/` that has no cockpit).

   - **`flightdeck/cockpit.md` does NOT exist** → run **First-time setup**:
     1. **git check** — does the deck root (cwd) contain `.git`? If **no**: tell the user "no git here — flightdeck still works, but staleness/history fall back to `landed/HISTORY.md`", and **offer to run `git init`? (y/N)**. If yes, run it. (Non-blocking either way.)
     2. Ask: **"Create a flightdeck deck here? (full layout + 3-file contract)"** — wait for confirmation.
     3. **Copy the scaffold verbatim** from this skill's `../../scaffolds/full/flightdeck/` (resolve relative to this skill's base directory; the plugin packages `scaffolds/`) into `./flightdeck/` — every folder + each `INDEX.md` + the **commented** `rules.md` + `cockpit.md` + `landed/HISTORY.md`. **Copy, do NOT re-author** — this is what preserves the `rules.md` comments. Then substitute today's date + `<user>` into `cockpit.md`; the scaffold `rules.md` `version` should equal `MIGRATION.md` `current` — bump it if the scaffold is behind.
     4. **Interview (2 Q)** → replace the cockpit placeholders: "Active focus — current main thread (5–15 words)?" → replace `<ACTIVE_FOCUS …>`; "First 'next session' item — one concrete action?" → replace `<FIRST_NEXT_ITEM …>`.
     5. **AGENTS.md** — ask "Generate `AGENTS.md` (cross-tool bridge from cockpit)? (Y/n)". If yes, run `/flightdeck:emit-agents-md`. (Opt-in; creating it now is the bootstrap — matches the 3.0 emit-on-presence rule.)
     6. **Tutorial** — ask "Run a 2-minute guided tour? It creates a throwaway sample and cleans it up. (y/N)". If yes, follow [onboarding.md](onboarding.md); if no, skip.
     7. **Then STOP** — the next `/preflight` takes the read path below.
   - **`flightdeck/cockpit.md` exists** → continue to step 1 (read path).

1. **Read `flightdeck/rules.md`** if present. Resolve config per [protocol § Rule resolution order](protocol.md#rule-resolution-order): infer git from deck root `.git` (House Rule `this deck doesn't use git` overrides) — when no-git, skip step 4's git reconcile entirely; honor `disabled_folders` (don't suggest them in fallback). Pre-3.0 keys, if present, are honored for compat.

2. **Check version (migration detection; non-silent on mismatch).** Read `flightdeck/rules.md` `version` + `MIGRATION.md` frontmatter (`current` + `layout_need_update`); apply [protocol.md § Migration detection](protocol.md#migration-detection):

   - **`version == current`** → up to date; continue silently (report nothing).
   - **`version` < some `layout_need_update` entry** → "deck on `<version>`, migration `<v>` applies — migrate now?"; follow the matching [MIGRATION.md](../../MIGRATION.md) section; do not proceed until the user decides.
   - **`version` < `current`, no newer `layout_need_update` entry** → silently bump `rules.md` `version` to `current`; continue.
   - **No `version` / no `rules.md`** (pre-2.2 deck, incl. a cockpit-only deck) → "pre-2.2 deck detected — run the 2.2 migration? (create `rules.md` with `version`, ensure `landed/HISTORY.md`, drop the cockpit `**Layout**` line)" per [MIGRATION.md](../../MIGRATION.md). If legacy 1.x markers exist (`manifest.md`/`logbook.md`/`kneeboard/`/`flight-plans/`/`incident-reports/`/`safety-reviews/`), route to the 1.x→1.2 migration first.

   Never migrate (or stamp) silently — always ask the user first.

3. **Read `flightdeck/INDEX.md`** (root INDEX) once, in full — it carries the global status summary (counts per folder). Then **read `flightdeck/cockpit.md`** once, in full — focus on `Last updated`, `Active focus`, and the `## Next session` section. These two reads together are the reconcile baseline; do not re-read either during the ritual.

4. **(skip entirely when no-git — deck root has no `.git`, or a House Rule says so) Reconcile against repo state.** Run these checks independently (in parallel where supported):
   - `git branch --show-current` — matches `Active focus` in cockpit?
   - `git status --short` — does the first "Next session" item show up as in-progress files?
   - `git stash list` — any entries not mentioned in cockpit?
   - `git log -1 --format=%cs` — is `Last updated` more than ~14 days behind the most recent commit? (When no-git, compare against the newest `landed/HISTORY.md` entry instead.)

   Cross-check cockpit's `## Next session` against reality (branch, tree state). Flag any mismatch.

5. **Mismatch handling** — **always ask the user before acting**:
   - If branch differs: "Cockpit says focus is X but branch is Y — which is current?"
   - If `git status` is clean but cockpit says in-progress: "Cockpit flags 'X in progress' but tree is clean — did it ship?"
   - If stash exists not in cockpit: "Stash entry from <date> not on cockpit — pick up, drop, or note?"
   - If cockpit > 14 days stale: "Cockpit last updated <date>, most recent commit <date>. Cockpit may be stale — refresh first?"

6. **Load the routing catalog** (know-what-exists, NOT read-all). Read the folder INDEX files — do NOT glob individual files or read per-file frontmatter:
   - Read `flightdeck/checklists/INDEX.md` — it already lists each checklist's `when_to_read`, `applies_to`, and `status`.
   - Read `flightdeck/incidents/INDEX.md` — same structure for incident files.
   - If either INDEX is missing or obviously stale (file count in INDEX differs from root INDEX count), note it: "⚠ `<folder>/INDEX.md` missing or stale — walkaround owns the fix." This is non-blocking.
   - **Do NOT read individual checklist or incident files** at catalog time. The folder INDEX is the catalog. Only drill into an individual file when a trigger actually matches the current task (i.e. at execution time, not preflight time).

7. **Status sanity (from INDEX).** Scan each folder INDEX row for a missing `status` or an illegal status value for that folder's kind; report and offer to fix, non-silent. (Deeper file audits belong to walkaround.)

   Valid status values by folder:
   - Workflow folders (`sketches/`, `specs/`, `plans/`): `pending / active / awaiting-review / blocked / done / scrapped` (sketches: typically only `active / scrapped`)
   - Knowledge folders (`incidents/`, `checklists/`, `charts/`, `debriefs/`): `active / obsolete / superseded`

   List all findings before offering fixes. Offer once: "Fix all flagged files?" — do not fix any until the user confirms.

8. **All reconciled → report item #1, then STOP.** Read-only recon doesn't fly the mission. State the item in one sentence and hand off: "Preflight complete (read-only). Say 'go' to execute item #1." Do not load any file body or start the task — that's the next turn.

   **Land-readiness (signal 2), as the FINAL output line / a dedicated `## Land-readiness` block** (never mid-report): run the [Land-readiness check](exit-ritual.md#land-readiness-check) — if `git status` shows **≥ 5** changed files under `flightdeck/` (skip entirely under no-git), append "⚠ N unlanded changes since last land — consider `/flightdeck:landing`". Below the threshold, say nothing.

## Fallback when "Next session" is empty

Don't auto-start anything. Search in order (a missing directory counts as empty), present candidates to the user:

1. `flightdeck/plans/` — surface `pending` / `blocked` / `active` plans (read `plans/INDEX.md`), most actionable first; a `done`-but-unlanded plan → offer to land it.
2. `flightdeck/specs/` — `active` / `pending` designs not yet turned into a plan (read `specs/INDEX.md`); ask which to plan next.
3. `flightdeck/sketches/` — unstarted ideas (read `sketches/INDEX.md`); ask which (if any) to promote to a spec.

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

Next session item #1: <item description>

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

- Don't run the layout check (step 2) before the deck-existence check (step 0).
- Don't auto-execute item #1 — report and stop.
- Don't auto-pick a fallback when `Next session` is empty — always ask.
- Don't bump `Last updated` — entry doesn't modify cockpit (the First-time-setup write is the one exception).
- Don't glob individual checklist/incident files or read per-file frontmatter for the catalog — read folder INDEX files only.
- Don't drill into individual files until a trigger matches at execution time.
- Don't grep the codebase for "things to do" — cockpit.md is authoritative.
- Don't migrate (or initialize, or stamp) silently — always ask the user first.

## Protocol knowledge (load on demand)

The operational entry ritual is above. The protocol "textbook" lives in companions — read on demand:

- [protocol.md](protocol.md) — data model · status · INDEX · folder map · routing · authority order · write gate · lifecycle · promotion gates · common mistakes
- [folder-semantics.md](folder-semantics.md) — what each folder holds; deck layout (full, always)
- [templates.md](templates.md) — per-file frontmatter + cockpit / rules.md / INDEX templates
- [exit-ritual.md](exit-ritual.md) — the landing ritual (run by `/flightdeck:landing`) + Land-readiness check
- [onboarding.md](onboarding.md) — optional first-run guided tour (demonstration; auto-cleaned)
