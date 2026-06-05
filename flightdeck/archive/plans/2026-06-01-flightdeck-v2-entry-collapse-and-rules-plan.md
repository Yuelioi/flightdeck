# flightdeck v2 — entry-layer collapse + customization layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship flightdeck v2.0 — collapse the entry layer to `cockpit.md` + `INDEX.md`, add a `rules.md` customization layer, give multi-plan specs a state-word ledger, remove `kneeboard/`, generalize `landed/`, and provide a guided migration — across the skill docs, scaffolds, and release plumbing.

**Architecture:** flightdeck is plain-markdown conventions enforced by skill prose (no code, no test suite). Each task edits one file's section(s) and verifies with a ripgrep assertion (presence of new terms / absence of removed terms) — TDD's "red/green" maps to "grep shows the old term gone / the new term present". The authoritative design is [`flightdeck/specs/2026-05-31-flightdeck-v2-entry-collapse-and-rules-design.md`](../specs/2026-05-31-flightdeck-v2-entry-collapse-and-rules-design.md); read it before starting.

**Tech Stack:** Markdown, YAML frontmatter, ripgrep for verification, git. Repo root: `E:\projects\tools\flightdeck`.

**Ordering rationale:** Phase 1 (`rules.md`) is foundational — later skills branch on its toggles. Phase 2–4 rewrite the core convention docs. Phase 5 updates the four entry skills that consume the convention. Phase 6 adds migration + scaffolds. Phase 7 does docs + the version bump, which MUST be last (it greps for residue of removed terms as a release gate). Do NOT commit/tag/push (Phase 7 Task 18) until the user confirms — they asked to decide commit timing after the plan is reviewed.

**Conventions for every task below:**
- "Verify removed" = `rg -n '<term>' <path>` returns **no matches** (exit 1).
- "Verify present" = `rg -n '<term>' <path>` returns the expected line.
- Do NOT touch anything under `flightdeck/landed/` (archived history; exempt from current-state rules).
- `.github/PULL_REQUEST_TEMPLATE/manifest-verification.md` is about the **five release manifests**, NOT flightdeck `manifest.md` — leave it alone.

---

## Phase 1 — Customization layer (`rules.md`)

### Task 1: Define the `rules.md` template

**Files:**
- Modify: `skills/workflow/templates.md` (add a new `## rules.md` template section)

- [ ] **Step 1: Add the `rules.md` template** near the top of `templates.md` (after the intro, before `## incident-report`), inserting:

````markdown
## rules.md

```markdown
---
git: true                 # false → skills skip all git reconcile/commit steps
emit_agents_md: true      # false → emit-agents-md refuses (no-op)
disabled_folders: []      # e.g. [charts, safety-reviews] → never suggested; not flagged as orphans
disabled_gates: []        # e.g. [awaiting-review-owner, safety-review-disposition]
---

## House rules

Free-prose project conventions every flightdeck skill must honor
(e.g. "never auto-commit", "specs written in Chinese", "do not create sketches/").
```

### Rules

- **Optional file.** No `rules.md` = v2 defaults (git on, emit on, all folders/gates active). Purely additive.
- **Closed toggle set** — only these four keys are honored. An unknown key is ignored with a one-line warning (typos must not silently change behavior):

  | Key | Type | Default | Effect when changed |
  | --- | --- | --- | --- |
  | `git` | bool | `true` | `false` → skip git branch/status/stash/log reconcile; never auto-commit; staleness + history use `landed/HISTORY.md`. |
  | `emit_agents_md` | bool | `true` | `false` → `emit-agents-md` refuses and reports "disabled via rules.md". |
  | `disabled_folders` | list | `[]` | Listed folders never suggested by fallback/exit classification; not flagged as orphans by `walkaround`. |
  | `disabled_gates` | list | `[]` | Named gates skipped. Known: `awaiting-review-owner`, `safety-review-disposition`, `frontmatter-required`. |

- **`disabled_gates: [frontmatter-required]` is dangerous** — it makes routed files invisible to grep-routing. Warn the user when honoring it.
- **House rules are advisory prose** the AI honors, but they cannot redefine the four toggle keys.
- **Malformed YAML or unparseable frontmatter** → warn and fall back to all defaults; never hard-fail (a broken `rules.md` must not brick the entry ritual).
- **Read first**: every entry skill (`workflow`, `preflight`, `walkaround`, `landing`, `emit-agents-md`) reads `rules.md` before acting and branches on the toggles.
```
````

- [ ] **Step 2: Verify present**

Run: `rg -n 'disabled_gates|## rules.md' skills/workflow/templates.md`
Expected: matches for the `## rules.md` heading and the toggle table.

- [ ] **Step 3: Commit**

```bash
git add skills/workflow/templates.md
git commit -m "feat(rules): add rules.md template + closed toggle set"
```

### Task 2: Wire the "read rules.md first" contract into `workflow/SKILL.md`

**Files:**
- Modify: `skills/workflow/SKILL.md` (add a `## Project rules (rules.md)` section after `## Core principle`; update `## Authority order`)

- [ ] **Step 1: Add the rules section** after the `## Core principle` block:

```markdown
## Project rules (`rules.md`)

`flightdeck/rules.md` is an **optional** project-config file read **first** by every entry skill (`workflow`, `preflight`, `walkaround`, `landing`, `emit-agents-md`). It carries a closed set of structured toggles plus free-prose house rules. Absent file = defaults (git on, emit on, all folders/gates active).

Toggles: `git` · `emit_agents_md` · `disabled_folders` · `disabled_gates`. Full schema + degradation rules: [templates.md § rules.md](templates.md#rulesmd).

When `git: false`, skills skip all git reconcile/commit steps and use `landed/HISTORY.md` for the staleness check and history. When a folder is in `disabled_folders`, it is never suggested and never flagged as an orphan. Honor house-rules prose, but it cannot override the four toggles or the project's own agent rules.
```

- [ ] **Step 2: Update the authority order.** Replace the existing authority-order line and its peer-group paragraph with:

```markdown
Project agent rules > `rules.md` > `cockpit.md` > active `flight-plans/` > active `specs/` > `checklists/` > `incident-reports/` > `landed/`

`rules.md` sits just below the project's own agent rules: it governs how flightdeck skills behave. `cockpit.md` is the single operational entry below it. (v1's `manifest.md` / `logbook.md` peer group is gone — see [folder-semantics.md](folder-semantics.md).)
```

- [ ] **Step 3: Verify present**

