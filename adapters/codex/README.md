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
4. Try one routing scenario from the README routing table (e.g., "Why did the migration break?" should walk `knowledge/<domain>/` and surface a `# ⚠` trap).
5. Open a PR that:
   - Updates the README compatibility matrix `⚠️ untested` → `✅ tested`.
   - Pastes the verification transcript here.
   - Notes any Codex-specific quirks (e.g., force-invoke syntax differences).

## Invocation

The three verbs — `preflight` / `launch` / `walkaround` — are user-invoked slash commands; **persist** runs automatically at turn end (no command). Nothing fires on session start, so no call-source detection is needed on this platform.
