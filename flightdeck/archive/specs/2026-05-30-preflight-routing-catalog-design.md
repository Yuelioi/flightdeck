# Spec: preflight routing catalog — prime the routing graph into context at entry

> **Status**: implemented + shipped in v1.1.0 (2026-05-30). Archived.
> **Targets**: `skills/preflight/SKILL.md`, `CHANGELOG.md` + `VERSION`.
> **Type**: additive (post-v1.0 additive-only window) → minor bump.

## Implementation note (2026-05-30, v1.1.0)

Shipped as designed. Plan: `landed/flight-plans/2026-05-30-preflight-routing-catalog-plan.md`. Notes for the record:

- All design decisions implemented verbatim into `skills/preflight/SKILL.md` (new step 5 catalog build; step 6 now matches `applies_to` before executing; grouped 4-column output with `[Malformed bundles]`; `skip_when` excluded; leaves excluded; `⚠` markers for parse-error / missing-`when_to_read` / missing-`bundle:true`).
- The existing "Don't do" bulk-read bullet was refined (rather than adding a new line) to tie it to the catalog: step 5 loads metadata only, bodies stay on-demand.
- Verified by a dogfood fixture run (8/8 assertions, incl. leaf-excluded, malformed-bundle-grouped, `landed/`-excluded, negative no-body-read). No automated test harness — verification is markdown dogfood, consistent with the rest of flightdeck.
- `VERSION` not re-bumped: ships inside the same unreleased 1.1.0 minor as the bundles work.

## Motivation

Flightdeck routes `checklists/` and `incident-reports/` by frontmatter (`when_to_read` / `applies_to`), discovered via a recursive frontmatter scan. But nothing loads that metadata eagerly: the SessionStart hook injects only `workflow/SKILL.md`, and that scan is an action the AI must *choose* to run when a task seems relevant. So a routed resource is only consulted if the AI remembers to look at the right moment.

Concrete failure: a checklist with `when_to_read: before writing or editing any source-code comment` is never opened if the AI just starts editing code — its declared trigger fires *before* writing, but the only scenario-table edge into `checklists/` is "preparing commit" (too late). The file's instruction sits in a document nobody read. This is the routing soft spot: reliability depends on the AI self-initiating that scan, and there is no eager surface of "what routed resources exist and when to read them."

Skills solve the analogous problem by loading every skill's `description` (its when-to-use) at startup, so the model knows what exists and when each applies — without loading bodies. This spec brings that model to flightdeck's routed resources, scoped to the explicit entry ritual.

## Decisions (settled in brainstorming)

- **Load timing**: only on `/flightdeck:preflight` (NOT auto every session via the hook). Zero passive token cost; relies on the user's existing "run preflight at entry" habit.
- **Scope**: `checklists/` + `incident-reports/` flat files + bundle `README.md`s. (Same `when_to_read`/`applies_to` frontmatter, same invisibility problem.)
- **Approach A — ephemeral, no stored file**: preflight reads and parses each routed file's frontmatter live and prints a table into context. No materialized index (rejected B: a stored catalog re-introduces the metadata-decay problem and would need a walkaround audit + landing regeneration; rejected C: INDEX.md is optional, AUTO-section-maintained, and may omit bundle READMEs). A reads source truth each run — zero staleness, no new artifact, no code, no bash YAML parsing. Mirrors the skill-`description` model: read fresh from frontmatter at load time, not from a cache.

## Design

A single additive change to `skills/preflight/SKILL.md`. preflight is a markdown checklist the AI follows; this adds one step.

### New step placement

Insert after the current mismatch-handling step and before "execute the first Next session item" — i.e. after repo state is reconciled, before work begins, so the catalog is in context when the task starts. The execute step renumbers accordingly.

### Catalog construction (the action the AI runs)

1. Read the frontmatter (YAML between `---`) of, **searching recursively** (not just the top level — bundle READMEs live one directory down), under `checklists/` and `incident-reports/`, excluding anything under `landed/`:
   - every flat `*.md` directly in those folders, and
   - every subdirectory `README.md`.
   The AI parses the frontmatter natively (so multi-line / quoted / comma-bearing `when_to_read` values are handled) — this is not a brittle one-line regex.
2. Extract per file: path, `when_to_read`, `applies_to`, `last_updated`. (`skip_when` is intentionally NOT extracted here — it is a match-time negative-routing concern, irrelevant to a know-what-exists catalog.) Classify each entry by **kind** for grouped display:
   - flat file under `checklists/` → `checklist`; flat file under `incident-reports/` → `incident-report`.
   - any subdirectory `README.md` with `bundle: true` → `bundle` (regardless of parent folder).
   - a subdirectory `README.md` **lacking** `bundle: true` → it is NOT a bundle, so do not put it under `[Bundles]`; surface it in a separate `[Malformed bundles]` group with a `⚠ missing bundle: true` note. Do NOT silently fall back to the `checklist`/`incident-report` group and do NOT hide it — a malformed bundle should be visible, not invisible (walkaround Audit 1 is the authority that flags it CRITICAL; preflight only surfaces).
3. **Leaves are NOT listed** — bundle leaves carry no routing frontmatter and are reached via the README's `reading_order`. Listing them would break the single-entry guarantee.
4. **No silent disappearance.** Any file whose frontmatter can't be parsed, or that is missing `when_to_read`, is still listed — with a `⚠ parse error` or `⚠ missing when_to_read` marker — so it never vanishes from the catalog. All markers are **non-blocking** (preflight stays read-only; hard-fail enforcement remains in `workflow` / `walkaround`).

