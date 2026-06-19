"""Byte-parity harness: every Node script must match its Python twin.

Runs `python <name>.py <args>` and `node <name>.js <args>` over identical
fixture copies, LF-normalizes (Python's write_text emits CRLF on Windows; the
parity contract is *content*, spec §3.3 "换行恒 LF"), and asserts equality of
stdout and of the full mutated .md tree. Skips when node is absent or the .js
does not exist yet — so it arms incrementally as ports land.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).resolve().parent / "parity" / "fixture_deck"
HAVE_NODE = shutil.which("node") is not None


def _lf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def _copy_deck() -> Path:
    d = Path(tempfile.mkdtemp())
    shutil.copytree(FIXTURE, d / "flightdeck")
    return d / "flightdeck"


def _run(interp, script, deck, extra):
    cmd = interp + [str(SCRIPTS / script), str(deck), *extra]
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, _lf(p.stdout), _lf(p.stderr)


def _tree_snapshot(deck: Path):
    out = {}
    for p in sorted(deck.rglob("*.md")):
        out[str(p.relative_to(deck)).replace("\\", "/")] = _lf(p.read_bytes())
    return out


class ParityBase(unittest.TestCase):
    stem = None  # e.g. "flightdeck_index"

    def assert_parity(self, extra, mutates=False):
        if not HAVE_NODE:
            self.skipTest("node not on PATH")
        js = SCRIPTS / f"{self.stem}.js"
        if not js.is_file():
            self.skipTest(f"{js.name} not ported yet")
        py_deck = _copy_deck()
        js_deck = _copy_deck()
        rc_py, out_py, _ = _run([sys.executable], f"{self.stem}.py", py_deck, extra)
        rc_js, out_js, _ = _run(["node"], f"{self.stem}.js", js_deck, extra)
        self.assertEqual(out_py, out_js, f"stdout diff for {self.stem} {extra}")
        self.assertEqual(rc_py, rc_js, f"exit-code diff for {self.stem} {extra}")
        if mutates:
            self.assertEqual(
                _tree_snapshot(py_deck), _tree_snapshot(js_deck),
                f"mutated-tree diff for {self.stem} {extra}",
            )


class IndexParity(ParityBase):
    stem = "flightdeck_index"

    def test_regen(self):
        self.assert_parity([], mutates=True)

    def test_check(self):
        self.assert_parity(["--check"])

    def test_archivable(self):
        self.assert_parity(["--archivable"])

    def test_advance(self):
        self.assert_parity(["--advance-candidates"])

    def test_verify_pending(self):
        self.assert_parity(["--verify-pending"])

    def test_match_signature(self):
        self.assert_parity(["--match-signature", "boom"])


class LintParity(ParityBase):
    stem = "flightdeck_lint"

    def test_default(self):
        self.assert_parity([])


if __name__ == "__main__":
    unittest.main()