Run: `rg -n 'rules.md|Project agent rules > ' skills/workflow/SKILL.md`
Expected: the new section heading and the new authority-order line.

- [ ] **Step 4: Verify the peer-group language is gone**

Run: `rg -n 'three new files are \*\*peers\*\*|≡ .manifest' skills/workflow/SKILL.md`
Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/SKILL.md
git commit -m "feat(rules): workflow reads rules.md first; rules.md enters authority order"
```

---

## Phase 2 — Entry-layer collapse (A1)

### Task 3: Rewrite the cockpit template; remove the manifest + logbook templates

**Files:**
- Modify: `skills/workflow/templates.md` (`## cockpit.md` section; delete `## manifest.md` and `## logbook.md` sections)

- [ ] **Step 1: Replace the `## cockpit.md` template** (lines currently spanning the cockpit template + its Rules) with:

````markdown
## cockpit.md

```markdown
# Cockpit — <project>

**Last updated**: YYYY-MM-DD by <who> (<one-line state summary>)
**Active focus**: <current main thread, 5–15 words>

## Next session

1. <first concrete action — executable by reading cockpit only>
2. <second>

## In flight

<!-- OMIT this section entirely when empty. Only artifacts whose state: diverges
     from folder location appear (state: blocked / awaiting-review / scrapped).
     Implicit pending specs / in-progress plans need NO row. -->

| Artifact | State | Owner / Reason | Refs |
| --- | --- | --- | --- |

## Blockers

<!-- OMIT when empty. Items waiting on an external decision / answer. -->

## Hanging tasks

- [ ] Finish disposition of [safety-reviews/...](safety-reviews/...)
```

### Rules

- **Length cap: 80 lines hard ceiling.** Past 80, trim immediately.
- **`In flight` and `Blockers` are omitted when empty** — they cost zero lines on a healthy project. Only divergent-state artifacts get an `In flight` row.
- **`Active focus` is current state**, not history.
- **Hanging tasks block landing.**
- **History does not live in cockpit.** Durable record = `landed/` archive + `git log` (+ `landed/HISTORY.md` when `git: false`). A finished item leaves `Next session`; it is not logged in cockpit.
- **No metric tracking duplicated elsewhere** — link to the single source.
````

- [ ] **Step 2: Delete the entire `## manifest.md` section and the entire `## logbook.md` section** from `templates.md` (everything from `## manifest.md` through the end of the logbook Rules list, i.e. up to but not including `## INDEX.md`).

- [ ] **Step 3: Verify removed**

Run: `rg -n '^## manifest.md|^## logbook.md' skills/workflow/templates.md`
Expected: no matches.

- [ ] **Step 4: Verify cockpit template updated**

Run: `rg -n '## In flight|OMIT this section|landed/HISTORY.md' skills/workflow/templates.md`
Expected: matches inside the cockpit template + Rules.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/templates.md
git commit -m "feat(cockpit): fold In flight/Blockers into cockpit; drop manifest+logbook templates"
```

### Task 4: Rewrite the `folder-semantics.md` entry-files section + folder map

**Files:**
- Modify: `skills/workflow/folder-semantics.md` (the `## The 11 folders + 3 entry files` ASCII map, the `## Entry files` section, the routing model entry list)

- [ ] **Step 1: Replace the ASCII folder map** (the fenced block under `## The 11 folders + 3 entry files`) with:

```
flightdeck/
├── rules.md            # OPTIONAL project config — read first by every entry skill
├── cockpit.md          # The single must-read entry (≤80 lines): do / open / blockers
├── INDEX.md            # OPTIONAL resource lookup for checklists/ + incident-reports/
│
├── specs/              # Design docs (multi-plan spec carries its own ## Plans ledger)
├── flight-plans/       # Implementation plans
│
├── checklists/         # Operational reference (checklists, conventions, standards; may be bundles)
├── incident-reports/   # Lessons learned (mistakes worth not repeating)
├── charts/             # External material (competitor code, RFCs, articles)
│
├── sketches/           # Long-term ideas (not started; awaiting trigger)
├── safety-reviews/     # External AI / reviewer feedback (raw + disposition)
│
└── landed/             # Archive umbrella — mirrors ANY source folder on demand
    ├── flight-plans/   # Archived after the plan is fully executed
    ├── specs/          # Archived after the design is shipped
    ├── checklists/     # Archived obsolete-but-historical reference
    ├── incident-reports/
    └── HISTORY.md      # Append-only landing log (required when rules.md git: false)
```

Also rename the section heading `## The 11 folders + 3 entry files` → `## The folders + entry files`, and update the minimal-vs-full table's "Full" row to read `all folders + cockpit.md (+ optional rules.md / INDEX.md)`.

- [ ] **Step 2: Replace the whole `## Entry files` section** (from `## Entry files` through the end of the `### logbook.md` subsection and its peer paragraph) with:

```markdown
## Entry files

### `cockpit.md` — the single must-read

**The only required file.** Read first, updated last. Hard ceiling: **80 lines**.

Contains:
- `Last updated: YYYY-MM-DD by <who> (<one-line>)`
- `Active focus: <current main thread>`
- `## Next session` — 1–5 concrete items.
- `## In flight` — **only** artifacts whose `state:` diverges from folder location (`blocked` / `awaiting-review` / `scrapped`). Omitted when empty.
- `## Blockers` — external waits. Omitted when empty.
- `## Hanging tasks` — open items blocking a clean landing.

**Why a single entry (v2):** v1 split the old `board.md` into `cockpit` / `manifest` / `logbook` by read-frequency, but content cleaves by *category* not frequency, so the three files' responsibilities blurred and everything drifted back into cockpit anyway. v2 folds the divergent-state `In flight` table and `Blockers` back into cockpit as omit-when-empty sections (zero line cost when healthy), drops `manifest.md` and `logbook.md`, and keeps `INDEX.md` purely as the resource lookup.

Authority: project state lives here; cockpit beats an archived spec.

Update rule: only "user-perceivable semantic progress" updates `Last updated` — pure exploration / grep / typo-fix does not.

### `INDEX.md` — optional resource lookup

