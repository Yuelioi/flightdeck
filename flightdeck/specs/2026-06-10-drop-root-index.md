---
status: active
summary: 删 root flightdeck/INDEX.md 及其派生链：cockpit 是唯一的板，root INDEX 纯机制件、其唯一可见产物(preflight 计数行)相对 cockpit 进行中+step3 Routing catalog 完全冗余。删脚本 regen_root_index/folder_summary/imported_summary + yield root（保留 FOLDER_ORDER/IMPORTED_KINDS，仍被 REGEN_FOLDERS+lint 用）、相关测试、dogfood+scaffold 两份 INDEX.md、preflight step2/报告首行、walkaround Audit5 根计数、landing/exit-ritual 刷新 root 表述、protocol 文件夹图根 token、templates root 段。folder INDEX 全保留、恢复载荷红线零影响。
last_updated: 2026-06-10
graduate: false
---

# 删除 root INDEX.md（de-scope 续）

## 动机

root `flightdeck/INDEX.md` 不是用户看的板（记忆 `cockpit-is-the-only-board`：用户只看 cockpit 导航）。它纯粹是机制件，由脚本/turn-end hook 机械重建，内容是各文件夹的状态计数。它唯一「被人看到」的产物是 preflight 报告首行 `Root INDEX: specs/ — N | plans/ — N | …`，而这串计数相对其它已有产物**完全冗余**：

- specs/plans 的 active 项已在 cockpit `## 进行中` 按名列出（preflight 报告本就含此块）；
- knowledge 三类（docs / checklist / incident）的计数已在 preflight step3 `Routing catalog` 行显示；
- references 计数极少被看。

删它去掉一整条派生链（一个脚本函数簇 + 两份磁盘文件 + 一个 walkaround 审计项 + 多处 skill 表述），契合 3.0 de-scope 第0版「砍派生 / 冗余 / 防御性机制」主线（记忆 `flightdeck-3.0-descope-v0`）。

**红线**：核心卖点「上下文不丢」零损失——folder INDEX（携 routing 的 `when_to_read`/`applies_to`）全保留，cockpit + 各 folder INDEX 的恢复载荷不动。本次只砍根级的派生计数件。

## 范围裁定

- **只删根 INDEX**，不动任何 folder INDEX。folder INDEX 携路由价值（catalog warm-up 读它们），是真资产。
- preflight 计数行的去向：**整行删掉**（用户拍板），不改为现场计算——保留一个用户基本不看的显示没有价值。
- **设计意图显式确认**：删后「**deck 不带 root INDEX**」是**第一公民合法状态**，而非待修复缺陷——lint / walkaround / preflight 都不得把「缺 root INDEX」当问题报。这是本 spec 的意图断言（测试通过只证明「不报错」是代码行为；意图由此处与「不动」节共同钉死）。
- **名字消失本身是目标**：`regen_root_index` / `folder_summary` / `imported_summary` 三个符号名连同其测试/注释/fixture 引用要**彻底消失**，不接受「内联实现但保留名字」——验收 §4 的字面量零命中即据此（这是显式取舍，不是误伤）。

## 删除清单

### 1. 脚本 `scripts/flightdeck_index.py`

删除：
- `regen_root_index(deck)` 函数；
- `folder_summary(folder)` 函数（唯一调用方是 `regen_root_index`）；
- `imported_summary(folder)` 函数（唯一调用方是 `regen_root_index`）；
- regen 目标生成器里的 `yield "root", deck / "INDEX.md", regen_root_index(deck)` 一行。

**保留**（有其它调用方，删了会破坏别处；**用描述性引用，不写固定行号——删除会使行号漂移**）：
- `FOLDER_ORDER` —— `REGEN_FOLDERS` 定义处 `[name for name in FOLDER_ORDER if name not in IMPORTED_KINDS]` 依赖它来**决定哪些 folder 被 regen + 其顺序**（不只 lint 用）；
- `IMPORTED_KINDS`（`= {"references"}`，语义=references 是手维护的外部导入、排除出 auto-regen）—— 被 `REGEN_FOLDERS` 推导 + `flightdeck_lint.py` 的 `KNOWN_FOLDERS` 依赖；其语义独立于被删的 summary 函数，retention 成立。

