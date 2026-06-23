---
name: status
description: Keep a flightdeck artifact's lifecycle status fresh and its folder INDEX row + cockpit `## In Progress` in sync. Identify the target artifact with high confidence (currently-edited file → current executing-plan → most-recent unambiguous creation); if none is unambiguous, do nothing. Always-auto: right after writing a new spec/plan into `flightdeck/{specs,plans}` set `idea`. Default-on (unless a deck `### Rules` entry disables it): `start` → when beginning work on an idea, flip `idea → active` (add the `YYYY-MM-DD-` prefix + regen cockpit `## In Progress`); on user approval/sign-off set `done`. Archiving is `/flightdeck:landing`'s smart judgment, not status's. Reads/writes the optional `note:` diagnostic. Never fires on ordinary edits (typo/wording fixes); forward-only, never downgrades. Triggered automatically or by `/flightdeck:status`.
---

# Flightdeck Status — lifecycle auto-flip

The only **high-frequency, lightweight, model-invocable** flightdeck ritual. It keeps a single artifact's lifecycle `status:` honest mid-session, so state doesn't drift and the next `preflight` reads truth from the INDEX. It is complementary to `landing`, not a replacement: `landing` is the low-frequency batch wrap-up; `status` is the in-flight keep-fresh.

It edits one artifact's frontmatter `status:` (and, on every flip, that artifact's `last_updated:` — see Step 4) + that artifact's row in its folder `INDEX.md`. On an `idea → active` flip it **also** renames the file to add the `YYYY-MM-DD-` prefix and regenerates the cockpit `## In Progress` AUTO region (the only cockpit region `status` touches — see Step 5a; `landing` also regenerates it). Beyond regenerating `## In Progress`, it does **not** touch `cockpit.md` (`Focus` / `## Next` / `Hanging Tasks`), does **not** archive (archiving is `landing`'s smart judgment), does **not** commit, does **not** run length / AGENTS.md regeneration.

## Step 1 — read config

**Default (3.0): `start` is on.** `start` (idea→active when work begins) fires automatically; a deck `### Rules` entry turns it off. The **core** create→`idea` and approval→`done` transitions below always run. **status no longer archives** — once an artifact flips to `done`, whether/when to move it into `archive/` is `/flightdeck:landing`'s smart, cross-reference-aware judgment (there is no `auto land` toggle anymore).

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
| Wrote a **new spec/plan** into `flightdeck/{specs,plans}` | `idea` (a captured-but-unstarted thought) | core | always |
| **Began work** on an idea (start executing / fleshing it out) | `idea → active` (+ date prefix + regen cockpit `## In Progress`) | default-on `start` | unless a deck `### Rules` entry disables it |
| User **approved / signed off** | `active → done` (+ regen cockpit `## In Progress`) | core | always — **status sets `done` only; it does not archive** |

- Fire only at **new-artifact writes** and **clear status-semantic moments** — never on ordinary edits (typo/wording fixes).
- A new spec/plan that is *already* being worked on (not merely captured) may go straight to `active` — see the direct-jump note in Step 4.
- For the last trigger, status flips `done` and regenerates `## In Progress` (the artifact leaves the active set). **Archiving is not status's job** — `/flightdeck:landing` decides whether to move a `done` artifact into `archive/` by cross-reference-aware judgment.

## Step 4 — forward-only state machine

