# Adapter: Claude Code

**Status**: ✅ tested

## Manifests

- [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) — plugin manifest.
- [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json) — self-hosted marketplace declaration.

## Install — primary path (plugin marketplace)

In any Claude Code session:

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

To update: re-run `/plugin install`. To uninstall: `/plugin uninstall flightdeck`.

This is the recommended path — it gives proper version tracking and lifecycle.

## Install — alternative (direct copy)

For users who don't want to use the plugin marketplace, the installers at the repo root copy every `skills/*` subdir directly into the user-level Claude Code skills directory.

| OS | Target path |
| --- | --- |
| macOS / Linux | `~/.claude/skills/` |
| Windows | `%USERPROFILE%\.claude\skills\` |

```powershell
.\install.ps1
```

```bash
./install.sh
```

After install:

```
~/.claude/skills/preflight/             # /flightdeck:preflight — session-entry takeover (read-only; deckless → launch)
├── SKILL.md
├── protocol.md
├── folder-semantics.md
├── templates.md
└── exit-ritual.md
~/.claude/skills/launch/                # /flightdeck:launch — first-time deck creation
└── SKILL.md
~/.claude/skills/new/                    # /flightdeck:new — author a deck artifact
└── SKILL.md
~/.claude/skills/landing/               # /flightdeck:landing explicit trigger
└── SKILL.md
~/.claude/skills/walkaround/            # /flightdeck:walkaround integrity audit
└── SKILL.md
~/.claude/skills/emit-agents-md/        # /flightdeck:emit-agents-md AGENTS.md emitter
└── SKILL.md
~/.claude/skills/status/                # /flightdeck:status lifecycle status flip (model-invocable; opt-in via rules.md)
└── SKILL.md
```

## Verification

After install (either path), in a Claude Code session:

1. Start a session in any project directory.
2. The `preflight` skill should appear in the available skills list with description starting "Use when explicitly invoking the flightdeck entry ritual...".
3. Force-invoke with `/flightdeck:preflight` and confirm the takeover runs (read-only; in a deckless dir it points to `/flightdeck:launch`).
4. Force-invoke `/flightdeck:landing` and `/flightdeck:walkaround` — these should run the corresponding rituals explicitly.

If the skill does not appear:
- Direct install: check `ls ~/.claude/skills/preflight/SKILL.md` exists.
- Marketplace install: check `~/.claude/plugins/` for the cached plugin.
- Either: verify SKILL.md frontmatter is intact (`name:` and `description:`).

## How invocation works

- **Nothing loads automatically** — flightdeck installs no startup hook. You run `/flightdeck:preflight` to begin a session.
- `/flightdeck:preflight` is the session-entry takeover: it reads `cockpit.md`, reconciles against git (passive note only), and reports the next item. In a deckless dir (no `cockpit.md`) it points you to `/flightdeck:launch` and stops — deck creation lives there.
- Flightdeck is **self-contained**: it does not require any other plugin to function. If you also have `superpowers` installed, the SKILL.md mentions its `brainstorming` / `writing-plans` skills as optional companions — fine if present, fine if absent.

## Uninstall

Marketplace path:

```text
/plugin uninstall flightdeck
```

Direct path:

```bash
# macOS / Linux
rm -rf ~/.claude/skills/{preflight,launch,new,landing,walkaround,emit-agents-md,status}
```

```powershell
# Windows
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\preflight", "$env:USERPROFILE\.claude\skills\launch", "$env:USERPROFILE\.claude\skills\new", "$env:USERPROFILE\.claude\skills\landing", "$env:USERPROFILE\.claude\skills\walkaround", "$env:USERPROFILE\.claude\skills\emit-agents-md", "$env:USERPROFILE\.claude\skills\status"
```

## Invocation (no gate as of 3.0)

All five flightdeck rituals (`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`) **always self-invoke** — 3.0 removed the model-invocation gate, so there is no call-source check. Claude Code still injects a `<command-name>/flightdeck:<ritual></command-name>` marker on explicit user invocation, but flightdeck no longer keys any behavior off it. (Pre-3.0 `model_invocable` lists are read but ignored.)

The 5th ritual `status` is auto-discovered from `skills/status/` (directory-based manifest); `launch` (first-time deck creation) likewise from `skills/launch/`. No manifest edit is needed to add either.
