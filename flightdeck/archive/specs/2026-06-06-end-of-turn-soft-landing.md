---
status: done
summary: end-of-turn 若有知识增量,自动跑 landing 的知识+状态落盘子集并输出「已保存」标记,让用户随时可安全关闭对话、上下文不丢;soft-landing 不 commit、不归档(commit/归档/晋升闸都是 full landing 的尾巴),landing 幂等重跑只补差集
last_updated: 2026-06-07
---

# 会话结尾自动落盘（soft-landing）+「已保存」标记

## 背景 / 要解决的问题

**根本问题**:landing 里**真正易失**的两样——**会话新知识**和**cockpit 状态**——只活在会话上下文里,**一旦关掉/缓存失效就拿不回来**;而 git commit、归档到 `archive/` 是对**已落盘文件**的操作,关了会话也能追溯、不急。

**放大成本的诱因**:长会话(2h 执行任务)里,AI 干完活后若停下来等用户"批准 done"再 landing,用户往往已离开;回来时超过 prompt cache TTL(~5min),再确认/再 landing 要重读整个会话 = 浪费大量 token。(注:cache 失效本身只影响**成本**、不影响状态正确性;真正要防的是**未落盘的易失增量丢失**,成本是它的放大器。)

**现有 gap**(exit-ritual § Land-readiness "Deliberate gap (YAGNI)"):长会话埋头干、从不翻 `done`,**不会在会话内自动 landing**,只在下次 preflight 入口才提示。于是易失增量悬在会话里,用户也**不知道什么时候关对话是安全的**。

## 框架:三档同源(先交代,再展开细节)

checkpoint、soft-landing、full landing 是**同一个 landing 的不同触发时机与范围**,依次增强(checkpoint ⊂ soft-landing ⊂ full landing),不是三个独立仪式。按"本质"对齐:

| 档 | 本质 | 触发 | 范围 | commit / 归档 |
|---|---|---|---|---|
| **checkpoint** | 保存**状态** | plan-task 边界 / end-of-turn 仅状态增量 | 纯看板(`## 下一步` + plan `current:`),disk-only | 无 |
| **soft-landing**(本 spec) | 保存**状态 + 知识** | end-of-turn 且有**知识增量** | checkpoint + **知识分类落盘** + 变动 INDEX | **不 commit、不归档** |
| **full landing** | + **推进生命周期** | `done` / 显式 `/flightdeck:landing` | soft-landing + 归档 done + 晋升闸 | + 本地 commit + 归档 |

三档的**互斥去重**见 §1。关键分流:**状态增量 → checkpoint;知识增量 → soft-landing**(详见 §1 增量判据)。

## 核心切分:易失 vs 可追溯

| | 内容 | 紧迫性 | 处理 |
|---|---|---|---|
| **易失** | 会话新知识、cockpit 状态(`## 进行中`/`## 下一步`/`Active focus`)、plan 进度 | 缓存失效/关会话就拿不回 | **end-of-turn 必须自动落盘** |
| **可追溯** | git commit、归档到 `archive/` | 对已落盘文件操作,随时可补 | 留给 full landing,**非 soft-landing 动作** |

## 目标

1. **上下文不丢**:AI 在 end-of-turn 自动把易失增量(知识 + 状态)落盘,不依赖用户先翻 `done`。
2. **用户知道能关**:落盘后输出一个肉眼可见的「已保存」标记,给"现在关闭对话不会丢"的确定性。

## 非目标(YAGNI)

- 不引入第四个仪式 / 不新增自治开关——复用 landing,出厂默认开,可被 House Rule 降级。
- **soft-landing 不 commit、不归档**——两者都是可追溯尾巴,留给 full landing;落盘文件本身已保证不丢(preflight 读文件、不读 git)。
- 不强迫 AI 自评翻 `done`(保留"done = 用户拍板",纯做任务在安全阀内例外,见 §3)。
- 不做 harness 计时 hook,也不持久化 turn id watermark——signal 3 是 AI 自调,去重靠盘面自查(§1)。

