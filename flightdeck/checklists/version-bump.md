---
status: active
last_updated: 2026-06-11
when_to_read: before cutting a new flightdeck release / bumping the version number
applies_to: [.claude-plugin, .codex-plugin, .cursor-plugin, gemini-extension.json, CHANGELOG.md, MIGRATION.md, scripts/bump_version.py]
---

# Version bump checklist

## When to follow this

Whenever the version number changes — shipping a release, or correcting a version. Flightdeck carries the version in **five** manifest files plus `CHANGELOG.md`; they must agree, or different platforms advertise different versions.

## Fast path (script)

The mechanical parts — bumping all five manifests and verifying they agree — are scripted in `scripts/bump_version.py` (pure stdlib; run with `uv run` or `python`):

- **`bump_version.py set X.Y.Z`** — write the version into all five manifests at once (kills the "forgot one manifest" pitfall below).
- **`bump_version.py --check`** — verify the five agree and match the `CHANGELOG.md` top heading; exit non-zero on drift.

It deliberately does **not** touch `MIGRATION.md` (its `current` is a separate two-part *layout* version, not the release semver) or write the CHANGELOG. Everything in Steps 1, 3–6 that needs judgment stays manual.

## Steps

1. **Pick the semver level** (current → next):
   - **patch** (`x.y.Z`) — backward-compatible fixes / wording / reliability hardening of existing skills. No new folders, fields, or commands.
   - **minor** (`x.Y.0`) — new backward-compatible capability (new folder, frontmatter field, audit, skill).
   - **major** (`X.0.0`) — breaking change (renamed folder/command, removed field). Post-v1.0 these need a migration note.
   - **pre-release** (`X.Y.Z-alpha.N` → `-beta.N` → bare `X.Y.Z`) — early-tester cut of an unfinished release; semver sorts it before the final. Script regexes accept the suffix (since v3.0.0-alpha.1). **Never four-part `X.Y.Z.W`** — not valid semver; marketplaces/npm won't parse it.
2. **Bump the version string in all five manifests** (keep them identical) — or run `uv run scripts/bump_version.py set X.Y.Z`:
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `.codex-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
   - `gemini-extension.json`
3. **Add a `CHANGELOG.md` entry** at the top under a new `## [x.y.z] — YYYY-MM-DD` heading, grouped Keep-a-Changelog style (`Added` / `Changed` / `Fixed` / etc.). Link archived specs/plans in `flightdeck/archive/` where relevant.
   - **Also bump `MIGRATION.md` frontmatter `current`** to the new version. If the release changes deck structure (a mandatory new field, a removed cockpit field, any contract change requiring existing decks to migrate), write a `3.0 → X.Y` migration section in `MIGRATION.md`. (3.0 = format baseline / version 0: no backward-compat machinery — migration is authored on demand starting at the first structural release after 3.0, not pre-wired.) Purely additive releases need no migration section.
4. **Commit** — subject `vX.Y.Z: <one-line summary>` (matches existing release commits). Follow `checklists/commits.md` if present.
5. **Tag — annotated** — `git tag -a vX.Y.Z -m "vX.Y.Z — <summary>"`. Must be annotated: lightweight tags (`git tag vX.Y.Z`) are silently skipped by `--follow-tags` and never reach origin. The README version badge reads GitHub releases, which come from tags.
6. **Push** — `git push origin main --follow-tags` (commit + annotated tag together), then confirm with `git ls-remote --tags origin`. If the tag is missing, push it explicitly: `git push origin vX.Y.Z`.

## Verification

- All five manifests agree + match the CHANGELOG: `uv run scripts/bump_version.py --check` (or `grep -rn '"version"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json` for one value).
- `CHANGELOG.md` top entry matches that value and carries today's date.
- `git tag --points-at HEAD` shows `vX.Y.Z`.
- `git status` clean and `main` not ahead of `origin/main` after push.

## Common pitfalls

- **Bumping fewer than five files** — the easiest miss; Cursor/Codex/Gemini manifests get forgotten because Claude's is the one you usually open. Always grep all five afterward.
- **Tag ↔ CHANGELOG drift** — tagging `vX.Y.Z` while the CHANGELOG top still says the previous version, or vice versa.
- **Forgetting the tag** — a pushed release commit with no tag leaves the version badge stale (this is how `v1.1.0` shipped untagged).
- **Lightweight tag + `--follow-tags`** — `--follow-tags` only pushes *annotated* tags, so a `git tag vX.Y.Z` (no `-a`) is created locally but silently never pushed. Always `git tag -a`, and verify with `git ls-remote --tags origin` after pushing. (Hit on the v1.1.1 release itself.)
