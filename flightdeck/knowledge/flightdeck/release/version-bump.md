# version bump checklist

SUMMARY: How to cut a new flightdeck release / bump the version number.
READ WHEN: before cutting a new release / bumping the version number

---

## When to follow this

Whenever the version number changes — shipping a release, or correcting a version. Flightdeck carries the version in **five** manifest files, **both READMEs** (badge alt-text + URL + the warning-banner token), plus `CHANGELOG.md`; they must agree, or different platforms advertise different versions.

## Fast path (script)

The mechanical parts — bumping all five manifests **and both READMEs** and verifying they agree — are scripted in `scripts/bump_version.py` (pure stdlib; run with `uv run` or `python`):

- **`bump_version.py set X.Y.Z`** — write the version into all five manifests **and both READMEs** (badge + banner) at once (kills the "forgot one manifest" / "README badge drifted" pitfalls below). It rewrites only anchored version sites, so bare semvers in prose (e.g. "the final 3.0.0") are left untouched.
- **`bump_version.py --check`** — verify the five manifests + both READMEs agree and match the `CHANGELOG.md` top heading; exit non-zero on drift.

It deliberately does **not** write the CHANGELOG. Everything in Steps 1, 3–6 that needs judgment stays manual.

## Pre-release gates (block the release if any fails)

- **Publishing surface is English-only.** `skills/` (incl. the launch scaffold), `examples/`, README, banners, field labels ship to / are seen by every user — prose, headings, anchors, and examples must all be English (see `briefing.md` `## Conventions`). A prose rule alone has repeatedly failed to hold, so this is a hard release gate: `rg -lP '\p{Han}' skills examples` must return **nothing**. Any hit → translate before cutting the release (mind Chinese-named headings that other files anchor-link to, and Chinese-named section conventions like `## 评审纪要`).

## Steps

1. **Pick the semver level** (current → next):
   - **patch** (`x.y.Z`) — backward-compatible fixes / wording / reliability hardening of existing skills. No new folders, fields, or commands.
   - **minor** (`x.Y.0`) — new backward-compatible capability (new folder, frontmatter field, audit, skill).
   - **major** (`X.0.0`) — breaking change (renamed folder/command, removed field). Post-v1.0 these need a migration note.
   - **pre-release** (`X.Y.Z-alpha.N` → `-beta.N` → bare `X.Y.Z`) — early-tester cut of an unfinished release; semver sorts it before the final. Script regexes accept the suffix (since v3.0.0-alpha.1). **Never four-part `X.Y.Z.W`** — not valid semver; marketplaces/npm won't parse it.
2. **Bump the version string in all five manifests + both READMEs** (keep them identical) — or run `uv run scripts/bump_version.py set X.Y.Z` (does all of them):
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `.codex-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
   - `gemini-extension.json`
   - `README.md` + `README.zh.md` (version badge + warning-banner token — `set` rewrites both)
3. **Add a `CHANGELOG.md` entry** at the top under a new `## [x.y.z] — YYYY-MM-DD` heading, grouped Keep-a-Changelog style (`Added` / `Changed` / `Fixed` / etc.). Summarize relevant archived work context when useful, but do not make the changelog depend on archived spec or plan links.
   - **Migration is `/flightdeck:walkaround`'s job, not a doc.** If a release changes deck structure, fold the old→new mapping into walkaround's check 8 and update the `examples/deck/` reference — there is no migration file to bump.
4. **Commit** — subject `vX.Y.Z: <one-line summary>` (matches existing release commits). Follow the subscribed commits checklist if present.
5. **Tag — annotated** — `git tag -a vX.Y.Z -m "vX.Y.Z — <summary>"`. Must be annotated: lightweight tags (`git tag vX.Y.Z`) are silently skipped by `--follow-tags` and never reach origin. The README version badge reads GitHub releases, which come from tags.
6. **Push** — `git push origin main --follow-tags` (commit + annotated tag together), then confirm with `git ls-remote --tags origin`. If the tag is missing, push it explicitly: `git push origin vX.Y.Z`.

## Verification

- All five manifests + both READMEs agree + match the CHANGELOG: `uv run scripts/bump_version.py --check` (or `grep -rn '"version"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json` for one value).
- `CHANGELOG.md` top entry matches that value and carries today's date.
- `git tag --points-at HEAD` shows `vX.Y.Z`.
- **Publishing surface English-only**: `rg -lP '\p{Han}' skills examples` returns nothing.
- `git status` clean and `main` not ahead of `origin/main` after push.

## Common pitfalls

- **Bumping fewer than five files** — the easiest miss; Cursor/Codex/Gemini manifests get forgotten because Claude's is the one you usually open. Always grep all five afterward.
- **README badge/banner left behind** — both READMEs hardcode the version (the badge is a static shields image, not a dynamic release badge); a manifest-only bump leaves them stale (this is how `alpha.2` lingered in the badge all the way through `alpha.4`). `bump_version.py set` now rewrites them and `--check` flags the drift — but a hand-bump still has to remember.
- **Tag ↔ CHANGELOG drift** — tagging `vX.Y.Z` while the CHANGELOG top still says the previous version, or vice versa.
- **Forgetting the tag** — a pushed release commit with no tag leaves the version badge stale (this is how `v1.1.0` shipped untagged).
- **Lightweight tag + `--follow-tags`** — `--follow-tags` only pushes *annotated* tags, so a `git tag vX.Y.Z` (no `-a`) is created locally but silently never pushed. Always `git tag -a`, and verify with `git ls-remote --tags origin` after pushing. (Hit on the v1.1.1 release itself.)
