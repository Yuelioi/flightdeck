# preflight Routing Catalog Implementation Plan

> **Archived plan** — fully executed and shipped in v1.1.0 (2026-05-30). All tasks done; verified by dogfood fixture (8/8). Kept as history; current behavior lives in `skills/preflight/SKILL.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/flightdeck:preflight` print a grouped, freshness-stamped routing catalog (checklists / incident-reports / bundle READMEs) into context at session entry, so routed resources' triggers are known before work begins.

**Architecture:** A single additive change to one markdown skill file, `skills/preflight/SKILL.md`. preflight is a checklist the AI follows — adding a "load routing catalog" step + an output block is the entire mechanism. No code, no hook change, no stored file, no new dependency. The catalog is built fresh each run by reading + parsing routed files' frontmatter (zero staleness).

**Tech Stack:** Plain Markdown + YAML frontmatter. The "engine" is the AI executing the skill checklist. Verification is a dogfood run of the skill against a fixture `flightdeck/` (flightdeck has no automated test binary by design — `walkaround` and release-gate scenarios are likewise markdown-driven).

**Design source:** `flightdeck/landed/specs/2026-05-30-preflight-routing-catalog-design.md`. Read it before starting.

---

## File Structure

- `skills/preflight/SKILL.md` — the only behavioral change. Gets: (1) a new checklist step "Load the routing catalog", (2) an expanded Output format section with the grouped catalog block, (3) an updated `description` frontmatter, (4) a "Don't do" line guarding against bulk-read.
- `CHANGELOG.md` — one bullet under the current unreleased version.
- `VERSION` — already `1.1.0` from the bundles work this cycle; confirm, do not re-bump (this feature ships in the same unreleased minor).
- Fixture (scratch, NOT committed) — a throwaway `flightdeck/` tree used only by the verification task.

---

## Task 1: Add the "Load the routing catalog" step to preflight

**Files:**
- Modify: `skills/preflight/SKILL.md` — the `## Run this checklist exactly` numbered list (insert a new step between the current step 4 "Mismatch handling" and step 5 "All reconciled → execute").

- [ ] **Step 1: Insert the new step 5 and renumber the execute step to 6**

Find the current step 5:

```markdown
5. **All reconciled → execute the first "Next session" item.**
   State the item back to the user in one sentence ("Executing: [item description]"), then proceed.
```

Replace it with the new step 5 + renumbered step 6:

```markdown
5. **Load the routing catalog** (know-what-exists, NOT read-all). Build a compact table of routed resources so their triggers are in context before work starts:
   - **Discover** recursively under `flightdeck/checklists/` and `flightdeck/incident-reports/` (exclude anything under `landed/`): every flat `*.md`, and every subdirectory `README.md`.
   - **Read and parse** each file's frontmatter (the YAML between `---`) as YAML — do not pattern-match a single line; multi-line / quoted / comma-bearing `when_to_read` values must survive.
   - **Extract** per file: path, `when_to_read`, `applies_to`, `last_updated`. Do NOT extract `skip_when` (it is a match-time negative-routing concern, not a catalog one).
   - **Classify by kind**: flat file in `checklists/` → checklist; flat file in `incident-reports/` → incident-report; subdirectory `README.md` with `bundle: true` → bundle; subdirectory `README.md` lacking `bundle: true` → malformed bundle.
   - **Do NOT list bundle leaves** (non-README files inside a bundle): they carry no routing frontmatter and are reached via the README's `reading_order`. Listing them breaks the single-entry guarantee.
   - **Never let a file vanish**: if frontmatter won't parse or `when_to_read` is missing, still list the file with a `⚠ parse error` / `⚠ missing when_to_read` marker. All markers are non-blocking — preflight is read-only; hard-fail enforcement stays in `workflow` / `walkaround`.
   - Print the catalog in the grouped format defined in [Output format](#output-format).
6. **All reconciled → execute the first "Next session" item.**
   Before executing, match the task's keywords / touched paths against the catalog's `applies_to` and load the matching bodies. Then state the item back to the user in one sentence ("Executing: [item description]") and proceed.
```

- [ ] **Step 2: Verify the edit reads correctly**

Run: read `skills/preflight/SKILL.md` lines around `## Run this checklist exactly`.
Expected: steps run 1→6 with no duplicate or skipped numbers; new step 5 is the catalog; step 6 is execute and includes the "match against `applies_to`" sentence.

- [ ] **Step 3: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "feat(preflight): add routing-catalog build step"
```

---

## Task 2: Add the grouped catalog block to the Output format section

**Files:**
- Modify: `skills/preflight/SKILL.md` — the `## Output format` section.

- [ ] **Step 1: Replace the "Report concisely" example block**

Find:

```markdown
Report concisely:

```
Cockpit reconciled (Last updated: 2026-05-25; Active focus: <X>; tree clean)
Next session item #1: <item description>

