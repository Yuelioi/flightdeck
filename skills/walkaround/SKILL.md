---
name: walkaround
description: Use when explicitly invoking the flightdeck integrity audit — checks cockpit.md / rules.md / specs / plans / incidents / checklists / docs / references for status validity, INDEX↔folder consistency (incl. nested knowledge areas), cockpit `## In Progress` AUTO-region consistency, orphan plans, dangling references, stray files, AGENTS.md drift, and (INFO) staging anomalies (## Staged derived-view drift / pending-review↔archive conflict) + missing workflow summary/last_updated + dangling supersedes/related edges + oversized Key Context, sync drift (vendored shared-knowledge stale / dangling), cockpit field-structure conformance (Audit 16). Triggered by `/flightdeck:walkaround`.
---

# Flightdeck Walkaround

User-triggered integrity audit of a flightdeck for protocol drift. Surfaces drift loudly so the author can fix it. The markdown checklist below is the source of truth for *what* to check; the mechanical audits (Audits 1/4/5/7/8) are computed by `flightdeck_lint` (JSON findings) and `flightdeck_index --check` (call form per the recorded `runtime` — [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order)), and the model reads their output to narrate and judge.

**Audit-only, never fix (walkaround invariant):** walkaround **MUST NOT modify any file** — it only surfaces drift. The fix path is `flightdeck_index <deck>` or `/flightdeck:landing`.

**Field authority**: [protocol.md § Frontmatter field reference](../preflight/protocol.md#frontmatter-field-reference-canonical) is the source of truth; these audits check against it.

## Severity legend

- **CRITICAL** — protocol contract broken. Fix before new work.
- **WARNING** — drift that accumulates. Fix soon.
- **INFO** — heads-up, judge per item.

## Audits

Run all 16 in order. First read `flightdeck/rules.md` if present; resolve behavior per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order). Empty/unused folders are not findings. Report each finding with its severity tag.

**Audit 1** — Check the `status` field of every non-archive `.md` → flag missing (CRITICAL), illegal value (WARNING; legal for `specs/plans`: `idea/active/done`; for knowledge: `active/stale/obsolete`; retired old values `pending/awaiting-review/blocked/superseded` are all WARNING).

**Audit 2** — Check the routing fields of non-archive knowledge files (top-level authored `.md` in `incidents/checklists/docs/references/`) → flag missing `when_to_read`/`applies_to`/`last_updated` (WARNING); an `incidents/` `recurrences` count that disagrees with its narrative section (INFO).

**Audit 3** — Check non-archive knowledge files for retired-in-3.0 fields → flag a still-present `superseded_by` field (WARNING; remove the field, the newer artifact carries `supersedes:`) or `status: superseded` (WARNING; migrate per Audit 1).

**Audit 4** — Check each file in `plans/` (non-archive) → flag those with no `implements:` field (INFO; consider linking a spec or confirm it is standalone).

**Audit 5** — Check each artifact folder's `INDEX.md` → flag a missing INDEX (WARNING), a file with no matching row (WARNING), a row whose file does not exist (WARNING), a row whose status disagrees with the actual frontmatter (WARNING); also check nested knowledge-area sub-folder INDEXes and their parent-INDEX reference rows. Computed by `flightdeck_index --check <deck>`.

**Audit 6** — Check each `status`-carrying `.md` under `archive/` → flag a workflow file not `done` (WARNING), a knowledge file not `obsolete` (WARNING).

**Audit 7** — Check every non-HTTP, non-pure-anchor markdown link in `flightdeck/` and repo-root `*.md` → flag those whose target file does not exist (CRITICAL; report source file:line + the broken path).

**Audit 8** — Check `.md` under `flightdeck/` that belong to no known folder / known root entry and are linked by no known entry point → flag orphan files (WARNING); a `<area>/` sub-folder under a knowledge folder is not stray; a `status: idea` spec is not an orphan; a sub-folder inside `specs/plans/` is a WARNING; a non-`.md` file not covered by folder semantics (WARNING).

**Audit 9** — If repo-root `AGENTS.md` carries a flightdeck marker block → compare field-by-field against `cockpit.md` (Focus / `## In Progress` / `## Next` / hanging tasks) vs the block content → flag any field divergence (WARNING; name the diverging field). Also read `rules.md`'s `agents_md` intent vs reality (both **INFO**, never a hard finding — walkaround never fixes): `agents_md: auto` + `AGENTS.md` **absent** → "`agents_md: auto` but no AGENTS.md (next landing will create it)"; `agents_md: off` + `AGENTS.md` **present** → "AGENTS.md present but `agents_md: off` (landing won't refresh it; run `/flightdeck:emit-agents-md` or accept staleness)".

**Audit 10** — Check each file in `specs/plans/` (non-archive) → aggregate those missing `summary` / `last_updated` → emit **one** aggregated INFO each (not per-file, to avoid flooding).

**Audit 11** — Check the `supersedes:`/`related:` field values of non-archive workflow files → flag targets that exist in neither the active tree nor `archive/` (INFO; an edge pointing into archive is normal, not flagged).

