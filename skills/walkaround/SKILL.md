---
name: walkaround
description: Use when explicitly invoking the flightdeck integrity audit — checks cockpit.md / rules.md / specs / plans / incidents / checklists / docs / references for status validity, INDEX↔folder consistency (incl. nested knowledge areas), cockpit `## 进行中` AUTO-region consistency, orphan plans, dangling references, stray files, AGENTS.md drift, layout-version / legacy paths, and (INFO) done-but-unlanded + missing workflow summary/last_updated + dangling supersedes/related edges. Triggered by `/flightdeck:walkaround`.
---

# Flightdeck Walkaround

User-triggered integrity audit of a flightdeck for protocol drift. The protocol is markdown + filesystem conventions; drift is the silent killer of advice systems. Walkaround surfaces drift loudly so the author can fix it. Implemented as a slash skill (markdown checklist the AI follows) — the audit logic and every judgment live in markdown, never in a binary, preserving flightdeck's plain-markdown + git bet. The mechanical audits (status legality, orphan plans, INDEX↔folder consistency, dangling references, the unambiguous stray-file cases — Audits 1/4/5/7/8) MAY use the bundled `flightdeck_lint.py` as an optional fast path (it emits a JSON findings list; INDEX↔folder alone is also covered by `flightdeck_index.py --check`) — see [exit-ritual § Script fast path](../preflight/exit-ritual.md#script-fast-path-optional-accelerator). The markdown checklist below is the always-valid fallback and source of truth, and every judgment (classification, migration decisions, the full stray-file reachability call) stays in markdown, so the plain-markdown bet holds.

## When to invoke

- Periodically (e.g., before a release commit, weekly during active work).
- After a long absence from the project — drift accumulates silently.
- When something feels off (cockpit doesn't match reality, checklists unread, AGENTS.md stale).
- Before promoting flightdeck conventions to a downstream project — walkaround should be clean on the source.

## Severity legend

- **CRITICAL** — protocol contract broken (e.g., artifact missing required frontmatter, dangling internal reference). Fix before proceeding with new work.
- **WARNING** — drift that will accumulate (e.g., stale INDEX rows, missing routing fields, legacy paths). Fix soon, before the next release.
- **INFO** — heads-up that may or may not need action (e.g., orphan plan with no `implements`, a long-stale `active` with no `note:`). Judge per item.

## Audits

Run all 14 in order. First read `flightdeck/rules.md` if present; resolve behavior per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order). Do not flag the absence of pre-3.0 toggle keys as an error (3.0 removed them — inferred / House-Rules now); pre-3.0 keys (`disabled_folders` / `model_invocable` / `commit_mode` / `status_auto` / `disabled_gates`) are read but ignored. **Empty or unused folders are not findings** — emptiness is normal; only genuinely misplaced content is flagged (see Audit 8). For each, report findings with the severity tag.

