import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_index import (
    parse_frontmatter,
    format_row,
    regen_folder_index,
    folder_summary,
    replace_auto_block,
    charts_summary,
    regen_root_index,
    main,
)

DASH = "—"  # em dash, the INDEX row delimiter


class ParseFrontmatterTest(unittest.TestCase):
    def test_extracts_simple_key_value(self):
        text = "---\nstatus: active\nsummary: hello world\n---\n# Body\n"
        fm = parse_frontmatter(text)
        self.assertEqual(fm["status"], "active")
        self.assertEqual(fm["summary"], "hello world")


class FormatRowTest(unittest.TestCase):
    def test_summary_kind_uses_status_then_summary(self):
        fm = {"status": "active", "summary": "hello"}
        row = format_row("sketches", "foo.md", fm)
        self.assertEqual(row, f"- [foo.md](foo.md) {DASH} active {DASH} hello")

    def test_knowledge_kind_uses_when_to_read_and_applies_to(self):
        fm = {
            "status": "active",
            "when_to_read": "before X",
            "applies_to": "[a, b]",
        }
        row = format_row("incidents", "foo.md", fm)
        self.assertEqual(
            row,
            f"- [foo.md](foo.md) {DASH} active {DASH} "
            f"when_to_read: before X {DASH} applies_to: [a, b]",
        )

    def test_debriefs_kind_uses_reviewed_and_last_updated(self):
        fm = {
            "status": "active",
            "reviewed": "specs/x.md",
            "last_updated": "2026-06-02",
        }
        row = format_row("debriefs", "foo.md", fm)
        self.assertEqual(
            row,
            f"- [foo.md](foo.md) {DASH} active {DASH} "
            f"reviewed: specs/x.md {DASH} 2026-06-02",
        )


class RegenFolderIndexTest(unittest.TestCase):
    def test_regenerates_alphabetical_block_from_frontmatter(self):
        # Isolated fixture: the real deck's INDEX can drift from frontmatter,
        # so it is not a valid golden source — author files + expected output.
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "checklists"
            folder.mkdir()
            # written out of order to prove alphabetical sort by filename
            (folder / "bbb.md").write_text(
                "---\nstatus: active\nwhen_to_read: do b\napplies_to: [x]\n---\n",
                encoding="utf-8",
            )
            (folder / "aaa.md").write_text(
                "---\nstatus: active\nwhen_to_read: do a\napplies_to: [y]\n---\n",
                encoding="utf-8",
            )
            (folder / "INDEX.md").write_text("stale, must be ignored\n", encoding="utf-8")

            expected = (
                "<!-- AUTO:checklists -->\n"
                f"- [aaa.md](aaa.md) {DASH} active {DASH} when_to_read: do a {DASH} applies_to: [y]\n"
                f"- [bbb.md](bbb.md) {DASH} active {DASH} when_to_read: do b {DASH} applies_to: [x]\n"
                "<!-- /AUTO -->"
            )
            self.assertEqual(regen_folder_index(folder), expected)


class ReplaceAutoBlockTest(unittest.TestCase):
    def test_swaps_block_preserving_header_and_trailer(self):
        text = "# title\n\n<!-- AUTO:specs -->\nold row\n<!-- /AUTO -->\n\ntrailer\n"
        new = "<!-- AUTO:specs -->\nNEW row\n<!-- /AUTO -->"
        self.assertEqual(
            replace_auto_block(text, new),
            "# title\n\n<!-- AUTO:specs -->\nNEW row\n<!-- /AUTO -->\n\ntrailer\n",
        )


class RegenRootIndexTest(unittest.TestCase):
    def test_assembles_rows_in_folder_order_skipping_missing(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "a.md").write_text(
                "---\nstatus: done\nsummary: x\n---\n", encoding="utf-8"
            )
            (deck / "sketches").mkdir()
            (deck / "sketches" / "b.md").write_text(
                "---\nstatus: active\nsummary: y\n---\n", encoding="utf-8"
            )
            # plans/incidents/checklists/charts/debriefs absent -> skipped
            expected = (
                "<!-- AUTO:root -->\n"
                f"- specs/ {DASH} 1 done\n"
                f"- sketches/ {DASH} 1 active\n"
                "<!-- /AUTO -->"
            )
            self.assertEqual(regen_root_index(deck), expected)


class FolderSummaryTest(unittest.TestCase):
    def test_counts_and_uses_uniform_status(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "specs"
            folder.mkdir()
            (folder / "a.md").write_text(
                "---\nstatus: done\nsummary: x\n---\n", encoding="utf-8"
            )
            (folder / "b.md").write_text(
                "---\nstatus: done\nsummary: y\n---\n", encoding="utf-8"
            )
            (folder / "INDEX.md").write_text("ignored", encoding="utf-8")
            self.assertEqual(folder_summary(folder), "2 done")

    def test_mixed_status_breaks_down_in_lifecycle_order(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "specs"
            folder.mkdir()
            (folder / "a.md").write_text(
                "---\nstatus: done\nsummary: x\n---\n", encoding="utf-8"
            )
            (folder / "b.md").write_text(
                "---\nstatus: active\nsummary: y\n---\n", encoding="utf-8"
            )
            (folder / "c.md").write_text(
                "---\nstatus: done\nsummary: z\n---\n", encoding="utf-8"
            )
            # active before done (lifecycle order), per folder-semantics example
            self.assertEqual(folder_summary(folder), "3 (1 active, 2 done)")

    def test_empty_folder_is_zero(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "specs"
            folder.mkdir()
            (folder / "INDEX.md").write_text("ignored", encoding="utf-8")
            self.assertEqual(folder_summary(folder), "0")

    def test_charts_summary_counts_imported_entries(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "charts"
            folder.mkdir()
            (folder / "INDEX.md").write_text(
                "# charts\n<!-- AUTO:charts -->\n"
                f"- [a/](a/) {DASH} 1 project imported {DASH} desc\n"
                "<!-- /AUTO -->\n",
                encoding="utf-8",
            )
            self.assertEqual(charts_summary(folder), "1 project imported")


class MainCliTest(unittest.TestCase):
    def test_check_reports_drift_without_writing_then_write_fixes(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            specs = deck / "specs"
            specs.mkdir()
            (specs / "a.md").write_text(
                "---\nstatus: done\nsummary: real\n---\n", encoding="utf-8"
            )
            (specs / "INDEX.md").write_text(
                "# specs\n\n<!-- AUTO:specs -->\n"
                f"- [a.md](a.md) {DASH} done {DASH} STALE\n"
                "<!-- /AUTO -->\n",
                encoding="utf-8",
            )
            (deck / "INDEX.md").write_text(
                "# root\n\n<!-- AUTO:root -->\n"
                f"- specs/ {DASH} 1 done\n"
                "<!-- /AUTO -->\n",
                encoding="utf-8",
            )

            # --check: detects drift (exit 1) and writes nothing
            self.assertEqual(main([str(deck), "--check"]), 1)
            self.assertIn("STALE", (specs / "INDEX.md").read_text(encoding="utf-8"))

            # write: fixes the drift (exit 0)
            self.assertEqual(main([str(deck)]), 0)
            fixed = (specs / "INDEX.md").read_text(encoding="utf-8")
            self.assertIn("real", fixed)
            self.assertNotIn("STALE", fixed)

            # --check again: clean
            self.assertEqual(main([str(deck), "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
