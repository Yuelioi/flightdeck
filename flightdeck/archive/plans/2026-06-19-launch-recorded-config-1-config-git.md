---
status: done
summary: Phase 1 of launch-recorded-config: declare the rules.md frontmatter settings schema (runtime/agents_md, version no longer the only structured field, steady-state Settings>Rules precedence), add a lint audit validating the new fields, and force git by deleting every no-git branch across the skills + protocol + folder-semantics + scaffold. No field stamping/reading yet (phases 2-3).
last_updated: 2026-06-19
implements: specs/2026-06-19-launch-recorded-config.md
---

# Launch-recorded config — Phase 1: config model + git force

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `rules.md` frontmatter 立起记录式配置 schema(`runtime` / `agents_md`)、加一个校验它们的 lint 审计,并删掉贯穿 skills/protocol/scaffold 的所有 no-git 分支——为后续相(launch 探测落字段、运行期读字段)铺好地基。

**Architecture:** 配置走 `rules.md` 既有 frontmatter(复用 `flightdeck_index.parse_frontmatter`,零新解析)。本相**只声明 schema + 校验 + 删 no-git**,**不**实现 launch 探测写入(相二)或运行期读取(相三)——审计只在字段**存在时**校验合法值,故与后续相解耦。git 强制是纯散文删除(skill markdown),验证靠 grep + 既有 pytest + 英文门,无单测。

**Tech Stack:** Python 3.8+ 纯标准库(`flightdeck_lint.py` / `flightdeck_index.py`)、`unittest` + `tempfile`、ripgrep(`rg`)。

---

## File structure(本相触及)

| 文件 | 职责 | 动作 |
|---|---|---|
| `scripts/flightdeck_lint.py` | 机械审计层 | **改**:加 `audit_settings`、注册进 `lint()` |
| `scripts/tests/test_flightdeck_lint.py` | lint 单测 | **改**:加 `AuditSettingsTest` |
| `scaffolds/full/flightdeck/rules.md` | 新 deck 模板 | **改**:frontmatter 加 `agents_md: off`;删 no-git 注释示例 |
| `skills/preflight/templates.md` | frontmatter 契约 | **改**:`version` 不再唯一结构化字段 + 记 `runtime`/`agents_md` + 稳态 Settings>Rules 优先级 |
| `skills/preflight/protocol.md` | Rule resolution order | **改**:删 git 推断条目、加 Settings>Rules 优先级条 |
| `skills/preflight/SKILL.md` | preflight | **改**:删 step 1 git 推断 / step 4 no-git 跳过 |
| `skills/landing/SKILL.md` | landing | **改**:删 step 0 no-git `mv` 退路 / step 11 no-git 跳 commit |
| `skills/preflight/exit-ritual.md` | landing 教科书 | **改**:删 `no-git overrides all`、anchor 兜底、signal 2 no-git 禁用 |
| `skills/preflight/folder-semantics.md` | 文件夹语义 | **改**:删「A no-git deck loses nothing…」整段 |
| `skills/status/SKILL.md`、`skills/emit-agents-md/SKILL.md` | | **改**:删 no-git 旁支 |

> 验证分两类:**代码任务**(Task 1–2)走 TDD;**散文任务**(Task 3–8)无单测,验证 = `rg` 确认 no-git 残留为零 + `uv run pytest scripts/tests/` 全绿 + 英文门 `rg -lP '\p{Han}' skills scaffolds` 为空。

---

### Task 1: `audit_settings` — 校验 rules.md frontmatter 新字段

**Files:**
- Modify: `scripts/flightdeck_lint.py`(在 `audit_when_to_update` 之后、`_collect_md` 之前加函数;顶部常量区加合法值集合)
- Test: `scripts/tests/test_flightdeck_lint.py`

- [ ] **Step 1: 写失败测试**

在 `test_flightdeck_lint.py` 的 import 块把 `audit_settings` 加进 `from flightdeck_lint import (...)`,并在文件末尾追加:

