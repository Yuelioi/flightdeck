---
status: active
summary: 把 hook-primary 大重构落地的逐文件实施：相位1 机制（Codex/Gemini config + Cursor stop + 脚本 project-dir/emit 四家泛化 + HOOK_DEBUG + 自动化脚本测试）→ 相位2 文案（删 why-no-hooks + 引用清理、bootstrap 三链路、exit-ritual board-AUTO 移出 agent、preflight/protocol/landing/status/session-flow hook-primary 重写、保行为紧致 diff 自检）→ 相位3 spec 收编（auto-land 标 superseded、两 rollout 并入）→ 相位4 每家 Phase0 live 实证门（resync 后新会话，未过停地板）
last_updated: 2026-06-07
implements: specs/2026-06-07-hook-primary-refactor.md
supersedes: archive/plans/2026-06-06-auto-land-executor-rollout.md
---

# hook-primary 重构 rollout（逐文件实施 + verify-then-strip 相位）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实施。步骤用 `- [ ]` 复选框跟踪。

**Goal:** 把 `specs/2026-06-07-hook-primary-refactor` 落地——四家吃满真 hook（被动注入 + board-sync）、删 why-no-hooks、全 skill 文案降到 hook-primary，按 verify-then-strip 相位推进。

**Architecture:** 机制 = Approach A（每家一份薄 config 指向共享 `hooks/run-hook.cmd`→`session-start`/`stop`；脚本按宿主 env/stdin 分支）。文案 = 删降级对冲 + 保留内生职责（知识分类归 agent）+ 一行地板。次序 = verify-then-strip：先接线 + 自动化脚本测试，再每家 live 实证（Phase 0），过了才删该家降级叙事（Phase 1）。

**Tech Stack:** bash hook 脚本 + `.cmd` polyglot wrapper；JSON/TOML manifest；Python `scripts/flightdeck_index.py`（board-sync，复用不改接口）；pytest（`scripts/tests/`）；`flightdeck_index.py --check` + `flightdeck_lint.py` 为闸。

**关键前置事实（spec 已 live 核实 2026-06-07）：**
- 注入字段：Claude/Codex/Gemini = `hookSpecificOutput.additionalContext`；Cursor = `additional_context`。
- 回合结尾事件：Claude/Codex `Stop`、Cursor `stop`、Gemini `AfterAgent`。
- project-dir 信号：Claude/Codex/Gemini stdin `cwd`（Gemini 另有 env `GEMINI_PROJECT_DIR`）、Cursor stdin `workspace_roots[0]`；全部 `$PWD` 兜底；解析后只认 `D/flightdeck/`、**不回溯上级**。
- Claude hooks 由插件 `hooks/hooks.json` 约定自动加载（**无需改 `.claude-plugin`**）；Cursor 已在 `.cursor-plugin/plugin.json` 指 `hooks-cursor.json`；Codex 需在 `.codex-plugin/plugin.json` 加 `hooks` 键；Gemini 现经 `GEMINI.md` `@`-include bootstrap（地板已在）。
- **解决 spec 内歧义**：Codex 用**独立** `hooks/hooks-codex.json`（非共享 `hooks.json`），与 Approach A「每家一份」一致、不与 Claude 耦死（non-goal B）。

## Progress

current: **Phase 4 — 每家 Phase 0 live 实证（待 resync 后新会话；本会话做不了，停地板）。** Phase 1–3 全 done、逐任务本地 commit、`scripts/tests/` 163 passed：
- **Phase 1 机制接线 ✅**（Task 1.1–1.7）。期间发现并修 Windows python3 桩致 board-sync 静默失效 → `incidents/2026-06-07-windows-python-stub-board-sync-noop.md`。
- **Phase 2 文案 ✅**（Task 2.1–2.8；2.6 无可压跳过）。
- **Phase 3 收编 ✅**（Task 3.1：auto-land spec+rollout done+archive+supersedes 反向边、soft-landing spec+rollout 均 done+archive）。模型坑：workflow 无 superseded 状态 → `incidents/2026-06-07-workflow-has-no-superseded-status`，正确走 done+archive+supersedes。

