"""Home-env-pinned byte-parity for the ~/.flightdeck-dependent index subcommands
(--sync-status / --list-consumers / --prune-consumers). Kept out of the deck
matrix so it never touches the real home dir: HOME/USERPROFILE are redirected at
a throwaway master. Skips when node is absent.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).resolve().parent / "parity" / "fixture_deck"
HAVE_NODE = shutil.which("node") is not None


def _lf(b):
    return b.replace(b"\r\n", b"\n")


def _run(interp, deck, extra, env=None):
    ext = ".py" if interp[0] == sys.executable else ".js"
    cmd = interp + [str(SCRIPTS / ("flightdeck_index" + ext)), str(deck), *extra]
    p = subprocess.run(cmd, capture_output=True, env=env)
    return p.returncode, _lf(p.stdout)


def _both(deck, extra, env=None):
    rc_py, out_py = _run([sys.executable], deck, extra, env)
    rc_js, out_js = _run(["node"], deck, extra, env)
    return (rc_py, out_py), (rc_js, out_js)


@unittest.skipUnless(HAVE_NODE, "node not on PATH")
class SyncParity(unittest.TestCase):
    def _master_home(self):
        home = Path(tempfile.mkdtemp())
        master = home / ".flightdeck"
        (master / "references").mkdir(parents=True)
        return home, master

    def _env(self, home):
        env = dict(os.environ)
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
        return env

    def test_sync_status(self):
        home, master = self._master_home()
        # master references/imported.md: empty shared body → differs from the
        # fixture deck's body → stale (fingerprint-keyed; last_updated no longer matters)
        (master / "references" / "imported.md").write_text(
            "---\nsynced: true\nlast_updated: 2026-01-09\n---\n", encoding="utf-8"
        )
        deck_root = Path(tempfile.mkdtemp())
        deck = deck_root / "flightdeck"
        shutil.copytree(FIXTURE, deck)
        # add a synced file with NO master twin (dangling)
        (deck / "docs" / "synced-orphan.md").write_text(
            "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nsynced: true\nlast_updated: 2026-01-01\n---\n",
            encoding="utf-8",
        )
        (py, jsr) = _both(deck, ["--sync-status"], self._env(home))
        self.assertEqual(py, jsr)

    def test_sync_pull_check(self):
        # Dry-run mechanical pull: one synced file whose shared region differs
        # from its master twin → exactly one would-pull line, exit 1, py==js.
        home, master = self._master_home()
        (master / "checklists").mkdir(parents=True)
        (master / "checklists" / "commits.md").write_text(
            "---\n---\n# Commits\n\nMASTER shared body\n", encoding="utf-8"
        )
        deck = Path(tempfile.mkdtemp()) / "flightdeck"
        (deck / "checklists").mkdir(parents=True)
        # marker present so the drift is pull-eligible `stale` (not `marker-missing`)
        (deck / "checklists" / "commits.md").write_text(
            "---\nsynced: true\nlast_updated: 2026-01-01\n---\n# Commits\n\nDECK drifted body\n"
            "<!-- flightdeck:project-specific -->\n\n## Project overrides\n",
            encoding="utf-8",
        )
        (py, jsr) = _both(deck, ["--sync-pull", "--check"], self._env(home))
        self.assertEqual(py, jsr)
        self.assertEqual(py[0], 1)                                    # one stale → exit 1
        self.assertEqual(py[1], b"would-pull\tchecklists/commits.md\n")

    def test_list_consumers(self):
        home, master = self._master_home()
        existing = Path(tempfile.mkdtemp()).resolve().as_posix()
        (master / "shared.md").write_text(
            f'---\nsynced: true\nconsumers: ["{existing}"]\nlast_updated: 2026-01-01\n---\n',
            encoding="utf-8",
        )
        (py, jsr) = _both(master, ["--list-consumers"])
        self.assertEqual(py, jsr)

    def test_prune_consumers(self):
        home, master = self._master_home()
        gone = (Path(tempfile.mkdtemp()) / "gone-deck").resolve().as_posix()  # parent exists, child absent
        body = f'---\nsynced: true\nconsumers: ["{gone}"]\nlast_updated: 2026-01-01\n---\n'
        m_py = master.parent / "m_py" / ".flightdeck"
        m_js = master.parent / "m_js" / ".flightdeck"
        for m in (m_py, m_js):
            m.mkdir(parents=True)
            (m / "shared.md").write_text(body, encoding="utf-8")
        rc_py, out_py = _run([sys.executable], m_py, ["--prune-consumers"])
        rc_js, out_js = _run(["node"], m_js, ["--prune-consumers"])
        self.assertEqual(out_py, out_js)
        # and the mutated master files match
        self.assertEqual(
            _lf((m_py / "shared.md").read_bytes()),
            _lf((m_js / "shared.md").read_bytes()),
        )


if __name__ == "__main__":
    unittest.main()
