---
status: done
summary: 把 drop-root-index spec 逐文件落地：相位1 脚本+测试（删 regen_root_index/folder_summary/imported_summary + _index_targets 的 yield root；改 2 处 lint 测试、删 index 测试；删 dogfood+scaffold 两份 root INDEX.md；pytest 绿 + --check clean）→相位2 skills 文案（preflight step2 子句+报告首行 / walkaround Audit5 根计数子句 / landing step3 / exit-ritual / protocol 图 token / templates root 段）→相位3 验收扫尾（残留 grep 两类、AGENTS.md regen、新 deck e2e --check）。每相位可独立 git revert。
last_updated: 2026-06-10
implements: archive/specs/2026-06-10-drop-root-index.md
---

# 删除 root INDEX.md —— 落地计划

> **For agentic workers:** REQUIRED SUB-SKILL: 用 superpowers:executing-plans 逐任务执行（本计划为删除型，inline 执行 + 相位 checkpoint 最合适；非 subagent-driven）。步骤用 `- [ ]` 复选框跟踪。

**Goal:** 删掉 root `flightdeck/INDEX.md` 及其整条派生链，使「deck 不带 root INDEX」成为合法状态，folder INDEX 与恢复载荷零影响。

**Architecture:** 三相位、各自可 `git revert`：①脚本+测试（唯一代码改动，`_index_targets` 删 `yield "root"` 单点退出 + 删三函数 + 删/改测试 + 删两份 INDEX 文件）→②skills 散文（6 处运行时引用）→③验收扫尾（残留扫描 / AGENTS.md / 新 deck e2e）。

**Tech Stack:** Python（`scripts/flightdeck_index.py` / `flightdeck_lint.py`，`uv run pytest`）、Markdown skills、git。

---

## 相位 1 — 脚本 + 测试 + 文件删除

**Files:**
- Modify: `scripts/flightdeck_index.py`（删 `regen_root_index` / `folder_summary` / `imported_summary` 三函数 + `_index_targets` 内 `yield "root", …` 一行）
- Modify: `scripts/tests/test_flightdeck_index.py`（删 import 名 + 4 个测试类）
- Modify: `scripts/tests/test_flightdeck_lint.py`（改 2 个测试方法）
- Delete: `flightdeck/INDEX.md`、`scaffolds/full/flightdeck/INDEX.md`

- [ ] **Step 1.1：删脚本三函数**

在 `scripts/flightdeck_index.py` 删除整个 `def folder_summary(folder):`、`def imported_summary(folder):`、`def regen_root_index(deck):` 三个函数体（连同各自前的 docstring/注释）。**保留** `FOLDER_ORDER`、`IMPORTED_KINDS` 两个模块级常量不动（仍被 `REGEN_FOLDERS` 推导 + lint `KNOWN_FOLDERS` 用）。

- [ ] **Step 1.2：删 `_index_targets` 里的 root yield**

在 `def _index_targets(deck):` 内删掉这一行：

```python
    yield "root", deck / "INDEX.md", regen_root_index(deck)
```

保留其余（folder 循环、nestable area、cockpit yield）。这是 root 退出 regen / `--check` / drift / 「缺 INDEX 新建」的单点。

- [ ] **Step 1.3：删 index 测试的 import 与测试类**

在 `scripts/tests/test_flightdeck_index.py`：
1. 从顶部 import 块删掉 `folder_summary,`、`imported_summary,`、`regen_root_index,` 三行（保留其余 import）。
2. 删除整 4 个测试类：`RegenRootIndexTest`、`FolderSummaryTest`（含其中的 `test_imported_summary_counts_imported_entries`）、`RootIndexDocsTest`、`ObsoleteCountExcludeTest`（该类用 `folder_summary` 验「obsolete 不计入计数」——计数随 root 退场而消失；注意**不要**误删 `ObsoleteRoutingExcludeTest`，它验 folder INDEX 路由排除 obsolete，走 `regen_folder_index`，保留）。

- [ ] **Step 1.4：改 lint 测试 `test_drifted_index_is_warning`**

在 `scripts/tests/test_flightdeck_lint.py` 的 `test_drifted_index_is_warning` 里：删掉写 root drift INDEX 的这段——

```python
            (deck / "INDEX.md").write_text(
                "# root\n\n<!-- AUTO:root -->\nSTALE\n<!-- /AUTO -->\n", encoding="utf-8"
            )
```

并删掉断言 `self.assertIn("root", labels)`。保留 specs 的写入与 `self.assertIn("specs", labels)`（仍验 drift 检测对 folder INDEX 生效）。

