---
name: landing
description: Use when explicitly invoking the flightdeck landing ritual — classifies new knowledge from the session, regenerates changed-folder INDEX files, updates cockpit.md, blocks on hanging tasks, runs a lightweight workspace smoke-check, commits locally (push asks). Triggered by `/flightdeck:landing`.
---

# Flightdeck Landing

User-triggered explicit landing ritual. Thin entry-point that runs the [exit-ritual.md](../preflight/exit-ritual.md) decision tree as a one-command slash. Use for:

- Wrapping up a session cleanly before context compression.
- Natural pause point (ship complete / brainstorm done) — closing checks before moving on.
- Re-running mid-session to refresh cockpit (`## 进行中` + `## 下一步`) and clear hanging tasks.

## Modes — full · soft-landing · checkpoint

`landing` runs in one of three modes; the AI picks by the trigger (`checkpoint ⊂ soft-landing ⊂ full`):

| | **full** (default) | **soft-landing** | **checkpoint** |
|---|---|---|---|
| Trigger | session wrap · `/flightdeck:landing` · end-of-turn `done`-flip | **end-of-turn with a knowledge increment** (signal 3) | plan / plan-task boundary · end-of-turn state-only |
| Runs | the whole checklist (Steps 0–7) | Steps 2–4 (classify knowledge · regen changed INDEX · cockpit board) + 「已保存」marker | only Step 4's board-sync |
| Skips | nothing | archive (3a) · promotion gate (3z) · smoke-check (6) · **commit (7)** | everything except Step 4 |
| Commit / archive | local commit (push asks) + archive | **neither** (durability deferred to full landing) | none |

soft-landing is landing's **no-`done` natural form** — Steps 2–4 with no commit/archive, plus the 「已保存」marker; canonical definition + signal 3 trigger + stateless dedup: [exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check) and [§ Checkpoint 三档 table](../preflight/exit-ritual.md#checkpoint--lightweight-board-sync-subpath). **landing 幂等:** re-running a full landing after a soft-landing only fills the diff (commit + archive + promotion gate); the already-persisted Steps 2–4 self-detect `already clean`. A checkpoint and a soft-landing are each a **strict subset of a full landing** — same machinery, no fork. When in doubt about the mode, a full landing is always safe — the lighter modes are cheaper options, not required ones.

## Run this checklist

The full rules + rationale live in [exit-ritual.md](../preflight/exit-ritual.md). The checklist below is **full mode**; in **checkpoint mode** run **only Step 4** (board-sync) and stop — skip every other step. Skeleton:

