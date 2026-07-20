# Wayfinder 与 Flightdeck：职责边界与吸收建议

## 结论

Wayfinder 解决的是**目标明确但路径仍在迷雾中的大型决策工作**：它以 Issue Tracker
中的 Map 和 Decision Tickets 逐步发现路线，默认在“已经没有关键问题待决定”时结束，
并不负责把目的地完整实现出来。Flightdeck 解决的是**仓库内长期工作的连续性**：它要
让新会话恢复当前 Work、执行到当前 Slice，并保留完成实现所需的稳定上下文。

两者不是替代关系。Flightdeck 不应原样接入 Wayfinder 的 Map、Ticket、标签、指派和
关闭流程；那会在 `index.md`、`plan.md`、Slices 之外再制造一套状态权威。更合适的做法
是吸收它的**决策探索方法**，把 Wayfinding 作为复杂 Work 的可选前期阶段，仍由
Flightdeck 的 Work Root、Plan 和 Slice 承载。

Flightdeck 明确假定同一仓库同一时刻只有一个顶层 AI 会话。该会话可以协调子代理并行
研究或执行，但必须统一汇总 Work、Plan 和 Slice 状态；多个独立顶层会话的原子认领、
阻塞查询、共享 frontier 与合并协议不属于产品范围，也不通过 Issue Tracker 增补。

## 两套模型在解决什么

| 维度 | Wayfinder | Flightdeck |
| --- | --- | --- |
| 问题类型 | 大到单次会话装不下、路径尚不清晰的决策探索；终点可以是 spec、决定或原地变更 | 任意需要跨会话继续的仓库工作，包括规划和执行 |
| 顶层目标 | `Destination`：把“路线已经清楚”定义为完成 | Work `Goal`：定义目标本身完成 |
| 核心状态单元 | 一个 Map Issue，加一组以“问题”为正文的 Decision Tickets | 一个 Work Root，加可选 Plan 与可恢复的交付 Slice |
| 默认行为 | 计划而不实施；Task 也只为解除决策阻塞 | 持续推进 Goal；Slice 可以跨会话、跨提交执行 |
| 结束条件 | frontier、fog 中都不再有到达 Destination 前必须解决的问题 | Work Goal 与适用验收满足，或 Work 被明确停止 |
| 恢复入口 | 每会话先读低分辨率 Map，再选一个 frontier ticket 并按需 zoom | 先读 deck，再读 Focus Work 的 index/context/plan，按 Next 打开当前 Slice或材料 |
| 并发机制 | Tracker assignee 是 claim；原生 blocking 关系产生可查询 frontier | 一个顶层会话可协调子代理；不支持多个独立顶层会话，因此没有 claim、锁或依赖查询协议 |
| 产物位置 | Map/Tickets 在 Tracker；研究分支和 prototype 等资产从 Ticket 链接 | 支持的文档产物进入 owning Work；源码和外部系统产物留在自然位置并链接 |
| 上下文成本 | Map 每会话只加载一次；不预读所有 Ticket，按需查看 | deck 和 Work Root 小而固定；只沿 Next 最多加载三个恢复链接 |