### Output

A block in preflight's report, **grouped by kind** with explicit headers — bundles get their own group because bundle is a first-class concept; do not make the reader infer type from the path/suffix. Omit any group with no entries. Columns are fixed at **File | when_to_read | applies_to | last_updated** (`last_updated` is one more frontmatter field already in hand — it lets the AI weigh trust: a `2024-01-01` rule is more suspect than a `2026-05-30` one).

```
Routing catalog (loaded this session — know-what-exists, not read-all):

[Checklists]
| File | when_to_read | applies_to | last_updated |
|---|---|---|---|
| checklists/comments.md | before writing or editing any source-code comment | comments, code-style, documentation | 2026-05-29 |
| checklists/verify.md | before commit | test, ci | 2026-03-10 |

[Incident reports]
| File | when_to_read | applies_to | last_updated |
|---|---|---|---|
| incident-reports/parser-recursion.md | before designing a recursive parser | parser, recursion | 2026-04-02 |

[Bundles]  (read the README first; leaves load via its reading_order)
| README | when_to_read | applies_to | last_updated |
|---|---|---|---|
| checklists/plugin-spec/README.md | before authoring a plugin spec | plugin, spec | 2026-05-30 |

[Malformed bundles]  (omitted when none — a README that isn't actually a bundle)
| README | issue |
|---|---|
| checklists/foo/README.md | ⚠ missing bundle: true |

→ Before executing the task, match its keywords / touched paths against `applies_to` above and load the matching bodies. The catalog tells you what exists; this step is what makes it useful.
This catalog is know-what-exists only — it is NOT a substitute for `/flightdeck:walkaround` (full integrity audit) and does NOT mean these checklists have been read or satisfied. Bodies still load on demand when a trigger matches.
```

A bundle is surfaced under `[Bundles]` regardless of whether it lives under `checklists/` or `incident-reports/` — its first-class kind wins over its parent folder for display grouping.

### Semantic boundary (state in the skill)

The catalog primes *know-what-exists + when-to-read*, mirroring skill descriptions. It does **NOT** mean "read all these files now" — bodies still load only when a trigger matches the current task during the session. This must be stated explicitly so the AI does not bulk-read every routed file at entry (token waste, the exact anti-pattern preflight's "Don't do" section already warns against).

### Edge cases

- No routed resources (minimal flightdeck, cockpit-only): print `Routing catalog: (empty — no routed resources yet)`. Never fail.
- `landed/` excluded throughout.

## Explicitly out of scope (YAGNI)

- No stored/materialized catalog file; no hook change; no new walkaround audit; no landing maintenance step.
- No auto-reading of bodies.
- No new scenario-table edges (e.g. "writing code/comments → checklists/"). That is a separate, independent improvement and is not bundled here.
- No auto-loading every session — explicitly rejected in favor of preflight-only.

## Verification (dogfood)

- Project with ≥1 checklist (e.g. one carrying `comments.md`): `/flightdeck:preflight` lists it with its `when_to_read`.
- Minimal flightdeck (cockpit only): graceful empty-catalog line, no error.
- Project with a bundle: the bundle `README.md` appears under its own `[Bundles]` group (not mixed into `[Checklists]`/`[Incident reports]`, and not left for the reader to infer from the `/README.md` suffix); **its leaves do NOT appear anywhere in the catalog**.
- Subdirectory `README.md` lacking `bundle: true`: listed under a separate `[Malformed bundles]` group with `⚠ missing bundle: true` — NOT under `[Bundles]` (it isn't one), and not silently regrouped or hidden.
- A checklist missing `when_to_read` (or with unparseable frontmatter): row shows the `⚠ missing` / `⚠ parse error` marker and is still listed; preflight does not block.
- **Negative case (semantic boundary)**: after preflight prints the catalog, there is NO read of any checklist / incident-report body unless the current task triggers that file's `when_to_read`. Printing the catalog must not cascade into bulk-reading every routed file.

## Accepted risks / known limits

- **Concurrent edits during the read** — if a routed file is being edited while preflight reads it, the catalog row may be momentarily inconsistent. Not flightdeck-specific; no mitigation, accepted.
- **Linear cost** — catalog build reads and parses every routed file's frontmatter, so cost grows linearly with the number of checklists / incident-reports / bundles. Trivial at current scale; if preflight ever becomes heavy, splitting the catalog into an on-demand sub-step is a future option (not now).
- **Actionability depends on the match step** — the catalog's value is realized only when the AI matches task keywords against `applies_to` (the `→` line in the output). The catalog alone is know-what; the match step is use-it.

## Implementation order

1. Add to `skills/preflight/SKILL.md`: the catalog-build step (recursive read, kind classification, `⚠` markers, leaves excluded), the grouped output block (4 columns), the match-against-task line, and the "not a walkaround substitute" boundary note.
2. Update the preflight `description` frontmatter. Draft:
   > Use when explicitly invoking the flightdeck entry ritual — reconciles cockpit.md against repo state, runs the staleness check, surfaces stale kneeboard files, loads a routing catalog (checklists / incident-reports / bundle READMEs with their `when_to_read` + `last_updated`), and reports the first "next session" item. Triggered by `/flightdeck:preflight`.
3. Bump `CHANGELOG.md` [Unreleased] + `VERSION` (minor).
