---
status: done
summary: 实施 shared-knowledge-sync：index.py 加只读 --sync-status 扫描（+单测）、新 skills/sync/SKILL.md、protocol 字段表登记 synced_from/shared_master + ## 项目覆盖/env 解析约定、walkaround 加 sync-drift audit、README/CHANGELOG 同步。
last_updated: 2026-06-19
implements: specs/2026-06-18-shared-knowledge-sync.md
---

# 实施：跨项目共享知识同步 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让一份共享 checklist/doc 在母库维护、一句 `/flightdeck:sync` 下发进任意消费 deck，产物是 git 可见真文件，母库为准、谁新谁赢、换机不失效。

**Architecture:** 「事实进脚本、判断留模型」。`flightdeck_index.py` 加一个只读 `--sync-status` 扫描算同步态（比 `last_updated`，无 hash）；新 skill `/flightdeck:sync` 消费扫描输出、AI 干合并（刷共享正文、保 `## 项目覆盖` 段 + frontmatter）；母库根从 `rules.md` frontmatter `shared_master`（env 引用）解析；walkaround 加一条被动 sync-drift audit。字段 `synced_from` 纯可选，绝大多数文件不带。

**Tech Stack:** Python 3.8+ 纯 stdlib（`flightdeck_index.py`，新增 `os` import）；`unittest`（`scripts/tests/`）；Markdown skill（`skills/sync/SKILL.md`）。

**仓库铁律：** 本仓只本地 commit，**绝不 push**（commit step 仅本地）。本机 `test_hooks.py` 的 17 个失败是 WSL bash 遮蔽 Git Bash 的环境噪音（见 incident `wsl-bash-shadows-git-bash-in-tests`），与本 plan 无关——验证只看 `test_flightdeck_index.py`。

---

## File Structure

| 文件 | 动作 | 职责 |
| --- | --- | --- |
| `scripts/flightdeck_index.py` | Modify | 加 `import os` + `sync_status(deck)` 纯函数 + `--sync-status` flag（只读，吐 `state<TAB>path<TAB>synced_from`） |
| `scripts/tests/test_flightdeck_index.py` | Modify | 加 `SyncStatusTest`：五态计算 + env 展开 + 只读（不写文件）+ 无 `synced_from` 被忽略 |
| `skills/sync/SKILL.md` | Create | `/flightdeck:sync` 仪式：母库解析、再同步全部 / 首次下发两模式、`## 项目覆盖` 约定、banner |
| `skills/preflight/protocol.md` | Modify | 字段表（canonical）登记 `synced_from` + `shared_master` 两行 |
| `skills/preflight/templates.md` | Modify | rules.md 模板加注释 `shared_master` 键 + 一条 authoring note |
| `skills/walkaround/SKILL.md` | Modify | 「Run all 14」→ 15；加 Audit 15（sync-drift，消费 `--sync-status`） |
| `README.md` / `README.zh.md` / `adapters/claude/README.md` | Modify | 命令表 / 安装目录树登记 `/flightdeck:sync` |
| `CHANGELOG.md` | Modify | Unreleased `### Added` 一条 |

---

## Task 1: `--sync-status` 只读扫描 + 单测（可测核心）

**Files:**
- Modify: `scripts/flightdeck_index.py`（顶部 import 区 + 加函数 + `main()` argparse/dispatch）
- Test: `scripts/tests/test_flightdeck_index.py`（文件末尾加一个 TestCase）

- [ ] **Step 1: 先写失败测试**

在 `scripts/tests/test_flightdeck_index.py` 末尾追加（确认文件顶部已 `import os`、`import tempfile`、`from pathlib import Path`、`import unittest`；缺 `os` 就在 import 区补一行 `import os`）：

