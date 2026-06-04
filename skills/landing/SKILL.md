---
name: landing
description: Use when explicitly invoking the flightdeck landing ritual — classifies new knowledge from the session, regenerates changed-folder INDEX files, updates cockpit.md, blocks on hanging tasks, runs a lightweight workspace smoke-check, commits locally (push asks). Triggered by `/flightdeck:landing`.
---

# Flightdeck Landing

User-triggered explicit landing ritual. Thin entry-point that runs the [exit-ritual.md](../preflight/exit-ritual.md) decision tree as a one-command slash. Use for:

- Wrapping up a session cleanly before context compression.
- Natural pause point (ship complete / brainstorm done) — closing checks before moving on.
- Re-running mid-session to refresh cockpit (`## 进行中` + `## 下一步`) and clear hanging tasks.

## Run this checklist

The full rules + rationale live in [exit-ritual.md](../preflight/exit-ritual.md). Skeleton:

0. **Read `flightdeck/rules.md`** if present; resolve config per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order). Infer git from deck root `.git` (House Rule `this deck doesn't use git` overrides). When no-git: skip the commit step (step 7), and instead append one line to `landed/HISTORY.md` (`YYYY-MM-DD — <result>; next: <pointer>`, newest first). Commit behavior (default: **local commit auto, push asks**; overrides `commit: ask` = confirm before the local commit / `don't auto-commit; leave changes for me / CI` = never) drives step 7 under git. (Pre-3.0 `commit_mode` / `disabled_gates` are read but ignored — use the `commit:` House-Rule phrases instead.)
0a. **Layout guard (before regenerating anything)** — get the deck's layout verdict: fast path `flightdeck_index.py <deck> --verdict` (script runtime reachable), else manual fallback (read `MIGRATION.md` frontmatter + self-check structural signals). If the verdict is **`structural-behind`** or **`malformed`** → **STOP**, report "deck layout is behind/broken (`<verdict>`) — run `/flightdeck:walkaround` to migrate first, then land." Do **not** regen a behind/broken deck (that is how landing used to crash mid-regen).
1. **Resolve hanging tasks first** — open `## Hanging tasks` items block clean exit. See [exit-ritual.md § Hanging tasks](../preflight/exit-ritual.md#hanging-tasks--block-session-exit). If one is genuinely blocking, list it and pause for the user before running steps 2–7. (There is **no** debrief-disposition gate — `debriefs/` was removed; external-review disposition folds into the reviewed spec's `## 评审纪要` as ordinary spec editing, not an exit-blocking gate.)
2. **Classify new knowledge** — apply heuristics (a)–(h), first-match wins. Folders: `specs/`, `plans/`, `incidents/`, `checklists/`, `charts/`. Each written artifact carries a `status` field in frontmatter (workflow: `idea` / `active` / `done` / `scrapped`). No new knowledge is a valid outcome — don't manufacture a classification just to complete landing. **External review feedback is not a folder** — fold its disposition into the reviewed spec's `## 评审纪要`; raw text stays in project-root `tmp/`. See [exit-ritual.md § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics).
3. **Regenerate INDEX for changed folders** — at session end, regenerate the `<!-- AUTO -->` region of `INDEX.md` only for folders where a file was added, modified, moved, landed, or had its status changed this session. Leave other folders' INDEX untouched. If any folder's counts changed, also refresh the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. `specs/INDEX` groups its AUTO region by status (`待启动（idea）` / `进行中·完成（active·done）`) and skips `scrapped`. **Fast path** (when a script runtime is reachable — `uv`/`python`, inferred): `flightdeck_index.py <deck>` regenerates every folder INDEX, the root INDEX, **and** the cockpit `## 进行中` block (step 4) in one run; the hand fallback is always valid. See [exit-ritual.md § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules).
3a. **Suggest status for affected artifacts** — for each artifact written or touched this session, the AI may suggest the next typical status (workflow recommended flow `idea → active → done`; any state → `scrapped`). Status changes are applied only after the user confirms. **Bump `last_updated`** on each workflow artifact changed substantively this session (not typo-only) before regenerating its INDEX — see [exit-ritual.md § Step 3a](../preflight/exit-ritual.md#decision-tree). An `idea → active` flip **adds the `YYYY-MM-DD-` prefix**; a bare `idea` spec is not given `last_updated`. For `done` artifacts, **decide archiving by judgment** (this is landing's智能 — there is no `auto land` toggle): if the artifact's work-cluster is complete **and no `status: active` artifact cross-references it**, run the shared [Land Routine](../preflight/exit-ritual.md#land-routine) to move it into `landed/`; if an `active` artifact still references it (or its sibling cluster isn't done yet), **keep it in place (done-but-unlanded)** and say why. `scrapped` artifacts: offer the same routine. **Never blindly archive on `done`** (do not inline the move/INDEX/HISTORY steps — call the Land Routine).
4. **Update `cockpit.md`** — only bump `Last updated` on the 4 sanctioned triggers; **regen the `## 进行中` AUTO region** from every `status: active` spec/plan (`<!-- AUTO:inprogress -->` block — fast path `flightdeck_index.py <deck>` regenerates it with the INDEXes); **auto-write `## 下一步`** (the next concrete single action — start an idea from the to-start pool, or advance an active artifact, per [exit-ritual § Cockpit update](../preflight/exit-ritual.md#cockpit-update--what-changes)); adjust `Active focus` / `## Hanging tasks` as needed. Status visibility lives in `## 进行中` + folder INDEX, not hand-written elsewhere. Then run the **Length check** (below) right away, before step 5 — so the trim is reflected before AGENTS.md regen and commit.
5. **Regenerate `AGENTS.md` if the cockpit changed** — if any cockpit field AGENTS.md renders changed this session (`Last updated` / `Active focus` / `## 进行中` / `## 下一步` / `## Hanging tasks`), run `/flightdeck:emit-agents-md` so the cross-tool bridge file stays current. Judge "changed" against the file's state at session start, not an empty baseline. See [emit-agents-md SKILL.md](../emit-agents-md/SKILL.md).
6. **Workspace smoke-check (lightweight, non-blocking)** — scan for files this session added/left in `flightdeck/` that would drift the workspace (use `git status --short` to spot what's new or modified). Report, do not block:
   - **Stray root file**: any `.md` directly under `flightdeck/` that is not an entry file (`cockpit.md` / `INDEX.md` / `rules.md`) → flag "stray root file; classify into a folder or remove".
   - **Orphan / unreachable**: any non-entry `.md` not reachable from an entry file → flag "orphan; link from an entry or remove". Skip `landed/`.
   - **Missing frontmatter `status`**: a new flat file in any knowledge folder lacking a `status` field → flag.
   - **Known folders**: `specs/`, `plans/`, `incidents/`, `checklists/`, `charts/`, and `landed/`. Files placed outside these known folders or directly under `flightdeck/` root (other than `cockpit.md` / `INDEX.md` / `rules.md`) are stray. (A not-yet-migrated deck may still carry `sketches/` / `debriefs/` — preflight offers the migration; landing does not flag them as stray, leaving the structural move to migration.)
   Surface any hit **before** the commit prompt so junk isn't committed; the user decides whether to fix now or proceed.
7. **Commit (local) + push (ask).** Default: generate the commit message and **commit locally without asking** (local commits are reversible — reset/amend; this is the safe default). **Never push without asking** — if pushing is appropriate, ask first (push is outward and not easily reversed). Overrides: `commit: ask` → ask "Commit now? (Y/n)" before the local commit; `don't auto-commit; leave changes for me / CI` → don't commit, leave the changes for the user / CI. (No-git already skipped this step at step 0.) Use `checklists/commits.md` style if it exists; otherwise terse imperative subject + reasoning in body.

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