**Field validity is governed by [protocol.md § Frontmatter field reference](../preflight/protocol.md#frontmatter-field-reference-canonical)** — that table is the source of truth for which fields are required per kind. The audits below check against it; if they disagree, the canonical table wins.

### 1. Frontmatter status validity (CRITICAL / WARNING)

**Folder = kind (implicit); `status` = the only required frontmatter field.** Audit `status` only here; no other frontmatter field is *required* for workflow artifacts. (The recommended workflow fields `summary` / `last_updated` and the optional relation edges `supersedes` / `related` get soft INFO checks in Audits 11–12, never CRITICAL/WARNING.)

#### Workflow artifacts (`specs/`, `plans/`) — NOT in `archive/`

For each `.md` file in these folders:

- MUST carry `status`. Missing: **CRITICAL**.
- Legal values (`specs/` and `plans/`): `idea` / `active` / `done`.
- Present but illegal value: **WARNING**. The retired pre-3.0 values (`pending` / `awaiting-review` / `blocked`) are illegal here — flag the value, but route the fix through the deck-level model-v4 migration reported once in Audit 10 (`pending → idea`, `awaiting-review`/`blocked → active`); don't prescribe a per-file remap that pre-empts the migration.
- The optional `note:` field is advisory diagnostic text — recognized and rendered (`[note: …]`), never validated as a status value.

#### Knowledge artifacts (`incidents/`, `checklists/`, `docs/`, `references/`) — NOT in `archive/`

For each `.md` file in these folders (excluding `INDEX.md`; the nestable knowledge folders may hold `<area>/` subdirectories — audit the `.md` files in those areas the same way; `references/` may contain external project trees — audit only flightdeck-authored top-level `.md` files directly under `references/`, not the imported external tree):

- MUST carry `status`. Missing: **CRITICAL**.
- Legal values: `active` / `stale` / `obsolete`.
- Present but illegal value: **WARNING**. `stale` is a legal status (auto-set by ritual when a doc's `when_to_update` condition is met; cleared by user when the doc is brought current again). The retired pre-3.0 value `superseded` is **not** legal here — a live knowledge file carrying `status: superseded` (outside `archive/`) is a **WARNING** (retired-3.0 leftover): the correct 3.0 representation is the dead artifact going `obsolete` (drained to `archive/` by the ritual) while the replacing artifact carries a `supersedes:` traceability edge. Route the fix as: "flip to `obsolete` if dead (and let the ritual drain it to `archive/`), or flip to `active`/`stale` if still valid; the replacing artifact should carry `supersedes: <this-file>` for traceability."

### 2. Knowledge routing fields (WARNING)

For each knowledge artifact NOT in `archive/`:

- Files in `incidents/`, `checklists/`, `docs/`, `references/` (top-level authored `.md`): MUST carry `when_to_read` + `applies_to` + `last_updated`. Any missing: **WARNING** — file is invisible to flightdeck routing.
- Malformed values (e.g. `last_updated: potato`, empty `when_to_read`): **WARNING**.
- `incidents/` only: the optional `recurrences` counter, if present, must be an int ≥ 1 and ≈ `1 + (count of "## [Case N]" blocks)`. A drift (counter ≠ narrative) is **INFO** — re-sync. Absent = treated as 1.

Workflow artifacts (`specs/`, `plans/`) are **out of scope here** — they carry no required routing fields. Their recommended `summary` / `last_updated` are checked at INFO in Audit 11.

### 3. Retired-3.0 supersession leftovers (WARNING)

The `superseded_by` field and `status: superseded` value were retired in flightdeck 3.0 (see [protocol.md § Supersession model](../preflight/protocol.md#supersession-model)). The old redirect mechanism (`superseded_by` required when `status: superseded`) was predicated on knowledge files staying in place indefinitely. Since `obsolete` is now a drain state (rituals move knowledge to `archive/` the same way they drain `done` workflow), the dead file is no longer on disk long enough to need a redirect. Supersession is now expressed entirely by the new artifact's `supersedes:` traceability edge plus the old artifact going `obsolete` and being drained to `archive/`.

For each knowledge artifact NOT in `archive/`:

- A live `superseded_by` field on the artifact: **WARNING** — retired-3.0 leftover. `superseded_by` no longer pins or redirects anything; remove the field. Ensure the replacing artifact carries `supersedes: <this-file>` for traceability, and that this artifact is `obsolete` (dead) or `active`/`stale` (still valid), whichever is correct.
- `status: superseded` on the artifact: **WARNING** — retired-3.0 leftover (handled in Audit 1, cross-reference here for completeness). Migrate as described in Audit 1.

An artifact in `archive/` that carries a legacy `status: superseded` (written before 3.0) is tolerated as frozen history — Audit 6 covers it. Do NOT flag archive files here.

### 4. Orphan plan (INFO)

For each file in `plans/` (NOT in `archive/`) with no `implements:` frontmatter field:

- **INFO** — consider linking a spec via `implements: specs/<x>.md`, or confirm this plan is intentionally standalone.

Do not flag files that carry `implements:` even if the target is also missing (that is caught by Audit 7 — dangling references).

### 5. INDEX ↔ folder consistency (WARNING)

**Fast path** (when a script runtime is reachable — `uv`/`python`, inferred): `flightdeck_index.py --check <deck>` reports every drift below deterministically and exits non-zero — see [exit-ritual § Script fast path](../preflight/exit-ritual.md#script-fast-path-optional-accelerator). The manual checks below are the always-valid fallback and source of truth.

For each artifact folder (`specs/`, `plans/`, `incidents/`, `checklists/`, `docs/`, `references/`):

- If the folder has no `INDEX.md`: **WARNING** — missing per-folder INDEX.
- Read the `<!-- AUTO -->` block in the folder's `INDEX.md`. Each row should list one file with its `status` (and other displayed metadata). Check:
  - A real file exists with no corresponding row: **WARNING** — missing INDEX row. (`specs/INDEX` groups its AUTO region into `待启动（idea）` / `进行中·完成（active·done）` subheadings — match rows within the grouped block.)
  - A row exists for a file not on disk: **WARNING** — stale INDEX row (ghost).
  - A row's displayed `status` does not match the file's actual frontmatter `status`: **WARNING** — out-of-sync status in INDEX. (Exception: `references/` rows show project/file count, not per-file status — do not flag `references/` for missing status values.) Audit 5 validates the `status` segment **only** — the `summary` segment is a derived value that the next `landing`/`status` regeneration self-heals, so it is not byte-compared here (avoids false drift from punctuation/wording).
- **Nested knowledge areas:** for each nestable knowledge folder (`incidents/`, `checklists/`, `docs/`, `references/`) that contains `<area>/` subdirectories:
  - An area subdir with `.md` files but **no** `<area>/INDEX.md`: **WARNING** — missing per-area INDEX.
  - The top-level folder's `INDEX.md` should carry a row/line for each populated area (so the area is reachable from the parent index). A populated area with no parent-INDEX line: **WARNING**.
- For the root `flightdeck/INDEX.md`:
  - If absent: **WARNING** — missing root INDEX.
  - Each per-folder summary line's counts (e.g. `specs/ — 3 (2 active, 1 done)`) must match the actual file counts and status distribution in that folder. Mismatch: **WARNING**. (`references/` is exempt from status counting; knowledge folders exclude `obsolete` from the count, matching their INDEX.)

### 6. `archive/` has no non-terminal status (WARNING)

For each `.md` file under `archive/` that carries a `status` field:

- Workflow files (`archive/specs/`, `archive/plans/`): status must be `done`. Any other value: **WARNING**. (A pre-3.0 deck may carry a historical `landed/sketches/` tree — left in place; audit its files by the same workflow rule.)
- Knowledge files (`archive/incidents/`, `archive/checklists/`, `archive/docs/`, `archive/references/`): status must be `obsolete`. Any other value: **WARNING**. (Pre-3.0 archived knowledge files may carry a legacy `status: superseded` — these are tolerated as frozen history written before 3.0 retired that value; no new `superseded` files should reach `archive/`. A pre-3.0 `landed/` tree or `landed/debriefs/` is historical — left in place, not regenerated; do not flag its presence — Audit 10 routes the rename.)

### 7. Dangling internal references (CRITICAL)

For each markdown file under `flightdeck/` and every `*.md` at repo root:

- Extract all markdown links matching `[text](path)` where `path` is NOT an HTTP/HTTPS URL and NOT an anchor-only (`#...`).
- For each link, strip any `#fragment` suffix, then resolve the path relative to the file's directory. Verify the **file** exists only — do not validate anchors.
- If the file is missing: **CRITICAL** — broken cross-reference. Report the source file:line + the broken target path.

### 8. Orphan / stray files (WARNING)

Known folders: `specs/` `plans/` `incidents/` `checklists/` `docs/` `references/` `archive/`. Known root entries: `cockpit.md` `INDEX.md` `rules.md`. (A not-yet-migrated deck may still carry `charts/` / `landed/` / `sketches/` / `debriefs/` — Audit 10 / preflight route them to the rename + model-v4 migration; do not double-flag them as stray here.)

- A `.md` directly under `flightdeck/` that is not a known entry file and not linked from any known entry: **WARNING** — orphan; either link it from an entry or remove it.
- A `.md` in a known folder that is neither a valid artifact file nor an `INDEX.md`: **WARNING** — stray file with no clear role.
- **Nested knowledge areas are NOT stray.** Under a nestable knowledge folder (`incidents/`, `checklists/`, `docs/`, `references/`), an `<area>/` subdirectory is a valid same-kind organization partition — do not flag the subdir itself, nor the `.md` files inside it, as stray (they are audited as area files in Audits 1/2/5). Only `specs/` and `plans/` (workflow) forbid subdirectories — a subdir there **is** flagged.
- **`status: idea` specs are NOT orphans.** An idea spec is the to-start pool — it is reachable via the `待启动（idea）` group of `specs/INDEX`, so the normal reachability rule already clears it. Never flag an idea spec as orphan/stray for "not in cockpit": ideas deliberately do not appear in cockpit `## 进行中` (only `active` does).
- A non-`.md` file under `flightdeck/` that no folder semantics cover: **WARNING**. Asset files (`.png` `.svg` `.json` `.yaml` etc.) under a folder that expects them (e.g. `references/`) are fine — do not flag those.
- `references/` may hold an external project tree — files nested inside `references/<project>/` are not stray. Only top-level unrecognized files directly under `flightdeck/` or directly under a non-nestable folder are flagged.

**First run note**: on an existing project, Audit 8 may list many items at once. Advise gradual cleanup, not a forced all-at-once sweep.

### 9. AGENTS.md drift (WARNING)

If `AGENTS.md` exists at repo root with flightdeck markers (`<!-- BEGIN: flightdeck -->` / `<!-- END: flightdeck -->`):

- Extract the source fields from `cockpit.md`: Active focus, `## 进行中`, `## 下一步`, Hanging tasks.
- Read the same fields as currently rendered inside the `AGENTS.md` flightdeck block.
- Compare field by field (actual values, not overall impression). Any source value absent from or different in the block: **WARNING** — `emit-agents-md` hasn't been re-run since the source changed. Name the diverging field.

If `AGENTS.md` doesn't exist or has no flightdeck markers: skip (the project hasn't dogfooded the emitter yet; that's optional).

### 10. Version / migration detection — walkaround is the sole version writer (CRITICAL / WARNING / INFO)

Get the **layout verdict**: fast path `flightdeck_index.py <deck> --verdict`; fallback read `rules.md` `version` + `MIGRATION.md` frontmatter (`current` + `layout_need_update`) and self-check the structural signals — both yield the same verdict (see [protocol.md § Migration detection](../preflight/protocol.md#migration-detection)). **walkaround is the only command that writes `version`** — preflight only reports the verdict, landing only guards on it. Act on it:

- **`malformed`** → **CRITICAL** — a required workflow frontmatter field is missing (e.g. a `specs/`/`plans/` file lacking `summary` or `status`); name the file(s) and fix per Audit 1/11 before other work.
- **`structural-behind`** → **WARNING** — a structural migration applies; point to the matching [MIGRATION.md](../../MIGRATION.md) section and **offer to perform it** (the moves/remaps are judgment — confirm with the author; don't silently move files). This subsumes the legacy/model-v4/rename markers below.
  - Legacy 1.x markers (`flightdeck/manifest.md` · `logbook.md` · `kneeboard/` · `flight-plans/` · `incident-reports/` · `safety-reviews/`) → route to the 1.x→1.2 migration first.
  - **Mainstream-rename markers (3.0): an old-name `flightdeck/charts/` or `flightdeck/landed/` folder still present** → route to the [MIGRATION.md](../../MIGRATION.md) rename section (`charts/ → references/`, `landed/ → archive/`; references semantics — imported external material — are unchanged, only the name). Report once here, not also as stray (Audit 8). (The verdict's `_structural_signal` fires on these folders.)
  - Pre-model-v4 structure (a `flightdeck/sketches/` or `flightdeck/debriefs/` folder in the *active* tree — not `archive/`; or a workflow file carrying a retired status `pending` / `awaiting-review` / `blocked`; or a `cockpit.md` with a hand-written `## Next session` and no `## 进行中` AUTO region) → route to the matching model-v4 section. Report once here, not also as stray (Audit 8) or illegal-status (Audit 1).
- **`compatible-behind`** → **bump `rules.md` `version` to `current`** (the one safe version write — a number stamp, no structural change) and report it as **INFO** ("version stamped to current"). This is walkaround's sanctioned write; it replaces the old preflight silent bump.
- **No `flightdeck/rules.md`, or `rules.md` has no `version`** → **CRITICAL** — `rules.md` + `version` are part of the minimal contract (the verdict reports `structural-behind` for the no-version case). A cockpit-only / pre-2.2 deck → point to the 2.2 migration in [MIGRATION.md](../../MIGRATION.md).
- **A stray `**Layout**` line still in `cockpit.md`** → **INFO** — leftover from a pre-2.2 deck; the 2.2 migration removes it (version lives in `rules.md` now).
- **`current`** → pass; report nothing.

Only report once per path — do not also flag these as stray/orphan in Audit 8.

### 11. Workflow recommended fields (INFO)

Scan workflow artifacts (`specs/`, `plans/`) NOT in `archive/` for the recommended `summary` / `last_updated`. **Report as a single aggregated INFO per field, not one finding per file** — a pre-enrichment deck would otherwise flood the report:

- `INFO — N workflow artifacts missing summary: <file, file, …>` (consider adding one; it drives the INDEX row and survives into `archive/`).
- `INFO — N workflow artifacts missing last_updated: <file, file, …>` (the next `status`/`landing` flip auto-adds it; bare `status: idea` specs commonly omit it — expected, don't push to add it).

These are **recommended, not required** — never escalate to WARNING/CRITICAL. If every workflow artifact has both, report nothing.

### 12. Dangling relation edges (INFO)

For each workflow artifact NOT in `archive/` carrying `supersedes:` or `related:`:

- Resolve each path value relative to the flightdeck root. If the target exists **neither in the active tree nor under `archive/`**: **INFO** — dangling relation edge (target deleted or never existed). An edge that points into `archive/` is normal (the Land Routine rewrites edges to the `archive/` prefix on archive) — do NOT flag it.
- This checks frontmatter edge **values** only; prose `[text](path)` links are Audit 7's job (`supersedes`/`related` are not markdown links). `superseded_by` is a retired-3.0 field — its presence is flagged by Audit 3, not here; Audit 12 does not touch it.

### 13. Cockpit `## 进行中` AUTO-region consistency (WARNING / INFO)

Cockpit `## 进行中` is the AUTO-derived projection of the active set — an artifact is in cockpit iff it is `status: active` (so orphans are structurally impossible). Verify the projection has not drifted (a hand edit, or a flip whose regen was skipped):

- Read the `<!-- AUTO:inprogress -->` … `<!-- /AUTO -->` block in `cockpit.md`. Compute the expected set = every `status: active` spec/plan (NOT in `archive/`). Compare to the rows present:
  - An `active` spec/plan with **no** row in `## 进行中`: **WARNING** — missing from the active projection (run a regen). An `active` artifact invisible in cockpit is exactly the orphan the model-v4 design rules out — so this is the load-bearing check.
  - A row for a file that is **not** `active` (it is `idea` / `done`, or absent on disk): **WARNING** — stale projection row.
  - A row whose `summary` / `[note: …]` differs from the file's current frontmatter: **INFO** — cosmetic drift, self-heals on the next `status`/`landing` regen (mirror of Audit 5's summary-segment leniency; don't byte-compare the summary as WARNING).
- **Fast path**: the same `flightdeck_index.py --check <deck>` from Audit 5 also checks the `cockpit` target — a reported `cockpit` drift label covers this audit's WARNING cases deterministically.
- If `cockpit.md` has no `<!-- AUTO:inprogress -->` region at all: this is a pre-model-v4 cockpit → handled by the migration offer (Audit 10 / preflight), not a separate finding here.

### 14. Done-but-unlanded (INFO)

A `status: done` workflow artifact still sitting in its source folder (`specs/` or `plans/`, NOT in `archive/`) is *done-but-unlanded* — landing has not yet drained it. This is INFO only (landing drains automatically; the file is correctly `done`), but the two sub-cases differ:

- **Blocked done** — the done artifact has a structural **inbound edge from an `active` artifact** (some active spec/plan points at it via `implements:`). It cannot land yet — the active work still depends on it. **INFO** — name the artifact **and the `active` artifact(s) blocking it** ("done-but-unlanded: `plans/x.md` held by active `specs/y.md`"). Don't push to land it.
- **Landable done** — the done artifact has **no** active inbound edge. It is safe to archive; landing just hasn't run. **INFO — "可 land"** (run `/flightdeck:landing` to drain it).

**Fast path** (when a script runtime is reachable — `uv`/`python`, inferred): `flightdeck_index.py <deck> --archivable` prints the deterministic *landable* set (done workflow files with no active inbound edge), read-only. A `done` source file **in** that list → landable ("可 land"); a `done` source file **not** in the list → blocked (some active artifact's inbound edge holds it — report the blocker). See [protocol § status/landing seam](../preflight/protocol.md#the-status--landing-seam). The manual edge-walk above is the always-valid fallback.

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

- Don't auto-fix any finding — walkaround surfaces, author resolves. **One exception:** the `compatible-behind` version bump in Audit 10 (a trivial, safe number stamp) — walkaround is the sole version writer. Structural migrations are still author-confirmed, never silent.
- Don't run walkaround against other repositories or foreign `flightdeck/` directories — false drift signals.
- Don't include `archive/` archived files in most audits — they're history, not subject to current-state rules (except Audit 6).
- **Don't flag empty-but-present folders / `INDEX.md`** — a freshly scaffolded full-layout deck (3.x) has empty folders + empty INDEX files; emptiness is the normal initial state, never an anomaly. (Under the full layout, a *missing* known folder is the mild anomaly instead — **INFO** "folder `<x>/` missing — full layout expects it", not CRITICAL.)
- Don't touch `cockpit.md` (no `Last updated` bump) — walkaround's only sanctioned write is the Audit 10 version bump; everything else it surfaces, the author resolves.