Proceeding.
```
```

Replace with:

````markdown
Report concisely:

```
Cockpit reconciled (Last updated: 2026-05-25; Active focus: <X>; tree clean)

Routing catalog (loaded this session — know-what-exists, not read-all):

[Checklists]
| File | when_to_read | applies_to | last_updated |
|---|---|---|---|
| checklists/comments.md | before writing or editing any source-code comment | comments, code-style, documentation | 2026-05-29 |

[Incident reports]
| File | when_to_read | applies_to | last_updated |
|---|---|---|---|
| incident-reports/parser-recursion.md | before designing a recursive parser | parser, recursion | 2026-04-02 |

[Bundles]  (read the README first; leaves load via its reading_order)
| README | when_to_read | applies_to | last_updated |
|---|---|---|---|
| checklists/plugin-spec/README.md | before authoring a plugin spec | plugin, spec | 2026-05-30 |

[Malformed bundles]  (omitted when none)
| README | issue |
|---|---|
| checklists/foo/README.md | ⚠ missing bundle: true |

Next session item #1: <item description>

→ Matching task keywords against applies_to before executing. Catalog is know-what-exists only — NOT a substitute for /flightdeck:walkaround, and does not mean these files were read. Bodies load on demand when a trigger matches.

Proceeding.
```

Grouping rules: one group per kind, explicit `[...]` headers; a bundle goes under `[Bundles]` regardless of whether it lives in `checklists/` or `incident-reports/`; a subdirectory `README.md` without `bundle: true` goes under `[Malformed bundles]`, never `[Bundles]`. Omit any group with no entries. If there are no routed resources at all, print `Routing catalog: (empty — no routed resources yet)`.
````

- [ ] **Step 2: Verify**

Run: read the `## Output format` section.
Expected: four possible groups present in the example (`[Checklists]`, `[Incident reports]`, `[Bundles]`, `[Malformed bundles]`), 4-column tables for the resource groups, the `→` boundary line, and the empty-catalog fallback sentence.

- [ ] **Step 3: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "docs(preflight): add grouped routing-catalog output format"
```

---

## Task 3: Update the preflight `description` frontmatter

**Files:**
- Modify: `skills/preflight/SKILL.md` — the YAML frontmatter `description:` line.

- [ ] **Step 1: Replace the description line**

Find:

```yaml
description: Use when explicitly invoking the flightdeck entry ritual — reconciles cockpit.md against repo state, runs staleness check, and reports the first "next session" item. Triggered by `/flightdeck:preflight`.
```

Replace with:

```yaml
description: Use when explicitly invoking the flightdeck entry ritual — reconciles cockpit.md against repo state, runs the staleness check, surfaces stale kneeboard files, loads a routing catalog (checklists / incident-reports / bundle READMEs with their when_to_read + last_updated), and reports the first "next session" item. Triggered by `/flightdeck:preflight`.
```

- [ ] **Step 2: Verify**

Run: read the frontmatter block (top of file, between the first pair of `---`).
Expected: `description:` mentions the routing catalog; `name: preflight` and `disable-model-invocation: true` unchanged.

- [ ] **Step 3: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "docs(preflight): mention routing catalog in skill description"
```

---

## Task 4: Record in CHANGELOG (VERSION unchanged)

**Files:**
- Modify: `CHANGELOG.md` — under the current unreleased version heading `## [1.1.0] — 2026-05-30`, in its `### Added` list.
- Confirm: `VERSION` is `1.1.0` (already bumped this cycle for the bundles work; this feature ships in the same unreleased minor — do NOT bump again).

- [ ] **Step 1: Add the bullet**

Under `## [1.1.0] — 2026-05-30` → `### Added`, append:

```markdown
- **preflight routing catalog** — `/flightdeck:preflight` now reads + parses the frontmatter of `checklists/` / `incident-reports/` flat files and bundle `README.md`s (recursively, excluding `landed/`) and prints a grouped catalog (`[Checklists]` / `[Incident reports]` / `[Bundles]` / `[Malformed bundles]`) with `when_to_read` + `applies_to` + `last_updated`, so routed triggers are in context at entry. Know-what-exists only (not read-all, not a `walkaround` substitute); leaves excluded; unparseable / missing-`when_to_read` / missing-`bundle:true` files surfaced with `⚠` markers rather than dropped. See `flightdeck/specs/2026-05-30-preflight-routing-catalog-design.md`.
```

- [ ] **Step 2: Confirm VERSION**

