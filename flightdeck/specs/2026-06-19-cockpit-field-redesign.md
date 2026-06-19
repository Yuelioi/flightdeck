---
status: active
graduate: true
summary: 三个真实 3.0 cockpit 实测：叙述字段（Last updated 括号 / Active focus / Next）漏入工作记录（changelog / 目标判据 / 进度日志），每仪式加载 = 主 token 黑洞；In Progress 反而干净（长仅因 summary 长）。大改原则：cockpit=纯恢复载荷，每字段只能是廉价投影或指针大小判断，记录回各自的家（git/plan Progress/spec body/rules/INDEX）只留链接。落：Last updated 砍 changelog、Active focus 退一行标签+链接、Next 退单步+进度移 plan、summary 加上限+In Progress 截断、标准化薄 Pointers 行。
last_updated: 2026-06-19
---

# Cockpit 字段重设计：指针 vs 记录边界（叙述字段瘦身）

> 3.0 alpha 打磨。本 spec 由一轮 brainstorm + 三个真实 3.0 cockpit 实测推导而来。与 `2026-06-19-cockpit-accumulator-convergence.md` 是**同一条原则的两条轴**（那条治 Key Context/Pending Review 的*生命周期*，本条治叙述字段的*越界*），互补不重叠；两者 done 后可毕业进同一篇 docs 原则。

## 背景 / 动机

用户观察：cockpit 容易「一个内容写多遍」（一个 spec 进 In Progress → Next → Last updated），且 In Progress「就是从 specs 提取的，没必要」。

实测三个真实在跑的 3.0 cockpit（`nuxtblog` / `aep-parser` / `YHFish`）+ dogfood，得到的结论**和「In Progress 是浪费」的直觉相反**：

| 实测模式 | 证据 | 判断 |
|---|---|---|
| ① `Last updated` 括号 = changelog，无一例外 | 四个全是「这次干了啥」流水账；nuxtblog/aep 尤巨 | 和 commit message + Next + spec body 三重重复 → 砍 |
| ② `Active focus` 涨成一整段 | aep 整段（目标+判据+方法+不变量+链接）；nuxtblog 挂 3 RFC + 落地序 | 在抄 spec body → 退回一行标签+链接 |
| ③ `## Next` 变成项目日志 | aep ~35 行（两 arc、Phase ✅🔶⛔ 清单、依据列表）；nuxtblog 12 里程碑链接+现状+续接+横切 | 在抄 plan `## Progress` → 退回单步+plan 链接 |
| ④ `In Progress` 长，只因 spec summary 长 | aep 6 spec，每个 summary 4-6 行 | AUTO 机制无错，是 `summary` 太长（它同时喂 INDEX + In Progress，两处每会话加载） |
| ⑤ 人人手搓「指针/知识地图」节 | nuxtblog `指针`+`Context`；aep 段尾 `依据:`；YHFish `知识在哪` | 标准 section 未满足的复发需求 |
| ⑥ Key Context/Pending Review 在活跃项目里直接消失 | aep、nuxtblog 两个都没有；YHFish、dogfood 才有 | Active focus/Next 膨胀把它们的活儿抢了 |
| ⑦ 耐用不变量/基线塞进叙述字段 | aep「不变量:双版本 AE gate」；YHFish「已知预存失败」基线 | 是 rules / Key Context 的料，misfile → 交 accumulator spec 的毕业机制路由 |

**核心诊断：cockpit 没有强制的「指针 vs 记录」边界，工作记录（历史/进度/目标/判据）漏进每仪式加载的叙述字段（Last updated / Active focus / Next），这才是主 token 黑洞。** `In Progress` 是唯一干净的：廉价投影、免费维护（hook 焊死、零 AI token）、preflight 唯一活跃工作视图（正常路径不读 specs/INDEX，只读 cockpit 这份已过滤成 active 的廉价子集）——保留。模式⑥证明：把叙述字段管回指针大小，Key Context 自然归位。

## 北极星原则

