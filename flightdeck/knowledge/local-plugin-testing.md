# local plugin testing checklist

SUMMARY: How to locally test an unpublished flightdeck build / sync the working tree into the plugin cache.
READ WHEN: before locally testing an unpublished build / syncing the working tree into the plugin cache

---

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

# Stamp the build FIRST, so /MIR carries the fresh .current into the cache. This is the
# only place --write runs — see "Build-stamp anchor" below.
uv run "$src\scripts\build_stamp.py" --write   # writes $src\.current = hash(build inputs)

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

## Build-stamp anchor (`.current` — "is the cache the latest dev build?")

Inside a dogfood session you can't see whether the loaded cache reflects your latest edits.
`.current` (repo root, **git-ignored**) holds a short content hash over the **plugin build inputs**
(`skills/ scripts/ scaffolds/ adapters/`, the `*-plugin/` manifests, `gemini-extension.json`,
`AGENTS.md`/`GEMINI.md`/`CLAUDE.md`) — **not** the `flightdeck/` deck, `docs/`, or `tmp/`.

> **Why git-ignored, never committed.** `.current` measures "*this* machine's working tree ==
> the build *this* machine last synced into *its* cache." That's per-machine local state. A
> committed copy lies on every other clone: a fresh checkout's working tree matches the
> committed hash → `--check` says `current`, but that clone never synced — its loaded plugin is
> the published marketplace build. Ignored instead: an un-synced clone has no `.current`, so
> `--check` correctly returns `unknown — run --write during sync` (exit 2). The tooling
> (`build_stamp.py`, this checklist) is committed; only the stamp value is local.

- `--write` recomputes and writes `.current`. It runs **only** as the first sync step above
  (before robocopy), so the mirror carries the fresh stamp into the cache. Never run `--write`
  without then syncing, or `.current` will claim "current" while the cache is stale.
- `--check` recomputes the live hash and compares: `current` (exit 0) / `stale` (exit 1) /
  no `.current` (exit 2). Any edit to a build input after the last sync makes it report `stale`.

Because `--write` only fires at sync, detection is automatic — no manual version bump. A
`git checkout`/`pull` that renormalizes line endings can report a spurious `stale`; that errs
toward re-syncing (never false-`current`), so it's safe.

## Verification

- Cache matches working tree: `uv run scripts\build_stamp.py --check` → `current`. (After any
  later build-input edit it flips to `stale` — that's the signal to re-sync.)
- Changed files landed: `Get-FileHash $src\skills\preflight\SKILL.md` equals `Get-FileHash $dst\skills\preflight\SKILL.md`.
- Deletions propagated: a file removed in the repo is absent under `$dst`.
- `.in_use` exists and is a directory: `(Get-Item "$dst\.in_use" -Force).PSIsContainer` → `True`.
- New session: the skill list / `/flightdeck:preflight` reflects the new behavior.