```python
class AuditSettingsTest(unittest.TestCase):
    def _deck_with_rules(self, frontmatter_body):
        d = tempfile.mkdtemp()
        deck = Path(d)
        (deck / "rules.md").write_text(
            f"---\n{frontmatter_body}\n---\n\n### Rules\n", encoding="utf-8"
        )
        return deck

    def test_legal_values_pass(self):
        deck = self._deck_with_rules("version: 3.0\nruntime: uv\nagents_md: off")
        self.assertEqual(audit_settings(deck), [])

    def test_illegal_runtime_is_warning(self):
        deck = self._deck_with_rules("version: 3.0\nruntime: deno")
        findings = _by_audit(audit_settings(deck), "settings")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], "WARNING")

    def test_illegal_agents_md_is_warning(self):
        deck = self._deck_with_rules("version: 3.0\nagents_md: maybe")
        findings = _by_audit(audit_settings(deck), "settings")
        self.assertEqual(len(findings), 1)

    def test_absent_fields_pass(self):
        # Phase 1: fields are optional (launch stamps runtime in Phase 2).
        deck = self._deck_with_rules("version: 3.0")
        self.assertEqual(audit_settings(deck), [])

    def test_missing_rules_file_is_noop(self):
        deck = Path(tempfile.mkdtemp())
        self.assertEqual(audit_settings(deck), [])
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_lint.py::AuditSettingsTest -v`
Expected: FAIL — `ImportError: cannot import name 'audit_settings'`

- [ ] **Step 3: 写最小实现**

在 `scripts/flightdeck_lint.py` 顶部常量区(`KNOWLEDGE_STATUSES = …` 附近)加:

```python
# Legal values for the recorded-config frontmatter fields (spec §2).
# Fields are optional in Phase 1 (launch stamps `runtime` in Phase 2); only
# *present* values are validated here.
LEGAL_SETTINGS = {
    "runtime": {"uv", "python", "node"},
    "agents_md": {"auto", "off"},
}
```

在 `audit_when_to_update` 之后加:

```python
def audit_settings(deck):
    """Settings schema — rules.md frontmatter `runtime`/`agents_md`, if present,
    must carry a legal value (spec §2). Absent = OK (optional in Phase 1)."""
    deck = Path(deck)
    rules = deck / "rules.md"
    if not rules.is_file():
        return []
    fm = parse_frontmatter(rules.read_text(encoding="utf-8"))
    findings = []
    for key, legal in LEGAL_SETTINGS.items():
        val = fm.get(key)
        if val is not None and val not in legal:
            findings.append(
                _finding(
                    "settings",
                    "WARNING",
                    rules,
                    f"rules.md `{key}: {val}` is illegal (legal: {sorted(legal)})",
                )
            )
    return findings
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_lint.py::AuditSettingsTest -v`
Expected: PASS（5 passed）

- [ ] **Step 5: Commit**

```bash
git add scripts/flightdeck_lint.py scripts/tests/test_flightdeck_lint.py
git commit -m "feat(lint): audit_settings — validate rules.md runtime/agents_md frontmatter"
```

---

### Task 2: 把 `audit_settings` 接进 `lint()`

**Files:**
- Modify: `scripts/flightdeck_lint.py`(`lint()` 函数)
- Test: `scripts/tests/test_flightdeck_lint.py`

- [ ] **Step 1: 写失败测试**

在 `test_flightdeck_lint.py` 末尾追加:

```python
class LintWiringSettingsTest(unittest.TestCase):
    def test_lint_runs_settings_audit(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "rules.md").write_text(
                "---\nversion: 3.0\nruntime: deno\n---\n\n### Rules\n", encoding="utf-8"
            )
            findings = lint(deck)
            self.assertTrue(any(f["audit"] == "settings" for f in findings))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_lint.py::LintWiringSettingsTest -v`
Expected: FAIL — 找不到 `settings` audit（`lint()` 未调用它）

- [ ] **Step 3: 写最小实现**

在 `scripts/flightdeck_lint.py` 的 `lint()` 里,`findings += audit_when_to_update(deck)` 之后加一行:

```python
    findings += audit_settings(deck)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_lint.py -v`
Expected: PASS（含原有全部用例）

- [ ] **Step 5: Commit**

```bash
git add scripts/flightdeck_lint.py scripts/tests/test_flightdeck_lint.py
git commit -m "feat(lint): wire audit_settings into lint()"
```

---

### Task 3: scaffold rules.md — 加 `agents_md: off`、删 no-git 注释

**Files:**
- Modify: `scaffolds/full/flightdeck/rules.md`

当前内容(全文):