A scannable index of `checklists/` + `incident-reports/` (and `charts/`) resources — one line per file with a hook. AI maintains the `<!-- AUTO-START -->` … `<!-- AUTO-END -->` sections; everything outside is hand-curated. Add it only when there are enough resources that scanning is no longer easy. See [templates.md § INDEX.md](templates.md#indexmd).

### `landed/HISTORY.md` — append-only landing log

Lives under `landed/`, so it is **outside the routing graph** (never read at session start). One line per landing: `YYYY-MM-DD — <result>; next: <pointer>`, newest first.

**Required when `rules.md` sets `git: false`** (no commit log to lean on); optional otherwise (git projects already have `git log` + the `landed/` archive). This is what keeps project memory alive for no-git projects while cockpit stays purely now/next.
```

- [ ] **Step 3: Update the routing-model entry list.** In `## Routing model`, change every "`cockpit.md`, `INDEX.md`, `manifest.md`, or any bundle `README.md`" enumeration to "`cockpit.md`, `INDEX.md`, `rules.md`, or any bundle `README.md`" (drop `manifest.md`, add `rules.md`).

- [ ] **Step 4: Verify removed**

Run: `rg -n 'manifest.md|logbook.md|11 folders' skills/workflow/folder-semantics.md`
Expected: no matches.

- [ ] **Step 5: Verify present**

Run: `rg -n 'landed/HISTORY.md|single must-read|rules.md' skills/workflow/folder-semantics.md`
Expected: matches.

- [ ] **Step 6: Commit**

```bash
git add skills/workflow/folder-semantics.md
git commit -m "feat(entry): collapse entry layer to cockpit+INDEX; add rules.md + HISTORY.md"
```

### Task 5: Update `workflow/SKILL.md` folder map, entry checklist, lifecycle, common mistakes

**Files:**
- Modify: `skills/workflow/SKILL.md`

- [ ] **Step 1: Update the `## Folder map` section.** Change "11 folders + 3 entry files, all optional except `cockpit.md`" → "Folders + entry files, all optional except `cockpit.md`". Update the entries-reachable parenthetical from "(`cockpit.md`, `INDEX.md`, `manifest.md`, or a bundle `README.md`)" → "(`cockpit.md`, `INDEX.md`, `rules.md`, or a bundle `README.md`)".

- [ ] **Step 2: Update the Entry checklist** (`## Entry checklist`). Add a new step 0 before current step 1:

```markdown
0. Read `flightdeck/rules.md` if present; apply its toggles for the rest of the session (when `git: false`, skip every git step below and use `landed/HISTORY.md` for the staleness check).
```

In the existing step 2 reconcile bullets, prefix the git bullets with "(skip when `git: false`)". Change the stale check to: "Is `Last updated` more than ~14 days behind the most recent commit (or, when `git: false`, behind the newest `landed/HISTORY.md` entry)? → cockpit may be stale."

- [ ] **Step 3: Update the Fallback note** at the end of `## Entry checklist`: replace "Active flight-plans/specs should be in manifest's `In flight` table — if fallback finds something that isn't, that's a manifest sync bug" with "Active divergent-state artifacts should appear in cockpit's `In flight` section — if fallback finds a blocked/awaiting-review artifact that isn't listed there, that's a cockpit sync bug; flag to user."

- [ ] **Step 4: Update `## Lifecycle of specs and plans`.** Replace the paragraph "**Manifest `In flight` table shows ONLY rows where state diverges from location**…" with "**Cockpit's `In flight` section shows ONLY rows where state diverges from location** — i.e., rows with an explicit `state:` value. Implicit-state artifacts don't need a row; their folder location is enough." (Also update the mermaid `note right of` labels that say "manifest" if any — there are none; the labels reference frontmatter, leave them.)

- [ ] **Step 5: Update `## Exit ritual`.** Change "After classifying: update `cockpit.md` (`Last updated` + "next session") → commit." to "After classifying: update `cockpit.md` (`Last updated` + `Next session` + any `In flight`/`Blockers` changes); append to `landed/HISTORY.md` when `git: false`; then commit (unless `git: false`)."

- [ ] **Step 6: Update the `## Common mistakes` table.** Change the row "Cockpit > 80 lines | Trim immediately — move historical / contextual content to `logbook.md` or `manifest.md`." → "Cockpit > 80 lines | Trim immediately — drop finished items, move design detail to the relevant `specs/` file; history is `git log` / `landed/HISTORY.md`, not cockpit." Delete the `Recently finished > 5 entries` row entirely (logbook is gone).

- [ ] **Step 7: Verify removed**

Run: `rg -n 'manifest|logbook|Recently finished' skills/workflow/SKILL.md`
Expected: no matches.

- [ ] **Step 8: Verify present**

Run: `rg -n "Read .flightdeck/rules.md|cockpit's .In flight. section|landed/HISTORY.md" skills/workflow/SKILL.md`
Expected: matches.

- [ ] **Step 9: Commit**

```bash
git add skills/workflow/SKILL.md
git commit -m "feat(entry): SKILL.md entry checklist + lifecycle reference cockpit (not manifest/logbook)"
```

### Task 6: Rewrite `exit-ritual.md` for the collapsed entry layer + #3 update rule

**Files:**
- Modify: `skills/workflow/exit-ritual.md`

- [ ] **Step 1: Update the decision tree Step 3 + Step 3a.** In `Step 3: Update cockpit.md`, replace the `- **Update manifest.md In flight row states**` bullet with `- **Update cockpit's In flight rows** (divergent-state artifacts only — see lifecycle table below)`. In the Step 3a lifecycle table, replace every "manifest" with "cockpit's In flight", and the "Review passed" row's "add 1 entry to logbook `Recently finished`" with "append a line to `landed/HISTORY.md` when `git: false`". Remove the standalone "add … logbook" phrasing in the Blocked/Scrapped rows.

- [ ] **Step 2: Replace the whole `## Board update — what changes` block** with:

```markdown
## Cockpit update — what changes

```
Last updated:     ONLY in these 4 cases (otherwise leave alone):
                  (a) Next session content changes
                  (b) Active focus shifts (main thread moved)
                  (c) A major task / phase completes (user-perceivable progress)
                  (d) A divergent-state artifact resolves (In flight row clears)
Active focus:     update if main thread shifted (otherwise leave)
Next session:     always update — at minimum confirm the first item is still right
In flight:        update if a divergent-state artifact started/resolved. Omit the section when empty.
Blockers:         update if blockers resolved or new ones appeared. Omit when empty.
Hanging tasks:    update — add new hangings, clear resolved ones
HISTORY.md:       when git: false, append one line per landing (YYYY-MM-DD — result; next: pointer)
```

**`Last updated` is not a session-activity log.** False triggers that must NOT bump it: pure exploration / grep / reading code; typo fixes; internal refactor with no user-perceivable surface; a commit that doesn't complete a cockpit task; running already-passing tests.

**When to update mid-session (#3 rule):** after any commit that changes user-perceivable state, refresh `Next session` before starting the next task — don't wait for landing.

**Length check before exit:** if `cockpit.md` > 80 lines, trim immediately (drop finished items; move design detail to `specs/`). History is `git log` / `landed/HISTORY.md`, never cockpit.
```

- [ ] **Step 3: Update the `## Core principle` decision tree Step 1** — change "(incomplete safety-review disposition / kneeboard files older than this session)" → "(incomplete safety-review disposition)". (kneeboard removal is Task 8; this line is touched here because it is inside the block being edited — keep edits consistent.)

- [ ] **Step 4: Verify removed**

Run: `rg -n 'manifest|logbook|Recently finished|Board update' skills/workflow/exit-ritual.md`
Expected: no matches (kneeboard handled in Task 8).

- [ ] **Step 5: Verify present**

Run: `rg -n 'Cockpit update|#3 rule|landed/HISTORY.md|after any commit that changes user-perceivable' skills/workflow/exit-ritual.md`
Expected: matches.

- [ ] **Step 6: Commit**

```bash
git add skills/workflow/exit-ritual.md
git commit -m "feat(exit): cockpit-only update rules; #3 mid-session trigger; HISTORY on git:false"
```

---

## Phase 3 — Multi-plan progress ledger (B1)

### Task 7: Add the `## Plans` ledger convention

**Files:**
- Modify: `skills/workflow/folder-semantics.md` (`### specs/` subsection)
- Modify: `skills/workflow/templates.md` (add a `## spec ## Plans ledger` snippet)
- Modify: `skills/workflow/SKILL.md` (`## Lifecycle of specs and plans` — add a note)

- [ ] **Step 1: In `folder-semantics.md` `### specs/`,** append:

```markdown
**Multi-plan specs carry a `## Plans` ledger** at the file tail listing their child plans with explicit state words (`pending` / `active` / `blocked` / `awaiting-review` / `landed` / `scrapped` — the same set as the spec/plan lifecycle). The spec is the progress rollup; `cockpit.Next session` points at the spec, not each plan. Do **not** use `- [ ]` checkboxes for ledger status — checkboxes stay optional notation inside a plan file and never carry the rollup state (avoids the `- [ ] plan — blocked` double-representation). Single-plan specs don't need a ledger.
```

- [ ] **Step 2: In `templates.md`,** add after the spec-evolution-markers section:

````markdown
## spec `## Plans` ledger (multi-plan specs only)

```markdown
## Plans

- 2026-06-01-foo-phase1-plan.md — landed
- 2026-06-03-foo-phase2-plan.md — active
- phase 3 (auth) — pending
- phase 4 (migration) — blocked: waiting on infra decision
```

States: `pending` / `active` / `blocked` / `awaiting-review` / `landed` / `scrapped`. The ledger word and a plan's frontmatter `state:` must agree. No `- [ ]` checkboxes.
````

- [ ] **Step 3: In `SKILL.md` `## Lifecycle of specs and plans`,** add a sentence after the short-circuit paragraph: "When one spec spawns multiple plans, the spec owns a `## Plans` ledger (state words, not checkboxes) and is the progress rollup — see [folder-semantics.md § specs/](folder-semantics.md#specs--design-docs)."

- [ ] **Step 4: Verify present**

Run: `rg -n '## Plans|state words|awaiting-review' skills/workflow/folder-semantics.md skills/workflow/templates.md skills/workflow/SKILL.md`
Expected: matches in all three.

- [ ] **Step 5: Commit**

```bash
git add skills/workflow/folder-semantics.md skills/workflow/templates.md skills/workflow/SKILL.md
git commit -m "feat(specs): multi-plan ## Plans ledger with state words (B1)"
```

---

## Phase 4 — Folder semantics (C1 remove kneeboard, C3 generalize landed)

### Task 8: Remove `kneeboard/` from the convention docs

**Files:**
- Modify: `skills/workflow/templates.md` (delete `## kneeboard` template + Rules + pre-write checklist)
- Modify: `skills/workflow/folder-semantics.md` (delete `### kneeboard/` subsection; fix the ASCII map already done in Task 4; update anti-patterns + which-folder table)
- Modify: `skills/workflow/SKILL.md` (`## Common mistakes` — delete kneeboard rows)
- Modify: `skills/workflow/exit-ritual.md` (delete `### Stale kneeboard files` subsection + Step 1 reference already trimmed in Task 6)

- [ ] **Step 1:** In `templates.md`, delete the entire `## kneeboard` section (template + Rules + Pre-write checklist), from `## kneeboard` through the `---` before `## safety-review`.

- [ ] **Step 2:** In `folder-semantics.md`, delete the `### kneeboard/` subsection. In `## Anti-patterns`, delete the two `sketches/ used as kneeboard/` rows. In `### sketches/`, change "Distinguish from `kneeboard/`: sketches are **unstarted**…" to "Sketches are **unstarted** ideas; transient session scratch lives in project-root `tmp/` (gitignored), not in flightdeck." In the naming-convention table, delete the `kneeboard/` row.

- [ ] **Step 3:** In `SKILL.md` `## Common mistakes`, delete the three kneeboard rows (`sketches/ used as kneeboard/`, `kneeboard/ file without last_touched`, `kneeboard/ files older than current session`). Add one row: `Scratch written into flightdeck/ | Transient scratch lives in project-root tmp/ (gitignored), not flightdeck.`

- [ ] **Step 4:** In `exit-ritual.md`, delete the `### Stale kneeboard/ files` subsection under `## Hanging tasks`. In that section's intro, change "while either of these is unresolved" → "while this is unresolved" and drop the kneeboard bullet.

- [ ] **Step 5: Verify removed across all workflow docs**

Run: `rg -ni 'kneeboard' skills/workflow/`
Expected: no matches.

- [ ] **Step 6: Commit**

```bash
git add skills/workflow/
git commit -m "feat(folders): remove kneeboard/ from the convention (C1); scratch lives in tmp/"
```

### Task 9: Generalize `landed/`

**Files:**
- Modify: `skills/workflow/folder-semantics.md` (`### landed/` subsection — ASCII map already updated in Task 4)

- [ ] **Step 1:** Replace the `### landed/ — archive umbrella` body with:

```markdown
Top-level archive for completed or retired work. `landed/` **mirrors any source folder on demand** — create the matching subdirectory the first time you archive something of that kind:

- `landed/flight-plans/` — plans archived after full execution.
- `landed/specs/` — specs archived after the design ships.
- `landed/checklists/`, `landed/incident-reports/`, `landed/charts/` — obsolete-but-historical reference moved out of the active set instead of deleted.
- `landed/HISTORY.md` — append-only landing log (see [Entry files](#entry-files)).

Archiving vs `status: obsolete`: flip `status: obsolete` to keep a dead file in place (still reachable, marked dead); **move to `landed/`** to take it out of the active routing set while preserving history. Archived files lose to current state in [authority order](SKILL.md#authority-order-when-sources-disagree). Routing already excludes everything under `landed/`.
```

- [ ] **Step 2: Verify present**

Run: `rg -n 'mirrors any source folder|landed/checklists/' skills/workflow/folder-semantics.md`
Expected: matches.

- [ ] **Step 3: Commit**

```bash
git add skills/workflow/folder-semantics.md
git commit -m "feat(landed): generalize landed/ to mirror any source folder (C3)"
```

### Task 10: Add the `HISTORY.md` template

**Files:**
- Modify: `skills/workflow/templates.md` (add `## HISTORY.md` template)

- [ ] **Step 1:** Add after the cockpit template section:

````markdown
## landed/HISTORY.md

```markdown
# History — <project>

<!-- Append-only landing log. One line per landing, newest first.
     Required when rules.md sets git: false; optional otherwise.
     Lives under landed/ — outside the routing graph; never read at session start. -->

- YYYY-MM-DD — <what landed this session>; next: <pointer to next session item>
```

### Rules

- **One line per landing**, newest first. No multi-line entries — link to the archived artifact for detail.
- **Required only when `git: false`** (no commit log). Git projects may keep it but `git log` is authoritative.
- **Never read at session start** — it is reference for retrospectives / no-git staleness checks only.
````

- [ ] **Step 2: Verify present**

Run: `rg -n '## landed/HISTORY.md|Append-only landing log' skills/workflow/templates.md`
Expected: matches.

- [ ] **Step 3: Commit**

```bash
git add skills/workflow/templates.md
git commit -m "feat(history): add landed/HISTORY.md template"
```

---

## Phase 5 — Entry skills

### Task 11: Update `preflight/SKILL.md`

**Files:**
- Modify: `skills/preflight/SKILL.md`

- [ ] **Step 1: Update the frontmatter `description`** — replace "surfaces stale kneeboard files, " with "" (drop the kneeboard clause).

- [ ] **Step 2: Add a new checklist step 0** before current step 1:

```markdown
0. **Read `flightdeck/rules.md`** if present. Apply its toggles for the whole ritual: when `git: false`, skip step 2's git reconcile entirely and run the staleness check against the newest `landed/HISTORY.md` entry instead; honor `disabled_folders` (don't suggest them in fallback).
```

- [ ] **Step 3: Gate step 2** — prefix the heading "**Reconcile against repo state.**" with "(skip entirely when `rules.md` sets `git: false`)". For the stale check bullet, append "— or, when `git: false`, compare against the newest `landed/HISTORY.md` entry."

- [ ] **Step 4: Delete step 3** (`Surface stale kneeboard/ files`) entirely and renumber the remaining steps (old 4→3, 5→4, 6→5).

- [ ] **Step 5: Add migration detection** as a new bullet at the end of step 1 (cockpit read): 

```markdown
   - **Old-layout detection:** if `flightdeck/manifest.md`, `flightdeck/logbook.md`, or `flightdeck/kneeboard/` exists, this is a v1 flightdeck. Before reconciling, tell the user "v1 layout detected — run guided migration to v2? (folds manifest→cockpit, imports logbook history, clears kneeboard)" and follow [MIGRATION.md](../../MIGRATION.md). Never migrate silently.
```

- [ ] **Step 6: Fix the fallback note** — replace "Actively-implementing artifacts SHOULD already be in manifest's `In flight` table. If fallback finds something not on the manifest, flag as a manifest sync bug." with "Divergent-state artifacts SHOULD already be in cockpit's `In flight` section. If fallback finds a blocked/awaiting-review artifact not listed there, flag as a cockpit sync bug."

- [ ] **Step 7: Verify removed**

Run: `rg -ni 'kneeboard|manifest' skills/preflight/SKILL.md`
Expected: no matches.

- [ ] **Step 8: Verify present**

Run: `rg -n 'rules.md|git: false|Old-layout detection' skills/preflight/SKILL.md`
Expected: matches.

- [ ] **Step 9: Commit**

```bash
git add skills/preflight/SKILL.md
git commit -m "feat(preflight): read rules.md; git:false branch; migration detect; drop kneeboard"
```

### Task 12: Update `landing/SKILL.md`

**Files:**
- Modify: `skills/landing/SKILL.md`

- [ ] **Step 1: Update frontmatter `description`** — replace "blocks on hanging tasks, runs a lightweight stray/orphan workspace smoke-check, optionally commits" leaving intact but remove any kneeboard implication (none in description; skip if absent).

- [ ] **Step 2: Add a step 0**:

```markdown
0. **Read `flightdeck/rules.md`** if present. When `git: false`: skip the commit step (step 7), and instead append one line to `landed/HISTORY.md` (`YYYY-MM-DD — <result>; next: <pointer>`, newest first). Honor `disabled_gates` (e.g. skip the safety-review-disposition gate if disabled).
```

- [ ] **Step 3: Update step 1** — change "incomplete safety-review dispositions and stale `kneeboard/` files block clean exit" → "incomplete safety-review dispositions block clean exit".

- [ ] **Step 4: Update step 5 (AGENTS.md regen)** — change "(`cockpit.md`: … ; `manifest.md`: `In flight`)" → "(`cockpit.md`: `Last updated` / `Active focus` / `Next session` / `In flight` / `Hanging tasks`)". Drop the manifest clause.

- [ ] **Step 5: Update step 6 (smoke-check)** — change the stray-root-file whitelist "(`cockpit.md` / `manifest.md` / `logbook.md` / `INDEX.md`)" → "(`cockpit.md` / `INDEX.md` / `rules.md`)". In the orphan bullet, change "(`cockpit.md` / `INDEX.md` / `manifest.md` / a bundle `README.md` …)" → "(`cockpit.md` / `INDEX.md` / `rules.md` / a bundle `README.md` …)" and change "Skip `landed/` and `kneeboard/`." → "Skip `landed/`."

- [ ] **Step 6: Update the Length check section** — replace "historical / contextual sections that belong in `logbook.md` or `manifest.md`" → "finished items (drop them) and design detail (move to the relevant `specs/` file)". Delete the `logbook.md > 300 lines` sentence.

- [ ] **Step 7: Update the Output format block** — replace the `Logbook updated:` lines with `History (git:false): [+1 HISTORY.md line / n/a]`. Update the smoke-check entry-list parenthetical to drop kneeboard.

- [ ] **Step 8: Update Red flags** — replace the kneeboard bullet "Leaving `kneeboard/` files for "next session"…" with "Saving transient scratch into `flightdeck/` instead of project-root `tmp/`".

- [ ] **Step 9: Verify removed**

Run: `rg -ni 'kneeboard|manifest|logbook' skills/landing/SKILL.md`
Expected: no matches.

- [ ] **Step 10: Verify present**

Run: `rg -n 'rules.md|git: false|landed/HISTORY.md' skills/landing/SKILL.md`
Expected: matches.

- [ ] **Step 11: Commit**

```bash
git add skills/landing/SKILL.md
git commit -m "feat(landing): rules.md toggles; HISTORY on git:false; drop kneeboard/manifest/logbook"
```

### Task 13: Update `walkaround/SKILL.md`

**Files:**
- Modify: `skills/walkaround/SKILL.md`

- [ ] **Step 1: Update frontmatter `description`** — replace "checks cockpit.md / manifest.md / logbook.md / specs / flight-plans / incident-reports / checklists / kneeboard" → "checks cockpit.md / rules.md / specs / flight-plans / incident-reports / checklists".

- [ ] **Step 2: Add a step 0** under `## Audits` intro: "First read `flightdeck/rules.md` if present. Skip git-dependent audits (8 AGENTS.md drift uses no git; none are git-only — but honor `disabled_folders`: do not flag a disabled folder as orphan/stray in Audits 9–10, and do not flag a `disabled_gates` gate)."

- [ ] **Step 3: Delete Audit 2** (`Stale kneeboard files`) entirely and renumber Audits 3–10 → 2–9. Update the "Run all 10 in order" → "Run all 9 in order".

- [ ] **Step 4: Replace Audit 5** (`Manifest ↔ folder lifecycle mismatch`) with a cockpit-based version:

```markdown
### 4. Cockpit In flight ↔ folder lifecycle mismatch (WARNING)

Compare `flightdeck/cockpit.md` `## In flight` (if present) against `specs/` and `flight-plans/` folder state:
- Files in `specs/` or `flight-plans/` (NOT in `landed/`) with frontmatter `state: blocked` or `state: awaiting-review` MUST have a row in cockpit `In flight`. Missing row: **WARNING**.
- Files in `landed/specs/` or `landed/flight-plans/` must NOT have a `state:` field (or it must be `done`). Stray state: **WARNING**.
- Every row in cockpit `In flight` must point to a real file. Broken row: **WARNING**.
```

- [ ] **Step 5: Replace Audit 6** (`Stale Blockers`) target — change "For each bullet in manifest's `## Blockers` section" → "For each bullet in cockpit's `## Blockers` section".

- [ ] **Step 6: Delete Audit 7** (`Recently finished length` — logbook is gone) and renumber.

- [ ] **Step 7: Update Audit 8 (AGENTS.md drift)** — change source-field extraction "`cockpit.md` → Active focus, Next session, Hanging tasks; `manifest.md` → In flight" → "`cockpit.md` → Active focus, Next session, In flight, Hanging tasks".

- [ ] **Step 8: Update Audit 9 (orphans)** — entry set "`cockpit.md`, `INDEX.md`, `manifest.md`, and every bundle `README.md`" → "`cockpit.md`, `INDEX.md`, `rules.md`, and every bundle `README.md`". Change "excluding `landed/`, `kneeboard/`, and files that are themselves entries" → "excluding `landed/` and files that are themselves entries".

- [ ] **Step 9: Update Audit 10 (stray files)** whitelist — "Entry files: `cockpit.md`, `manifest.md`, `logbook.md`, `INDEX.md`." → "Entry files: `cockpit.md`, `INDEX.md`, `rules.md`." Known folders: drop `kneeboard/`. Drop the "Skip `landed/` and `kneeboard/`" mention if present.

- [ ] **Step 10: Verify removed**

Run: `rg -ni 'kneeboard|manifest.md|logbook|Recently finished|all 10' skills/walkaround/SKILL.md`
Expected: no matches.

- [ ] **Step 11: Verify present**

Run: `rg -n 'rules.md|all 9 in order|cockpit.s .## In flight' skills/walkaround/SKILL.md`
Expected: matches.

- [ ] **Step 12: Commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "feat(walkaround): audit cockpit not manifest/logbook; honor rules.md; drop kneeboard"
```

### Task 14: Update `emit-agents-md/SKILL.md`

**Files:**
- Modify: `skills/emit-agents-md/SKILL.md`

- [ ] **Step 1: Add a step 0** before Step 1: "Read `flightdeck/rules.md` if present. If `emit_agents_md: false`, do nothing and report 'AGENTS.md emit disabled via rules.md'. If `git: false`, still emit (AGENTS.md is not git-dependent) but skip any working-tree-clean warning."

- [ ] **Step 2: Rewrite Step 1** — it currently reads `cockpit.md` AND `manifest.md`. Change to read `cockpit.md` only. The `In flight` rows now come from cockpit's `## In flight` section (skip when the section is absent/empty). Delete the "Then use Read on `flightdeck/manifest.md`" paragraph; instead: "Extract all rows under cockpit's `## In flight` section if present (the section is omitted when empty — treat absence as zero rows)."

- [ ] **Step 3: Update Step 3** — the `## In flight` block instruction "If there are non-placeholder rows in manifest.md" → "If cockpit has a non-empty `## In flight` section".

- [ ] **Step 4: Update Step 6 report + Idempotency + Why-this-exists** — replace `manifest.md` mentions with cockpit's `In flight`. In `## Why this exists`, change "across `flightdeck/cockpit.md` + `manifest.md`" → "in `flightdeck/cockpit.md`".

- [ ] **Step 5: Verify removed**

Run: `rg -ni 'manifest' skills/emit-agents-md/SKILL.md`
Expected: no matches.

- [ ] **Step 6: Verify present**

Run: `rg -n "rules.md|emit_agents_md: false|cockpit.s .## In flight" skills/emit-agents-md/SKILL.md`
Expected: matches.

- [ ] **Step 7: Commit**

```bash
git add skills/emit-agents-md/SKILL.md
git commit -m "feat(emit): source In flight from cockpit; honor emit_agents_md/git toggles"
```

---

## Phase 6 — Migration + scaffolds

### Task 15: Write the migration procedure in `MIGRATION.md`

**Files:**
- Modify: `MIGRATION.md` (add a `## v1 → v2` section at the top)

- [ ] **Step 1: Read the current `MIGRATION.md`** to match its heading style.

Run: `rg -n '^#' MIGRATION.md`
Expected: see existing section headings.

- [ ] **Step 2: Add the v2 migration section** at the top of the body:

```markdown
## v1.x → v2.0

v2 collapses the entry layer and removes three concepts. `preflight`/`workflow` detect the old layout (presence of `manifest.md`, `logbook.md`, or `kneeboard/`) and offer this **interactive, non-silent** migration:

1. **`manifest.md` → `cockpit.md`.** Move non-placeholder `## In flight` rows into a `## In flight` section in `cockpit.md`; move `## Blockers` bullets into a `## Blockers` section. Omit either section if empty. Delete `manifest.md`.
2. **`logbook.md` history → `landed/HISTORY.md`.** Never silently dropped. Import each `## Recently finished` entry as a one-line `landed/HISTORY.md` row (newest first). Required when `git: false`; offered (default yes) when `git: true`. Move `## Deferred` items to `sketches/` files or `cockpit.Next session` lines (ask per item). Delete `logbook.md`.
3. **`kneeboard/` → classify or delete.** For each file, classify into a folder via the exit-ritual heuristics or delete. Then remove the empty `kneeboard/` directory.
4. **Optional: add `flightdeck/rules.md`** if the project needs toggles (no git, no AGENTS.md, disabled folders/gates).

Changes are staged (not committed) until the user confirms, unless `rules.md` sets `git: false`.
```

- [ ] **Step 3: Verify present**

Run: `rg -n 'v1.x → v2.0|landed/HISTORY.md|Never silently dropped' MIGRATION.md`
Expected: matches.

- [ ] **Step 4: Commit**

```bash
git add MIGRATION.md
git commit -m "docs(migration): v1.x → v2.0 guided migration procedure"
```

### Task 16: Update scaffolds

**Files:**
- Delete: `scaffolds/full/flightdeck/manifest.md`, `scaffolds/full/flightdeck/logbook.md`
- Delete: `scaffolds/full/flightdeck/kneeboard/.gitkeep` (and the directory)
- Create: `scaffolds/full/flightdeck/rules.md`, `scaffolds/full/flightdeck/landed/HISTORY.md`
- Create: `scaffolds/full/flightdeck/landed/checklists/.gitkeep`, `scaffolds/full/flightdeck/landed/incident-reports/.gitkeep`
- Modify: `scaffolds/full/flightdeck/cockpit.md`, `scaffolds/minimal/flightdeck/cockpit.md`, `scaffolds/full/flightdeck/INDEX.md`

- [ ] **Step 1: Delete removed scaffold files/dirs.**

```bash
git rm scaffolds/full/flightdeck/manifest.md scaffolds/full/flightdeck/logbook.md scaffolds/full/flightdeck/kneeboard/.gitkeep
```

- [ ] **Step 2: Create `scaffolds/full/flightdeck/rules.md`:**

```markdown
---
git: true                 # false → skills skip all git reconcile/commit steps
emit_agents_md: true      # false → emit-agents-md refuses (no-op)
disabled_folders: []      # e.g. [charts, safety-reviews]
disabled_gates: []        # e.g. [awaiting-review-owner, safety-review-disposition]
---

## House rules

<!-- Free-prose project conventions every flightdeck skill must honor.
     Delete this file entirely to use defaults (git on, emit on, all folders/gates active). -->
```

- [ ] **Step 3: Create `scaffolds/full/flightdeck/landed/HISTORY.md`:**

```markdown
# History — [project name]

<!-- Append-only landing log, newest first. One line per landing.
     Required when rules.md sets git: false; optional otherwise. Never read at session start. -->
```

- [ ] **Step 4: Create the two new `landed/` placeholders** (empty `.gitkeep` files): `scaffolds/full/flightdeck/landed/checklists/.gitkeep` and `scaffolds/full/flightdeck/landed/incident-reports/.gitkeep`.

- [ ] **Step 5: Update `scaffolds/full/flightdeck/cockpit.md`** — replace the hygiene footer's logbook/manifest references:

```markdown
---

**Cockpit hygiene** (skill: workflow):
- **80 lines hard ceiling.** Cockpit is operational, not archival. History lives in `git log` / `landed/HISTORY.md`.
- Add `## In flight` (divergent-state artifacts only) and `## Blockers` sections only when non-empty.
- `Last updated` bumps ONLY when: Next session changes / Active focus shifts / a major task completes / a divergent-state artifact resolves.
- Finished items leave `Next session`; they are not logged in cockpit.
```

The minimal `scaffolds/minimal/flightdeck/cockpit.md` already has no manifest/logbook reference — leave it unchanged (confirmed: it is cockpit-only with no footer).

- [ ] **Step 6: Update `scaffolds/full/flightdeck/INDEX.md`** — delete the `2. [manifest.md](manifest.md) — what's in flight / blocked` reading-order line and renumber the list.

- [ ] **Step 7: Verify removed**

Run: `rg -ni 'manifest|logbook|kneeboard' scaffolds/`
Expected: no matches.

- [ ] **Step 8: Verify present**

Run: `rg -n 'House rules|landed/HISTORY.md' scaffolds/full/flightdeck/rules.md scaffolds/full/flightdeck/landed/HISTORY.md`
Expected: matches.

- [ ] **Step 9: Commit**

```bash
git add scaffolds/
git commit -m "feat(scaffolds): v2 surface — rules.md + HISTORY.md; drop manifest/logbook/kneeboard"
```

---

## Phase 7 — Docs + release

### Task 17: Update top-level docs (README, AGENTS.md, GEMINI.md, TEST_PLAN.md)

**Files:**
- Modify: `README.md`, `README.zh.md`, `AGENTS.md`, `GEMINI.md`, `TEST_PLAN.md`

- [ ] **Step 1: Grep each doc for the removed terms** to find exact lines:

Run: `rg -n 'manifest.md|logbook.md|kneeboard|11 folders|3 entry files' README.md README.zh.md GEMINI.md TEST_PLAN.md`
Expected: a list of lines to edit.

- [ ] **Step 2: README.md / README.zh.md** — update any folder-count/entry-file enumeration to the v2 surface (cockpit + optional rules.md + INDEX.md; no manifest/logbook/kneeboard). Update the folder tree if shown. Add a one-line mention of `rules.md` (customization) and generalized `landed/`. Keep the two READMEs in sync (EN/ZH).

- [ ] **Step 3: AGENTS.md** — regenerate the flightdeck block via the v2 emit rules: the `## More` footer line currently reads "read `flightdeck/cockpit.md` (entry), `flightdeck/manifest.md` (open work), `flightdeck/logbook.md` (history)…" → change to "read `flightdeck/cockpit.md` and the linked artifacts." The repo's own `flightdeck/cockpit.md` will have no manifest after migration; ensure the `## In flight` source is cockpit. (This repo dogfoods flightdeck — it must itself be migrated; see Task 18 Step 1.)

- [ ] **Step 4: GEMINI.md** — same flightdeck-block fix as AGENTS.md if it carries one.

- [ ] **Step 5: TEST_PLAN.md** — update any test step referencing manifest/logbook/kneeboard to the v2 equivalents (cockpit In flight, HISTORY.md, rules.md toggles). Add a test row for: rules.md `git: false` skips git steps; migration detection fires on a v1 layout.

- [ ] **Step 6: Verify removed**

Run: `rg -ni 'manifest.md|logbook.md|kneeboard' README.md README.zh.md GEMINI.md TEST_PLAN.md AGENTS.md`
Expected: no matches (AGENTS.md `## More` line fixed).

- [ ] **Step 7: Commit**

```bash
git add README.md README.zh.md AGENTS.md GEMINI.md TEST_PLAN.md
git commit -m "docs: update top-level docs to v2 surface (rules.md, no manifest/logbook/kneeboard)"
```

### Task 18: Migrate this repo's own flightdeck, then version-bump to 2.0.0

**Files:**
- Modify: `flightdeck/cockpit.md` (this repo dogfoods flightdeck)
- Delete: `flightdeck/manifest.md`, `flightdeck/logbook.md` (if present) — there is no `flightdeck/kneeboard/` here
- Modify: `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`, `CHANGELOG.md`
- Follow: [`flightdeck/checklists/version-bump.md`](../checklists/version-bump.md)

- [ ] **Step 1: Migrate this repo's own flightdeck to v2.** Fold `flightdeck/manifest.md` `In flight`/`Blockers` into `flightdeck/cockpit.md` (omit if empty); import `flightdeck/logbook.md` `Recently finished` into a new `flightdeck/landed/HISTORY.md`; move `Deferred` items to `sketches/` or `Next session`. Then `git rm flightdeck/manifest.md flightdeck/logbook.md`. Update cockpit's hygiene footer to the v2 version (matches Task 16 Step 5).

Run after: `rg -ni 'manifest|logbook' flightdeck/cockpit.md`
Expected: no matches.

- [ ] **Step 2: Run `/flightdeck:walkaround`** on this repo to confirm the v2 audits pass clean (no manifest/logbook/kneeboard residue, no orphans).
Expected: `✅ Clean.` (or only intended INFO items).

- [ ] **Step 3: Bump the version string to `2.0.0` in all five manifests + `VERSION`** (currently `VERSION` reads `1.1.0` — stale; set to `2.0.0`). Keep all six identical.

- [ ] **Step 4: Add the `CHANGELOG.md` entry** at top under `## [2.0.0] — <today>`, Keep-a-Changelog grouped:

```markdown
## [2.0.0] — 2026-06-01

### Changed (BREAKING)
- Collapsed the entry layer to `cockpit.md` (single must-read) + optional `INDEX.md`. `In flight` and `Blockers` now live as omit-when-empty sections in `cockpit.md`.
- Generalized `landed/` to mirror any source folder (`landed/checklists/`, `landed/incident-reports/`, …).

### Added
- `rules.md` customization layer: `git` / `emit_agents_md` / `disabled_folders` / `disabled_gates` toggles + free-prose house rules, read first by every entry skill.
- `landed/HISTORY.md` append-only landing log (required when `git: false`).
- Multi-plan specs carry a `## Plans` state-word ledger (B1).
- Guided v1→v2 migration in `preflight`/`workflow` (see `MIGRATION.md`).

### Removed (BREAKING)
- `manifest.md`, `logbook.md`, and the `kneeboard/` folder. Scratch now lives in project-root `tmp/`.

Design: [flightdeck/landed/specs/2026-05-31-flightdeck-v2-entry-collapse-and-rules-design.md] (move the spec to landed/ on ship).
```

- [ ] **Step 5: Verify manifests agree**

Run: `rg -n '"version"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json; cat VERSION`
Expected: all show `2.0.0`.

- [ ] **Step 6: STOP — do not commit/tag/push yet.** Per the user's instruction, hold here. Present the full diff and the moved-to-`landed/` spec, and ask the user whether to commit (and whether to commit the design spec + plan together). Only on explicit confirmation: move the design spec + this plan to `landed/`, then commit `v2.0.0: …`, tag annotated `git tag -a v2.0.0`, and `git push origin <branch> --follow-tags` per the version-bump checklist. Branch off `main` first (do not commit directly to `main`).

---

## Self-Review (run before execution)

- **Spec coverage:** A1 → Tasks 3–6, 11–14, 16. B1 → Task 7. C1 → Task 8. C3 → Task 9. D (rules.md) → Tasks 1–2, 11–14. History fallback → Task 10, 16, 18. Migration → Tasks 11, 15, 18. Release → Task 18. All seven original frictions + the history follow-up are covered.
- **Type consistency:** toggle key names (`git`, `emit_agents_md`, `disabled_folders`, `disabled_gates`), ledger state words (`pending`/`active`/`blocked`/`awaiting-review`/`landed`/`scrapped`), and file paths (`landed/HISTORY.md`, `flightdeck/rules.md`) are used identically across all tasks and match the spec.
- **No placeholders:** every new file's full content is given; every removal/rewrite names exact terms + a grep assertion.
- **Ordering:** rules.md first; version-bump + repo self-migration last (the final grep is the release gate); commit/tag/push gated on user confirmation.
```
