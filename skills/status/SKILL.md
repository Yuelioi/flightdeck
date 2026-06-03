---
name: status
description: Keep a flightdeck artifact's lifecycle status fresh and its folder INDEX row in sync. Identify the target artifact with high confidence (currently-edited file → current executing-plan → most-recent unambiguous creation); if none is unambiguous, do nothing. Always-auto (when self-invoked, unless a House Rule restricts `status`): (1) right after writing a new file into `flightdeck/{specs,plans,sketches,…}` set `pending` (sketches → `active`); (2) in the reasoning moment just before a user-requested commit that finishes a plan/spec's work, set `awaiting-review`. Default-on (unless a House Rule `status: don't auto …` disables it): `start` → when beginning execution of a plan set `active`; `land` → when the user approves/signs off set `done`, then ask before archiving. Never fires on ordinary edits (typo/wording fixes); forward-only, never downgrades. Triggered automatically or by `/flightdeck:status`.
---

# Flightdeck Status — lifecycle auto-flip

The only **high-frequency, lightweight, model-invocable** flightdeck ritual. It keeps a single artifact's lifecycle `status:` honest mid-session, so state doesn't drift and the next `preflight` reads truth from the INDEX. It is complementary to `landing`, not a replacement: `landing` is the low-frequency batch wrap-up; `status` is the in-flight keep-fresh.

It edits one artifact's frontmatter `status:` (and, on every flip, that artifact's `last_updated:` — see Step 4) + that artifact's row in its folder `INDEX.md` (+ that folder's count in the root INDEX). When `land` is enabled it additionally archives via the shared Land Routine (confirm-gated). It does **not** touch `cockpit.md`, does **not** commit, does **not** run length / AGENTS.md regeneration.

## Step 0 — model-invocation gate (run before any other step)

Read `flightdeck/rules.md` and resolve per [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order). **Default (3.0): `status` is self-invocable** — continue.

- **Restricted** only if House Rules `### Autonomy overrides` says `status: don't self-invoke; I run it manually` (or a pre-3.0 deck's `model_invocable` list omits `status`):
  - explicit user `/flightdeck:status` (e.g. a `<command-name>` marker) → allowed; continue.
  - model self-invocation, or you cannot tell the call source → **STOP immediately.** Report: "`status` is manual-only in this project (House Rule). Remove the `status: don't self-invoke` line to allow model self-invoke." Run no further step.

Manual `/flightdeck:status` always bypasses this gate (it only restricts model self-invoke).

## Step 1 — read config

**Default (3.0): both optional transitions (`start`, `land`) are on.** A House Rule `status: don't auto start` / `status: don't auto land` disables one (or, on a not-yet-migrated deck, a pre-3.0 `status_auto` list is honored for compat — enabling only its members). The two **core** transitions below always run.

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
| **Began executing** a plan | `active` | default-on `start` | unless House Rule `status: don't auto start` |
| User **approved / signed off** | `done` → land | default-on `land` | unless disabled; `done` auto, land confirm-gated |

- Fire only at **new-artifact writes** and **clear status-semantic moments** — never on ordinary edits (typo/wording fixes).
- For trigger #4, if `land` is **disabled** (House Rule `status: don't auto land`), do nothing (leave it to `landing`) — do not set `done` either.

## Step 4 — forward-only state machine

- Chain: `pending → active → awaiting-review → done`. **Direct jumps allowed**: since `active` is opt-in, `finish` commonly does `pending → awaiting-review` skipping `active` — this is legal.
- **Forward-only / idempotent**: if the target status equals the current one or is *earlier* in the chain → **no-op** (never downgrade, never error). E.g. user manually set a new file to `active`; the create→pending trigger is a no-op.
- **sketches**: legal statuses are `active`/`scrapped` only; create sets `active`; sketches never enter the awaiting-review/done chain.
- `blocked` / `scrapped` are **explicit human** actions — never auto-set them.
- **Bump `last_updated` on every flip.** Whenever this skill changes `status:` (any transition above, including the create→`pending`/`active` write), set the same artifact's `last_updated:` to today. A status flip is by definition a substantive change. This is the auto-bump anchor for the case where the user (or model) edited the body and `status` performs the flip — `status` writes `last_updated` so no one has to remember a second field. Adding `last_updated` to a spec/plan that lacked it is fine (it's recommended). Do **not** bump `last_updated` on a no-op (when the flip is skipped per forward-only). **Sketch exception:** do not *add* `last_updated` to a sketch that lacks it — sketches usually carry only `status` + `summary`, and the terminal `scrapped` flip gains nothing from it; if a sketch already has the field, bump it as usual.

## Step 5 — sync the INDEX

After flipping frontmatter, reuse landing's single-folder regeneration (see [exit-ritual.md § INDEX regeneration](../preflight/exit-ritual.md#index-regeneration--scope-rules)):

1. Regenerate the affected folder's `INDEX.md` `<!-- AUTO -->` region in full (folders hold few files — cheap and deterministic; avoids fragile in-place +1/−1 count math). Build each row per the shared **Row format** rule — a workflow row's summary segment is the file's `summary` frontmatter, so `status` reads `summary` from the start (not status alone).
2. Recompute **only that folder's** count line in the root `flightdeck/INDEX.md` `<!-- AUTO -->` region. Touch no other folder.

## Step 6 — done + land (skipped only when a House Rule disables `land`)

When the user approves and `land` is enabled:

1. **Set `done` automatically** — "review passed" is an asserted fact; do not ask to confirm `done` itself.
2. **Ask to confirm the archive** (destructive: moves files). On confirm → run the shared **[Land Routine](../preflight/exit-ritual.md#land-routine)** (do not reimplement it). On decline → leave the artifact at `done` **but un-archived** (done-but-unlanded); `preflight`/`landing` will surface and offer to land it later. **Never** revert `done` because the land confirm was declined.

## Step 7 — land-readiness (signal 1)

If this invocation flipped an artifact to `done` / `awaiting-review`, run the shared [Land-readiness check](../preflight/exit-ritual.md#land-readiness-check) — signal 1 is satisfied, so emit a one-line nudge ("looks like a landing point — run `/flightdeck:landing`?") or auto-run landing per [Rule resolution order](../preflight/protocol.md#rule-resolution-order). Edge-triggered by the flip itself; a no-op transition emits nothing (no nag).

## Don't do

- Don't touch `cockpit.md` (no `Last updated` bump, no sections) — status visibility lives in folder INDEX, not cockpit.
- Don't commit, don't run length checks or AGENTS.md regeneration.
- Don't downgrade a status; don't auto-set `blocked`/`scrapped`.
- Don't reimplement the land steps — call the shared Land Routine.
- Don't act when the target artifact is ambiguous.