```python
class SyncStatusTest(unittest.TestCase):
    """flightdeck_index.sync_status — 共享知识漂移只读扫描。"""

    def _master_file(self, master, relpath, last_updated):
        p = master / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\n"
            f"last_updated: {last_updated}\n---\n# {p.stem}\n",
            encoding="utf-8",
        )

    def _consumer(self, root, shared_master_raw):
        deck = root / "consumer"
        (deck / "checklists").mkdir(parents=True)
        rules = "---\nversion: 3.0\n"
        if shared_master_raw is not None:
            rules += f"shared_master: {shared_master_raw}\n"
        rules += "---\n"
        (deck / "rules.md").write_text(rules, encoding="utf-8")
        return deck

    def _vendored(self, deck, name, last_updated, synced_from):
        (deck / "checklists" / name).write_text(
            f"---\nstatus: active\nsynced_from: {synced_from}\n"
            f"when_to_read: x\napplies_to: [y]\nlast_updated: {last_updated}\n---\n# {name}\n",
            encoding="utf-8",
        )

    def test_states_and_ignores_unsynced(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / "master"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root, str(master))
            self._vendored(deck, "commits.md", "2026-06-18", "checklists/commits.md")   # 母库新
            self._vendored(deck, "ahead.md", "2026-06-25", "checklists/commits.md")     # 项目新
            self._vendored(deck, "gone.md", "2026-06-18", "checklists/missing.md")       # 源已删
            (deck / "checklists" / "local.md").write_text(                                # 无 synced_from → 忽略
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-18\n---\n# local\n",
                encoding="utf-8",
            )
            states = {rel: st for st, rel, _ in sync_status(deck)}
            self.assertEqual(states["checklists/commits.md"], "upstream-changed")
            self.assertEqual(states["checklists/ahead.md"], "locally-ahead")
            self.assertEqual(states["checklists/gone.md"], "dangling")
            self.assertNotIn("checklists/local.md", states)

    def test_in_sync_equal_dates(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / "master"
            self._master_file(master, "checklists/commits.md", "2026-06-18")
            deck = self._consumer(root, str(master))
            self._vendored(deck, "commits.md", "2026-06-18", "checklists/commits.md")
            self.assertEqual(sync_status(deck)[0][0], "in-sync")

    def test_master_missing_when_env_unset(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            deck = self._consumer(root, "$FD_MASTER_DEFINITELY_UNSET_XYZ")
            self._vendored(deck, "commits.md", "2026-06-18", "checklists/commits.md")
            self.assertEqual(sync_status(deck)[0][0], "master-missing")

    def test_env_expansion_resolves_master(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / "master"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root, "$FD_TEST_MASTER")
            self._vendored(deck, "commits.md", "2026-06-18", "checklists/commits.md")
            os.environ["FD_TEST_MASTER"] = str(master)
            try:
                self.assertEqual(sync_status(deck)[0][0], "upstream-changed")
            finally:
                del os.environ["FD_TEST_MASTER"]

    def test_read_only_writes_nothing(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / "master"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root, str(master))
            self._vendored(deck, "commits.md", "2026-06-18", "checklists/commits.md")
            before = {p: p.read_text(encoding="utf-8") for p in deck.rglob("*.md")}
            sync_status(deck)
            after = {p: p.read_text(encoding="utf-8") for p in deck.rglob("*.md")}
            self.assertEqual(before, after)
            self.assertFalse((deck / "INDEX.md").exists())
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_index.py -k SyncStatus -v`
Expected: FAIL —— `ImportError: cannot import name 'sync_status'`（函数尚未存在）。

- [ ] **Step 3: 加 `import os`**

在 `scripts/flightdeck_index.py` 顶部 import 区（`import hashlib` 那组）加一行：

```python
import os
```

- [ ] **Step 4: 实现 `sync_status` 纯函数**

在 `scripts/flightdeck_index.py` 中 `verify_pending` 函数之后（约 L420，`_index_targets` 之前）插入：

