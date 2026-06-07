---
status: done
summary: 把写门从抽象标准升级为操作化指引（借 claude-mem observer prompt）：① protocol § Write gate 加自立 skip-list 负例 + 一对 ✅/❌「写不写」示例；② exit-ritual 加独立 ### body 质量小节——记实质结果/变更而非过程元叙述 + 一对 ✅/❌「怎么写」示例 + 跨类一行 + 含文件名/函数/值。纯 prose/prompt、不动脚本/数据模型；#1 先于 hook refactor 落地、定稿写门/启发/body 段，refactor Phase2 按 section 锚点跳过。YAGNI：各一对例非每 kind 矩阵、不引 6-type/private/concepts
last_updated: 2026-06-07
---

# 写门操作化：负例 skip-list + GOOD/BAD + body 质量规则

## 背景 / 要解决的问题

flightdeck 写门现为**抽象标准**（`protocol.md:297-299`：「改变未来行为 / 影响决策 / 被反复引用；session 副产物不算；gate strictly」）+ exit-ritual 首匹配启发 (a)–(h)（含 (g) One-off → DO NOT WRITE）。`docs/external-memory-borrowings.md` 的 #1：claude-mem observer prompt 证明**负例（GOOD/BAD 成对 + skip-list）+ 动词表 + "记系统现在做什么而非你做了什么"**比抽象标准更能稳定地让 agent ① 该写才写 ② 写成可复用形态。本 spec 把这套操作化指引并入现有写门，不改数据模型、不引基础设施。

> 用户已定：#1 **单独推进、先于 hook refactor 落地**（纯 prompt 低风险）；placement = **就地增强**（不另起 fragment 文件）。

## 目标

1. **gate 锐化（whether to write）**：`protocol § Write gate` 在现有标准后加 ① 一条**自立 skip-list 负例**（不依赖读 exit-ritual (g)）② **一对 ✅/❌「写不写」示例**。
2. **body 质量（how to write what you keep）**：exit-ritual 加**独立 `###` 小节**——「记实质结果/变更，而非过程元叙述」+ 「每条 fact 自立（无代词）、含文件名/函数/值」+ 一对 ✅/❌「怎么写」示例 + 跨类一行。
3. **不动**：脚本、数据模型、status 语义、frontmatter 契约、folder 分类——纯 prose/prompt。

> **示例形式统一（claude）**：全 spec 示例一律 `✅/❌` 形式（"GOOD/BAD 对"的落地写法）；gate 处 = ✅写/❌不写，body 处 = ✅怎么写好/❌怎么写糟。落地用 `✅`/`❌` 符号，不混用 "GOOD/BAD" 文字标签。

## 非目标（YAGNI）

- **不引 claude-mem 的 6-type 枚举**（folder kinds 已覆盖；ReMe 自己也结论"角色由 body 定非 type 标签"）。
- **不做 per-artifact-kind 的 GOOD/BAD 矩阵**——**一对**通用例足矣，多了是 bloat。
- **不在本 spec 引 `<private>` 脱敏标记 / `concepts` 标签轴**——那是 borrowings 的"次要可选"，各自单独走。
- **不堆 prompt 墙**——claude-mem 原 prompt 很长，flightdeck 蒸馏到要点，**读起来更紧不是更长**。
- 与 #2/#4/#7 无关（那些并入 hook refactor 或后置）。

## 设计

> **现有标准原文（锚点，ds#1）**：`protocol.md:297-299` § Write gate = 「`flightdeck/` records only content that **changes future behavior, influences decisions, or gets referenced repeatedly**. Session byproducts, debug logs, and chat play-by-plays do not qualify. Gate strictly.」本 spec 在这段**之后**追加，原句不动。

### 改动点 1 —— `protocol.md § Write gate`（gate 锐化＝该不该写）

现有段保留，后接一个**自立的 Skip 清单**（不依赖读者看过 exit-ritual (g)）+ 一对**"写不写"对口示例**：

- **Skip —— 命中即 gate 掉（不写）**：空状态检查（status / ls 无后续发现）；**依赖安装 / 构建命令成功且无衍生结论**（`npm/pip/uv install`、build 通过本身）；**无结论的探索**（搜了既没找到、也没排除任何东西）；**无新信息的重复**（同操作再做、未扩覆盖 / 未得新结论 / 未排除新可能）；一次性日志 / 试错流水（"今天日志是" / "我试了 5 种"）。
  - **两个边界（不算 skip，要写）**：① 探索得出**排除性结论**（"X 不是根因"）是负面知识，**写**；② 重复操作**带来新覆盖 / 新结论**，**写**。（去掉"置信度"——flightdeck 无此度量，ds）
