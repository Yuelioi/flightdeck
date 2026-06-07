---
status: active
summary: 把 auto-land 执行层 spec 落地的逐文件实施——新增 hooks/（run-hook.cmd + session-start 注入 + stop 被动 board-sync + hooks.json/hooks-cursor.json）+ skills/_shared/bootstrap.md，接 Cursor/Gemini manifest，加 hook 测试；再做 Layer 3 文档改写（exit-ritual board-AUTO 移出 agent 顾虑、protocol/landing 同步、why-no-hooks 前提部分失效改写 + 新决策原则、session-flow 纳入注入入场 + Stop board-sync）
last_updated: 2026-06-06
implements: specs/2026-06-06-auto-land-executor.md
---

# auto-land 执行层落地实施 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 spec `2026-06-06-auto-land-executor` 定义的执行层做出来：① 脚本焊死 board-sync（Claude Stop hook 每回合结尾静默 regen `## 进行中` + INDEX 的 AUTO 区，不 block / 不归档）；② session-start 注入（全工具薄胶水 + 单一真相源 bootstrap），开场第 0 turn 进入 preflight 接手态 + 知识落盘强制令常驻；③ Layer 3 把机械 AUTO 区移出 agent 回合结尾顾虑、改写 why-no-hooks 抽出新 hook 决策原则、session-flow 纳入新主干。

**Architecture:** 三层职责正交（spec § 设计）。Layer 1（session-start）+ Layer 2（Stop）是**新 `hooks/` 目录** + 跨平台 polyglot wrapper（near-verbatim 采用 `flightdeck/references/superpowers/hooks/run-hook.cmd`）；触发胶水每工具一薄层（Claude 靠约定自动发现 `hooks/hooks.json`；Cursor `.cursor-plugin/plugin.json` 加 `hooks` 键指向 `hooks-cursor.json`；Gemini `GEMINI.md` `@`-include bootstrap；Codex 走 AGENTS.md，效果未实证）。**复用 `scripts/flightdeck_index.py <deck>` 做 board-sync，不新增脚本接口。** Layer 3 是纯文档工程。

**Tech Stack:** bash hook 脚本（Git-Bash on Windows 经 polyglot `.cmd` 兜底）；`scripts/flightdeck_index.py`（board-sync 复用 + 只读校验）、`scripts/flightdeck_lint.py`（dangling-ref 校验）；pytest（hook 行为测试，subprocess 调 bash）。

**约定（全 plan 通用）：**
- **single source of truth = `skills/_shared/bootstrap.md`**：静态强制令只此一份，session-start 注入它、Gemini/Codex include 它。任何工具要改强制令措辞，只改这一处。
- **hook 永不 block、永不报错退出**：session-start 与 stop 都以 `exit 0` 收尾；缺 bash / 缺 python / 缺 `flightdeck/` → 静默降级（退回手动 preflight），绝不打断会话。这是 spec 的硬底线。
- **语言**：hook 注入文案 + skill prose 是英文（措辞可按邻近风格微调，不是 placeholder）；**「已保存」标记 + cockpit board 保持中文**。
- **commit**：本仓库 commit 由 landing 管、**never push**（见 memory `never-push-only-commit`）。逐 task 改完跑 checkpoint（推进下方 `current:` 指针，disk-only），**不在 task 末尾单独 commit**；全部完成后 Task 13 收尾（hooks 是 `feat`、Layer 3 是 `docs`，按 `checklists/commits.md` §4 原子性**分两个 commit**）。
- **每个 task 的"验证"**：代码 task 跑对应 pytest；文档 task 跑 `flightdeck_lint.py flightdeck`（无新 dangling-ref）+ `grep` 确认跨文件锚点/术语一致 + 读改动节确认与 spec 对应节一致。
- **双 shell commit 坑**：多行 commit message 经 `git commit -F <file>`，**别用 PowerShell here-string 过 Bash tool**（见 incident `powershell-herestring-in-bash-tool`）。
- **死链警惕**：skill prose 加任何 `[text](#anchor)` 前先确认锚点存在（见 incident `skill-prose-links-into-dogfood-deck`）。
- **scaffold 逐字 ship**：`hooks/` 是 plugin 内容、随插件分发，注意它在用户项目里跑（deck 在 cwd、脚本在 `$CLAUDE_PLUGIN_ROOT`），见 incident `scaffold-ships-verbatim` 的同源精神。