> **复选框说明**：Phase 1–3 在 commit 流里逐任务完成，但本文档 `- [ ]` 未回勾（账漏同步，已知）。其中少数子步把宿主接法延到 Phase 4 live 核（Task 1.3 Gemini extension 声明法、Task 1.1 Codex `${CODEX_PLUGIN_ROOT}` 变量名）——这些待 Phase 4 实证后才定。Phase 4 见 Task 4.1。

---

## File Structure

**新增：**
- `hooks/hooks-codex.json` — Codex 的 `SessionStart`+`Stop` 接线（指向 `run-hook.cmd`）。
- `hooks/hooks-gemini.json`（或 `.gemini/settings.json` 片段）— Gemini 的 `SessionStart`+`AfterAgent` 接线。
- `scripts/tests/test_hooks.py` 内新增用例（不新建文件，扩现有）。

**修改（机制）：**
- `hooks/session-start` — `emit()` 加 Codex/Gemini 分支；project-dir 解析按宿主单一信号 + 不回溯；`FLIGHTDECK_HOOK_DEBUG`。
- `hooks/stop` — project-dir 解析泛化四家；`FLIGHTDECK_HOOK_DEBUG`。
- `.codex-plugin/plugin.json` — 加 `"hooks": "./hooks/hooks-codex.json"`。
- `gemini-extension.json` / `GEMINI.md` — 接 Gemini hook（机制见 Task 1.3）。

**新增（Cursor 注入）：** `.cursor/rules/flightdeck-context.mdc`（hook 生成、gitignore，非手写）。

**修改（文案）：** `skills/_shared/bootstrap.md`、`skills/preflight/{SKILL,exit-ritual,protocol,templates}.md`（templates 含 cockpit `## 关键上下文` 槽 #2）、`skills/{landing,status}/SKILL.md`（landing 含失败捕获 #4）、`docs/session-flow.md`；保行为紧致 `skills/preflight/folder-semantics.md` + `skills/{walkaround,new,emit-agents-md,launch}/SKILL.md` + `docs/{model-architecture,script-layer,spec-lifecycle}.md`。

> **本轮纳入的恢复增量**：#2 cockpit `## 关键上下文`（Task 2.7）+ #4 失败捕获（Task 2.8）。**不并入**：#1 写门负例（单独）、#7 恢复回归测试（流程稳定后）——见 spec「纳入的恢复质量增量」+ `docs/external-memory-borrowings.md`。

**删除：** `docs/why-no-hooks.md`（+ 引用清理）。

**收编：** `specs/2026-06-06-auto-land-executor`、`plans/2026-06-06-auto-land-executor-rollout`、`plans/2026-06-06-soft-landing-rollout` 标 `superseded`。

---

## Phase 1 — 机制接线（可在本会话 TDD；脚本逻辑用 mock stdin 测）

> 注：自动化测试验证**脚本逻辑**（喂 mock stdin/env → 断言 emit 的 JSON / board regen）。宿主**真实触发** = Phase 4 live 实证。

### Task 1.1: Codex 接线 `hooks/hooks-codex.json` + manifest

**Files:**
- Create: `hooks/hooks-codex.json`
- Modify: `.codex-plugin/plugin.json`（加 `hooks` 键）
- Test: `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试** — 断言 Codex config 存在、结构含 `SessionStart`+`Stop` 指向 `run-hook.cmd`。

```python
def test_codex_hooks_config_shape():
    cfg = json.loads(Path("hooks/hooks-codex.json").read_text(encoding="utf-8"))
    assert "SessionStart" in cfg["hooks"]
    assert "Stop" in cfg["hooks"]
    cmds = [h["command"] for grp in cfg["hooks"]["SessionStart"] for h in grp["hooks"]]
    assert any("run-hook.cmd" in c and "session-start" in c for c in cmds)
