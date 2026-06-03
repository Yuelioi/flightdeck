# Exit ritual

The protocol for closing an AI coding session cleanly so the next preflight can pick up without context loss.

## Core principle

**90% of session-end decisions are obvious.** Classify directly. Only **true ambiguity** triggers brainstorming. Default-brainstorm is high-friction → skipped → knowledge lost.

## Decision tree

```
Session is wrapping up
↓
Step 1: Are there pending hanging tasks?
        (incomplete debrief disposition)
├─ yes → resolve them first, then continue
└─ no  → proceed to step 2

Step 2: Did this session produce new knowledge / discover a bug / agree on a decision?
├─ no  → only update cockpit.md if Active focus shifted, then proceed to Step 4
└─ yes → for each piece, apply classification heuristics in order, first match wins
         (full triggers + detail in "## Classification heuristics" below):
           (a) bug + root cause → incidents/ (status: active; existing topic → append [Case N])
           (b) repeated procedure, 2nd occurrence → checklists/ (status: active)
           (c) design decision → specs/ (status: pending; brainstorm if substantial)
           (d) multi-step task → plans/ (status: pending; optional implements: specs/<x>.md)
           (e) external feedback → debriefs/ (status: active; disposition required)
           (f) imported external material → charts/ (status: active)
           (g) long-term idea → sketches/ (status: active; mark "Revisit when")
           (h) one-off / log / byproduct → DO NOT WRITE (gate)
           (i) ambiguous, no clear primary → brainstorm with user

Step 3: Regenerate INDEX for changed folders — full rules in "## INDEX regeneration —
        scope rules" below. Gist: regenerate the <!-- AUTO --> region only for folders
        with activity this session; refresh root INDEX if counts changed; walkaround
        owns the full INDEX↔frontmatter check.

Step 3a: Suggest status for affected artifacts
         For each artifact written or touched this session, the AI MAY suggest the next
         typical status per the recommended flow ([protocol § Status](protocol.md#status-label--recommended-flow)).

         Status changes are applied ONLY after the user confirms. The user may
         change status to any legal value at any time — the AI does not block.
         (Status is a label — no table, no verbs. The AI suggests; the user decides.)

         Bump last_updated: for each spec/plan changed substantively this
         session — body OR frontmatter, not a typo/wording-only edit — set its
         `last_updated:` to today before regenerating that folder's INDEX. A
         confirmed status flip already counts as substantive. **Sketches**: bump
         only if the file already carries `last_updated` — don't *add* it to a
         bare sketch (its `status` + `summary` suffice). This is the landing
         anchor for the recommended-but-not-required workflow `last_updated`;
         knowledge artifacts already carry their own required `last_updated`.

         For done or scrapped artifacts, offer to land them via the
         single shared Land Routine (see "## Land Routine" below) —
         do not inline the move/INDEX/HISTORY steps here.

Step 4: Update cockpit.md — full rules in "## Cockpit update — what changes"
        below. Gist: bump Last updated only on the 4 sanctioned triggers;
        always refresh Next session; Active focus / Hanging tasks as needed;
        cockpit is focus, not status. Then run the Length check (§ below).

Step 5: Commit — honor the commit override (House Rules; default `confirm`)
        - manual (`don't auto-commit…`)  → do NOT commit; leave the changes for you / CI
        - confirm (default) → generate the commit, then ask "Commit now? (Y/n)"
        - auto (`commit without asking`)    → commit without prompting
        - no-git overrides all three → no commit (landing already logged landed/HISTORY.md)
        - Message: use checklists/commits.md if it exists; else terse imperative subject + reasoning in body