```python
def sync_status(deck):
    """共享知识漂移只读扫描：对每个带 `synced_from` 的工件，比它与母库源的
    `last_updated`，返回 (state, project_relpath, synced_from)。写任何文件都不。

    母库根从消费 deck 的 rules.md frontmatter `shared_master`（env 引用，
    os.path.expandvars 展开）解析。状态：
      upstream-changed  母库更新（母库 last_updated 更大）→ /flightdeck:sync 可拉
      in-sync           相等
      locally-ahead     项目更新 → 可能想回流母库（MVP：只报）
      dangling          母库源文件已删
      master-missing    shared_master 缺失/未解析（本机没设 env） → 优雅跳过
    路径相对 deck、POSIX 斜杠；按项目路径排序。排除 archive/。"""
    deck = Path(deck)
    rules = deck / "rules.md"
    raw = ""
    if rules.is_file():
        raw = parse_frontmatter(rules.read_text(encoding="utf-8")).get("shared_master", "") or ""
    master_root = Path(os.path.expandvars(raw)) if raw else None
    master_ok = master_root is not None and master_root.is_dir()
    out = []
    for p in deck.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(deck).parts:
            continue
        try:
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        src = fm.get("synced_from")
        if not src:
            continue
        rel = str(p.relative_to(deck)).replace("\\", "/")
        if not master_ok:
            out.append(("master-missing", rel, src))
            continue
        master_file = master_root / src
        if not master_file.is_file():
            out.append(("dangling", rel, src))
            continue
        proj_lu = fm.get("last_updated", "")
        mast_lu = parse_frontmatter(master_file.read_text(encoding="utf-8")).get("last_updated", "")
        if mast_lu > proj_lu:          # ISO 日期字符串比较 == 时序比较
            state = "upstream-changed"
        elif mast_lu < proj_lu:
            state = "locally-ahead"
        else:
            state = "in-sync"
        out.append((state, rel, src))
    return sorted(out, key=lambda t: t[1])
```

- [ ] **Step 5: 接 `main()` 的 argparse + dispatch**

在 `scripts/flightdeck_index.py` 的 `main()` 里，`--verify-pending` 那条 `add_argument` 之后加：

```python
    ap.add_argument(
        "--sync-status",
        action="store_true",
        help="print (state<TAB>path<TAB>synced_from) for every artifact carrying `synced_from`, "
        "comparing last_updated against the shared_master source (read-only)",
    )
```

并在 `if args.verify_pending:` 的 dispatch 块之后加：

```python
    if args.sync_status:
        for state, path, src in sync_status(args.deck):
            print(f"{state}\t{path}\t{src}")
        return 0
```

- [ ] **Step 6: 跑测试确认通过**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_index.py -k SyncStatus -v`
Expected: PASS（5 个 test 全绿）。

- [ ] **Step 7: 跑全套 index 测试防回归**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全绿（既有 test 不受影响）。

- [ ] **Step 8: 本地 commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(scripts): index.py 加只读 --sync-status 扫描 + 单测

实施 shared-knowledge-sync 的事实层：扫带 synced_from 的工件、从 rules.md
shared_master（env 引用）解析母库根、比 last_updated 出五态。纯只读、可单测。"
```

---

## Task 2: `/flightdeck:sync` skill

**Files:**
- Create: `skills/sync/SKILL.md`

- [ ] **Step 1: 建目录 + 写 SKILL.md**

新建 `skills/sync/SKILL.md`，内容（沿用既有 skill 的双语行文 + frontmatter 习惯；`description` 英文作触发面）：

````markdown
---
name: sync
description: Use when explicitly syncing this deck's vendored shared-knowledge files (a checklist/doc carrying `synced_from`) against their master deck — pulls upstream-changed bodies, preserves the reserved project-specific section + routing frontmatter, and surfaces drift it can't auto-resolve. Triggered by `/flightdeck:sync`.
---

# Flightdeck Sync — vendored shared-knowledge refresh

母库（master deck）是共享知识的唯一真相源；本仪式把消费 deck 里 vendored 的副本按母库刷新。**谁新谁赢**（比 `last_updated`，无 hash）。AI 干合并；`flightdeck_index.py --sync-status` 算事实。

## 母库解析（master resolution）

1. 读消费 deck `rules.md` frontmatter 的 `shared_master`（一个 env 引用，如 `$FLIGHTDECK_SHARED_MASTER`）。
2. 展开 env 变量 → 母库 deck 根。
3. （Claude 便利回退）env 未设时，查用户全局 CLAUDE.md 的跨项目资产库根。
4. 仍解析不到 → 本机没有母库：每文件吐 `master-missing`、**优雅跳过**并报告；vendored 文件本身是自洽真文件，照常可用。

## 两个模式

### A. 再同步全部（裸跑 `/flightdeck:sync`）