## 设计

### 1. 触发 —— land-readiness 新增 signal 3

在现有两个 signal(signal 1 = 刚翻 done;signal 2 = preflight 入口 ≥5 改动)外新增:

> **signal 3 —— end-of-turn 落盘**:AI 即将把控制权交还给用户时,若本会话有**知识增量**,自动跑 §2 的 soft-landing 落盘子集。

**"end-of-turn" 是可判定事件,不是预测用户行为**:在 agent harness 里,一个 assistant turn 结束(AI 停止输出、把控制权交还)是确定的边界事件,与现有 `done → landing` 用的是**同一个触发点**——exit-ritual § Land-readiness 原文:landing "runs once before the AI returns control to the user — **end-of-turn, a decidable event, replacing the old unimplementable 'natural pause'**"。signal 3 与它同源。

**时序**:soft-landing 发生在 assistant turn 的**最后阶段**——先落盘,再把「已保存」标记作为本回合可见回复的收尾输出。即 **落盘 → 标记 → 结束回合**,不是先回复后落盘(钉死时序,防实现漂移)。

**增量分两类(决定走哪一档)**:
- **知识增量**(→ soft-landing):本会话产生**新的、尚未落盘的够写门知识条目**——写门 = `protocol § Write gate`(改变未来行为 / 影响决策 / 被反复引用;纯副产物如日志、调试、寒暄、grep 不算)。落地形态:incident 根因+影响+下次规避 / checklist when_to_read+检查项 / doc 一节解释 / spec 设计决策 / plan 步骤。
- **状态增量**(→ checkpoint,不触发 soft-landing):仅 cockpit 的 active set / `## 下一步` / `Active focus` 变化,或某 plan 进度推进(task 完成),**但无新知识**。这类只需 checkpoint 的看板落盘,跑知识分类是空操作——交给 checkpoint。
- 纯对话性内容("好的我来帮你"、解释、探索、读代码)不算任何增量 → 沉默。

**去重(无状态、靠盘面自查,不存 watermark)**:
- 同一 turn 内若已因 `done` 触发 full landing → **不再**额外跑 soft-landing(full 已含 soft 子集,一 turn 一条 landing 路径)。
- 本 turn 若已在某 plan-task 边界跑过 checkpoint,则**从该 checkpoint 跑完到 turn 结束之间**是否有新知识增量,决定 end-of-turn 要不要再 soft-landing:有 → soft-landing(顺带把看板补到最新);无 → 沉默(checkpoint 已落看板,无知识可分类)。"此后"= checkpoint 完成到 turn 结束这一段时间窗;若 checkpoint 恰在 turn 末尾跑、窗口为空,则退化条件成立 → 沉默。
- 为什么不存 `last_checkpoint_time` / turn-id watermark:**盘面本身就是 watermark**——"有没有未落盘的知识"= AI 在会话上下文里知道、但文件里还没有的结构化内容;已落盘的下次自查即 `already clean`,天然 no-op。无状态比时间戳更健壮(§6 同此机制)。

### 2. 动作 —— landing 的"易失落盘子集"

soft-landing = **full landing 去掉生命周期推进(归档 + commit + 晋升闸)** 后的易失落盘:

| landing 步骤 | soft-landing | 备注 |
|---|---|---|
| 分类落盘新知识 (Step 2) | ✅ | 易失,核心 |
| 重生成变动 INDEX (Step 3) | ✅ | 知识落盘附带 |
| 更新 cockpit 看板 (Step 4) | ✅ | 易失,核心(状态一并落) |
| status 推进 (Step 3a) | ✅ 见 §3 | 纯做的可翻 done(状态落盘);需验证的不翻 |
| 归档 done (Land Routine) | ❌ **不做** | 归档是可追溯尾巴、有副作用(文件被移走),全部留 full landing |
| 晋升闸 / recurrence sweep (Step 5a) | ❌ **跳过** | 需用户确认的晋升 prompt 不在用户不在场时弹,留 full landing |
| 本地 commit (Step 5) | ❌ **不做** | 落盘已保证不丢;commit 留 full landing 一次性做,避免碎 commit |
| 输出「已保存」标记 | ✅ | 见 §4 |

