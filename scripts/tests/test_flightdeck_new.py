import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re

from flightdeck_new import new, KIND_FOLDER
import flightdeck_index


def _deck(d):
    """Make a minimal deck skeleton (folders only) under temp dir d."""
    deck = Path(d) / "flightdeck"
    for f in ["specs", "plans", "incidents", "checklists", "references", "docs"]:
        (deck / f).mkdir(parents=True)
    return deck


class NewHappyPathTest(unittest.TestCase):
    def test_idea_spec_is_dateless_with_minimal_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "spec", slug="my-idea", title="My Idea",
                       status="idea", summary="an idea gist", regen=False)
            self.assertEqual(path, deck / "specs" / "my-idea.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: idea", text)
            self.assertIn("summary: an idea gist", text)
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
            path = new(deck, "plan", slug="roll-it", title="Roll It", summary="roll gist",
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

    def test_chart_falls_in_references_folder(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "chart", slug="arch-overview", title="Arch Overview",
                       when_to_read="when designing", applies_to=["arch"],
                       date="2026-06-05", regen=False)
            self.assertEqual(path, deck / "references" / "2026-06-05-arch-overview.md")
            self.assertNotIn("charts", str(path))

    def test_doc_kind_falls_in_docs_dateless(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "doc", slug="folder-semantics", title="Folder Semantics",
                       when_to_read="before creating files", applies_to=["all"],
                       summary="explains folder layout", date="2026-06-05", regen=False)
            # dateless: no date prefix
            self.assertEqual(path, deck / "docs" / "folder-semantics.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: active", text)
            self.assertIn("summary: explains folder layout", text)
            self.assertIn("when_to_read: before creating files", text)
            self.assertIn("applies_to: [all]", text)
            self.assertIn("last_updated: 2026-06-05", text)
            self.assertIn("# Folder Semantics", text)

    def test_doc_requires_routing_fields(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "doc", slug="bare", title="Bare", regen=False)


class NewValidationTest(unittest.TestCase):
    def test_unknown_kind_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "widget", slug="x", title="X", regen=False)

    def test_status_choices_reject_retired_superseded(self):
        # superseded is retired in 3.0 — the real CLI parser must reject it.
        from flightdeck_new import main
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(SystemExit):
                main([str(deck), "spec", "--slug", "x", "--title", "X",
                      "--status", "superseded"])

    def test_illegal_slug_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            for bad in ["Has Space", "中文", "Upper", "under_score", ""]:
                with self.assertRaises(ValueError):
                    new(deck, "spec", slug=bad, title="X", regen=False)

    def test_missing_title_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "spec", slug="x", title="", regen=False)

    def test_workflow_without_summary_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "spec", slug="x", title="X", status="idea", regen=False)

    def test_knowledge_without_routing_fields_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "incident", slug="x", title="X", regen=False)

    def test_implements_on_knowledge_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "incident", slug="x", title="X", when_to_read="w",
                    applies_to=["a"], implements="specs/x.md", regen=False)

    def test_refuses_if_exists(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            new(deck, "spec", slug="dup", title="Dup", summary="g", status="idea", regen=False)
            with self.assertRaises(FileExistsError):
                new(deck, "spec", slug="dup", title="Dup", summary="g", status="idea", regen=False)


class NewRegenTest(unittest.TestCase):
    def _full_deck(self, d):
        """A deck with the INDEX/cockpit files regen needs (copy from scaffold)."""
        import shutil
        scaffold = Path(__file__).resolve().parent.parent.parent / "scaffolds" / "full" / "flightdeck"
        deck = Path(d) / "flightdeck"
        shutil.copytree(scaffold, deck)
        return deck

    def test_regen_after_active_spec_leaves_index_clean(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._full_deck(d)
            new(deck, "spec", slug="demo", title="Demo",
                status="active", summary="demo gist", date="2026-06-04", regen=True)
            self.assertEqual(flightdeck_index.index_drift(deck), [])


class SkillContractConsistencyTest(unittest.TestCase):
    """skills/new/SKILL.md is the authoring contract's prose face; its
    `kind → folder` table must not drift from flightdeck_new.KIND_FOLDER.
    (2026-06-05: it had — `chart` showed `charts/`, `doc` was missing.)"""

    def _skill_table(self):
        skill = (Path(__file__).resolve().parents[2] / "skills" / "new" / "SKILL.md")
        text = skill.read_text(encoding="utf-8")
        # rows shaped `| <kind> | `<folder>/` |` — backtick on the folder cell
        # excludes the header (`| kind | folder |`) and separator (`|---|---|`).
        pairs = re.findall(r"^\|\s*([a-z0-9-]+)\s*\|\s*`([a-z0-9/]+?)/?`\s*\|", text, re.M)
        return {kind: folder for kind, folder in pairs}

    def test_skill_kind_folder_table_matches_script(self):
        self.assertEqual(self._skill_table(), KIND_FOLDER)


class IncidentSignatureScaffoldTest(unittest.TestCase):
    def test_incident_body_has_signature_and_resolved_by(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "incident", slug="x", title="X",
                       when_to_read="w", applies_to=["a"], regen=False)
            text = path.read_text(encoding="utf-8")
            self.assertIn("resolved_by:", text)        # frontmatter 字段（空）
            self.assertIn("## Signature", text)         # 正文 scaffold
            self.assertIn("- symptom:", text)
            self.assertIn("## Cases", text)

    def test_non_incident_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "checklist", slug="y", title="Y",
                       when_to_read="w", applies_to=["a"], regen=False)
            self.assertNotIn("## Signature", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
