import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bump_version import read_versions, set_version, changelog_version, check, main

MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]


def make_repo(root, version="2.3.0", changelog="2.3.0"):
    root = Path(root)
    for rel in MANIFESTS:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if "marketplace" in rel:  # version is nested, like the real file
            p.write_text(
                '{\n  "name": "fd",\n  "plugins": [\n    {\n'
                f'      "version": "{version}"\n    }}\n  ]\n}}\n',
                encoding="utf-8",
            )
        else:
            p.write_text(
                f'{{\n  "name": "fd",\n  "version": "{version}",\n  "x": 1\n}}\n',
                encoding="utf-8",
            )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{changelog}] — 2026-06-03\n\n- stuff\n", encoding="utf-8"
    )
    return root


def make_readme(root, version):
    """Minimal README.md + README.zh.md carrying the 3 version sites + a bare-semver trap.

    The trap (`final 3.0.0` / `正式 3.0.0`) is an un-anchored semver in prose that must
    never be rewritten — only the badge + banner-leading version token may move.
    """
    root = Path(root)
    dashed = version.replace("-", "--")  # shields escapes a literal '-' as '--'
    (root / "README.md").write_text(
        "# flightdeck\n\n"
        f"[![Version: {version}](https://img.shields.io/badge/version-{dashed}-orange?style=flat-square)](CHANGELOG.md)\n"
        "[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)\n\n"
        f"> **`{version}` — pre-release for early testers.** Format may change before the final 3.0.0.\n",
        encoding="utf-8",
    )
    (root / "README.zh.md").write_text(
        "# flightdeck\n\n"
        f"[![Version: {version}](https://img.shields.io/badge/version-{dashed}-orange?style=flat-square)](CHANGELOG.md)\n\n"
        f"> **`{version}` —— 面向早期试用者的预发布版。** 正式 3.0.0 之前格式仍可能再变。\n",
        encoding="utf-8",
    )
    return root


class ReadmeVersionTest(unittest.TestCase):
    def test_set_rewrites_badge_and_banner_in_both_readmes(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="3.0.0-alpha.2", changelog="3.0.0-alpha.4")
            make_readme(root, "3.0.0-alpha.2")
            set_version(root, "3.0.0-alpha.4")
            for rel in ("README.md", "README.zh.md"):
                text = (Path(root) / rel).read_text(encoding="utf-8")
                self.assertIn("[![Version: 3.0.0-alpha.4]", text)
                self.assertIn("/badge/version-3.0.0--alpha.4-orange", text)
                self.assertIn("**`3.0.0-alpha.4`", text)
                self.assertNotIn("alpha.2", text)

    def test_set_preserves_bare_semver_in_readme_prose(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="3.0.0-alpha.2", changelog="3.0.0-alpha.4")
            make_readme(root, "3.0.0-alpha.2")
            set_version(root, "3.0.0-alpha.4")
            self.assertIn(
                "final 3.0.0", (Path(root) / "README.md").read_text(encoding="utf-8")
            )
            self.assertIn(
                "正式 3.0.0", (Path(root) / "README.zh.md").read_text(encoding="utf-8")
            )

    def test_check_flags_readme_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="3.0.0-alpha.4", changelog="3.0.0-alpha.4")
            make_readme(root, "3.0.0-alpha.2")  # README behind the manifests
            problems = check(root)
            self.assertTrue(any("README" in p for p in problems))

    def test_check_passes_when_readme_matches(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="3.0.0-alpha.4", changelog="3.0.0-alpha.4")
            make_readme(root, "3.0.0-alpha.4")
            self.assertEqual(check(root), [])

    def test_set_tolerates_missing_readmes(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="2.3.0")  # no README files written
            set_version(root, "2.4.0")  # must not raise
            self.assertEqual(set(read_versions(root).values()), {"2.4.0"})


class CheckTest(unittest.TestCase):
    def test_passes_when_all_consistent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(check(make_repo(d)), [])

    def test_flags_manifest_disagreement(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            (root / "gemini-extension.json").write_text(
                '{\n  "version": "9.9.9"\n}\n', encoding="utf-8"
            )
            problems = check(root)
            self.assertTrue(any("gemini-extension.json" in p for p in problems))

    def test_flags_changelog_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="2.3.0", changelog="2.2.0")
            problems = check(root)
            self.assertTrue(any("CHANGELOG" in p for p in problems))


class SetTest(unittest.TestCase):
    def test_writes_new_version_to_all_manifests(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="2.3.0")
            set_version(root, "3.0.0")
            versions = read_versions(root)
            self.assertEqual(set(versions.values()), {"3.0.0"})
            # changelog untouched (judgment stays manual)
            self.assertEqual(changelog_version(root), "2.3.0")


class PrereleaseTest(unittest.TestCase):
    def test_set_and_check_prerelease_version(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="2.3.0", changelog="3.0.0-alpha.1")
            set_version(root, "3.0.0-alpha.1")
            versions = read_versions(root)
            self.assertEqual(set(versions.values()), {"3.0.0-alpha.1"})
            self.assertEqual(changelog_version(root), "3.0.0-alpha.1")
            self.assertEqual(check(root), [])

    def test_set_back_to_release_from_prerelease(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="3.0.0-alpha.1", changelog="3.0.0")
            set_version(root, "3.0.0")
            self.assertEqual(set(read_versions(root).values()), {"3.0.0"})


class MainTest(unittest.TestCase):
    def test_check_exits_nonzero_on_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="2.3.0", changelog="2.2.0")
            self.assertEqual(main(["--check", str(root)]), 1)

    def test_set_then_check_clean(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d, version="2.3.0", changelog="2.2.0")
            self.assertEqual(main(["set", "2.2.0", str(root)]), 0)
            # now manifests = 2.2.0 = changelog 2.2.0
            self.assertEqual(main(["--check", str(root)]), 0)


if __name__ == "__main__":
    unittest.main()
