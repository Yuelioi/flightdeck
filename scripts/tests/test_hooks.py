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
    proj = _mk_deck(tmp_path, "# Cockpit\n**Active focus**: ship X\n\n## Next\n\n- do Y\n")
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
    proj = _mk_deck(tmp_path, "**Active focus**: z\n\n## Next\n- w\n")
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
    proj = _mk_deck(tmp_path, "**Active focus**: c\n\n## Next\n- c1\n")
    r = _run_host("session-start", {"CODEX_PLUGIN_ROOT": "x"},
                  project_env={"CLAUDE_PROJECT_DIR": proj})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert "hookSpecificOutput" in out
    assert "additionalContext" in out["hookSpecificOutput"]


def test_gemini_emit_and_projectdir_via_gemini_var(tmp_path):
    # GEMINI_PROJECT_DIR is the ONLY project signal → also tests project-dir resolution.
    proj = _mk_deck(tmp_path, "**Active focus**: g\n\n## Next\n- g1\n")
    r = _run_host("session-start", {"GEMINI_PROJECT_DIR": str(proj)})
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert "hookSpecificOutput" in out
    assert "additionalContext" in out["hookSpecificOutput"]
    assert "g1" in out["hookSpecificOutput"]["additionalContext"]


def _mk_regenerable_deck(tmp_path):
    proj = _mk_deck(
        tmp_path,
        "# Cockpit\n**Active focus**: t\n\n## In Progress\n\n"
        "<!-- AUTO:inprogress -->\n<!-- /AUTO -->\n\n## Next\n- x\n",
    )
    # A specs/ folder with an artifact but no specs/INDEX.md — the stop hook's
    # regen must create that folder INDEX, the side-effect we assert below.
    specs = proj / "flightdeck" / "specs"
    specs.mkdir()
    (specs / "2026-06-01-a.md").write_text(
        "---\nstatus: active\nsummary: regen proof\n---\n", encoding="utf-8"
    )
    return proj


def test_stop_projectdir_via_gemini_var(tmp_path):
    # GEMINI_PROJECT_DIR is the only project signal; $PWD points at REPO. The side
    # effect (specs/INDEX.md created in the TEMP deck, not REPO) proves resolution used it.
    proj = _mk_regenerable_deck(tmp_path)
    r = _run_host("stop", {"GEMINI_PROJECT_DIR": str(proj)})
    assert r.returncode == 0
    assert (proj / "flightdeck" / "specs" / "INDEX.md").exists()


def test_stop_projectdir_via_cursor_var(tmp_path):
    proj = _mk_regenerable_deck(tmp_path)
    r = _run_host("stop", {"CURSOR_PROJECT_ROOT": str(proj)})
    assert r.returncode == 0
    assert (proj / "flightdeck" / "specs" / "INDEX.md").exists()


def test_hook_debug_stop_emits_diagnostics(tmp_path):
    # tmp_path has no flightdeck/ -> stop exits at the gate; debug must narrate it.
    r = _run_host("stop", {"FLIGHTDECK_HOOK_DEBUG": "1", "GEMINI_PROJECT_DIR": str(tmp_path)})
    assert r.returncode == 0
    assert "flightdeck-hook" in r.stderr
    assert "project-dir" in r.stderr or "gate" in r.stderr


def test_hook_debug_session_start_emits_diagnostics(tmp_path):
    r = _run_host("session-start",
                  {"FLIGHTDECK_HOOK_DEBUG": "1", "GEMINI_PROJECT_DIR": str(tmp_path)})
    assert r.returncode == 0
    assert "flightdeck-hook" in r.stderr


def test_hook_debug_silent_by_default(tmp_path):
    r1 = _run_host("stop", {"GEMINI_PROJECT_DIR": str(tmp_path)})
    r2 = _run_host("session-start", {"GEMINI_PROJECT_DIR": str(tmp_path)})
    assert r1.returncode == 0 and r1.stderr == ""
    assert r2.returncode == 0 and r2.stderr == ""


def _cursor_rule(proj):
    return proj / ".cursor" / "rules" / "flightdeck-context.mdc"


def test_cursor_session_start_writes_rule_file(tmp_path):
    proj = _mk_deck(tmp_path, "**Active focus**: cur\n\n## Next\n- cur1\n")
    r = _run_host("session-start",
                  {"CURSOR_PLUGIN_ROOT": "x", "CURSOR_PROJECT_ROOT": str(proj)})
    assert r.returncode == 0
    assert "additional_context" in json.loads(r.stdout)  # belt-and-suspenders still emits
    rule = _cursor_rule(proj)
    assert rule.exists()
    txt = rule.read_text(encoding="utf-8")
    assert "alwaysApply: true" in txt
    assert "EXTREMELY_IMPORTANT" in txt       # bootstrap body
    assert "cur1" in txt                       # cockpit anchor (Next)
    assert "flightdeck-cockpit-anchor" in txt


def test_cursor_stop_refreshes_rule_file(tmp_path):
    proj = _mk_regenerable_deck(tmp_path)
    r = _run_host("stop", {"CURSOR_PLUGIN_ROOT": "x", "CURSOR_PROJECT_ROOT": str(proj)})
    assert r.returncode == 0
    rule = _cursor_rule(proj)
    assert rule.exists()
    assert "alwaysApply: true" in rule.read_text(encoding="utf-8")


def test_non_cursor_writes_no_rule_file(tmp_path):
    # A Gemini/Claude session must NOT spray a .cursor/ dir into the project.
    proj = _mk_deck(tmp_path, "**Active focus**: g\n\n## Next\n- g1\n")
    r = _run_host("session-start", {"GEMINI_PROJECT_DIR": str(proj)})
    assert r.returncode == 0
    assert not _cursor_rule(proj).exists()
