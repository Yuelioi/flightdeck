import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_conform import (
    LEGAL_FIELDS,
    REQUIRED_FIELDS,
    kind_of,
    prune_frontmatter,
    conform_file,
    stamp_rules,
    add_missing_sections,
    COCKPIT_SECTIONS,
    RULES_SECTIONS,
)


class FieldSetTest(unittest.TestCase):
    def test_required_subset_of_legal(self):
        for k, req in REQUIRED_FIELDS.items():
            self.assertTrue(req <= LEGAL_FIELDS[k], k)

    def test_spec_legal_set_pinned(self):
        # Drift guard: changing the schema must be an intentional edit here.
        self.assertEqual(
            LEGAL_FIELDS["spec"],
            {"status", "summary", "last_updated", "note", "supersedes",
             "related", "graduate", "verify"},
        )

    def test_knowledge_required_pinned(self):
        self.assertEqual(
            REQUIRED_FIELDS["checklist"],
            {"status", "when_to_read", "applies_to", "last_updated"},
        )

    def test_rules_legal_pinned(self):
        self.assertEqual(LEGAL_FIELDS["rules"], {"version", "runtime", "agents_md"})


class KindOfTest(unittest.TestCase):
    def test_routes_known_folders(self):
        deck = Path("/deck")
        self.assertEqual(kind_of(deck, deck / "checklists" / "x.md"), "checklist")
        self.assertEqual(kind_of(deck, deck / "specs" / "2026-01-01-x.md"), "spec")
        self.assertEqual(kind_of(deck, deck / "docs" / "area" / "x.md"), "doc")
        self.assertEqual(kind_of(deck, deck / "rules.md"), "rules")

    def test_excludes_archive_cockpit_and_stray(self):
        deck = Path("/deck")
        self.assertIsNone(kind_of(deck, deck / "archive" / "specs" / "x.md"))
        self.assertIsNone(kind_of(deck, deck / "cockpit.md"))
        self.assertIsNone(kind_of(deck, deck / "weird" / "x.md"))


class PruneFrontmatterTest(unittest.TestCase):
    def test_drops_nonschema_keeps_legal_and_body(self):
        text = (
            "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\n"
            "last_updated: 2026-06-19\nportable: true\n---\n# body\n"
        )
        out, removed = prune_frontmatter(text, "checklist")
        self.assertEqual(removed, ["portable"])
        self.assertNotIn("portable", out)
        self.assertIn("# body", out)
        self.assertIn("when_to_read: x", out)

    def test_preserves_order_and_comment_lines(self):
        text = (
            "---\n# a comment\nstatus: active\ngit: true\n"
            "summary: hi\nbad_field: 1\n---\nbody\n"
        )
        out, removed = prune_frontmatter(text, "spec")
        self.assertEqual(removed, ["git", "bad_field"])
        self.assertEqual(
            out, "---\n# a comment\nstatus: active\nsummary: hi\n---\nbody\n"
        )

    def test_no_frontmatter_is_untouched(self):
        text = "# just a body\nno frontmatter here\n"
        out, removed = prune_frontmatter(text, "doc")
        self.assertEqual(out, text)
        self.assertEqual(removed, [])

    def test_body_after_fence_is_byte_for_byte(self):
        body = "---\nstatus: active\nsummary: s\n---\nline1\n---\nnot fm\n"
        out, removed = prune_frontmatter(body, "spec")
        self.assertEqual(out, body)
        self.assertEqual(removed, [])


class ConformFileTest(unittest.TestCase):
    def test_apply_writes_pruned_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            p.write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\n"
                "last_updated: 2026-06-19\nportable: true\n---\nbody\n",
                encoding="utf-8",
            )
            ch = conform_file(p, "checklist", apply=True)
            self.assertEqual(ch.removed, ["portable"])
            self.assertNotIn("portable", p.read_text(encoding="utf-8"))

    def test_check_writes_nothing(self):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            original = (
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\n"
                "last_updated: 2026-06-19\nportable: true\n---\nbody\n"
            )
            p.write_text(original, encoding="utf-8")
            ch = conform_file(p, "checklist", apply=False)
            self.assertEqual(ch.removed, ["portable"])
            self.assertEqual(p.read_text(encoding="utf-8"), original)


class StampRulesTest(unittest.TestCase):
    def test_adds_all_three_when_missing(self):
        text = "---\n---\n## House rules\n"
        out = stamp_rules(text, "uv")
        self.assertIn("version: 3.0", out)
        self.assertIn("runtime: uv", out)
        self.assertIn("agents_md: off", out)
        self.assertIn("## House rules", out)

    def test_leaves_existing_untouched(self):
        text = "---\nversion: 3.0\nagents_md: auto\n---\nbody\n"
        out = stamp_rules(text, "python")
        self.assertIn("agents_md: auto", out)
        self.assertNotIn("agents_md: off", out)
        # version not duplicated
        self.assertEqual(out.count("version:"), 1)
        # runtime is the one missing field added
        self.assertIn("runtime: python", out)

    def test_canonical_order_when_all_added(self):
        out = stamp_rules("---\n---\n", "node")
        self.assertEqual(
            out, "---\nversion: 3.0\nruntime: node\nagents_md: off\n---\n"
        )

    def test_no_frontmatter_gets_a_block(self):
        out = stamp_rules("## House rules\nbody\n", "uv")
        self.assertTrue(out.startswith("---\nversion: 3.0\nruntime: uv\nagents_md: off\n---\n"))
        self.assertIn("## House rules", out)


class AddSectionsTest(unittest.TestCase):
    def test_appends_missing_cockpit_sections(self):
        text = (
            "# Cockpit\n\nUpdated: 2026-06-19\n\n## Next\n\n- do x\n\n"
            "## In Progress\n\n<!-- AUTO:inprogress -->\n<!-- /AUTO -->\n"
        )
        out, added = add_missing_sections(text, "cockpit")
        self.assertEqual(added, ["## Key Context", "## Pending Review", "## Hanging Tasks"])
        self.assertIn("## Key Context", out)
        self.assertIn("- (none)", out)
        # existing sections kept, not duplicated
        self.assertEqual(out.count("## Next"), 1)
        self.assertEqual(out.count("## In Progress"), 1)

    def test_in_progress_skeleton_carries_auto_markers(self):
        out, added = add_missing_sections("# Cockpit\n", "cockpit")
        self.assertIn("## In Progress", added)
        self.assertIn("<!-- AUTO:inprogress -->", out)
        self.assertIn("<!-- /AUTO -->", out)

    def test_no_duplicate_when_all_present(self):
        text = "".join(s + "\n\n- x\n\n" for s in COCKPIT_SECTIONS)
        out, added = add_missing_sections(text, "cockpit")
        self.assertEqual(added, [])
        self.assertEqual(out, text)

    def test_rules_sections(self):
        out, added = add_missing_sections("---\nversion: 3.0\n---\n", "rules")
        self.assertEqual(added, RULES_SECTIONS)
        for s in RULES_SECTIONS:
            self.assertIn(s, out)


if __name__ == "__main__":
    unittest.main()
