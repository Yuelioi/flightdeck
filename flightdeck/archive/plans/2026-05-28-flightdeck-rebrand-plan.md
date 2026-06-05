# Flightdeck Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the project from `workshop` to `flightdeck`, decompose the overloaded `board.md` into `cockpit.md` + `manifest.md` + `logbook.md`, and ship as v1.0.

**Architecture:** Single feature branch (`flightdeck-rebrand`). Each phase is one logical commit, leaving the project broken on branch but atomic per phase. Final phase tags v1.0.0 and merges. No new code — the entire change is renaming files, restructuring the dogfood directory, rewriting markdown, and updating 4 plugin manifests.

**Tech Stack:** Markdown, JSON, PowerShell/bash scripts, Claude Code slash skills. No tests in the unit-test sense — verification is `grep -r workshop` returning expected counts plus manual slash-skill invocation.

**Reference spec:** [workshop/specs/2026-05-28-flightdeck-rebrand-design.md](../specs/2026-05-28-flightdeck-rebrand-design.md) (becomes `flightdeck/specs/...` after Phase 1).

**Path note:** This plan file lives at `workshop/plans/2026-05-28-flightdeck-rebrand-plan.md` initially. Phase 1 renames the project's own workshop dir to flightdeck, so by Task 1.5 this plan file moves to `flightdeck/flight-plans/2026-05-28-flightdeck-rebrand-plan.md`. The executing agent must follow the file as it moves.

---

## Phase 0 — Pre-flight

### Task 0.1: Re-read spec with dogfood findings in hand

**Files:**
- Read: `workshop/specs/2026-05-28-flightdeck-rebrand-design.md`
- Read: `workshop/scars/*.md` if any new files since 2026-05-28 (currently empty dir)
- Read: `workshop/wip/*.md` if any unresolved items

**Context:** The spec notes "Pending dogfood-week completion (~2026-06-02) before implementation; findings may amend the Decisions section." Today's date (when executing) determines whether dogfood week is complete.

- [ ] **Step 1: Check execution date vs dogfood window**

```bash
date +%F
```

If date is before 2026-06-02: STOP. Dogfood week is not complete. Resume this plan on or after 2026-06-02.

- [ ] **Step 2: List new scars / wip since 2026-05-28**

```bash
git -C E:/projects/tools/workshop log --since="2026-05-28" --name-only --pretty=format: -- workshop/scars/ workshop/wip/ | grep -v '^$' | sort -u
```

Expected: list of files added/modified since spec was written. Could be empty.

- [ ] **Step 3: For each dogfood finding, decide impact on spec**

For each scar / wip surfaced in Step 2, classify:
- **No impact** — finding is orthogonal to rebrand
- **Minor amendment** — single decision needs adjustment (e.g., a different folder name)
- **Material amendment** — protocol-level finding (e.g., board.md split needs different sections)