0. **Read `flightdeck/rules.md`** if present; resolve config per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order). Infer git from deck root `.git` (House Rule `this deck doesn't use git` overrides). When no-git: skip the commit step (step 7), and instead append one line to `archive/HISTORY.md` (`YYYY-MM-DD — <result>; next: <pointer>`, newest first). Commit behavior (default: **local commit auto, push asks**; overrides `commit: ask` = confirm before the local commit / `don't auto-commit; leave changes for me / CI` = never) drives step 7 under git. (Pre-3.0 `commit_mode` / `disabled_gates` are read but ignored — use the `commit:` House-Rule phrases instead.)
0a. **Layout guard (before regenerating anything)** — get the deck's layout verdict: fast path `flightdeck_index.py <deck> --verdict` (script runtime reachable), else manual fallback (read `MIGRATION.md` frontmatter + self-check structural signals). If the verdict is **`structural-behind`** or **`malformed`** → **STOP**, report "deck layout is behind/broken (`<verdict>`) — run `/flightdeck:walkaround` to migrate first, then land." Do **not** regen a behind/broken deck (that is how landing used to crash mid-regen). **Compatibility-window consequence (known cost, not a bug):** on a not-yet-migrated (`structural-behind`, still carrying old `charts/` / `landed/`) deck, an end-of-turn `done` hand-off hits this same guard → it reports "migrate first" **instead of archiving**, so auto-archival is **effectively paused** on un-migrated decks until the author runs the migration — the deliberate guard against mixing old/new structure, not a malfunction. See [exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check).
1. **Resolve hanging tasks first** — open `## Hanging tasks` items block clean exit. See [exit-ritual.md § Hanging tasks](../preflight/exit-ritual.md#hanging-tasks--block-session-exit). If one is genuinely blocking, list it and pause for the user before running steps 2–7. (There is **no** debrief-disposition gate — `debriefs/` was removed; external-review disposition folds into the reviewed spec's `## 评审纪要` as ordinary spec editing, not an exit-blocking gate.)
2. **Classify new knowledge** — apply heuristics (a)–(h), first-match wins. Folders: `specs/`, `plans/`, `incidents/`, `checklists/`, `docs/`, `references/`. Each written artifact carries a `status` field in frontmatter (workflow: `idea` / `active` / `done`). Two distinctions to keep straight: imported external material (competitor code, RFCs, articles) → `references/` (heuristic (e)); self-authored standing technical reference (architecture / rationale / subsystem you wrote to *understand* the system) → `docs/` (heuristic (e2)). `docs/` is what you **read to comprehend** ("how it works"); `checklists/` is what you **execute** ("what steps to run"). No new knowledge is a valid outcome — don't manufacture a classification just to complete landing. **External review feedback is not a folder** — fold its disposition into the reviewed spec's `## 评审纪要`; raw text stays in project-root `tmp/`. See [exit-ritual.md § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics).
3. **Regenerate INDEX for changed folders** — at session end, regenerate the `<!-- AUTO -->` region of `INDEX.md` only for folders where a file was added, modified, moved, landed, or had its status changed this session. Leave other folders' INDEX untouched. If any folder's counts changed, also refresh the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. `specs/INDEX` groups its AUTO region by status (`待启动（idea）` / `进行中·完成（active·done）`). **Fast path** (when a script runtime is reachable — `uv`/`python`, inferred): `flightdeck_index.py <deck>` regenerates every folder INDEX, the root INDEX, **and** the cockpit `## 进行中` block (step 4) in one run; the hand fallback is always valid. See [exit-ritual.md § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules).
3z. **Recurrence sweep + promotion gate** — for each bug / lesson this session produced, run the signature-aware recurrence sweep (see [§ Recurrence sweep wiring](#recurrence-sweep-wiring) below + canonical [exit-ritual § Step 5a](../preflight/exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up)): deterministic `--match-signature` first, AI fuzzy layer on no-match, gated revival on an `obsolete` hit, idempotent against create-time `+1`, and a retire prompt when `resolved_by` is filled but the entry is still `active`.
3a. **Suggest status for affected artifacts** — for each artifact written or touched this session, the AI may suggest the next typical status (workflow recommended flow `idea → active → done`; rejection deletes the file). Status changes are applied only after the user confirms. **Plan-done → spec advance (co-advance 对账):** run `flightdeck_index.py <deck> --advance-candidates` — active specs whose implementing plans are **all** `done`. For each, **confirm-gated** offer to advance the spec to `done` (never auto: the user judges whether the design is truly realized; status's "never flip a second artifact" rule is exactly why this offer lives in landing, not status). A confirmed spec joins **this same landing**'s `--archivable` set, so the finished spec+plan cluster lands together. This is orthogonal to the recurrence sweep (incident signatures) and the archivable pass (done-archival) — it walks only the `implements:` edge, so no double-offer. **Bump `last_updated`** on each workflow artifact changed substantively this session (not typo-only) before regenerating its INDEX — see [exit-ritual.md § Step 3a](../preflight/exit-ritual.md#decision-tree). An `idea → active` flip **adds the `YYYY-MM-DD-` prefix**; a bare `idea` spec is not given `last_updated`. For `done` artifacts, **decide archiving deterministically — don't read bodies to judge** (this is landing's智能 — there is no `auto land` toggle): which `done` items are archivable is the **deterministic `--archivable` set** — fast path `flightdeck_index.py <deck> --archivable` (the `done` artifacts with **no `active` inbound edge** via `implements:` / `superseded_by:`; hand fallback computes the same edge graph). Run the shared [Land Routine](../preflight/exit-ritual.md#land-routine) to move every artifact in that set into `archive/`; a `done` item still pointed at by an `active` artifact stays **done-but-unlanded** until its blocker clears. **Each landing rescans ALL `done`-in-place artifacts across the deck** (not just this session's freshly-produced ones) so the active area drains automatically — any whose inbound edge has since cleared is swept in this same pass. **Never blindly archive on `done`, and never decide by AI-reading cross-references** (do not inline the move/INDEX/HISTORY steps — call the Land Routine; the judgment is the edge graph). See [exit-ritual § Land Routine](../preflight/exit-ritual.md#land-routine). **Default relay = end-of-turn debounce:** a `done` flip does not run landing per-item — it marks "owes one landing" and runs landing **once before the AI returns control to the user**, aggregating all of this turn's `done`s into the **same** landing (this is why the rescan above sweeps the whole `done`-in-place set, not just the just-flipped artifact). House Rule `landing: nudge on done, don't auto-run` downgrades this to **prompt-only** (nudge, don't auto-run). See [exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check).
4. **Update `cockpit.md`** — only bump `Last updated` on the 4 sanctioned triggers; **regen the `## 进行中` AUTO region** from every `status: active` spec/plan (`<!-- AUTO:inprogress -->` block — fast path `flightdeck_index.py <deck>` regenerates it with the INDEXes); **auto-write `## 下一步`** (the next concrete single action — start an idea from the to-start pool, or advance an active artifact, per [exit-ritual § Cockpit update](../preflight/exit-ritual.md#cockpit-update--what-changes)); adjust `Active focus` / `## Hanging tasks` as needed. Status visibility lives in `## 进行中` + folder INDEX, not hand-written elsewhere. Then run the **Length check** (below) right away, before step 5 — so the trim is reflected before AGENTS.md regen and commit.
5. **Regenerate `AGENTS.md` if the cockpit changed** — if any cockpit field AGENTS.md renders changed this session (`Last updated` / `Active focus` / `## 进行中` / `## 下一步` / `## Hanging tasks`), run `/flightdeck:emit-agents-md` so the cross-tool bridge file stays current. Judge "changed" against the file's state at session start, not an empty baseline. See [emit-agents-md SKILL.md](../emit-agents-md/SKILL.md).
6. **Workspace smoke-check (lightweight, non-blocking)** — scan for files this session added/left in `flightdeck/` that would drift the workspace (use `git status --short` to spot what's new or modified). Report, do not block:
   - **Stray root file**: any `.md` directly under `flightdeck/` that is not an entry file (`cockpit.md` / `INDEX.md` / `rules.md`) → flag "stray root file; classify into a folder or remove".
   - **Orphan / unreachable**: any non-entry `.md` not reachable from an entry file → flag "orphan; link from an entry or remove". Skip `archive/`.
   - **Missing frontmatter `status`**: a new flat file in any knowledge folder lacking a `status` field → flag.
   - **Known folders**: `specs/`, `plans/`, `incidents/`, `checklists/`, `docs/`, `references/`, and `archive/`. Files placed outside these known folders or directly under `flightdeck/` root (other than `cockpit.md` / `INDEX.md` / `rules.md`) are stray. A nestable folder's `<area>/` subdirectory (e.g. `references/<project>/`) is **not** stray. (A not-yet-migrated deck may still carry old `charts/` / `landed/` / `sketches/` / `debriefs/` — preflight offers the migration; landing does not flag them as stray, leaving the structural move to migration.)
   Surface any hit **before** the commit prompt so junk isn't committed; the user decides whether to fix now or proceed.
7. **Commit (local) + push (ask).** Default: generate the commit message and **commit locally without asking** (local commits are reversible — reset/amend; this is the safe default). **Never push without asking** — if pushing is appropriate, ask first (push is outward and not easily reversed). Overrides: `commit: ask` → ask "Commit now? (Y/n)" before the local commit; `don't auto-commit; leave changes for me / CI` → don't commit, leave the changes for the user / CI. (No-git already skipped this step at step 0.) Use `checklists/commits.md` style if it exists; otherwise terse imperative subject + reasoning in body.

## Recurrence sweep wiring

Step 3z's sweep is a **two-layer** match, with a gated branch for revived bugs and two safety rails. The base recurrence-sweep + promotion-gate decision tree is [exit-ritual § Step 5a](../preflight/exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up); this section wires in the signature-aware layers on top of it:

1. **Deterministic layer first.** For each bug this session produced, run `flightdeck_index.py <deck> --match-signature "<symptom>" [--sig-error-type <TYPE>]` (the precise fingerprint layer). A hit on an **`active`** entry → **append `## [Case N]` + bump `recurrences` +1** with no per-increment confirm (counting is AI-facing bookkeeping; the consequential step — promotion — stays gated). **No fingerprint hit** → fall to the **AI fuzzy layer** (`applies_to` overlap / same root cause), whose three outcomes are unchanged: confirmed same incident / confirmed new / **uncertain → ask the user** (the false-positive guard). Incidents with no `## Signature` skip the deterministic layer and go straight to the fuzzy layer.

2. **Gated regression (an `obsolete` hit).** When `--match-signature` matches an entry whose `status: obsolete`, **do NOT directly append a Case** — an obsolete entry means "we thought this was root-fixed". First **confirm it is a real regression** (same gate as the fuzzy "uncertain" path — guards against a *new* bug that merely shares a symptom). On confirmation, **revive** the incident: flip `status` back to `active`, **clear `resolved_by`**, add a Case noting **"回归，原根治失效"**, and let `recurrences` **keep accumulating (never reset** — it is the lifetime count; the regression Case note separates the pre-fix and post-fix eras). Decline → leave it obsolete; treat the symptom as a genuinely new incident if warranted.

3. **Idempotency.** An incident that was **already `+1`'d at create-time** (the author ran the hit-path check before writing and appended the Case then) must **NOT be re-counted** by this landing sweep — dedup by Case round / session identity so "create-time +1 then landing +1" can never double-count.

4. **Retire prompt (never auto-flip).** When the sweep sees an entry with `resolved_by` **filled but still `status: active`**, **prompt** "resolved_by is filled but still active — retire (flip `obsolete`)?" — **never auto-flip**. Retirement is a deliberate, gated act (see [protocol § Retirement semantics](../preflight/protocol.md#retirement-semantics-resolved_by--status-obsolete)); the script only surfaces the candidate.

Then run the 3-criterion promotion gate per [exit-ritual § Step 5a](../preflight/exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up) for each incident touched this session.

## Length check (runs right after step 4)

If `flightdeck/cockpit.md` > 80 lines: propose a trim. `## 进行中` is AUTO-derived and usually short — a long cockpit is piled-up `active` (a focus-loss signal) or hand-written cruft in `## 下一步` / `Active focus`. The fix is to move design detail to the relevant `specs/` entry — not to delete content; confirm with the user before removing anything from cockpit.

## Output format

```
Hanging tasks: none / [resolved X / blocking on Y]
New knowledge classified:
  - specs/ +1: <file>
  - incidents/ +0 (no triggers)
  - (etc.)
INDEX regenerated: [folders / none]
Status changes: [list / none]
Landed: [files / none]
Cockpit updated:
  - Last updated: [yes/no, reason]
  - 进行中: [regenerated from N active / unchanged]
  - 下一步: [refreshed / unchanged]
  - Hanging tasks: [cleared X / added Y / unchanged]
History (git:false): [+1 HISTORY.md line / n/a]
Workspace smoke-check: clean / [stray: X | orphan: Y | missing-status: Z]  (run /flightdeck:walkaround for full audit)

Commit: [committed locally (default) / Commit now? (Y/n) (commit: ask) / skipped (don't auto-commit | git:false)]  (push: asked first / n/a)
```

## Red flags

If you find yourself doing any of these, STOP and re-read [exit-ritual.md § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics):

- Brainstorming where every knowledge item belongs (heuristics catch 90%; default-brainstorm is the failure mode)
- Saving session logs / debug dumps to `flightdeck/` — transient byproducts, not knowledge; DO NOT WRITE
- Bumping `Last updated` after a typo fix or pure exploration
- Saving transient scratch into `flightdeck/` instead of project-root `tmp/`
- Adding cockpit sections that duplicate what the folder INDEX files already track (status lives there)