**Audit 12** — Check `cockpit.md`'s `<!-- AUTO:inprogress -->` block → compute the expected set (every non-archive `status: active` spec/plan) → flag an active file with no matching row (WARNING), a row whose file is not active (WARNING), summary/note text differences (INFO; self-heals on next regen); a fully missing block is WARNING. Computed by the `cockpit` drift tag of `flightdeck_index --check <deck>`.

**Audit 13** — `status: done` files in `specs/plans/` (non-archive) are **normal staged output** — they await the land valve, so walkaround does **not** treat done-not-archived as debt and does **not** nag to land. Instead audit the staging area for **anomalies**: (a) the `## Staged` derived view is out of sync with its truth source — the `cockpit:staged` drift tag of `flightdeck_index --check <deck>` (a hand-edited cockpit/INDEX or a script bug) → **WARNING**; (b) reading frontmatter directly, a pending-review knowledge artifact (`stale` + `verify`) that also has a copy at the same relpath under `archive/` (staged-in-place yet already landed — a contradiction) → **WARNING**. A `done` spec/plan with an active inbound `implements:` edge is still reported as **blocked done** (INFO; the inbound edge is unresolved so archival is pinned — report the blocker), but this is a real dependency, not a land-nag. Computed by `flightdeck_index <deck> --archivable` (the edge graph) + `--check` (the staged-view drift tag).

**Audit 14** — Check `cockpit.md`'s `## Key Context` accumulation hygiene (non-blocking) → flag an entry that looks stale (points at an archived/graduated target), an entry grown into prose rather than a literal pointer, or an obviously oversized section (INFO; suggest a per-entry drain/shrink at the next `/flightdeck:landing`, see [exit-ritual § Accumulator-drain](../preflight/exit-ritual.md#cockpit-update--what-changes)). walkaround only surfaces, never drains.

**Audit 15** — Check vendored files carrying `synced: true`. Sync state uses the read-only `flightdeck_index <deck> --sync-status` (emits `state<TAB>relpath`; the master store is fixed at `~/.flightdeck`):
- Validate the relpath invariant: no source file at the same relpath in the master store → `dangling`, report **WARNING**;
- `stale` (the shared-region fingerprint differs from the master's) → report **INFO** "N shared files stale — run `/flightdeck:sync`";
- `marker-missing` (drifted **and** the consumer file has no `<!-- flightdeck:project-specific -->` marker) → report **WARNING** "local additions will be overwritten on next pull — add the project-specific marker before syncing": the whole body is treated as shared, so a `--sync-pull` would splice it away (the pull itself skips these, but the file is stuck out-of-sync until the marker is added);
- `master-missing` (`~/.flightdeck` absent) → **do not report** (no master store on this machine, not drift).

Also check (reading frontmatter directly, not `--sync-status` output): a consumer-side `synced: true` file that carries a `consumers` field → report **WARNING** (`consumers` is a master-store-only field, must be stripped when vendoring; its presence in a consumer copy is illegal).

No `synced: true` files → N/A.

**Audit 16** — cockpit field-structure / role conformance. Check `cockpit.md` against the canonical field set (`Updated` / `Focus` / `Pointers` / `## Next` / `## In Progress` / `## Staged (awaiting land)` / `## Key Context` / `## Pending Review` / `## Hanging Tasks`, per [templates § cockpit.md](../preflight/templates.md#cockpitmd)) → flag (all **INFO**, non-blocking — surface only, never modify, per the walkaround invariant): a non-standard hand-added section; a missing standard section; or field **role-creep** — `Updated` carrying a changelog (belongs in `git log`), `Focus` grown into a paragraph (goal/criteria/method that belongs in the spec body), or `## Next` carrying a progress checklist / rationale list / milestone links (belong in the plan's `## Progress`). Deck **content language** is never a finding (decks follow the user's language). **Fix:** `/flightdeck:conform` snaps the deck back to the canonical shape (mechanical script pass + AI reshape) — walkaround only reports this drift, it never rewrites.

## Output format

```
─── 🔍 walkaround ───
Audit run: <ISO date>
Flightdeck root: <path>

CRITICAL findings (N):
  - <file:line> — <issue>

WARNING findings (N):
  - ...

INFO findings (N):
  - ...

Total: N findings (X CRITICAL, Y WARNING, Z INFO)
```

If there are no findings at all, output `✅ Clean.`. Omit any severity row with count=0. An audit whose target folder does not exist → N/A, not a finding.

## Don't do

- **walkaround MUST NOT modify any file. NEVER auto-fix** — it only surfaces; the author decides. The `rules.md` version is a static stamp written by `launch`; walkaround neither reads, writes, nor bumps it.
- Don't run against other repos / foreign `flightdeck/` — false positives.
- Don't include archive files in most audits (Audit 6 excepted).
- Don't flag empty-but-present folders / INDEX — empty is a normal initial state; only a missing known folder is INFO.