**连带效果——单点机制坐实，非假设**：`_index_targets(deck)` 是**唯一**的 INDEX 目标生成器，被三条路径共用——`main` 的 regen、`main --check` 的 drift、`index_drift`（`flightdeck_lint.py` 用）。root 仅通过其末尾 `yield "root", …` 一行进入。删这一行 → root 同时退出 regen / `--check` / drift / 「缺 INDEX 时新建最小 INDEX」的逻辑（该新建逻辑也只作用于 `_index_targets` 产出的目标）。**不存在独立的「确保 root INDEX 存在」路径**，故无需额外改代码。（行号随实现漂移，按符号名定位。）

### 2. 测试

- `scripts/tests/test_flightdeck_index.py`：删与 `regen_root_index` / `folder_summary` / `imported_summary` 相关的导入与用例（涉及行约 15–18、232、247、263、271、273、425、756、764 处——以实际为准，删到这三个名字零引用）。
- `scripts/tests/test_flightdeck_index.py`：除删 4 个测试类外，还需清 4 处 *incidental* root INDEX fixture（`MainCliTest` / `CockpitWiredIntoMainTest` / 两个 area-INDEX 测试在 deck 里顺手写了 `<!-- AUTO:root -->` 的 root INDEX，但断言无关 root）——删这些 fixture 写入即可（`AUTO:root` 字面量归零，断言不变仍通过）。
- `scripts/tests/test_flightdeck_init.py`：`test_creates_full_deck_and_substitutes_cockpit` 原断言 `assertTrue((deck/"INDEX.md").exists())`（新 deck 出厂带 root INDEX）→ **反转为 `assertFalse(..., "root INDEX must not ship")`**，把「root INDEX 不出厂」钉成测试（呼应「合法状态」意图）。
- `scripts/tests/test_hooks.py`：`test_stop_projectdir_via_{gemini,cursor}_var` 原用「hook 重建 root INDEX」作 projectdir 解析的副作用证据——改用 `specs/INDEX.md` 被创建作等价副作用（`_mk_regenerable_deck` 加一个 specs/ 工件、断言改 `specs/INDEX.md`）。
- `scripts/tests/test_flightdeck_lint.py`：**两处**（已核实断言，给单一改法，不留分叉）——
  - `test_drifted_index_is_warning`（约 232–244）：当前同时造 specs 与 root 的 drift INDEX，断言 `assertIn("specs", labels)` + `assertIn("root", labels)`。root 退出 `_index_targets` 后 `audit_index_consistency` 不再产出 "root" 标签 → **删第 238–240 行的 root INDEX.md 写入 + 删第 244 行 `self.assertIn("root", labels)`**；保留 specs drift 断言（仍验 drift 检测）。
  - `test_clean_index_no_finding`（约 246–258）：写干净 specs+root INDEX，断言 `audit_index_consistency(deck) == []`。**删第 254–257 行的 root INDEX.md 写入**；断言不变——它现在额外坐实「无 root INDEX 的 deck 不被误报」。

### 3. 文件删除

- `flightdeck/INDEX.md`（dogfood deck）；
- `scaffolds/full/flightdeck/INDEX.md`（出厂脚手架——新建 deck 不再带根 INDEX）。

### 4. skills 文案