> **cockpit = 纯恢复载荷。每个字段只能是两种之一：(a) 廉价投影（In Progress），或 (b) 压到指针大小的不可约判断（Next 单步 / Key Context 字面量 / Pending / Hanging）。记录住在各自的家——历史→git、进度→plan `## Progress`、目标判据方法→spec body、不变量→rules、知识→INDEX——cockpit 只放链接。**

## 决策（5 条，均按推荐）

### D1. `Last updated` 砍 changelog → 纯戳
退化成 `Updated: <日期> · <作者> · Stage: <lifecycle>` 一行；删括号叙述。历史 = `git log` + commit message + spec/plan body。**禁止**在此写「这次干了啥」的流水账（实证①）。

### D2. `Active focus` → 一行 `Focus` 标签 + 链接
`Focus: <一行线程标签，≤~100 字> → <当前 spec/plan 链接>`。目标 / 判据 / 方法 / 不变量**禁止入内**——它们住 spec body（不变量住 rules）。实证②的整段 aep Active focus 塌成一行 + spec 链接。

### D3. `## Next` → 单个下一步 + plan 链接，进度清单移去 plan `## Progress`
Next = 「下一个具体单步动作」+ 对应 plan 链接。Phase 进度清单（✅🔶⛔）、`依据:` 列表、里程碑归档链接**强制移去 plan 的 `## Progress`**（开 plan 才读，不每仪式加载）。实证③——最大一块瘦身。

### D4. `summary` 字段加长度上限 + In Progress 截断渲染
`summary`（喂 INDEX + In Progress，两处每会话加载）软上限 **≤ ~1-2 行 / ~200 字**：它是行描述、不是摘要论文。In Progress 的 AUTO 渲染取 `summary` **截断头部（≤~80 字）+ 链接**，完整 summary 留 spec frontmatter。实证④。
- 落地点细化（留 plan 定）：上限是「脚本截断渲染」还是「landing 密度门控提示作者收 summary」，二选一或并用；脚本只做确定性截断、不做判断。

### D5. 标准化薄 `Pointers` 行
实证⑤——三个项目都自发手搓「指针/知识地图」节，说明是**承重导航**的真需求。标准化一行（或一薄块）`Pointers:`：配置→rules.md · 约定→conventions · artifact→各 folder INDEX · 历史→archive。**薄**——只放跳转锚点，不放内容（内容在被指向的家）。模板 + scaffold 纳入。

## 提议的新 cockpit 形状（aep 怪兽塌缩示范）

```
# Cockpit — aep-parser
Updated: 2026-06-19 · claude · Stage: 执行中

Focus: Booyah Glitch 全工程复刻 → specs/2026-06-19-booyah-glitch-full-replication.md

Pointers: 配置→rules.md · 约定→conventions.md · artifact→specs|incidents|checklists/INDEX · 历史→archive/

## Next
Phase 1 Task 1.1：重建 clear_ae_crashstate 工具 → 清崩溃标志 → warm-retry verify
→ plans/2026-06-19-booyah-glitch-replication.md（Phase 进度在 plan ## Progress）

## In Progress   (AUTO·短行：标题 + ≤80字头 + 链接)
- booyah-glitch-full-replication — 整工程从零复刻作理解金标准 → spec
- technique-ontology — 三轴本体数据契约（冻结）→ spec
- …

## Key Context
- 不变量：每渲染类双版本 AE ship-gate（红线4）；能力真相源 capindex
- (其余进 rules / docs)

## Pending Review / Hanging Tasks
- (none)
```

35 行 Next + 整段 Active focus + changelog Last updated → ~12 行，信息零丢失（全在 plan/spec/git，cockpit 只指过去）。

## 落地面