```
---
version: 3.0
---

## House rules
<!-- Defaults: local commit auto (reset/amend-able) + push asks + landing archives by judgment;
     git / AGENTS / scripts all inferred. To change a behavior, just tell the AI a persistent
     preference in plain language ("ask before committing", "this deck doesn't use git") and it
     appends a rule under ### Rules — no magic-string syntax to memorize. -->

### Project conventions

### Rules
```

- [ ] **Step 1: 改 frontmatter + 注释**

把整个文件替换为(frontmatter 加 `agents_md: off`;注释删掉 git-inference / "this deck doesn't use git",改为反映强制 git/runtime + frontmatter 配置):

```
---
version: 3.0
agents_md: off
---

## House rules
<!-- flightdeck requires git + a script runtime (uv/python/node) — launch refuses without them.
     Recorded settings live in this frontmatter (runtime stamped by launch; agents_md auto|off).
     For anything else, tell the AI a persistent preference in plain language
     ("ask before committing") and it appends a rule under ### Rules — no magic-string syntax. -->

### Project conventions

### Rules
```

- [ ] **Step 2: 验证 scaffold 仍合法**

Run: `uv run python -c "import sys; sys.path.insert(0,'scripts'); from flightdeck_index import parse_frontmatter; print(parse_frontmatter(open('scaffolds/full/flightdeck/rules.md',encoding='utf-8').read()))"`
Expected: 打印 `{'version': '3.0', 'agents_md': 'off'}`

- [ ] **Step 3: 英文门**

Run: `rg -lP '\p{Han}' scaffolds/full/flightdeck/rules.md`
Expected: 无输出（exit 1 = 无匹配）

- [ ] **Step 4: Commit**

```bash
git add scaffolds/full/flightdeck/rules.md
git commit -m "feat(scaffold): rules.md ships agents_md:off; drop no-git comment"
```

---

### Task 4: templates.md — 改 frontmatter 契约

**Files:**
- Modify: `skills/preflight/templates.md`（`## rules.md` 节,约 line 32–39）

- [ ] **Step 1: 改「version 是唯一结构化字段」断言**

定位现文(line 32–33 附近):

```
- **Mandatory file** — part of the minimal contract (`rules.md` + `cockpit.md`). Must exist and carry `version` — the **only** structured field. Behavior resolves via [protocol § Rule resolution order](protocol.md#rule-resolution-order) (deck `### Rules` → environment inference → built-in default / skill judgment).
```

替换为:

```
- **Mandatory file** — part of the minimal contract (`rules.md` + `cockpit.md`). Must exist and carry `version`. Recorded-config fields also live in frontmatter: `runtime` (`uv|python|node`, stamped by launch) and `agents_md` (`auto|off`). Behavior resolves via [protocol § Rule resolution order](protocol.md#rule-resolution-order) (frontmatter field → deck `### Rules` → built-in default / skill judgment).
```

- [ ] **Step 2: 改「what used to be toggles」块的 git/commit 条 + 加优先级**

定位 line 34–39 的 `### Rules is AI-authored` 块。把 `git` 子条(line 35)与 `commit`/ritual 子条(line 37–38)改为反映:git 是前置(不可配)、`runtime`/`agents_md` 是 frontmatter 字段、`commits` 仍走散文。在该块末尾加一条**稳态优先级**:

```
- **Frontmatter settings outrank conflicting `### Rules` prose** for the keys they cover. A field (`runtime: node`) wins over a prose line that contradicts it ("always use python"); prose only governs preferences with **no** corresponding field.
```

（精确措辞实现时定;须:删 git-inference 表述、`runtime`/`agents_md` 指向 frontmatter、保留 `commits` 散文路径、加上面这条优先级。）

- [ ] **Step 3: 英文门 + 链接完整性**

Run: `rg -lP '\p{Han}' skills/preflight/templates.md` （Expected: 无输出）
Run: `uv run python scripts/flightdeck_lint.py flightdeck` （Expected: 无 `dangling-ref` 涉及 templates.md）

- [ ] **Step 4: Commit**

```bash
git add skills/preflight/templates.md
git commit -m "docs(skill): rules.md frontmatter carries runtime/agents_md; settings outrank prose"
```

---

### Task 5: protocol.md — 删 git 推断、加优先级条

**Files:**
- Modify: `skills/preflight/protocol.md`（Rule resolution order 节 + `### Rules` 描述,约 line 22 / 30–38）

- [ ] **Step 1: 删 Rule resolution order 里的 git 推断**

定位 line 30–32 的解析顺序(Deck rule → environment inference → default)。**删除 git 推断**作为一个被解析项的表述,改为:git 是**安装前置**(launch 已强制),不参与运行期解析;`runtime`/`agents_md` 由 frontmatter 字段直读。

- [ ] **Step 2: 加稳态优先级条**

在 Rule resolution order 处加一条:frontmatter 结构化字段对其 key 高于 `### Rules` 散文(与 templates.md Task 4 Step 2 同一规则,链接之、不复述定义)。

- [ ] **Step 3: 改 line 38 的「no … toggle」清单**

line 38 现列 `no self-invoke override / no auto land / no run scripts toggle / no disabled_folders`。把 `scripts inferred from runtime` 改为 `runtime is a recorded frontmatter field (required; no inference)`;删任何 no-git 可配表述。

- [ ] **Step 4: 验证**

Run: `rg -n 'no-git|no git' skills/preflight/protocol.md` （Expected: 无输出）
Run: `rg -lP '\p{Han}' skills/preflight/protocol.md` （Expected: 无输出）

- [ ] **Step 5: Commit**

```bash
git add skills/preflight/protocol.md
git commit -m "docs(skill): protocol drops git inference; frontmatter settings outrank prose"
```

---

### Task 6: 删 preflight / landing / exit-ritual 的 no-git 分支

**Files:**
- Modify: `skills/preflight/SKILL.md`（step 1 git 推断、step 4 no-git 跳过)
- Modify: `skills/landing/SKILL.md`（step 0 no-git `mv` 退路、step 11 no-git 跳 commit、line 72 banner 的 no-git 注)
- Modify: `skills/preflight/exit-ritual.md`（`no-git overrides all`(~line 124)、anchor 兜底(~line 133)、signal 2 no-git 禁用(~line 449)）

