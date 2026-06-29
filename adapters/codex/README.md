# Adapter: Codex

**Status**: tested

## What's in place

- [`.codex-plugin/plugin.json`](../../.codex-plugin/plugin.json) — Codex plugin manifest pointing at `./skills/`.
- Skill content under [`skills/`](../../skills/) is plain markdown and shared with the other adapters.

## Install

Codex installation from a GitHub plugin link has been verified.

1. Open `Plugins`.
2. Add a plugin from GitHub.
3. Paste:

```text
https://github.com/Yuelioi/flightdeck
```

Then enable `Flightdeck`.

## Invocation

Use the three user-invoked commands:

- `/flightdeck:launch`
- `/flightdeck:preflight`
- `/flightdeck:walkaround`

`persist` is not a command. In an engaged flightdeck session, it runs as the turn-end habit: update the deck, capture useful knowledge, and commit locally.