## Progress

current: done — all 13 tasks implemented; 149 tests pass, index --check clean, lint clean. Status stays `active` until live-verify + user approval to land (archive deferred to next /flightdeck:landing).

---

### Task 1: `hooks/run-hook.cmd` —— 跨平台 polyglot wrapper（near-verbatim 采用 superpowers）

**Files:**
- Create: `hooks/run-hook.cmd`
- Reference: `flightdeck/references/superpowers/hooks/run-hook.cmd`（已验证版，逐行采用）

- [ ] **Step 1: 写 wrapper（与 superpowers 版逐字相同，仅注释里项目名改 flightdeck）**

```cmd
: << 'CMDBLOCK'
@echo off
REM Cross-platform polyglot wrapper for flightdeck hook scripts.
REM On Windows: cmd.exe runs the batch portion, which finds and calls bash.
REM On Unix: the shell interprets this as a script (: is a no-op in bash).
REM
REM Hook scripts use extensionless filenames (e.g. "session-start" not
REM "session-start.sh") so Claude Code's Windows auto-detection -- which
REM prepends "bash" to any command containing .sh -- doesn't interfere.
REM
REM Usage: run-hook.cmd <script-name> [args...]

if "%~1"=="" (
    echo run-hook.cmd: missing script name >&2
    exit /b 1
)

set "HOOK_DIR=%~dp0"

REM Try Git for Windows bash in standard locations
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM Try bash on PATH (e.g. user-installed Git Bash, MSYS2, Cygwin)
where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM No bash found - exit silently rather than error
REM (plugin still works, just without SessionStart context injection / board-sync)
exit /b 0
CMDBLOCK

# Unix: run the named script directly
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$1"
shift
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
```

- [ ] **Step 2: 验证**

Run: `python -c "import pathlib,sys; t=pathlib.Path('hooks/run-hook.cmd').read_text(); sys.exit(0 if 'CMDBLOCK' in t and 'exit /b 0' in t and 'No bash found' in t else 1)"`
Expected: exit 0（polyglot 结构 + 无 bash 静默降级分支都在）。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 2`。

---

### Task 2: `skills/_shared/bootstrap.md` —— 静态强制令单一真相源

**Files:**
- Create: `skills/_shared/bootstrap.md`

- [ ] **Step 1: 写 bootstrap（自带 `<EXTREMELY_IMPORTANT>` 包裹，使 Gemini/Codex `@`-include 时独立生效；session-start 原样注入，不再外包一层）**

```markdown
<EXTREMELY_IMPORTANT>
This project uses **flightdeck** — a `flightdeck/` deck is present at the project root.

**On entry (handoff, from turn 0):** before doing anything else, take over per the
`/flightdeck:preflight` protocol — read `flightdeck/cockpit.md` (`Active focus`, `## 进行中`,
`## 下一步`) and the folder `INDEX.md` files, then report the next step. You are already in
*handoff* mode; the user does NOT need to type `/flightdeck:preflight` for you to read the
cockpit and continue the prior thread.

**On exit (end-of-turn, before returning control):** if this turn produced **write-gated
knowledge** — something that changes future behavior, influences a decision, or will be
referenced repeatedly (protocol § Write gate; transient byproducts and pure Q&A do NOT count) —
you MUST **soft-land** before you stop: persist the knowledge + board state and print the
「已保存」marker. Do not answer-then-stop and leave the increment unpersisted. A **state-only**
increment (board moved, no new knowledge) → run a silent **checkpoint** instead. **No** increment
→ say nothing.

This directive is the single source of truth shared across every host (Claude Code, Cursor,
Gemini, Codex). The mechanical part of board-sync (`## 进行中` + each `INDEX.md` AUTO region) is
additionally welded by a Stop hook on Claude Code — but the *judgment* parts above (entry handoff,
knowledge classification, `## 下一步` / `Active focus`) are always yours.
</EXTREMELY_IMPORTANT>
```

- [ ] **Step 2: 验证**

Run: `python -c "import pathlib,sys; t=pathlib.Path('skills/_shared/bootstrap.md').read_text(encoding='utf-8'); sys.exit(0 if '<EXTREMELY_IMPORTANT>' in t and 'soft-land' in t and 'preflight' in t and '已保存' in t else 1)"`
Expected: exit 0。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 3`。

---

