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


# --- Phase 1: cross-host hook wiring ---

def test_codex_hooks_config_shape():
    cfg = json.loads((REPO / "hooks" / "hooks-codex.json").read_text(encoding="utf-8"))
    assert "SessionStart" in cfg["hooks"]
    assert "Stop" in cfg["hooks"]
    cmds = [h["command"] for grp in cfg["hooks"]["SessionStart"] for h in grp["hooks"]]
    assert any("run-hook.cmd" in c and "session-start" in c for c in cmds)
    stop_cmds = [h["command"] for grp in cfg["hooks"]["Stop"] for h in grp["hooks"]]
    assert any("run-hook.cmd" in c and "stop" in c for c in stop_cmds)


def test_codex_plugin_manifest_declares_hooks():
    mf = json.loads((REPO / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert mf.get("hooks") == "./hooks/hooks-codex.json"


def test_cursor_has_stop_hook():
    cfg = json.loads((REPO / "hooks" / "hooks-cursor.json").read_text(encoding="utf-8"))
    assert "stop" in cfg["hooks"]
    assert any("stop" in h["command"] for h in cfg["hooks"]["stop"])


def test_gemini_hooks_config_shape():
    cfg = json.loads((REPO / "hooks" / "hooks-gemini.json").read_text(encoding="utf-8"))
    assert "SessionStart" in cfg["hooks"]
    assert "AfterAgent" in cfg["hooks"]
    cmds = [h["command"] for grp in cfg["hooks"]["SessionStart"] for h in grp["hooks"]]
    assert any("run-hook.cmd" in c and "session-start" in c for c in cmds)
    after = [h["command"] for grp in cfg["hooks"]["AfterAgent"] for h in grp["hooks"]]
    assert any("run-hook.cmd" in c and "stop" in c for c in after)


def _run_host(script, host_env, *, project_env=None, stdin=""):
    """Run a hook with all host vars cleared, then apply only host_env.
    project_env keys (e.g. CLAUDE_PROJECT_DIR / GEMINI_PROJECT_DIR) locate the deck."""
    env = dict(os.environ)
    for k in ("CLAUDE_PLUGIN_ROOT", "CURSOR_PLUGIN_ROOT", "CURSOR_PROJECT_ROOT",
              "GEMINI_PROJECT_DIR", "CODEX_PLUGIN_ROOT", "COPILOT_CLI",
              "CLAUDE_PROJECT_DIR"):
        env.pop(k, None)
    if project_env:
        env.update({k: str(v) for k, v in project_env.items()})
    env.update({k: str(v) for k, v in host_env.items()})
    return subprocess.run(
        [BASH, str(REPO / "hooks" / script)],
        input=stdin, capture_output=True, text=True, encoding="utf-8", env=env,
    )


def test_codex_emit_uses_hookSpecificOutput(tmp_path):
    proj = _mk_deck(tmp_path, "**Active focus**: c\n\n## 下一步\n- c1\n")
    r = _run_host("session-start", {"CODEX_PLUGIN_ROOT": "x"},
                  project_env={"CLAUDE_PROJECT_DIR": proj})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert "hookSpecificOutput" in out
    assert "additionalContext" in out["hookSpecificOutput"]


def test_gemini_emit_and_projectdir_via_gemini_var(tmp_path):
    # GEMINI_PROJECT_DIR is the ONLY project signal → also tests project-dir resolution.
    proj = _mk_deck(tmp_path, "**Active focus**: g\n\n## 下一步\n- g1\n")
    r = _run_host("session-start", {"GEMINI_PROJECT_DIR": str(proj)})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert "hookSpecificOutput" in out
    assert "additionalContext" in out["hookSpecificOutput"]
    assert "g1" in out["hookSpecificOutput"]["additionalContext"]