Run: read `VERSION`.
Expected: `1.1.0`. If it reads `1.0.0`, set it to `1.1.0`; otherwise leave unchanged.

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md VERSION
git commit -m "docs: changelog entry for preflight routing catalog"
```

---

## Task 5: Dogfood verification against a fixture flightdeck

This is the "test". There is no unit-test harness; verification = follow the updated `skills/preflight/SKILL.md` catalog step against a controlled fixture and assert each spec requirement against the produced output.

**Files:**
- Create (scratch, do NOT commit): a fixture tree under a temp directory, e.g. `./.tmp-preflight-fixture/flightdeck/`.

- [ ] **Step 1: Build the fixture**

Create these files (frontmatter exactly as shown):

`./.tmp-preflight-fixture/flightdeck/cockpit.md`:
```markdown
# Cockpit — fixture

**Last updated**: 2026-05-30 by tester
**Active focus**: verifying the routing catalog

## Next session
1. confirm the catalog renders

## Hanging tasks
- (none)
```

`./.tmp-preflight-fixture/flightdeck/checklists/comments.md`:
```markdown
---
when_to_read: before writing or editing any source-code comment
applies_to: [comments, code-style, documentation]
last_updated: 2026-05-29
---
# Comments
body
```

`./.tmp-preflight-fixture/flightdeck/checklists/no-trigger.md` (missing `when_to_read`):
```markdown
---
applies_to: [misc]
last_updated: 2026-05-01
---
# No trigger
body
```

`./.tmp-preflight-fixture/flightdeck/incident-reports/parser-recursion.md`:
```markdown
---
when_to_read: before designing a recursive parser
applies_to: [parser, recursion]
last_updated: 2026-04-02
---
# Parser recursion
body
```

`./.tmp-preflight-fixture/flightdeck/checklists/plugin-spec/README.md` (valid bundle):
```markdown
---
bundle: true
when_to_read: before authoring a plugin spec
applies_to: [plugin, spec]
reading_order: [01-intro.md]
last_updated: 2026-05-30
---
# Plugin spec bundle
```
`./.tmp-preflight-fixture/flightdeck/checklists/plugin-spec/01-intro.md` (leaf, no routing frontmatter):
```markdown
# Intro
leaf body
```

`./.tmp-preflight-fixture/flightdeck/checklists/foo/README.md` (malformed bundle — no `bundle: true`):
```markdown
---
when_to_read: something
---
# Foo
```

`./.tmp-preflight-fixture/flightdeck/landed/checklists/old.md` (must be ignored):
```markdown
---
when_to_read: should never appear
applies_to: [archived]
last_updated: 2020-01-01
---
# Old
```

- [ ] **Step 2: Run preflight against the fixture**

Execute the `## Run this checklist exactly` steps of `skills/preflight/SKILL.md` (specifically the new step 5) treating `./.tmp-preflight-fixture/flightdeck/` as the flightdeck root. Capture the printed Routing catalog block.

- [ ] **Step 3: Assert each requirement**

Check the captured output against the spec's Verification list:

1. `checklists/comments.md` appears under `[Checklists]` with `when_to_read = "before writing or editing any source-code comment"` and `last_updated = 2026-05-29`. — PASS/FAIL
2. `incident-reports/parser-recursion.md` appears under `[Incident reports]`. — PASS/FAIL
3. `checklists/plugin-spec/README.md` appears under `[Bundles]`; **`01-intro.md` (the leaf) appears NOWHERE** in the catalog. — PASS/FAIL
4. `checklists/foo/README.md` appears under `[Malformed bundles]` with `⚠ missing bundle: true` — NOT under `[Bundles]`, not hidden. — PASS/FAIL
5. `checklists/no-trigger.md` is listed with `⚠ missing when_to_read` (not dropped). — PASS/FAIL
6. `landed/checklists/old.md` appears NOWHERE. — PASS/FAIL
7. Negative case: after printing the catalog, NO checklist/incident body was read (the step is read-frontmatter-only; bodies load only on a matching task trigger). — PASS/FAIL

Expected: all 7 PASS.

- [ ] **Step 4: Empty-catalog case**

Make a second fixture with only `cockpit.md` (no `checklists/` or `incident-reports/`). Run step 5 against it.
Expected: prints `Routing catalog: (empty — no routed resources yet)`, no error.

- [ ] **Step 5: Clean up the fixtures**

```bash
rm -rf ./.tmp-preflight-fixture ./.tmp-preflight-fixture-empty
```

No commit (fixtures are scratch; nothing committed from this task).

---

## Notes for the executor

- **Do not** add a "writing code / comments → checklists/" row to the scenario table in `skills/workflow/SKILL.md`. That is explicitly out of scope (separate change).
- **Do not** create a stored catalog file, touch the SessionStart hook, or add a walkaround audit. Approach A is ephemeral-only.
- If `VERSION` or the CHANGELOG heading differs from what Task 4 expects (e.g. someone released 1.1.0 in the meantime), open a new `## [Unreleased]` section and put the bullet there, and bump `VERSION` to the next minor.
