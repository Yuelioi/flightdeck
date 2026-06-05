import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import flightdeck_lint
from flightdeck_lint import (
    audit_status,
    audit_orphan_plans,
    audit_index_consistency,
    audit_dangling_refs,
    audit_stray,
    lint,
    main,
)


def _sev(findings, severity):
    return [f for f in findings if f["severity"] == severity]


def _by_audit(findings, audit):
    return [f for f in findings if f["audit"] == audit]


class AuditStatusTest(unittest.TestCase):
    def test_workflow_missing_status_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "a.md").write_text(
                "---\nsummary: no status here\n---\n", encoding="utf-8"
            )
            crit = _sev(audit_status(deck), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertTrue(crit[0]["path"].endswith("a.md"))

    def test_workflow_illegal_status_is_warning(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "plans").mkdir()
            # retired pre-3.0 value
            (deck / "plans" / "b.md").write_text(
                "---\nstatus: pending\nsummary: x\n---\n", encoding="utf-8"
            )
            warn = _sev(audit_status(deck), "WARNING")
            self.assertEqual(len(warn), 1)
            self.assertIn("pending", warn[0]["message"])

    def test_workflow_legal_status_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            for s in ("idea", "active", "done", "scrapped"):
                (deck / "specs" / f"{s}.md").write_text(
                    f"---\nstatus: {s}\nsummary: x\n---\n", encoding="utf-8"
                )
            self.assertEqual(audit_status(deck), [])

    def test_knowledge_illegal_status_is_warning(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "incidents").mkdir()
            # 'done' is a workflow status, illegal for knowledge
            (deck / "incidents" / "i.md").write_text(
                "---\nstatus: done\nwhen_to_read: x\napplies_to: [a]\n---\n",
                encoding="utf-8",
            )
            warn = _sev(audit_status(deck), "WARNING")
            self.assertEqual(len(warn), 1)

    def test_knowledge_legal_status_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "checklists").mkdir()
            (deck / "checklists" / "c.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_status(deck), [])

    def test_index_md_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "INDEX.md").write_text("no frontmatter\n", encoding="utf-8")
            self.assertEqual(audit_status(deck), [])

    def test_archive_is_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "archive" / "specs").mkdir(parents=True)
            (deck / "archive" / "specs" / "old.md").write_text(
                "---\nsummary: archived no status\n---\n", encoding="utf-8"
            )
            self.assertEqual(audit_status(deck), [])

    def test_references_external_tree_not_audited(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "references" / "proj").mkdir(parents=True)
            # nested file inside an imported tree — must not be flagged
            (deck / "references" / "proj" / "deep.md").write_text(
                "no frontmatter\n", encoding="utf-8"
            )
            self.assertEqual(audit_status(deck), [])

    def test_docs_knowledge_status_audited(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            (deck / "docs" / "guide.md").write_text(
                "---\nstatus: done\nwhen_to_read: x\napplies_to: [a]\n---\n",
                encoding="utf-8",
            )
            warn = _sev(audit_status(deck), "WARNING")
            self.assertEqual(len(warn), 1)
            self.assertIn("done", warn[0]["message"])

    def test_docs_legal_status_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            (deck / "docs" / "guide.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_status(deck), [])


class AuditOrphanPlansTest(unittest.TestCase):
    def test_plan_without_implements_is_info(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "plans").mkdir()
            (deck / "plans" / "p.md").write_text(
                "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
            )
            info = _sev(audit_orphan_plans(deck), "INFO")
            self.assertEqual(len(info), 1)
            self.assertTrue(info[0]["path"].endswith("p.md"))

    def test_plan_with_implements_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "plans").mkdir()
            (deck / "plans" / "p.md").write_text(
                "---\nstatus: active\nimplements: specs/s.md\nsummary: x\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_orphan_plans(deck), [])

    def test_archive_plans_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "archive" / "plans").mkdir(parents=True)
            (deck / "archive" / "plans" / "p.md").write_text(
                "---\nstatus: done\nsummary: x\n---\n", encoding="utf-8"
            )
            self.assertEqual(audit_orphan_plans(deck), [])


class AuditIndexConsistencyTest(unittest.TestCase):
    def _deck(self, d):
        deck = Path(d)
        specs = deck / "specs"
        specs.mkdir()
        (specs / "a.md").write_text(
            "---\nstatus: done\nsummary: real\n---\n", encoding="utf-8"
        )
        return deck, specs

    def test_drifted_index_is_warning(self):
        with tempfile.TemporaryDirectory() as d:
            deck, specs = self._deck(d)
            (specs / "INDEX.md").write_text(
                "# specs\n\n<!-- AUTO:specs -->\nSTALE\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            (deck / "INDEX.md").write_text(
                "# root\n\n<!-- AUTO:root -->\nSTALE\n<!-- /AUTO -->\n", encoding="utf-8"
            )
            warn = _sev(audit_index_consistency(deck), "WARNING")
            labels = " ".join(f["message"] for f in warn)
            self.assertIn("specs", labels)
            self.assertIn("root", labels)

    def test_clean_index_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck, specs = self._deck(d)
            import flightdeck_index
            (specs / "INDEX.md").write_text(
                "# specs\n\n" + flightdeck_index.regen_folder_index(specs) + "\n",
                encoding="utf-8",
            )
            (deck / "INDEX.md").write_text(
                "# root\n\n" + flightdeck_index.regen_root_index(deck) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_index_consistency(deck), [])


class AuditDanglingRefsTest(unittest.TestCase):
    def test_missing_target_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "doc.md"
            f.write_text("see [the plan](plans/ghost.md) for details\n", encoding="utf-8")
            crit = _sev(audit_dangling_refs([f]), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("ghost.md", crit[0]["message"])

    def test_existing_target_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "target.md").write_text("hi\n", encoding="utf-8")
            f = Path(d) / "doc.md"
            f.write_text("see [t](target.md)\n", encoding="utf-8")
            self.assertEqual(audit_dangling_refs([f]), [])

    def test_http_link_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "doc.md"
            f.write_text("[x](https://example.com/a.md)\n", encoding="utf-8")
            self.assertEqual(audit_dangling_refs([f]), [])

    def test_anchor_only_link_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "doc.md"
            f.write_text("[x](#a-heading)\n", encoding="utf-8")
            self.assertEqual(audit_dangling_refs([f]), [])

    def test_fragment_is_stripped_before_resolving(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "target.md").write_text("hi\n", encoding="utf-8")
            f = Path(d) / "doc.md"
            f.write_text("[x](target.md#some-anchor)\n", encoding="utf-8")
            self.assertEqual(audit_dangling_refs([f]), [])

    def test_links_inside_code_are_ignored(self):
        # link syntax shown as a prose example (inline code or fenced block) is
        # documentation, not a real cross-reference — must not be flagged.
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "doc.md"
            f.write_text(
                "the row format is `[file](specs/ghost.md) — summary`\n\n"
                "```\n"
                "- [block](plans/also-ghost.md)\n"
                "```\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_dangling_refs([f]), [])

    def test_real_link_outside_code_still_flagged(self):
        # the code-stripping must not swallow genuine links elsewhere in the file
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "doc.md"
            f.write_text(
                "example `[x](a.md)` then a real [y](missing.md) link\n",
                encoding="utf-8",
            )
            crit = _sev(audit_dangling_refs([f]), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("missing.md", crit[0]["message"])


class AuditStrayTest(unittest.TestCase):
    def test_unknown_dir_under_deck_is_warning(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "bogus").mkdir()
            warn = _sev(audit_stray(deck), "WARNING")
            self.assertTrue(any("bogus" in f["message"] for f in warn))

    def test_unknown_root_md_is_warning(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "cockpit.md").write_text("# c\n", encoding="utf-8")
            (deck / "stray.md").write_text("# orphan\n", encoding="utf-8")
            warn = _sev(audit_stray(deck), "WARNING")
            self.assertTrue(any("stray.md" in f["message"] for f in warn))

    def test_known_root_files_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            for name in ("cockpit.md", "INDEX.md", "rules.md"):
                (deck / name).write_text("# x\n", encoding="utf-8")
            for folder in ("specs", "plans", "incidents", "checklists", "docs", "references", "archive"):
                (deck / folder).mkdir()
            self.assertEqual(audit_stray(deck), [])

    def test_nestable_area_subdir_not_stray(self):
        """NESTABLE_KINDS folders may have <area>/ subdirs — those must not be flagged."""
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            for kind in ("incidents", "checklists", "docs", "references"):
                area = deck / kind / "infra"
                area.mkdir(parents=True)
                (area / "note.md").write_text("# note\n", encoding="utf-8")
            self.assertEqual(audit_stray(deck), [])

    def test_root_md_linked_from_entry_is_reachable(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "cockpit.md").write_text(
                "see [notes](notes.md)\n", encoding="utf-8"
            )
            (deck / "notes.md").write_text("# notes\n", encoding="utf-8")
            self.assertEqual(audit_stray(deck), [])


class LintAndMainTest(unittest.TestCase):
    def test_lint_aggregates_audits(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "plans").mkdir()
            (deck / "plans" / "p.md").write_text(
                "---\nstatus: active\nsummary: x\n---\n", encoding="utf-8"
            )  # orphan plan -> INFO
            findings = lint(deck)
            self.assertTrue(any(f["audit"] == "orphan-plan" for f in findings))

    def test_main_emits_json_and_exits_nonzero_on_warning(self):
        import io
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "a.md").write_text(
                "---\nsummary: missing status\n---\n", encoding="utf-8"
            )  # CRITICAL
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck)])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertIn("findings", payload)
            self.assertTrue(any(f["severity"] == "CRITICAL" for f in payload["findings"]))

    def test_main_exits_zero_when_clean(self):
        import io
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "cockpit.md").write_text("# c\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["findings"], [])


if __name__ == "__main__":
    unittest.main()
