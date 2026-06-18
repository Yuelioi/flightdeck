import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import flightdeck_index
from flightdeck_index import (
    parse_frontmatter,
    format_row,
    regen_folder_index,
    replace_auto_block,
    regen_cockpit_inprogress,
    main,
    STATUS_ORDER,
    SUMMARY_KINDS,
    KNOWLEDGE_KINDS,
    FOLDER_ORDER,
)

DASH = "—"  # em dash, the INDEX row delimiter


class ModelConstantsTest(unittest.TestCase):
    def test_status_order(self):
        self.assertEqual(STATUS_ORDER, ["idea", "active", "done"])

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
        (folder / "INDEX.md").write_text("stale\n", encoding="utf-8")
        return folder

    def test_specs_index_groups_by_status(self):
        with tempfile.TemporaryDirectory() as d:
            folder = self._specs(d)
            expected = (
                "<!-- AUTO:specs -->\n"
                "### Backlog (idea)\n"
                f"- [alpha-idea.md](alpha-idea.md) {DASH} idea {DASH} a idea\n"
                f"- [zeta-idea.md](zeta-idea.md) {DASH} idea {DASH} z idea\n"
                "\n"
                "### Active · Done\n"
                f"- [2026-06-03-new-done.md](2026-06-03-new-done.md) {DASH} done {DASH} new done\n"
                f"- [2026-06-01-old-active.md](2026-06-01-old-active.md) {DASH} active {DASH} old active\n"
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
            self.assertNotIn("Backlog", out)
            self.assertIn("Active · Done", out)


class ReplaceAutoBlockTest(unittest.TestCase):
    def test_swaps_block_preserving_header_and_trailer(self):
        text = "# title\n\n<!-- AUTO:specs -->\nold row\n<!-- /AUTO -->\n\ntrailer\n"
        new = "<!-- AUTO:specs -->\nNEW row\n<!-- /AUTO -->"
        self.assertEqual(
            replace_auto_block(text, new),
            "# title\n\n<!-- AUTO:specs -->\nNEW row\n<!-- /AUTO -->\n\ntrailer\n",
        )


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
            (deck / "cockpit.md").write_text(
                "# Cockpit\n\n## In Progress\n\n<!-- AUTO:inprogress -->\nSTALE\n<!-- /AUTO -->\n\n## Next\n",
                encoding="utf-8",
            )
            self.assertEqual(main([str(deck), "--check"]), 1)
            self.assertEqual(main([str(deck)]), 0)
            cockpit = (deck / "cockpit.md").read_text(encoding="utf-8")
            self.assertNotIn("STALE", cockpit)
            self.assertIn("real work", cockpit)
            self.assertIn("## Next", cockpit)  # hand region preserved


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

    def test_supersedes_edge_does_not_pin_target(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            (deck / "docs" / "new.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\nsupersedes: docs/old.md\n---\n# new\n",
                encoding="utf-8",
            )
            from flightdeck_index import _active_inbound_targets
            self.assertNotIn("docs/old.md", _active_inbound_targets(deck))

    def test_superseded_by_no_longer_pins(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            (deck / "docs" / "x.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\nsuperseded_by: docs/old.md\n---\n# x\n",
                encoding="utf-8",
            )
            from flightdeck_index import _active_inbound_targets
            self.assertNotIn("docs/old.md", _active_inbound_targets(deck))

    def test_archivable_includes_obsolete_knowledge(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "incidents").mkdir()
            for name, st in (("dead.md", "obsolete"), ("live.md", "active"), ("amber.md", "stale")):
                (deck / "incidents" / name).write_text(
                    f"---\nstatus: {st}\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# {name}\n",
                    encoding="utf-8",
                )
            from flightdeck_index import archivable_obsolete
            self.assertEqual(archivable_obsolete(deck), ["incidents/dead.md"])


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

    def test_archivable_cli_union_done_and_obsolete(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir(); (deck / "docs").mkdir()
            (deck / "specs" / "s.md").write_text("---\nstatus: done\nsummary: s\nlast_updated: 2026-06-07\n---\n# s\n", encoding="utf-8")
            (deck / "docs" / "d.md").write_text("---\nstatus: obsolete\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# d\n", encoding="utf-8")
            from flightdeck_index import archivable_done, archivable_obsolete
            union = sorted(set(archivable_done(deck)) | set(archivable_obsolete(deck)))
            self.assertIn("specs/s.md", union)
            self.assertIn("docs/d.md", union)


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


class SignatureFingerprintTest(unittest.TestCase):
    def test_same_after_normalize_same_fp(self):
        from flightdeck_index import signature_fingerprint
        self.assertEqual(
            signature_fingerprint("fail 0x7f3a", "KeyError"),
            signature_fingerprint("fail 0x99aa", "KeyError"),
        )

    def test_distinct_key_distinct_fp(self):
        from flightdeck_index import signature_fingerprint
        self.assertNotEqual(
            signature_fingerprint("KeyError: 'summary'", "KeyError"),
            signature_fingerprint("KeyError: 'title'", "KeyError"),
        )

    def test_where_not_in_fingerprint(self):
        # spec：where 不进主指纹（重构换 where 不应换指纹）
        from flightdeck_index import signature_fingerprint
        import inspect
        self.assertNotIn("where", inspect.signature(signature_fingerprint).parameters)


class ParseSignatureTest(unittest.TestCase):
    SIG = (
        "---\nstatus: active\n---\n# t\n\n"
        "## Signature\n"
        "- symptom: `KeyError: 'summary'`\n"
        "- error_type: KeyError\n"
        "- where: regen_cockpit_inprogress\n"
        "- trigger: active 工件缺 summary\n\n"
        "## 根因\n...\n"
    )

    def test_parses_four_keys(self):
        from flightdeck_index import parse_signature
        sig = parse_signature(self.SIG)
        self.assertEqual(sig["symptom"], "KeyError: 'summary'")   # 反引号被剥
        self.assertEqual(sig["error_type"], "KeyError")
        self.assertEqual(sig["where"], "regen_cockpit_inprogress")
        self.assertEqual(sig["trigger"], "active 工件缺 summary")

    def test_no_block_returns_empty(self):
        from flightdeck_index import parse_signature
        self.assertEqual(parse_signature("---\nstatus: active\n---\n# t\n## 根因\nx\n"), {})


class MatchSignatureTest(unittest.TestCase):
    def _deck(self, d):
        deck = Path(d)
        (deck / "incidents").mkdir(parents=True)
        return deck

    def _inc(self, deck, name, status, symptom, etype="KeyError"):
        (deck / "incidents" / name).write_text(
            f"---\nstatus: {status}\nwhen_to_read: w\napplies_to: [a]\nlast_updated: 2026-06-05\n---\n"
            f"# t\n\n## Signature\n- symptom: `{symptom}`\n- error_type: {etype}\n- where: foo\n- trigger: t\n",
            encoding="utf-8",
        )

    def test_exact_match_returns_path_and_status(self):
        from flightdeck_index import match_signature
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._inc(deck, "2026-06-05-a.md", "active", "KeyError: 'summary'")
            hits = match_signature(deck, "KeyError: 'summary'", "KeyError")
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["status"], "active")
            self.assertTrue(hits[0]["path"].endswith("2026-06-05-a.md"))

    def test_obsolete_still_matched(self):
        # 回归检测依赖：obsolete 不被过滤
        from flightdeck_index import match_signature
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._inc(deck, "2026-06-05-b.md", "obsolete", "KeyError: 'summary'")
            hits = match_signature(deck, "KeyError: 'summary'", "KeyError")
            self.assertEqual([h["status"] for h in hits], ["obsolete"])

    def test_signatureless_skipped(self):
        from flightdeck_index import match_signature
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "incidents" / "old.md").write_text(
                "---\nstatus: active\nwhen_to_read: w\napplies_to: [a]\nlast_updated: 2026-06-05\n---\n# t\n## 根因\nx\n",
                encoding="utf-8")
            self.assertEqual(match_signature(deck, "KeyError: 'summary'", "KeyError"), [])

    def test_match_signature_reaches_archived_incidents(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "archive" / "incidents").mkdir(parents=True)
            (deck / "archive" / "incidents" / "old.md").write_text(
                "---\nstatus: obsolete\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n"
                "# old\n## Signature\n- symptom: boom on parse\n- error_type: ValueError\n- where: p.py\n- trigger: bad input\n",
                encoding="utf-8",
            )
            from flightdeck_index import match_signature
            hits = match_signature(deck, "boom on parse", "ValueError")
            self.assertTrue(any("old.md" in h["path"] for h in hits))


class MatchSignatureCliTest(unittest.TestCase):
    def test_cli_prints_status_tab_path(self):
        import io
        from contextlib import redirect_stdout
        from flightdeck_index import main
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "incidents").mkdir()
            (deck / "incidents" / "2026-06-05-a.md").write_text(
                "---\nstatus: active\nwhen_to_read: w\napplies_to: [a]\nlast_updated: 2026-06-05\n---\n"
                "# t\n\n## Signature\n- symptom: `KeyError: 'summary'`\n- error_type: KeyError\n- where: foo\n- trigger: t\n",
                encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--match-signature", "KeyError: 'summary'", "--sig-error-type", "KeyError"])
            self.assertEqual(rc, 0)
            self.assertIn("active", buf.getvalue())
            self.assertIn("2026-06-05-a.md", buf.getvalue())


class ObsoleteRoutingExcludeTest(unittest.TestCase):
    def test_obsolete_row_absent_from_knowledge_index(self):
        from flightdeck_index import regen_folder_index
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "incidents"
            folder.mkdir()
            (folder / "live.md").write_text(
                "---\nstatus: active\nwhen_to_read: w\napplies_to: [x]\nlast_updated: 2026-06-05\n---\n# t\n",
                encoding="utf-8")
            (folder / "dead.md").write_text(
                "---\nstatus: obsolete\nwhen_to_read: w\napplies_to: [x]\nlast_updated: 2026-06-05\nresolved_by: test_x\n---\n# t\n",
                encoding="utf-8")
            block = regen_folder_index(folder)
            self.assertIn("live.md", block)
            self.assertNotIn("dead.md", block)   # obsolete 不进路由


class FormatRowVerifyMarkerTest(unittest.TestCase):
    def test_format_row_verify_vs_stale_markers(self):
        # 知识件：stale + verify → ⚠未验证
        r1 = flightdeck_index.format_row("checklists", "a.md",
            {"status": "stale", "when_to_read": "x", "applies_to": "[a]", "verify": "跑一遍"})
        self.assertTrue(r1.startswith("⚠未验证 "))
        # 知识件：stale 单独（过期）→ ⚠待复核
        r2 = flightdeck_index.format_row("checklists", "b.md",
            {"status": "stale", "when_to_read": "x", "applies_to": "[a]"})
        self.assertTrue(r2.startswith("⚠待复核 "))
        # 工作流件：done + verify → ⚠未验证
        r3 = flightdeck_index.format_row("specs", "c.md",
            {"status": "done", "summary": "s", "verify": "相位4 实证"})
        self.assertTrue(r3.startswith("⚠未验证 "))
        # 工作流件：done 干净 → 无标记
        r4 = flightdeck_index.format_row("specs", "d.md", {"status": "done", "summary": "s"})
        self.assertFalse(r4.startswith("⚠"))


class StaleIndexRenderTest(unittest.TestCase):
    def test_index_marks_stale_and_excludes_obsolete(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            for name, st in (("amber.md", "stale"), ("dead.md", "obsolete"), ("live.md", "active")):
                (deck / "docs" / name).write_text(
                    f"---\nstatus: {st}\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# {name}\n",
                    encoding="utf-8",
                )
            from flightdeck_index import regen_folder_index
            body = regen_folder_index(deck / "docs")
            self.assertIn("amber.md", body)      # stale shown
            self.assertIn("⚠", body)             # stale marked
            self.assertNotIn("dead.md", body)    # obsolete excluded


class SpecAdvanceCandidatesTest(unittest.TestCase):
    def _deck(self, root):
        deck = Path(root)
        (deck / "specs").mkdir()
        (deck / "plans").mkdir()
        return deck

    def _spec(self, deck, name, status):
        (deck / "specs" / name).write_text(
            f"---\nstatus: {status}\nsummary: s\n---\n", encoding="utf-8")

    def _plan(self, deck, name, status, implements):
        (deck / "plans" / name).write_text(
            f"---\nstatus: {status}\nimplements: {implements}\nsummary: p\n---\n", encoding="utf-8")

    def test_active_spec_with_all_plans_done_is_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._spec(deck, "2026-06-01-x.md", "active")
            self._plan(deck, "2026-06-02-p.md", "done", "specs/2026-06-01-x.md")
            self.assertEqual(
                flightdeck_index.spec_advance_candidates(deck),
                ["specs/2026-06-01-x.md"])

    def test_two_done_plans_one_spec_is_candidate_once(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._spec(deck, "2026-06-01-x.md", "active")
            self._plan(deck, "2026-06-02-a.md", "done", "specs/2026-06-01-x.md")
            self._plan(deck, "2026-06-03-b.md", "done", "specs/2026-06-01-x.md")
            self.assertEqual(
                flightdeck_index.spec_advance_candidates(deck),
                ["specs/2026-06-01-x.md"])

    def test_active_spec_with_an_active_plan_not_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._spec(deck, "2026-06-01-x.md", "active")
            self._plan(deck, "2026-06-02-p1.md", "done", "specs/2026-06-01-x.md")
            self._plan(deck, "2026-06-03-p2.md", "active", "specs/2026-06-01-x.md")
            self.assertEqual(flightdeck_index.spec_advance_candidates(deck), [])

    def test_done_spec_not_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._spec(deck, "2026-06-01-x.md", "done")
            self._plan(deck, "2026-06-02-p.md", "done", "specs/2026-06-01-x.md")
            self.assertEqual(flightdeck_index.spec_advance_candidates(deck), [])

    def test_active_spec_no_plan_not_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._spec(deck, "2026-06-01-x.md", "active")
            self.assertEqual(flightdeck_index.spec_advance_candidates(deck), [])

    def test_active_spec_with_only_idea_plan_not_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._spec(deck, "2026-06-01-x.md", "active")
            self._plan(deck, "2026-06-02-p.md", "idea", "specs/2026-06-01-x.md")
            self.assertEqual(flightdeck_index.spec_advance_candidates(deck), [])

    def test_plan_implementing_missing_spec_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._plan(deck, "2026-06-02-p.md", "done", "specs/ghost.md")
            self.assertEqual(flightdeck_index.spec_advance_candidates(deck), [])


def _git(deck, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", HOME=str(deck))
    subprocess.run(["git", *args], cwd=deck, check=True, capture_output=True, env=env)


class AnchorTest(unittest.TestCase):
    def test_anchor_and_changed_since(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            _git(deck, "init", "-q")
            (deck / "a").write_text("1", encoding="utf-8")
            _git(deck, "add", "-A"); _git(deck, "commit", "-qm", "land\n\nFlightdeck-Sync: 1")
            (deck / "b").write_text("2", encoding="utf-8")
            _git(deck, "add", "-A"); _git(deck, "commit", "-qm", "ordinary work")
            from flightdeck_index import last_anchor_ref, changed_since_anchor
            self.assertIsNotNone(last_anchor_ref(deck))
            changed = changed_since_anchor(deck)
            self.assertIn("b", changed)
            self.assertNotIn("a", changed)


class VerifyPendingTest(unittest.TestCase):
    def test_verify_pending_scans_active_and_archive(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d) / "flightdeck"
            (deck / "checklists").mkdir(parents=True)
            (deck / "archive" / "specs").mkdir(parents=True)
            (deck / "checklists" / "foo.md").write_text(
                "---\nstatus: stale\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-08\nverify: 跑一遍 foo 流程\n---\n# foo\n",
                encoding="utf-8",
            )
            (deck / "archive" / "specs" / "bar.md").write_text(
                "---\nstatus: done\nsummary: bar\nverify: 相位4 各家 live 实证\n---\n# bar\n",
                encoding="utf-8",
            )
            (deck / "checklists" / "clean.md").write_text(
                "---\nstatus: active\nwhen_to_read: y\napplies_to: [b]\nlast_updated: 2026-06-08\n---\n# clean\n",
                encoding="utf-8",
            )
            # Defence-in-depth: an INDEX.md carrying a verify: field must be
            # excluded by the `if p.name == "INDEX.md": continue` guard.
            (deck / "checklists" / "INDEX.md").write_text(
                "---\nverify: 这是 INDEX 不应出现在结果里\n---\n# checklists INDEX\n",
                encoding="utf-8",
            )
            rows = flightdeck_index.verify_pending(str(deck))
            self.assertEqual(
                rows,
                [
                    ("archive/specs/bar.md", "相位4 各家 live 实证"),
                    ("checklists/foo.md", "跑一遍 foo 流程"),
                ],
            )
            # The INDEX.md must not appear in the result at all.
            paths = [r[0] for r in rows]
            self.assertNotIn("checklists/INDEX.md", paths)


class VerifyPendingUtf8CliTest(unittest.TestCase):
    """Regression: --verify-pending CJK notes must survive subprocess stdout as UTF-8.

    On Windows, sys.stdout defaults to the locale codepage (e.g. gbk).
    The fix (sys.stdout.reconfigure(encoding='utf-8') at the start of main)
    must ensure the subprocess consumer can decode as UTF-8 and see the CJK intact.
    """

    def test_verify_pending_cli_emits_utf8_cjk(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d) / "flightdeck"
            (deck / "specs").mkdir(parents=True)
            (deck / "specs" / "x.md").write_text(
                "---\nstatus: done\nsummary: s\nverify: 相位4 各家 live 实证（resync 后新会话）\n---\n# x\n",
                encoding="utf-8",
            )
            script = Path(__file__).resolve().parents[1] / "flightdeck_index.py"
            result = subprocess.run(
                [sys.executable, str(script), str(deck), "--verify-pending"],
                capture_output=True,
            )
            out = result.stdout.decode("utf-8")
            self.assertIn("相位4 各家 live 实证（resync 后新会话）", out)


class SyncStatusTest(unittest.TestCase):
    """flightdeck_index.sync_status — 共享知识漂移只读扫描（v2：固定母库 + synced 标记）。"""

    def _master_file(self, master, relpath, last_updated):
        p = master / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\n"
            f"last_updated: {last_updated}\n---\n# {p.stem}\n",
            encoding="utf-8",
        )

    def _consumer(self, root):
        deck = root / "consumer"
        (deck / "checklists").mkdir(parents=True)
        (deck / "rules.md").write_text("---\nversion: 3.0\n---\n", encoding="utf-8")
        return deck

    def _vendored(self, deck, relpath, last_updated):
        p = deck / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\nstatus: active\nsynced: true\n"
            f"when_to_read: x\napplies_to: [y]\nlast_updated: {last_updated}\n---\n# {p.stem}\n",
            encoding="utf-8",
        )

    def _home(self, fake_home):
        # 母库恒为 ~/.flightdeck —— 测试里把 Path.home() 指到 fake_home，母库 = fake_home/.flightdeck
        return mock.patch.object(flightdeck_index.Path, "home", return_value=fake_home)

    def test_states_and_ignores_unsynced(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / ".flightdeck"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")   # 母库更新 → upstream-changed
            self._vendored(deck, "checklists/ahead.md", "2026-06-25")     # 母库无源 → dangling（源不存在）
            (deck / "checklists" / "local.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-18\n---\n# local\n",
                encoding="utf-8",
            )
            with self._home(root):
                states = {rel: st for st, rel in sync_status(deck)}
            self.assertEqual(states["checklists/commits.md"], "upstream-changed")
            self.assertEqual(states["checklists/ahead.md"], "dangling")
            self.assertNotIn("checklists/local.md", states)

    def test_locally_ahead_and_in_sync(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / ".flightdeck"
            self._master_file(master, "checklists/commits.md", "2026-06-18")
            self._master_file(master, "checklists/comments.md", "2026-06-10")
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")   # 相等 → in-sync
            self._vendored(deck, "checklists/comments.md", "2026-06-25")  # 项目更新 → locally-ahead
            with self._home(root):
                states = {rel: st for st, rel in sync_status(deck)}
            self.assertEqual(states["checklists/commits.md"], "in-sync")
            self.assertEqual(states["checklists/comments.md"], "locally-ahead")

    def test_master_missing_when_no_flightdeck_home(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)                 # root 下不建 .flightdeck → 母库缺席
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")
            with self._home(root):
                self.assertEqual(sync_status(deck)[0][0], "master-missing")

    def test_read_only_writes_nothing(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / ".flightdeck"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")
            before = {p: p.read_text(encoding="utf-8") for p in deck.rglob("*.md")}
            with self._home(root):
                sync_status(deck)
            after = {p: p.read_text(encoding="utf-8") for p in deck.rglob("*.md")}
            self.assertEqual(before, after)


class ConsumersRegistryTest(unittest.TestCase):
    """consumers 注册表：register / list / prune（对母库 frontmatter 读改写）。"""

    def _mfile(self, master, relpath, consumers=None):
        p = master / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        extra = f"consumers: {json.dumps(consumers)}\n" if consumers is not None else ""
        p.write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\n{extra}"
            f"last_updated: 2026-06-19\n---\n# {p.stem}\n",
            encoding="utf-8",
        )
        return p

    def test_register_is_idempotent_and_normalizes(self):
        from flightdeck_index import register_consumer, _read_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            self._mfile(master, "checklists/commits.md")
            deckdir = Path(d) / "projA" / "flightdeck"
            deckdir.mkdir(parents=True)
            register_consumer(master, "checklists/commits.md", str(deckdir))
            # 再注册同 deck（带尾斜杠变体）→ 不重复增长
            register_consumer(master, "checklists/commits.md", str(deckdir) + os.sep)
            fm = flightdeck_index.parse_frontmatter(
                (master / "checklists/commits.md").read_text(encoding="utf-8"))
            self.assertEqual(_read_consumers(fm), [deckdir.resolve().as_posix()])

    def test_register_rejects_non_file_relpath(self):
        from flightdeck_index import register_consumer
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            (master / "checklists").mkdir(parents=True)
            deckdir = Path(d) / "projA"
            deckdir.mkdir()
            with self.assertRaises(ValueError):
                register_consumer(master, "checklists/", str(deckdir))      # 目录非文件
            with self.assertRaises(ValueError):
                register_consumer(master, "checklists/missing.md", str(deckdir))  # 不存在

    def test_list_consumers_union_dedup_reachable_only(self):
        from flightdeck_index import list_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            a = Path(d) / "projA" / "flightdeck"; a.mkdir(parents=True)
            b = Path(d) / "projB" / "flightdeck"; b.mkdir(parents=True)
            gone = (Path(d) / "projGONE" / "flightdeck").resolve().as_posix()  # 不存在目录
            self._mfile(master, "checklists/commits.md",
                        consumers=[a.resolve().as_posix(), gone])
            self._mfile(master, "checklists/comments.md",
                        consumers=[a.resolve().as_posix(), b.resolve().as_posix()])
            got = list_consumers(master)
            self.assertEqual(got, sorted([a.resolve().as_posix(), b.resolve().as_posix()]))
            self.assertNotIn(gone, got)        # 不可达目录被跳过
            # 纯读：母库文件未被改写
            self.assertIn(gone, flightdeck_index._read_consumers(
                flightdeck_index.parse_frontmatter(
                    (master / "checklists/commits.md").read_text(encoding="utf-8"))))

    def test_list_consumers_skips_non_utf8_file(self):
        # 非 UTF-8 的 .md（如 GBK/BOM/误命名二进制）应被跳过，不让整个扫描崩
        # （UnicodeDecodeError 是 ValueError，不是 OSError）。
        from flightdeck_index import list_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            a = Path(d) / "projA" / "flightdeck"; a.mkdir(parents=True)
            self._mfile(master, "checklists/commits.md",
                        consumers=[a.resolve().as_posix()])
            (master / "checklists" / "junk.md").write_bytes(b"\xff\xfe\x00bad bytes")
            self.assertEqual(list_consumers(master), [a.resolve().as_posix()])

    def test_prune_removes_only_confirmed_gone(self):
        from flightdeck_index import prune_consumers, _read_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            alive = Path(d) / "projA" / "flightdeck"; alive.mkdir(parents=True)
            # gone：父目录 projGONE 存在、deck 本身不存在 → 应剔除
            gone_parent = Path(d) / "projGONE"; gone_parent.mkdir()
            gone = (gone_parent / "flightdeck").resolve().as_posix()
            # unreachable：父目录都不存在（整盘离线模拟）→ 不剔除
            unreachable = (Path(d) / "noSuchDrive" / "x" / "flightdeck").resolve().as_posix()
            self._mfile(master, "checklists/commits.md",
                        consumers=[alive.resolve().as_posix(), gone, unreachable])
            removed = prune_consumers(master)
            self.assertIn(("checklists/commits.md", gone), removed)
            kept = _read_consumers(flightdeck_index.parse_frontmatter(
                (master / "checklists/commits.md").read_text(encoding="utf-8")))
            self.assertIn(alive.resolve().as_posix(), kept)
            self.assertIn(unreachable, kept)       # 父不可达 → 保守保留
            self.assertNotIn(gone, kept)


if __name__ == "__main__":
    unittest.main()