```

- [ ] **Step 2: 跑测试确认失败** — `uv run pytest scripts/tests/test_hooks.py::test_codex_hooks_config_shape -v` → FAIL（文件不存在）。

- [ ] **Step 3: 写 `hooks/hooks-codex.json`**（Codex 与 Claude 同构）：

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "startup|resume|clear|compact",
        "hooks": [ { "type": "command", "command": "\"${CODEX_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start" } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "\"${CODEX_PLUGIN_ROOT}/hooks/run-hook.cmd\" stop" } ] }
    ]
  }
}
```

> **impl 注**：`${CODEX_PLUGIN_ROOT}` 占位以 Codex live 文档为准（若 Codex 无此变量，改用相对 `./hooks/run-hook.cmd`，Phase 4 核）。

- [ ] **Step 4: 接 manifest** — `.codex-plugin/plugin.json` 加键：`"hooks": "./hooks/hooks-codex.json"`。

- [ ] **Step 5: 跑测试确认通过** — `uv run pytest scripts/tests/test_hooks.py::test_codex_hooks_config_shape -v` → PASS。

- [ ] **Step 6: Commit**

```bash
git add hooks/hooks-codex.json .codex-plugin/plugin.json scripts/tests/test_hooks.py
git commit -m "feat(hooks): 接 Codex SessionStart+Stop hook（独立 hooks-codex.json，Approach A 解耦）"
```

### Task 1.2: Cursor 补 `stop`

**Files:**
- Modify: `hooks/hooks-cursor.json`
- Test: `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试**

```python
def test_cursor_has_stop_hook():
    cfg = json.loads(Path("hooks/hooks-cursor.json").read_text(encoding="utf-8"))
    assert "stop" in cfg["hooks"]
    assert any("stop" in h["command"] for h in cfg["hooks"]["stop"])
```

- [ ] **Step 2: 跑测试确认失败** — FAIL（无 `stop` 键）。
- [ ] **Step 3: 改 `hooks/hooks-cursor.json`** 加 `stop`（与 `sessionStart` 共存）：

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [ { "command": "./hooks/run-hook.cmd session-start" } ],
    "stop": [ { "command": "./hooks/run-hook.cmd stop" } ]
  }
}
```

- [ ] **Step 4: 跑测试确认通过** — PASS。
- [ ] **Step 5: Commit** — `git commit -m "feat(hooks): Cursor 补 stop board-sync 接线"`

### Task 1.3: Gemini 接线（`SessionStart` + `AfterAgent`）

**Files:**
- Create: `hooks/hooks-gemini.json`（hook 块，供 `.gemini/settings.json` 合并 / extension 引用）
- Modify: `gemini-extension.json`（按 Gemini extension hook 加载方式接；不支持则在 README/scaffold 提供用户加进 `.gemini/settings.json` 的片段）
- Test: `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试**

```python
def test_gemini_hooks_config_shape():
    cfg = json.loads(Path("hooks/hooks-gemini.json").read_text(encoding="utf-8"))
    assert "SessionStart" in cfg["hooks"]
    assert "AfterAgent" in cfg["hooks"]
```

- [ ] **Step 2: 跑测试确认失败** — FAIL。
- [ ] **Step 3: 写 `hooks/hooks-gemini.json`**：

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "startup",
        "hooks": [ { "type": "command", "command": "$GEMINI_PROJECT_DIR/hooks/run-hook.cmd session-start", "name": "flightdeck-handoff" } ] }
    ],
    "AfterAgent": [
      { "hooks": [ { "type": "command", "command": "$GEMINI_PROJECT_DIR/hooks/run-hook.cmd stop", "name": "flightdeck-board-sync" } ] }
    ]
  }
}
```

- [ ] **Step 4: 接 extension** — 核 Gemini extension 是否支持声明 hooks；支持则在 `gemini-extension.json` 引用；**不支持**则把上面片段写进 scaffold + README「用户合并进 `.gemini/settings.json`」。此决定记进 Task 4 的 Gemini live 核查（**本步不阻塞 Phase 1，自动化测试只验文件结构**）。
- [ ] **Step 5: 跑测试确认通过** — PASS。
- [ ] **Step 6: Commit** — `git commit -m "feat(hooks): Gemini SessionStart+AfterAgent hook 块（extension 接法见 Phase 4 核）"`

