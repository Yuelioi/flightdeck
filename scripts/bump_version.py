"""flightdeck release helper — sync the version across packaging manifests (maintainer tooling).

The mechanical part of `flightdeck/checklists/version-bump.md`:
- `set <version>` writes the version into all 5 packaging manifests (the #1 pitfall is
  forgetting one of them).
- `--check` verifies the 5 agree and match the CHANGELOG top heading.

Judgment stays manual (see the checklist): semver level, CHANGELOG prose, `MIGRATION.md`
`current` (deliberately NOT touched here — manual), commit, annotated tag, push.

This operates on flightdeck's OWN repo, not a user deck — it is sibling to flightdeck_index.py
(which regenerates user-deck INDEXes), not part of the shipped deck mechanical layer.
"""

import re
import sys
from pathlib import Path

MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]

# Both READMEs hardcode the version (no dynamic badge) and drift silently when only the
# manifests get bumped — so the bumper owns them too. Each carries the version at anchored
# sites only; bare semvers in prose (e.g. "the final 3.0.0") must stay put.
READMES = ["README.md", "README.zh.md"]

# Only quoted semver (optional pre-release, e.g. 3.0.0-alpha.1) — never an
# unquoted integer schema version.
_SEMVER = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?"
VERSION_RE = re.compile(r'("version"\s*:\s*")(' + _SEMVER + r')(")')
CHANGELOG_RE = re.compile(r"^##\s*\[(" + _SEMVER + r")\]", re.MULTILINE)

# README version sites, each (prefix, version, suffix). Anchored tight so prose semvers
# never match. The shields badge URL escapes a literal '-' as '--', so its version token
# is captured loosely (between `version-` and `-orange`) and round-tripped via _dash/_undash.
_BADGE_URL_RE = re.compile(r"(/badge/version-)(.+?)(-orange)")
_BADGE_ALT_RE = re.compile(r"(\[!\[Version:\s*)(" + _SEMVER + r")(\])")
_BANNER_RE = re.compile(r"(>\s*\*\*`)(" + _SEMVER + r")(`)")


def _dash(v):
    return v.replace("-", "--")  # semver -> shields URL escaping


def _undash(v):
    return v.replace("--", "-")  # shields URL escaping -> semver


def read_versions(root):
    root = Path(root)
    out = {}
    for rel in MANIFESTS:
        m = VERSION_RE.search((root / rel).read_text(encoding="utf-8"))
        out[rel] = m.group(2) if m else None
    return out


def set_version(root, new):
    root = Path(root)
    for rel in MANIFESTS:
        p = root / rel
        text = VERSION_RE.sub(
            lambda m: m.group(1) + new + m.group(3), p.read_text(encoding="utf-8")
        )
        p.write_text(text, encoding="utf-8")
    set_readme_version(root, new)


def set_readme_version(root, new):
    root = Path(root)
    for rel in READMES:
        p = root / rel
        if not p.exists():  # READMEs are optional in test fixtures
            continue
        text = p.read_text(encoding="utf-8")
        text = _BADGE_URL_RE.sub(lambda m: m.group(1) + _dash(new) + m.group(3), text)
        text = _BADGE_ALT_RE.sub(lambda m: m.group(1) + new + m.group(3), text)
        text = _BANNER_RE.sub(lambda m: m.group(1) + new + m.group(3), text)
        p.write_text(text, encoding="utf-8")


def read_readme_versions(root):
    root = Path(root)
    out = {}
    for rel in READMES:
        p = root / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        m = _BADGE_URL_RE.search(text)
        if m:
            out[f"{rel}#badge"] = _undash(m.group(2))
        m = _BANNER_RE.search(text)
        if m:
            out[f"{rel}#banner"] = m.group(2)
    return out


def changelog_version(root):
    m = CHANGELOG_RE.search((Path(root) / "CHANGELOG.md").read_text(encoding="utf-8"))
    return m.group(1) if m else None


def check(root):
    problems = []
    versions = read_versions(root)
    for rel, v in versions.items():
        if v is None:
            problems.append(f"{rel}: no quoted semver version field found")
    sites = {rel: v for rel, v in versions.items()}
    sites.update(read_readme_versions(root))  # READMEs drift too — verify them
    present = {v for v in sites.values() if v}
    if len(present) > 1:
        detail = ", ".join(f"{rel}={v}" for rel, v in sites.items())
        problems.append(f"version sites disagree: {detail}")
    cl = changelog_version(root)
    if present and cl and cl not in present:
        problems.append(f"CHANGELOG top [{cl}] != version sites {sorted(present)}")
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "--check":
        root = argv[1] if len(argv) > 1 else "."
        problems = check(root)
        if problems:
            print("version DRIFT:")
            for p in problems:
                print("  - " + p)
            return 1
        print("manifests consistent")
        return 0

    if argv and argv[0] == "set":
        if len(argv) < 2:
            print("usage: bump_version.py set <version> [root]")
            return 2
        new, root = argv[1], (argv[2] if len(argv) > 2 else ".")
        set_version(root, new)
        print(f"set version {new} across {len(MANIFESTS)} manifests")
        return 0

    print("usage: bump_version.py (set <version> | --check) [root]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
