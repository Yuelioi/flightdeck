---
status: done
summary: 统一所有流程输出格式（先正文 → 末尾一个标准 banner，状态/着陆恒在最后、一回合一个）+ 可逆动作无门自动执行 + 统一「翻回」撤销 + soft-landing 覆盖全生命周期状态（brainstorm/spec/plan/部分/待审/通过/即席）+ Pending Review 写明验证后动作；确保随时关闭、下次 preflight 从看板恢复
last_updated: 2026-06-16
---

# Act-report-close loop: ungated reversible auto-exec + unified flow-output + recoverable across lifecycle

## 背景 / 动机

用户的实际流程是纯 AI 全自动驱动：`preflight` 报下一步 → 用户「go」→ AI 执行 → 收尾。两条铁律：

1. **纯 AI 操作**——95% 的可逆 deck 动作不需事前确认；与其为 5% 留 95% 的确认噪音（还压热路径预算），不如可逆动作全放过，只留一个统一「翻回」通道。
2. **上下文随时关闭都可恢复**——任何回合、任何生命周期阶段被打断，用户随时关对话，下次 `preflight` 只看 cockpit + INDEX 就能干净接手，不依赖对话历史。

本 spec 落第二根支柱 + 与之咬合的执行侧（无门自动执行）+ 把所有流程的输出收成一个统一格式。配置面（删人工开关、rules.md 改 AI 落盘）拆给 **Spec 2 `ai-authored-config`**。

> Spec 1 / 2。本篇定义「AI 做什么不问、做完怎么报告、怎么撤、输出长什么样」；Spec 2 的「AI 按用户自然话写 rule」正是被本篇报告/撤销循环覆盖的一个可逆动作。

## 决策（已与用户拍板）

1. **可逆 deck 动作无前置 confirm 门**：直接按判断执行，删散落各 skill 的确认门 + 谨慎散文。
2. **统一一个「翻回」撤销通道**替代 per-action 门：撤销**最近一个着陆单元**整体（见 Part 1）。
3. **统一流程输出格式**：所有 flightdeck 流程＝先正文散文 → 末尾一个标准化 banner + 关键信息；banner 恒在最后、一回合只一个。
4. **soft-landing 覆盖全生命周期状态**：无论 brainstorm / spec / plan / 部分完成 / 待审 / 通过 / 即席任务哪一档被打断，末尾 banner + 看板都要写清「在哪一档 + 怎么续」。
5. **需验证项进 cockpit `Pending Review`，写明「验证通过后该做什么」**，使恢复只依赖看板。
6. **红线固化为不可关内置**：可逆→自动 commit、外发/不可逆（push）→ 先问；**恢复载荷（cockpit + INDEX + 已落盘工件）零损失**（不含未落盘的对话推理）；preflight 纯读零写。
7. **国际化（i18n）原则**：flightdeck 发布面（skills / scaffolds / templates / README / banner 结构 / flow 名 / 字段标签）一律**英文**；用户 deck 内容用其工作语言，经 `rules.md` / `CLAUDE.md` + AI 自动适配——工具自身不为某语言定制。

## Part 1 — 可逆动作无门执行 + 统一「翻回」通道

### 可逆 / 不可逆判据（权威表在 protocol.md，单一真相源）

判据：**改动只落 deck 内文件 / git 本地、可被反向编辑或 git 本地回退 = 可逆**（自动执行，无门）；**外发 / 不可逆 = 先问**（红线）。

- 可逆示例（自动）：`status` flip、`--advance-candidates`（all-plans-done spec → done）、`incident → checklist` promotion、`done` 工件归档、应用 status 建议、stale 翻转、cockpit 段维护。
- 不可逆 / 外发示例（先问）：`git push`、对外发布 / 调外部服务。`git commit` 属可逆（本地），自动。

> **唯一真相源**：完整可逆/不可逆判据表落 `protocol.md`；本 spec + 各 skill **只指针引用，不各自再放一份枚举**（防两处漂移 + skill 作者换名重引门）。新动作按判据归类。
>
> **破坏用户手写内容的可逆编辑**（重写/大规模删 cockpit 手写笔记等）：git 上可逆，但**必在 banner 显式报告**（透明），不静默。

### 删除项（瘦 prompt / 热路径预算）

各 skill 里针对可逆动作的门删除或改写为「直接做 + 报告」：`landing` 的 `promotion is always user-gated` · `--advance-candidates → confirm-gated offer` · `Status … applied only on user confirm` · `retire prompt`；`status` SKILL 的 `applied only on user confirm`；其它 skill 的 `confirm before` / `ask you to … before proceeding`（`Hanging Tasks` 除外）。

