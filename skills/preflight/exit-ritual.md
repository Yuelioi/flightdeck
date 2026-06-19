# Exit ritual

The protocol for closing an AI coding session cleanly so the next preflight can pick up without context loss.

## Core principle

**90% of session-end decisions are obvious.** Classify directly. Only **true ambiguity** triggers brainstorming. Default-brainstorm is high-friction → skipped → knowledge lost.

## Decision tree

```
Session is wrapping up
↓
Step 1: Are there pending hanging tasks?
        (open items in cockpit ## Hanging Tasks)
├─ yes → resolve them first, then continue
└─ no  → proceed to step 2

Step 2: Did this session produce new knowledge / discover a bug / agree on a decision?
├─ no  → only update cockpit.md if Focus shifted, then proceed to Step 4
└─ yes → for each piece, apply classification heuristics in order, first match wins
         (full triggers + detail in "## Classification heuristics" below):
           (a) bug + root cause → incidents/ (status: active; existing topic → append [Case N])
           (b) repeated procedure, 2nd occurrence → checklists/ (status: active)
           (c) design decision → specs/ (status: active, or idea if unstarted; brainstorm if substantial)
           (d) multi-step task → plans/ (status: active; optional implements: specs/<x>.md)
           (e) imported external material → references/ (status: active)
           (e2) authored standing technical reference (architecture / rationale / subsystem) → docs/ (status: active)
           (f) long-term idea / unstarted design → specs/ (status: idea, no date prefix; mark "Revisit when")
           (g) one-off / log / byproduct → DO NOT WRITE (gate)
           (h) ambiguous, no clear primary → brainstorm with user

         (External review feedback is NOT a folder: fold its disposition into the
          reviewed spec's ## Review notes; raw text stays in project-root tmp/. See § Classification heuristics.)

Step 3: Regenerate INDEX for changed folders — full rules in "## INDEX regeneration —
        scope rules" below. Gist: regenerate the <!-- AUTO --> region only for folders
        with activity this session; walkaround owns the full INDEX↔frontmatter check.

Step 3a: Suggest status for affected artifacts
         For each artifact written or touched this session, the AI applies the next
         typical status per the recommended flow ([protocol § Status ⟂ location](protocol.md#status--location-two-orthogonal-axes)).

         Status changes are applied by judgment (reversible — reported in the banner; the user can undo). The user may
         change status to any legal value at any time — the AI does not block.
         (Status is a label — no table, no verbs.)

         Bump last_updated: for each spec/plan changed substantively this
         session — body OR frontmatter, not a typo/wording-only edit — set its
         `last_updated:` to today before regenerating that folder's INDEX. A
         confirmed status flip already counts as substantive. **Idea-stage
         specs** (`status: idea`): bump only if the file already carries
         `last_updated` — don't *add* it to a bare idea (its `status` +
         `summary` suffice). This is the landing
         anchor for the recommended-but-not-required workflow `last_updated`;
         knowledge artifacts already carry their own required `last_updated`.

         For done artifacts, offer to land them via the
         single shared Land Routine (see "## Land Routine" below) —
         do not inline the move/INDEX steps here.

Step 3b: Graduate finish (landing = primary path).
         For each `graduate: true` spec that is `done` AND still in `specs/`:
         - Rewrite its body into a current-truth perspective as a new `docs/` entry.
           The new doc MUST carry `when_to_read`, `applies_to`, and `when_to_update`
           (spec files carry none of these; omitting `when_to_update` opts the doc out
           of stale detection immediately, defeating the point).
         - A `## Design tradeoffs` section MAY be preserved in the new doc when the rationale
           has lasting value; other spec-internal history is not ported.
         - Move the rewritten file to `docs/<slug>.md` (or a nested area if appropriate).
           NO archive twin — one artifact, the docs/ copy. Do NOT also archive the
           source spec.
         - Remove the source `specs/` file; update both `specs/INDEX` and `docs/INDEX`.
         Idempotency key = source file still in `specs/`. Once moved, the key is gone;
         re-runs are safe no-ops. A missed window is caught by the next landing's rescan
         (this step walks every `graduate: true` done spec still in `specs/`, not just
         this session's).

Step 3c: Stale detection + pending-verify surfacing (landing/soft-landing = single on-exit ritual).
         The stale flip happens ONLY in this on-exit step; preflight entry no longer flips stale.
         The trigger is **mechanical path overlap**:
         Run: `flightdeck_index.py <deck> --changed-since-anchor`
         (emits paths changed since the last `Flightdeck-Sync:` trailer commit, plus
         worktree uncommitted changes).
         Intersect the returned changed paths with the **path entries** in every `docs/` + knowledge
         artifact's `applies_to` (entries containing `/`, prefix-matched; plain word-tags are routing-only,
         excluded) — a hit flips it stale. **Do not read the doc body, do not evaluate `when_to_update`
         as a runtime condition**: `when_to_update` is a human-facing rationale; the runtime decision
         uses the `applies_to` path entries.
         For each knowledge artifact whose `applies_to` path entries intersect the changed set:
         - Auto-flip `status: stale` in its frontmatter (no pre-ask — stale is
           reversible, local, purely a warning; "docs quietly lying" is the worst outcome).
         - Idempotent: already-`stale` = no-op.
         - Surface a one-line `pending-review: <file>` note in cockpit `## Pending Review`
           (the standing awaiting-review home — no longer an optional subsection).
         When no `Flightdeck-Sync:` anchor exists yet (first landing on a fresh
         deck), the scan has no prior commit to diff against and falls back to this
         session's worktree changes only — same intersection, narrower change set.

         Pending-verify (the verify-debt list) rides the SAME surfacing channel, but is
         NOT hand-written — it is **derived by scanning every `verify`-carrying
         artifact across the active tree + archive/** (via
         `flightdeck_index <deck> --verify-pending`, which prints `path<TAB>note`
         for each; semantically a full scan — the implementation may index/cache).
         The two debts are distinguished by the `verify` field on the same pending-review
         channel: `⚠ unverified: <file> — <how>` (verify present) vs the plain
         `⚠ pending-review: <file>` (stale, no verify). The cockpit line is a **derived
         display, NOT the source of truth** — editing or regenerating cockpit cannot
         lose the debt: the next scan rebuilds it from the `verify` fields on disk.
         An archived `done + verify` item still being scanned-out every preflight is
         **intentional** (non-blocking + persistently visible until verified), not an
         archive-semantics bug.

Step 4: Update cockpit.md — full rules in "## Cockpit update — what changes"
        below. Gist: bump Updated only on the 4 sanctioned triggers;
        regen the ## In Progress AUTO region from status:active; auto-write ## Next;
        Focus / Hanging Tasks as needed. Then run the Length check (§ below).

Step 5: Commit (local) + push (ask) — default: commit locally without asking
        (local commits are reversible); NEVER push without asking (push is outward).
        - default        → generate the message + `git commit` locally, no prompt
        - deck rule (ask-before-commit) → ask "Commit now? (Y/n)" before the local commit
        - deck rule (don't auto-commit) → do NOT commit; leave the changes for you / CI
        - push → only when appropriate AND after asking; never automatic
        - Message: use checklists/commits.md if it exists; else terse imperative subject + reasoning in body
        - **`Flightdeck-Sync:` trailer (REQUIRED on every landing/soft-land commit):**
          append `Flightdeck-Sync: <git-ref>` as a commit trailer (the ref is `HEAD`
          *after* the commit — i.e. the new SHA, or the current branch tip). This is
          the anchor that `--changed-since-anchor` keys on for the next landing's
          stale-detection pass (single on-exit ritual). Without it, the anchor is absent and
          the next landing must fall back to a full worktree diff.
```

### Step 5a — Recurrence sweep + promotion gate (wrap-up)

**Recurrence sweep first.** For each bug / lesson this session produced, compare it against existing `incidents/` (`applies_to` overlap / same root cause):
- **Clear same-incident match** → auto-append `## [Case N]` (with today's date) **and** bump that incident's `recurrences` frontmatter counter. No per-increment confirm — counting is AI-facing bookkeeping, and the consequential step (promotion) stays gated below.
- **Ambiguous match** → ask the user before recording (the false-positive guard lives here).

Then, **for each incident touched** (newly written, or recurrence-bumped) this session, evaluate the 3-criterion promotion gate:

1. `recurrences ≥ 3`?
2. Recurred across ≥ 2 distinct sessions (distinct `[Case N]` dates)?
3. Remediation pattern stable across cases?

If ALL three hold: **promote** `incidents/<topic>.md` → `checklists/<topic>.md` by judgment (reversible — move the file) and **surface it in cockpit `## Pending Review`** for veto; undo reverses it. No pre-confirm gate — the three criteria are themselves the guard against false positives, and the user retains final say via Pending Review / undo ([protocol § Act-report-close loop](protocol.md#act-report-close-loop)).

If any criterion fails: skip silently. Don't promote-prompt for marginal cases.

## Classification heuristics

These are first-match-wins rules — apply in order. The first one that matches the new piece of knowledge wins; do not over-think.

### (a) Bug + root cause → `incidents/`

**Trigger phrase**: "I assumed X but actually Y" / "this kept failing because"

Always goes to `incidents/`. Check existing topics first — if related, append `## [Case N]` to existing file. Do not start a new file for the same recurrence.

Set `status: active` in frontmatter.

**Also fires on an abandoned path / wall, not just a shipped fix.** If this turn **tried an approach and dropped it** — or hit a wall that cost real time — record the **failure path + why it failed** (including why a plausible-looking option doesn't work), not only the final working fix. Negative knowledge ("X looks viable but fails because Y, so we chose Z") is exactly what stops the next session from re-walking the dead end. ✅ "Cursor `sessionStart` `additional_context` proved unreliable → switched to a `.cursor/rules/*.mdc` rule file"  ❌ silently keeping only "used a rule file" with the rejected option lost. The write gate still applies (a momentary typo you fixed in the same breath is not a wall).

### (b) Repeated procedure → `checklists/`

**Trigger phrase**: "every time we do X, the steps are" / "the way to do X correctly is"

Goes to `checklists/` **only on the second occurrence**. First time is ad-hoc work; second time is a pattern worth recording.

Set `status: active` in frontmatter.

### (c) Design decision → `specs/`

**Trigger phrase**: "we should architecturally do X" / "the design here is"

Substantial decisions go to `specs/`. If the reasoning is complex enough to matter later, brainstorm with the user first — don't free-write.

Set `status: active` if work has begun, or `status: idea` if it is captured but unstarted.

### (d) Multi-step task → `plans/`

**Trigger phrase**: "let me break this into steps" / "the plan is"

Produce a structured plan in `plans/`. Optionally reference the governing design with `implements: specs/<x>.md`. Don't free-write.

Set `status: active` in frontmatter.

### (e) Imported external material → `references/`

**Trigger phrase**: "here's the RFC" / "import this competitor's API design"

Raw external material — competitor code, RFCs, articles, research papers — goes to `references/`. Authored operational procedures go to `checklists/` instead (keep the split clear).

Set `status: active` in frontmatter.

### (e2) Authored standing technical reference → `docs/`

**Trigger phrase**: "here's how the X subsystem works" / "the architecture / rationale here is, for future reference"

Self-authored, durable explanatory material — architecture overviews, design rationale, subsystem references you wrote to *understand* the system — goes to `docs/`. Keep `docs/` (explanatory: things you read to comprehend) distinct from `checklists/` (procedural: steps you execute) and from `references/` (imported external raw material, not authored). If it teaches *how it works*, it's `docs/`; if it tells you *what steps to run*, it's `checklists/`.

Set `status: active` in frontmatter.

### (f) Long-term idea / unstarted design → `specs/` (`status: idea`)

**Trigger phrase**: "we could maybe one day" / "wouldn't it be cool if"

Goes to `specs/` with `status: idea` (no date prefix — the to-start pool). Mark a "Revisit when" condition if you can. Starting it later is a single flip `idea → active`.

### (g) One-off → DO NOT WRITE

**Trigger phrase**: "the log output today was" / "I tried these 5 things and got"

Do not write. Gate strictly. Flightdeck is not a session log.

### External review feedback → reviewed spec's `## Review notes` (no folder)

**Trigger phrase**: user pastes review text from another AI / colleague

There is **no `debriefs/` folder**. The raw feedback is a transient input — keep it in project-root `tmp/` (gitignored, the user's own habit) and read it. Its lasting value is the **disposition** (adopt / reject / defer), which folds into the **reviewed spec's** own `## Review notes` section. Raw text is discarded once dispositioned. See [folder-semantics § External review feedback](folder-semantics.md#external-review-feedback-no-folder).

### (h) Ambiguous → brainstorm

**Trigger phrase**: "this is sort of an incident but also a checklist"

If genuinely ambiguous, brainstorm with the user. Use the AI-asks-user template below.

### Quality of the artifact body — how to write what you keep

Once the gate says *keep it*, write the body so it is reusable (this is **not** part of the (a)–(h) match chain above — it is how you write whatever (a)–(f) routed):

- **Record the substantive result / change, not process meta-narration.** State the new fact or constraint about the system / your understanding directly — "`emit()` gained a Codex branch", "X failed because Y" — the statement stands on its own, **no** `implemented` / `discovered` verb prefix required. Do **not** write process meta-narration ("analyzed…", "investigated…", "currently looking at…"). The opposite of a good body is *process narration*, not "state vs change".
  > A verb table (implemented / fixed / decided / migrated) only **illustrates the shape of a good entry — it is not mandatory**; `discovered` / `decided` slip back into action-sentences, so prefer stating the result directly, and many valid statements ("`emit()` gained a Codex branch") need no leading verb at all.
- **Each fact stands alone** — no pronouns ("it" / "this"); readable out of context.
- **Carry the load-bearing literals** — filenames, function / symbol names, key values, error strings. Not "changed that function" but "`emit()` gained a Codex branch".
- **Examples + one cross-kind line:**
  - ✅ "`emit()` now branches injection fields per host (Claude / Codex / Gemini = `additionalContext`)"  ❌ "researched how each host differs in injection fields"
  - Decisions / incidents likewise: record "chose Z over the alternatives because of constraint Y" / "X failed because Y" — **not** "discussed several options".

## AI-asks-user template (ambiguous classification)

When triggering (h), open the conversation with a structured ask:

```
I learned something from this session that I want to record, but I'm
not sure where it belongs. Here's the content:

> <one-paragraph summary of the knowledge>

Candidates:
- incidents/   if the takeaway is "next time, avoid X because Y"
- checklists/  if the takeaway is "the steps to do X are"
- specs/       if the takeaway is "the design decision is X"
- plans/       if the takeaway is "here are the steps to implement X"

My weak preference: <one candidate>, because <one reason>.

Which do you want? Or skip the write?
```

This forces a structured decision in seconds. The "skip the write" option is critical — defaulting to write is the failure mode.

## Self-asserting `done` — non-blocking, carry `verify`

The AI **may** self-assert `done` on **any** task — including needs-verify work — but a needs-verify `done` **must carry a `verify: <one-line how-to-verify>` marker** (the verification debt, not a refusal to mark it done). The old needs-verify *block* (which forbade self-asserting `done` on such work) is **removed**: verification is now a [non-blocking marker, not a gate](protocol.md#non-blocking-verification). The boundary is still **rule-first, examples-second** (avoid the "list = exhaustive" trap):

- **Rule:** anything that will be **mechanically executed by AI or scripts, where a misjudgment is not easily noticed**, is **needs-verify** — self-assert `done` **and** stamp `verify:` so the debt survives. Everything else is no-verify (`done`, no `verify`).
- **Examples (non-exhaustive, needs-verify):** any external-system change (open PR, deploy, write DB, send email…); governance / data-model edits (`protocol.md`, `rules.md`, `AGENTS.md`, frontmatter fields, script contracts).
- **Print a verdict line** so the call is observable and auditable:
  - needs-verify → `[decision: <reason>; pending-verify: <how>; done + verify]`
  - no-verify → `[decision: <reason>; no verify needed; done]`
- The `verify:` **value** is the one-line how-to-verify (e.g. `verify: phase-4 live validation on each host`) — its *content* survives any cockpit edit/regen and the deterministic scan re-surfaces it. Binary present/absent only — **no `verify: failed` value** (see [verify field](protocol.md#verify--the-verification-marker)).
- **Boundary this does NOT loosen — ask before outward actions.** Loosening only touches the **self-assert-done marker**. Whether the AI may *execute* an outward action (open PR, deploy, send email) is a **separate, unchanged** concern governed by the commit/push default + the ask-before-outward-action rule — marking a deploy task `done + verify` is not permission to run the deploy.
- Self-asserting `done` is a **state write only** — soft-landing still does **not** archive (archival stays full landing's). The safety that used to come from *blocking* now comes from **visibility** (the `verify` debt is re-surfaced every preflight via the deterministic scan) **plus reversibility** (`done` + `verify` are frontmatter fields the user can flip / clear; no commit/move was produced).

### Resolving a `verify` debt — per-kind pass/fail

When the user performs the verification, act per the artifact's kind. The canonical pass/fail table lives in [protocol § Non-blocking verification](protocol.md#non-blocking-verification) — the operational steps here defer to it. **First identify the kind** (knowledge vs workflow — by folder), then:

- **Verify passes:**
  - **workflow** (`done` + `verify`): **drop the `verify` field**; it stays `done` and now enters the `--archivable` set (no inbound `active` edge → lands on the next sweep).
  - **knowledge** (`stale` + `verify`): **drop the `verify` field** **and** flip `stale → active` (the verify-pass exception to "stale→active is user-asserted only" — see [protocol § Status transition authority](protocol.md#status-transition-authority-table-single-source-of-truth)).
- **Verify fails** (both kinds): **revive to `active`** (`mv` back from `archive/` if it had already landed) and **KEEP the `verify` field** — the work is re-done + re-verified. There is **no `verify: failed` value**; the marker just stays present.
- **One at a time.** Multiple pending verify items are resolved **independently, one per verification** — never batch-cleared.

## Hanging Tasks — block session exit

A session **cannot be closed cleanly** while an open `## Hanging Tasks` item remains. Either resolve it now, or record it explicitly in `cockpit.md` "Hanging Tasks" (`- [ ] <blocking item>`) so the next preflight sees it on entry and resolves.

`Hanging Tasks` in cockpit is a **hand-maintained** list — the AI does not auto-derive it from INDEX. Add and clear entries explicitly.

(There is **no debrief-disposition gate** — `debriefs/` was removed. External review feedback is transient (project-root `tmp/`); its disposition folds into the reviewed spec's `## Review notes` as part of normal spec editing, not as an exit-blocking gate.)

## INDEX regeneration — scope rules

Regenerate the `<!-- AUTO -->` region of a folder's `INDEX.md` **only when that folder had activity this session**:

- Activity = file added, modified, moved, landed, or status changed
- Non-activity = the folder was only read (grep, preflight routing, etc.) — leave its INDEX alone

The hand area outside `<!-- AUTO -->` is never touched by the AI — grouping notes, cross-references, and other hand-written content are preserved.

Walkaround is responsible for the **full-consistency check** — it regenerates all indexes and validates every frontmatter. Exit ritual only touches changed folders.

### Row format — how each AUTO row is built (single source of truth)

Every `<!-- AUTO -->` row is generated **from the file's frontmatter only — never its body** (a further token saving, complementing read-INDEX-first). `status`, `landing`, and `walkaround` all build rows this way; do not reimplement it elsewhere.

- **Workflow folders** (`specs/` `plans/`): `- [<file>](<file>) — <status> — <summary>`, where `<summary>` is the file's `summary` frontmatter copied **verbatim**. If the file has no `summary` (it is recommended, not required), omit the trailing ` — <summary>` segment entirely. `implements` / `supersedes` / `related` / `note` are never shown in the INDEX (reverse links are grep-derived). `specs/INDEX` groups its AUTO region into two sections: `Backlog (idea)` / `Active · Done` — see [folder-semantics § specs/](folder-semantics.md#specs--designs).
- **Knowledge folders** (`incidents/` `checklists/` `docs/` `references/`): `- [<file>](<file>) — <status> — when_to_read: <…> — applies_to: <…>`. (`references/` rows show project/file count, not per-file status; `docs/` rows read `<status> — when_to_read: <…> — applies_to: <…>` like the other authored knowledge folders.)
- **`|` escaping (fallback):** the `summary` constraint already forbids `|` `[` `]` and newlines, but defensively escape any literal `|` pulled from frontmatter as `\|` so a stray pipe can never corrupt the generated line.

### Script path (the mechanical engine)

INDEX regeneration and the INDEX↔folder consistency check are fully mechanical — they read frontmatter and emit the rows above. flightdeck ships these as scripts and a **script runtime is mandatory** (recorded in `rules.md` frontmatter `runtime: uv|python|node`, stamped by `launch`); the call form is selected per [protocol § Rule resolution order](protocol.md#rule-resolution-order) (`uv run …/flightdeck_index.py` / `python …/flightdeck_index.py` / `node …/flightdeck_index.js` — the `.py` and `.js` are byte-parity twins). `status`, `landing`, and `walkaround` invoke it directly; there is **no hand-rebuild path** — a recorded runtime that cannot be found is a hard failure ([protocol § Rule resolution order](protocol.md#rule-resolution-order)), never a silent fall-through to manual markdown.

- `flightdeck_index <deck>` implements **exactly the Row format rule above** — it regenerates every folder + root `<!-- AUTO -->` block from frontmatter; `flightdeck_index <deck> --check` reports drift and exits non-zero (used by walkaround). It runs in a subprocess, so its file reads never enter context (a token saving on top of determinism).
- `flightdeck_lint <deck>` covers the **mechanical subset of the walkaround audit** — status legality (Audit 1), orphan plans (Audit 4), INDEX↔folder drift (Audit 5, reusing `flightdeck_index`), dangling references (Audit 7), and the unambiguous stray-file cases (Audit 8). It emits a JSON `{"findings": [...]}` list (each with `audit` / `severity` / `path` / `message`) and exits non-zero when any CRITICAL/WARNING is present. The dangling-ref scan covers repo-root `*.md` by default (the deck's parent); `--repo-root <path>` points that part of the scan at a different root. `walkaround` uses it for those audits — the model still reads the JSON and narrates/judges.

The script **computes facts only**; the judgment-bearing audits (knowledge classification, migration decisions, AGENTS.md semantic drift, full stray-file reachability) stay in the markdown checklist. Never let the script make judgments (classification, status decisions, routing) — it only generates/checks the deterministic INDEX rows.

## Cockpit update — what changes

```
Updated:          stamp only — `Updated: <date> · <who> · Stage: <stage>`; NO changelog. Bump on:
                  (a) Next content changes
                  (b) Focus shifts (main thread moved)
                  (c) A major task / phase completes (user-perceivable progress)
                  (d) An artifact lands or a blocker resolves
Focus:             one coarse thread label + current spec/plan link; ≤~100 chars. NO goal/criteria/method (→ spec body; invariants → rules.md)
Pointers:          thin nav anchors (config/conventions/INDEXes/archive), hand-maintained; never content
## Next:           auto-written — next concrete single action + plan link; progress checklists → plan ## Progress
## In Progress:    AUTO — regen from every status:active spec/plan (do NOT hand-write); renders truncated summary head
## Key Context:    agent-judged — load-bearing literals a next session needs to resume; drain/shrink entries that no longer carry (or - (none))
## Pending Review: agent-judged — AI work awaiting your sign-off + surfaced stale pending-review notes; drains when reviewed (or - (none))
Hanging Tasks:     hand-maintained list — add new blocking items, clear resolved ones
```

**`## In Progress` is AUTO-derived, not hand-written.** Regenerate its `<!-- AUTO:inprogress -->` region from every `status: active` spec/plan (same mechanism + row format as INDEX; a file's `note:` appends `[note: …]`). The `status` skill regenerates it on a status flip; landing regenerates it here. A hand edit is overwritten on the next regen. This is what makes cockpit a **status projection** of the active set — an artifact is in cockpit iff it is `active`, so orphans are structurally impossible.

**`## Next` is auto-written by landing** (and on `idea→active` / a completed milestone / **a plan-task checkpoint** — see [§ Checkpoint](#checkpoint--lightweight-board-sync-subpath)). Its content is the next concrete **single** action — either (i) start an idea from the to-start pool, or (ii) advance an active artifact. `preflight` reads it but does not rewrite it (a stale entry is corrected at the next write point).

**`Focus` vs `## Next` — different granularity, no overlap.** `Focus` = the current session main thread, one coarse label + a link to the spec/plan it names; goal / criteria / method live in that spec, not in cockpit. `## Next` = the next concrete executable single step + its plan link. The user adjusts either by directing the AI, not by hand-editing.

**`Pointers` is thin navigation, hand-maintained (not AUTO).** A single line of jump anchors — config → `rules.md` · conventions → file · artifacts → folder INDEXes · history → `archive/` — anchors only, never content; the content lives at the target. Omit the line when a deck has nothing worth pinning.

**`## Key Context` is a transient staging area, not a permanent home.** It carries the **load-bearing literals a next session needs to resume** (the file under edit, a failing test name, an error string, a key value) — literals, not prose; agent-maintained (not AUTO); nothing to carry → `- (none)`. Crucially, **nothing lives here forever** — each entry leaves by one of two exits at landing:

- **Drain (near-deterministic).** When an entry's referent — the spec / plan / incident it points to — was archived / graduated / flipped `done` this session, it is a dead pointer: drop it (move any still-live detail into the matching `specs/` entry first). Auto-detected from the session's archived set and **auto-dropped, reported in the landing banner (undoable)** — no pre-ask.
- **Graduate (judgment — same as a `done` spec graduating to `docs/`).** A durable entry that does *not* point at a dying referent — a standing principle, convention, or always-true fact — does not belong on the dashboard: move it to its permanent home (below) and remove it from cockpit. A durable principle never points at a dying referent, so the drain exit never touches it; the graduate exit is what keeps it from rotting in place. (No `pin` marker, no protect-in-place, no age-based eviction — age is the wrong trigger for Key Context: it would evict standing principles.)

**Home-by-kind (graduate target — agent-neutral):**

| Durable entry kind | Graduates to | Why |
|---|---|---|
| Behavior red line / convention | `rules.md` | read in full every ritual — loudest, agent-neutral |
| Design rationale / decision | `docs/` (routed by `when_to_read`) | surfaced when relevant; off the always-loaded budget |
| Standing project meta | the project's agent instruction file (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`, per the running agent) | always loaded — use sparingly |

`rules.md` and the agent instruction file are always-loaded budget — keep them lean; most durable Key Context is conditionally-relevant rationale and belongs in `docs/` (often it is already a duplicate pointer to a doc — then just delete the cockpit copy).

**`## Pending Review` is the sign-off queue (agent-judged, not AUTO).** Things the AI completed and self-judged `done` but you haven't approved yet — plus the surfaced stale `pending-review` notes from Step 3c (both are "awaiting your eyes"). Each row `- [<artifact/topic>] <what changed · how to look>`. **Non-blocking** (you can land with items queued — unlike `Hanging Tasks`) and **subjective** (human sign-off — unlike the objective `verify:` / `⚠ unverified` scan). Drains when you sign off, or at the next landing once confirmed; nothing queued → `- (none)`. **Aged-item forcing function:** an item that has survived **≥ 1 landing still unsigned** is no longer left to pile up silently — landing surfaces each aged item and prompts you per item: *sign off / keep / drop*. The sign-off stays explicit (items are never auto-deleted); the prompt only stops the queue from rotting into a junk drawer.

**Accumulator-drain discipline.** `## Key Context` and `## Pending Review` are the two non-AUTO sections that *accumulate*; each MUST converge or it rots into a junk drawer. Convergence is a judgment step → it runs at **landing** (which already rewrites cockpit by judgment), not at the mechanical checkpoint. `Key Context` (transient staging, above): **drain** an entry whose referent died this session, **graduate** a durable entry to its home-by-kind — either exit removes it from cockpit; **shrink** a still-live entry to a one-line pointer. `Pending Review`: drain on sign-off, and **prompt** each item aged past one landing (sign off / keep / drop). The 80-line cap is the ceiling, not the discipline — converge per-entry first. (`walkaround` Audit 14 already flags a referent-died / oversized `Key Context` as a non-blocking INFO; it never drains.)

**`Updated` is a freshness stamp, not a session-activity log.** It carries `<date> · <who> · Stage` and nothing more — **no parenthetical changelog of what the session did.** False triggers that must NOT bump it: pure exploration / grep / reading code; typo fixes; internal refactor with no user-perceivable surface; a commit that doesn't complete a cockpit task; running already-passing tests. The record of *what changed* lives in `git log` + the commit message + the spec/plan body — never as a narrative in cockpit.

**When to update mid-session — this is the *checkpoint*:** at every plan / plan-task boundary, refresh `## Next` and advance the plan's `## Progress` `current:` pointer **before** starting the next task — don't wait for landing. This lightweight board-sync has a name and a home: see [§ Checkpoint](#checkpoint--lightweight-board-sync-subpath).

**Length check before exit — gated criteria.** (1) **Line count:** `cockpit.md` > 80 lines → trim immediately (drop finished items; move design detail to a `specs/` entry). (2) **Per-field density** — catches the few-lines-but-dense-prose bloat the line count misses: scan each hand-maintained field against its soft cap — `Focus` ≤ one coarse line / ~100 chars · each `## Key Context` / `## Pending Review` entry ≤ a one-line literal pointer (and no entry whose target already archived/graduated — that case is the accumulator-drain above). (3) **Role-creep** — a field holding content that belongs in another home: `Updated` carrying a changelog (→ git log + commit) · `Focus` carrying goal/criteria/method (→ spec body) · `## Next` carrying a progress checklist / rationale list / milestone links (→ plan `## Progress`). Any (2)/(3) hit → **propose a gated trim**: route the off-home content back to its home (git / spec / plan), then cut the cockpit prose; ≤ cap and in-role → no-op (idempotent). The trim is **gated** because *which detail is still live and where it goes* is live judgment, never an auto-delete. `## In Progress` is AUTO and usually short; piled-up `active` is itself a focus-loss signal — **> ~5 active threads → emit a non-blocking nudge** "N active threads — consider parking/closing some" (remind only, never delete; the root cause is too many open threads, fixed by behavior not by cockpit). History is `git log` + the `archive/` folder, never cockpit.

### Soft-landing banner — the visible safe-to-close signal

A **soft-landing** (signal 3) ends the turn with the **unified banner** (full format / field rules → [protocol § Act-report-close loop](protocol.md#act-report-close-loop)):

```
─── 🛬 soft landing ───
[Stage]   <lifecycle stage>
[Saved]   <≤3 filenames; overflow → "+N more">; cockpit updated.   (no commit hash — soft-landing does not commit)
[Pending] ⚠ <N> await verification → cockpit Pending Review.   (omit when empty)
You can close / switch the conversation anytime — next preflight resumes from the board.
```

- `[Saved]` wording is **persisted / saved, never "LANDED / archived / done"** — soft-landing does not archive and may not be `done`; never collide with `done ≠ archived`. No commit hash (soft-landing does not commit).
- **No silence on no-increment:** a flow turn with no new knowledge still emits the banner with `[No change]` (an honest "nothing to save, board current, safe to close") — replacing the old print-nothing rule. Only a **pure conversation / clarification turn** (no flow, no deck change) prints no banner.

## Checkpoint — lightweight board-sync subpath

A **checkpoint** is the cheapest possible status-write: it keeps the persisted board (`cockpit.md` + the active plan file) equal to *actual* progress, so a user can close the conversation at any plan-task boundary and the next `/flightdeck:preflight` resumes on a true picture — no lost context. It is **a strict subset of landing**: landing = checkpoint + the wrap-up heavy lifting (knowledge-classify, INDEX regen, archive, smoke-check, commit).

**Three tiers, one landing.** `checkpoint` ⊂ `soft-landing` ⊂ `full landing` — same machinery, different trigger + range (not three rituals):

| Tier | Essence | Trigger | Range | commit / archive |
|---|---|---|---|---|
| **checkpoint** | save **state** | plan-task boundary / end-of-turn state-only increment | board only (`## Next` + plan `current:`), disk-only | none |
| **soft-landing** | save **state + knowledge** | end-of-turn with a **knowledge increment** (signal 3) | checkpoint + classify knowledge + regen changed INDEX | **neither** |
| **full landing** | + **advance lifecycle** | `done` / explicit `/flightdeck:landing` | soft-landing + archive done + promotion gate | + local commit + archive |

`soft-landing` carries **no commit and no archive** — both are "traceable tails" deferred to a full landing (durability rides on files being on disk; `preflight` reads files, not git). See [§ Land-readiness signal 3](#land-readiness-check).

**Trigger (AI self-invoke — not a hook):** a plan or plan-task **finishes**. Trivial edits do **not** trigger (avoid noise commits/churn). This extends the "rituals self-invoke" trigger point from *session-wrap only* to *also task boundaries*; it is the AI deciding to run landing's light mode, never a harness-timed hook (consistent with flightdeck's deliberate no-startup-hooks design).

**Action — exactly two board writes, then stop:**
1. Refresh cockpit `## Next` to the next concrete single action (the next task).
2. Advance the active plan's `## Progress` `current:` pointer to the next task.

Both are **disk writes only**. A checkpoint **does NOT**: classify new knowledge · regen any INDEX · archive a `done` item · run the smoke-check · bump `Updated` for a non-milestone task · **commit**.

**Why no commit (the two orthogonal axes):** "close-and-reopen with context intact" rides on the **board being on disk**, not on git — `preflight` reads the *files*, regardless of commit state. So a checkpoint syncs the board (cheap, every task, uncommitted) while **commit stays a deliberate, separate axis** (landing or a milestone), avoiding a trail of noise commits. (If a checkpoint *does* coincide with a milestone worth a commit, a local commit is still within the default — reversible; push always asks.)

**Reuse, don't fork:** a checkpoint's two writes are the *same* `## Next` / `## Progress` logic landing's cockpit board-sync step uses — there is one implementation. `landing` simply has a `checkpoint` mode that runs only that board-sync step and skips everything else (see [landing SKILL.md § Modes](../landing/SKILL.md#modes--full--soft-landing--checkpoint)).

**The *mechanical* half of board-sync is welded by a passive turn-end hook.** Every host fires it (Claude/Codex `Stop`, Cursor `stop`, Gemini `AfterAgent`); it regenerates the `## In Progress` AUTO region + each `INDEX.md` `<!-- AUTO -->` region at end-of-turn (idempotent `scripts/flightdeck_index.py <deck>`; never blocks, never archives). So you **don't carry the mechanical AUTO regions at turn end — they self-heal.** What stays yours at every plan-task boundary is the *judgment* half: refreshing `## Next`, advancing the plan's `## Progress` `current:` pointer, and the soft-land decision (any write-gated knowledge this turn? → persist it). This hook is a deterministic enhancement, not a behavior the protocol depends on — see the project's cross-host-hooks doc for the passive-vs-gating hook decision principle.

## Land Routine

The single source of truth for landing artifacts. Both `landing` (Step 3a above) and the `status` skill (`skills/status/SKILL.md`) MUST call this — do not reimplement it anywhere.

Landing operates on a **land set**: the one-or-more `done` artifacts archived in this operation (a single `status land` is a set of one; a `landing` sweep may land several at once). Process the whole set together — **collect the remap first, then migrate, then rewrite** — so cross-references *inside* the set survive:

0. **Compute the land set deterministically — don't read bodies to decide.** Which `done` artifacts are archivable is a **deterministic fact**: a `done` artifact is archivable iff **no `active` artifact points at it** via an `implements:` inbound edge (the only pinning edge — `superseded_by:` is retired in 3.0, and `supersedes:` is traceability-only, NOT a pinning edge). Read the deterministic set from `flightdeck_index <deck> --archivable` (it scans active artifacts' relation edges and emits the no-inbound-edge `done` artifacts — **and** any `obsolete` knowledge artifacts still in the active area). The judgment is the **edge graph** (for workflow) or **status** (for knowledge), never an AI reading of prose references. (`scrapped` artifacts are never archived — they stay in `specs/`; only `done` workflow items and `obsolete` knowledge items land.)

   **Drain, don't accumulate.** Every landing rescans **all** `done`-in-place artifacts **and `obsolete` knowledge artifacts** across the deck — **not just this session's freshly-produced ones**. `done` workflow items whose inbound edge has since cleared are swept in; `obsolete` knowledge items are swept in unconditionally (no blocking edges apply). The active area drains automatically; neither `done`-but-unlanded nor `obsolete`-not-yet-drained lingers as residue.

   **Drain destination for `obsolete` knowledge:** mirror the source structure — `incidents/foo.md → archive/incidents/foo.md`, `docs/foo.md → archive/docs/foo.md`, etc. Specifically, `archive/incidents/` is the required destination for retired incidents so `--match-signature` can scan them for regression detection (it now also scans `archive/incidents/`). Freeze the file's status as `obsolete` — the archive entry is the cold record.

1. **Build the remap, before moving anything.** For every artifact in the land set, record `M[<folder>/<file>] = archive/<folder>/<file>` (mirrors source structure, e.g. `specs/foo.md → archive/specs/foo.md`). Taking this snapshot *before* any move is what lets intra-set edges survive: it captures both ends of a mutual reference while they still sit at their old paths.
2. **Move (plain filesystem rename — never `git mv`).** For each entry in `M`, move `<folder>/<file>` → `archive/<folder>/<file>`, creating `archive/<folder>/` if absent. Use a plain `mv` / rename, **not `git mv`**: a plain move is sufficient because the later commit step records the rename in git; `git mv` adds no benefit here and introduces unnecessary coupling to git's working-tree tracking.
3. **Rewrite relation edges against `M`.** Scan `implements:` / `supersedes:` / `related:` frontmatter values in **both** the active tree **and** the just-moved files; rewrite any value equal to a key in `M` to `M[value]`. Because `M` covers the entire set, this fixes all three edge classes a path change can dangle: (a) an *external* active artifact pointing at a landed one, (b) an *intra-set* mutual reference (both ends in `M`), and (c) a landed file's *own outbound* edge to a sibling in the same set. Touch **frontmatter values only** — prose `[text](path)` links are out of scope here (walkaround Audit 7 covers those). List the rewrites in the landing summary.
4. **INDEX.** Remove each landed file's row from its `<folder>/INDEX.md` `<!-- AUTO -->` region. No unaffected folder is touched.

The land record is the moved files in `archive/` (+ `git log` on git-backed decks) — flightdeck keeps **no separate landing log** under any git mode. `archive/<folder>/<file>` *is* the durable history; `preflight` reads files, not a journal.

**There is a single implementation and a single source of truth. `landing` and `status` are merely two invocation paths.** A single-file land is just a land set of one: `M` has one entry, there are no intra-set edges, and edges pointing at still-active artifacts keep their active path (correct).

**Landing failure does not roll back `done`.** If landing fails mid-run, the artifact stays `done` at its current in-place location (done-but-unlanded); the next landing sweep picks it up. Never revert `status: done` on a landing failure — `done` asserts user approval, not a system-check result.

## Land-readiness check

Shared predicate, called by `status` (mid-session) and `preflight` (entry). **landable** = signal 1 OR signal 2 (each queues a full landing at end-of-turn). **signal 3** is separate — it triggers a *soft-landing* (knowledge + state persist only, no commit/archive), not a full landing:

- **signal 1** — this `status` invocation just flipped an artifact to `done`.
- **signal 2** — at session entry, `git status` shows **≥ 5** changed files under `flightdeck/`.
- **signal 3** — at end-of-turn (the AI is about to return control to the user), the session has a **knowledge increment**: a new, not-yet-persisted, write-gated knowledge item — the [§ Write gate](protocol.md#write-gate) bar (changes future behavior / influences decisions / referenced repeatedly), transient byproducts excluded. A **state-only** increment (cockpit `## In Progress` / `## Next` / `Focus`, or plan-task progress, with **no** new knowledge) routes to **checkpoint**, not soft-landing.

Mechanics:
- signal 1 is emitted by `status` in the **same invocation** that performs the flip — the edge *is* the flip action, so no stored state is needed; an idempotent rerun on an already-`done` artifact is a no-op → no repeat, no nag.
- **signal 1 auto-landing is end-of-turn debounced.** A `done` flip does **not** immediately run landing per-item; it marks "owes one landing" and runs landing **once before the AI returns control to the user** (end-of-turn — a *decidable* event, replacing the old unimplementable "natural pause"), aggregating all of this turn's `done`s into the **same** landing. This is why landing rescans the whole `done`-in-place set (Land Routine step 0) rather than only the just-flipped artifact.
- signal 2 is reported by `preflight` at entry as the **last line / a dedicated `## Land-readiness` block** (never mid-output), once per entry.
- Whether to then auto-run landing reuses [Rule resolution order](protocol.md#rule-resolution-order) (default self-invocable + any deck rule).
- **signal 3 fires a *soft-landing*** — full landing's knowledge-classify / changed-INDEX-regen / cockpit-board work, with **no commit, no archive, no promotion**. It is landing's no-`done` natural form + a visible banner. Timing is pinned: persist → emit the soft-landing banner → end the turn (never "reply then persist"). The banner format is in [§ Soft-landing banner](#soft-landing-banner--the-visible-safe-to-close-signal); the three-tier framing is in [§ Checkpoint](#checkpoint--lightweight-board-sync-subpath).
- **soft-landing dedup is stateless — the board itself is the watermark.** A turn that already ran a full landing (a `done` flip's end-of-turn debounce) does **not** also soft-land (one turn, one landing path). Knowledge already on disk reads back `already clean` → no-op. If a checkpoint already ran at a plan-task boundary this turn, only a **knowledge increment produced after that checkpoint** (checkpoint-done → turn-end window — the interval between that checkpoint completing and the AI returning control) re-triggers soft-landing; a checkpoint at turn's end leaves an empty window → silent. **No `last_checkpoint_time` / turn-id is stored** — already-persisted content self-detects as clean.
- **What the Stop hook does and does not do.** On Claude Code a passive `Stop` hook regenerates *only* the mechanical AUTO regions (`## In Progress` + each `INDEX.md`), so those are never stale between landings. It does **not** write `## Next` / `Focus`, classify knowledge, flip `done`, commit, or archive — every judgment + soft-landing step above stays agent-driven. "Board-sync is automatic" therefore means *the AUTO regions*, not the whole checkpoint/soft-landing.
- **Deliberate gap (YAGNI):** a long session that churns without ever flipping a status **and without a knowledge increment** is not nudged at all (caught at next preflight entry). Signal 3 covers the knowledge-increment case at end-of-turn; pure **state-only** churn is the remaining gap. No mid-session watermark — it would need cross-call state.

## See also

[`protocol.md` § Common mistakes](protocol.md#common-mistakes--stop-and-reclassify) consolidates the per-symptom red flags and rationalizations to avoid.
