---
status: active
last_updated: 2026-06-02
when_to_read: before cutting a new flightdeck release / bumping the version number
applies_to: [.claude-plugin, .codex-plugin, .cursor-plugin, gemini-extension.json, CHANGELOG.md, MIGRATION.md]
---

# Version bump checklist

## When to follow this

Whenever the version number changes — shipping a release, or correcting a version. Flightdeck carries the version in **five** manifest files plus `CHANGELOG.md`; they must agree, or different platforms advertise different versions.

## Steps

1. **Pick the semver level** (current → next):
   - **patch** (`x.y.Z`) — backward-compatible fixes / wording / reliability hardening of existing skills. No new folders, fields, or commands.
   - **minor** (`x.Y.0`) — new backward-compatible capability (new folder, frontmatter field, audit, skill).
   - **major** (`X.0.0`) — breaking change (renamed folder/command, removed field). Post-v1.0 these need a migration note.
2. **Bump the version string in all five manifests** (keep them identical):
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `.codex-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
   - `gemini-extension.json`
3. **Add a `CHANGELOG.md` entry** at the top under a new `## [x.y.z] — YYYY-MM-DD` heading, grouped Keep-a-Changelog style (`Added` / `Changed` / `Fixed` / etc.). Link landed specs/plans in `flightdeck/landed/` where relevant.
   - **Also update `MIGRATION.md` frontmatter `current`** to the new version. If the release changes deck structure (a mandatory new field, a removed cockpit field, any contract change requiring existing decks to migrate), **add the new version to `layout_need_update`** and write a migration section. Purely additive releases leave `layout_need_update` untouched (so they never trigger a false migration prompt).
4. **Commit** — subject `vX.Y.Z: <one-line summary>` (matches existing release commits). Follow `checklists/commits.md` if present.
5. **Tag — annotated** — `git tag -a vX.Y.Z -m "vX.Y.Z — <summary>"`. Must be annotated: lightweight tags (`git tag vX.Y.Z`) are silently skipped by `--follow-tags` and never reach origin. The README version badge reads GitHub releases, which come from tags.
6. **Push** — `git push origin main --follow-tags` (commit + annotated tag together), then confirm with `git ls-remote --tags origin`. If the tag is missing, push it explicitly: `git push origin vX.Y.Z`.

## Verification

- All five manifests agree: `grep -rn '"version"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json` shows one value.
- `CHANGELOG.md` top entry matches that value and carries today's date.
- `git tag --points-at HEAD` shows `vX.Y.Z`.
- `git status` clean and `main` not ahead of `origin/main` after push.

## Common pitfalls

- **Bumping fewer than five files** — the easiest miss; Cursor/Codex/Gemini manifests get forgotten because Claude's is the one you usually open. Always grep all five afterward.
- **Tag ↔ CHANGELOG drift** — tagging `vX.Y.Z` while the CHANGELOG top still says the previous version, or vice versa.
- **Forgetting the tag** — a pushed release commit with no tag leaves the version badge stale (this is how `v1.1.0` shipped untagged).
- **Lightweight tag + `--follow-tags`** — `--follow-tags` only pushes *annotated* tags, so a `git tag vX.Y.Z` (no `-a`) is created locally but silently never pushed. Always `git tag -a`, and verify with `git ls-remote --tags origin` after pushing. (Hit on the v1.1.1 release itself.)