### Hanging Tasks（窄定义，只阻塞 landing）

`Hanging Tasks` **不是 confirm 门**——它是**真有外部依赖 / 未完成阻塞**的安全停，**不是「想先问用户」**（防把删掉的确认门换名成 hanging task 偷回来）。作用域：**只阻塞 landing（退场仪式），不阻塞回合内的可逆动作**——有 hanging task 时，回合内可逆动作照样自动执行，只是不让干净退场。

### 统一「翻回」通道

- **触发**：用户自然话「翻回去 / 撤销 / undo / 还原上一步」。
- **撤销单元 = 最近一个「着陆单元」整体**：一次 `landing` / `checkpoint` 形成的 commit，或**本回合尚未提交的 deck 变更**。不是「文件级最近一次变更」，是**一个回合的 deck 改动作为整体**回退。
- **跨会话可恢复**：撤销目标**从 git + 看板推导**，不依赖对话内存——读 `git log -1 --oneline`：commit message 明确带 `landing:` / `checkpoint:` 标记 → 回退该单元；**未明确标记 / 跨多回合 / 歧义 → 让用户澄清目标（不强行自动）**。这条 fallback 使「关掉对话后再开新会话仍可翻回」确定可实现。
- **动作**：反向该单元的可逆变更（un-flip status / un-archive / `git` 本地回退 / 删刚 promote 的 checklist）。push 不在可撤范围（外发本就先问）。
- **不建撤销栈**：「最近着陆单元」由 git + 看板还原，无需持久化命令历史。
- **commit 级机制**（revert vs reset / 多 commit / 安全边界：拒绝撤不可逆操作）→ **plan 精化**。

## Part 2 — 统一流程输出格式 + 显式 soft-landing（替换 bootstrap 退场契约）

### 统一输出格式（所有 flightdeck 流程通用）

**每个流程回合的输出 = 先正文散文，最后一个标准化 banner + 关键信息。**

- banner **永远放最后**；**一个回合只出一个 banner**（杜绝重复 / 冲突的着陆标记）。
- **「回合」定义**：一次用户输入 → 一次完整 AI 响应（含其间多步内部动作）；末尾只出**一个聚合 banner**，不按原子动作逐个出。
- **banner 触发**：跑了某 flow 或做了实际工作的回合才出（`preflight`/`landing`/`soft landing`/`new`/`walkaround`/执行回合）；**纯对话 / 澄清问答**（没跑 flow、没改 deck）不出。「无增量」指**跑了 flow 但无新知识**的回合（仍出 banner），≠ 纯对话回合。
- **嵌套与聚合**：一回合内 flow 套 flow（如 landing 内触发 soft-landing）只出**最外层** flow 的 banner；内层产生的 `[Saved]`/`[Pending]` 信息**并入（union）外层 banner 对应字段**——「只出一个」= 汇总到一个，不丢内层增量。
- **失败态**：flow 崩溃 / 部分成功 / landing 失败**仍出 banner**，用 `[Failed]` 行写明失败点 + 已落盘到哪 + 怎么续；不允许失败就不报。

格式：

```
─── <icon> <flow> ───
<关键信息 / 恢复路径，逐行>
```

各 flow 各有 icon + flow 名：`preflight` 🛫 · `soft landing` 🛬 · `landing` 🛬 · `new` ✍️ · `walkaround` 🔎 …。flow 名 + 字段标签走结构英文（决策 7）；标签后内容用用户语言。

### banner 字段集（必填 / 可省 / 空值）

- **恒在**：`[Stage]`（恢复需要，见 Part 3）+ 末行「可随时关闭」可关信号。
- **按情况**：`[Saved]`（有知识落盘时）· `[No change]`（无新知识时）· `[Pending]`（**当且仅当 Pending Review 非空**——为空则**省略该字段**，不显示空 `[Pending]`）· `[Failed]`（失败态）。
- 各 flow（preflight / landing / new …）的**最小字段集 + 模板实例** → plan 给。preflight banner 至少 `[Next]`（item #1）+ 路由计数。

### soft-landing 触发

**执行回合**结束 → 出 soft-landing banner。**纯对话 / 澄清问答回合** → 不出（只读 flow 如 preflight/walkaround 仍出简短 banner；「回合」「触发」精确定义见上）。

### 现状 → 改动 delta（`skills/_shared/bootstrap.md` 的 On exit 段）