```

### Step 5a — Check incidents→checklists promotion gate (wrap-up)

For each incident in `incidents/` touched (newly written or updated with `[Case N]` append) this session, evaluate the 3-criterion gate:

1. `[Case N] count ≥ 3`?
2. Recurred across ≥ 2 distinct sessions?
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

Set `status: pending` in frontmatter (typically moves to `active` once implementation begins).

### (d) Multi-step task → `plans/`

**Trigger phrase**: "let me break this into steps" / "the plan is"

Produce a structured plan in `plans/`. Optionally reference the governing design with `implements: specs/<x>.md`. Don't free-write.

Set `status: pending` in frontmatter.

### (e) External feedback → `debriefs/`

**Trigger phrase**: user pastes review text from another AI / colleague

Goes to `debriefs/`. **Must include disposition section before landing** (see [templates.md § debrief](templates.md#debrief-body)).

Set `status: active` in frontmatter.

### (f) Imported external material → `charts/`

**Trigger phrase**: "here's the RFC" / "import this competitor's API design"

Raw external material — competitor code, RFCs, articles, research papers — goes to `charts/`. Authored operational procedures go to `checklists/` instead (keep the split clear).

Set `status: active` in frontmatter.

### (g) Long-term idea → `sketches/`

**Trigger phrase**: "we could maybe one day" / "wouldn't it be cool if"

Goes to `sketches/`. Mark "Revisit when" condition if you can. Sketches only use `status: active` or `status: scrapped`.

### (h) One-off → DO NOT WRITE

**Trigger phrase**: "the log output today was" / "I tried these 5 things and got"

Do not write. Gate strictly. Flightdeck is not a session log.

### (i) Ambiguous → brainstorm

**Trigger phrase**: "this is sort of an incident but also a checklist"

If genuinely ambiguous, brainstorm with the user. Use the AI-asks-user template below.

## AI-asks-user template (ambiguous classification)

When triggering (i), open the conversation with a structured ask:

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

A session **cannot be closed cleanly** while this is unresolved:

### Hanging debrief disposition

If `debriefs/<file>` exists without a complete `Disposition` section, either:
- Complete the disposition now, or
- Add to `cockpit.md` "Hanging tasks": `- [ ] Finish disposition of [debriefs/<file>](debriefs/<file>)`

The hanging task must be reflected in `cockpit.md`. The next preflight will see it on entry and resolve.

`Hanging tasks` in cockpit is a **hand-maintained** list — the AI does not auto-derive it from INDEX. Add and clear entries explicitly.

## INDEX regeneration — scope rules

Regenerate the `<!-- AUTO -->` region of a folder's `INDEX.md` **only when that folder had activity this session**:

- Activity = file added, modified, moved, landed, or status changed
- Non-activity = the folder was only read (grep, preflight routing, etc.) — leave its INDEX alone

After regenerating any folder INDEX, check whether that folder's file count or status breakdown changed relative to what the root `flightdeck/INDEX.md` currently shows. If yes, regenerate the root INDEX's `<!-- AUTO -->` region too.

The hand area outside `<!-- AUTO -->` is never touched by the AI — grouping notes, cross-references, and other hand-written content are preserved.

Walkaround is responsible for the **full-consistency check** — it regenerates all indexes and validates every frontmatter. Exit ritual only touches changed folders.

### Row format — how each AUTO row is built (single source of truth)

Every `<!-- AUTO -->` row is generated **from the file's frontmatter only — never its body** (a further token saving, complementing read-INDEX-first). `status`, `landing`, and `walkaround` all build rows this way; do not reimplement it elsewhere.

- **Workflow folders** (`sketches/` `specs/` `plans/`): `- [<file>](<file>) — <status> — <summary>`, where `<summary>` is the file's `summary` frontmatter copied **verbatim**. If the file has no `summary` (it is recommended, not required), omit the trailing ` — <summary>` segment entirely. `implements` / `supersedes` / `related` are never shown in the INDEX (reverse links are grep-derived).
- **Knowledge folders** (`incidents/` `checklists/` `charts/`): `- [<file>](<file>) — <status> — when_to_read: <…> — applies_to: <…>`. `debriefs/`: reviewed spec + `last_updated`. (`charts/` rows show project/file count, not per-file status.)
- **`|` escaping (fallback):** the `summary` constraint already forbids `|` `[` `]` and newlines, but defensively escape any literal `|` pulled from frontmatter as `\|` so a stray pipe can never corrupt the generated line.

### Script fast path (optional accelerator)

INDEX regeneration and the INDEX↔folder consistency check are fully mechanical — they read frontmatter and emit the rows above. flightdeck bundles `scripts/flightdeck_index.py` (pure Python, stdlib-only) that implements **exactly the Row format rule above**: `flightdeck_index.py <deck>` regenerates every folder + root `<!-- AUTO -->` block from frontmatter; `flightdeck_index.py <deck> --check` reports drift and exits non-zero (used by walkaround). `status`, `landing`, and `walkaround` MAY use it as a fast path.

This is a **dual track**, not a dependency:

- **Enabled** only when the `run scripts` House Rule is set in `rules.md` `### Autonomy overrides` (absent → manual by default — see [protocol § Rule resolution order](protocol.md#rule-resolution-order)) **and** a Python runtime + the bundled script are reachable. `run scripts with <runtime>` pins the interpreter.
- **Fallback is always valid**: regenerate by hand from frontmatter exactly as described above. The markdown path is the source of truth; the script only saves tokens (it runs in a subprocess — its file reads never enter context) and adds determinism. A tool that cannot run it loses nothing but speed — which is what keeps flightdeck tool-agnostic.

Never let the script make judgments (classification, status decisions, routing) — it only generates/checks the deterministic INDEX rows.

## Cockpit update — what changes