### Task 3: `hooks/session-start` —— 入场注入（gate + bootstrap + 动态 cockpit 锚点 + 平台分支）

**Files:**
- Create: `hooks/session-start`（extensionless bash，可执行）
- Reference: `flightdeck/references/superpowers/hooks/session-start`（escape_for_json + 平台分支照搬）

- [ ] **Step 1: 写脚本**

护栏（采纳 spec § Layer 1）：gate = 项目根存在 `flightdeck/` 目录；`flightdeck/` 在但 `cockpit.md` 缺/读不出 → **仍注入静态 bootstrap**、只跳过动态锚点；无 `flightdeck/` → 输出空 `{}`、彻底闭嘴。`exit 0` 收尾。

```bash
#!/usr/bin/env bash
# SessionStart hook for flightdeck: inject the bootstrap directive + a live
# cockpit anchor so the agent enters in preflight-handoff mode from turn 0.
# Never errors out — degrades to silence (manual preflight still works).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Resolve the project dir the hook is running against.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-${CURSOR_PROJECT_ROOT:-$PWD}}"

emit() {
  # $1 = the context string (already the final injected text)
  local ctx; ctx="$(escape_for_json "$1")"
  if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
    printf '{\n  "additional_context": "%s"\n}\n' "$ctx"
  elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -z "${COPILOT_CLI:-}" ]; then
    printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "SessionStart",\n    "additionalContext": "%s"\n  }\n}\n' "$ctx"
  else
    printf '{\n  "additionalContext": "%s"\n}\n' "$ctx"
  fi
}

escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"; s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"; s="${s//$'\r'/\\r}"; s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

# Gate: no deck here → say nothing.
if [ ! -d "${PROJECT_DIR}/flightdeck" ]; then
  printf '{}\n'
  exit 0
fi

# Static directive (single source of truth). Missing bootstrap is a packaging
# bug, not a user state — degrade to silence rather than inject a broken anchor.
bootstrap="$(cat "${PLUGIN_ROOT}/skills/_shared/bootstrap.md" 2>/dev/null || true)"
if [ -z "$bootstrap" ]; then
  printf '{}\n'
  exit 0
fi

# Dynamic cockpit anchor (best-effort; skipped if cockpit missing/empty).
cockpit="${PROJECT_DIR}/flightdeck/cockpit.md"
anchor=""
if [ -s "$cockpit" ]; then
  focus="$(grep -m1 -E '^\*\*Active focus\*\*' "$cockpit" 2>/dev/null || true)"
  # The "## 下一步" section: from its heading to the next "## " heading.
  next="$(awk '/^## 下一步/{f=1;next} /^## /{f=0} f' "$cockpit" 2>/dev/null || true)"
  if [ -n "$focus" ] || [ -n "$next" ]; then
    anchor=$'\n\n<flightdeck-cockpit-anchor note="may lag last turn; reconcile via /flightdeck:preflight">\n'
    anchor+="${focus}"$'\n## 下一步:\n'"${next}"
    anchor+=$'\n</flightdeck-cockpit-anchor>'
  fi
fi

emit "${bootstrap}${anchor}"
exit 0
```

- [ ] **Step 2: 验证（人工跑一遍三种 gate）**

```bash
# 有 deck + cockpit：含 bootstrap + 锚点
CLAUDE_PROJECT_DIR="$PWD" CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/session-start </dev/null | python -c "import sys,json; d=json.load(sys.stdin); c=d['hookSpecificOutput']['additionalContext']; assert 'EXTREMELY_IMPORTANT' in c and 'flightdeck-cockpit-anchor' in c; print('ok-deck')"
# 无 deck：空 {}
CLAUDE_PROJECT_DIR=/tmp CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/session-start </dev/null | python -c "import sys,json; assert json.load(sys.stdin)=={}; print('ok-nodeck')"
```
Expected: 打印 `ok-deck` 和 `ok-nodeck`（JSON 合法、字段正确）。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 4`。

---

### Task 4: `hooks/stop` —— 被动 board-sync（不门控、不归档、永 `exit 0`）

**Files:**
- Create: `hooks/stop`（extensionless bash，可执行）

- [ ] **Step 1: 写脚本**

机制（spec § Layer 2，**不 block**）：gate `flightdeck/` → 找 python → 跑 `flightdeck_index.py <deck>` 静默重生 AUTO 区 → `exit 0`。缺 python / 缺 deck → 静默降级。脚本在 `$CLAUDE_PLUGIN_ROOT/scripts/`，deck 在 `$PROJECT_DIR/flightdeck`。

```bash
#!/usr/bin/env bash
# Stop hook for flightdeck: silently regenerate the board AUTO regions
# (cockpit ## 进行中 + each INDEX.md AUTO region) at end-of-turn. Passive
# only — never decision:block, never archive, never touch judgment fields.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# Gate: no deck → nothing to sync.
[ -d "${PROJECT_DIR}/flightdeck" ] || exit 0

