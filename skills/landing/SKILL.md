---
name: landing
description: Use when explicitly invoking the flightdeck landing ritual — classifies new knowledge from the session, regenerates changed-folder INDEX files, updates cockpit.md, blocks on hanging tasks, runs a lightweight workspace smoke-check, commits locally (push asks). Triggered by `/flightdeck:landing`.
---

# Flightdeck Landing

The one-command exit ritual. This file is the **checklist face**; the canonical rules + rationale live in [exit-ritual.md](../preflight/exit-ritual.md) — each step links its section, don't re-derive here. Use for: session wrap before context compression · a natural pause point · a mid-session board refresh.

## Modes — full · soft-landing · checkpoint

The AI picks the mode by trigger (`checkpoint ⊂ soft-landing ⊂ full` — same machinery, no fork):

| | **full** (default) | **soft-landing** | **checkpoint** |
|---|---|---|---|
| Trigger | session wrap · `/flightdeck:landing` · end-of-turn `done`-flip | end-of-turn with a **knowledge increment** (signal 3) | plan-task boundary · end-of-turn state-only |
| Runs | Steps 0–11 | Steps 2–3 + 5 + 8, then the soft-landing banner | Step 8's board-sync only |
| Graduate / sweep / archive / smoke / commit | all | **none** (durability deferred to full landing) | none |