```
Last updated:     ONLY in these cases (otherwise leave alone):
                  (a) Next session content changes
                  (b) Active focus shifts (main thread moved)
                  (c) A major task / phase completes (user-perceivable progress)
                  (d) An artifact lands or a blocker resolves
Active focus:     update if main thread shifted (otherwise leave)
Next session:     always update — at minimum confirm the first item is still right
Hanging tasks:    hand-maintained list — add new blocking items, clear resolved ones
HISTORY.md:       when no-git, append one line per landing (YYYY-MM-DD — result; next: pointer)
```

**`Last updated` is not a session-activity log.** False triggers that must NOT bump it: pure exploration / grep / reading code; typo fixes; internal refactor with no user-perceivable surface; a commit that doesn't complete a cockpit task; running already-passing tests.

**Cockpit is focus, not status.** Status visibility lives in the folder INDEX files, not cockpit. To see what is active, read the relevant `specs/INDEX.md`, `plans/INDEX.md`, etc.

**When to update mid-session:** after any commit that changes user-perceivable state, refresh `Next session` before starting the next task — don't wait for landing.

**Length check before exit:** if `cockpit.md` > 80 lines, trim immediately (drop finished items; move design detail to a `specs/` entry or a sketch). History is `git log` / `landed/HISTORY.md`, never cockpit.

## Land Routine

The single source of truth for landing artifacts. Both `landing` (Step 3a above) and the `status` skill (`skills/status/SKILL.md`) MUST call this — do not reimplement it anywhere.

Landing operates on a **land set**: the one-or-more `done` / `scrapped` artifacts archived in this operation (a single `status land` is a set of one; a `landing` sweep may land several at once). Process the whole set together — **collect the remap first, then migrate, then rewrite** — so cross-references *inside* the set survive:

1. **Build the remap, before moving anything.** For every artifact in the land set, record `M[<folder>/<file>] = landed/<folder>/<file>` (mirrors source structure, e.g. `specs/foo.md → landed/specs/foo.md`). Taking this snapshot *before* any move is what lets intra-set edges survive: it captures both ends of a mutual reference while they still sit at their old paths.
2. **Move.** For each entry in `M`, move `<folder>/<file>` → `landed/<folder>/<file>`, creating `landed/<folder>/` if absent.
3. **Rewrite relation edges against `M`.** Scan `implements:` / `supersedes:` / `related:` frontmatter values in **both** the active tree **and** the just-moved files; rewrite any value equal to a key in `M` to `M[value]`. Because `M` covers the entire set, this fixes all three edge classes a path change can dangle: (a) an *external* active artifact pointing at a landed one, (b) an *intra-set* mutual reference (both ends in `M`), and (c) a landed file's *own outbound* edge to a sibling in the same set. Touch **frontmatter values only** — prose `[text](path)` links are out of scope here (walkaround Audit 7 covers those). List the rewrites in the landing summary.
4. **INDEX.** Remove each landed file's row from its `<folder>/INDEX.md` `<!-- AUTO -->` region, then recompute the affected folders' count lines in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. No unaffected folder is touched.
5. When no-git (deck root has no `.git`, or a House Rule says so), append one line per landing to `landed/HISTORY.md` (`YYYY-MM-DD — <what landed>; next: <pointer>`, newest first).

**There is a single implementation and a single source of truth. `landing` and `status` are merely two invocation paths.** A single-file land is just a land set of one: `M` has one entry, there are no intra-set edges, and edges pointing at still-active artifacts keep their active path (correct).

## Land-readiness check

Shared predicate, called by `status` (mid-session) and `preflight` (entry). **landable** = signal 1 OR signal 2:

- **signal 1** — this `status` invocation just flipped an artifact to `done` / `awaiting-review`.
- **signal 2** — at session entry, `git status` shows **≥ 5** changed files under `flightdeck/` (disabled under no-git).

Mechanics:
- signal 1 is emitted by `status` in the **same invocation** that performs the flip — the edge *is* the flip action, so no stored state is needed; an idempotent rerun on an already-`done` artifact is a no-op → no repeat, no nag.
- signal 2 is reported by `preflight` at entry as the **last line / a dedicated `## Land-readiness` block** (never mid-output), once per entry.
- Whether to then auto-run landing reuses [Rule resolution order](protocol.md#rule-resolution-order) (default self-invocable + House Rules).
- **Deliberate gap (YAGNI):** a long single session that churns without ever flipping a status is not nudged mid-session (caught at next entry). No mid-session watermark — it would need cross-call state. Future signpost: under no-git, signal 2 could use `landed/HISTORY.md` mtime / line growth.

## See also

[`protocol.md` § Common mistakes](protocol.md#common-mistakes--stop-and-reclassify) consolidates the per-symptom red flags and rationalizations to avoid.
