import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_init import init, main

FOLDERS = ["specs", "plans", "incidents", "checklists", "charts"]


class InitTest(unittest.TestCase):
    def test_creates_full_deck_and_substitutes_cockpit(self):
        with tempfile.TemporaryDirectory() as d:
            init(d, name="myproj", user="月离", date="2026-06-03",
                 focus="just exploring", next_item="decide what to build")
            deck = Path(d) / "flightdeck"
            cockpit = (deck / "cockpit.md").read_text(encoding="utf-8")
            self.assertIn("# Cockpit — myproj", cockpit)
            self.assertIn("2026-06-03 by 月离 (deck initialized)", cockpit)
            self.assertIn("**Active focus**: just exploring", cockpit)
            self.assertIn("decide what to build", cockpit)
            self.assertNotIn("<ACTIVE_FOCUS", cockpit)
            self.assertNotIn("<FIRST_NEXT_ITEM", cockpit)
            # full layout + 3-file contract present
            for f in FOLDERS:
                self.assertTrue((deck / f / "INDEX.md").exists(), f)
            self.assertTrue((deck / "INDEX.md").exists())
            self.assertTrue((deck / "rules.md").exists())
            self.assertTrue((deck / "landed" / "HISTORY.md").exists())
            # rules.md copied verbatim (a scaffold token survives — not re-authored)
            rules = (deck / "rules.md").read_text(encoding="utf-8")
            self.assertIn("status: don't auto start", rules)  # cheat-sheet phrase, scaffold-only
            self.assertNotIn("disabled_folders", rules)  # removed in the autonomy-convergence pass

    def test_no_git_keeps_history(self):
        # target without .git → no-git deck → HISTORY.md is the history substrate, kept
        with tempfile.TemporaryDirectory() as d:
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            self.assertTrue((Path(d) / "flightdeck" / "landed" / "HISTORY.md").exists())

    def test_git_deck_drops_history(self):
        # target with .git → git log is the history → the copied HISTORY.md is removed
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".git").mkdir()
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            self.assertFalse((Path(d) / "flightdeck" / "landed" / "HISTORY.md").exists())
            # the rest of the deck is unaffected
            self.assertTrue((Path(d) / "flightdeck" / "cockpit.md").exists())
            self.assertTrue((Path(d) / "flightdeck" / "landed").is_dir())

    def test_refuses_if_deck_already_exists(self):
        with tempfile.TemporaryDirectory() as d:
            init(d, name="x", user="x", date="2026-06-03", focus="f", next_item="n")
            with self.assertRaises(FileExistsError):
                init(d, name="x", user="x", date="2026-06-03", focus="f", next_item="n")

    def test_main_writes_deck(self):
        with tempfile.TemporaryDirectory() as d:
            rc = main([d, "--name", "p", "--user", "u", "--date", "2026-06-03",
                       "--focus", "f", "--next", "n"])
            self.assertEqual(rc, 0)
            self.assertTrue((Path(d) / "flightdeck" / "cockpit.md").exists())


if __name__ == "__main__":
    unittest.main()
