"""Byte-parity for flightdeck_init / flightdeck_new — the artifact-stamping ports.

init seeds a deck from the scaffold; new stamps an artifact + regenerates INDEX.
Both take a target/date/user, so they are pinned deterministically here and the
created tree is byte-compared (LF-normalized) rather than the path-bearing stdout.
Skips when node is absent.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
HAVE_NODE = shutil.which("node") is not None


def _lf(b):
    return b.replace(b"\r\n", b"\n")


def _tree(root):
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root)).replace("\\", "/")] = _lf(p.read_bytes())
    return out


def _run(stem, interp, args):
    ext = ".py" if interp[0] == sys.executable else ".js"
    return subprocess.run(interp + [str(SCRIPTS / (stem + ext)), *args], capture_output=True)


@unittest.skipUnless(HAVE_NODE, "node not on PATH")
class InitParity(unittest.TestCase):
    def test_seed(self):
        py_t = Path(tempfile.mkdtemp())
        js_t = Path(tempfile.mkdtemp())
        common = ["--name", "p", "--user", "yueli", "--date", "2026-06-03", "--focus", "f", "--next", "n"]
        _run("flightdeck_init", [sys.executable], [str(py_t), *common])
        _run("flightdeck_init", ["node"], [str(js_t), *common])
        self.assertEqual(_tree(py_t / "flightdeck"), _tree(js_t / "flightdeck"))

    def test_refuses(self):
        t = Path(tempfile.mkdtemp())
        _run("flightdeck_init", [sys.executable], [str(t), "--date", "2026-06-03"])
        rc_py = _run("flightdeck_init", [sys.executable], [str(t), "--date", "2026-06-03"]).returncode
        rc_js = _run("flightdeck_init", ["node"], [str(t), "--date", "2026-06-03"]).returncode
        self.assertEqual(rc_py, 2)
        self.assertEqual(rc_js, 2)


@unittest.skipUnless(HAVE_NODE, "node not on PATH")
class NewParity(unittest.TestCase):
    def _seed_deck(self):
        t = Path(tempfile.mkdtemp())
        _run("flightdeck_init", [sys.executable], [str(t), "--date", "2026-06-03", "--name", "p"])
        return t / "flightdeck"

    def _stamp(self, interp, deck, args):
        return _run("flightdeck_new", interp, [str(deck), *args])

    def test_stamp_plan_and_index(self):
        # stamp the same artifact under both into two deck copies, compare trees
        py_deck = self._seed_deck()
        js_deck_src = self._seed_deck()
        args = ["plan", "--slug", "do-x", "--title", "Do X", "--status", "active",
                "--summary", "A plan to do x", "--implements", "specs/2026-01-01-thing.md"]
        self._stamp([sys.executable], py_deck, args)
        self._stamp(["node"], js_deck_src, args)
        self.assertEqual(_tree(py_deck), _tree(js_deck_src))

    def test_stamp_idea_dateless(self):
        py_deck = self._seed_deck()
        js_deck = self._seed_deck()
        args = ["spec", "--slug", "an-idea", "--title", "An Idea"]  # default status idea → dateless
        self._stamp([sys.executable], py_deck, args)
        self._stamp(["node"], js_deck, args)
        self.assertEqual(_tree(py_deck), _tree(js_deck))


if __name__ == "__main__":
    unittest.main()