# Locate a python runtime; degrade silently if none.
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || exit 0

index_py="${PLUGIN_ROOT}/scripts/flightdeck_index.py"
[ -f "$index_py" ] || exit 0

# Regenerate AUTO regions; swallow all output (passive, idempotent).
"$PY" "$index_py" "${PROJECT_DIR}/flightdeck" >/dev/null 2>&1 || true
exit 0
```

- [ ] **Step 2: 验证（dogfood：本仓库即一个 deck）**

```bash
CLAUDE_PROJECT_DIR="$PWD" CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/stop; echo "exit=$?"
python scripts/flightdeck_index.py flightdeck --check
```
Expected: `exit=0`；`--check` → `clean`（Stop hook 跑完 board AUTO 区一致、无 drift）。

- [ ] **Step 3: checkpoint** —— `current:` → `Task 5`。

---

### Task 5: `hooks/hooks.json` + `hooks/hooks-cursor.json` —— 触发声明

**Files:**
- Create: `hooks/hooks.json`（Claude：SessionStart + Stop）
- Create: `hooks/hooks-cursor.json`（Cursor：sessionStart）

- [ ] **Step 1: 写 `hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" stop",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: 写 `hooks/hooks-cursor.json`**

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "command": "./hooks/run-hook.cmd session-start"
      }
    ]
  }
}
```

> 注：Cursor 侧只接 `sessionStart`（spec：Cursor = 入场注入；board-sync 焊死是 Claude-only 增强）。Cursor 的 Stop 等价钩子不接——保持"被动同步类 hook 仅 Claude-only deterministic 增强"的决策原则。

- [ ] **Step 3: 验证**

Run: `python -c "import json; json.load(open('hooks/hooks.json')); json.load(open('hooks/hooks-cursor.json')); print('json-ok')"`
Expected: `json-ok`；再确认 `hooks.json` 有 `SessionStart` 与 `Stop` 两个键、命令都指向 `run-hook.cmd`。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 6`。

---

### Task 6: manifest 接线 —— Cursor / Gemini / Codex

**Files:**
- Modify: `.cursor-plugin/plugin.json`（加 `hooks` 键）
- Modify: `GEMINI.md`（`@`-include bootstrap）
- Read/decide: `.codex-plugin/plugin.json` + Codex AGENTS.md 机制

- [ ] **Step 1: `.cursor-plugin/plugin.json` 加 hooks 键**

在 `"skills": "./skills/",` 之后加一行（照 superpowers `.cursor-plugin` 形状）：

```json
  "hooks": "./hooks/hooks-cursor.json",
```

- [ ] **Step 2: `GEMINI.md` 把 bootstrap 放到 `@`-include 列表首行**

在现有 `@./skills/preflight/SKILL.md` 之前插入一行，让强制令最先注入：

```
@./skills/_shared/bootstrap.md
```

- [ ] **Step 3: Claude 侧无需改 manifest（确认）**

`.claude-plugin/plugin.json` **不加 hooks 键**——Claude Code 按约定自动发现 plugin 根的 `hooks/hooks.json`（superpowers 的 `.claude-plugin/plugin.json` 同样无 hooks 键却生效，已核实）。本 step 只读确认、不改文件。

- [ ] **Step 4: Codex 侧——调研 + 落最小接法或诚实标记未实证**

Codex 无富 hooks（见 `flightdeck/docs/why-no-hooks.md` 表）。spec 的 Codex Layer 1 = 指令文件注入、**效果未实证**。本 step：① 查 `.codex-plugin/plugin.json` 是否支持 context-file 字段指向 bootstrap；② 若支持，指向 `skills/_shared/bootstrap.md`；③ 若不支持/不确定，**不硬接**，在 Task 11 的 why-no-hooks 改写里如实记"Codex 仅指令文件、效果未实证、列入测试"。**不为 Codex 造 gating**（spec 非目标）。

