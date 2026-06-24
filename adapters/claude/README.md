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
~/.claude/skills/preflight/    # /flightdeck:preflight — session-entry takeover (read-only; deckless → launch)
├── SKILL.md
└── protocol.md
~/.claude/skills/launch/       # /flightdeck:launch — first-time deck creation
└── SKILL.md
~/.claude/skills/walkaround/   # /flightdeck:walkaround — read-only integrity audit
└── SKILL.md
```

## Verification

After install (either path), in a Claude Code session:

1. Start a session in any project directory.
2. The `preflight` skill should appear in the available skills list with description starting "Use when explicitly invoking the flightdeck entry ritual...".
3. Force-invoke with `/flightdeck:preflight` and confirm the takeover runs (read-only; in a deckless dir it points to `/flightdeck:launch`).
4. Force-invoke `/flightdeck:walkaround` — it should run the integrity audit (read-only; reports drift, fixes nothing).

If the skill does not appear:
- Direct install: check `ls ~/.claude/skills/preflight/SKILL.md` exists.
- Marketplace install: check `~/.claude/plugins/` for the cached plugin.
- Either: verify SKILL.md frontmatter is intact (`name:` and `description:`).

## How invocation works

- **Nothing loads automatically** — flightdeck installs no startup hook. You run `/flightdeck:preflight` to begin a session; if you never run it, flightdeck isn't engaged.
- `/flightdeck:preflight` is the session-entry takeover: it loads the protocol, reads `cockpit.md` (plus `rules.md` / `uses.md`), walks the tree for what's needed, and reports the next item. In a deckless dir (no `cockpit.md`) it points you to `/flightdeck:launch` and stops — deck creation lives there.
- **persist** is automatic, not a command: at the end of any turn that did real work, the AI scans for new knowledge worth keeping and writes it to `knowledge/`, rewrites `cockpit.md`, and commits the repo.
- Flightdeck is **self-contained**: it does not require any other plugin to function. If you also have `superpowers` installed, the SKILL.md mentions its `brainstorming` / `writing-plans` skills as optional companions — fine if present, fine if absent.

## Uninstall

Marketplace path:

```text
/plugin uninstall flightdeck
```

Direct path:

```bash
# macOS / Linux
rm -rf ~/.claude/skills/{preflight,launch,walkaround}
```

```powershell
# Windows
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\preflight", "$env:USERPROFILE\.claude\skills\launch", "$env:USERPROFILE\.claude\skills\walkaround"
```

## Invocation

The three verbs — `preflight` (session entry), `launch` (first-time deck creation), and `walkaround` (integrity audit) — are user-invoked slash commands. Claude Code injects a `<command-name>/flightdeck:<verb></command-name>` marker on explicit invocation; flightdeck keys no behavior off it. **persist** runs automatically as you work — at each turn / milestone that moves the board (no command). Nothing fires on session start.