| 现 | 改 |
|---|---|
| 有知识 → 打印「已保存」标记 | 有知识 → soft-land，明细写进末尾 banner `[Saved]` |
| 纯状态 → **静默** checkpoint | 纯状态 → checkpoint，banner 一句话（不再静默） |
| 无增量 → **什么都不说** | 无增量 → banner `[No change]` 一句诚实的话（无新东西要存、看板已最新、可放心关；Pending Review 非空则带 `[Pending]`） |

> 「无增量也出一句」是对原「say nothing」的**蓄意翻转**，不违反「不过度宣称」：那句话不假装「已保存」，而是明说「没有要保存的、可放心关」。记忆 `dont-overclaim-in-public-docs` 随之更新。原散落「已保存」标记收编进统一 banner。

### soft-landing banner（具体实例）

```
─── 🛬 soft landing ───
[Stage]     <生命周期档，见 Part 3>
[Saved]     已保存：specs/ +1 <file>；cockpit Next 已更新。
[No change] 本回合无新知识沉淀，看板已最新。
[Pending]   ⚠ 另有 N 条待验证（N 动态计算）：<什么> → 已记入 cockpit Pending Review，写明「验证通过后：怎么 commit / 下一步」。
可随时关闭 / 切换对话——下次 preflight 从看板接手。
```

正文按增量择一/组合：`[Saved]` 与 `[No change]` 互斥（有无新知识二选一）；`[Pending]` 独立，按 Pending Review 是否非空决定出现。**既无新知识又有待验证** → `[No change]` + `[Pending]` 两行并列（不挤一行）。

### 与既有 soft-landing 机器的关系

三档 `checkpoint ⊂ soft-landing ⊂ full` 是**内部「做多少」的工作范围**（持久化 / 归档 / commit 的程度）；**banner 是对外输出，永远一个、可见**——二者正交：checkpoint 档的回合照样出一个可见 soft-landing banner，只是做的事少。复用 turn-end hook 焊接的 AUTO 区，不重造。

## Part 3 — 全生命周期恢复（被打断也能续）

工作可能停在任一档，且**都可能中途打断**——末尾 banner 的 `[Stage]` + 看板必须够下次 `preflight` 认出「在哪、怎么续」：

| # | 阶段 | 恢复锚点（看板写什么 → 下次怎么续） |
|---|---|---|
| 1 | 写头脑风暴 | 无 deck 工件；cockpit Active focus/Next 记「正在 brainstorm X、已问到哪、下一问」；**已定决策即时软着陆进 spec**（见下） |
| 2 | spec 已写 | spec(active) 在 In Progress；Next＝复核 spec → 写 plan |
| 3 | plan 已写 | plan(active) 在 In Progress；Next＝执行 plan 第 N 步 |
| 4 | plan 部分完成 | Next＝从「下一未完步」继续（plan 内进度自述）；已完成部分不回头 |
| 5 | plan 完成待审 | 进 Pending Review，写明「验证通过后：怎么 commit / 下一步」 |
| 6 | 审核通过 | 触发 landing：flip done、归档、commit |
| — | 即席任务（无 spec/plan） | cockpit Next 直述「正在做 X、已到哪」；可逆即做、按 Part 2 报告 |

### 阶段派生（确定性，避免漂移）

`[Stage]` 取值优先级：**plan status > spec status > cockpit Active focus 散文**（无工件的 brainstorm/即席阶段才落到散文）。同时存在 spec + plan 时以 plan 阶段为准。

### brainstorm 增量软着陆（化解档1「无工件」张力 + 降过度承诺）

档1 一旦产生**已拍板的决策**，即把该决策软着陆进 spec（哪怕 spec 仍在成形）——此刻阶段**自然推进到档2**（spec 已写），非矛盾，是档1→档2 的过渡。未落盘的在途探索（还没拍板的讨论）**不保证零损失**——「零损失」只覆盖恢复载荷（决策6），长 brainstorm 靠「边定边落」缩小丢失面。

### 两种恢复语境（不冲突）

- **preflight 恢复**：只读 cockpit + INDEX（恢复载荷），**不读 git、不读对话** → 保 preflight 纯读零写。
- **「翻回」撤销**：用户主动触发的独立动作（非 preflight），**可读 git log + 看板**反推着陆单元。
- 二者是不同操作，「恢复永远只读看板」专指前者。

### Pending Review 恢复完整性（档5 / 需验证）

`## Pending Review` 行格式：`- [<topic>] <做了什么 · 怎么验> → 验证通过后：<怎么 commit / 下一步>`。把「验证后动作」写进看板——关对话后下次 preflight 读这条即知「卡在等验证，验过后该 commit / 接着做什么」。沿用既有 drain 纪律（拍板或下次 landing 确认 → 删行；空 → `- (none)`）。topic 保持**简短单行**（drain 靠 AI 判断不靠 regex，不引入解析层）。