- [ ] **Step 1: preflight/SKILL.md**

- step 1(line 9):删「Infer git per that order (ancestor `.git` + deck not gitignored; a deck `### Rules` no-git entry → skip step 4)」——git 现为前置,不推断。
- step 4(line 12):删开头「(skip when no-git)」与任何 no-git 条件;git note 无条件执行。

- [ ] **Step 2: landing/SKILL.md**

- step 0(line 26):删「No-git → skip Step 11 and use a plain `mv`…」整句;land 移动恒用 git-aware 路径。
- step 11(line 37):删「skipped entirely under no-git」类表述;commit 恒执行(local auto / push asks 不变)。
- line 72 banner:删 `skipped under no-git or a commit deck rule` 里的 `no-git`(保留 commit-rule 部分)。

- [ ] **Step 3: exit-ritual.md**

- ~line 124:删 `no-git overrides all → no commit …` 这条 decision-tree 分支。
- ~line 133:删 `Under no-git: skip (no commit → no anchor trailer; preflight falls back).`
- ~line 449 signal 2:删 `(disabled under no-git)`。
- ~line 96/102 的 anchor `Fallback (no Python runtime or no anchor yet)`:**保留** anchor-yet 部分,删 `no Python runtime` 部分(runtime 现强制——但完整删 runtime 兜底是相二的事;本相**只删 no-git**,runtime 兜底留给 Task 标注以免越界)。

> 边界:本 Task **只删 no-git**。runtime 手写兜底删除属相二,勿在此动,避免相交叉。

- [ ] **Step 4: 验证无 no-git 残留(这三文件)**

Run: `rg -n 'no-git|no git|gitignored' skills/preflight/SKILL.md skills/landing/SKILL.md skills/preflight/exit-ritual.md`
Expected: 无输出
Run: `rg -lP '\p{Han}' skills/preflight/SKILL.md skills/landing/SKILL.md skills/preflight/exit-ritual.md` （Expected: 无输出）

- [ ] **Step 5: Commit**

```bash
git add skills/preflight/SKILL.md skills/landing/SKILL.md skills/preflight/exit-ritual.md
git commit -m "feat(skill): force git — drop no-git branches in preflight/landing/exit-ritual"
```

---

### Task 7: 删 folder-semantics / status / emit-agents-md 的 no-git 分支

