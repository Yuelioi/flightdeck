---
name: status
description: Keep a flightdeck artifact's lifecycle status fresh and its folder INDEX row in sync. Identify the target artifact with high confidence (currently-edited file → current executing-plan → most-recent unambiguous creation); if none is unambiguous, do nothing. Always-auto (when self-invoked and `status` is in rules.md `model_invocable`): (1) right after writing a new file into `flightdeck/{specs,plans,sketches,…}` set `pending` (sketches → `active`); (2) in the reasoning moment just before a user-requested commit that finishes a plan/spec's work, set `awaiting-review`. Opt-in (only if the member is in rules.md `status_auto`): `start` → when beginning execution of a plan set `active`; `land` → when the user approves/signs off set `done`, then ask before archiving. Never fires on ordinary edits (typo/wording fixes); forward-only, never downgrades. Triggered automatically or by `/flightdeck:status`.
---

# Flightdeck Status — lifecycle auto-flip

The only **high-frequency, lightweight, model-invocable** flightdeck ritual. It keeps a single artifact's lifecycle `status:` honest mid-session, so state doesn't drift and the next `preflight` reads truth from the INDEX. It is complementary to `landing`, not a replacement: `landing` is the low-frequency batch wrap-up; `status` is the in-flight keep-fresh.

It **only** edits one artifact's frontmatter `status:` + that artifact's row in its folder `INDEX.md` (+ that folder's count in the root INDEX). When `land` is enabled it additionally archives via the shared Land Routine (confirm-gated). It does **not** touch `cockpit.md`, does **not** commit, does **not** run length / AGENTS.md regeneration.

## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` (absent file ⇒ treat every key as empty). Look at its `model_invocable` list (absent key or `[]` = empty).

- If **`status` is in `model_invocable`** → allowed; continue this ritual normally.
- Else (`status` not listed):
  - If you can tell this run was an **explicit user `/flightdeck:status`** invocation (e.g. the platform injected a `<command-name>` marker for it) → allowed; continue.
  - Otherwise — you reached this skill by **model self-invocation** (skill tool), **or you cannot tell the call source** → **STOP immediately.** Report: "`status` is manual-only in this project. To let the model self-invoke it, add `model_invocable: [status]` to `flightdeck/rules.md`." Run no further step.

This gate defaults to manual-only: with no `model_invocable` key (or no `rules.md`), behavior matches the former `disable-model-invocation: true`. Manual `/flightdeck:status` always bypasses this gate (it only restricts model self-invoke).

## Step 1 — read config

From the same `flightdeck/rules.md` read `status_auto` (a list; absent key, `[]`, or no `rules.md` ⇒ empty = no optional transitions). The two **core** transitions below run regardless of `status_auto`; the **opt-in** transitions run only if their member is present.

## Step 2 — identify the target artifact (confidence rule)

Every auto-flip needs to know **which** artifact. Resolve by priority:

1. The flightdeck artifact **being written/edited this turn**.
2. The plan **currently being executed** (executing-plans context).
3. The **most recently created** artifact this session, if unambiguous.
4. None uniquely determined → **do nothing**.

**If the target artifact cannot be identified with high confidence, status MUST NOT perform an automatic transition.** (Missing a flip is recoverable by `landing`/`preflight`; flipping the wrong artifact is hard to detect and forward-only cannot undo it.)

## Step 3 — transitions

| Trigger | Target | Class | Auto? |
|---|---|---|---|
| Wrote a **new artifact** into `flightdeck/{specs,plans,sketches,…}` | `pending` (sketches → `active`) | core | always |
| Bound work **finished / just before a user-requested commit** | `awaiting-review` | core | always |
| **Began executing** a plan | `active` | opt-in `status_auto:[start]` | only if enabled |
| User **approved / signed off** | `done` → land | opt-in `status_auto:[land]` | only if enabled; `done` auto, land confirm-gated |

- Fire only at **new-artifact writes** and **clear status-semantic moments** — never on ordinary edits (typo/wording fixes).
- For trigger #4, if `land` is **not** in `status_auto`, do nothing (leave it to `landing`) — do not set `done` either.

## Step 4 — forward-only state machine

- Chain: `pending → active → awaiting-review → done`. **Direct jumps allowed**: since `active` is opt-in, `finish` commonly does `pending → awaiting-review` skipping `active` — this is legal.
- **Forward-only / idempotent**: if the target status equals the current one or is *earlier* in the chain → **no-op** (never downgrade, never error). E.g. user manually set a new file to `active`; the create→pending trigger is a no-op.
- **sketches**: legal statuses are `active`/`scrapped` only; create sets `active`; sketches never enter the awaiting-review/done chain.
- `blocked` / `scrapped` are **explicit human** actions — never auto-set them.

## Step 5 — sync the INDEX

After flipping frontmatter, reuse landing's single-folder regeneration (see [exit-ritual.md § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules)):

1. Regenerate the affected folder's `INDEX.md` `<!-- AUTO -->` region in full (folders hold few files — cheap and deterministic; avoids fragile in-place +1/−1 count math).
2. Recompute **only that folder's** count line in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. Touch no other folder.

## Step 6 — done + land (only when `status_auto` includes `land`)

When the user approves and `land` is enabled:

1. **Set `done` automatically** — "review passed" is an asserted fact; do not ask to confirm `done` itself.
2. **Ask to confirm the archive** (destructive: moves files). On confirm → run the shared **[Land Routine](../preflight/exit-ritual.md#land-routine)** (do not reimplement it). On decline → leave the artifact at `done` **but un-archived** (done-but-unlanded); `preflight`/`landing` will surface and offer to land it later. **Never** revert `done` because the land confirm was declined.

## Don't do

- Don't touch `cockpit.md` (no `Last updated` bump, no sections) — status visibility lives in folder INDEX, not cockpit.
- Don't commit, don't run length checks or AGENTS.md regeneration.
- Don't downgrade a status; don't auto-set `blocked`/`scrapped`.
- Don't reimplement the land steps — call the shared Land Routine.
- Don't act when the target artifact is ambiguous.
