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

## Call-source detection (model_invocable gate)

**Mode: degraded (until verified).** This platform's manifest carries no per-skill
manual-only switch, so the soft gate ships via the shared `SKILL.md` body. Whether this
platform lets the skill body distinguish a user invocation from a model self-invoke is
**unverified**. Under 3.0 most rituals default **self-invocable**, so the common case needs no
detection; only a restricted ritual needs source detection — that includes **`landing`, which defaults to
manual** (it archives + commits; enable with `landing: self-invoke`), plus any House-Rules restriction
(`<ritual>: don't self-invoke; I run it manually`, or a pre-3.0 `model_invocable` omission honored for compat). Until verified, a
restricted ritual runs degraded — treated as manual-only, prompting even on an explicit
user invocation. See [protocol § Rule resolution order](../../skills/preflight/protocol.md#rule-resolution-order).
Flip this note to "formal" with a transcript when verified.
