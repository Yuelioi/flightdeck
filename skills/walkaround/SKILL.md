---
name: walkaround
description: Use when explicitly invoking the flightdeck integrity audit — checks cockpit.md / rules.md / sketches / specs / plans / incidents / checklists / charts / debriefs for status validity, INDEX↔folder consistency, orphan plans, dangling references, stray files, AGENTS.md drift, layout-version / legacy 1.x paths, and (INFO) missing workflow summary/last_updated + dangling supersedes/related edges. Triggered by `/flightdeck:walkaround`.
---

# Flightdeck Walkaround

User-triggered integrity audit of a flightdeck for protocol drift. The protocol is markdown + filesystem conventions; drift is the silent killer of advice systems. Walkaround surfaces drift loudly so the author can fix it. Implemented as a slash skill (markdown checklist the AI follows), NOT a CLI binary, to preserve flightdeck's plain-markdown + git bet.

## When to invoke

- Periodically (e.g., before a release commit, weekly during active work).
- After a long absence from the project — drift accumulates silently.
- When something feels off (cockpit doesn't match reality, checklists unread, AGENTS.md stale).
- Before promoting flightdeck conventions to a downstream project — walkaround should be clean on the source.

## Severity legend

- **CRITICAL** — protocol contract broken (e.g., artifact missing required frontmatter, dangling internal reference). Fix before proceeding with new work.
- **WARNING** — drift that will accumulate (e.g., stale INDEX rows, missing routing fields, legacy paths). Fix soon, before the next release.
- **INFO** — heads-up that may or may not need action (e.g., orphan plan with no `implements`, stale `awaiting-review`). Judge per item.

## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` and look at its `model_invocable` list (absent key or `[]` = empty).

- If **`walkaround` is in `model_invocable`** → allowed; continue this ritual normally.
- Else (`walkaround` not listed):
  - If you can tell this run was an **explicit user `/flightdeck:walkaround`** invocation (e.g. the platform injected a `<command-name>` marker for it) → allowed; continue.
  - Otherwise — you reached this skill by **model self-invocation** (skill tool), **or you cannot tell the call source** → **STOP immediately.** Report: "`walkaround` is manual-only in this project. To let the model self-invoke it, add `model_invocable: [walkaround]` to `flightdeck/rules.md`." Run no further step.

This gate defaults to manual-only: with no `model_invocable` key, behavior is identical to the former `disable-model-invocation: true`. (Tool-agnostic — ships to every platform via this body. See the adapter READMEs for per-platform formal/degraded mode.)

## Audits

Run all 12 in order. First read `flightdeck/rules.md` if present: honor `disabled_folders` (do not flag a disabled folder as orphan/stray) and `disabled_gates` (do not flag a disabled gate). For each, report findings with the severity tag.

**Field validity is governed by [protocol.md § Frontmatter field reference](../preflight/protocol.md#frontmatter-field-reference-canonical)** — that table is the source of truth for which fields are required per kind. The audits below check against it; if they disagree, the canonical table wins.

### 1. Frontmatter status validity (CRITICAL / WARNING)

**Folder = kind (implicit); `status` = the only required frontmatter field.** Audit `status` only here; no other frontmatter field is *required* for workflow artifacts. (The recommended workflow fields `summary` / `last_updated` and the optional relation edges `supersedes` / `related` get soft INFO checks in Audits 11–12, never CRITICAL/WARNING.)

#### Workflow artifacts (`sketches/`, `specs/`, `plans/`) — NOT in `landed/`

For each `.md` file in these folders:

- MUST carry `status`. Missing: **CRITICAL**.
- Legal values:
  - `sketches/`: `active` / `scrapped` only.
  - `specs/` and `plans/`: `pending` / `active` / `awaiting-review` / `blocked` / `done` / `scrapped`.
- Present but illegal value: **WARNING**.

#### Knowledge artifacts (`incidents/`, `checklists/`, `charts/`, `debriefs/`) — NOT in `landed/`

For each `.md` file in these folders (excluding `INDEX.md`; `charts/` may contain external project trees — audit only top-level `.md` files directly under `charts/`, not the external tree):

- MUST carry `status`. Missing: **CRITICAL**.
- Legal values: `active` / `obsolete` / `superseded`.
- Present but illegal value: **WARNING**.

### 2. Knowledge routing fields (WARNING)

For each knowledge artifact NOT in `landed/`:

- Files in `incidents/`, `checklists/`, `charts/`: MUST carry `when_to_read` + `applies_to` + `last_updated`. Any missing: **WARNING** — file is invisible to flightdeck routing.
- Files in `debriefs/`: MUST carry `reviewed` + `last_updated`. Any missing: **WARNING**. (`debriefs/` does NOT use `when_to_read` / `applies_to`.)
- Malformed values (e.g. `last_updated: potato`, empty `when_to_read`): **WARNING**.

Workflow artifacts (`sketches/`, `specs/`, `plans/`) are **out of scope here** — they carry no required routing fields. Their recommended `summary` / `last_updated` are checked at INFO in Audit 11.

### 3. `superseded` needs `superseded_by` (WARNING)

For each knowledge artifact with `status: superseded` (NOT in `landed/`):

- MUST carry `superseded_by` pointing to the replacing file. Missing or empty: **WARNING** — superseded artifact has no forward pointer; readers cannot find the replacement.
- If `superseded_by` is present but the pointed-to file does not exist on disk: **WARNING** — broken `superseded_by` reference.

### 4. Orphan plan (INFO)

For each file in `plans/` (NOT in `landed/`) with no `implements:` frontmatter field:

- **INFO** — consider linking a spec via `implements: specs/<x>.md`, or confirm this plan is intentionally standalone.

Do not flag files that carry `implements:` even if the target is also missing (that is caught by Audit 7 — dangling references).

### 5. INDEX ↔ folder consistency (WARNING)

For each artifact folder (`sketches/`, `specs/`, `plans/`, `incidents/`, `checklists/`, `charts/`, `debriefs/`):

- If the folder has no `INDEX.md`: **WARNING** — missing per-folder INDEX.
- Read the `<!-- AUTO -->` block in the folder's `INDEX.md`. Each row should list one file with its `status` (and other displayed metadata). Check:
  - A real file exists with no corresponding row: **WARNING** — missing INDEX row.
  - A row exists for a file not on disk: **WARNING** — stale INDEX row (ghost).
  - A row's displayed `status` does not match the file's actual frontmatter `status`: **WARNING** — out-of-sync status in INDEX. (Exception: `charts/` rows show project/file count, not per-file status — do not flag `charts/` for missing status values.)
- For the root `flightdeck/INDEX.md`:
  - If absent: **WARNING** — missing root INDEX.
  - Each per-folder summary line's counts (e.g. `specs/ — 3 (2 active, 1 done)`) must match the actual file counts and status distribution in that folder. Mismatch: **WARNING**. (Again, `charts/` is exempt from status counting.)

### 6. `landed/` has no non-terminal status (WARNING)

For each `.md` file under `landed/` that carries a `status` field:

- Workflow files (`landed/sketches/`, `landed/specs/`, `landed/plans/`): status must be `done` or `scrapped`. Any other value: **WARNING**.
- Knowledge files (`landed/incidents/`, `landed/checklists/`, `landed/charts/`, `landed/debriefs/`): status must be `obsolete` or `superseded`. Any other value: **WARNING**.

### 7. Dangling internal references (CRITICAL)

For each markdown file under `flightdeck/` and every `*.md` at repo root:

- Extract all markdown links matching `[text](path)` where `path` is NOT an HTTP/HTTPS URL and NOT an anchor-only (`#...`).
- For each link, strip any `#fragment` suffix, then resolve the path relative to the file's directory. Verify the **file** exists only — do not validate anchors.
- If the file is missing: **CRITICAL** — broken cross-reference. Report the source file:line + the broken target path.

### 8. Orphan / stray files (WARNING)

Known folders: `sketches/` `specs/` `plans/` `incidents/` `checklists/` `charts/` `debriefs/` `landed/`. Known root entries: `cockpit.md` `INDEX.md` `rules.md`.

- A `.md` directly under `flightdeck/` that is not a known entry file and not linked from any known entry: **WARNING** — orphan; either link it from an entry or remove it.
- A `.md` in a known folder that is neither a valid artifact file nor an `INDEX.md`: **WARNING** — stray file with no clear role.
- A non-`.md` file under `flightdeck/` that no folder semantics cover: **WARNING**. Asset files (`.png` `.svg` `.json` `.yaml` etc.) under a folder that expects them (e.g. `charts/`) are fine — do not flag those.
- `charts/` may hold an external project tree — files nested inside `charts/<project>/` are not stray. Only top-level unrecognized files directly under `flightdeck/` or directly under a non-`charts/` folder are flagged.

**First run note**: on an existing project, Audit 8 may list many items at once. Advise gradual cleanup, not a forced all-at-once sweep.

### 9. AGENTS.md drift (WARNING)

If `AGENTS.md` exists at repo root with flightdeck markers (`<!-- BEGIN: flightdeck -->` / `<!-- END: flightdeck -->`):

- Extract the source fields from `cockpit.md`: Active focus, Next session, Hanging tasks.
- Read the same fields as currently rendered inside the `AGENTS.md` flightdeck block.
- Compare field by field (actual values, not overall impression). Any source value absent from or different in the block: **WARNING** — `emit-agents-md` hasn't been re-run since the source changed. Name the diverging field.

If `AGENTS.md` doesn't exist or has no flightdeck markers: skip (the project hasn't dogfooded the emitter yet; that's optional).

### 10. Version / migration detection (CRITICAL / WARNING / INFO)

Read `flightdeck/rules.md` `version` + `MIGRATION.md` frontmatter (`current` + `layout_need_update`); apply [protocol.md § Migration detection](../preflight/protocol.md#migration-detection).

- **No `flightdeck/rules.md`, or `rules.md` has no `version`** → **CRITICAL** — `rules.md` + `version` are part of the minimal 3-file contract. (A cockpit-only / pre-2.2 deck → point to the 2.2 migration in [MIGRATION.md](../../MIGRATION.md).)
- **`version` < some `layout_need_update` entry** → **WARNING** — a structural migration applies; point to the matching [MIGRATION.md](../../MIGRATION.md) section.
- **Legacy 1.x markers present** (`flightdeck/manifest.md` · `logbook.md` · `kneeboard/` · `flight-plans/` · `incident-reports/` · `safety-reviews/`) → **WARNING** — legacy 1.x deck; route to the 1.x→1.2 migration first.
- **A stray `**Layout**` line still in `cockpit.md`** → **INFO** — leftover from a pre-2.2 deck; the 2.2 migration removes it (version lives in `rules.md` now).
- **`version` < `current` but no newer `layout_need_update` entry**, or **`version == current`** → pass; report nothing (preflight silently bumps the compatible-but-behind case).

Only report once per path — do not also flag these as stray/orphan in Audit 8.

### 11. Workflow recommended fields (INFO)

For each workflow artifact (`sketches/`, `specs/`, `plans/`) NOT in `landed/`:

- Missing `summary`: **INFO** — the artifact's INDEX row carries no summary; consider adding one (it drives the row and survives into `landed/`).
- Missing `last_updated`: **INFO** — staleness can't be judged; the next `status`/`landing` flip auto-adds it.

These are **recommended, not required** — never escalate to WARNING/CRITICAL (that would flood pre-enrichment decks). Sketches commonly lack `last_updated`; INFO is enough.

### 12. Dangling relation edges (INFO)

For each workflow artifact NOT in `landed/` carrying `supersedes:` or `related:`:

- Resolve each path value relative to the flightdeck root. If the target exists **neither in the active tree nor under `landed/`**: **INFO** — dangling relation edge (target deleted or never existed). An edge that points into `landed/` is normal (the Land Routine rewrites edges to the `landed/` prefix on archive) — do NOT flag it.
- This checks frontmatter edge **values** only; prose `[text](path)` links are Audit 7's job (`supersedes`/`related` are not markdown links). `superseded_by` is knowledge-only and stays in Audit 3 — Audit 12 does not touch it.

## Output format

```
=== /flightdeck:walkaround report ===
Audit run: <ISO date>
Flightdeck root: <path>

CRITICAL findings (N):
  - <file:line> — <issue>
  - ...

WARNING findings (N):
  - ...

INFO findings (N):
  - ...

Total: N findings (X CRITICAL, Y WARNING, Z INFO)
```

If no findings overall:

```
=== /flightdeck:walkaround report ===
Audit run: <ISO date>
Flightdeck root: <path>

✅ Clean.
```

Omit any severity line whose count is 0. If an audit's target folder is absent (e.g. no `incidents/`), treat that audit as N/A — nothing to check, not a finding.

## Handling findings

- **CRITICAL**: fix before any other work. These are broken contracts.
- **WARNING**: schedule for the current session if quick; otherwise add a hanging task to cockpit.md.
- **INFO**: judge per item. Some are useful nudges; some are noise. Don't auto-fix.

Walkaround never auto-fixes. The author decides.

## Don't do

- Don't auto-fix any finding — walkaround surfaces, author resolves.
- Don't run walkaround against other repositories or foreign `flightdeck/` directories — false drift signals.
- Don't include `landed/` archived files in most audits — they're history, not subject to current-state rules (except Audit 6).
- Don't fail loudly on optional missing folders — a project with no `debriefs/` directory is fine.
- Don't bump cockpit `Last updated` from running walkaround — walkaround is read-only by design.
