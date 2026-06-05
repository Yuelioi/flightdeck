import sys
import tempfile
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_init import init, main

# 当前可验证的文件夹（docs 由 init 内联建，其他来自 scaffolds/full 现有结构）
FOLDERS_CURRENT = ["specs", "plans", "incidents", "checklists", "docs"]
# Task 5.1 完成后才存在的文件夹（scaffolds/full 重命名 charts→references）
FOLDERS_POST_51 = ["references"]

# NOTE: scaffolds/full 尚未重命名（Task 5.1 负责），目前仍含 charts/ 和 landed/。
# init() 已内联建 docs/，但 references/ 依赖 Task 5.1 完成后才存在。


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
            # full layout + 3-file contract present (current: charts/ still exists from scaffold)
            for f in FOLDERS_CURRENT:
                self.assertTrue((deck / f / "INDEX.md").exists(), f"missing {f}/INDEX.md")
            self.assertTrue((deck / "INDEX.md").exists())
            self.assertTrue((deck / "rules.md").exists())
            # no-git deck keeps HISTORY.md (archive/ is 3.0 name; landed/ until Task 5.1)
            self.assertTrue(
                (deck / "archive" / "HISTORY.md").exists()
                or (deck / "landed" / "HISTORY.md").exists(),
                "HISTORY.md should exist in archive/ or landed/ for no-git deck",
            )
            # rules.md copied verbatim (a scaffold token survives — not re-authored)
            rules = (deck / "rules.md").read_text(encoding="utf-8")
            self.assertIn("status: don't auto start", rules)  # cheat-sheet phrase, scaffold-only
            self.assertNotIn("disabled_folders", rules)  # removed in the autonomy-convergence pass

    @pytest.mark.xfail(
        reason="Task 5.1 未完成：scaffolds/full 仍含 charts/ 而非 references/，重命名后此测试应转绿",
        strict=True,
    )
    def test_references_folder_exists_after_task51(self):
        """Task 5.1 完成（scaffolds/full charts→references）后此测试应转绿。"""
        with tempfile.TemporaryDirectory() as d:
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            deck = Path(d) / "flightdeck"
            for f in FOLDERS_POST_51:
                self.assertTrue((deck / f / "INDEX.md").exists(), f"missing {f}/INDEX.md")
            # charts/ should not exist once Task 5.1 renames it
            self.assertFalse((deck / "charts").exists(), "charts/ should be gone after Task 5.1")

    def test_no_git_keeps_history(self):
        # target without .git → no-git deck → HISTORY.md is the history substrate, kept
        # archive/ is the 3.0 name; landed/ is the scaffold name until Task 5.1 renames it
        with tempfile.TemporaryDirectory() as d:
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            deck = Path(d) / "flightdeck"
            history_exists = (
                (deck / "archive" / "HISTORY.md").exists()
                or (deck / "landed" / "HISTORY.md").exists()
            )
            self.assertTrue(history_exists, "HISTORY.md should exist for no-git deck")

    def test_git_deck_drops_history(self):
        # target with .git → git log is the history → the copied HISTORY.md is removed
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".git").mkdir()
            init(d, name="p", user="u", date="2026-06-03", focus="f", next_item="n")
            deck = Path(d) / "flightdeck"
            self.assertFalse((deck / "archive" / "HISTORY.md").exists())
            self.assertFalse((deck / "landed" / "HISTORY.md").exists())
            # the rest of the deck is unaffected
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