- [ ] **Step 5: 验证**

Run: `python -c "import json; d=json.load(open('.cursor-plugin/plugin.json')); assert d['hooks']=='./hooks/hooks-cursor.json'; print('cursor-ok')"`
再 `grep -n "bootstrap.md" GEMINI.md`（确认在首行）。
Expected: `cursor-ok` + GEMINI.md 首行命中。

- [ ] **Step 6: checkpoint** —— `current:` → `Task 7`。

---

### Task 7: hook 行为测试 —— `scripts/tests/test_hooks.py`

**Files:**
- Create: `scripts/tests/test_hooks.py`
- Reference: 既有测试风格 `scripts/tests/test_flightdeck_index.py`

测试经 `subprocess` 调 `bash hooks/<script>`（本机 Git-Bash 可用；CI 无 bash 时 `skip`）。覆盖 spec § 影响的文件·测试清单的四项。

- [ ] **Step 1: 写失败测试**

```python
import json, os, shutil, subprocess, sys
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
        input=stdin, capture_output=True, text=True, env=env,
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
        capture_output=True, text=True,
    )
    assert chk.returncode == 0 and "clean" in chk.stdout


def test_stop_silent_without_deck(tmp_path):
    r = _run("stop", tmp_path)
    assert r.returncode == 0
```

- [ ] **Step 2: 跑测试确认结构正确**

Run: `python -m pytest scripts/tests/test_hooks.py -v`
Expected: 全 PASS（本机 bash 可用）；若环境无 bash → 全 `skip`（不算失败）。

- [ ] **Step 3: 回归——确认没碰坏既有测试**

Run: `python -m pytest scripts/tests/ -q`
Expected: 既有 143 测试 + 新增 hook 测试全通过。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 8`。

---

### Task 8: Layer 3 —— `exit-ritual.md`：board AUTO 移出 agent 回合结尾顾虑（保留判断性看板 + 知识分类）

**Files:**
- Modify: `skills/preflight/exit-ritual.md` —— § Checkpoint（`## Checkpoint — lightweight board-sync subpath`，line ~285）与 § Land-readiness（signal 段，line ~338+）

> correctness（采纳 spec § Layer 3 / gpt）：checkpoint ≠ board-sync。脚本焊死的只有**机械 AUTO 区**（`## 进行中` + INDEX AUTO）；checkpoint 还含刷 `## 下一步` + 推进 plan `current:`，**这俩需判断、仍归 agent**。改写要点是"把机械 AUTO 区从 agent 盘子里拿走、判断部分保留"，**不是**"agent 只剩二元问"。

- [ ] **Step 1: 在 § Checkpoint 加一段"机械 AUTO 区由 Stop hook 焊死"的说明**

在 `## Checkpoint — lightweight board-sync subpath` 段内（§ "Reuse, don't fork" 一段附近）插入：

```markdown
**On Claude Code, the *mechanical* half of board-sync is welded by a Stop hook.** A passive
`Stop` hook regenerates the `## 进行中` AUTO region + each `INDEX.md` `<!-- AUTO -->` region at
every end-of-turn (idempotent `scripts/flightdeck_index.py <deck>`; never blocks, never archives).
So you no longer carry the *mechanical* AUTO regions at turn end — they self-heal. **But a
checkpoint is more than the AUTO region:** refreshing `## 下一步` and advancing the plan's
`## Progress current:` pointer are *judgment* writes and **remain yours** at every plan-task
boundary. On hosts without the hook (Cursor/Gemini/Codex), the AUTO regions ride on the next
`landing`/`status`/`checkpoint` regen as before. This hook is a deterministic Claude-only
enhancement, not a behavior the protocol depends on — see the project's why-no-hooks doc for the
passive-vs-gating hook decision principle.
```

> 死链警惕（incident `skill-prose-links-into-dogfood-deck`）：上面末句**只用纯文本**"see the project's why-no-hooks doc"，**绝不写成 markdown 链接**——skill prose 指向 dogfood deck（`flightdeck/...`）是死链。

- [ ] **Step 2: 在 § Land-readiness 的 signal 机制处，把 board AUTO 的"自动发生"措辞收紧**

在 signal 1/3 机制描述附近补一句（区分脚本焊死 vs agent 判断）：

```markdown
- **What the Stop hook does and does not do.** It regenerates *only* the mechanical AUTO regions
  (`## 进行中` + `INDEX.md`), so those are never stale on Claude Code. It does **not** write
  `## 下一步` / `Active focus`, classify knowledge, flip `done`, commit, or archive — every
  judgment + soft-landing step above is still agent-driven. "Board-sync is automatic" therefore
  means *the AUTO regions*, not the whole checkpoint/soft-landing.
