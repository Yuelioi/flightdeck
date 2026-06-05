import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import flightdeck_index
from flightdeck_index import (
    parse_frontmatter,
    format_row,
    regen_folder_index,
    folder_summary,
    replace_auto_block,
    imported_summary,
    regen_root_index,
    regen_cockpit_inprogress,
    main,
    STATUS_ORDER,
    SUMMARY_KINDS,
    KNOWLEDGE_KINDS,
    FOLDER_ORDER,
)

DASH = "—"  # em dash, the INDEX row delimiter


class ModelConstantsTest(unittest.TestCase):
    def test_status_order_is_four_states(self):
        self.assertEqual(STATUS_ORDER, ["idea", "active", "done", "scrapped"])

    def test_summary_kinds(self):
        self.assertEqual(SUMMARY_KINDS, {"specs", "plans"})

    def test_knowledge_kinds_includes_docs(self):
        self.assertEqual(flightdeck_index.KNOWLEDGE_KINDS, {"checklists", "incidents", "docs"})

    def test_imported_kinds_is_references(self):
        self.assertEqual(flightdeck_index.IMPORTED_KINDS, {"references"})

    def test_folder_order_mainstream_names(self):
        self.assertEqual(
            FOLDER_ORDER, ["specs", "plans", "incidents", "checklists", "docs", "references"]
        )
        self.assertNotIn("charts", FOLDER_ORDER)
        self.assertNotIn("landed", FOLDER_ORDER)

    def test_nestable_kinds_are_knowledge(self):
        self.assertEqual(
            flightdeck_index.NESTABLE_KINDS, {"incidents", "checklists", "docs", "references"}
        )


class ParseFrontmatterTest(unittest.TestCase):
    def test_extracts_simple_key_value(self):
        text = "---\nstatus: active\nsummary: hello world\n---\n# Body\n"
        fm = parse_frontmatter(text)
        self.assertEqual(fm["status"], "active")
        self.assertEqual(fm["summary"], "hello world")


class FormatRowTest(unittest.TestCase):
    def test_summary_kind_uses_status_then_summary(self):
        fm = {"status": "active", "summary": "hello"}
        row = format_row("specs", "foo.md", fm)
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

    def test_incident_recur_shown_when_above_one(self):
        fm = {
            "status": "active",
            "when_to_read": "before X",
            "applies_to": "[a]",
            "recurrences": "3",
        }
        row = format_row("incidents", "foo.md", fm)
        self.assertEqual(
            row,
            f"- [foo.md](foo.md) {DASH} active {DASH} "
            f"when_to_read: before X {DASH} applies_to: [a] {DASH} recur: 3",
        )

    def test_incident_recur_omitted_when_one_or_absent(self):
        base = {"status": "active", "when_to_read": "before X", "applies_to": "[a]"}
        self.assertNotIn("recur:", format_row("incidents", "foo.md", base))
        self.assertNotIn("recur:", format_row("incidents", "foo.md", {**base, "recurrences": "1"}))

    def test_checklists_never_show_recur(self):
        fm = {
            "status": "active",
            "when_to_read": "before X",
            "applies_to": "[a]",
            "recurrences": "3",
        }
        self.assertNotIn("recur:", format_row("checklists", "foo.md", fm))

    def test_debriefs_kind_is_no_longer_known(self):
        # model-v4 dropped debriefs/ — format_row must reject it.
        with self.assertRaises(ValueError):
            format_row("debriefs", "foo.md", {"status": "active"})

    def test_summary_kind_missing_summary_does_not_raise(self):
        # 缺 summary 的 workflow 文件不应让 regen 崩；用可见哨兵占位。
        row = format_row("specs", "foo.md", {"status": "active"})
        self.assertIn("foo.md", row)
        self.assertIn("⚠", row)

    def test_summary_kind_missing_status_does_not_raise(self):
        row = format_row("specs", "foo.md", {"summary": "x"})
        self.assertIn("foo.md", row)


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