### Task 1.4: `session-start` emit() 四家 + project-dir 优先级

**Files:**
- Modify: `hooks/session-start`
- Test: `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试**（喂各家 env/stdin，断言 emit 的注入字段）：

```python
def run_session_start(env, project_dir):
    return subprocess.run(["bash", "hooks/session-start"], capture_output=True, text=True,
                          env={**os.environ, **env, "CLAUDE_PROJECT_DIR": project_dir}).stdout

def test_codex_emit_uses_hookSpecificOutput(tmp_deck):
    out = run_session_start({"CODEX_PLUGIN_ROOT": "x"}, tmp_deck)
    assert "hookSpecificOutput" in out and "additionalContext" in out

def test_gemini_emit_uses_hookSpecificOutput(tmp_deck):
    out = run_session_start({"GEMINI_PROJECT_DIR": tmp_deck}, tmp_deck)
    assert "hookSpecificOutput" in out and "additionalContext" in out
```

- [ ] **Step 2: 跑测试确认失败** — FAIL（当前 emit 无 Codex/Gemini 分支，落进 else 的 `additionalContext` 裸字段）。
- [ ] **Step 3: 改 `hooks/session-start` 的 `emit()`** — 加 Codex/Gemini 分支（同 Claude 形状）：

```bash
emit() {
  local ctx; ctx="$(escape_for_json "$1")"
  if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
    printf '{\n  "additional_context": "%s"\n}\n' "$ctx"
  elif [ -n "${CODEX_PLUGIN_ROOT:-}" ] || [ -n "${GEMINI_PROJECT_DIR:-}" ] \
       || { [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -z "${COPILOT_CLI:-}" ]; }; then
    printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "SessionStart",\n    "additionalContext": "%s"\n  }\n}\n' "$ctx"
  else
    printf '{\n  "additionalContext": "%s"\n}\n' "$ctx"
  fi
}
```

- [ ] **Step 4: 改 project-dir 解析** — 顶部 `PROJECT_DIR` 按宿主单一信号 + 不回溯：

```bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-${CURSOR_PROJECT_ROOT:-${GEMINI_PROJECT_DIR:-$PWD}}}"
# gate 严格：只认 $PROJECT_DIR/flightdeck，不向上层目录回溯（见已有 line 33 gate）
```

- [ ] **Step 5: 跑测试确认通过** — PASS。
- [ ] **Step 6: Commit** — `git commit -m "feat(hooks): session-start emit 四家分支 + project-dir 优先级（不回溯）"`

### Task 1.5: `stop` project-dir 泛化四家

**Files:**
- Modify: `hooks/stop`
- Test: `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试** — 喂 `GEMINI_PROJECT_DIR`/`CURSOR_PROJECT_ROOT` 指向临时 deck，断言 `flightdeck_index.py` 被调用、AUTO 区重生、`exit 0`。
- [ ] **Step 2: 跑测试确认失败** — FAIL（当前 stop 仅认 `CLAUDE_PROJECT_DIR`）。
- [ ] **Step 3: 改 `hooks/stop`** line 9：

```bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-${CURSOR_PROJECT_ROOT:-${GEMINI_PROJECT_DIR:-$PWD}}}"
```

- [ ] **Step 4: 跑测试确认通过** — PASS。
- [ ] **Step 5: Commit** — `git commit -m "feat(hooks): stop board-sync project-dir 泛化四家"`

### Task 1.6: `FLIGHTDECK_HOOK_DEBUG` 可观测