If ANY material amendment: amend the spec, commit the amendment as a separate commit before proceeding to Task 0.2. Use `MODIFIED:` markers per [workshop spec evolution markers](../../skills/workshop-workflow/templates.md#spec-evolution-markers-optional-convention) if changes are non-trivial.

- [ ] **Step 4: Commit (only if amendments were made)**

```bash
git -C E:/projects/tools/workshop add workshop/specs/2026-05-28-flightdeck-rebrand-design.md
git -C E:/projects/tools/workshop commit -m "design: amend flightdeck rebrand spec with dogfood findings"
```

If no amendments: skip the commit; proceed to Task 0.2.

---

### Task 0.2: Create feature branch

**Files:** none

- [ ] **Step 1: Verify main is clean**

```bash
git -C E:/projects/tools/workshop status
```

Expected: `working tree clean` or only the plan/spec from Phase 0 amendments staged.

- [ ] **Step 2: Create + switch branch**

```bash
git -C E:/projects/tools/workshop checkout -b flightdeck-rebrand
```

Expected: `Switched to a new branch 'flightdeck-rebrand'`

---

## Phase 1 — Restructure project's own workshop dir (dogfood the new layout)

This phase migrates the maintainer's own workshop/ to the new structure. Doing it first means subsequent phases can reference real flightdeck/ paths.

### Task 1.1: Split workshop/board.md into cockpit + manifest + logbook

**Files:**
- Read: `workshop/board.md`
- Create: `workshop/cockpit.md`
- Create: `workshop/manifest.md`
- Create: `workshop/logbook.md`
- Delete (after): `workshop/board.md`

- [ ] **Step 1: Read current board.md and locate section boundaries**

```bash
grep -n '^## ' E:/projects/tools/workshop/workshop/board.md
```

Expected section headers (per current state on 2026-05-28):
- `## Next session`
- `## In flight (only artifacts whose state diverges from folder location)`
- `## Blockers`
- `## Deferred`
- `## Recently finished (cap 5, FIFO)`
- `## Hanging tasks`
- `## Note on dogfooding`

Section routing per spec:
- cockpit.md: header (Last updated + Active focus) + `Next session` + `Hanging tasks` + `Note on dogfooding`
- manifest.md: `In flight` + `Blockers`
- logbook.md: `Recently finished` + `Deferred`

- [ ] **Step 2: Write workshop/cockpit.md**

Content template (fill from current board.md values):

```markdown
# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: <copy from board.md verbatim>
**Active focus**: <copy from board.md verbatim>

## Next session

<copy entire "Next session" section from board.md>

## Hanging tasks

<copy "Hanging tasks" section from board.md — likely "(none)">

## Note on dogfooding

<copy "Note on dogfooding" section from board.md>

---

**Cockpit hygiene** (skill: flightdeck-workflow):
- **80 lines hard ceiling.** Cockpit is intentionally ephemeral and operational. Historical / archival content does not live here — it goes to logbook.md.
- `Last updated` bumps ONLY when: Next session changes / Active focus shifts / a major task completes. Not on typo fixes, grep, or routine commits.
- If something feels permanent or referential, it does not belong in cockpit — move to logbook.md or out entirely.
```

- [ ] **Step 3: Write workshop/manifest.md**

Content template:

```markdown
# Manifest — flightdeck open work

> On-demand read. Open only when picking up an artifact flagged with a divergent state, or when investigating a blocker. Not part of the entry ritual.

## In flight (only artifacts whose state diverges from folder location)

<copy "In flight" section from board.md verbatim — table + status legend>

## Blockers

<copy "Blockers" section from board.md verbatim>

---

**Manifest hygiene**:
- Only lists artifacts with explicit `state:` frontmatter (the divergent ones). Implicit ⚪/🟡/✅ state is inferred from folder location and does NOT belong here.
- No line ceiling. Content is structurally bounded by state-divergence — if it grows, the project genuinely has many divergent artifacts.
```

- [ ] **Step 4: Write workshop/logbook.md**

Content template:

```markdown
# Logbook — flightdeck history

> Rarely read. Open when writing release notes, doing retrospectives, or auditing what was done across past sessions.

## Recently finished (cap 5, FIFO)

<copy "Recently finished" section from board.md verbatim>

## Deferred

<copy "Deferred" section from board.md verbatim>

---

**Logbook hygiene**:
- `Recently finished` cap 5 entries FIFO. Per-entry summary ≤ 3 lines. Longer content → link to commit / archived plan.
- `Deferred` items live here as long as they remain deferred. Promote out when actively worked on.
- No date-bumping rule — logbook is append-mostly history.
```

- [ ] **Step 5: Verify content preservation**

```bash
wc -l E:/projects/tools/workshop/workshop/board.md
wc -l E:/projects/tools/workshop/workshop/cockpit.md E:/projects/tools/workshop/workshop/manifest.md E:/projects/tools/workshop/workshop/logbook.md
```

Expected: total lines of three new files ≈ board.md ± 10 lines (for new headers / hygiene blocks).

```bash
grep -c 'v0.8.0' E:/projects/tools/workshop/workshop/logbook.md
```

Expected: ≥ 1 (the v0.8.0 finished entry made it).

- [ ] **Step 6: Verify cockpit.md respects ceiling**

```bash
wc -l E:/projects/tools/workshop/workshop/cockpit.md
```

Expected: ≤ 80. If over, the migration over-stuffed cockpit — move content to logbook until under.

- [ ] **Step 7: Delete board.md**

```bash
rm E:/projects/tools/workshop/workshop/board.md
```

- [ ] **Step 8: Commit**

```bash
git -C E:/projects/tools/workshop add -A workshop/
git -C E:/projects/tools/workshop commit -m "refactor: split workshop/board.md into cockpit + manifest + logbook"
```

---

### Task 1.2: Rename workshop subfolders + move finish/ to landed/

**Files:**
- Rename: `workshop/plans/` → `workshop/flight-plans/`
- Rename: `workshop/wip/` (currently empty) → `workshop/kneeboard/`
- Create: `workshop/landed/`
- Move: `workshop/flight-plans/finish/*` → `workshop/landed/flight-plans/*` and delete the now-empty `workshop/flight-plans/finish/`

Current dogfood workshop contains: `plans/`, `plans/finish/`, `specs/`, `wip/`. No playbooks/scars/critiques/reference/sketches exist yet.

- [ ] **Step 1: Verify pre-state**

```bash
ls E:/projects/tools/workshop/workshop/
```

Expected: `cockpit.md  logbook.md  manifest.md  plans/  specs/  wip/`

- [ ] **Step 2: Rename plans → flight-plans**

```bash
git -C E:/projects/tools/workshop mv workshop/plans workshop/flight-plans
```

- [ ] **Step 3: Rename wip → kneeboard**

```bash
git -C E:/projects/tools/workshop mv workshop/wip workshop/kneeboard
```

If wip is empty, git mv may fail (git tracks files, not empty dirs). In that case:

```bash
mkdir E:/projects/tools/workshop/workshop/kneeboard
rmdir E:/projects/tools/workshop/workshop/wip
```

- [ ] **Step 4: Move flight-plans/finish/* into landed/flight-plans/**

```bash
mkdir -p E:/projects/tools/workshop/workshop/landed/flight-plans
git -C E:/projects/tools/workshop mv workshop/flight-plans/finish/* workshop/landed/flight-plans/
rmdir E:/projects/tools/workshop/workshop/flight-plans/finish
```

- [ ] **Step 5: Verify post-state**

```bash
ls E:/projects/tools/workshop/workshop/
```

Expected: `cockpit.md  flight-plans/  kneeboard/  landed/  logbook.md  manifest.md  specs/`

```bash
ls E:/projects/tools/workshop/workshop/landed/flight-plans/
```

Expected: the 3 finished plan files (`2026-05-25-v0.6-cleanup.md`, `2026-05-26-v0.7-cross-tool-reach.md`, `2026-05-26-v0.8-lifecycle-deepening.md`).

- [ ] **Step 6: Commit**

```bash
git -C E:/projects/tools/workshop add -A workshop/
git -C E:/projects/tools/workshop commit -m "refactor: rename workshop subfolders to flightdeck naming"
```

---

### Task 1.3: Rename top-level workshop/ → flightdeck/

**Files:**
- Rename: `workshop/` → `flightdeck/` (and everything inside it moves with it, including this plan file)

- [ ] **Step 1: Verify current branch + clean state**

```bash
git -C E:/projects/tools/workshop status
git -C E:/projects/tools/workshop branch --show-current
```

Expected: clean tree, on `flightdeck-rebrand`.

- [ ] **Step 2: Rename**

```bash
git -C E:/projects/tools/workshop mv workshop flightdeck
```

- [ ] **Step 3: Verify**

```bash
ls E:/projects/tools/workshop/flightdeck/
ls E:/projects/tools/workshop/workshop 2>&1
```

Expected: flightdeck dir exists with cockpit/manifest/logbook/specs/flight-plans/kneeboard/landed; `workshop` directory does not exist.

**Note for executing agent:** this plan file is now at `E:/projects/tools/workshop/flightdeck/flight-plans/2026-05-28-flightdeck-rebrand-plan.md`. The spec is at `flightdeck/specs/...`. Reference links from this point use the new paths.

- [ ] **Step 4: Commit**

```bash
git -C E:/projects/tools/workshop add -A
git -C E:/projects/tools/workshop commit -m "refactor: rename workshop/ -> flightdeck/ at project root"
```

---

## Phase 2 — Rename skill modules

The project ships 5 skill modules. After this phase: `flightdeck-workflow/`, `preflight/`, `landing/`, `walkaround/`, `emit-agents-md/` (last one unchanged).

### Task 2.1: Rename skill module directories

**Files:**
- Rename: `skills/workshop-workflow/` → `skills/flightdeck-workflow/`
- Rename: `skills/session-enter/` → `skills/preflight/`
- Rename: `skills/session-exit/` → `skills/landing/`
- Rename: `skills/doctor/` → `skills/walkaround/`

- [ ] **Step 1: Rename all four module directories**

```bash
cd E:/projects/tools/workshop
git mv skills/workshop-workflow skills/flightdeck-workflow
git mv skills/session-enter skills/preflight
git mv skills/session-exit skills/landing
git mv skills/doctor skills/walkaround
```

- [ ] **Step 2: Verify**

```bash
ls E:/projects/tools/workshop/skills/
```

Expected: `emit-agents-md  flightdeck-workflow  landing  preflight  walkaround`

- [ ] **Step 3: Commit**

```bash
git -C E:/projects/tools/workshop commit -m "refactor: rename skill module directories to flightdeck names"
```

---

### Task 2.2: Update SKILL.md frontmatter for renamed modules

**Files:**
- Modify: `skills/flightdeck-workflow/SKILL.md`
- Modify: `skills/preflight/SKILL.md`
- Modify: `skills/landing/SKILL.md`
- Modify: `skills/walkaround/SKILL.md`
- Modify: `skills/emit-agents-md/SKILL.md` (description updates only)

Each SKILL.md has a frontmatter `name:` and `description:` field. The slash-skill name (e.g., `/workshop:session-enter`) is derived from `name:`, so updating it changes the user-visible command.

- [ ] **Step 1: Update flightdeck-workflow/SKILL.md frontmatter**

Open `skills/flightdeck-workflow/SKILL.md`. Find the frontmatter block at the top. Change:

```yaml
name: workshop-workflow
description: Use when a project has a workshop/ directory, when starting one, or when AI session context needs to survive across sessions
```

To:

```yaml
name: flightdeck-workflow
description: Use when a project has a flightdeck/ directory, when starting one, or when AI session context needs to survive across sessions
```

- [ ] **Step 2: Update preflight/SKILL.md frontmatter**

Change:

```yaml
name: session-enter
description: Use when explicitly invoking the workshop entry ritual — reconciles board.md against repo state, runs staleness check, and reports the first "next session" item. Triggered by `/workshop:session-enter`.
```

To:

```yaml
name: preflight
description: Use when explicitly invoking the flightdeck entry ritual — reconciles cockpit.md against repo state, runs staleness check, and reports the first "next session" item. Triggered by `/flightdeck:preflight`.
```

- [ ] **Step 3: Update landing/SKILL.md frontmatter**

Open the file, replace `name: session-exit` → `name: landing`. Update description to say "flightdeck landing ritual" and replace `/workshop:session-exit` reference with `/flightdeck:landing`. Replace any `board.md` reference with `cockpit.md`.

- [ ] **Step 4: Update walkaround/SKILL.md frontmatter**

Open the file, replace `name: doctor` → `name: walkaround`. Update description: replace "workshop" with "flightdeck", replace medical-check framing with pre-flight inspection framing. Replace `/workshop:doctor` with `/flightdeck:walkaround`.

- [ ] **Step 5: Update emit-agents-md/SKILL.md frontmatter**

Name stays `emit-agents-md`. Description still references the project context — replace `workshop` with `flightdeck` wherever it appears in the description and body.

- [ ] **Step 6: Verify each SKILL.md still has required frontmatter fields**

```bash
for f in E:/projects/tools/workshop/skills/*/SKILL.md; do
  echo "=== $f ==="
  head -5 "$f"
done
```

Expected: each has `---`, `name:`, `description:`, `---` at the top.

- [ ] **Step 7: Commit**

```bash
git -C E:/projects/tools/workshop add skills/
git -C E:/projects/tools/workshop commit -m "refactor: update skill module frontmatter for flightdeck rename"
```

---

### Task 2.3: Replace workshop/board.md references throughout skill module bodies

**Files:**
- Modify: every `.md` file under `skills/`

Skill module bodies reference `workshop/board.md`, folder names like `workshop/plans/`, slash commands like `/workshop:session-enter`, etc. All need updating.

- [ ] **Step 1: Inventory affected files**

```bash
grep -rl 'workshop' E:/projects/tools/workshop/skills/
```

Expected: every SKILL.md, plus folder-semantics.md, templates.md, exit-ritual.md inside flightdeck-workflow.

- [ ] **Step 2: Replace via per-file Edit calls**

For each file in Step 1, apply these `Edit replace_all` substitutions (in this order — order matters because `workshop/board.md` is more specific than `workshop/`):

| Find | Replace |
| --- | --- |
| `workshop/board.md` | `flightdeck/cockpit.md` |
| `workshop/plans/finish` | `flightdeck/landed/flight-plans` |
| `workshop/specs/finish` | `flightdeck/landed/specs` |
| `workshop/plans/` | `flightdeck/flight-plans/` |
| `workshop/playbooks/` | `flightdeck/checklists/` |
| `workshop/scars/` | `flightdeck/incident-reports/` |
| `workshop/reference/` | `flightdeck/charts/` |
| `workshop/critiques/` | `flightdeck/safety-reviews/` |
| `workshop/wip/` | `flightdeck/kneeboard/` |
| `workshop/sketches/` | `flightdeck/sketches/` (no rename, only top-level prefix) |
| `workshop/specs/` | `flightdeck/specs/` (no rename, only top-level prefix) |
| `workshop/INDEX.md` | `flightdeck/INDEX.md` |
| `/workshop:session-enter` | `/flightdeck:preflight` |
| `/workshop:session-exit` | `/flightdeck:landing` |
| `/workshop:doctor` | `/flightdeck:walkaround` |
| `/workshop:emit-agents-md` | `/flightdeck:emit-agents-md` |
| `workshop-workflow` | `flightdeck-workflow` (skill module name) |
| `workshop/` (top-level folder mention, no subpath) | `flightdeck/` |
| `Workshop` (capitalized product name in prose) | `Flightdeck` |
| ` workshop ` (with surrounding spaces — generic word, careful) | manual review per file |
| `board.md` (when referring to the file convention, not a path) | `cockpit.md / manifest.md / logbook.md` (or just `cockpit.md` if context is the entry-point file) |
| `wip/` (folder convention prose) | `kneeboard/` |
| `playbooks/` (folder convention prose) | `checklists/` |
| `scars/` (folder convention prose) | `incident-reports/` |
| `reference/` (folder convention prose) | `charts/` |
| `critiques/` (folder convention prose) | `safety-reviews/` |
| `plans/` (folder convention prose) | `flight-plans/` |
| `finish/` (when describing the archive subdir convention) | `landed/<type>/` (note: structure changes from nested to umbrella) |

**Special case**: `folder-semantics.md` describes the folder set in detail. Its body needs structural revision (new umbrella `landed/`, three new entry files cockpit/manifest/logbook). Plan to:
- Replace the "10 folders" intro with "11 files/folders" (3 root .md + 8 directories) and update the tree diagram.
- Add a new section describing cockpit.md / manifest.md / logbook.md with the read-time rationale (lifted from the spec).
- Rewrite the `board.md` section to point at cockpit.md.
- Rewrite the `wip/` section under the new name `kneeboard/`.
- Update the naming convention table at line ~148-157 to use new folder names.

**Special case**: `templates.md` doesn't reference workshop folders by name in templates themselves (templates are content), but cross-folder reference syntax examples do. Update the examples.

**Special case**: `SKILL.md` of `flightdeck-workflow` has the authority order line. Replace it per the spec's new authority order block (see spec § board.md decomposition).

- [ ] **Step 3: Verify no stale workshop references in skills/**

```bash
grep -rn 'workshop' E:/projects/tools/workshop/skills/
```

Expected: zero results, OR only intentional historical references like "(previously named workshop)" in a migration note.

If results exist that should remain (e.g., a quote of an old commit message), audit case-by-case.

- [ ] **Step 4: Commit**

```bash
git -C E:/projects/tools/workshop add skills/
git -C E:/projects/tools/workshop commit -m "refactor: replace workshop -> flightdeck references in skill bodies"
```

---

### Task 2.4: Surface the governing principle into post-v1.0 docs

**Files:**
- Modify: `skills/flightdeck-workflow/SKILL.md`

**Context:** The spec's "Design warning" section establishes a governing principle — **"Semantic clarity outranks thematic consistency."** — that the spec calls "load-bearing". The spec archives to `landed/specs/` after v1.0 ships and loses to current state per authority order. Without lifting this principle to persistent surface, it dies in archive.

Plan: surface the principle in `skills/flightdeck-workflow/SKILL.md` (auto-loaded every session) at minimum. README.md and AGENTS.md surface in their respective tasks (5.1, 5.2).

- [ ] **Step 1: Add design-philosophy section to flightdeck-workflow/SKILL.md**

Locate an appropriate position — after the "Authority order" section, before "Lifecycle of specs and plans". Add this new section:

```markdown
## Design philosophy

> **Semantic clarity outranks thematic consistency.**

When naming or structuring decisions trigger a conflict between "fits the aviation metaphor" and "reads correctly", clarity wins. The flightdeck metaphor is used because it sharpens operational intent — *not* as a theme to be applied uniformly. Two folders (`specs/`, `sketches/`) intentionally use neutral names because no aviation equivalent improves them. Future concepts face the same test.

Reject:
- aviation roleplay / sci-fi theming / meme interfaces / gamified agent cosplay
- "cute but unclear" terms (e.g., `/stuck → /request-vector` is rejected — `/stuck` already reads correctly)
- forcing every new term into the metaphor
```

- [ ] **Step 2: Verify section exists and renders correctly**

```bash
grep -A 5 'Design philosophy' E:/projects/tools/workshop/skills/flightdeck-workflow/SKILL.md
```

Expected: the heading + first sentence + bullet list visible.

- [ ] **Step 3: Commit**

```bash
git -C E:/projects/tools/workshop add skills/flightdeck-workflow/SKILL.md
git -C E:/projects/tools/workshop commit -m "skill: surface 'semantic clarity outranks thematic consistency' as project principle"
```

---

## Phase 3 — Scaffolds

### Task 3.1: Rename scaffold root directories and inner content

**Files:**
- Rename: `scaffolds/full/workshop/` → `scaffolds/full/flightdeck/`
- Rename: `scaffolds/minimal/workshop/` → `scaffolds/minimal/flightdeck/`
- Modify: every file inside both scaffold dirs to reflect new layout

- [ ] **Step 1: Inspect current scaffold contents**

```bash
find E:/projects/tools/workshop/scaffolds -type f | sort
```

- [ ] **Step 2: Rename top-level scaffold dirs**

```bash
cd E:/projects/tools/workshop
git mv scaffolds/full/workshop scaffolds/full/flightdeck
git mv scaffolds/minimal/workshop scaffolds/minimal/flightdeck
```

- [ ] **Step 3: Rename inner subdirs in full scaffold**

The full scaffold should mirror the flightdeck layout: cockpit.md (template), manifest.md (template), logbook.md (template), specs/, flight-plans/, checklists/, incident-reports/, charts/, sketches/, safety-reviews/, kneeboard/, landed/.

Inspect what currently exists and rename / create as needed.

```bash
ls E:/projects/tools/workshop/scaffolds/full/flightdeck/
```

For each subdir that needs renaming, use `git mv`. If a subdir doesn't exist in the current scaffold (e.g., `checklists/` was never in `scaffolds/full/workshop/`), create an empty placeholder only if the spec calls for it (defer to the spec — premature folder creation is itself an anti-pattern).

- [ ] **Step 4: Rewrite scaffold template files**

If `scaffolds/full/flightdeck/board.md` exists, split it into cockpit.md / manifest.md / logbook.md following Task 1.1 templates. The scaffold versions are skeletons with placeholder text like `<Active focus here>` rather than real values.

Repeat for `scaffolds/minimal/flightdeck/`. Minimal scaffold = cockpit.md only.

- [ ] **Step 5: Verify scaffolds match spec structure**

```bash
find E:/projects/tools/workshop/scaffolds -type f | sort
```

Cross-check against the spec's folder map.

- [ ] **Step 6: Commit**

```bash
git -C E:/projects/tools/workshop add scaffolds/
git -C E:/projects/tools/workshop commit -m "refactor: rebuild scaffolds for flightdeck layout"
```

---

## Phase 4 — Plugin manifests and adapters

### Task 4.1: Update all four platform manifests

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `.cursor-plugin/plugin.json`
- Modify: `gemini-extension.json`

Each manifest currently has `"name": "workshop"`, `"version": "0.8.1"`, repo URL pointing to `Yuelioi/workshop`, and Chinese/English descriptions referencing "workshop directory".

- [ ] **Step 1: Update .claude-plugin/plugin.json**

Replace:
- `"name": "workshop"` → `"name": "flightdeck"`
- `"version": "0.8.1"` → `"version": "1.0.0"`
- Description: `"Persistent workshop directory protocol for AI coding sessions — session entry, scenario triggers, write gate, and exit ritual"` → `"Operational protocol for AI-assisted engineering sessions — preflight, scenario triggers, write gate, and landing ritual"`
- `"homepage": "https://github.com/Yuelioi/workshop"` → `"https://github.com/Yuelioi/flightdeck"`
- `"repository": ...` same change
- `"keywords"`: replace `"workshop"` with `"flightdeck"`, replace `"context-persistence"` keyword unchanged, consider adding `"operations"` and `"reliability"` if relevant per spec direction

- [ ] **Step 2: Update .claude-plugin/marketplace.json**

Replace:
- `"name": "workshop-marketplace"` → `"name": "flightdeck-marketplace"`
- Description: replace `workshop` → `flightdeck`
- Inner `plugins[0].name` → `"flightdeck"`
- Inner `plugins[0].version` → `"1.0.0"`
- Inner description: same product description update

- [ ] **Step 3: Update .codex-plugin/plugin.json**

Same pattern as Step 1.

- [ ] **Step 4: Update .cursor-plugin/plugin.json**

Same as Step 1 plus:
- `"displayName": "Workshop"` → `"displayName": "Flightdeck"`

- [ ] **Step 5: Update gemini-extension.json**

Replace:
- `"name": "workshop"` → `"name": "flightdeck"`
- description: same update
- `"contextFileName": "GEMINI.md"` (unchanged — Gemini standard filename)

Note: the `.cursor-plugin/plugin.json` also has rich interface metadata (`interface.displayName`, `interface.longDescription`, `interface.defaultPrompt`). Update each prose-y field — `defaultPrompt` currently says "Pick up the thread from workshop/board.md and continue." Replace with "Pick up the thread from flightdeck/cockpit.md and continue."

- [ ] **Step 6: Verify JSON validity**

```bash
for f in E:/projects/tools/workshop/.claude-plugin/plugin.json E:/projects/tools/workshop/.claude-plugin/marketplace.json E:/projects/tools/workshop/.codex-plugin/plugin.json E:/projects/tools/workshop/.cursor-plugin/plugin.json E:/projects/tools/workshop/gemini-extension.json; do
  echo "=== $f ==="
  jq . "$f" > /dev/null && echo OK || echo INVALID
done
```

Expected: each prints `OK`.

- [ ] **Step 7: Commit**

```bash
git -C E:/projects/tools/workshop add .claude-plugin/ .codex-plugin/ .cursor-plugin/ gemini-extension.json
git -C E:/projects/tools/workshop commit -m "refactor: update plugin manifests for flightdeck v1.0"
```

---

### Task 4.2: Update adapter READMEs

**Files:**
- Modify: `adapters/claude/README.md`
- Modify: `adapters/codex/README.md`
- Modify: `adapters/cursor/README.md`
- Modify: `adapters/gemini/README.md`

- [ ] **Step 1: For each adapter README, replace product references**

Apply the same find/replace table from Task 2.3 to each adapter README.

- [ ] **Step 2: Verify no stale references**

```bash
grep -rn 'workshop' E:/projects/tools/workshop/adapters/
```

Expected: zero (or only historical mentions explicitly preserved).

- [ ] **Step 3: Commit**

```bash
git -C E:/projects/tools/workshop add adapters/
git -C E:/projects/tools/workshop commit -m "refactor: update adapter READMEs for flightdeck"
```

---

### Task 4.3: Update hooks

**Files:**
- Modify: `hooks/hooks.json` (likely unchanged structurally — references env var `CLAUDE_PLUGIN_ROOT`)
- Modify: `hooks/session-start` script
- Modify: `hooks/run-hook.cmd`

- [ ] **Step 1: Read each hook file**

```bash
cat E:/projects/tools/workshop/hooks/session-start
cat E:/projects/tools/workshop/hooks/run-hook.cmd
```

- [ ] **Step 2: Replace workshop references**

The hook scripts likely contain text like "loading workshop-workflow skill" or paths referencing `workshop/`. Apply find/replace per Task 2.3 conventions.

`hooks/session-start` script logic: it currently auto-loads the workshop-workflow skill when `workshop/` exists in cwd. The trigger condition changes to `flightdeck/` AND should also recognize legacy `workshop/` to emit a "this directory looks like a pre-v1.0 workshop — see MIGRATION.md" message. Decision: omit the legacy detection for now (user base = 1). Pure replacement: detect `flightdeck/` only.

- [ ] **Step 3: Verify hook references are consistent**

```bash
grep -n 'workshop\|flightdeck' E:/projects/tools/workshop/hooks/*
```

Audit each occurrence is intentional.

- [ ] **Step 4: Commit**

```bash
git -C E:/projects/tools/workshop add hooks/
git -C E:/projects/tools/workshop commit -m "refactor: update SessionStart hook to detect flightdeck/"
```

---

## Phase 5 — Root-level documentation

### Task 5.1: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Identify sections needing rewrite**

```bash
grep -n '^#\|^## \|workshop' E:/projects/tools/workshop/README.md
```

Expected: 50 workshop references, plus heading structure.

- [ ] **Step 2: Replace per Task 2.3 conventions**

The README opens with "# workshop" — change to "# flightdeck". Tagline currently "A persistent workbench protocol for AI coding sessions." Update to reflect the operational identity per spec direction (e.g., "An operational protocol for AI-assisted engineering sessions.").

The folder layout diagram in README must be updated to the new structure (cockpit.md / manifest.md / logbook.md / flight-plans / checklists / incident-reports / charts / sketches / safety-reviews / kneeboard / landed).

Installation instructions: replace `/plugin install workshop@workshop-marketplace` → `/plugin install flightdeck@flightdeck-marketplace`. Repeat for Cursor / Codex / Gemini install commands.

Add a short "Renamed from workshop (≤ v0.8.1)" note near the top — useful for any GitHub redirect arrivals to understand they're in the right place. Point to `MIGRATION.md` for upgrade steps.

Add a "Design philosophy" subsection (or quote-callout) somewhere after the "Why it exists" section, containing the governing principle:

> **Semantic clarity outranks thematic consistency.** The flightdeck metaphor sharpens operational intent — it is not a theme to apply uniformly. Two folders (`specs/`, `sketches/`) keep neutral names because no aviation equivalent improves them.

- [ ] **Step 3: Verify**

```bash
grep -n 'workshop' E:/projects/tools/workshop/README.md
```

Expected: a handful (only the deliberate "previously named workshop" mentions in the migration note).

---

### Task 5.2: Update README.zh.md, AGENTS.md, GEMINI.md, TEST_PLAN.md

**Files:**
- Modify: `README.zh.md`
- Modify: `AGENTS.md`
- Modify: `GEMINI.md`
- Modify: `TEST_PLAN.md`

- [ ] **Step 1: README.zh.md**

Same updates as README.md but in Chinese. The header "workshop" → "flightdeck" (keep English name since it's a product name). Tagline translates to operational identity. Layout diagram and install commands match English version.

Open question from spec: should README.zh.md remain full parity, or shift to English-first with Chinese summary? Default: keep full parity (the user has so far written README.zh.md as full mirror — preserve convention). If user has signaled a change, follow that.

- [ ] **Step 2: AGENTS.md**

AGENTS.md content is auto-generated by `/flightdeck:emit-agents-md` skill. After updating the skill (Task 2.3 already updated descriptions; the templated content the skill emits may still reference workshop paths — verify by reading the skill body).

Manual approach for v1.0: rewrite AGENTS.md by hand to reference flightdeck paths. Future emits regenerate to the same content.

Include the governing principle in AGENTS.md so other AI tools see it. Add a "Design principle" line near the top:

```markdown
**Design principle**: Semantic clarity outranks thematic consistency. The flightdeck aviation metaphor is used where it sharpens operational intent — not as a theme to apply uniformly. Neutral names (`specs/`, `sketches/`) are intentional.
```

- [ ] **Step 3: GEMINI.md**

Same as AGENTS.md — replace workshop references.

- [ ] **Step 4: TEST_PLAN.md**

Replace workshop references. If TEST_PLAN.md is a scenario list (S1–S6 per earlier specs), update each scenario to reference flightdeck paths / commands.

- [ ] **Step 5: Commit**

```bash
git -C E:/projects/tools/workshop add README.md README.zh.md AGENTS.md GEMINI.md TEST_PLAN.md
git -C E:/projects/tools/workshop commit -m "docs: rewrite README + agent files for flightdeck v1.0"
```

---

### Task 5.3: Update install scripts, .github templates, VERSION

**Files:**
- Modify: `install.sh`
- Modify: `install.ps1`
- Modify: `.github/PULL_REQUEST_TEMPLATE/manifest-verification.md`
- Modify: `VERSION`

- [ ] **Step 1: install.sh and install.ps1**

These scripts likely contain the marketplace install command and a self-check. Apply find/replace per Task 2.3.

- [ ] **Step 2: PR template**

`.github/PULL_REQUEST_TEMPLATE/manifest-verification.md` is the community-PR template for verifying Codex/Cursor/Gemini behavior. Update product name and command references.

- [ ] **Step 3: VERSION bump**

```bash
echo "1.0.0" > E:/projects/tools/workshop/VERSION
```

- [ ] **Step 4: Commit**

```bash
git -C E:/projects/tools/workshop add install.sh install.ps1 .github/ VERSION
git -C E:/projects/tools/workshop commit -m "build: bump VERSION to 1.0.0, update install scripts + PR template"
```

---

### Task 5.4: Write CHANGELOG v1.0.0 entry

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Read existing changelog structure**

```bash
head -50 E:/projects/tools/workshop/CHANGELOG.md
```

Note the style (date format, section headers, etc.).

- [ ] **Step 2: Add v1.0.0 entry at top**

Template:

```markdown
## [1.0.0] — 2026-06-XX (replace with ship date)

### Renamed
- Project renamed from **workshop** to **flightdeck**. Aviation metaphor adopted for operational discipline, continuity, and reliability framing — see [flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md](flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md) for design rationale.
- Folders renamed per spec: `plans/ → flight-plans/`, `playbooks/ → checklists/`, `scars/ → incident-reports/`, `reference/ → charts/`, `critiques/ → safety-reviews/`, `wip/ → kneeboard/`. `specs/` and `sketches/` retain neutral names.
- Skill modules renamed: `session-enter → preflight`, `session-exit → landing`, `doctor → walkaround`. `emit-agents-md` unchanged.
- Slash commands renamed: `/workshop:session-enter → /flightdeck:preflight`, `/workshop:session-exit → /flightdeck:landing`, `/workshop:doctor → /flightdeck:walkaround`.

### Decomposed
- `board.md` split into three files separated by read-time:
  - `cockpit.md` — must-read every session entry (Active focus, Next session, Hanging tasks). 80-line hard ceiling.
  - `manifest.md` — on-demand (In flight artifacts, Blockers).
  - `logbook.md` — rarely read (Recently finished FIFO 5, Deferred).

### Restructured
- `*/finish/` archive subdirs promoted to top-level `landed/` umbrella. `landed/flight-plans/`, `landed/specs/`.

### Repository
- GitHub repo renamed `Yuelioi/workshop` → `Yuelioi/flightdeck`. Auto-redirect in place. Plugin marketplace identifier updated.

### Migration
- Single-user migration. See [MIGRATION.md](MIGRATION.md) for the step list.
```

Note: this PATH `flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md` assumes the spec moves to `landed/specs/` post-ship per workshop convention (specs move to finish/landed after the work ships). The CHANGELOG entry should be written after that move (Task 7.x below).

- [ ] **Step 3: Commit**

```bash
git -C E:/projects/tools/workshop add CHANGELOG.md
git -C E:/projects/tools/workshop commit -m "docs: add v1.0.0 CHANGELOG entry"
```

---

## Phase 6 — MIGRATION.md

### Task 6.1: Write MIGRATION.md

**Files:**
- Create: `MIGRATION.md` at repo root

This is a self-note for the maintainer (user base = 1). Documents what was changed in v1.0 in case future-you needs to remember.

- [ ] **Step 1: Write MIGRATION.md**

```markdown
# Migration: workshop → flightdeck (v0.8.1 → v1.0.0)

This document records the v1.0 rebrand for the maintainer's reference. Read this if you cloned a pre-v1.0 workshop directory and need to update it manually, or if you're trying to reconcile old commits / docs against new paths.

## What changed

### Top-level
- Project name: **workshop** → **flightdeck**
- GitHub repo: `Yuelioi/workshop` → `Yuelioi/flightdeck` (auto-redirect in place)
- Plugin name and marketplace identifier: workshop → flightdeck
- VERSION: 0.8.1 → 1.0.0

### Directory rename
- `workshop/` → `flightdeck/`

### Folders inside the working dir
| Old | New |
| --- | --- |
| `plans/` | `flight-plans/` |
| `playbooks/` | `checklists/` |
| `scars/` | `incident-reports/` |
| `reference/` | `charts/` |
| `critiques/` | `safety-reviews/` |
| `wip/` | `kneeboard/` |
| `*/finish/` | `landed/*/` (promoted from nested archive to umbrella) |
| `specs/`, `sketches/` | unchanged |

### Entry-point file decomposition
- `board.md` split into three files (separated by read-time):
  - `cockpit.md` — Active focus + Next session + Hanging tasks. 80-line ceiling.
  - `manifest.md` — In flight + Blockers.
  - `logbook.md` — Recently finished + Deferred.

### Slash skills
- `/workshop:session-enter` → `/flightdeck:preflight`
- `/workshop:session-exit` → `/flightdeck:landing`
- `/workshop:doctor` → `/flightdeck:walkaround`
- `/workshop:emit-agents-md` → `/flightdeck:emit-agents-md` (unchanged function, namespace updated)

## Migrating a pre-v1.0 workshop directory

For each project that has a `workshop/` directory you want to update:

1. Rename top-level: `git mv workshop flightdeck`
2. Rename inner folders per the table above (`git mv flightdeck/plans flightdeck/flight-plans`, etc.)
3. Move archives: create `flightdeck/landed/`, move `flightdeck/flight-plans/finish/*` → `flightdeck/landed/flight-plans/`, repeat for specs.
4. Split board.md: read your current `flightdeck/board.md` and partition its sections into three new files per the read-time mapping above. Delete `board.md` after.
5. Update any AGENTS.md / CLAUDE.md at project root to reference the new paths.
6. Re-emit AGENTS.md with `/flightdeck:emit-agents-md` if you use the auto-generated form.

## Why the rename

See [flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md](flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md) for the design rationale. Short version: workshop framed the project as a maker space; flightdeck frames it as operational protocol — closer to what the project actually does.
```

- [ ] **Step 2: Commit**

```bash
git -C E:/projects/tools/workshop add MIGRATION.md
git -C E:/projects/tools/workshop commit -m "docs: add MIGRATION.md for v0.8.1 -> v1.0.0 transition"
```

---

## Phase 7 — Verification + spec archive

### Task 7.1: Full-tree workshop reference audit

**Files:** read-only across whole repo

- [ ] **Step 1: Run final grep for stale references**

```bash
grep -rn 'workshop' E:/projects/tools/workshop/ --exclude-dir=.git --exclude-dir=node_modules
```

Expected results that are OK:
- `MIGRATION.md` — explicit migration content
- `CHANGELOG.md` — "Renamed from workshop"
- `README.md` — the "previously named workshop" note
- `flightdeck/landed/flight-plans/2026-05-25*.md`, `2026-05-26*.md` — historical plan files; do NOT rewrite (they are landed history)
- `flightdeck/landed/specs/2026-05-25-v0.6-to-v1.0-roadmap.md` and `2026-05-23-v1.0-release-gate.md` if landed — historical content preserved
- `flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md` — this spec, after landing

Any other result → file should have been updated in Phases 1–5; go back and fix.

- [ ] **Step 2: Run grep for slash command stale references**

```bash
grep -rn '/workshop:' E:/projects/tools/workshop/ --exclude-dir=.git
```

Expected: zero results (or only inside MIGRATION.md / CHANGELOG.md for migration documentation).

- [ ] **Step 3: Verify all JSON manifests still parse**

```bash
for f in E:/projects/tools/workshop/.claude-plugin/*.json E:/projects/tools/workshop/.codex-plugin/*.json E:/projects/tools/workshop/.cursor-plugin/*.json E:/projects/tools/workshop/gemini-extension.json; do
  jq . "$f" > /dev/null && echo "OK: $f" || echo "FAIL: $f"
done
```

Expected: all OK.

- [ ] **Step 4: Verify SKILL.md frontmatter**

```bash
for f in E:/projects/tools/workshop/skills/*/SKILL.md; do
  echo "=== $f ==="
  awk '/^---$/{c++} c==1{print} c==2{exit}' "$f"
done
```

Each SKILL.md should show frontmatter with `name:` matching the new directory name.

- [ ] **Step 5: No commit unless fixes were applied during audit. If fixes:**

```bash
git -C E:/projects/tools/workshop add -A
git -C E:/projects/tools/workshop commit -m "chore: fix stale workshop references found in v1.0 audit"
```

---

### Task 7.2: Archive the rebrand spec + this plan to landed/

**Files:**
- Move: `flightdeck/specs/2026-05-28-flightdeck-rebrand-design.md` → `flightdeck/landed/specs/2026-05-28-flightdeck-rebrand-design.md`
- Move: `flightdeck/flight-plans/2026-05-28-flightdeck-rebrand-plan.md` → `flightdeck/landed/flight-plans/2026-05-28-flightdeck-rebrand-plan.md`

- [ ] **Step 1: Move spec and plan**

```bash
cd E:/projects/tools/workshop
git mv flightdeck/specs/2026-05-28-flightdeck-rebrand-design.md flightdeck/landed/specs/
git mv flightdeck/flight-plans/2026-05-28-flightdeck-rebrand-plan.md flightdeck/landed/flight-plans/
```

- [ ] **Step 2: Update cross-references**

Any document that referenced the spec or plan at the active path now points to landed. Use grep to find and update:

```bash
grep -rn '2026-05-28-flightdeck-rebrand' E:/projects/tools/workshop/ --exclude-dir=.git --exclude-dir=landed
```

For each result, update the path to include `/landed/`.

- [ ] **Step 3: Commit**

```bash
git -C E:/projects/tools/workshop add -A
git -C E:/projects/tools/workshop commit -m "archive: move flightdeck-rebrand spec + plan to landed/"
```

---

### Task 7.3: Update cockpit.md with v1.0 shipping state

**Files:**
- Modify: `flightdeck/cockpit.md`

- [ ] **Step 1: Update cockpit.md fields**

```markdown
**Last updated**: 2026-06-XX by 月离 (shipped v1.0 — flightdeck rebrand + board decomposition)
**Active focus**: post-v1.0 dogfood under new names

## Next session

1. Dogfood flightdeck on real projects. Watch for: manifest.md naming friction, cockpit.md ceiling pressure, metaphor lock-in temptations on any new concept added.
2. Re-emit AGENTS.md across active projects using `/flightdeck:emit-agents-md`.
3. Reassess [out-of-scope folders](landed/specs/2026-05-28-flightdeck-rebrand-design.md#out-of-scope-deferred-to-v11) (briefing/, blackbox/, crew-handover/, experiments/) after 1-2 weeks of real use.
```

- [ ] **Step 2: Commit**

```bash
git -C E:/projects/tools/workshop add flightdeck/cockpit.md
git -C E:/projects/tools/workshop commit -m "cockpit: bump for v1.0 ship"
```

---

## Phase 8 — Tag and merge

### Task 8.1: Tag v1.0.0 and merge to main

**Files:** none

- [ ] **Step 1: Verify branch state**

```bash
git -C E:/projects/tools/workshop log --oneline main..flightdeck-rebrand
git -C E:/projects/tools/workshop status
```

Expected: ~15-20 commits on flightdeck-rebrand, clean tree.

- [ ] **Step 2: Switch to main, merge with no-ff**

```bash
git -C E:/projects/tools/workshop checkout main
git -C E:/projects/tools/workshop merge --no-ff flightdeck-rebrand -m "v1.0.0 — flightdeck rebrand + board.md decomposition

Merges feature branch flightdeck-rebrand. See CHANGELOG.md and MIGRATION.md."
```

- [ ] **Step 3: Tag v1.0.0**

```bash
git -C E:/projects/tools/workshop tag -a v1.0.0 -m "v1.0.0 — flightdeck"
```

- [ ] **Step 4: Push branch + tag + main**

```bash
git -C E:/projects/tools/workshop push origin main
git -C E:/projects/tools/workshop push origin flightdeck-rebrand
git -C E:/projects/tools/workshop push origin v1.0.0
```

Note: this is a network action. If the maintainer wants to inspect locally first, defer push until satisfied.

---

### Task 8.2: GitHub repo rename (manual step — user action)

**Files:** none (action happens in GitHub UI)

- [ ] **Step 1: User action**

Navigate to https://github.com/Yuelioi/workshop/settings → change name to `flightdeck`. GitHub creates an auto-redirect from the old URL.

- [ ] **Step 2: Update local remote URL**

```bash
git -C E:/projects/tools/workshop remote set-url origin https://github.com/Yuelioi/flightdeck.git
git -C E:/projects/tools/workshop remote -v
```

- [ ] **Step 3: Re-push tag if needed**

```bash
git -C E:/projects/tools/workshop fetch origin
```

Expected: no errors; refs sync correctly with renamed remote.

---

## Post-ship

After v1.0.0 ships, return to dogfood with the new structure. Track in cockpit.md "Next session" item #1. Re-evaluate the v1.1+ deferred items (briefing/, blackbox/, crew-handover/, experiments/) after 1-2 weeks of real use under flightdeck names.

If `manifest.md` naming proves friction-laden during dogfood (per spec open question #4), file a new spec for renaming it; do not re-litigate in this release.

---

## Notes on this plan

- TDD adaptation: there are no unit tests in workshop. "Tests" in this plan are `grep` audits and JSON-validity checks. Real verification is manual: invoking renamed slash skills in a fresh Claude Code session to confirm they load.
- Each phase is one commit (or a small commit series). The feature branch tolerates broken intermediate states; the merge to main is atomic.
- The plan file itself moves with the project — Tasks 1.3 and 7.2 reflect this.
- If at any point a step's expected output diverges materially from actual, STOP and reconcile against the spec before proceeding. Do not silently absorb structural surprises.
