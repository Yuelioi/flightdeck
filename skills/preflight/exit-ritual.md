# Exit ritual

The protocol for closing an AI coding session cleanly so the next preflight can pick up without context loss.

## Core principle

**90% of session-end decisions are obvious.** Classify directly. Only **true ambiguity** triggers brainstorming. Default-brainstorm is high-friction → skipped → knowledge lost.

## Decision tree

```
Session is wrapping up
↓
Step 1: Are there pending hanging tasks?
        (open items in cockpit ## Hanging tasks)
├─ yes → resolve them first, then continue
└─ no  → proceed to step 2

Step 2: Did this session produce new knowledge / discover a bug / agree on a decision?
├─ no  → only update cockpit.md if Active focus shifted, then proceed to Step 4
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
          reviewed spec's ## 评审纪要; raw text stays in project-root tmp/. See § Classification heuristics.)

Step 3: Regenerate INDEX for changed folders — full rules in "## INDEX regeneration —
        scope rules" below. Gist: regenerate the <!-- AUTO --> region only for folders
        with activity this session; refresh root INDEX if counts changed; walkaround
        owns the full INDEX↔frontmatter check.

Step 3a: Suggest status for affected artifacts
         For each artifact written or touched this session, the AI MAY suggest the next
         typical status per the recommended flow ([protocol § Status ⟂ location](protocol.md#status--location-two-orthogonal-axes)).

         Status changes are applied ONLY after the user confirms. The user may
         change status to any legal value at any time — the AI does not block.
         (Status is a label — no table, no verbs. The AI suggests; the user decides.)

         Bump last_updated: for each spec/plan changed substantively this
         session — body OR frontmatter, not a typo/wording-only edit — set its
         `last_updated:` to today before regenerating that folder's INDEX. A
         confirmed status flip already counts as substantive. **Idea-stage
         specs** (`status: idea`): bump only if the file already carries
         `last_updated` — don't *add* it to a bare idea (its `status` +
         `summary` suffice). This is the landing
         anchor for the recommended-but-not-required workflow `last_updated`;
         knowledge artifacts already carry their own required `last_updated`.

         For done or scrapped artifacts, offer to land them via the
         single shared Land Routine (see "## Land Routine" below) —
         do not inline the move/INDEX/HISTORY steps here.

Step 4: Update cockpit.md — full rules in "## Cockpit update — what changes"
        below. Gist: bump Last updated only on the 4 sanctioned triggers;
        regen the ## 进行中 AUTO region from status:active; auto-write ## 下一步;
        Active focus / Hanging tasks as needed. Then run the Length check (§ below).

Step 5: Commit (local) + push (ask) — default: commit locally without asking
        (local commits are reversible); NEVER push without asking (push is outward).
        - default        → generate the message + `git commit` locally, no prompt
        - `commit: ask`  → ask "Commit now? (Y/n)" before the local commit
        - `don't auto-commit…` → do NOT commit; leave the changes for you / CI
        - no-git overrides all → no commit (landing already logged archive/HISTORY.md)
        - push → only when appropriate AND after asking; never automatic
        - Message: use checklists/commits.md if it exists; else terse imperative subject + reasoning in body
```

### Step 5a — Recurrence sweep + promotion gate (wrap-up)

**Recurrence sweep first.** For each bug / lesson this session produced, compare it against existing `incidents/` (`applies_to` overlap / same root cause):
- **Clear same-incident match** → auto-append `## [Case N]` (with today's date) **and** bump that incident's `recurrences` frontmatter counter. No per-increment confirm — counting is AI-facing bookkeeping, and the consequential step (promotion) stays gated below.
- **Ambiguous match** → ask the user before recording (the false-positive guard lives here).

Then, **for each incident touched** (newly written, or recurrence-bumped) this session, evaluate the 3-criterion promotion gate:

1. `recurrences ≥ 3`?
2. Recurred across ≥ 2 distinct sessions (distinct `[Case N]` dates)?
3. Remediation pattern stable across cases?

If ALL three hold: prompt the user "Promote `incidents/<topic>.md` to `checklists/<topic>.md`?". On user confirmation, move the file. On user defer or reject, leave alone — the gate will fire again next time. **No automatic promotion** — the gate guards against false positives; the user always decides.

If any criterion fails: skip silently. Don't promote-prompt for marginal cases.

## Classification heuristics

These are first-match-wins rules — apply in order. The first one that matches the new piece of knowledge wins; do not over-think.

### (a) Bug + root cause → `incidents/`

**Trigger phrase**: "I assumed X but actually Y" / "this kept failing because"