Canonical definitions, signal-3 trigger, stateless dedup: [exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check) + [§ Checkpoint 三档 table](../preflight/exit-ritual.md#checkpoint--lightweight-board-sync-subpath). **幂等**: re-running a full landing after a soft-landing only fills the diff (commit + archive + gates) — already-persisted steps self-detect `already clean`. When in doubt, a full landing is always safe.

> The board AUTO regions landing regenerates (`## In Progress` + each `INDEX.md`) are the *same* regions the passive **turn-end hook** welds (one implementation: `flightdeck_index.py <deck>`; Claude/Codex `Stop`, Cursor `stop`, Gemini `AfterAgent`). The hook keeps them fresh between landings; landing still owns graduate, archive, promotion, and commit.

## Run this checklist

0. **Config + git.** Read `flightdeck/rules.md`; resolve everything per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order) (git inference incl. the gitignored-deck = no-git rule, commit defaults, House-Rule overrides). No-git → skip Step 11 and use a plain `mv` for land moves; the moved files in `archive/` are the record — no separate landing log.
1. **Hanging tasks.** Open `## Hanging Tasks` items block clean exit — resolve, or list and pause for the user. [exit-ritual § Hanging tasks](../preflight/exit-ritual.md#hanging-tasks--block-session-exit)
2. **Classify new knowledge** — heuristics (a)–(h), first-match wins; **no new knowledge is a valid outcome**; capture abandoned paths, not just shipped fixes; external review feedback folds into the reviewed spec's `## Review notes` (raw text stays in project-root `tmp/`); a **persistent behavior request** ("from now on…" / 以后每次) → append a free-prose rule to `rules.md` `### Rules` (source + date). [exit-ritual § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics)
3. **Regenerate INDEX for changed folders only.** Fast path: `flightdeck_index.py <deck>` regenerates every folder INDEX **and** the cockpit `## In Progress` block in one run; hand fallback per [exit-ritual § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules).
4. **Graduate finish.** Each `graduate: true` spec that is `done` and still in `specs/`: rewrite as a current-truth `docs/` entry (must carry `when_to_read` / `applies_to` / `when_to_update`), move it, update both INDEXes — **no archive twin**; idempotency key = source still in `specs/`. [exit-ritual § Step 3b](../preflight/exit-ritual.md#decision-tree)
5. **Stale detection + 待验证 surfacing (退场单仪式 — landing/soft-landing only).** `--changed-since-anchor` paths ∩ each knowledge artifact's `applies_to` **path entries** (entries containing `/`) → auto-flip `stale` (idempotent, no pre-ask). Surface verify debt from `--verify-pending` (source of truth = the `verify` fields on disk, never a hand-written cockpit line): `⚠未验证: <file> — <怎么验>` (verify) vs `⚠待复核: <file>` (stale). The `⚠待复核` (stale) items surface into cockpit `## Pending Review` (their awaiting-review home); `⚠未验证` (verify) stays the objective scan, separate. [exit-ritual § Step 3c](../preflight/exit-ritual.md#decision-tree)
6. **Recurrence sweep + promotion** — run [§ Recurrence sweep wiring](#recurrence-sweep-wiring) below for each bug/lesson this session; promotion **auto-fires** when the gate's criteria hold (reversible) and **surfaces in cockpit `## Pending Review`** for veto — no pre-confirm ([protocol § Act-report-close loop](../preflight/protocol.md#act-report-close-loop)).
7. **Status + land.** Apply the next typical status to touched artifacts **by judgment** (reversible — reported in the banner, user can undo); `--advance-candidates` **auto-flips** each all-plans-done spec to `done` (it joins this same landing's archivable set; archival is **idempotent** — no double-archive); bump `last_updated` on substantively changed artifacts. Then land the **deterministic `--archivable` set** via the shared [Land Routine](../preflight/exit-ritual.md#land-routine) — the judgment is the `implements:` edge graph, never AI prose-reading; `done + verify` archives normally (the marker rides into `archive/` and keeps surfacing until verified); every landing rescans **all** done-in-place artifacts so the active area drains. A mid-turn `done` flip debounces into **one** landing at end-of-turn ([exit-ritual § Land-readiness](../preflight/exit-ritual.md#land-readiness-check); a deck `### Rules` nudge-on-done entry downgrades to nudge-only).
8. **Cockpit board-sync.** Bump `Updated` only on the 4 sanctioned triggers; regen the `## In Progress` AUTO region; auto-write `## Next`; refresh `## Key Context` / `## Pending Review` / `## Hanging Tasks` as needed, **applying the accumulator-drain discipline** ([templates § cockpit Rules](../preflight/templates.md#cockpitmd)): **drain** `Key Context` entries whose referent died this session and **graduate** durable entries to their home-by-kind (`rules.md` / `docs/` / the agent instruction file), shrinking still-live ones to one-line pointers; **drain** signed-off `Pending Review` items and surface new ones (AI work-products awaiting sign-off + stale `待复核` notes), and **prompt** each item aged past one landing (sign off / keep / drop). Then the **length check** (gated): cockpit > 80 lines **or** any field over its density cap or in role-creep (`Focus` ≤ one line / ~100 chars + a link · `Updated` is a stamp with no changelog · `## Next` holds no progress checklist · `Key Context` / `Pending Review` entries one-line literals) → propose a gated trim (route off-home content back to git / spec body / plan `## Progress`; confirm before deleting) — see [exit-ritual § Length check](../preflight/exit-ritual.md#cockpit-update--what-changes). Also a **non-blocking nudge** if `## In Progress` shows > ~5 active threads (focus-loss signal; remind only). [exit-ritual § Cockpit update](../preflight/exit-ritual.md#cockpit-update--what-changes)
9. **Regenerate `AGENTS.md`** if any cockpit field it renders changed this session (judge against session start) — run [`/flightdeck:emit-agents-md`](../emit-agents-md/SKILL.md).
10. **Workspace smoke-check (non-blocking).** Via `git status --short`: stray root `.md` (root entries are `cockpit.md` / `rules.md` only), files outside the known folders, orphans (skip `archive/`), missing `status` in knowledge folders. Surface **before** the commit prompt; the user decides.
11. **Commit (local auto) + push (ask).** Local commit without asking (reversible); **never push without asking**. A deck `### Rules` entry may ask-before-commit or disable auto-commit. Style: `checklists/commits.md` if present. **REQUIRED trailer on every landing/soft-land commit:** `Flightdeck-Sync: <git-ref>` — the anchor `--changed-since-anchor` keys on; without it the next landing falls back to a full worktree diff.

## Recurrence sweep wiring

Step 6's sweep is a **two-layer** match with a gated regression branch and two rails. Base decision tree: [exit-ritual § Step 5a](../preflight/exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up); this section wires the signature layers on top:

1. **Deterministic layer first.** `flightdeck_index.py <deck> --match-signature "<symptom>" [--sig-error-type <TYPE>]`. Hit on an **`active`** entry → append `## [Case N]` + bump `recurrences` (auto; promotion itself auto-fires + surfaces in Pending Review). No fingerprint hit → **AI fuzzy layer** (`applies_to` overlap / same root cause): confirmed same / confirmed new / **uncertain → ask the user**. No `## Signature` block → skip straight to the fuzzy layer.
2. **Gated regression (an `obsolete` hit).** `--match-signature` also scans `archive/incidents/` (retired entries stay matchable — regression detection depends on it). A hit there means "we thought this was root-fixed": **confirm a real regression first** (never silently re-append). On confirmation, **revive**: move back to `incidents/`, flip `active`, clear `resolved_by`, add a Case noting "回归，原根治失效", update both INDEXes; `recurrences` keeps accumulating (lifetime count, never reset). Decline → leave archived; treat as a new incident if warranted.
3. **Idempotency.** An incident already `+1`'d at create-time is **not** re-counted by this sweep — dedup by Case round / session identity.
4. **Retire (auto when resolved, reversible).** `resolved_by` filled + the fix confirmed (e.g. the guard test exists) → auto-flip `obsolete` (drains to `archive/`) and surface in Pending Review; reversible via undo. Ambiguous (filled but fix unconfirmed) → leave `active`, note in Pending Review. ([protocol § Retirement semantics](../preflight/protocol.md#retirement-semantics-resolved_by--status-obsolete))

Then evaluate the 3-criterion promotion gate per [exit-ritual § Step 5a](../preflight/exit-ritual.md#step-5a--recurrence-sweep--promotion-gate-wrap-up) for each incident touched this session.

## Output format

**Prose first** — report what landed (one line each; omit empties):

```
Hanging tasks: none / [resolved X / blocking on Y]
New knowledge: specs/ +1 <file> · incidents/ +0 · (etc.)
Graduate: [specs/<x>.md → docs/<x>.md / none]
Stale detected: [docs/<x>.md (applies_to path hit) / none]
Verify pending: [N / none]  (--verify-pending)
INDEX regenerated: [folders / none]
Status changes: [list / none]
Landed: [files / none] (incl. obsolete knowledge drained to archive/)
Cockpit: Updated [y/n, reason] · In Progress [regen N] · Next [refreshed] · Key Context [drained N/shrank M] · Pending Review [added N (sign-off + stale 待复核) / drained M] · Hanging Tasks [unchanged]
Workspace smoke-check: clean / [stray/orphan/missing-status]  (walkaround for full audit)
```

**Then the standardized banner, last** (per [protocol § Act-report-close loop](../preflight/protocol.md#act-report-close-loop)):

```
─── 🛬 landing ───
[Stage]   <lifecycle stage>
[Saved]   committed locally <SHA> (Flightdeck-Sync: <ref>); landed <N> file(s).   (push: asked first / n/a; skipped under no-git or a commit deck rule)
[Pending] ⚠ <N> item(s) await verification → cockpit Pending Review.   (omit when empty)
You can close / switch the conversation anytime — next preflight resumes from the board.
```

## Red flags

STOP and re-read [exit-ritual § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics) if you catch yourself:

- Brainstorming where every knowledge item belongs (heuristics catch 90%)
- Saving session logs / debug dumps / transient scratch into `flightdeck/` (scratch → project-root `tmp/`) — DO NOT WRITE
- Bumping `Updated` after a typo fix or pure exploration
- Adding cockpit sections that duplicate what the folder INDEX files already track