- **✅/❌「写不写」对口示例**（gate 层＝是否够格进 deck，每例挂钩 gate 三标准，gpt/ds#1）：
  - ✅ 写：「Cursor 注入定为 `.mdc` 规则文件主路径（sessionStart 不可靠）」（→ **影响未来决策、会被反复引用**）
  - ❌ 不写：「今天跑 `--check` 输出 clean」（一次性状态、不改未来行为）

> 与 exit-ritual **(g) One-off → DO NOT WRITE** 同向但各自完整（ds 重复质疑的答复）：两者服务**不同读者路径**——本 Skip 清单是 `protocol` 写门的 canonical 负面清单（写任何工件前都过），(g) 是 `landing` 分类的首匹配项（落地分类时过）。故措辞各自自立、不交叉依赖阅读；同步成本＝两处都是"一次性/无信息→不写"一句话，可接受。

### 改动点 2 —— `exit-ritual.md`（body 质量＝写下来的怎么写）

**落点（claude#3 / ds#11）**：作 **独立 `### 写工件 body 的质量` 小节**，置于 `## Classification heuristics` 的 **(h) 之后、晋升闸之前**——**不插进 (a)–(h) 首匹配链**（那是门控触发链，不混入写作规范）。内容：

- **记实质结果 / 变更，而非过程元叙述**（gpt#2/ds#3 修正）：**直接陈述系统 / 认知的新事实或新约束**——"`emit()` 加 Codex 分支"、"X 因 Y 失败"——**陈述本身完整即可，无需** `implemented` / `discovered` 之类动词前缀；**不写**过程元叙述（"分析了" / "调研了" / "正在看"）。对立面是**过程元叙述**，不是"状态 vs 变更"。
  > 动词表（implemented/fixed/decided/migrated）仅**示意正例形状、非强制**（gpt/ds）——`discovered`/`decided` 易滑回动作句式，优先直接陈述结果；很多有效陈述（"`emit()` 加 Codex 分支"）根本不需要起头动词。
- **每条 fact 自立**：无代词（"它/这个"）、脱离上下文可独立读懂。
- **含承重字面量**：文件名、函数/符号名、关键值、错误串——不写"改了那个函数"，写"`emit()` 加 Codex 分支"。
- **对口示例 + 跨类一行**（gpt#6 折中，非 per-kind 矩阵）：
  - ✅「`emit()` 现按宿主分支输出注入字段（Claude/Codex/Gemini = `additionalContext`）」 ❌「研究了各宿主的注入字段差异」
  - 决策 / incident 同理：记「X 因 Y 约束选 Z」「X 因 Y 失败」，**不记**「讨论了几种方案」。

> **与 #2 `## 关键上下文` 划层**：#2 是 cockpit 的**恢复槽**（hook refactor 内）；本块是**知识工件 body** 的写法（本 spec）。同强调承重字面量、不同层，互引不重复。

### 与 hook refactor 的边界（防漂移锚点，gpt#8 / ds#10）

#1 与 hook refactor Phase 2 都碰 `protocol.md` / `exit-ritual.md`。**#1 先落地、定稿两段**；refactor Phase 2 prose 重写**按 section 标题锚点跳过**：`protocol.md` 的 **`## Write gate`**（已核实存在＝`protocol.md:297`，反驳 ds 的"可能没有此标题"）、`exit-ritual.md` 的 **`### 写工件 body 的质量`** 小节 + **`## Classification heuristics`** 的 (a)–(h)——这些归 #1，Phase 2 只改 hook/注入叙事段。
- **本 spec 落地后**在 `specs/2026-06-07-hook-primary-refactor.md`（本会话已建、cockpit `## 进行中` 在册）的"文案层"加一行：「写门 / 分类启发 / body 质量段归 `write-gate-examples`，本轮不重写」。
- **残留漂移点（gpt#hook 漏洞，记录在案）**：若 refactor Phase 2 **移动/改名**了这些 section 标题，锚点失效——故规定 Phase 2 **不得改这三处标题文本/层级**（只跳过、不重构）；真要动结构须在 refactor 里显式交接新锚点。现实风险低，记录为唯一剩余漂移点。

## 影响的文件

- 改：`skills/preflight/protocol.md`（§ Write gate 加 skip-list + ✅/❌ 写不写示例）、`skills/preflight/exit-ritual.md`（加独立 `### body 质量` 小节）。
- 注记：`specs/2026-06-07-hook-primary-refactor.md`（加边界一行）。

> **无 scaffold 同步问题（已核实）**：`scaffolds/full/` 只 ship deck（cockpit/INDEX/rules），`protocol.md`/`exit-ritual.md` 仅在 `skills/preflight/`（插件 ship、所有 deck 共享）。改 skills/ 即对所有 deck 生效，无副本要同步。

## 测试 / 验收