class SpecsGroupingTest(unittest.TestCase):
    def _specs(self, d):
        folder = Path(d) / "specs"
        folder.mkdir()
        # idea: no date prefix, timeless
        (folder / "zeta-idea.md").write_text(
            "---\nstatus: idea\nsummary: z idea\n---\n", encoding="utf-8"
        )
        (folder / "alpha-idea.md").write_text(
            "---\nstatus: idea\nsummary: a idea\n---\n", encoding="utf-8"
        )
        # active / done: dated
        (folder / "2026-06-01-old-active.md").write_text(
            "---\nstatus: active\nsummary: old active\n---\n", encoding="utf-8"
        )
        (folder / "2026-06-03-new-done.md").write_text(
            "---\nstatus: done\nsummary: new done\n---\n", encoding="utf-8"
        )
        # scrapped: physically present but must not appear
        (folder / "2026-05-01-rejected.md").write_text(
            "---\nstatus: scrapped\nsummary: rejected\n---\n", encoding="utf-8"
        )
        (folder / "INDEX.md").write_text("stale\n", encoding="utf-8")
        return folder

    def test_specs_index_groups_by_status_with_scrapped_in_own_section(self):
        with tempfile.TemporaryDirectory() as d:
            folder = self._specs(d)
            expected = (
                "<!-- AUTO:specs -->\n"
                "### 待启动（idea）\n"
                f"- [alpha-idea.md](alpha-idea.md) {DASH} idea {DASH} a idea\n"
                f"- [zeta-idea.md](zeta-idea.md) {DASH} idea {DASH} z idea\n"
                "\n"
                "### 进行中·完成（active·done）\n"
                f"- [2026-06-03-new-done.md](2026-06-03-new-done.md) {DASH} done {DASH} new done\n"
                f"- [2026-06-01-old-active.md](2026-06-01-old-active.md) {DASH} active {DASH} old active\n"
                "\n"
                "### 已否决（scrapped）\n"
                f"- [2026-05-01-rejected.md](2026-05-01-rejected.md) {DASH} scrapped {DASH} rejected\n"
                "<!-- /AUTO -->"
            )
            self.assertEqual(regen_folder_index(folder), expected)

    def test_specs_index_omits_empty_idea_group(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "specs"
            folder.mkdir()
            (folder / "2026-06-01-a.md").write_text(
                "---\nstatus: active\nsummary: a\n---\n", encoding="utf-8"
            )
            out = regen_folder_index(folder)
            self.assertNotIn("待启动", out)
            self.assertIn("进行中·完成（active·done）", out)


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
            (deck / "plans").mkdir()
            (deck / "plans" / "b.md").write_text(
                "---\nstatus: active\nsummary: y\n---\n", encoding="utf-8"
            )
            # incidents/checklists/charts absent -> skipped
            expected = (
                "<!-- AUTO:root -->\n"
                f"- specs/ {DASH} 1 done\n"
                f"- plans/ {DASH} 1 active\n"
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

    def test_specs_scrapped_excluded_from_root_count(self):
        # scrapped specs stay on disk but are invisible in the specs INDEX, so
        # they must not be counted in the root summary either — the root count
        # must equal the number of visible INDEX rows.
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "specs"
            folder.mkdir()
            (folder / "2026-06-01-a.md").write_text(
                "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
            )
            (folder / "2026-05-01-r.md").write_text(
                "---\nstatus: scrapped\nsummary: r\n---\n", encoding="utf-8"
            )
            (folder / "INDEX.md").write_text("ignored", encoding="utf-8")
            # 1 visible (active); scrapped excluded
            self.assertEqual(folder_summary(folder), "1 active")

    def test_non_specs_folder_counts_all_statuses(self):
        # the scrapped exclusion is specs-only; other folders count everything.
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "plans"
            folder.mkdir()
            (folder / "a.md").write_text(
                "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
            )
            (folder / "b.md").write_text(
                "---\nstatus: scrapped\nsummary: y\n---\n", encoding="utf-8"
            )
            self.assertEqual(folder_summary(folder), "2 (1 active, 1 scrapped)")

    def test_empty_folder_is_zero(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "specs"
            folder.mkdir()
            (folder / "INDEX.md").write_text("ignored", encoding="utf-8")
            self.assertEqual(folder_summary(folder), "0")

    def test_imported_summary_counts_imported_entries(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "references"
            folder.mkdir()
            (folder / "INDEX.md").write_text(
                "# references\n<!-- AUTO:references -->\n"
                f"- [a/](a/) {DASH} 1 project imported {DASH} desc\n"
                "<!-- /AUTO -->\n",
                encoding="utf-8",
            )
            self.assertEqual(imported_summary(folder), "1 project imported")


class CockpitInprogressTest(unittest.TestCase):
    def _deck(self, d):
        deck = Path(d)
        specs = deck / "specs"
        specs.mkdir()
        plans = deck / "plans"
        plans.mkdir()
        return deck, specs, plans

    def test_derives_active_rows_from_specs_and_plans(self):
        with tempfile.TemporaryDirectory() as d:
            deck, specs, plans = self._deck(d)
            (specs / "2026-06-01-s.md").write_text(
                "---\nstatus: active\nsummary: spec work\n---\n", encoding="utf-8"
            )
            (specs / "idea.md").write_text(
                "---\nstatus: idea\nsummary: not yet\n---\n", encoding="utf-8"
            )
            (plans / "2026-06-02-p.md").write_text(
                "---\nstatus: active\nsummary: plan work\n---\n", encoding="utf-8"
            )
            (plans / "2026-05-01-done.md").write_text(
                "---\nstatus: done\nsummary: finished\n---\n", encoding="utf-8"
            )
            expected = (
                "<!-- AUTO:inprogress -->\n"
                f"- [2026-06-01-s.md](specs/2026-06-01-s.md) {DASH} spec work\n"
                f"- [2026-06-02-p.md](plans/2026-06-02-p.md) {DASH} plan work\n"
                "<!-- /AUTO -->"
            )
            self.assertEqual(regen_cockpit_inprogress(deck), expected)

    def test_empty_when_no_active(self):
        with tempfile.TemporaryDirectory() as d:
            deck, specs, plans = self._deck(d)
            (specs / "idea.md").write_text(
                "---\nstatus: idea\nsummary: not yet\n---\n", encoding="utf-8"
            )
            expected = "<!-- AUTO:inprogress -->\n\n<!-- /AUTO -->"
            self.assertEqual(regen_cockpit_inprogress(deck), expected)

    def test_note_appended_to_row(self):
        with tempfile.TemporaryDirectory() as d:
            deck, specs, plans = self._deck(d)
            (specs / "2026-06-01-s.md").write_text(
                "---\nstatus: active\nsummary: spec work\nnote: 等迁移定稿\n---\n",
                encoding="utf-8",
            )
            expected = (
                "<!-- AUTO:inprogress -->\n"
                f"- [2026-06-01-s.md](specs/2026-06-01-s.md) {DASH} spec work {DASH} [note: 等迁移定稿]\n"
                "<!-- /AUTO -->"
            )
            self.assertEqual(regen_cockpit_inprogress(deck), expected)


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


class CockpitWiredIntoMainTest(unittest.TestCase):
    def test_main_regenerates_cockpit_inprogress(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            specs = deck / "specs"
            specs.mkdir()
            (specs / "2026-06-01-a.md").write_text(
                "---\nstatus: active\nsummary: real work\n---\n", encoding="utf-8"
            )
            (specs / "INDEX.md").write_text(
                "# specs\n\n<!-- AUTO:specs -->\nstale\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            (deck / "INDEX.md").write_text(
                "# root\n\n<!-- AUTO:root -->\nstale\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            (deck / "cockpit.md").write_text(
                "# Cockpit\n\n## 进行中\n\n<!-- AUTO:inprogress -->\nSTALE\n<!-- /AUTO -->\n\n## 下一步\n",
                encoding="utf-8",
            )
            self.assertEqual(main([str(deck), "--check"]), 1)
            self.assertEqual(main([str(deck)]), 0)
            cockpit = (deck / "cockpit.md").read_text(encoding="utf-8")
            self.assertNotIn("STALE", cockpit)
            self.assertIn("real work", cockpit)
            self.assertIn("## 下一步", cockpit)  # hand region preserved


class VersionGuardTest(unittest.TestCase):
    def _deck_with_version(self, root, version):
        deck = Path(root)
        (deck / "rules.md").write_text(
            f"---\nversion: {version}\n---\n", encoding="utf-8"
        )
        specs = deck / "specs"
        specs.mkdir()
        (specs / "a.md").write_text(
            "---\nstatus: done\nsummary: x\n---\n", encoding="utf-8"
        )
        (specs / "INDEX.md").write_text(
            "# s\n\n<!-- AUTO:specs -->\nOLD\n<!-- /AUTO -->\n", encoding="utf-8"
        )
        (deck / "INDEX.md").write_text(
            "# r\n\n<!-- AUTO:root -->\nOLD\n<!-- /AUTO -->\n", encoding="utf-8"
        )
        return deck

    def test_refuses_and_writes_nothing_on_version_mismatch(self):
        # the bundled MIGRATION.md current is 3.0; a 2.2 deck must be refused
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck_with_version(d, "2.2")
            self.assertEqual(main([str(deck)]), 2)
            self.assertIn("OLD", (deck / "specs" / "INDEX.md").read_text(encoding="utf-8"))

    def test_force_bypasses_version_guard(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck_with_version(d, "2.2")
            self.assertEqual(main([str(deck), "--force"]), 0)
            self.assertNotIn("OLD", (deck / "specs" / "INDEX.md").read_text(encoding="utf-8"))

    def test_matching_version_proceeds(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck_with_version(d, "3.0")
            self.assertEqual(main([str(deck)]), 0)
            self.assertNotIn("OLD", (deck / "specs" / "INDEX.md").read_text(encoding="utf-8"))


class LayoutVerdictTest(unittest.TestCase):
    def _deck(self, root, version="3.0"):
        deck = Path(root)
        (deck / "rules.md").write_text(
            f"---\nversion: {version}\n---\n", encoding="utf-8"
        )
        specs = deck / "specs"
        specs.mkdir()
        (specs / "2026-06-01-a.md").write_text(
            "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
        )
        (deck / "cockpit.md").write_text(
            "# Cockpit\n## 进行中\n<!-- AUTO:inprogress -->\n\n<!-- /AUTO -->\n## 下一步\n",
            encoding="utf-8",
        )
        return deck

    def test_sketches_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "sketches").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_debriefs_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "debriefs").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_retired_status_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "specs" / "2026-06-02-b.md").write_text(
                "---\nstatus: awaiting-review\nsummary: y\n---\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_cockpit_missing_auto_region_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "cockpit.md").write_text(
                "# Cockpit\n## Next session\n- do thing\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_version_below_need_entry_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="2.3")  # 2.3 < 3.0（need 项）
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_no_version_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "rules.md").write_text("---\n---\n", encoding="utf-8")  # 无 version
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_legacy_charts_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "charts").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_legacy_landed_dir_is_structural(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "landed").mkdir()
            self.assertEqual(flightdeck_index.layout_verdict(deck), "structural-behind")

    def test_current_version_clean_is_current(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="3.0")
            self.assertEqual(flightdeck_index.layout_verdict(deck), "current")

    def test_compatible_behind_logic(self):
        # 直接验证比对逻辑，不依赖真实 MIGRATION
        self.assertEqual(
            flightdeck_index._classify_version("3.0", "3.1", ["2.2", "3.0"]),
            "compatible-behind",
        )
        self.assertEqual(
            flightdeck_index._classify_version("2.5", "3.0", ["2.2", "3.0"]),
            "structural-behind",
        )
        self.assertEqual(
            flightdeck_index._classify_version("3.0", "3.0", ["2.2", "3.0"]),
            "current",
        )
        self.assertEqual(
            flightdeck_index._classify_version(None, "3.0", ["2.2", "3.0"]),
            "structural-behind",
        )

    def test_missing_summary_on_current_deck_is_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="3.0")
            (deck / "specs" / "2026-06-02-bad.md").write_text(
                "---\nstatus: active\n---\n", encoding="utf-8"  # 缺 summary
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "malformed")

    def test_scrapped_missing_summary_not_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d, version="3.0")
            (deck / "specs" / "2026-05-01-r.md").write_text(
                "---\nstatus: scrapped\n---\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.layout_verdict(deck), "current")


class VerdictCliTest(unittest.TestCase):
    def test_verdict_flag_prints_and_writes_nothing(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "rules.md").write_text("---\nversion: 3.0\n---\n", encoding="utf-8")
            specs = deck / "specs"
            specs.mkdir()
            (specs / "2026-06-01-a.md").write_text(
                "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
            )
            (deck / "cockpit.md").write_text(
                "## 进行中\n<!-- AUTO:inprogress -->\n\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--verdict"])
            self.assertEqual(rc, 0)
            self.assertIn("current", buf.getvalue().strip())
            # 只读：不应创建 INDEX.md
            self.assertFalse((deck / "INDEX.md").exists())


class RootIndexDocsTest(unittest.TestCase):
    def _deck(self, root):
        deck = Path(root)
        for k in ("specs", "plans", "incidents", "checklists", "docs", "references"):
            (deck / k).mkdir()
        (deck / "docs" / "arch.md").write_text(
            "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
            encoding="utf-8",
        )
        (deck / "references" / "INDEX.md").write_text(
            "# references\n<!-- AUTO:references -->\n- [rfc.md](rfc.md)\n<!-- /AUTO -->\n", encoding="utf-8"
        )
        (deck / "INDEX.md").write_text(
            "# INDEX\n<!-- AUTO:root -->\n\n<!-- /AUTO -->\n", encoding="utf-8"
        )
        return deck

    def test_root_has_docs_status_row_and_references_imported_row(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            block = flightdeck_index.regen_root_index(deck)
            self.assertIn("docs/ — 1 active", block)
            self.assertIn("references/ — 1 project imported", block)


class SpecsScrappedGroupTest(unittest.TestCase):
    def test_scrapped_listed_in_own_group(self):
        with tempfile.TemporaryDirectory() as d:
            specs = Path(d) / "specs"
            specs.mkdir()
            (specs / "idea-x.md").write_text("---\nstatus: idea\nsummary: i\n---\n", encoding="utf-8")
            (specs / "2026-06-01-a.md").write_text("---\nstatus: active\nsummary: a\n---\n", encoding="utf-8")
            (specs / "2026-05-01-dead.md").write_text("---\nstatus: scrapped\nsummary: d\n---\n", encoding="utf-8")
            block = flightdeck_index.regen_folder_index(specs)
            self.assertIn("### 待启动（idea）", block)
            self.assertIn("### 进行中·完成（active·done）", block)
            self.assertIn("### 已否决（scrapped）", block)
            self.assertIn("2026-05-01-dead.md", block)


class ArchivableDoneTest(unittest.TestCase):
    def _deck(self, root):
        deck = Path(root)
        (deck / "specs").mkdir()
        (deck / "plans").mkdir()
        return deck

    def test_done_spec_with_active_plan_implements_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "specs" / "2026-06-01-a.md").write_text("---\nstatus: done\nsummary: a\n---\n", encoding="utf-8")
            (deck / "plans" / "2026-06-02-p.md").write_text(
                "---\nstatus: active\nsummary: p\nimplements: specs/2026-06-01-a.md\n---\n", encoding="utf-8"
            )
            self.assertEqual(flightdeck_index.archivable_done(deck), [])

    def test_done_spec_with_no_active_inbound_is_archivable(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "specs" / "2026-06-01-a.md").write_text("---\nstatus: done\nsummary: a\n---\n", encoding="utf-8")
            (deck / "plans" / "2026-06-02-p.md").write_text(
                "---\nstatus: done\nsummary: p\nimplements: specs/2026-06-01-a.md\n---\n", encoding="utf-8"
            )
            self.assertEqual(
                flightdeck_index.archivable_done(deck),
                ["plans/2026-06-02-p.md", "specs/2026-06-01-a.md"],
            )


class ArchivableCliTest(unittest.TestCase):
    def test_archivable_flag_prints_paths_writes_nothing(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "2026-06-01-a.md").write_text("---\nstatus: done\nsummary: a\n---\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--archivable"])
            self.assertEqual(rc, 0)
            self.assertIn("specs/2026-06-01-a.md", buf.getvalue())
            self.assertFalse((deck / "INDEX.md").exists())


