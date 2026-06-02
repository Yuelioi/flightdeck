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
└─ yes → for each piece of new knowledge:

         Apply classification heuristics in order, first match wins:

         (a) Bug + root cause → incidents/
             (use incident-report template; check if existing topic — append [Case N])
             Set status: active in frontmatter.

         (b) "Every time we do X, follow these steps" → checklists/
             (promote only on the second occurrence, not the first)
             Set status: active in frontmatter.

         (c) Design decision worth referencing later → specs/
             Set status: pending in frontmatter.
             (if substantial, brainstorm with user first)

         (d) Multi-step task to execute later → plans/
             Set status: pending in frontmatter.
             Optionally add implements: specs/<x>.md if it executes a spec.

         (e) External feedback / review received → debriefs/
             (must include disposition section before landing)
             Set status: active in frontmatter.

         (f) Imported external material (RFCs, articles, competitor code) → charts/
             Set status: active in frontmatter.

         (g) Long-term idea worth remembering → sketches/
             Set status: active in frontmatter.
             Mark "Revisit when" condition if you can.

         (h) One-off log analysis, debug output, conversation byproduct
             → DO NOT WRITE (gating)

         (i) Spans multiple folders, no clear primary
             → brainstorm with user

Step 3: Regenerate INDEX for changed folders
        At session end, regenerate the <!-- AUTO --> region of INDEX.md
        only for folders where a file was added, modified, moved, landed,
        or had its status changed this session. Other folders' INDEX untouched.

        If any folder's counts changed, also refresh the root flightdeck/INDEX.md
        <!-- AUTO --> region.

        Walkaround does the full INDEX↔frontmatter consistency check across all folders.

Step 3a: Suggest status for affected artifacts
         For each artifact written or touched this session, the AI MAY suggest
         the next typical status per the recommended flow:
           pending → active → awaiting-review → done
           active ↔ blocked
           any active state → scrapped

         Status changes are applied ONLY after the user confirms. The user may
         change status to any legal value at any time — the AI does not block.
         (Status is a label — no table, no verbs. The AI suggests; the user decides.)

         For done or scrapped artifacts, offer to land them via the
         single shared Land Routine (see "## Land Routine" below) —
         do not inline the move/INDEX/HISTORY steps here.

Step 4: Update cockpit.md
        - Bump Last updated ONLY on real progress (new artifact written,
          artifact landed, blocker resolved, Active focus shifted, or
          Next session content changes — NOT for grep/read/explore-only sessions)
        - Update Active focus if main thread shifted (otherwise leave)
        - Update Next session: 1–5 concrete items (always confirm first item is still right)
        - Update Hanging tasks: add new blocking items, clear resolved ones
        - Cockpit is focus only — artifact status lives in the folder `INDEX.md` files

Step 5: Commit
        - Use checklists/commits.md if it exists
        - Otherwise: terse imperative subject + reasoning in body
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
HISTORY.md:       when git: false, append one line per landing (YYYY-MM-DD — result; next: pointer)
```

**`Last updated` is not a session-activity log.** False triggers that must NOT bump it: pure exploration / grep / reading code; typo fixes; internal refactor with no user-perceivable surface; a commit that doesn't complete a cockpit task; running already-passing tests.

**Cockpit is focus, not status.** Status visibility lives in the folder INDEX files, not cockpit. To see what is active, read the relevant `specs/INDEX.md`, `plans/INDEX.md`, etc.

**When to update mid-session:** after any commit that changes user-perceivable state, refresh `Next session` before starting the next task — don't wait for landing.

**Length check before exit:** if `cockpit.md` > 80 lines, trim immediately (drop finished items; move design detail to a `specs/` entry or a sketch). History is `git log` / `landed/HISTORY.md`, never cockpit.

## Land Routine

The single source of truth for landing an artifact. Both `landing` (Step 3a above) and the `status` skill (`skills/status/SKILL.md`) MUST call this — do not reimplement it anywhere.

Given a `done` (or `scrapped`) artifact at `<folder>/<file>`:

1. Move it to `landed/<folder>/<file>`, mirroring source structure (e.g. `specs/foo.md → landed/specs/foo.md`). Create `landed/<folder>/` if absent.
2. Remove its row from `<folder>/INDEX.md`'s `<!-- AUTO -->` region, then recompute that folder's count line in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. No other folder is touched.
3. When `rules.md` sets `git: false`, append one line to `landed/HISTORY.md` (`YYYY-MM-DD — <what landed>; next: <pointer>`, newest first).

**There is a single implementation and a single source of truth. `landing` and `status` are merely two invocation paths.**

## See also

[`SKILL.md` § Common mistakes](SKILL.md#common-mistakes--stop-and-reclassify) consolidates the per-symptom red flags and rationalizations to avoid.