- [ ] **Step 1.5：改 lint 测试 `test_clean_index_no_finding`**

在同文件 `test_clean_index_no_finding` 里删掉写 root INDEX 的这段——

```python
            (deck / "INDEX.md").write_text(
                "# root\n\n" + flightdeck_index.regen_root_index(deck) + "\n",
                encoding="utf-8",
            )
```

保留 specs INDEX 写入与断言 `self.assertEqual(audit_index_consistency(deck), [])`。改后该测试额外坐实「无 root INDEX 的干净 deck 不被误报」。（若 `import flightdeck_index` 在该方法内已无其它用处可一并清理，但不强求。）

- [ ] **Step 1.6：跑测试，必须全绿**

Run: `uv run pytest scripts/tests/ -q`
Expected: PASS，0 failed（原 164 → 删类后略少，全绿）。若有 `regen_root_index`/`folder_summary`/`imported_summary` 未定义报错，回 Step 1.3 查漏的 import/引用。

- [ ] **Step 1.7：删两份 root INDEX 文件**

```bash
rm flightdeck/INDEX.md scaffolds/full/flightdeck/INDEX.md
```

- [ ] **Step 1.8：regen + --check，确认 root 不再生成**

Run: `uv run scripts/flightdeck_index.py flightdeck && uv run scripts/flightdeck_index.py flightdeck --check; echo "exit=$?"`
Expected: regen 后 `flightdeck/INDEX.md` **仍不存在**（脚本不再 yield root）；`--check` 输出 `exit=0`（clean，无 missing-INDEX 报 root）。

- [ ] **Step 1.9：提交相位 1**

```bash
git add -A
git commit -F- <<'EOF'
refactor(index): 删 root INDEX 派生链——脚本三函数 + _index_targets yield + 两份 INDEX 文件（相位1）

regen_root_index/folder_summary/imported_summary 三函数删除；_index_targets 删 yield "root" 单点退出 regen/--check/drift；删 dogfood + scaffold 两份 root INDEX.md。保留 FOLDER_ORDER/IMPORTED_KINDS（REGEN_FOLDERS+lint 仍用）。同步删 4 个 index 测试类、改 2 处 lint 测试。pytest 绿 + --check clean。

implements: specs/2026-06-10-drop-root-index.md
EOF
```

---

## 相位 2 — skills 散文（6 处运行时引用）

**Files:**
- Modify: `skills/preflight/SKILL.md`、`skills/walkaround/SKILL.md`、`skills/landing/SKILL.md`、`skills/preflight/exit-ritual.md`、`skills/preflight/protocol.md`、`skills/preflight/templates.md`、`skills/preflight/folder-semantics.md`、`skills/status/SKILL.md`

- [ ] **Step 2.1：preflight SKILL.md**

`skills/preflight/SKILL.md`：
1. step2 当前形如「Read `flightdeck/INDEX.md`（root INDEX, full）. Read `flightdeck/cockpit.md`（full）…」——**仅删 root INDEX 那句**，保留 cockpit 读取与 step 编号（step2 不顺延）。
2. `## Output format` 块删掉首行 `Root INDEX: specs/ — N (N active, N done) | plans/ — N active | …`（连同其示意行）。
3. Fallback 段里 `plans/INDEX.md` / `specs/INDEX.md`（folder INDEX）引用**保留**。

- [ ] **Step 2.2：walkaround SKILL.md**

`skills/walkaround/SKILL.md` 的 Audit5：删句「检查根 `flightdeck/INDEX.md` 的文件夹摘要计数」。**Audit5 编号与 folder INDEX 一致性审计全留**（不顺延、不造悬挂引用）。

- [ ] **Step 2.3：landing SKILL.md**

`skills/landing/SKILL.md` step3：删表述「若任一文件夹计数变了，也刷新根 `flightdeck/INDEX.md` 的 `<!-- AUTO -->` 区」（中英视实际文案）。保留「regenerate 每个 changed folder 的 INDEX」与 fast-path 描述（但 fast-path 句若写「regenerates every folder INDEX, the root INDEX, and the cockpit」需删其中 the root INDEX）。

- [ ] **Step 2.4：exit-ritual.md**

`skills/preflight/exit-ritual.md`：删「refresh root INDEX if counts changed」同款表述（INDEX regeneration 节）。**保留**「each `INDEX.md` AUTO region」这类泛指（root 退场后措辞仍成立）。

- [ ] **Step 2.5：protocol.md 文件夹图**

`skills/preflight/protocol.md` 的文件夹图根行 `├── cockpit.md   rules.md   INDEX.md   [comment]`：删 `INDEX.md` token，收敛多余空格，目视该 ASCII 图与上下行对齐。下方各 folder 行的 `INDEX.md` 全留。

