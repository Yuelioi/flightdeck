# Adapter: Cursor

**Status**: ⚠️ manifest in place, behaviorally untested

## What's in place

- [`.cursor-plugin/plugin.json`](../../.cursor-plugin/plugin.json) — Cursor plugin manifest pointing at `./skills/`.

## Install

In Cursor Agent chat:

```text
/add-plugin flightdeck
```

Or search "flightdeck" in the plugin marketplace.

## What "untested" means

Cursor's skill / rules discovery has evolved across versions. The manifest follows the same shape as established plugins (e.g., superpowers), and the skill content under `skills/preflight/` is plain markdown — so it should load. What has **not** been verified:

- That Cursor's plugin loader actually surfaces `SKILL.md` frontmatter to the agent.
- That explicit invocation (`/flightdeck:preflight`) works in Cursor's UX.

## Likely Cursor-specific concerns

- **Rule budget**: Cursor injects rules into every prompt. If Cursor reads the full SKILL.md plus the three supporting files inline every turn, the token cost is meaningful. We may need a "lite" mode that loads only `SKILL.md` for Cursor and leaves the rest as on-demand reference.
- **Manual reload**: Cursor may not pick up changes to plugin content without restart.

## How to verify (and flip the matrix to ✅ tested)

1. Install on Cursor per the command above.
2. Open a project with `flightdeck/cockpit.md` populated.
3. Start a fresh chat, ask "What were we doing?" — confirm the AI reads `cockpit.md` first.
4. Try one routing scenario from the README routing table.
5. Open a PR that:
   - Updates the README compatibility matrix `⚠️ untested` → `✅ tested`.
   - Pastes the verification transcript here.
   - Notes token cost observations and whether a "lite" mode is needed.

## Invocation (no gate as of 3.0)

3.0 removed the model-invocation gate: all five rituals (`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`) **always self-invoke**, so no call-source detection is needed on this platform. (Pre-3.0 `model_invocable` lists are read but ignored.) See [protocol § Rule resolution order](../../skills/preflight/protocol.md#rule-resolution-order).
