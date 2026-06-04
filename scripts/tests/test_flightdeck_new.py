import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_new import new
import flightdeck_index


def _deck(d):
    """Make a minimal deck skeleton (folders only) under temp dir d."""
    deck = Path(d) / "flightdeck"
    for f in ["specs", "plans", "incidents", "checklists", "charts"]:
        (deck / f).mkdir(parents=True)
    return deck


class NewHappyPathTest(unittest.TestCase):
    def test_idea_spec_is_dateless_with_minimal_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "spec", slug="my-idea", title="My Idea",
                       status="idea", regen=False)
            self.assertEqual(path, deck / "specs" / "my-idea.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: idea", text)
            self.assertNotIn("last_updated:", text)   # idea omits last_updated
            self.assertIn("# My Idea", text)

    def test_active_spec_gets_date_prefix_and_last_updated(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "spec", slug="real-design", title="Real Design",
                       status="active", summary="a gist", date="2026-06-04", regen=False)
            self.assertEqual(path, deck / "specs" / "2026-06-04-real-design.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: active", text)
            self.assertIn("summary: a gist", text)
            self.assertIn("last_updated: 2026-06-04", text)

    def test_plan_carries_implements(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "plan", slug="roll-it", title="Roll It",
                       status="active", implements="specs/x.md", date="2026-06-04", regen=False)
            self.assertEqual(path, deck / "plans" / "2026-06-04-roll-it.md")
            self.assertIn("implements: specs/x.md", path.read_text(encoding="utf-8"))

    def test_knowledge_defaults_active_and_carries_routing_fields(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "incident", slug="oops", title="Oops",
                       when_to_read="before X", applies_to=["a", "b"],
                       date="2026-06-04", regen=False)
            self.assertEqual(path, deck / "incidents" / "2026-06-04-oops.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: active", text)           # knowledge default
            self.assertIn("when_to_read: before X", text)
            self.assertIn("applies_to: [a, b]", text)


if __name__ == "__main__":
    unittest.main()