**Files:**
- Modify: `skills/preflight/folder-semantics.md`（~line 81–85 的 no-git 段)
- Modify: `skills/status/SKILL.md`、`skills/emit-agents-md/SKILL.md`（no-git 旁支)

- [ ] **Step 1: folder-semantics.md**

删「flightdeck keeps no history-log file…」段里的 no-git 论述:整句「A no-git deck (e.g. a gitignored `flightdeck/`) loses nothing: the archived artifacts themselves are the history.」删除;保留「archive/ + git log 是记录」的主句(git 现恒在)。

- [ ] **Step 2: emit-agents-md/SKILL.md**

line 20:删「Under no-git, still emit (AGENTS.md is not git-dependent) but skip the working-tree-clean warning」——git 恒在,working-tree-clean 警告无条件适用。

- [ ] **Step 3: status/SKILL.md**

`rg -n 'no-git|no git' skills/status/SKILL.md` 定位任何 no-git 旁支并删除(若 grep 为空则本步无改动,跳过)。

- [ ] **Step 4: 验证**

Run: `rg -n 'no-git|no git|gitignored' skills/preflight/folder-semantics.md skills/status/SKILL.md skills/emit-agents-md/SKILL.md`
Expected: 无输出
Run: `rg -lP '\p{Han}' skills/preflight/folder-semantics.md skills/status/SKILL.md skills/emit-agents-md/SKILL.md` （Expected: 无输出）

- [ ] **Step 5: Commit**

```bash
git add skills/preflight/folder-semantics.md skills/status/SKILL.md skills/emit-agents-md/SKILL.md
git commit -m "feat(skill): force git — drop no-git branches in folder-semantics/status/emit-agents-md"
```

---

### Task 8: 全相收口验证

**Files:** 无改动（验证 + 收尾 commit if needed）

- [ ] **Step 1: 全仓 no-git 残留扫描(skills + scaffolds)**

Run: `rg -n 'no-git|no git|gitignored|deck not gitignored' skills scaffolds`
Expected: 无输出。**若有命中** → 回到对应文件删除后再继续(可能有 Task 6/7 漏网点,如 protocol/SKILL 描述里的二次提及)。

- [ ] **Step 2: 全测试套件**

Run: `uv run python -m pytest scripts/tests/ -q`
Expected: 全绿（`test_hooks.py` 若因 WSL bash 遮蔽 Git Bash 报 returncode=127 = 环境噪音,见 `incidents/wsl-bash-shadows-git-bash-in-tests.md`,非本相回归）。

- [ ] **Step 3: lint 本仓 dogfood deck**

Run: `uv run python scripts/flightdeck_lint.py flightdeck`
Expected: 无新增 CRITICAL/WARNING（本仓 rules.md 暂无 runtime/agents_md 字段 → settings 审计 0 findings;符合 Phase 1「字段可选」)。

- [ ] **Step 4: 英文门(发布面)**

Run: `rg -lP '\p{Han}' skills scaffolds`
Expected: 无输出。

- [ ] **Step 5: 相一完成标记**

本相 done 条件:Task 1–7 commit 齐 + Step 1–4 全过。此时相一可经 `/flightdeck:status` 翻 `done`(交仪式,不在此手动)。相二(launch 探测 + Node 移植 + runtime 兜底删除)另起 plan。

---

## Self-review(对照 spec)

- **§2 配置形态**:frontmatter 字段(Task 3/4)、晋升判据已在 spec 定;**稳态优先级**(Task 4 Step 2 / Task 5 Step 2)✅。
- **§2 `version` 不再唯一结构化**:Task 4 Step 1 ✅。
- **§3.1 git 强制 / 删 no-git**:Task 6/7/8 覆盖 spec 列的 7 处(preflight/landing/exit-ritual/status/emit-agents-md/folder-semantics/protocol/scaffold)✅。
- **校验**:`audit_settings`(Task 1/2)= spec §8「非法值怎么报」的相一落地(WARNING,非阻塞)✅。
- **范围纪律**:launch 探测写入(§4)、运行期读字段(§5)、Node 移植 + runtime 兜底删除(§3.2/3.3)**均不在本相**——Task 6 Step 3 显式标了 runtime 兜底的边界,防越界。
- **无占位符**:代码任务含完整测试 + 实现;散文任务因无单测,给了精确定位 + grep 验证命令(措辞细节标「实现时定」处仅限发布面英文措辞,不影响行为)。