- Chain: `idea → active → done`. **Direct jumps allowed**: a new spec/plan that is *already* being worked on may go straight to `active` (skipping the captured `idea` stage) — this is legal.
- **Forward-only / idempotent**: if the target status equals the current one or is *earlier* in the chain → **no-op** (never downgrade, never error). E.g. user manually set a new file to `active`; the create→`idea` trigger is a no-op.
- **idea has no date prefix.** A `status: idea` spec is timeless (`<topic>.md`). The `idea → active` flip is the **one** transition that renames the file to add the `YYYY-MM-DD-` prefix — do the rename and the cockpit `## In Progress` regen (Step 5a) in the **same action** so no intermediate state is left behind.
- **Rejecting** a workflow artifact **deletes the file** — only on explicit user instruction (never auto; the AI MUST NOT unilaterally abandon work). git log preserves the history; record a one-line reason in the commit body. There is no `scrapped` status value. `done` is auto-set on user approval/sign-off (the last trigger) — a flip only, no archive.
- **Bump `last_updated` on every flip.** Whenever this skill changes `status:` (any transition above, including the create→`idea` write), set the same artifact's `last_updated:` to today. A status flip is by definition a substantive change. This is the auto-bump anchor for the case where the user (or model) edited the body and `status` performs the flip — `status` writes `last_updated` so no one has to remember a second field. Adding `last_updated` to a spec/plan that lacked it is fine (it's recommended). Do **not** bump `last_updated` on a no-op (when the flip is skipped per forward-only). **Idea exception:** do not *add* `last_updated` to a bare `status: idea` spec that lacks it — an idea usually carries only `status` + `summary`; if it already has the field, bump it as usual.
- **`note:` field.** When the user gives a "why it hasn't moved" reason (a blocker / waiting-on note), write it to the artifact's optional `note:` frontmatter (the merged `active` state's diagnostic carrier — see [protocol § Status ⟂ location](../preflight/protocol.md#status--location-two-orthogonal-axes)); clear it when the reason resolves. `note:` never gates a flip — it is advisory text rendered as `[note: …]` in cockpit `## In Progress` + walkaround.

## Step 5 — sync the INDEX

After flipping frontmatter, regenerate the affected folder's INDEX via the index script — `flightdeck_index <deck>` (call form per the recorded `runtime` — [protocol § Rule resolution order](../preflight/protocol.md#rule-resolution-order)) rewrites that folder's `<!-- AUTO -->` region in full, deterministically from frontmatter, following the shared [Row format](../preflight/exit-ritual.md#index-regeneration--scope-rules) rule — a workflow row's summary segment is the file's `summary` frontmatter, so `status` reads `summary` (not status alone). For `specs/INDEX`, the AUTO region groups by status (`Backlog (idea)` / `Active · Done`) — see [folder-semantics § specs/](../preflight/folder-semantics.md#specs--designs). Touch no other folder.

(One run covers Step 5a too — `flightdeck_index <deck>` regenerates the folder INDEX **and** the cockpit `## In Progress` block together.)

## Step 5a — regen cockpit `## In Progress` (only on a flip that changes the active set)

A `status: active` spec/plan is **visible in cockpit iff it is active** — cockpit `## In Progress` is the AUTO-derived projection of the active set ([protocol § cockpit](../preflight/protocol.md#data-model-folder--kind-frontmatter--status)). So whenever this skill's flip changes the active set — an `idea → active` start (an artifact **enters** `## In Progress`) or an `active → done` flip (it **leaves**) — regenerate the cockpit `<!-- AUTO:inprogress -->` region from every current `status: active` spec/plan:

`flightdeck_index <deck>` emits the `<!-- AUTO:inprogress -->` block (exact marker string) alongside the INDEXes — one row per `status: active` spec/plan, same Row format as INDEX, appending `[note: …]` when the file carries `note:`; one run does Steps 5 + 5a. Because the block is re-derived from current files, the `idea → active` rename is picked up automatically — do the rename **before** the regen so the new filename/link lands in the row.

A create→`idea` write does **not** change the active set → no `## In Progress` regen. This is the only cockpit region `status` touches; `Focus` / `## Next` / `Hanging Tasks` stay landing's / the user's.

## Step 6 — set `done` on approval (status flips only; no archive)

When the user approves / signs off:

1. **Set `done` automatically** — "review passed" is an asserted fact; do not ask to confirm `done` itself. Regenerate the cockpit `## In Progress` region (the artifact leaves the active set — see Step 5a).

   **Verify branch** — when flipping to `done`, first determine whether the task is **needs-verify** (rule: anything mechanically executed by AI/scripts where a misjudgment is not easily noticed; full rule + examples in [exit-ritual § Self-asserting done](../preflight/exit-ritual.md#self-asserting-done--non-blocking-carry-verify)):

   - **needs-verify** → also write `verify: <one-line how-to-verify>` to the artifact's frontmatter, then print: `🔄 [decision: <reason>; pending-verify: <how>; done + verify]`
   - **no-verify** → plain `done` (no `verify` field), print: `🔄 [decision: <reason>; no verify needed; done]`

   `verify` is a **status add-on marker, not a new status** — the full per-kind semantics (present = owes verification, absent = verified, no `verify: failed` value, non-blocking re-surfacing every preflight) live in [protocol § verify field](../preflight/protocol.md#verify--the-verification-marker) and [protocol § Non-blocking verification](../preflight/protocol.md#non-blocking-verification). **The WHEN — when `done` is offered and confirmed — is unchanged.**

2. **Do not archive.** status leaves the artifact `done` in its source folder (done-but-unarchived). Whether to move it into `archive/` is `/flightdeck:landing`'s smart, cross-reference-aware judgment (it evaluates `--archivable` deterministically — see [exit-ritual § Land Routine](../preflight/exit-ritual.md#land-routine)). `done`-not-archived is the **normal staged state** — it waits in the staging area (cockpit `## Staged`) until the user opens the land valve; status emits no land nudge (Step 7).

## Step 7 — `done` is a staged state (no land trigger)

Flipping an artifact to `done` does **not** trigger landing. `done`-not-archived is the **normal staged state**: it sits in the staging area (cockpit `## Staged (awaiting land)`) until the user opens the land valve (`/flightdeck:landing`). `status` does no debounce, no nudge, no auto-land — it flips `done` (+ regen `## In Progress`) and stops. A no-op transition emits nothing.

**Stage (the automatic turn-end persist) does NOT go through `status`.** Every execution turn auto-stages — classify knowledge + board-sync + local commit (see [exit-ritual § Stage](../preflight/exit-ritual.md#stage--turn-end-persist--board-sync)); `status` is only the mid-flight single-artifact flip. When stage judges a state-only "actual change", it **reuses this skill's `## In Progress` diff logic** (Step 5a — re-derive from the current `status: active` set), not a new diff.

## Don't do

- Don't touch `cockpit.md` **beyond** the `## In Progress` AUTO region on an active-set-changing flip (Step 5a) — no `Updated` bump, no `Focus` / `## Next` / `Hanging Tasks` edits. Those are landing's / the user's.
- Don't commit, don't run length checks or AGENTS.md regeneration.
- Don't downgrade a status; don't auto-set `done` outside user approval/sign-off. **Never delete a workflow artifact without explicit user instruction.**
- Don't archive — moving a `done` artifact into `archive/` is `/flightdeck:landing`'s judgment, not status's.
- Don't write `archived` or `landed` into any artifact's `status:` field — these are not valid status values; only the landing Land Routine can move files into `archive/`. Claiming an artifact is archived before landing has run is incorrect.
- Don't act when the target artifact is ambiguous.