## 落点 / 爆炸半径（≈与上次同级或更大）

1. **注入 directive**：`skills/_shared/bootstrap.md`（On exit 段重写 = **最小运行时指针**，不重定义 banner 格式）。
2. **唯一真相源**：`skills/preflight/protocol.md` —— banner 格式规范 + 可逆/不可逆判据表的**单一家**；`exit-ritual.md` / 各 SKILL **引用不重定义**（防再次双重定义）。
3. **skills 散文**：`landing/SKILL.md`、`status/SKILL.md`（删确认门）、`preflight/SKILL.md`（preflight 走统一 banner 🛫）、`new`/`walkaround`/`emit-agents-md`（输出走统一 banner）。
4. **模板**：`skills/preflight/templates.md` + `scaffolds/full/flightdeck/cockpit.md`（Pending Review 行格式 + banner 说明）。
5. **测试**：见验证。
6. **外圈文档**：`README*.md` / `docs/architecture.md` / `docs/session-flow.md` / `TEST_PLAN.md` 校准措辞。
7. **知识归宿**：交互边界写进 `docs/descope-baseline.md` 或 `docs/session-flow.md`。

## 破坏性变更处置

退场行为变化（无增量也出 banner；全流程统一末尾 banner）+ 删确认门 = 行为破坏性变更，alpha 期允许；不可逆动作仍先问，安全面不降；无向后兼容垫片。

## 红线 / 不动项

**恢复载荷（cockpit + INDEX + 已落盘工件）零损失，不含未落盘对话推理** · `push`/外发先问保留 · `commit` 自动本地保留 · `preflight` 纯读零写 · `Hanging Tasks` 阻塞（窄定义，只挡退场）保留 · rules.md `version: 3.0` 戳不动。

## 已定 / 待定

- banner 标签语言 = 英文（已定，决策 7）；分隔线 `─── <icon> <flow> ───`（已定）。
- **graduate**（待定）：契约常驻家在 `bootstrap.md`/`protocol.md`/landing skill，倾向不 graduate（落地即归档）。

## 验证

- `uv run pytest scripts/tests/`。
- **测试场景（plan 落具体用例）**：删门回归（可逆动作不再先问）· banner 格式 + 一回合一个 · 跨会话「翻回」（模拟，含 untagged commit → 求澄清 fallback）· **landing 归档幂等**（--advance-candidates 自动推进后不二次归档）· 阶段派生优先级 · **Hanging Tasks 窄定义**（挡 landing、不挡回合内可逆）· Pending Review 非空 + `[No change]` banner 联动 · 嵌套 banner 取最外层 + 字段并入 · 失败态出 banner。
- `wc -m` 作 token 代理（**plan 记 baseline**），确认删门后热路径字符数下降；粗代理、仅方向性，不作硬判据。

## 评审纪要（外部 AI 评审 ds / claude / gpt，2026-06-16，两轮；原文留 tmp/）

评审者**不知项目现状**（用户声明仅供参考），技术过滤。红线检查三方均通过。

**第 1 轮**采纳要点已**回写正文**：回合/banner 触发定义（Part 2）· 字段标签英文化（决策7 + banner 实例）· 无增量遮蔽 Pending Review（banner `[No change]`/`[Pending]`）· 翻回=最近着陆单元（Part 1）· 可逆判据单一源 protocol.md（Part 1）· Hanging Tasks 窄定义只挡 landing（Part 1）· 阶段派生优先级（Part 3）· 零损失收窄（决策6 / 红线 / Part 3）· 单一输出源（落点2）· 归档幂等（验证）。
驳回：PR vs Hanging 谁阻塞（上一已 land 模型已定）· Pending Review 上 YAML 强解析（散文 + 判断 drain）· graduate 术语（既有）· wc -m 不精（已降级方向性参考）。

**第 2 轮**：
- **ds**：二次审核**判定可进实现**，10 问全闭环/降级；两条非阻塞残留 → plan：① 翻回跨会话 fallback（git log -1 未标记 → 求澄清，已写入 Part 1）；② `[No change]` 的 N 动态计算（已注 banner 实例）。
- **claude / gpt**（同一核心批评，**已采纳**）：第 1 轮采纳项只活在「评审纪要」、未回写正文，导致正文与纪要冲突。→ **本次重写已把全部规范回写 Part 1/2/3/决策/红线**，纪要降级为处置日志（不再承担规范职责）。