**Files:** Modify `hooks/session-start` + `hooks/stop`；Test `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试** — 置 `FLIGHTDECK_HOOK_DEBUG=1` 跑 stop（无 deck），断言 stderr 含 `gate` / `project-dir` 诊断行；不置位时 stderr 为空。
- [ ] **Step 2: 跑测试确认失败** — FAIL。
- [ ] **Step 3: 加诊断** — 两脚本里包一个 `dbg()`：`[ -n "${FLIGHTDECK_HOOK_DEBUG:-}" ] && printf 'flightdeck-hook[%s]: %s\n' "$(basename "$0")" "$1" >&2 || true`，在 gate/project-dir 解析/regen 前后各打一行。默认静默不变。
- [ ] **Step 4: 跑测试确认通过** — PASS。
- [ ] **Step 5: 全量回归** — `uv run pytest scripts/tests/ -v`：现有 149 + 新增全绿。
- [ ] **Step 6: Commit** — `git commit -m "feat(hooks): FLIGHTDECK_HOOK_DEBUG 诊断开关（破静默盲区）"`

### Task 1.7: Cursor 规则文件注入（主路径，独立成立）

> 决策：Cursor `sessionStart` `additional_context` 不可靠（claude-mem 实证）→ Cursor 主注入 = hook 写 `.cursor/rules/flightdeck-context.mdc`（`alwaysApply: true`），Cursor 每对话稳定加载。原则：稳定加载 > 优雅加载。机制照搬 `references/claude-mem/cursor-hooks/CONTEXT-INJECTION.md`。

**Files:**
- Modify: `hooks/session-start`、`hooks/stop`（Cursor 分支写规则文件）
- Modify: `.gitignore`（加 `.cursor/rules/flightdeck-context.mdc`）
- Test: `scripts/tests/test_hooks.py`

- [ ] **Step 1: 写失败测试** — 设 Cursor env + 临时 deck，跑 session-start，断言 `<deck>/../.cursor/rules/flightdeck-context.mdc` 被写、含 `alwaysApply: true` + bootstrap 文本 + cockpit 锚点。
- [ ] **Step 2: 跑测试确认失败** — FAIL（当前无规则文件写出）。
- [ ] **Step 3: 加 Cursor 规则文件写出** — 在 `session-start`/`stop` 的 Cursor 分支（`CURSOR_PLUGIN_ROOT`/`CURSOR_PROJECT_ROOT` 存在）追加：

```bash
write_cursor_rules() {  # $1 = project_dir, $2 = injected content
  local rules_dir="$1/.cursor/rules"
  mkdir -p "$rules_dir" 2>/dev/null || return 0
  { printf -- '---\nalwaysApply: true\ndescription: "flightdeck cockpit handoff (auto-updated)"\n---\n\n'; printf '%s\n' "$2"; } > "$rules_dir/flightdeck-context.mdc"
}
```
session-start 与 stop 都在收尾调用它（stop 复用已抽出的 bootstrap+anchor 组装）。Cursor 仍可顺带 emit `additional_context`（belt-and-suspenders，非主依赖）。

- [ ] **Step 4: gitignore** — `.gitignore` 加 `**/.cursor/rules/flightdeck-context.mdc`（派生投影，不进 git）。
- [ ] **Step 5: 跑测试确认通过** — PASS；`uv run pytest scripts/tests/ -v` 全绿。
- [ ] **Step 6: Commit** — `git commit -m "feat(hooks): Cursor 规则文件注入为主路径（alwaysApply，稳定加载>优雅加载）"`

---

## Phase 2 — 文案精简（编辑型；host-agnostic + Claude-已证 部分现在做，非-Claude 降级叙事的删除留 Phase 4 闸后）

> **verify-then-strip 落到本相位**：现在做的是 ① 删 why-no-hooks（不依赖单家实证）② 保行为紧致（同）③ bootstrap/exit-ritual/preflight 等改为 hook-primary 叙事，**其中 Claude 写"已证"、Codex/Gemini/Cursor 写"待 Phase 0 实证"**。Phase 4 各家过了，再由该家的收尾步把"待实证"翻成最终态。

### Task 2.1: 删 `why-no-hooks.md` + 引用清理

**Files:** Delete `flightdeck/docs/why-no-hooks.md`；Modify 命中引用的文件；regen INDEX。

- [ ] **Step 1: grep 指向引用** — `rg -n "why-no-hooks" flightdeck skills` 列全部命中（`[[why-no-hooks]]`、`why-no-hooks.md` 相对链接、纯文本）。
- [ ] **Step 2: 逐处重定向/删除** — 指向决策原则的 → 改指 `docs/cross-host-hooks.md`；就近无意义的删。
- [ ] **Step 3: grep 废措辞变体** — `rg -ni "无 ?hook|no-hook|仅 ?Claude|退指令文件|未实证|效果未实证" skills flightdeck/docs`，逐处判删（**保留** `cross-host-hooks.md` 史述）。
- [ ] **Step 4: 删文件** — `git rm flightdeck/docs/why-no-hooks.md`。
- [ ] **Step 5: regen + 验证** — `uv run scripts/flightdeck_index.py flightdeck`（docs/INDEX 自动去行）；`rg -n "why-no-hooks" flightdeck skills` 仅剩 spec/plan/cross-host 的史述提及。
- [ ] **Step 6: Commit** — `git commit -m "refactor(docs): 删 why-no-hooks（理由已入 cross-host-hooks）+ 清引用与废措辞"`

### Task 2.2: `bootstrap.md` —— turn-end 四家 + 三链路优先级 + 降级判据

**Files:** Modify `skills/_shared/bootstrap.md`

- [ ] **Step 1: 改 line 18-21 的「welded by a Stop hook on Claude Code」** → 「welded by the turn-end hook on every host that fires it（Claude/Codex `Stop`、Cursor `stop`、Gemini `AfterAgent`）」。保留 entry-handoff + 知识分类 + soft-land 强制令原文。
- [ ] **Step 2: 加三链路优先级 + 降级判据**（spec 文案层 item 2 的 blockquote 内容）：hook 入场注入=主；`GEMINI.md`/`AGENTS.md` `@`-include=地板；manifest 不重复注入；「hook 不可用」= 配置/脚本缺失 ∨ 无 bash/python ∨ Phase0 实证未达。
- [ ] **Step 3: 验证** — bootstrap 经 `GEMINI.md` `@`-include，确认无断链；`rg -n "Claude Code" skills/_shared/bootstrap.md` 不再把 board 焊死限定 Claude。
- [ ] **Step 4: Commit** — `git commit -m "refactor(bootstrap): turn-end hook 四家 + 三链路优先级 + 降级判据"`

### Task 2.3: `exit-ritual.md` —— board-AUTO 移出 agent 顾虑

**Files:** Modify `skills/preflight/exit-ritual.md`

- [ ] **Step 1:** 删「只有 Claude 焊 board / agent 回合结尾要重生 AUTO 区」的措辞 → AUTO 区由 turn-end hook（每家）保证；agent 回合结尾只剩判断性看板（`## 下一步`/plan `current:`）+「本回合有写门知识吗 → soft-land」。
- [ ] **Step 2:** 非-Claude 宿主的"焊死"措辞标「待 Phase 0 实证」（Claude 写"已证"）。
- [ ] **Step 3: 验证** — `rg -ni "仅.*Claude|只有 Claude" skills/preflight/exit-ritual.md` 空。
- [ ] **Step 4: Commit** — `git commit -m "refactor(exit-ritual): board-AUTO 移出 agent 回合结尾顾虑（hook 焊死）"`