1. 跑 `flightdeck_index.py <deck> --sync-status` → 每个 vendored 文件一行 `state<TAB>path<TAB>synced_from`。
2. 逐状态处理：
   - `upstream-changed` → 打开母库源 + 项目副本：**用母库正文替换共享正文；逐字保留项目的 `## 项目覆盖` 段 + 整个 frontmatter；把 `last_updated` 戳成母库的。** 绝不动 `when_to_read` / `applies_to`。
   - `in-sync` → 跳过。
   - `locally-ahead` → 跳过 + 报一句「项目这份比母库新，可能想回流母库」（MVP：只报，不自动回流）。
   - `dangling` → 报告（母库源已删），问用户：删本地副本 / 保留 / 改指。
   - `master-missing` → 报告一次、全跳（本机没母库）。
3. regen INDEX：`flightdeck_index.py <deck>`。
4. 出 banner。

### B. 首次下发（`/flightdeck:sync <母库相对路径>`）

1. 解析母库根；读 `<母库相对路径>` 处的母库文件。
2. 整文件拷贝（frontmatter + 正文）进消费 deck 的**同一相对路径**（母库 `checklists/commits.md` → deck `checklists/commits.md`）。
3. 往其 frontmatter 戳 `synced_from: <母库相对路径>`。
4. 按需本地化路由（项目可改 `when_to_read` / `applies_to`）；项目专属补充另起 `## 项目覆盖` 段。
5. regen INDEX。

## `## 项目覆盖` 约定

vendored 文件的项目专属补充写在一个保留标题段下（`## 项目覆盖`，或本 deck 语言的等价标题，如 `## Project-specific`）。sync **永不覆盖**该段下任何内容。该段**之上**（共享正文）归母库所有，`upstream-changed` 时被刷新。

## Don't do

- 不碰没有 `synced_from` 的文件（本地原创）。
- 不覆盖 frontmatter，也不覆盖 `## 项目覆盖` 段。
- 不自动把 `locally-ahead` 改动回流母库（MVP）。
- 母库缺席不硬失败 —— 优雅 no-op。

## Report

末尾统一 banner（先正文后 banner、一回合一个）：

```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · K locally-ahead · D dangling
[Master]  <已解析母库根>   (或 "master-missing — $FLIGHTDECK_SHARED_MASTER 未设，已跳过")
```
````

- [ ] **Step 2: 结构自检（无运行时测试，肉眼校验）**

确认：frontmatter 有 `name: sync` + 英文 `description`（含 "Triggered by `/flightdeck:sync`."）；两模式齐全；`## 项目覆盖` 约定在；banner 段在。

- [ ] **Step 3: 本地 commit**

```bash
git add skills/sync/SKILL.md
git commit -m "feat(skills): 新增 /flightdeck:sync —— vendored 共享知识刷新

母库为准、谁新谁赢；再同步全部 / 首次下发两模式；保留 ## 项目覆盖 段 +
frontmatter；母库缺席优雅 no-op。消费 flightdeck_index.py --sync-status。"
```

---

## Task 3: protocol.md 字段表登记两字段

**Files:**
- Modify: `skills/preflight/protocol.md`（§ Frontmatter field reference 的表，`version` 行之后）

- [ ] **Step 1: 在 `version` 行后插入两行**

找到表里这一行（约 L70）：

```
| `version` | `rules.md` (root) | **required** (rules.md is mandatory) | — (static identity stamp; future 3.0→3.1 migration anchor) | **launch only** (init) | — |
```

紧随其后插入：

```
| `synced_from` | checklists/docs（仅 vendored） | optional | `/flightdeck:sync` + walkaround sync-drift（`flightdeck_index.py --sync-status`） | `sync`（首次下发时戳） | sync-drift audit；缺失**绝不**报警 |
| `shared_master` | `rules.md` (root) | optional（仅消费共享知识的 deck） | `/flightdeck:sync` + `--sync-status`（env 展开得母库根） | author（env 引用，逐机器设） | — |
```

- [ ] **Step 2: 链接完整性检查**

Run: `uv run scripts/flightdeck_lint.py flightdeck`
Expected: 不因本次编辑新增 dangling-ref（表里两行无 markdown 链接，预期不引入断链）。

- [ ] **Step 3: 本地 commit**

```bash
git add skills/preflight/protocol.md
git commit -m "docs(protocol): 字段表登记 synced_from / shared_master

canonical 字段表是唯一真相源；synced_from 纯可选（缺失不报警）、shared_master
是 rules.md 的 env 引用配置键。"
```

---

## Task 4: templates.md rules.md 模板加 `shared_master`