### 3. 需验证 vs 纯做 + 安全阀(AI 自己按性质判)

- **需你验证**(UI / 外发 / 观感):知识 + 状态照常落盘,但**不翻 done**——留给用户测完一句话拍板。
- **纯做、不需验证**且任务确实完成:AI **可直接翻 `done`**(这是状态落盘);但**归档仍留 full landing**——soft-landing 不归档。

**安全阀**(规则在前、例子在后,避免遗漏感):
- **通用规则**:凡"会被 AI 或脚本**机械执行、且误判不易察觉**"的改动,一律视为**需验证**(禁止自评 done)。
- **典型例子**(非穷举):任何外部系统变更(发 PR、部署、写数据库、发邮件…);治理 / 数据模型类改动(`protocol.md`、`rules.md`、`AGENTS.md`、frontmatter 字段、脚本契约)。
- AI 选择自评 done 时,**必须在回复里显式输出判定声明**:`[判定: <理由>; 无需验证; 自动 done]`——使判断可观察、可追责。
- 误判兜底:`done` 是 frontmatter 一字段,落盘后用户可直接改回;且 soft-landing 不 commit、不归档,误判连提交/移动都不产生,代价极低。

### 4.「已保存」标记

soft-landing 跑完,会话结尾输出:

```
──────────── 💾 上下文已保存 ────────────
知识 + 状态已落盘 · 现在关闭对话不会丢失
已落:<文件名,最多列 3 个;更多写「等 N 个文件」> · cockpit 已更新
下次 /flightdeck:preflight 干净接手
```

- 措辞刻意用"**已保存 / 已落盘**"而非"LANDED / 已归档 / 已完成"——soft-landing 不归档、不一定 done,避免与 `spec-lifecycle` 强调的 `done ≠ archived` 混淆。
- 第 3 行是一行**极简核对摘要**,文件名**最多 3 个**,超出写"等 N 个文件";不列 commit(soft-landing 不 commit)。
- **标记只在 soft-landing 实际触发(有知识增量)时打**。仅状态增量 → 走 checkpoint、静默(沿用现有 checkpoint 无标记);完全无增量 → 沉默。已知取舍:用户无法从"没看到标记"区分"本就无需落盘"与"AI 漏判",接受此歧义以换防噪音。

### 5. 默认面

- **出厂默认开**(符合 3.0"删开关、换好默认")。
- 可被一条 House Rule 降级,如 `landing: 结尾不自动落盘`——沿用现有 Rule resolution order,不新增开关机制。

### 6. landing 幂等:soft-landing 之后再 landing 只补差集

soft-landing 已把**易失部分**落盘,但**未 commit、未归档、未跑晋升闸**。之后用户显式 `/flightdeck:landing`(full)时,**不重跑完整流程,只补差集**。机制是**每步自查当前盘面状态**,而非记住"soft-land 过"的标志位(无状态 → 幂等 → 更健壮,与 §1 去重同一原理):

| full landing 步骤 | soft-landing 已做? | 重跑时 |
|---|---|---|
| 分类知识 / INDEX / cockpit (Step 2–4) | 是 | 自查 → `already clean` → no-op |
| 归档 done (Land Routine) | 否(不做) | 扫 `--archivable` 集,只归还没归的 |
| 晋升闸 / recurrence (Step 5a) | 否(跳过) | 此时才跑 |
| 本地 commit (Step 5) | 否(不做) | 工作树 dirty → 执行(soft-landing 故意留的尾巴) |

