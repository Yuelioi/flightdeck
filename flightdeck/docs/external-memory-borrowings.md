---
status: active
when_to_read: 规划 flightdeck 记忆/知识/路由相关能力、或考虑引入某个记忆系统机制前
applies_to: [memory, write-gate, cockpit, when_to_read, routing, landing, incidents, retrieval, references]
last_updated: 2026-06-07
---

# 外部记忆系统借鉴清单（ReMe + claude-mem）

> 2026-06-07 深读 `references/ReMe`（Python 向量记忆框架 + benchmark）与 `references/claude-mem`（Claude Code 记忆插件：daemon + SQLite + ChromaDB）后的提炼——**只取可移植的 prompt/策略/概念，弃其基础设施**。

## Headline

两者**架构都是向量/DB 后端**（claude-mem = 常驻 daemon + SQLite + Chroma；ReMe = 向量库 + 可选 BM25），与 flightdeck「人读 markdown + git + 仪式」是**异范式**——基础设施全是 mismatch。但两者的 **prompt / 策略 / 概念操作**可移植，且**多处独立重新推导出 flightdeck 已有设计**（写门 + `[SILENT]` 哨兵、结构化恢复摘要、`when_to_use`=`when_to_read` 路由）——**对 flightdeck 的核心赌注是强验证**。

一个诚实反差：claude-mem **营销** "compression / biomimetic / Endless Mode"，但 `src/` **没 ship 任何 consolidation/decay**（observations 永久累积、无合并无遗忘）。flightdeck 的 `status`/`supersedes`/INDEX-regen 反而是**更真实的生命周期**。

## 可借鉴清单（按 fit×价值排序，均 markdown 原生、不引 DB）

1. **写门 prompt 加负例 + 动词表 + skip-list（claude-mem observer prompt）。** flightdeck 写门现为抽象标准（"改变未来行为"）；claude-mem 用 **GOOD/BAD 成对例**（GOOD="认证现支持 OAuth2 PKCE"；BAD="分析了认证实现并记录"）+ 动词表（implemented/fixed/deployed）+ **skip 清单**（空状态检查、装包无错、空 file-research、已记过的重复操作）+ "facts 无代词、每条自立、含文件名/函数/值"。→ 落进 `rules.md` 或 landing/soft-land 提示。**低成本高收益。**

2. **cockpit 加 `## 关键上下文` 槽（ReMe Compactor `## Critical Context`）。** ReMe 摘要强制保留**精确 file path / 函数名 / 错误串**；flightdeck cockpit 有 focus + 下一步但缺"承重字面量"（正改的路径、失败的测试名）。→ 给 cockpit 加一个软落盘的 `## 关键上下文` AUTO/半 AUTO 区。**纯 markdown。**

3. **`when_to_read` 升为强制主路由键（ReMe `when_to_use`）。** ReMe **嵌入的是 `when_to_use` 条件本身**（不是 body）、并以它为检索主键 + `MemoryValidationOp` 质量闸。flightdeck 已有 `when_to_read`/`applies_to` 但当被动提示。→ `walkaround` flag 泛化/空的 `when_to_read`；preflight 路由**按 `when_to_read` 串**建目录。lint + 读取顺序，无 DB。

4. **失败/弯路记忆 + 对比提取（ReMe `FailureExtractionOp`/`ComparativeExtractionOp`）。** 从**失败**轨迹提教训、对比同任务成功 vs 失败定位决定性差异。flightdeck `incidents/` 正为此，但写门话术偏"最终修复"，**弱化负面知识**（"看似对、因 X 失败"）。→ landing 分类器加显式分支："本回合若放弃某路径/撞墙，写 incident 记**失败路径 + 为何**，不只记最终修复"。本会话自己就有多个被否方案——典型场景。

5. **两跳路由「先地图后领土」（claude-mem 3-layer search / ReMe hop-based recall）。** 先读 INDEX 的 `when_to_read`（hop1）→ 只展开 next-step 需要的 1-2 个工件 body（hop2），不整文件夹批读。flightdeck INDEX 本就是"地图"，把这条纪律写进 preflight 仪式即可。**token 省，零基础设施。**

6. **合并动词 CORROBORATE/REFINE/CORRECT + 永不静默删（ReMe `docs4` consolidate 设计）。** 新知识触及既有工件时分类：同点加证据 / 加精度边界 / 矛盾则**标注不仲裁**（`> 注: 与 [[X]] 矛盾`）；重写**只增不静默删**。→ landing"更新既有工件"路径加这套话术。给 agent/评审一套词汇，防 regen 静默丢知识。（机械边守恒检查跳过——单用户 git，`git diff` 已显删除。）