class NestedIndexTest(unittest.TestCase):
    def test_top_index_lists_areas_with_purpose_and_date(self):
        with tempfile.TemporaryDirectory() as d:
            docs = Path(d) / "docs"
            (docs / "runtime").mkdir(parents=True)
            (docs / "runtime" / "INDEX.md").write_text(
                "---\npurpose: 运行时子系统\nlast_updated: 2026-06-05\n---\n"
                "# docs/runtime\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            (docs / "runtime" / "loop.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
                encoding="utf-8",
            )
            (docs / "INDEX.md").write_text("# docs\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            top = flightdeck_index.regen_folder_index(docs)
            self.assertIn("[runtime/](runtime/INDEX.md)", top)
            self.assertIn("运行时子系统", top)
            self.assertIn("2026-06-05", top)
            area = flightdeck_index.regen_folder_index(docs / "runtime")
            self.assertIn("loop.md", area)

    def test_flat_docs_without_subdirs_behaves_flat(self):
        with tempfile.TemporaryDirectory() as d:
            docs = Path(d) / "docs"
            docs.mkdir()
            (docs / "arch.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
                encoding="utf-8",
            )
            (docs / "INDEX.md").write_text("# docs\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            block = flightdeck_index.regen_folder_index(docs)
            self.assertIn("arch.md", block)
            self.assertNotIn("INDEX.md](", block)


class MainMissingAreaIndexTest(unittest.TestCase):
    def test_area_with_md_but_no_index_does_not_crash_main(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "rules.md").write_text("---\nversion: 3.0\n---\n", encoding="utf-8")
            area = deck / "docs" / "runtime"
            area.mkdir(parents=True)
            # area 有 .md 但**没有** INDEX.md
            (area / "loop.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
                encoding="utf-8",
            )
            (deck / "docs" / "INDEX.md").write_text("# docs\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            (deck / "INDEX.md").write_text("# INDEX\n<!-- AUTO:root -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck)])          # 默认 regen，不应崩
            # 缺失的 area INDEX 被新建，且含 AUTO 块与该文件行
            self.assertTrue((area / "INDEX.md").is_file())
            self.assertIn("loop.md", (area / "INDEX.md").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0)

    def test_area_missing_index_reported_as_drift_under_check(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "rules.md").write_text("---\nversion: 3.0\n---\n", encoding="utf-8")
            area = deck / "docs" / "runtime"
            area.mkdir(parents=True)
            (area / "loop.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-05\nsummary: s\n---\n",
                encoding="utf-8",
            )
            (deck / "docs" / "INDEX.md").write_text("# docs\n<!-- AUTO:docs -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            (deck / "INDEX.md").write_text("# INDEX\n<!-- AUTO:root -->\n\n<!-- /AUTO -->\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--check"])   # 只读，不应崩
            self.assertEqual(rc, 1)                  # 有 drift
            self.assertFalse((area / "INDEX.md").is_file())  # --check 不写


class CockpitProjectionRobustnessTest(unittest.TestCase):
    """regen_cockpit_inprogress must not KeyError on an active workflow file
    missing `summary` — it renders the same sentinel format_row uses."""

    def test_active_spec_missing_summary_renders_sentinel_not_keyerror(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "2026-06-05-no-summary.md").write_text(
                "---\nstatus: active\nlast_updated: 2026-06-05\n---\n# No summary\n",
                encoding="utf-8",
            )
            block = regen_cockpit_inprogress(deck)   # 不应抛 KeyError
            self.assertIn("2026-06-05-no-summary.md", block)
            self.assertIn("summary 缺失", block)


class SignatureNormalizeTest(unittest.TestCase):
    def test_quoted_keys_preserved_distinct(self):
        from flightdeck_index import normalize_symptom
        self.assertNotEqual(
            normalize_symptom("KeyError: 'summary'"),
            normalize_symptom("KeyError: 'title'"),
        )

    def test_volatile_tokens_collapsed(self):
        from flightdeck_index import normalize_symptom
        # hex / uuid / 路径 / 行号 / 时间戳 / 长整数 归一后应相等
        a = normalize_symptom("boom at 0x7f3a2b1c /home/alice/p/foo.py line 42 id=123456")
        b = normalize_symptom("boom at 0x99887766 /home/bob/q/foo.py line 99 id=999999")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