### Task 2.4: `preflight/SKILL` + `protocol` + `landing` + `status` hook-primary 叙事

**Files:** Modify `skills/preflight/{SKILL,protocol}.md`、`skills/{landing,status}/SKILL.md`

- [ ] **Step 1:** 各文件把入场/出场叙事统一到「hook 主路径注入接手态 + turn-end 焊 board-sync；hook 不可用 → 手动 `/flightdeck:preflight` 一行地板」，删散布的无-hook 双路径展开。
- [ ] **Step 2: 验证** — `uv run scripts/flightdeck_index.py flightdeck --check` clean + `uv run scripts/flightdeck_lint.py flightdeck` clean。
- [ ] **Step 3: Commit** — `git commit -m "refactor(skills): preflight/protocol/landing/status 降到 hook-primary 叙事"`

### Task 2.5: `session-flow.md` 主干图

**Files:** Modify `flightdeck/docs/session-flow.md`

- [ ] **Step 1:** 主干改为四家一致的 hook 入场 + turn-end board-sync；删宿主分级与兜底分支大段。
- [ ] **Step 2: Commit** — `git commit -m "refactor(docs): session-flow 主干纳入 hook 入场 + turn-end board-sync"`

### Task 2.6: 保行为紧致（有冗余则压、无则原样）