- `skills/preflight/exit-ritual.md` —— **真相源**。§Cockpit update：重写各字段角色（D1 Last updated 纯戳 / D2 Focus 一行 / D3 Next 单步+进度移 plan / D5 Pointers 行）。§Length check 的逐字段密度门控扩展为「角色越界检查」：Last updated 含 changelog、Active focus 含目标判据、Next 含进度清单 → 非阻塞提示 + 门控 trim（把越界内容路由回家）。
- `skills/preflight/protocol.md` —— `## Key Context is the recovery slot` 那段所在的 cockpit 字段语义，补 Pointers 行定义 + 「指针 vs 记录」边界一句。
- `skills/preflight/templates.md` —— cockpit 模板：新字段顺序（Updated / Focus / Pointers / Next / In Progress / Key Context / Pending / Hanging）+ 各字段 Rules 注释（角色 + 软上限 + 越界禁令）；`summary` 字段长度上限文案（D4）。
- `skills/landing/SKILL.md` —— Step 8 引用上述（checklist 面，不重述）；Next 进度移 plan `## Progress` 的措辞。
- `skills/preflight/SKILL.md` —— preflight 报告侧若需提示「Next 含进度/Active focus 越界」，对应措辞。
- `scripts/flightdeck_index.py` —— In Progress AUTO 渲染加 summary 截断（D4，确定性截断，非判断）；若 Pointers 行纳入 AUTO 则一并（倾向**不** AUTO——Pointers 是 hand-maintained 导航，判断哪些值得指）。
- `scaffolds/full/flightdeck/cockpit.md` —— 新形状落 scaffold（新 deck 出场即新结构）。
- `skills/walkaround/SKILL.md` —— **新增 Audit 16：cockpit 字段结构 / 角色 conformance（确认纳入，非可选）**。现 15 个 audit 无一查字段结构——实测三个真实 cockpit 格式各异（自加 `指针`/`Context` 节、缺 Key Context、Active focus 段落化），walkaround **全没发现**，是确认的缺口。Audit 16 → flag 非标准 section / 缺标准 section / 字段角色越界（Last updated 含 changelog · Active focus 段落化 · Next 含进度日志）为非阻塞 INFO（只浮出、不修，守 walkaround invariant）。**依赖序：本 spec 的新格式（D1–D5 + 字段顺序）先定稿，Audit 16 才能有 conformance 基准，故落在字段重构之后。**

## 非目标（YAGNI）

- **不**删 `## In Progress`——它是廉价投影、preflight 唯一活跃视图，删了反而要加载完整 specs/+plans/ INDEX，更亏。
- **不**给 cockpit 加硬字符总预算 / 自动截断字段内容（违「上下文不丢」红线）；密度/越界检查只「提示 + 门控」，删动作要用户点头。
- **不**把 Pointers 行做成 AUTO/结构化——它是承重导航判断，hand-maintained。
- **不**改 `## In Progress` 的 AUTO 投影机制本身（只改渲染长度）。
- 与 accumulator spec 重叠的 Key Context/Pending Review *生命周期*（毕业/排空/逼问）**不在本 spec**——本 spec 只管字段*结构/角色边界*。

## 验证

- 用本 spec 把三个真实 cockpit（nuxtblog/aep/YHFish）+ dogfood 各过一遍重构：叙述字段越界内容路由回家（changelog→git、进度→plan Progress、目标判据→spec body、不变量→rules/Key Context），看 `wc -m cockpit.md` 净降幅（aep/nuxtblog 预期最大）。
- 新 scaffold 出场 cockpit 即新结构；新建 deck `/flightdeck:launch` 验证。
- `uv run pytest scripts/tests/`（In Progress 截断渲染 / Pointers 模板若落脚本则加测试；纯措辞改无脚本测试）。
- 归 3.0 alpha。

## 开放参数（留 plan/review 定）

- D4 落地：脚本截断渲染 vs landing 门控提示作者收 summary，二选一或并用。
- D5 Pointers：一行 inline vs 一薄块；纳不纳入 scaffold 默认（倾向纳入）。
- 字段顺序最终定稿（Updated / Focus / Pointers / Next / In Progress / Key Context / Pending / Hanging 是提议）。

（walkaround Audit 16 已从开放项升为确认落地，见落地面。）

## 沿革

- 源自一轮 brainstorm（cockpit「一个内容写多遍」+「In Progress 没必要」质疑 → 实测三个真实 3.0 cockpit）。用户拍板：兄弟 spec（与 accumulator 分轴）、大改、五条决策全按推荐。
- 与 `2026-06-19-cockpit-accumulator-convergence.md` 共享北极星原则（cockpit 只物化判断、记录回家只留指针），分治字段*生命周期* vs 字段*结构边界*。