```

- [ ] **Step 3: 验证**

Run: `python scripts/flightdeck_lint.py flightdeck`（确认无新 dangling-ref；尤其上面 Step 1 末句已改纯文本、无指向 dogfood deck 的链接）。
再 `grep -n "Stop hook" skills/preflight/exit-ritual.md` 确认两处插入；读改动节确认"机械 AUTO 焊死、判断仍归 agent"立场清楚、与 spec § Layer 3 一致。
Expected: lint `{"findings": []}`。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 9`。

---

### Task 9: Layer 3 —— `protocol.md` + `landing/SKILL.md` 同步 hook 语义

**Files:**
- Modify: `skills/preflight/protocol.md` —— § Lifecycle（line ~259 附近，end-of-turn 说明）
- Modify: `skills/landing/SKILL.md` —— Modes 段附近

- [ ] **Step 1: protocol.md § Lifecycle 补一句 Stop hook board-sync**

在 end-of-turn debounce 说明附近插入：

```markdown
On Claude Code, a passive `Stop` hook additionally regenerates the mechanical board AUTO regions
(`## 进行中` + `INDEX.md`) at every end-of-turn — a deterministic enhancement that keeps those
regions from going stale between landings. It never blocks, archives, or writes judgment fields;
the protocol does not depend on it (other hosts regen on the next landing/status/checkpoint).
```

- [ ] **Step 2: landing/SKILL.md Modes 段补一句脚本焊死与 landing regen 同源**

在 Modes 表（`## Modes — full · soft-landing · checkpoint`）之后补一句：

```markdown
> The `## 进行中` + `INDEX.md` AUTO regions a landing regenerates are the *same* regions the
> Claude-only Stop hook welds at end-of-turn (one implementation: `flightdeck_index.py <deck>`).
> The hook keeps them fresh between landings; landing still owns archive, promotion gate, and
> commit. No divergence — the hook is a passive subset.
```

- [ ] **Step 3: 验证**

Run: `python scripts/flightdeck_lint.py flightdeck` → `{"findings": []}`。
`grep -n "Stop hook" skills/preflight/protocol.md skills/landing/SKILL.md` 确认；术语（`board AUTO regions` / `flightdeck_index.py <deck>`）跨 exit-ritual/protocol/landing 一致。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 10`。

---

### Task 10: Layer 3 —— `flightdeck/docs/why-no-hooks.md` 改写（前提部分失效 + 新决策原则）

**Files:**
- Modify: `flightdeck/docs/why-no-hooks.md`

> 降调（用户拍板）：**非"正式推翻"**，是"核心前提部分失效、据此调整"。对 **gating/拦截类 hook** 论据仍成立；对 **被动注入/同步类 hook** 被 superpowers 证伪。抽出新决策原则。

- [ ] **Step 1: 标题段加"前提部分失效"的更新说明**

在文首 `# Why flightdeck installs no hooks` 之后、`## 决策` 之前插入一段（中文，与该 doc 风格一致）：

```markdown
## 更新（2026-06-06）：前提部分失效

下面"跨工具 hook 无统一标准"的论据，对 **gating / 拦截类 hook**（PreToolUse 拦操作、强 block
续命）**仍然成立**——那条路是纯兼容包袱，继续拒绝。但对 **被动注入 / 同步类 hook**（无门控、
只在 SessionStart 注入上下文 / 在 Stop 静默重生派生区），superpowers 用 `hooks/run-hook.cmd`
跨平台 polyglot wrapper + 每工具一薄层胶水**证明可移植**。flightdeck 据此采纳了一套被动 hook
（见 `hooks/`、spec `2026-06-06-auto-land-executor`）。所以本文 standpoint 从"任何宿主都不装
hook"修订为下面的**新决策原则**。
```

- [ ] **Step 2: 末尾"由此推论"段替换为新决策原则**

把 `## 由此推论` 段改写为可操作的二分原则：