- [ ] **Step 2.6：templates.md**

`skills/preflight/templates.md`：删 `## INDEX.md — root` 整段模板（含其 `<!-- AUTO:root -->` 示例）。folder INDEX 模板保留。

- [ ] **Step 2.7：folder-semantics.md**（残留扫描补漏 surface）

`skills/preflight/folder-semantics.md`：删整个 `### \`INDEX.md\` — root index` 子节（root INDEX 说明 + `AUTO:root` 示例块 + 「downgradeable component」注），保留前后 layout/landing-log 说明。

- [ ] **Step 2.8：status/SKILL.md**（残留扫描补漏 surface）

`skills/status/SKILL.md`：删两处——「(+ that folder's count in the root INDEX)」与 fast-path 句里的「the root INDEX, 」（保留 folder INDEX + cockpit）。

- [ ] **Step 2.9：提交相位 2**

```bash
git add -A
git commit -F- <<'EOF'
docs(skills): 去 root INDEX 运行时引用——preflight/walkaround/landing/exit-ritual/protocol/templates（相位2）

preflight step2 删 root 读取句 + 报告首行；walkaround Audit5 删根计数子句（编号留）；landing step3 / exit-ritual 删刷新 root 表述；protocol 文件夹图删根 token；templates 删 root 模板段。folder INDEX 引用全留，"each INDEX.md AUTO region" 泛指留。

implements: specs/2026-06-10-drop-root-index.md
EOF
```

---

## 相位 3 — 验收扫尾

**Files:** 无源码改动（验收 + 可能的回扫修补）

- [ ] **Step 3.1：符号名/标记/字面量——活 surface 零命中**

Run:
```bash
grep -rn -e regen_root_index -e folder_summary -e imported_summary -e 'AUTO:root' -e 'Root INDEX' \
  scripts/ skills/ scaffolds/ --exclude-dir=__pycache__
```
Expected: 无输出（退出码 1）。**不扫全仓**：drop-root-index 的 spec/plan/cockpit/INDEX 自描述件必然含这些符号名，是合法内容非残留；要验证的是活的代码+skill+脚手架零引用。有命中 → 回对应相位补删（本轮就是这样补到了 folder-semantics.md / status/SKILL.md）。

- [ ] **Step 3.2：描述性提法仅限 skills/ + scaffolds/ 零命中**

Run: `grep -rn -e '根 INDEX' -e '顶层 INDEX' -e 'root INDEX' skills/ scaffolds/`
Expected: 无输出。（`docs/`、commit、迁移注释里的历史叙述不在此扫描范围、合法保留。）

- [ ] **Step 3.3：两份文件确已删除**

Run: `ls flightdeck/INDEX.md scaffolds/full/flightdeck/INDEX.md 2>&1`
Expected: 两个都报 No such file。`ls scaffolds/full/flightdeck/specs/INDEX.md` 仍存在（folder INDEX 保留）。

- [ ] **Step 3.4：新建 deck e2e --check clean**

Run:
```bash
rm -rf /tmp/fd-e2e && cp -r scaffolds/full/flightdeck /tmp/fd-e2e && \
  uv run scripts/flightdeck_index.py /tmp/fd-e2e --check; echo "exit=$?"; \
  ls /tmp/fd-e2e/INDEX.md 2>&1
```
Expected: `exit=0`（无 missing-INDEX/drift）；`/tmp/fd-e2e/INDEX.md` 报 No such file。（Windows 下用 `$env:TEMP` 等价路径。）

- [ ] **Step 3.5：AGENTS.md regen（手动）**

跑 `/flightdeck:emit-agents-md`，确认 `AGENTS.md` 无 root INDEX 引用、未新增任何根级索引概念等价表述（「the folder `INDEX.md` files」指 folder INDEX，保留）。`git diff AGENTS.md` 审一眼。

- [ ] **Step 3.6：全量测试复跑**

Run: `uv run pytest scripts/tests/ -q`
Expected: 全绿。

- [ ] **Step 3.7：提交相位 3（若有扫尾改动 / AGENTS.md 变更）**

```bash
git add -A
git commit -F- <<'EOF'
chore(deck): drop-root-index 验收扫尾——残留扫描清零 + AGENTS.md regen（相位3）

implements: specs/2026-06-10-drop-root-index.md
EOF
```
（若相位 3 无任何文件变更，跳过提交。）

---

## 收尾（人工，非本计划步骤）

三相位绿后，spec+plan 由用户签收 → landing flip `done` + 归档（spec `graduate:false`，不改写进 docs）。