- `skills/preflight/SKILL.md`：step2 同时读 root INDEX **和 cockpit**——**step2 保留、编号不顺延**，仅删其中「Read `flightdeck/INDEX.md`（root INDEX, full）」一句，cockpit 读取留；`## Output format` 去掉首行 `Root INDEX: …`；Fallback 段对 `plans/INDEX.md`、`specs/INDEX.md` 的引用保留（那是 folder INDEX，不受影响）。
- `skills/walkaround/SKILL.md`：Audit5 **保留为 Audit5**（不改编号、不造悬挂引用）——仅删其中「检查根 `flightdeck/INDEX.md` 的文件夹摘要计数」一句，folder INDEX 一致性审计全留。
- `skills/landing/SKILL.md`：step3 去掉「若任一文件夹计数变了，也刷新根 `flightdeck/INDEX.md` AUTO 区」表述；保留「regen 每个 folder INDEX」。
- `skills/preflight/exit-ritual.md`：去掉同款「refresh root INDEX if counts changed」表述（第 38 行附近）；「each `INDEX.md` AUTO region」这类泛指措辞保留（root 只是不再在列，措辞仍成立）。
- `skills/preflight/protocol.md`：文件夹图第 223 行形如 `├── cockpit.md   rules.md   INDEX.md   [comment]`——**只删该行的 `INDEX.md` token**，保留同行 `cockpit.md` + `rules.md` + 注释；删后收敛多余空格、目视该 ASCII 图与上下行对齐；下方各 folder 行的 `INDEX.md` 全保留。
- `skills/preflight/templates.md`：删 `## INDEX.md — root` 模板段（约第 187–192 行）；folder INDEX 模板保留。
- `skills/preflight/folder-semantics.md`：删整个 `### \`INDEX.md\` — root index` 子节（含 `AUTO:root` 示例 + 「downgradeable component」注）；其余 folder/layout 说明保留。
- `skills/status/SKILL.md`：删两处 root INDEX 引用——「(+ that folder's count in the root INDEX)」与 fast-path 句里的「the root INDEX, 」。folder INDEX 引用保留。

### 5. bootstrap / 注入 / AGENTS.md

- `skills/_shared/bootstrap.md` 的「each `INDEX.md` AUTO region」泛指措辞保留，无需改。
- 实现末轮**手动**跑一次 `/flightdeck:emit-agents-md`（AGENTS.md 由 cockpit 派生，无独立校验脚本——由实现者在合并前执行），确认无 root INDEX 引用、且**未新增任何根级索引概念**的等价表述。

## 不动

- 所有 folder INDEX（specs / plans / incidents / checklists / docs / references 的 INDEX.md）；
- turn-end hook 实现（仍 regen 各 folder INDEX AUTO 区，root 自然退出）；
- 恢复载荷（cockpit + folder INDEX 内容）——红线零影响；
- walkaround / lint 的 folder INDEX 一致性审计——它走 `_index_targets` 逐 label 独立比对（folder INDEX 自身 vs 其 regen），**不以 root INDEX 为参照基线**，故删 root 后 folder 审计行为不变。

## 验收

1. `uv run pytest scripts/tests/` 全绿。
2. `uv run scripts/flightdeck_index.py flightdeck` regen 后**不生成** root INDEX（`flightdeck/INDEX.md` 不存在）；`uv run scripts/flightdeck_index.py flightdeck --check` 退出码 0（clean）。
3. preflight 跑一遍：报告**首行无 `Root INDEX: …` 计数行**；以下核心块照常产出且内容等价——Cockpit 行、Routing catalog 行、待验证块、下一步（item #1）。（不强求逐字节「不变」——行数/空行受首行删除影响属预期；断言的是这些块仍在且语义不变。）
4. **残留扫描**（在仓库根执行；扫描对象是**活的代码 + skill 散文 + 出厂脚手架**这三个 surface，**不含本 deck 自描述件**）：
   - **符号名 / 标记 / 字面量——`scripts/ skills/ scaffolds/` 零命中**，固定命令（POSIX 可移植）：
     ```
     grep -rn -e regen_root_index -e folder_summary -e imported_summary -e 'AUTO:root' -e 'Root INDEX' \
       scripts/ skills/ scaffolds/ --exclude-dir=__pycache__
     ```
     **刻意不扫全仓**：drop-root-index 的 spec/plan/cockpit/INDEX 本身在描述这次删除，必然出现这些符号名（自描述件），那是合法内容，不是残留。`references/`、`archive/`、`tmp/`（外评原文）同理排除。要验证的不变量是「**活 surface 零引用**」。
   - **描述性提法（`根 INDEX` / `顶层 INDEX` / `root INDEX`）——仅 `skills/` + `scaffolds/` 零命中**。同理：`docs/`、commit message、迁移注释里「曾有 root INDEX」是合法历史叙述，删除目标只是活的运行时引用。
5. 两份 `INDEX.md`（dogfood `flightdeck/INDEX.md` + 出厂 `scaffolds/full/flightdeck/INDEX.md`）已删除；`scaffolds/full/flightdeck/` 下各 folder INDEX（specs/plans/…）保留。
6. **AGENTS.md**（手动，合并前）：跑 `/flightdeck:emit-agents-md` 后，`AGENTS.md` 既无 root INDEX 引用、也未新增任何根级索引概念的等价表述（现状本就无；「the folder `INDEX.md` files」指 folder INDEX，保留）。
7. **新建 deck 端到端**（手动；`/flightdeck:launch` 依赖能跑脚本的环境，本仓有 `uv`）：起一个全新 deck——
   ```
   cp -r scaffolds/full/flightdeck /tmp/fd-e2e && uv run scripts/flightdeck_index.py /tmp/fd-e2e --check
   ```
   断言：(a) `/tmp/fd-e2e/INDEX.md` **不存在**；(b) `--check` 退出码 0（无 missing-INDEX / 无 drift）；(c) 对该 deck 跑 `/flightdeck:preflight` 不报 missing root INDEX。

## 评审纪要

外部三家（ds / claude / gpt）评审 v1 spec（reviewer 不了解项目现状，技术过滤后处置）：

**采纳并已折入**：
- **lint 测试改法是分叉**（三家一致命中，最强信号）：v1 写「二选一，视断言而定」。已核实实为**两处**测试（`test_drifted_index_is_warning` + `test_clean_index_no_finding`），各给确定单一改法，见删除清单 §2。
- **残留扫描范围过窄**（claude/gpt）：v1 只扫 `scripts/ skills/`。已扩为全仓 + 显式排除 + 补 `Root INDEX` 字面量，见验收 §4。
- **缺 scaffold/AGENTS.md 端到端验收**（claude/gpt）：补验收 §6、§7。
- **protocol 删除粒度模糊**（ds）：已写明 token 级删法，见 skills 文案 §protocol。
- **walkaround Audit5 编号漂移顾虑**（gpt）：已写明 Audit5 保留编号、仅删根计数子句。

**技术过滤（reviewer 不了解现状）**：
- ds「漏删 `turn-end-hook.md`」：**本项目无此文件**。hook 实现即 `flightdeck_index.py`；`_index_targets` 是 regen/`--check`/drift 的唯一目标生成器，删一行 `yield "root"` 单点排除——gpt「--check / 缺 INDEX 新建是假设」由此机制坐实为非假设（已写入删除清单 §1 连带效果）。
- ds「`last_updated` 是未来日期」：今天即 2026-06-10。
- gpt「`AUTO:root` 标记可能不存在」：存在（regen 产出 + 现 INDEX 第 3 行），扫它有效。
- claude/ds 关于 `FOLDER_ORDER` 保留理由：已补「REGEN_FOLDERS 用它决定 regen 范围+顺序」，retention 成立。

**v2 复审（ds / gpt，两家均判 v2 扎实、无阻塞）——采纳并折入 v3**：
- 重复的 `## 评审纪要` 占位段（两家都抓到）→ 已删。
- 设计意图「缺 root INDEX 是否合法」未显式确认（ds）→ 已在「范围裁定」钉死为第一公民合法状态。
- 脚本硬行号脆（ds）→ §1 改描述性符号引用。
- §4「全仓」vs「限定 skills/+scaffolds/」措辞矛盾 + `--exclude-dir={}` 不可移植（ds/gpt）→ §4 拆两类扫描、给可移植固定命令。
- 「其余不变」过强（gpt）→ §3 改为「列核心块、语义不变」。
- 名字消失是显式目标（gpt）→ 已在「范围裁定」写明。
- e2e 缺新 deck `--check` + 缺命令 + 时机（gpt/ds）→ §7 给 cp+`--check` 命令、标注手动。
- AGENTS.md 验收过窄（gpt）→ §6 加「未新增根级索引等价表述」。

**v2 复审技术过滤**：ds「step2 删除致编号顺延」→ step2 同时读 cockpit，仅删 root 子句、编号不动；ds「Audit5 folder 审计依赖 root 基线」→ folder 审计逐 label 独立、不参照 root（已写入「不动」节）；ds「IMPORTED_KINDS 语义」→ 语义独立于被删函数，retention 成立（已写入 §1）。