- **结构闸（人工核，主体——gpt#7/ds#8 弱 rg 修正）**：① `protocol § Write gate` 新增 = 自立 Skip 清单（含两个"不算 skip"边界）+ 一对 ✅/❌**写不写**示例；② `exit-ritual` 新增 = **独立 `###` 小节**（不在 (a)–(h) 链内）+ 一对 ✅/❌**怎么写**示例 + **跨类一行**（决策/incident 同理）；③ **对口自检**：gate 两例都是"够不够格进 deck"、body 两例都是"同一条该写的知识写好/写糟"，**不串层**（防回归原始错位）。`rg` 仅辅助定位、不作通过判据。
- **软护栏（非 pass/fail 闸——回应 gpt#9/ds#9 的计算争议）**：两处新增**宜 ≤ ~25 非空行**，仅作"是否堆砌"的提示参考、**不是硬闸**（prose 不按行数卡死；"26 行算不算"不构成阻塞）；超出则人工复看可否精简。示例 gate 一对、body 一对，**不出现** 6-type / `<private>` / `concepts`。
- `flightdeck_index.py flightdeck --check` + `flightdeck_lint.py flightdeck` clean（必要非充分：只证 frontmatter/INDEX，不证文案）。

## 风险 / 取舍

- **prompt 膨胀**：明确以"各一对例 + 简短 skip-list"封顶；≤~25 非空行软护栏提示。
- **与 #2 概念重叠**（承重字面量）：已划层——cockpit 恢复槽 vs 工件 body 写法，互引不重复。

## 评审纪要

用户拍板：#1 先行、就地增强、placement 定。

外部 AI 评审一轮（claude/gpt/ds，transient 存 `tmp/`；"不了解项目现状仅供参考"）。三家高度收敛。

**采纳（改了 spec）**：
- **示例放错层**（claude#1/gpt#3/ds#2，最强）→ gate 处改"写不写"对子、body 处改"怎么写"对子，各自对口。
- **动词表 vs "记系统现在做什么"伪冲突**（gpt#2/#3/ds#3）→ 根因是我把 claude-mem 原意（实质结果/变更 vs 过程元叙述）译歪成"系统现在做什么"；改措辞为"记实质结果/变更，非过程元叙述"，动词表保留为结果动词。
- **body 块落点 + 职责**（claude#3/ds#6/#11）→ 独立 `###` 小节、(h) 后晋升前，不插 (a)–(h) 首匹配链。
- **skip-list 精确化 + 自立**（gpt#4/#5/ds#5/#7/claude#2）→ 补两边界（排除性结论要写、有新信息的重复要写）、protocol 处自立。
- **防漂移锚点**（gpt#8/ds#10）→ 用 section 标题锚点、refactor spec 点名两段归 #1。
- **弱验收**（gpt#7/#9/ds#8/#9）→ 改人工结构闸 + ≤~25 行客观护栏，rg 降为辅助。
- **示例只覆盖代码**（gpt#6）→ body 加跨类一行（decision/incident 同理），非 per-kind 矩阵。
- 小：引现有 gate 原文（ds#1）；"空 file-research"措辞改"无结论的探索"消除 kind 联想（ds#4）。

**反驳/部分**：
- ds#6「body 规范完全不该进 exit-ritual」→ 仅采纳独立小节，不采纳完全移走（exit-ritual 本就是 landing 写工件处）。
- ds#4 file-research「依赖 kind」→ 误读（指搜索动作非 artifact kind），措辞微调。
- ds#12 外部依赖未内联 → flightdeck 范式＝引用 deck 工件不内联复制（cross-host 那轮已立，内联=双源）；加指针即可。

外部 AI 评审第二轮（三家明显收敛，gpt：「接近可落地，最大剩余＝文首旧表述未同步」）：

**采纳**：
- **三处表述不一致**（claude/gpt 最强）→ summary + 目标 + 正文统一"记实质结果/变更、非过程元叙述"；示例统一 `✅/❌` 形式。
- **动词表诱导动作句式**（gpt/ds 两条）→ 弱化为示意非强制；强调"直接陈述结果、陈述完整即无需动词前缀"。
- **"置信度"/"装包"外来词**（ds）→ 去置信度；装包明确为依赖安装/构建命令成功无衍生结论。
- **gate ✅ 例偏 body**（gpt/ds#1）→ 换决策类例（Cursor 主路径）+ 挂钩 gate 三标准尾注。
- **验收补漏**（ds）→ 跨类一行 + 对口自检并入结构闸；≤25 行明说**软护栏非硬闸**（消除"26 算不算"）。

**反驳**：
- ds「`## Write gate` 标题可能不存在」→ 已核实 `protocol.md:297` 即此标题。
- ds「边界注记目标文件未核实」→ 本会话已建、cockpit 在册。
- gpt「锚点若 Phase2 改标题失效」→ 采纳：规定 Phase2 不得改这三处标题、真要动须显式交接；记为唯一剩余漂移点。