Wayfinder 对自身边界说得很明确：Ticket 解决的是决定，而不是 build Slice；默认不执行
Destination，仅允许 Map Notes 显式覆盖这一默认值。参见
[Wayfinder：开篇与 Plan, don't do](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#plan-dont-do)。
Flightdeck 则把 Slice 定义为可交付、可验证且可跨会话或提交的执行单位，并明确 Plan
负责完成汇总。参见 [CONTEXT：Product language](../../CONTEXT.md#product-language)、
[ADR-0001](../adr/0001-slices-are-durable-work-units.md) 与
[ADR-0003](../adr/0003-plan-owns-slice-completion.md)。

## Wayfinder 的关键机制

### 1. Map 是索引，不是详情仓库

Map 只保留 Destination、Notes、Decisions so far、Not yet specified 和 Out of scope。
每个决定只在对应 Ticket 中保留完整答案；Map 仅写一行 gist 和链接。这与 Flightdeck
“Plan 是汇总、Slice 是局部详情”的分层非常接近。参见
[Wayfinder：The Map](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#the-map)
和 [ADR-0003](../adr/0003-plan-owns-slice-completion.md)。

### 2. Frontier 不是预先穷举出来的计划

Wayfinder 刻意允许地图不完整。只有问题已经能被精确表述时才创建 Ticket；尚不能精确
描述的在 `Not yet specified` 中保留为 fog，前置决定完成后再逐步“毕业”为新 Ticket。
这避免在缺乏事实时制造虚假的 30 步完整计划。参见
[Wayfinder：Fog of war](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#fog-of-war)。

### 3. Ticket 类型选择的是解决方法

Research、Prototype、Grilling 和 Task 不是四套生命周期，而是四种清除不确定性的办法；
其中 Research 是 AFK，Prototype 与 Grilling 必须让人实际参与，Task 只为解除一个决定的
阻塞。参见
[Wayfinder：Ticket Types](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#ticket-types)。

### 4. 并发能力依赖 Tracker

Ticket 必须先指派再开展工作，指派就是 claim；blocking 使用 Tracker 原生依赖；frontier
是“open + unblocked + unclaimed”的子 Issue 集合。Wayfinder 还允许研究 Ticket 由子代理
并行处理，并要求不同会话预期 Tracker 正在被并发修改。参见
[Wayfinder：Tickets](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#tickets)
和 [Wayfinder：Invocation](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#invocation)。

`agents/openai.yaml` 只声明显示信息并禁止隐式调用，没有补充持久状态或本地实现；所以
Wayfinder 的并发保证确实来自外部 Tracker，而不是 skill 自身。
参见 [Wayfinder agent policy](../../references/mattpocock-skills/skills/engineering/wayfinder/agents/openai.yaml)。

## 与 Flightdeck 的重叠

1. **低分辨率入口 + 按需放大。** Map 不加载所有 Ticket；Work Root 不加载所有 Slice。
2. **索引不复制详情。** Map gist 链 Ticket；Plan checklist 链 Slice。详情只有一个权威位置。
3. **名称优先于编号。** Wayfinder 强制在人类界面使用 Ticket 名称；Flightdeck 也应让 Plan
   项使用结果导向的可读标题，而不是只显示 `Slice 17`。
4. **当前边缘只有一个。** Wayfinder 每会话最多手工解决一个 Ticket；Flightdeck 的 index
   只应给出一个明确 Next 和当前执行指针。
5. **方法编排。** 两者都需要按问题调用 Research、Prototype、Grilling 等专业方法；
   Flightdeck 的 Work Output Contract 已经为受支持 skills 规定 owning Work。
   参见 [ADR-0011](../adr/0011-supported-skills-obey-the-work-output-contract.md)。
6. **控制上下文成本。** 两者都拒绝一次加载全部历史和材料；Flightdeck 进一步用 Next 中
   最多三个链接显式限定恢复载荷。参见
   [ADR-0008](../adr/0008-next-links-drive-immediate-recovery.md)。

## 不能直接合并的冲突

### 双重顶层状态

若同时保留 Wayfinder Map 和 Flightdeck Work，Destination 与 Goal、Decisions so far 与
context、open Tickets 与 Plan/Slices、当前 frontier 与 index Next 都会发生重叠。发生冲突
时没有稳定答案。因此，仓库内模式必须以 Work page 为恢复权威；这一点已由
[ADR-0005](../adr/0005-work-page-is-the-recovery-root.md) 明确。

### Decision Ticket 不是 Execution Slice

Wayfinder Ticket 以“问题”为核心，关闭表示已得到决定；Flightdeck Slice 以“Outcome”为
核心，完成表示已交付并验证。二者可以使用同一种页面容器，但不能把“决定已完成”误作
“实现已完成”。Plan 中必须明确区分探索阶段的 Decision Slice 和实施阶段的 Delivery
Slice，或者至少用标题表达其产出。

### 动态 frontier 与有序 checklist 的张力

Flightdeck Plan 是有序完成汇总；Wayfinder 则不预先创建仍在 fog 中的 Ticket。强迫复杂
决策一开始就拆成完整 Slices，会重新引入虚假计划。Plan 必须允许一个可选的
`Not yet specified` 区域，并允许随着决定推进增删未完成项，而不能把最初 checklist 当作
不可变合同。

### Tracker 并发语义不属于 Flightdeck

本地 Slice 中写 `Claimed by` 只是文字，不具备原子性；两个会话仍可能同时认领。Git
分支也不能提供实时 frontier 查询。Flightdeck 因此把多个独立顶层会话排除在支持范围外，
而不是用 Tracker、锁或兼容代码模拟 Wayfinder 的并发保证。一个顶层会话内部可以协调
子代理，但由它统一写回权威状态。当前 Flightdeck 的产品边界也明确它不是 workflow runtime。
参见 [CONTEXT：Product boundaries](../../CONTEXT.md#product-boundaries)。

### Git 自动化政策冲突

Wayfinder 会为研究 Ticket 建 throwaway branch；Flightdeck 明确 Git 操作服从项目政策，
不应由保存仪式自动触发。研究分支只能在项目规则和用户授权允许时创建，不能成为
Flightdeck 核心恢复协议。参见
[Wayfinder：Chart the map](../../references/mattpocock-skills/skills/engineering/wayfinder/SKILL.md#chart-the-map)
与 [CONTEXT：Product boundaries](../../CONTEXT.md#product-boundaries)。

## 建议吸收的方法

### 作为 Work 内的可选 Wayfinding 阶段

当 Goal 已能描述、但实施路线仍不清楚时，Flightdeck 可以让 `plan.md` 先包含一个
Wayfinding 阶段：

```md
## Wayfinding

- [x] [确定类型系统的唯一权威](slices/decide-type-authority.md)
- [ ] [确定迁移兼容边界](slices/decide-migration-boundary.md)

## Not yet specified

- 迁移边界明确后，再判断是否需要双写期以及如何验收。

## Delivery

- 尚未规划；Wayfinding 清晰后展开。
```

这里的 Decision Slice 仍遵循 Flightdeck Slice 的最小结构：Outcome 是要得到的决定，
Current 是已知事实与未决分歧，Next 是下一次 Research、Prototype 或 Grilling 动作。决定
完成后由 Plan checkbox 汇总；后续实施仍另建 Delivery Slice，不复用同一个完成标记。

### 吸收 fog、frontier 和 out-of-scope 思维

- 只创建当前能精确描述的问题，不为未知部分制造空 Slice。
- `Not yet specified` 作为 Plan 的可选动态区块，而不是一种文件或状态。
- 稳定的 scope boundary 写入 `context.md`；Plan 中只保留会影响当前路线的简短
  Out-of-scope 说明或链接，避免双份权威。
- 当一个决定暴露新问题时，先更新 Plan，再选择新的 index Next。

### 吸收 ticket type，但不要吸收标签系统

Research、Prototype、Grilling、Task 应成为 Slice `Next` 中自然语言表达的**下一方法**，
而不是 YAML、frontmatter 或固定 `type` 字段。例如：

```md
## Next

使用 grilling 与 domain-modeling 确认谁对迁移期兼容性拥有最终决定权。
```

对应输出继续服从 Work Output Contract：Work 局部研究进入 `references/`，局部术语和稳定
决定进入 `context.md`，执行进展留在 Slice；不能纳入 Work 的外部资产才链接。

### 吸收可读名称与一次一个决策

- Plan 链接必须用结果名称，不以编号代替含义。
- 一个 Decision Slice 只解决一个足以改变后续路线的问题。
- 默认一次会话只推进一个 Decision Slice；纯 Research 可以并行，但研究结论必须回写
  owning Work 后才算纳入恢复状态。

## 应明确拒绝的部分

- 不在 Flightdeck 内再创建 `wayfinder:map`、Map 文件或第二份 ticket tree。
- 不把 label、assignee、closed comment、blocking graph 镜像进 Markdown 字段。
- 不要求每个大型 Work 都先完整 Wayfinding；路线已经清晰时直接写 Delivery Plan。
- 不把所有 Slices 改成“问题”，也不把所有决定当成执行完成。
- 不自动创建研究分支、提交或 Tracker Issue。
- 不把 `Not yet specified` 误作必须填满的固定模板区块。

## 单顶层会话边界

Flightdeck 的支持模型是同一仓库同一时刻只有一个顶层 AI 会话：

1. **顶层会话是状态协调者：** Decision Slices 全部保存在 Work 内，由顶层会话维护唯一
   权威状态。
2. **子代理是内部执行单元：** 顶层会话可以让子代理并行研究、审查或修改互不冲突的
   范围，再由顶层会话汇总结论并更新 Work、Plan 和 Slice。
3. **独立顶层会话不受支持：** Flightdeck 不检测、不阻止，也不协调同时启动的其他会话；
   因此不提供 claim、锁、合并协议或兼容保证。

这个边界避免为了实际不存在的使用模式引入状态机和兼容代码，同时保留单个顶层会话
内部的并行执行能力。参见 [ADR-0025](../adr/0025-flightdeck-assumes-one-top-level-session.md)。

## 对当前设计的具体建议

1. 保留 Deck → Work Root → Plan → Slice 的单一层级，不引入 Map。
2. 扩展 Plan 约定：除有序 checklist 与 Acceptance 外，允许按需出现
   `Not yet specified`；它没有 checkbox，也不算 Slice。
3. 扩展 Slice 语义：Outcome 可以是“得到一个决定”或“交付一个实现”，但 Plan 标题必须
   让类型一眼可见，且决定与实现不能共用同一完成项。
4. 在 Flightdeck 的 specialist orchestration 中加入 `wayfinding` 方法：先定 Goal/范围，
   breadth-first 找到当前可表述的决策，再按 Research、Prototype 或 Grilling 推进。
5. 不吸收 Wayfinder 的 Tracker 状态机，也不为多个独立顶层会话增加并发兼容层；顶层会话
   可以协调子代理，但必须统一维护 Flightdeck 状态。

最终定位可以浓缩为一句话：**Wayfinder 告诉 Flightdeck 在还不知道完整计划时如何发现
下一条可决定的路；Flightdeck 负责把这些决定连同后续执行状态留在仓库里，让下一次会话
真正继续。**