Always goes to `incidents/`. Check existing topics first — if related, append `## [Case N]` to existing file. Do not start a new file for the same recurrence.

Set `status: active` in frontmatter.

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

### External review feedback → reviewed spec's `## 评审纪要` (no folder)

**Trigger phrase**: user pastes review text from another AI / colleague

There is **no `debriefs/` folder**. The raw feedback is a transient input — keep it in project-root `tmp/` (gitignored, the user's own habit) and read it. Its lasting value is the **disposition** (adopt / reject / defer), which folds into the **reviewed spec's** own `## 评审纪要` section. Raw text is discarded once dispositioned. See [folder-semantics § External review feedback](folder-semantics.md#external-review-feedback-no-folder).

### (h) Ambiguous → brainstorm

**Trigger phrase**: "this is sort of an incident but also a checklist"

If genuinely ambiguous, brainstorm with the user. Use the AI-asks-user template below.

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

## Hanging tasks — block session exit

A session **cannot be closed cleanly** while an open `## Hanging tasks` item remains. Either resolve it now, or record it explicitly in `cockpit.md` "Hanging tasks" (`- [ ] <blocking item>`) so the next preflight sees it on entry and resolves.

`Hanging tasks` in cockpit is a **hand-maintained** list — the AI does not auto-derive it from INDEX. Add and clear entries explicitly.

(There is **no debrief-disposition gate** — `debriefs/` was removed. External review feedback is transient (project-root `tmp/`); its disposition folds into the reviewed spec's `## 评审纪要` as part of normal spec editing, not as an exit-blocking gate.)

## INDEX regeneration — scope rules

Regenerate the `<!-- AUTO -->` region of a folder's `INDEX.md` **only when that folder had activity this session**:

- Activity = file added, modified, moved, landed, or status changed
- Non-activity = the folder was only read (grep, preflight routing, etc.) — leave its INDEX alone

After regenerating any folder INDEX, check whether that folder's file count or status breakdown changed relative to what the root `flightdeck/INDEX.md` currently shows. If yes, regenerate the root INDEX's `<!-- AUTO -->` region too.

The hand area outside `<!-- AUTO -->` is never touched by the AI — grouping notes, cross-references, and other hand-written content are preserved.

Walkaround is responsible for the **full-consistency check** — it regenerates all indexes and validates every frontmatter. Exit ritual only touches changed folders.

### Row format — how each AUTO row is built (single source of truth)

Every `<!-- AUTO -->` row is generated **from the file's frontmatter only — never its body** (a further token saving, complementing read-INDEX-first). `status`, `landing`, and `walkaround` all build rows this way; do not reimplement it elsewhere.

- **Workflow folders** (`specs/` `plans/`): `- [<file>](<file>) — <status> — <summary>`, where `<summary>` is the file's `summary` frontmatter copied **verbatim**. If the file has no `summary` (it is recommended, not required), omit the trailing ` — <summary>` segment entirely. `implements` / `supersedes` / `related` / `note` are never shown in the INDEX (reverse links are grep-derived). `specs/INDEX` groups its AUTO region by status (idea / active·done) and skips `scrapped` — see [folder-semantics § specs/](folder-semantics.md#specs--designs).
- **Knowledge folders** (`incidents/` `checklists/` `docs/` `references/`): `- [<file>](<file>) — <status> — when_to_read: <…> — applies_to: <…>`. (`references/` rows show project/file count, not per-file status; `docs/` rows read `<status> — when_to_read: <…> — applies_to: <…>` like the other authored knowledge folders.)
- **`|` escaping (fallback):** the `summary` constraint already forbids `|` `[` `]` and newlines, but defensively escape any literal `|` pulled from frontmatter as `\|` so a stray pipe can never corrupt the generated line.

### Script fast path (optional accelerator)

INDEX regeneration and the INDEX↔folder consistency check are fully mechanical — they read frontmatter and emit the rows above. flightdeck bundles `scripts/flightdeck_index.py` (pure Python, stdlib-only) that implements **exactly the Row format rule above**: `flightdeck_index.py <deck>` regenerates every folder + root `<!-- AUTO -->` block from frontmatter; `flightdeck_index.py <deck> --check` reports drift and exits non-zero (used by walkaround). `status`, `landing`, and `walkaround` MAY use it as a fast path.

A second script, `scripts/flightdeck_lint.py` (pure stdlib), covers the **mechanical subset of the walkaround audit** — status legality (Audit 1), orphan plans (Audit 4), INDEX↔folder drift (Audit 5, reusing `flightdeck_index`), dangling references (Audit 7), and the unambiguous stray-file cases (Audit 8). `flightdeck_lint.py <deck>` emits a JSON `{"findings": [...]}` list (each with `audit` / `severity` / `path` / `message`) and exits non-zero when any CRITICAL/WARNING is present. The dangling-ref scan already covers repo-root `*.md` by default (the deck's parent); `--repo-root <path>` just points that part of the scan at a different root. `walkaround` MAY use it as a fast path for those audits — the model still reads the JSON and narrates/judges. **It computes facts only; the judgment-bearing audits (knowledge classification, migration decisions, AGENTS.md semantic drift, full stray-file reachability) stay in the markdown checklist.**

This is a **dual track**, not a dependency:

- **Enabled** whenever a Python runtime (`uv`/`python`) + the bundled script are reachable — script use is **inferred**, not a toggle (see [protocol § Rule resolution order](protocol.md#rule-resolution-order)). No runtime → fall back to the manual markdown path.
- **Fallback is always valid**: regenerate by hand from frontmatter exactly as described above. The markdown path is the source of truth; the script only saves tokens (it runs in a subprocess — its file reads never enter context) and adds determinism. A tool that cannot run it loses nothing but speed — which is what keeps flightdeck tool-agnostic.

Never let the script make judgments (classification, status decisions, routing) — it only generates/checks the deterministic INDEX rows.

## Cockpit update — what changes

```
Last updated:     ONLY in these cases (otherwise leave alone):
                  (a) 下一步 content changes
                  (b) Active focus shifts (main thread moved)
                  (c) A major task / phase completes (user-perceivable progress)
                  (d) An artifact lands or a blocker resolves
Active focus:     update if main thread shifted (otherwise leave) — coarse session main thread
## 进行中:        AUTO — regen from every status:active spec/plan (do NOT hand-write)
## 下一步:        auto-written — the next concrete single action (start an idea / advance an active)
Hanging tasks:    hand-maintained list — add new blocking items, clear resolved ones
HISTORY.md:       when no-git, append one line per landing (YYYY-MM-DD — result; next: pointer)
```

**`## 进行中` is AUTO-derived, not hand-written.** Regenerate its `<!-- AUTO:inprogress -->` region from every `status: active` spec/plan (same mechanism + row format as INDEX; a file's `note:` appends `[note: …]`). The `status` skill regenerates it on a status flip; landing regenerates it here. A hand edit is overwritten on the next regen. This is what makes cockpit a **status projection** of the active set — an artifact is in cockpit iff it is `active`, so orphans are structurally impossible.

**`## 下一步` is auto-written by landing** (and on `idea→active` / a completed milestone). Its content is the next concrete **single** action — either (i) start an idea from the to-start pool, or (ii) advance an active artifact. `preflight` reads it but does not rewrite it (a stale entry is corrected at the next write point).

**`Active focus` vs `## 下一步` — different granularity, no overlap.** `Active focus` = the current session main thread, one coarse line. `## 下一步` = the next concrete executable single step. The user adjusts either by directing the AI, not by hand-editing.

**`Last updated` is not a session-activity log.** False triggers that must NOT bump it: pure exploration / grep / reading code; typo fixes; internal refactor with no user-perceivable surface; a commit that doesn't complete a cockpit task; running already-passing tests.

**When to update mid-session:** after any commit that changes user-perceivable state, refresh `## 下一步` before starting the next task — don't wait for landing.

**Length check before exit:** if `cockpit.md` > 80 lines, trim immediately (drop finished items; move design detail to a `specs/` entry). `## 进行中` is AUTO and usually short; piled-up `active` is itself a focus-loss signal. History is `git log` / `archive/HISTORY.md`, never cockpit.

## Land Routine

The single source of truth for landing artifacts. Both `landing` (Step 3a above) and the `status` skill (`skills/status/SKILL.md`) MUST call this — do not reimplement it anywhere.

Landing operates on a **land set**: the one-or-more `done` / `scrapped` artifacts archived in this operation (a single `status land` is a set of one; a `landing` sweep may land several at once). Process the whole set together — **collect the remap first, then migrate, then rewrite** — so cross-references *inside* the set survive:

0. **Compute the land set deterministically — don't read bodies to decide.** Which `done` artifacts are archivable is a **deterministic fact**: a `done` artifact is archivable iff **no `active` artifact points at it** via an `implements:` / `superseded_by:` inbound edge. Fast path: read the deterministic set from `flightdeck_index.py <deck> --archivable` (it scans active artifacts' relation edges and emits the no-inbound-edge `done` artifacts). Fallback (no Python runtime): compute the same set by hand — scan every `active` artifact's `implements:` / `superseded_by:` values, collect their targets, and any `done`-in-place artifact **not** in that target set is archivable. Either way the judgment is the **edge graph**, never an AI reading of prose references. (`scrapped` artifacts are never archived — they stay in `specs/`; only `done` items land.)

   **Drain, don't accumulate.** Every landing rescans **all** `done`-in-place artifacts across the deck — **not just this session's freshly-produced ones**. Any whose inbound edge has since cleared (its blocking `active` artifact has itself landed or been re-pointed) is swept into the land set in this same pass; the rest stay **done-but-unlanded** until their blocker clears. So the active area drains automatically and `done`-but-unlanded never lingers as residue.

1. **Build the remap, before moving anything.** For every artifact in the land set, record `M[<folder>/<file>] = archive/<folder>/<file>` (mirrors source structure, e.g. `specs/foo.md → archive/specs/foo.md`). Taking this snapshot *before* any move is what lets intra-set edges survive: it captures both ends of a mutual reference while they still sit at their old paths.
2. **Move.** For each entry in `M`, move `<folder>/<file>` → `archive/<folder>/<file>`, creating `archive/<folder>/` if absent.
3. **Rewrite relation edges against `M`.** Scan `implements:` / `supersedes:` / `related:` frontmatter values in **both** the active tree **and** the just-moved files; rewrite any value equal to a key in `M` to `M[value]`. Because `M` covers the entire set, this fixes all three edge classes a path change can dangle: (a) an *external* active artifact pointing at a landed one, (b) an *intra-set* mutual reference (both ends in `M`), and (c) a landed file's *own outbound* edge to a sibling in the same set. Touch **frontmatter values only** — prose `[text](path)` links are out of scope here (walkaround Audit 7 covers those). List the rewrites in the landing summary.
4. **INDEX.** Remove each landed file's row from its `<folder>/INDEX.md` `<!-- AUTO -->` region, then recompute the affected folders' count lines in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. No unaffected folder is touched.
5. When no-git (deck root has no `.git`, or a House Rule says so), append one line per landing to `archive/HISTORY.md` (`YYYY-MM-DD — <what landed>; next: <pointer>`, newest first).

**There is a single implementation and a single source of truth. `landing` and `status` are merely two invocation paths.** A single-file land is just a land set of one: `M` has one entry, there are no intra-set edges, and edges pointing at still-active artifacts keep their active path (correct).

## Land-readiness check

Shared predicate, called by `status` (mid-session) and `preflight` (entry). **landable** = signal 1 OR signal 2:

- **signal 1** — this `status` invocation just flipped an artifact to `done` / `scrapped`.
- **signal 2** — at session entry, `git status` shows **≥ 5** changed files under `flightdeck/` (disabled under no-git).

Mechanics:
- signal 1 is emitted by `status` in the **same invocation** that performs the flip — the edge *is* the flip action, so no stored state is needed; an idempotent rerun on an already-`done` artifact is a no-op → no repeat, no nag.
- **signal 1 auto-landing is end-of-turn debounced.** A `done` flip does **not** immediately run landing per-item; it marks "owes one landing" and runs landing **once before the AI returns control to the user** (end-of-turn — a *decidable* event, replacing the old unimplementable "natural pause"), aggregating all of this turn's `done`s into the **same** landing. This is why landing rescans the whole `done`-in-place set (Land Routine step 0) rather than only the just-flipped artifact.
- signal 2 is reported by `preflight` at entry as the **last line / a dedicated `## Land-readiness` block** (never mid-output), once per entry.
- Whether to then auto-run landing reuses [Rule resolution order](protocol.md#rule-resolution-order) (default self-invocable + House Rules).
- **Compatibility-window consequence (known cost, not a bug).** On a deck that is `structural-behind` — not yet migrated to the 3.0 names, so it still has `landed/` / `charts/` — end-of-turn landing **hits the layout guard** and STOPs with "migrate first" instead of archiving. So during the compatibility window, auto-archival is **effectively paused** on un-migrated decks: `done` items stay in place until the author runs the migration. This is the deliberate guard against mixing old/new structure, not a malfunction — don't read it as "auto-landing broke."
- **Deliberate gap (YAGNI):** a long single session that churns without ever flipping a status is not nudged mid-session (caught at next entry). No mid-session watermark — it would need cross-call state. Future signpost: under no-git, signal 2 could use `archive/HISTORY.md` mtime / line growth.

## See also

[`protocol.md` § Common mistakes](protocol.md#common-mistakes--stop-and-reclassify) consolidates the per-symptom red flags and rationalizations to avoid.