```markdown
## 决策原则（hook 取舍）

要给 flightdeck 加任何 hook 前，先按类型二分：

- **被动注入 / 同步类**（无门控、胶水可移植、失败即静默降级到手动）→ **接受**。例：SessionStart
  注入 bootstrap + cockpit 锚点；Stop 静默重生 board AUTO 区。代价是每工具一薄层胶水 + 版本兼容
  跟进，明确承认、用维护成本换可靠性。
- **gating / 拦截类**（PreToolUse/PostToolUse 拦操作、`decision:block` 续命、承担业务语义判断）
  → **拒绝**，或仅 **Claude-only 增强且须 deterministic 触发**。理由不变：跨工具无统一标准、纯
  兼容包袱、且 block 对本项目的归账既漏（放行即漏）又矛盾（等于自动触发 full landing）。

以后遇 Resume/Compact/PostToolUse 之类照此判，不再逐个重吵。
```

- [ ] **Step 3: 同步表格/取舍段里"没有任何东西自动触发"的绝对表述**

把 § 取舍 里 "没有任何东西自动触发——入场必须显式 `/flightdeck:preflight`" 收紧为："默认无门控；Claude/Cursor 经被动 SessionStart 注入进入 preflight 接手态，其余宿主仍显式 `/flightdeck:preflight`"。`AGENTS.md` 那条引用（"不是 hooks"）保留。

- [ ] **Step 4: 验证**

Run: `python scripts/flightdeck_index.py flightdeck`（why-no-hooks 是 deck 内 doc，确认 INDEX 行不被破坏）+ `python scripts/flightdeck_lint.py flightdeck` → `{"findings": []}`。
读全文确认：gating 仍拒、被动接受、原则可操作、无自相矛盾（如别处还留"任何 hook 都不装"的绝对句）。
`grep -rn "不装 hook\|不装任何 hook\|installs no hooks" flightdeck/docs/why-no-hooks.md` 复查绝对表述都已收口。

- [ ] **Step 5: checkpoint** —— `current:` → `Task 11`。

---

### Task 11: Layer 3 —— `flightdeck/docs/session-flow.md` 纳入注入入场 + Stop board-sync

**Files:**
- Modify: `flightdeck/docs/session-flow.md` —— 主干图 + 主干逐段 + 两条轴

- [ ] **Step 1: 主干图 [进入] 段补"注入接手"**

把主干图 `[进入] preflight 只读接管` 一格旁补注（中文，对齐该 doc 风格）：Claude/Cursor 经 SessionStart 注入，开场第 0 turn 即处于 preflight 接手态（读 cockpit 锚点），不需手敲 `/flightdeck:preflight`；其余宿主仍显式入场。

- [ ] **Step 2: 主干图 / 收尾段补"回合末 board AUTO 由 Stop hook 焊死"**

在回合末（soft-landing 那支附近）补一行：Claude 的 Stop hook 每回合结尾静默重生 `## 进行中` + INDEX 的 AUTO 区（机械、幂等、不 commit/不归档），所以**机械看板永不漂**；判断性看板（`## 下一步`/`Active focus`/plan `current:`）+ 知识落盘仍由 agent（soft-landing/checkpoint）做。

- [ ] **Step 3: 两条轴或分叉表点一句**

在 § "两条贯穿全程的轴" 的"看板恒在盘上"一条里补半句：在 Claude 上机械 AUTO 区还额外由 Stop hook 焊死，进一步保证"随时关掉、下次干净接手"。

- [ ] **Step 4: 验证**

Run: `python scripts/flightdeck_index.py flightdeck`（确认 session-flow 的 INDEX 行不破）+ `python scripts/flightdeck_lint.py flightdeck` → `{"findings": []}`（doc 内既有链接仍有效）。
读改动确认主干图仍自洽、注入入场与 Stop board-sync 表述与 spec/why-no-hooks 一致。

- [ ] **Step 5: checkpoint** —— `current:` → `Task 12`。

---

### Task 12: 全局一致性验证

**Files:**
- Read-only 校验

- [ ] **Step 1: 跨文件术语一致性 grep**