**Files:**
- Modify: `skills/preflight/templates.md`（§ rules.md 的代码块 + Authoring notes）

- [ ] **Step 1: 模板 frontmatter 加注释键**

找到（约 L11-14）：

```markdown
---
version: 3.0             # REQUIRED — static identity stamp written by launch (future migration anchor; no ritual reads it at runtime)
---
```

改成：

```markdown
---
version: 3.0             # REQUIRED — static identity stamp written by launch (future migration anchor; no ritual reads it at runtime)
# shared_master: $FLIGHTDECK_SHARED_MASTER   # OPTIONAL — only if this deck vendors shared knowledge from a master deck; value is an env-var reference (per-machine path, kept out of git). See protocol field table + /flightdeck:sync.
---
```

- [ ] **Step 2: Authoring notes 加一条**

在 `### Authoring notes` 列表里（`- **Read first**:` 那条之后）追加：

```markdown
- **`shared_master`（可选配置）** — 仅出现在 vendoring 共享知识的 deck。值是 **env 引用**（如 `$FLIGHTDECK_SHARED_MASTER`），绝不写字面路径，使提交进 git 的文件跨机可移植；每台机器把该 env 设成本地母库 deck 根。由 `/flightdeck:sync` / `flightdeck_index.py --sync-status` 消费。
```

- [ ] **Step 3: 本地 commit**

```bash
git add skills/preflight/templates.md
git commit -m "docs(templates): rules.md 模板加可选 shared_master 键 + 注

env 引用、跨机可移植；只在 vendoring 共享知识的 deck 出现。"
```

---

## Task 5: walkaround 加 Audit 15（sync-drift）

**Files:**
- Modify: `skills/walkaround/SKILL.md`

- [ ] **Step 1: 改审计计数**

把 `## Audits` 段的句子（约 L22）：

```
Run all 14 in order.
```

改成：

```
Run all 15 in order.
```

- [ ] **Step 2: 在 Audit 14 之后加 Audit 15**

在 `**Audit 14** — ...walkaround 只浮出、不 drain。` 之后插入：

```
**Audit 15** — 查带 `synced_from` 的 vendored 文件的同步态（只读快速路径 `flightdeck_index.py <deck> --sync-status`）→ `upstream-changed` 报 **INFO**「N 个共享文件母库已更新——跑 `/flightdeck:sync`」；`dangling`（母库源已删）报 **WARN**；`locally-ahead` 报 **INFO**（项目这份较新，可能想回流）；`master-missing`（本机未配 `$FLIGHTDECK_SHARED_MASTER`）**不报**（环境噪音，非漂移）。无带 `synced_from` 文件 → N/A。
```

- [ ] **Step 3: 同步 frontmatter description（保持准确）**

在 SKILL.md frontmatter 的 `description:` 末尾（`done-but-unlanded ...` 枚举处）追加 `, sync drift (vendored shared-knowledge upstream-changed / dangling)`，使 description 不漏 Audit 15。

- [ ] **Step 4: 链接/结构检查**

Run: `uv run scripts/flightdeck_lint.py flightdeck`
Expected: 不新增 dangling-ref。

- [ ] **Step 5: 本地 commit**

```bash
git add skills/walkaround/SKILL.md
git commit -m "feat(skills): walkaround 加 Audit 15 sync-drift

被动浮出 vendored 共享知识漂移：upstream-changed/locally-ahead 出 INFO、
dangling 出 WARN、master-missing 不报。消费 --sync-status，只浮出不修。"
```

---

## Task 6: 发布面文档登记 `/flightdeck:sync`

**Files:**
- Modify: `README.md`（`### Commands` 表）
- Modify: `README.zh.md`（`### 命令` 表）
- Modify: `adapters/claude/README.md`（After install 目录树）

- [ ] **Step 1: README.md 命令表加行**

在 `| `/flightdeck:emit-agents-md` | ... |`（约 L130）之后加：

```markdown
| `/flightdeck:sync` | Refresh this deck's vendored shared-knowledge files against their master deck — newest wins (`last_updated`), preserves the project-specific section. |
```

- [ ] **Step 2: README.zh.md 命令表加行**

在中文表 `| `/flightdeck:emit-agents-md` | ... |`（约 L130）之后加：