所以"soft 完再 landing"≈ 只剩 **commit + 归档 + 晋升闸**,不会重复落盘。

## 影响的文件(改动清单)

1. **`skills/preflight/exit-ritual.md`**(主战场):§ Land-readiness 加 signal 3(触发 + 知识/状态增量分流 + 时序 + 无状态去重);§ Checkpoint 旁澄清三档同源与互斥;新增「已保存」标记格式 + 沉默规则;§ Classification 旁挂自评 done 安全阀(规则→例子)。
2. **`skills/landing/SKILL.md`**:Modes(现 full vs checkpoint)补 soft-landing(end-of-turn 自动触发、不 commit、不归档)+ 标记输出。
3. **`skills/preflight/protocol.md`**:Lifecycle / 职责表 / Rule resolution order 各一句收口 signal 3 与 House Rule 降级项。
4. **`skills/status/SKILL.md`**:交代 signal 3 由 AI 在 end-of-turn 自调 emit;cockpit"实际变化"复用现有 status diff 逻辑,不重新发明。
5. **dogfood**:`flightdeck/docs/session-flow.md` 更新,主干图纳入 soft-landing +「已保存」标记。

> 注:`flightdeck_index.py --archivable` 是 Land Routine **现有接口**(已实现 + 有 test,protocol/landing/status/walkaround 已引用),本 spec **不新增**脚本接口,仅沿用。

## 风险 / 取舍

- **AI 自评 done(纯做)误判** → 安全阀(通用规则 + 判定声明)兜底;误判可改回,且 soft-landing 不 commit、不归档,代价极低。
- **end-of-turn 可判定性** → agent turn 边界,与现有 `done` end-of-turn debounce **同源**,非预测用户。
- **知识落盘绑回复末尾**("绑定过紧"质疑) → 工具写文件本就即时;soft-landing 只把"收尾 + 标记"对齐到 turn 边界(一 turn 一次),钉死时序避免抖动。
- **沉默歧义** / **纯状态增量无标记** → 已知取舍(用户选防噪音),记录在案。
- **cockpit 抖动**质疑 → 仅知识增量触发 soft-landing,纯状态走 checkpoint;`## 进行中` 是 AUTO 派生,无 active 变化不动。

## 评审纪要

外部 AI 评审两轮(原文存 `tmp/{claude,gpt,ds}.txt`,transient)。

**第一轮 disposition**:
- 采纳:写清 end-of-turn 可判定性 + 出处;自评 done 安全阀;易失增量可操作判据 + 简述写门;双触发去重;**soft-landing 不 commit**(用户拍板);标记**改名「已保存」**(用户拍板);摘要文件名上限 ≤3;消歧义;三档同源前置;`--archivable` 确定性归档。
- 拒绝/反驳:"end-of-turn 不可判定"(误解,同源);"多人协作 push 同步/自动 commit 污染"(本仓库 never push,且已改不 commit);"取消 checkpoint"(3.0 核心特性);"隐式后台不可观察"(标记+声明即可观察)。
- 已知取舍:无增量沉默(防噪音 > 歧义消除,用户拍板)。

**第二轮 disposition**:
- 采纳:**soft-landing 完全不归档**(ds①,归档是可追溯尾巴、有副作用);**触发锚定知识增量、状态增量归 checkpoint**(gpt B/ds③,清三档边界);**时序钉死**(gpt,落盘→标记→结束);安全阀语序改"规则→例子"+补 AGENTS.md(claude②);checkpoint 退化"此后"时间窗澄清(claude③);cockpit"实际变化"复用 status diff(ds②,plan 注记)。
- 反驳/澄清:`--archivable` 非本 spec 新增(claude①,已实现+有 test+多处引用);watermark(gpt A)用**无状态幂等(盘面即 watermark)**替代,不持久化 turn id;`⊂` 笔误(ds④ 自评可忽略)。
- 三家共识:可进入 plan 阶段(剩余为边界定义,非架构问题)。
