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