```markdown
| `/flightdeck:sync` | 把本 deck 下发的共享知识文件按母库刷新 —— 谁新谁赢（比 `last_updated`），保留项目专属段。 |
```

- [ ] **Step 3: adapters/claude/README.md 目录树加块**

在 `status/` 块（约 L59-60）之后、闭合 ``` 之前加：

```
~/.claude/skills/sync/                  # /flightdeck:sync — refresh vendored shared-knowledge against the master deck
└── SKILL.md
```

- [ ] **Step 4: 本地 commit**

```bash
git add README.md README.zh.md adapters/claude/README.md
git commit -m "docs: README + adapters 登记 /flightdeck:sync 命令"
```

---

## Task 7: CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`（`## [Unreleased]` → `### Added`）

- [ ] **Step 1: Added 段加条**

在 `### Added` 列表末尾（`- **累积段排水纪律**...` 之后）加：

```markdown
- **`/flightdeck:sync` + 共享知识 vendoring**（shared-knowledge-sync spec）— 跨项目共享 checklist/doc：母库为准、谁新谁赢（比 `last_updated`，无 hash）；vendored 文件加可选 `synced_from`，母库根用 `rules.md` frontmatter `shared_master`（env 引用，换机不失效）；`flightdeck_index.py --sync-status` 只读扫描 + walkaround Audit 15；项目专属内容保在 `## 项目覆盖` 段。MVP 单向下发、不自动回流、仅 checklist/doc。
```

- [ ] **Step 2: 本地 commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): 记 shared-knowledge-sync（/flightdeck:sync）"
```

---

## Task 8: 端到端 smoke 验证（dogfood，只读不污染真 deck）

**Files:** 无（只跑命令）

- [ ] **Step 1: 全套 index 测试**

Run: `uv run python -m pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全绿（含新 `SyncStatusTest` 5 个）。

- [ ] **Step 2: 真 deck 上跑 `--sync-status`（确认只读 + 空集不炸）**

Run: `uv run scripts/flightdeck_index.py flightdeck --sync-status`
Expected: **无输出**（本 deck 暂无带 `synced_from` 的文件——spec 定了「先不迁内容」），退出码 0，且未改任何文件（`git status --short` 与跑前一致）。

- [ ] **Step 3: walkaround 不报无关漂移**

Run: `/flightdeck:walkaround`
Expected: Audit 15 对本 deck 报 N/A（无 vendored 文件）；其余审计无因本 plan 新增的 finding。

- [ ] **Step 4: spec 覆盖回扫**

对照 `specs/2026-06-18-shared-knowledge-sync.md` §3.1–§3.5 逐条确认有对应实现：①字段（synced_from 可选 + shared_master）→ Task 3/4；②同步动作两模式 + `## 项目覆盖` + 谁新谁赢 → Task 2；③walkaround 漂移 → Task 5；④env 可移植 → Task 1（解析）+ Task 4（模板）；⑤范围（仅 checklist/doc、单向、不迁内容）→ skill 文案 + Task 8 Step 2 验证。缺则补任务。

- [ ] **Step 5: landing**

跑 `/flightdeck:landing` 收尾：spec + plan 推进/归档判断、cockpit 刷新、本地 commit（不 push）。

---

## Self-Review（写完即扫，发现即改）

- **Spec 覆盖**：§3.1 字段（Task 3/4）✓ · §3.2 同步两模式 + `## 项目覆盖`（Task 2）✓ · §3.3 walkaround 漂移（Task 5）✓ · §3.4 env 可移植（Task 1 解析 + Task 4 模板 + Task 2 解析步骤）✓ · §3.5 事实进脚本/判断留模型（Task 1 + Task 2）✓ · §4 范围 / §5 代价 → skill 文案 + 验证 Step 2 ✓。
- **占位符扫描**：无 TBD/TODO；每个 code/doc step 给了完整待插内容。
- **类型/命名一致**：函数 `sync_status`、flag `--sync-status`（argparse → `args.sync_status`）、状态串 `upstream-changed / in-sync / locally-ahead / dangling / master-missing` 在脚本、测试、skill、walkaround Audit 15 四处一致；字段名 `synced_from` / `shared_master` 全程一致；保留段 `## 项目覆盖` 在 skill 与 protocol 表注一致。
