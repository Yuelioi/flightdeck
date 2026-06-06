import sys
import tempfile
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_init import init, main

# 全量文件夹列表（含 3.0 新结构：references 替代 charts，docs 正式加入）
FOLDERS = ["specs", "plans", "incidents", "checklists", "docs", "references"]


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
            # full layout + 2-file contract present
            for f in FOLDERS:
                self.assertTrue((deck / f / "INDEX.md").exists(), f"missing {f}/INDEX.md")
            self.assertTrue((deck / "INDEX.md").exists())
            self.assertTrue((deck / "rules.md").exists())
            # references/ exists, charts/ is gone
            self.assertTrue((deck / "references").exists(), "references/ should exist")
            self.assertFalse((deck / "charts").exists(), "charts/ should not exist")
            # no history-log file ships under any git mode (archive/ is created on demand)
            self.assertFalse(
                (deck / "archive" / "HISTORY.md").exists(),
                "HISTORY.md must never ship — archive/ files are the landing record",
            )
            # landed/ is gone (renamed to archive/ in scaffold)
            self.assertFalse((deck / "landed").exists(), "landed/ should not exist")
            # rules.md copied verbatim (a scaffold token survives — not re-authored)
            rules = (deck / "rules.md").read_text(encoding="utf-8")
            self.assertIn("status: don't auto start", rules)  # cheat-sheet phrase, scaffold-only
            self.assertNotIn("disabled_folders", rules)  # removed in the autonomy-convergence pass

    def test_references_folder_exists(self):
        """scaffold charts→references 完成后 references/INDEX.md 应存在。"""
        with tempfile.TemporaryDirectory() as d:
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            deck = Path(d) / "flightdeck"
            self.assertTrue((deck / "references" / "INDEX.md").exists(), "missing references/INDEX.md")
            self.assertFalse((deck / "charts").exists(), "charts/ should be gone")

    def test_docs_folder_exists(self):
        """scaffold 已含 docs/INDEX.md，新建 deck 应直接携带。"""
        with tempfile.TemporaryDirectory() as d:
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            deck = Path(d) / "flightdeck"
            self.assertTrue((deck / "docs" / "INDEX.md").exists(), "missing docs/INDEX.md")

    def test_no_history_log_under_any_git_mode(self):
        # flightdeck keeps no separate landing log — archive/ files are the record.
        # Neither a no-git target nor a git target ships HISTORY.md.
        for make_git in (False, True):
            with tempfile.TemporaryDirectory() as d:
                if make_git:
                    (Path(d) / ".git").mkdir()
                init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
                deck = Path(d) / "flightdeck"
                self.assertFalse(
                    (deck / "archive" / "HISTORY.md").exists(),
                    f"HISTORY.md must not ship (make_git={make_git})",
                )
                self.assertTrue((deck / "cockpit.md").exists())

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
