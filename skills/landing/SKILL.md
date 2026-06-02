---
name: landing
description: Use when explicitly invoking the flightdeck landing ritual — classifies new knowledge from the session, regenerates changed-folder INDEX files, updates cockpit.md, blocks on hanging tasks, runs a lightweight workspace smoke-check, optionally commits. Triggered by `/flightdeck:landing`.
---

# Flightdeck Landing

User-triggered explicit landing ritual. Thin entry-point that runs the [exit-ritual.md](../preflight/exit-ritual.md) decision tree as a one-command slash. Use for:

- Wrapping up a session cleanly before context compression.
- Natural pause point (ship complete / brainstorm done) — closing checks before moving on.
- Re-running mid-session to enforce the "no hanging debrief disposition" discipline.

## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` and look at its `model_invocable` list (absent key or `[]` = empty).

- If **`landing` is in `model_invocable`** → allowed; continue this ritual normally.
- Else (`landing` not listed):
  - If you can tell this run was an **explicit user `/flightdeck:landing`** invocation (e.g. the platform injected a `<command-name>` marker for it) → allowed; continue.
  - Otherwise — you reached this skill by **model self-invocation** (skill tool), **or you cannot tell the call source** → **STOP immediately.** Report: "`landing` is manual-only in this project. To let the model self-invoke it, add `model_invocable: [landing]` to `flightdeck/rules.md`." Run no further step.

This gate defaults to manual-only: with no `model_invocable` key, behavior is identical to the former `disable-model-invocation: true`. (Tool-agnostic — ships to every platform via this body. See the adapter READMEs for per-platform formal/degraded mode.)

## Run this checklist

The full rules + rationale live in [exit-ritual.md](../preflight/exit-ritual.md). Skeleton:

0. **Read `flightdeck/rules.md`** if present. When `git: false`: skip the commit step (step 7), and instead append one line to `landed/HISTORY.md` (`YYYY-MM-DD — <result>; next: <pointer>`, newest first). Honor `disabled_gates` (e.g. skip the debrief-disposition gate if disabled).
1. **Resolve hanging tasks first** — incomplete debrief dispositions block clean exit. See [exit-ritual.md § Hanging tasks](../preflight/exit-ritual.md#hanging-tasks--block-session-exit). If one is genuinely blocking, list it and pause for the user before running steps 2–7.
2. **Classify new knowledge** — apply heuristics (a)–(h), first-match wins. Folders: `specs/`, `plans/`, `incidents/`, `checklists/`, `charts/`, `debriefs/`, `sketches/`. Each written artifact carries a `status` field in frontmatter. No new knowledge is a valid outcome — don't manufacture a classification just to complete landing. See [exit-ritual.md § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics).
3. **Regenerate INDEX for changed folders** — at session end, regenerate the `<!-- AUTO -->` region of `INDEX.md` only for folders where a file was added, modified, moved, landed, or had its status changed this session. Leave other folders' INDEX untouched. If any folder's counts changed, also refresh the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. See [exit-ritual.md § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules).
3a. **Suggest status for affected artifacts** — for each artifact written or touched this session, the AI may suggest the next typical status (`pending → active → awaiting-review → done`; `active ↔ blocked`; any active state → `scrapped`). Status changes are applied only after the user confirms. For `done` or `scrapped` artifacts, offer to land them: move to `landed/` mirroring source structure (e.g. `specs/foo.md → landed/specs/foo.md`).
4. **Update `cockpit.md`** — only bump `Last updated` on the 4 sanctioned triggers. Status visibility lives in folder INDEX files, not cockpit. See [exit-ritual.md § Cockpit update](../preflight/exit-ritual.md#cockpit-update--what-changes). Then run the **Length check** (below) right away, before step 5 — so the trim is reflected before AGENTS.md regen and commit.
5. **Regenerate `AGENTS.md` if the cockpit changed** — if any cockpit field AGENTS.md renders changed this session (`Last updated` / `Active focus` / `Next session` / `Hanging tasks`), run `/flightdeck:emit-agents-md` so the cross-tool bridge file stays current. Judge "changed" against the file's state at session start, not an empty baseline. See [emit-agents-md SKILL.md](../emit-agents-md/SKILL.md).
6. **Workspace smoke-check (lightweight, non-blocking)** — scan for files this session added/left in `flightdeck/` that would drift the workspace (use `git status --short` to spot what's new or modified). Report, do not block:
   - **Stray root file**: any `.md` directly under `flightdeck/` that is not an entry file (`cockpit.md` / `INDEX.md` / `rules.md`) → flag "stray root file; classify into a folder or remove".
   - **Orphan / unreachable**: any non-entry `.md` not reachable from an entry file → flag "orphan; link from an entry or remove". Skip `landed/`.
   - **Missing frontmatter `status`**: a new flat file in any knowledge folder lacking a `status` field → flag.
   - **Known folders (1.2)**: `sketches/`, `specs/`, `plans/`, `incidents/`, `checklists/`, `charts/`, `debriefs/`, and `landed/`. Files placed outside these known folders or directly under `flightdeck/` root (other than `cockpit.md` / `INDEX.md` / `rules.md`) are stray.
   Surface any hit **before** the commit prompt so junk isn't committed; the user decides whether to fix now or proceed.
7. **Commit (if user wants)** — ask before; use `checklists/commits.md` style if it exists; otherwise terse imperative subject + reasoning in body.

## Length check (runs right after step 4)

If `flightdeck/cockpit.md` > 80 lines: propose a trim. The fix is to separate finished items (drop them) and move design detail to the relevant `specs/` entry or a sketch — not to delete content; confirm with the user before removing anything from cockpit.

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
  - Next session: [refreshed / unchanged]
  - Hanging tasks: [cleared X / added Y / unchanged]
History (git:false): [+1 HISTORY.md line / n/a]
Workspace smoke-check: clean / [stray: X | orphan: Y | missing-status: Z]  (run /flightdeck:walkaround for full audit)

Commit now? (Y/n)
```

## Red flags

If you find yourself doing any of these, STOP and re-read [exit-ritual.md § Classification heuristics](../preflight/exit-ritual.md#classification-heuristics):

- Brainstorming where every knowledge item belongs (heuristics catch 90%; default-brainstorm is the failure mode)
- Saving session logs / debug dumps to `flightdeck/` — transient byproducts, not knowledge; DO NOT WRITE
- Bumping `Last updated` after a typo fix or pure exploration
- Saving transient scratch into `flightdeck/` instead of project-root `tmp/`
- Adding cockpit sections that duplicate what the folder INDEX files already track (status lives there)
