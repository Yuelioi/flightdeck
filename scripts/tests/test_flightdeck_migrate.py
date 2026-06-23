"""Tests for flightdeck_migrate.py — the one-time 3.0 → new-form deck migrator.

The migrator is a throwaway mechanical pass (mv/rm + frontmatter strip); the
semantic pass (routing-header synthesis, domain regroup, cockpit reshape) is the
AI's job, not this script. Python-only (no js parity — it's run-once-and-discard).
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import io
from contextlib import redirect_stdout

from flightdeck_migrate import classify, strip_frontmatter, plan_moves, migrate, main


def _run_main(argv):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = main(argv)
    return rc, out.getvalue()


def _write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _fixture_deck(d):
    """A representative 3.0 deck: one of each disposition + INDEX + untouchables."""
    deck = Path(d) / "flightdeck"
    _write(deck / "specs" / "2026-01-01-live-design.md", "---\nstatus: active\n---\n\n# Live\n")
    _write(deck / "specs" / "an-idea.md", "---\nstatus: idea\n---\n\n# Idea\n")
    _write(deck / "specs" / "2025-12-01-old-design.md", "---\nstatus: done\n---\n\n# Old\n")
    _write(deck / "plans" / "2026-01-02-live-plan.md", "---\nstatus: active\n---\n\n# Plan\n")
    _write(deck / "checklists" / "commits.md", "---\nstatus: active\n---\n\n# Commits\n")
    _write(deck / "checklists" / "INDEX.md", "# checklists INDEX\n")
    _write(deck / "incidents" / "INDEX.md", "# incidents INDEX\n")
    _write(deck / "archive" / "2025-11-01-buried.md", "---\nstatus: done\n---\n\n# Buried\n")
    _write(deck / "cockpit.md", "# Cockpit\n")
    _write(deck / "rules.md", "---\nversion: 3.0\n---\n\n## House rules\n")
    return deck


def _by_src_name(moves):
    return {m.src.name + "|" + str(m.src.parent.name): m for m in moves}


class PlanMovesTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.deck = _fixture_deck(self._td.name)
        self.cold = Path(self._td.name) / "cold"
        self.moves = plan_moves(self.deck, self.cold, "proj")
        self.idx = _by_src_name(self.moves)

    def tearDown(self):
        self._td.cleanup()

    def test_active_spec_moves_to_work(self):
        m = self.idx["2026-01-01-live-design.md|specs"]
        self.assertEqual(m.action, "move")
        self.assertEqual(m.dst, self.deck / "work" / "2026-01-01-live-design.md")

    def test_idea_spec_moves_to_cold_ideas(self):
        m = self.idx["an-idea.md|specs"]
        self.assertEqual(m.dst, self.cold / "projects" / "proj" / "ideas" / "an-idea.md")

    def test_done_spec_moves_to_cold_archive(self):
        m = self.idx["2025-12-01-old-design.md|specs"]
        self.assertEqual(m.dst, self.cold / "projects" / "proj" / "archive" / "2025-12-01-old-design.md")

    def test_active_plan_moves_to_work(self):
        m = self.idx["2026-01-02-live-plan.md|plans"]
        self.assertEqual(m.dst, self.deck / "work" / "2026-01-02-live-plan.md")

    def test_knowledge_file_moves_to_knowledge(self):
        m = self.idx["commits.md|checklists"]
        self.assertEqual(m.dst, self.deck / "knowledge" / "commits.md")

    def test_archived_file_moves_to_cold_archive(self):
        m = self.idx["2025-11-01-buried.md|archive"]
        self.assertEqual(m.dst, self.cold / "projects" / "proj" / "archive" / "2025-11-01-buried.md")

    def test_index_files_are_deleted(self):
        for key in ("INDEX.md|checklists", "INDEX.md|incidents"):
            self.assertEqual(self.idx[key].action, "delete")
            self.assertIsNone(self.idx[key].dst)

    def test_cockpit_and_rules_are_untouched(self):
        names = {m.src.name for m in self.moves}
        self.assertNotIn("cockpit.md", names)
        self.assertNotIn("rules.md", names)


class ClassifyTest(unittest.TestCase):
    def test_active_spec_goes_to_work(self):
        self.assertEqual(classify("specs", "active"), "work")

    def test_idea_spec_goes_to_cold_ideas(self):
        self.assertEqual(classify("specs", "idea"), "cold-ideas")

    def test_done_spec_goes_to_cold_archive(self):
        self.assertEqual(classify("specs", "done"), "cold-archive")

    def test_active_plan_goes_to_work(self):
        self.assertEqual(classify("plans", "active"), "work")

    def test_done_plan_goes_to_cold_archive(self):
        self.assertEqual(classify("plans", "done"), "cold-archive")

    def test_knowledge_folders_go_to_knowledge_regardless_of_status(self):
        for folder in ("checklists", "docs", "incidents", "references"):
            self.assertEqual(classify(folder, "active"), "knowledge")

    def test_archive_folder_goes_to_cold_archive(self):
        self.assertEqual(classify("archive", "done"), "cold-archive")


class StripFrontmatterTest(unittest.TestCase):
    def test_strips_leading_yaml_block(self):
        text = "---\nstatus: active\nsummary: hi\n---\n\n# Title\n\nbody line\n"
        self.assertEqual(strip_frontmatter(text), "# Title\n\nbody line\n")

    def test_no_frontmatter_returned_unchanged(self):
        text = "# Title\n\nbody only, no frontmatter\n"
        self.assertEqual(strip_frontmatter(text), text)

    def test_body_with_its_own_triple_dash_is_preserved(self):
        # a horizontal rule inside the body must survive — only the FIRST block goes
        text = "---\nstatus: done\n---\n\nintro\n\n---\n\nafter rule\n"
        self.assertEqual(strip_frontmatter(text), "intro\n\n---\n\nafter rule\n")

    def test_does_not_treat_leading_hr_as_frontmatter(self):
        # a doc that opens with a horizontal rule (no key:val) is not frontmatter
        text = "---\n\njust a rule then text\n"
        self.assertEqual(strip_frontmatter(text), text)


class MigrateApplyTest(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.deck = _fixture_deck(self._td.name)
        self.cold = Path(self._td.name) / "cold"
        migrate(self.deck, self.cold, "proj", check=False)

    def tearDown(self):
        self._td.cleanup()

    def test_active_spec_landed_in_work_with_frontmatter_stripped(self):
        dst = self.deck / "work" / "2026-01-01-live-design.md"
        self.assertTrue(dst.exists())
        text = dst.read_text(encoding="utf-8")
        self.assertNotIn("status:", text)
        self.assertNotIn("---", text)
        self.assertIn("# Live", text)

    def test_source_removed_after_move(self):
        self.assertFalse((self.deck / "specs" / "2026-01-01-live-design.md").exists())

    def test_idea_spec_landed_in_cold_ideas(self):
        self.assertTrue((self.cold / "projects" / "proj" / "ideas" / "an-idea.md").exists())

    def test_knowledge_file_landed_in_knowledge(self):
        self.assertTrue((self.deck / "knowledge" / "commits.md").exists())

    def test_index_files_deleted(self):
        self.assertFalse((self.deck / "checklists" / "INDEX.md").exists())
        self.assertFalse((self.deck / "incidents" / "INDEX.md").exists())

    def test_cockpit_and_rules_untouched(self):
        self.assertTrue((self.deck / "cockpit.md").exists())
        rules = (self.deck / "rules.md").read_text(encoding="utf-8")
        self.assertIn("version: 3.0", rules)  # rules.md is NOT stripped (not moved)


class MigrateDryRunTest(unittest.TestCase):
    def test_check_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _fixture_deck(d)
            cold = Path(d) / "cold"
            moves = migrate(deck, cold, "proj", check=True)
            # plan still returned, but the tree is untouched
            self.assertTrue(moves)
            self.assertTrue((deck / "specs" / "2026-01-01-live-design.md").exists())
            self.assertTrue((deck / "checklists" / "INDEX.md").exists())
            self.assertFalse((deck / "work").exists())
            self.assertFalse(cold.exists())


class ScriptRunTest(unittest.TestCase):
    """Run the module as a real script — catches definition-order / __main__ bugs
    that import-based tests structurally cannot (functions are all registered on
    import, but a misplaced `if __name__ == '__main__'` guard fails only as a script)."""

    def test_runs_as_script_without_nameerror(self):
        import subprocess
        script = Path(__file__).resolve().parent.parent / "flightdeck_migrate.py"
        with tempfile.TemporaryDirectory() as d:
            deck = _fixture_deck(d)
            r = subprocess.run(
                [sys.executable, str(script), str(deck), "--check",
                 "--cold-root", str(Path(d) / "cold"), "--project", "proj"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("Traceback", r.stderr)
            self.assertIn("would move", r.stdout)


class MainCliTest(unittest.TestCase):
    def test_check_prints_plan_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _fixture_deck(d)
            cold = Path(d) / "cold"
            rc, out = _run_main([str(deck), "--check", "--cold-root", str(cold), "--project", "proj"])
            self.assertEqual(rc, 0)
            self.assertIn("would move", out)
            self.assertIn("would delete", out)
            self.assertIn("dry-run", out)
            self.assertFalse((deck / "work").exists())
            self.assertTrue((deck / "specs" / "2026-01-01-live-design.md").exists())

    def test_apply_moves_for_real(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _fixture_deck(d)
            cold = Path(d) / "cold"
            rc, out = _run_main([str(deck), "--cold-root", str(cold), "--project", "proj"])
            self.assertEqual(rc, 0)
            self.assertNotIn("would", out)
            self.assertTrue((deck / "work" / "2026-01-01-live-design.md").exists())

    def test_project_defaults_to_deck_parent_name(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _fixture_deck(d)
            cold = Path(d) / "cold"
            _run_main([str(deck), "--cold-root", str(cold)])
            parent = deck.resolve().parent.name
            self.assertTrue((cold / "projects" / parent / "ideas" / "an-idea.md").exists())


if __name__ == "__main__":
    unittest.main()
