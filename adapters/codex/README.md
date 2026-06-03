# Adapter: Codex

**Status**: ⚠️ manifest in place, behaviorally untested

## What's in place

- [`.codex-plugin/plugin.json`](../../.codex-plugin/plugin.json) — Codex plugin manifest pointing at `./skills/`.

## Install

### Codex CLI

```text
/plugins
```

Then search "flightdeck" → select → `Install Plugin`.

### Codex App

In the Codex app, click `Plugins` in the sidebar, find `Flightdeck`, click `+` and follow prompts.

## What "untested" means

The manifest is structured the same as the working Claude one, and the skill content under `skills/preflight/` is plain tool-agnostic markdown — so installation should succeed and Codex should discover the skill. What has **not** been verified:

- That Codex's skill-loading mechanism actually picks up `SKILL.md` with our frontmatter.
- That `description` triggers as expected when a project has `flightdeck/`.
- That `/preflight`-style force-invoke works (Codex may use different syntax).

## How to verify (and flip the matrix to ✅ tested)

1. Install on Codex per the commands above.
2. Open a project with `flightdeck/cockpit.md` populated.
3. Start a fresh session, ask "What were we doing?" — confirm the AI reads `cockpit.md` first.
4. Try one routing scenario from the README routing table (e.g., "Why did the migration break?" should consult `incident-reports/`).
5. Open a PR that:
   - Updates the README compatibility matrix `⚠️ untested` → `✅ tested`.
   - Pastes the verification transcript here.
   - Notes any Codex-specific quirks (e.g., force-invoke syntax differences).

## Call-source detection (model_invocable gate)

**Mode: degraded (until verified).** This platform's manifest carries no per-skill
manual-only switch, so the soft gate ships via the shared `SKILL.md` body. Whether this
platform lets the skill body distinguish a user invocation from a model self-invoke is
**unverified**. Under 3.0 the default is **self-invocable**, so the common case needs no
detection; only a House-Rules restriction (`<ritual>: don't self-invoke; I run it manually`, or a pre-3.0
`model_invocable` omission honored for compat) needs source detection. Until verified, a
restricted ritual runs degraded — treated as manual-only, prompting even on an explicit
user invocation. See [protocol § Rule resolution order](../../skills/preflight/protocol.md#rule-resolution-order).
Flip this note to "formal" with a transcript when verified.