7. **恢复回归测试（ReMe A/B with-vs-without + HaluMem 三轴）。** 冻结一个 `flightdeck/` deck + "下一步" oracle → 跑 preflight → 断言 surface 对的 next-step + 对的工件。三轴：Integrity（landing 抓对没有，walkaround 近似覆盖）/ Accuracy（cockpit 与 git HEAD 是否一致）/ Resumption（preflight 是否指向真 next-step）。flightdeck 有 `walkaround`（静态）但**无行为级恢复测试**——填真空白。markdown fixture + git，无基础设施。

**次要可选**：claude-mem `<private>` 脱敏标记（flightdeck 进 git，脱敏约定是廉价保险）；`concepts` 闭集标签轴（gotcha/pattern/trade-off/why-it-exists，正交于 kind，捕"为何重读"）；**Cursor 注入用 `alwaysApply` 规则文件**（claude-mem 实测 Cursor `sessionStart` 注入不可靠→改写 `.cursor/rules/*.mdc`，**直接关系 hook-primary 重构的 Cursor 路径**，见 [[cross-host-hooks]]）。

## 不借鉴（异范式，明确弃）

- **向量库 / embedding / BM25**（两者检索核心）——破"markdown+git、可读、可 diff、无网络依赖"。flightdeck 用 INDEX + `when_to_read` 路由替代。
- **常驻 daemon + HTTP worker + 端口/PID/孤儿回收**（claude-mem）——巨大运维面，只因存储是活 DB。
- **每 `PostToolUse` 第二 AI agent 连续 firehose 捕获**（claude-mem）——高噪、永不 consolidate（其生命周期本就空）。flightdeck 的**仪式化、写门、回合末**捕获更优。
- **图算法 Leiden/centrality/RRF**（ReMe `docs4`）——解千节点自增长的规模问题，flightdeck（单用户、人工策展、几十到上百工件）没这问题。
- **type 枚举当结构 schema**（ReMe 6 型）——folder kinds 已覆盖；**ReMe 自己也结论"节点角色由 body 内容定、非 frontmatter type 标签"**。
- **sidecar `meta/*.json` 派生状态**——破单一真相源 + 可读性；git 历史已给 recency/access 信号。
- **后台自治 vault 改写**（ReMe `CronDreamer`，且未 ship）——违"人读、git 可审、仪式驱动"。

## 采纳决策（2026-06-07，用户拍板）

**优先级（按"离核心价值=暂停后正确恢复"最近排序）**：

1. **#2 关键上下文 + #4 失败捕获**——直接提高恢复成功率，**并入 hook refactor**（二者本质是 landing/exit-ritual 产物，重构正在动进出场流程，顺手定义"恢复时真正需要的信息"成本最低）。
2. **#1 写门负例**——提升写入端质量、纯 prompt 层低风险，**单独推进**（不绑进重构）。
3. **#7 恢复回归测试**——最重要，但**放后面**：先让恢复模型稳定，再固化成测试，否则把测试绑死在还会变的流程上（"别测一个还在变的目标"）。

**Cursor 注入路径（架构决策，认真对待）**：claude-mem 实测 Cursor `sessionStart` 注入不可靠（社区踩坑），改用 `.cursor/rules/*.mdc`（`alwaysApply: true`）规则文件、hook 在入场+回合末刷新（见 `references/claude-mem/cursor-hooks/CONTEXT-INJECTION.md`）。**原则：稳定加载 > 优雅加载。** flightdeck 在 hook refactor 里把 **`.cursor/rules/flightdeck-context.mdc` 规则文件作为 Cursor 的主路径独立成立**，而非 sessionStart 的备用——核心行为不绑在已知不稳的 sessionStart 上。已回流进 `2026-06-07-hook-primary-refactor` spec/plan。

> 一句话收束（用户原话）：先做 #2 + #4（并入 hook refactor），随后补 #1，然后等流程稳定后用 #7 作为第一次真正验证 flightdeck 核心价值的行为测试。

## 来源

- `references/ReMe`：`reme/memory/file_based/components/summarizer.yaml`（写门 `[SILENT]`）、`compactor.yaml`（cockpit 类比）、`reme_ai/schema/memory.py`（`when_to_use`）、`reme_ai/summary/{personal,task}/`、`docs4/`（未 ship 的 markdown-graph 设计，概念金矿）、`benchmark/{halumem,bfcl}/`。
- `references/claude-mem`：`plugin/modes/code.json`（capture/skip prompt）、`src/services/sqlite/schema.sql`（记录形状）、`src/services/context/ObservationCompiler.ts`（recency 注入）、`cursor-hooks/CONTEXT-INJECTION.md`（Cursor 规则文件注入）、`plugin/skills/mem-search/SKILL.md`（3-layer 检索）。