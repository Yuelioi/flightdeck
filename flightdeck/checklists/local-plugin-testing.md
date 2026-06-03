---
status: active
last_updated: 2026-06-03
when_to_read: before locally testing an unpublished flightdeck build / syncing the working tree into the plugin cache
applies_to: [local-test, dogfood, plugin-cache, robocopy, .in_use, CLAUDE_CONFIG_DIR]
---

# Local plugin testing checklist

## When to follow this

When dogfooding an **unpublished** flightdeck build (e.g. a `3.x` branch) before cutting a release. The live install Claude Code loads is the **plugin cache**, not the repo — so testing means overwriting that cache with the working tree, then restarting the session.

> **Sync only on explicit say-so.** Don't re-mirror after every edit. Make repo edits freely, leave the cache stale, and run the sync once, when the user explicitly says "复制"/"copy". (Why: re-syncing unprompted is noisy and removes the user's control over when test changes go live.)

## Locate the live cache

1. The config dir is **`$env:CLAUDE_CONFIG_DIR`**, *not* always `~/.claude`. A multi-account switcher relocates it (e.g. under `…\.claude-accounts\<name>.config`). Always resolve it from the env var — guessing `~/.claude` syncs into the wrong profile.
2. Cache path: `$env:CLAUDE_CONFIG_DIR\plugins\cache\flightdeck-marketplace\flightdeck\<version>\`.
   - The folder is named after the **published** version (e.g. `2.3.0`) and stays that way even when the content is newer — cosmetic. Confirm the active path via `installed_plugins.json` (`installPath`) if unsure.
3. **`installPath` and the env-var path can disagree yet resolve to the *same bytes*.** On this setup `$CLAUDE_CONFIG_DIR\plugins` is a **junction** → `~/.claude\plugins`, so `installed_plugins.json`'s `installPath` (`~/.claude\…`) and the env-var path point at **one physical cache** — syncing either updates both. Don't assume two profiles when the paths differ: check for a reparse point first — `(Get-Item <path> -Force).Attributes -band [IO.FileAttributes]::ReparsePoint` (+ `.Target`). Only `…\max.config\plugins` is the junction; `…\max.config` itself is a real dir. (2026-06-03: lost two turns treating env-var-path vs `installPath` as two caches — it was one junction.)

## Sync the working tree into the cache

```powershell
$src = "<flightdeck repo root>"   # the working tree you're testing
$dst = "$env:CLAUDE_CONFIG_DIR\plugins\cache\flightdeck-marketplace\flightdeck\<published-version>"

robocopy $src $dst /MIR /XD .git tmp .vscode /XF .in_use   # /MIR mirrors deletions too
# robocopy exit code 0–7 = success; >=8 = failure.

# /MIR deletes .in_use (it is NOT in $src). Recreate it (see gotcha below):
New-Item -ItemType Directory -Force "$dst\.in_use" | Out-Null
$m = Get-Item "$dst\.in_use" -Force
$m.Attributes = $m.Attributes -bor [System.IO.FileAttributes]::Hidden
```

`/MIR` (mirror) is used so files **deleted** in the repo (e.g. a removed skill companion) also disappear from the cache. `/E` (no delete) is fine only for additive changes.

## Gotchas

- **`.in_use` is a hidden *directory*, not a file.** It holds per-session PID lock files the harness manages. `/MIR` wipes it (the repo has no `.in_use`); recreate it as an empty hidden dir after every mirror, or the harness loses its in-use marker. (`/XF .in_use` stops robocopy *copying* it but does **not** stop `/MIR` deleting it.)
- **The sandbox blocks `robocopy … /MIR`.** A destructive-command guard misreads the `/MIR` token as a path to delete. Run the sync with the sandbox bypass (or accept the permission prompt) — `/MIR` itself is intended.
- **Restart the session.** The running session already loaded the *old* skills into context; the synced build only takes effect in a **new** Claude Code session.
- **Never run `/plugin update` or a marketplace sync while testing.** It re-pulls the published version from GitHub and clobbers the local build. To restore the clean published build, reinstall via `/plugin`.

## Verification

- Changed files landed: `Get-FileHash $src\skills\preflight\SKILL.md` equals `Get-FileHash $dst\skills\preflight\SKILL.md`.
- Deletions propagated: a file removed in the repo is absent under `$dst`.
- `.in_use` exists and is a directory: `(Get-Item "$dst\.in_use" -Force).PSIsContainer` → `True`.
- New session: the skill list / `/flightdeck:preflight` reflects the new behavior.