```bash
grep -rn "Stop hook" skills/ flightdeck/docs/
grep -rn "board AUTO\|## 进行中" skills/preflight/exit-ritual.md skills/preflight/protocol.md skills/landing/SKILL.md
grep -rn "bootstrap.md" GEMINI.md skills/_shared/ hooks/
```
Expected: "Stop hook" 在 exit-ritual/protocol/landing/session-flow/why-no-hooks 表述一致（机械 AUTO、不 block/不归档、Claude-only deterministic）；bootstrap 单一真相源被 session-start + GEMINI.md 共同指向。

- [ ] **Step 2: 全量脚本 + 测试**

```bash
python scripts/flightdeck_index.py flightdeck --check
python scripts/flightdeck_lint.py flightdeck
python -m pytest scripts/tests/ -q
```
Expected: index `--check` → `clean`；lint `{"findings": []}`；pytest 全绿。

- [ ] **Step 3: 死链 / 锚点存活核对**

对本 plan 在 skill prose 里新增的引用逐个 `grep` 确认：① 没有任何指向 dogfood deck（`flightdeck/...`）的 markdown 链接（incident `skill-prose-links-into-dogfood-deck`）；② 跨 skill 的 `(../...#anchor)` 锚点目标真实存在。

- [ ] **Step 4: checkpoint** —— `current:` → `Task 13`。

---

### Task 13: 收尾 —— 两个原子 commit（hooks=feat / Layer 3=docs，never push）

**Files:**
- `git add` + `git commit -F`（×2），按 `checklists/commits.md`

> 本 plan 含两类逻辑改动：新增执行层（代码）+ 文档改写。按 commits.md §4 原子性**拆两个 commit**，不混。本仓库 **never push**（memory `never-push-only-commit`）。多行 message 经 `git commit -F <file>`（incident `powershell-herestring-in-bash-tool`）。

- [ ] **Step 1: commit 1 —— hooks 执行层（feat）**

`git add hooks/ skills/_shared/bootstrap.md .cursor-plugin/plugin.json GEMINI.md scripts/tests/test_hooks.py`（+ Codex manifest 若 Task 6 Step 4 改了）。
message（写入 `tmp/commit-hooks.txt` 再 `git commit -F`）：subject `feat(flightdeck): auto-land 执行层——SessionStart 注入 + Stop board-sync hook`；body 讲 what/why（脚本焊死机械 board-sync、入场注入接手态、单一真相源 bootstrap、无 bash/python 静默降级）。

- [ ] **Step 2: commit 2 —— Layer 3 文档改写（docs）**

`git add skills/preflight/exit-ritual.md skills/preflight/protocol.md skills/landing/SKILL.md flightdeck/docs/why-no-hooks.md flightdeck/docs/session-flow.md`。
message：subject `docs(flightdeck): Layer 3——board AUTO 移出 agent 顾虑 + why-no-hooks 新决策原则`；body 讲 why-no-hooks 前提部分失效→新二分原则、机械 AUTO 焊死/判断仍归 agent。

- [ ] **Step 3: 状态落盘（plan→done，不在此归档）**

把本 plan `current:` 推到 `done`；把 spec `2026-06-06-auto-land-executor` 与本 plan 的 cockpit 行更新交给下一次 `/flightdeck:landing`（归档 + 晋升闸是 full landing 的尾巴，不在本 plan 内做）。理由见与 spec 关系：spec 的 *what* 仍有效，落地后由 landing 统一推进归档。

- [ ] **Step 4: （部署，可选，不属本 plan 文件验收）** resync `hooks/` + skill 改动进 plugin 缓存重载（checklist `local-plugin-testing`：先 `build_stamp.py --write` 再 robocopy `/MIR`、重建 `.in_use`、**重启会话**），然后在一个真项目 live 复验：开场是否自动进入 preflight 接手态、回合末 `--check` 是否恒 clean。

---

## 备注：与 spec 的关系 + 部署边界

- 本 plan **只做文件改动 + 测试 + 本地 commit**；live 复验（注入是否真在下个会话生效、Stop board-sync 是否每回合 clean）属**部署验收**，在 Task 13 Step 4 之外、按 cockpit `## 下一步` 推进，不阻塞本 plan `done`。
- 知识/判断那半（入场接手率、soft-land 触发率）是 spec 的**观测软指标、非 pass/fail 闸**——本 plan 不为它设自动测试，靠 live dogfood 抽样回流改 bootstrap 措辞。
- Codex 侧（Task 6 Step 4）若查实无可移植接法，**诚实标记未实证**即可，不硬造——符合 spec "可移植性诚实账"。