**Files:** Modify `skills/preflight/{templates,folder-semantics}.md`、`skills/{walkaround,new,emit-agents-md,launch}/SKILL.md`、`docs/{model-architecture,script-layer,spec-lifecycle}.md`

- [ ] **Step 1:** 逐文件压冗余措辞；**有冗余才动，无可压跳过**（如 `spec-lifecycle.md` 无 hook 内容、若无可压即不改）。
- [ ] **Step 2: 双闸自检** — ① `--check` + `lint` 全绿（必要非充分）；② `git diff` 逐条人工确认删的是措辞、改的不是规则（数据模型/status 合法值/frontmatter 必填/文件夹分类/INDEX 行格式逐项不变）。
- [ ] **Step 3: 记 token 账** — `git diff --stat skills/` 记 skill 散文 before/after（基线 ≈2166 行）；观测净减、非闸。
- [ ] **Step 4: Commit** — `git commit -m "refactor(skills): 保行为紧致（压字数不动规则，双闸自检）"`

### Task 2.7: cockpit `## 关键上下文` 槽（#2 借 ReMe Critical Context）

**Files:** Modify `skills/preflight/templates.md`（cockpit 模板）、`skills/preflight/exit-ritual.md`（填写指引）、`skills/preflight/SKILL.md`（preflight 读取）

- [ ] **Step 1:** cockpit 模板加 `## 关键上下文` 区（位于 `## 下一步` 后），注释说明：承重字面量——正改的 file path、失败测试名、错误串、关键函数名/值；**agent 判断填写**（非脚本 AUTO，语义同 `## 下一步`）。
- [ ] **Step 2:** exit-ritual / soft-land 收尾指引加一条：「刷新 `## 关键上下文`——把本回合恢复时真正需要的字面量落进去（无则留空/`- (none)`）」。
- [ ] **Step 3:** preflight 读取 cockpit 时把 `## 关键上下文` 纳入报告（与 focus/下一步 并列）。
- [ ] **Step 4: 验证** — `--check` + `lint` clean；`scaffolds/full/` 的 cockpit 模板同步（若 scaffold 含 cockpit 模板）。
- [ ] **Step 5: Commit** — `git commit -m "feat(cockpit): 加 ## 关键上下文 槽（恢复承重字面量，借 ReMe Critical Context）"`

### Task 2.8: 失败/弯路捕获（#4 借 ReMe FailureExtraction）

**Files:** Modify `skills/preflight/exit-ritual.md`、`skills/landing/SKILL.md`（分类启发）

- [ ] **Step 1:** landing/exit-ritual 知识分类启发加一条显式分支：「本回合若**放弃某路径/撞墙**，写 `incident` 记**失败路径 + 为何失败**（含看似可行却失败的原因），不只记最终修复」。给一个 GOOD 例（"X 方案因 Y 约束失败，故选 Z"）。
- [ ] **Step 2: 验证** — `--check` + `lint` clean；`rg -n "失败|弯路|放弃" skills/preflight/exit-ritual.md skills/landing/SKILL.md` 命中新分支。
- [ ] **Step 3: Commit** — `git commit -m "feat(landing): 失败/弯路捕获分支（负面知识入 incidents，借 ReMe FailureExtraction）"`

---

