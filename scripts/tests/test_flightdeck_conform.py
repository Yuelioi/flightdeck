import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_conform import LEGAL_FIELDS, REQUIRED_FIELDS, kind_of


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


if __name__ == "__main__":
    unittest.main()
