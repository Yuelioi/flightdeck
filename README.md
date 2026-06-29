<div align="center">

# flightdeck

**A lightweight operating protocol for AI-assisted engineering sessions.**

[![Version: 3.0.0-alpha.6](https://img.shields.io/badge/version-3.0.0--alpha.6-orange?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)
[![Codex](https://img.shields.io/badge/Codex-tested-success?style=flat-square)](adapters/codex/README.md)

English · [中文 README](README.zh.md)

</div>

---

> [!WARNING]
> flightdeck 3.0 is still an alpha. The protocol is usable and dogfooded here, but file shape and wording may still change before the stable 3.0 release. Existing decks are not migrated automatically on install; run `/flightdeck:walkaround` to audit and repair an older deck, or start fresh with `/flightdeck:launch`.

AI assistants are good at one session and bad at continuity. flightdeck gives them a small, explicit recovery payload: what is active, what changed, what knowledge matters later, and what to do next.

## What You Get

- **Session continuity** — `/flightdeck:preflight` reads the project deck, shows resumable work, and waits for your choice before loading topic details.
- **Zero-loss handoff** — after work moves forward, flightdeck updates the active topic index, updates `cockpit.md`, captures durable knowledge, and commits locally.
- **Strict write gate** — it records only decisions, traps, procedures, and facts that change future behavior. No junk-drawer memory dump.
- **Plain markdown** — the deck is files and folders in your repo. You can diff it, review it, grep it, and keep using it across AI tools.

## Install

### Codex CLI / Codex App

Codex installation from a GitHub plugin link has been verified.

1. Open `Plugins`.
2. Add a plugin from GitHub.
3. Paste:

```text
https://github.com/Yuelioi/flightdeck
```

Then enable `Flightdeck` and run `/flightdeck:launch` in a project.

### Claude Code

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

Update by re-running `/plugin install`. Uninstall with `/plugin uninstall flightdeck`.

### Other Tools

Cursor and Gemini manifests are included, but they have not been verified end-to-end yet:

- Cursor: [`.cursor-plugin/`](.cursor-plugin/)
- Gemini CLI: [`gemini-extension.json`](gemini-extension.json)

Verification logs are welcome.

## First Use

In a project repository:

```text
/flightdeck:launch
```

This creates:

```text
flightdeck/
  briefing.md      # project rules and shared-knowledge subscriptions
  cockpit.md       # small project index: focus, active work, next step
  work/            # active topic packages
  knowledge/       # durable project knowledge, routed by headers
```

At the start of future sessions:

```text
/flightdeck:preflight
```

Preflight reads `briefing.md`, reads `cockpit.md`, scans knowledge headers, reports what can be resumed, and stops for your choice. It does not read every topic file or dump every knowledge body into context.

## Core Model

flightdeck keeps two tiers:

- **Warm tier** — `flightdeck/` inside the repo. This is the recovery payload and should be committed.
- **Cold tier** — `~/.flightdeck/` outside the repo. Finished topic packages and parked ideas can live there.

The core rule is **location is state**:

- `flightdeck/work/<topic>/` means active work.
- `~/.flightdeck/projects/<slug>/archive/<topic>/` means finished work.
- `~/.flightdeck/projects/<slug>/ideas/<topic>/` means parked, not active.

Each active topic has an `index.md` that says what is true, what to read now, what to read conditionally, what changed, and what comes next.

Knowledge files use one small routing header:

```markdown
# <title>

SUMMARY: <one-line summary>
READ WHEN: <when this should be loaded>

---
```

That lets preflight keep the map in context while loading bodies only when their trigger matters.

## Commands

| Command | Purpose |
| --- | --- |
| `/flightdeck:launch` | Create a new deck skeleton. Refuses to overwrite an existing deck. |
| `/flightdeck:preflight` | Enter a session: read the deck, scan routing headers, list resumable work, and wait for your choice. |
| `/flightdeck:walkaround` | Audit and repair deck drift: stale cockpit, malformed topic packages, missing routing headers, old deck shape, and similar issues. |

## Compatibility

| Tool | Status | Notes |
| --- | --- | --- |
| Claude Code | Tested | Marketplace install verified. |
| Codex CLI / App | Tested | GitHub plugin-link install verified. |
| Cursor | Manifest only | End-to-end behavior not verified. |
| Gemini CLI | Manifest only | End-to-end behavior not verified. |

## Documentation

- Protocol entrypoint: [skills/preflight/SKILL.md](skills/preflight/SKILL.md)
- Concepts: [skills/preflight/concepts.md](skills/preflight/concepts.md)
- Operations: [skills/preflight/operations.md](skills/preflight/operations.md)
- History: [CHANGELOG.md](CHANGELOG.md)

## Contributing

High-signal contributions:

- A transcript where an AI drifted from the protocol.
- A verification log for Cursor or Gemini.
- A small fix that makes the deck easier to recover from cold.

## License

[MIT](LICENSE) © 月离 (Yuelioi)
