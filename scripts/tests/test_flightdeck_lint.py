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
    audit_required_structure,
    lint,
    main,
)


FULL_COCKPIT = """# Cockpit — test

**Last updated**: 2026-06-06 by t
**Active focus**: x

## 进行中

<!-- AUTO:inprogress -->
- item
<!-- /AUTO -->

## 下一步

- do the thing

## Hanging tasks

- (none)
"""


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
            for s in ("idea", "active", "done"):
                (deck / "specs" / f"{s}.md").write_text(
                    f"---\nstatus: {s}\nsummary: x\n---\n", encoding="utf-8"
                )
            self.assertEqual(audit_status(deck), [])

    def test_scrapped_is_illegal_workflow_status(self):
        # `scrapped` was retired (3.0): a rejected artifact is deleted, not
        # parked. A lingering `status: scrapped` is now an illegal value.
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "specs").mkdir()
            (deck / "specs" / "2026-05-01-dead.md").write_text(
                "---\nstatus: scrapped\nsummary: r\n---\n", encoding="utf-8"
            )
            warn = _sev(audit_status(deck), "WARNING")
            self.assertEqual(len(warn), 1)
            self.assertIn("scrapped", warn[0]["message"])

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

    def test_knowledge_superseded_is_illegal(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            (deck / "docs" / "a.md").write_text(
                "---\nstatus: superseded\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# t\n",
                encoding="utf-8",
            )
            warns = _by_audit(audit_status(deck), "status")
            self.assertTrue(any("illegal status `superseded`" in f["message"] for f in warns))

    def test_knowledge_stale_is_legal(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "docs").mkdir()
            (deck / "docs" / "a.md").write_text(
                "---\nstatus: stale\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# t\n",
                encoding="utf-8",
            )
            self.assertEqual(_by_audit(audit_status(deck), "status"), [])


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
            warn = _sev(audit_index_consistency(deck), "WARNING")
            labels = " ".join(f["message"] for f in warn)
            self.assertIn("specs", labels)

    def test_clean_index_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck, specs = self._deck(d)
            import flightdeck_index
            (specs / "INDEX.md").write_text(
                "# specs\n\n" + flightdeck_index.regen_folder_index(specs) + "\n",
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


class AuditRequiredStructureTest(unittest.TestCase):
    def _write_cockpit(self, deck, text):
        (deck / "cockpit.md").write_text(text, encoding="utf-8")

    def test_full_cockpit_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT)
            self.assertEqual(audit_required_structure(deck), [])

    def test_missing_inprogress_heading_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("## 进行中\n", ""))
            crit = _sev(audit_required_structure(deck), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("进行中", crit[0]["message"])
            self.assertTrue(crit[0]["path"].endswith("cockpit.md"))

    def test_missing_next_step_heading_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("## 下一步\n", ""))
            crit = _sev(audit_required_structure(deck), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("下一步", crit[0]["message"])

    def test_missing_hanging_tasks_heading_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("## Hanging tasks\n", ""))
            crit = _sev(audit_required_structure(deck), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("Hanging tasks", crit[0]["message"])

    def test_missing_auto_open_anchor_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("<!-- AUTO:inprogress -->\n", ""))
            crit = _sev(audit_required_structure(deck), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("AUTO:inprogress", crit[0]["message"])

    def test_missing_auto_close_anchor_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("<!-- /AUTO -->\n", ""))
            crit = _sev(audit_required_structure(deck), "CRITICAL")
            self.assertEqual(len(crit), 1)
            self.assertIn("/AUTO", crit[0]["message"])

    def test_no_cockpit_file_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self.assertEqual(audit_required_structure(deck), [])

    def test_heading_with_trailing_whitespace_still_matches(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("## 下一步\n", "## 下一步   \n"))
            self.assertEqual(audit_required_structure(deck), [])

    def test_lint_includes_required_structure(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._write_cockpit(deck, FULL_COCKPIT.replace("## Hanging tasks\n", ""))
            findings = lint(deck)
            self.assertTrue(any(f["audit"] == "required-structure" for f in findings))


class AuditWhenToUpdateTest(unittest.TestCase):
    def _doc(self, deck, body_fm):
        (deck / "docs").mkdir(exist_ok=True)
        (deck / "docs" / "a.md").write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n{body_fm}---\n# t\n",
            encoding="utf-8",
        )
    def test_vague_when_to_update_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._doc(deck, "when_to_update: 有任何改动时\n")
            from flightdeck_lint import audit_when_to_update
            self.assertTrue(audit_when_to_update(deck))
    def test_concrete_when_to_update_ok(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._doc(deck, "when_to_update: 改了 plugin 加载协议 / 动了 hooks/stop.sh\n")
            from flightdeck_lint import audit_when_to_update
            self.assertEqual(audit_when_to_update(deck), [])
    def test_missing_when_to_update_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._doc(deck, "")
            from flightdeck_lint import audit_when_to_update
            self.assertEqual(audit_when_to_update(deck), [])


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
            (deck / "cockpit.md").write_text(FULL_COCKPIT, encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["findings"], [])


if __name__ == "__main__":
    unittest.main()