## Phase 3 — spec 收编

### Task 3.1: 标 superseded + 并入

**Files:** Modify `specs/2026-06-06-auto-land-executor.md`、`plans/2026-06-06-auto-land-executor-rollout.md`、`plans/2026-06-06-soft-landing-rollout.md`（frontmatter `status: superseded`）；regen。

- [ ] **Step 1:** 三个工件 frontmatter 改 `status: superseded`，正文顶加一行「superseded by `specs/2026-06-07-hook-primary-refactor`（已实施且有效的产出由新 rollout 承继）」。
- [ ] **Step 2:** `soft-landing` spec **不动 status**（其 what 仍有效）；仅确认其 exit-ritual 表述已由 Task 2.3 改写、无两套并存。
- [ ] **Step 3: regen + 验证** — `uv run scripts/flightdeck_index.py flightdeck`；确认 cockpit `## 进行中` 仅剩本 spec + 本 rollout（+ soft-landing spec）、无收编工件并存。`flightdeck:walkaround` 不报 superseded 悬链。
- [ ] **Step 4: Commit** — `git commit -m "chore(deck): 收编 auto-land spec + 两 rollout 为 superseded"`

---

## Phase 4 — 每家 Phase 0 live 实证门（resync 后新会话；手动，非本会话内）

> hook 只在 **resync 进 plugin 缓存后的新会话**触发。本相位在每家宿主里手动跑，**过了才翻该家「待实证」措辞为最终态**；过不了 → 该家停在地板叙事，记 incident，不回退。

### Task 4.1: resync + 各家 Phase 0 矩阵

- [ ] **Step 1: resync** — 按 `checklists/local-plugin-testing.md` 把工作树同步进各宿主插件缓存。
- [ ] **Step 2: 每家最小矩阵** `{入场注入到达、回合末 board `--check` clean、缺 deck 静默、缺 bash 静默、缺 python 静默}`：
  - **Claude**（当前宿主，多为已证）：开新会话确认入场接手态 + 回合末 `--check` 恒 clean。
  - **Codex**：`${CODEX_PLUGIN_ROOT}` 变量真伪、`hooks-codex.json` 是否加载、注入是否到达。
  - **Cursor**：**主路径 = `.cursor/rules/flightdeck-context.mdc` 规则文件**是否在入场+回合末被刷新、Cursor 是否每对话稳定加载（`alwaysApply`）；`stop` 是否每回合触发（社区报告曾不稳）；Windows extensionless 经 `run-hook.cmd` 无弹窗。`sessionStart` `additional_context` 不作主依赖（至多 bonus）。
  - **Gemini**：extension 是否真加载 hook（Task 1.3 Step 4 的接法）、`AfterAgent` board-sync 实测耗时（同步阻塞，记数据）。
- [ ] **Step 3: 翻最终态** — 过的家：把 Task 2.2/2.3 里该家「待 Phase 0 实证」措辞改为最终；未过：保留地板叙事 + `flightdeck:new incident` 记症状。
- [ ] **Step 4: 全绿则收口** — `specs/2026-06-07-hook-primary-refactor` + 本 rollout 翻 `done`、归档；cockpit `## 下一步` 清。

---

## Self-Review（写完对 spec 核）

- **Spec 覆盖**：机制（Task 1.1-1.6）✓ 文案+删 why-no-hooks（2.1-2.6）✓ 收编（3.1）✓ verify-then-strip（Phase 相位 + 2.x「待实证」+ Phase 4）✓ 可观测（1.6）✓ 保行为双闸（2.6）✓ token 账（2.6 Step3）✓。
- **占位扫描**：Gemini extension 接法（1.3 Step4）与 `${CODEX_PLUGIN_ROOT}` 变量（1.1）标为 Phase 4 核——非占位，是 live 待核的具体项 + 兜底分支已给。
- **类型一致**：`run-hook.cmd session-start|stop` 命令、`hookSpecificOutput.additionalContext`、`PROJECT_DIR` env 链各 Task 一致。