import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def _run(script, project_dir, *, plugin_root=None, extra_env=None, stdin=""):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root or REPO)
    env.pop("CURSOR_PLUGIN_ROOT", None)
    env.pop("COPILOT_CLI", None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [BASH, str(REPO / "hooks" / script)],
        input=stdin, capture_output=True, text=True, encoding="utf-8", env=env,
    )


def _mk_deck(tmp_path, cockpit_text=None):
    deck = tmp_path / "flightdeck"
    deck.mkdir()
    if cockpit_text is not None:
        (deck / "cockpit.md").write_text(cockpit_text, encoding="utf-8")
    return tmp_path


def test_session_start_injects_when_deck_present(tmp_path):
    proj = _mk_deck(tmp_path, "# Cockpit\n**Active focus**: ship X\n\n## 下一步\n\n- do Y\n")
    r = _run("session-start", proj)
    assert r.returncode == 0
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "EXTREMELY_IMPORTANT" in ctx
    assert "ship X" in ctx and "do Y" in ctx  # dynamic anchor present
    assert "flightdeck-cockpit-anchor" in ctx


def test_session_start_silent_without_deck(tmp_path):
    r = _run("session-start", tmp_path)  # no flightdeck/ dir
    assert r.returncode == 0
    assert json.loads(r.stdout) == {}


def test_session_start_static_only_when_cockpit_missing(tmp_path):
    proj = _mk_deck(tmp_path, cockpit_text=None)  # deck dir but no cockpit.md
    r = _run("session-start", proj)
    assert r.returncode == 0
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "EXTREMELY_IMPORTANT" in ctx               # static directive still injected
    assert "flightdeck-cockpit-anchor" not in ctx     # dynamic anchor skipped


def test_session_start_cursor_field(tmp_path):
    proj = _mk_deck(tmp_path, "**Active focus**: z\n\n## 下一步\n- w\n")
    r = _run("session-start", proj, extra_env={"CURSOR_PLUGIN_ROOT": str(REPO)})
    assert r.returncode == 0
    assert "additional_context" in json.loads(r.stdout)


def test_stop_regens_board_and_exits_zero(tmp_path):
    # Use the real dogfood deck so flightdeck_index.py has a valid target.
    r = _run("stop", REPO)
    assert r.returncode == 0
    chk = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "flightdeck_index.py"),
         str(REPO / "flightdeck"), "--check"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert chk.returncode == 0 and "clean" in chk.stdout


def test_stop_silent_without_deck(tmp_path):
    r = _run("stop", tmp_path)
    assert r.returncode == 0
