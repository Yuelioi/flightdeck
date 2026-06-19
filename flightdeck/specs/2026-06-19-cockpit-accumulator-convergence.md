---
status: active
graduate: true
summary: cockpit 两个非-AUTO accumulator（Key Context / Pending Review）堆积陈年内容，现有 drain 纪律+密度门控在却不真 drain（被动等签收/保守判断）。重构：Key Context 不再是永久住址而是中转暂存——耐用条目 landing 时毕业上迁到按类型选的永久家（rules.md / docs / agent 根指令文件，去 CLAUDE.md 写死），临时条目 referent 死即排空；Pending Review 保留显式签收但 landing 主动逼问老条目，停止静默堆积。
last_updated: 2026-06-19
---

# Cockpit accumulator 收敛：Key Context 中转暂存化 + Pending Review 老条目逼问

> 3.0 alpha 打磨。本 spec 由一轮 brainstorm 推导而来（见「沿革」），承接已 land 的 `cockpit-bloat-control v2`——v2 补了「出场密度检查」，本 spec 补「让 accumulator 真正收敛的 forcing function + Key Context 重新定性」。

## 背景 / 动机

cockpit 有两个非-AUTO、会累积的字段：`## Key Context` 和 `## Pending Review`（`exit-ritual.md` Accumulator-drain discipline 明指此二者）。用户观察：它们**堆积陈年内容**——「几百年前的 review 还挂着、Key Context 一堆过时的」。

诊断：**治理纪律已经全在**（Accumulator-drain discipline + cockpit-bloat-control v2 的密度门控），但 **drain 是被动的，没有 forcing function 逼它发生**：

- **Pending Review** 等的是「签收」信号——但它本是「AI 自主干的活挂这等你 veto」，**故意**赖着防你忘复核。用户从不显式说「这条 ok」，于是那个 drain 信号**永远等不到**，越堆越多。这是「安全」与「不堆积」的内在冲突，不是 bug。
- **Key Context** 的 drain 是判断活，且有「上下文不丢」红线压着，AI 倾向保守多留。

**关键洞察（本 spec 核心）：Key Context 不该是任何东西的永久住址，它是中转暂存区。** 本仓 dogfood 实测——当前 Key Context 里耐用的条目**几乎都是「别处该有的家」的重复指针**：

- 「de-scope 红线」自带「单一真相源 = `docs/descope-baseline.md`」——家已在 docs，cockpit 是副本。
- 「测试/度量 = `uv run pytest`」——常驻事实，该进 `rules.md` 或 agent 根指令文件。
- 「test_hooks 17 失败 = WSL 噪音」自带「见 incidents」——家在 incidents，cockpit 又是副本。

所以正解不是「原地保护耐用条目 + 按年龄逼问」（年龄对 Key Context 是**错触发**，会误杀该常驻的耐用原则），而是：**耐用的毕业上迁、临时的 referent 死即排空**——两条都跑完，Key Context 自然收敛到纯临时，无需 pin、无需原地保护。这正好复用 flightdeck 已有的 **graduate（毕业）** 机制（spec done → 毕业进 docs）。

## 决策

### A. Pending Review —— 保留显式签收 + landing 主动逼问老条目

landing（Step 8 / soft-landing 也跑）时，对**跨了 ≥1 个 landing 仍未签收**的 Pending Review 条目：单独拎出，逐条逼问「签收 / 留着 / 丢」。

- **不自动删**——安全语义不变（人来 veto/签收）。
- 只加「老条目强制摊到用户面前」这一个 forcing function，停止静默堆积。
- 复用现有「drains when reviewed」；新增的只是「老 = 必须本次摊出来问」。

### B. Key Context —— 中转暂存化，landing 两个自动出口

把 `## Key Context` 重新定性为**中转暂存区**：进来的条目只有两个出口，都在 landing 走。

- **B1 排空（近确定性，可自动）**：条目的 referent（指向的 spec / plan / incident）**本会话被 archive / graduate / done** → 死指针 → drop（或把仍活的细节挪进对应 specs）。landing 本就知道这次归档了谁，**反查「哪些 Key Context 指着它」是确定性操作**，不需要按年龄、不需要 AI 猜。referent 死=高确定 → 自动 drop，但在 landing 报告里列出（可翻回），不预问。
- **B2 毕业上迁（判断，与 spec 毕业同质）**：条目耐用、且不指向某个会死的件（standing 原则 / 约定 / 常驻事实）→ 移到「按类型选的永久家」（见 C），从 cockpit 删除。这是判断活，但与「spec done 毕业进 docs」是同一种判断，landing 已在做，**不新增机制**。

耐用原则因为不指向会死的件，天然不被 B1 碰到；B2 把它请出 cockpit。于是 Key Context 收敛到纯临时残留，下次 referent 一死即排空。

**取消**：`pin` 标记、「原地保护耐用条目」、「按年龄逼问/过期 Key Context」（年龄是错触发）。

### C. 毕业目标按类型选家 + 去 CLAUDE.md 写死（多-agent 红线）

B2 毕业去哪，按**条目类型**选——这也决定它下次怎样被看到：

| 耐用条目类型 | 毕业去 | 可见性 / 理由 |
|---|---|---|
| 行为红线 / 约定 | `rules.md` | preflight/landing **每仪式全文读** → 红线最响，且 agent 中立 |
| 设计依据 / 决策 | `docs/` | 按 `when_to_read` 路由，不占常驻预算；常常本就在 docs，删 cockpit 副本即可 |
| 常驻 meta（每会话都要看的项目级指令） | **agent 根指令文件** | Claude=`CLAUDE.md`、Gemini=`GEMINI.md`、其他=`AGENTS.md`（跨工具标准，已有 `emit-agents-md` 生成）。**绝不写死 CLAUDE.md** |

**多-agent 红线**：`CLAUDE.md` 和 `rules.md` 是「每会话常驻」预算，往里塞要克制——大多数耐用 Key Context 其实是「碰到才需要」的设计依据，归 `docs`。

**代码 review 发现的写死点**（须改成 agent 中立措辞，如「项目的 agent 指令文件（CLAUDE.md / AGENTS.md / GEMINI.md，按运行的 agent）」）：

- `skills/preflight/protocol.md:36` —— Override authority 行「**CLAUDE.md (project)** > deck rules > defaults」。
- `skills/preflight/templates.md:39` —— 「Authority: **CLAUDE.md** > deck `### Rules`… belong in **CLAUDE.md**」（两处）。
- `skills/preflight/templates.md:21` —— 「belong in **CLAUDE.md / AGENTS.md**」（已半中立，统一措辞）。

已查无问题、不动：`scripts/build_stamp.py:45-47`（AGENTS/GEMINI/CLAUDE 三文件对称处理）；`skills/emit-agents-md`（以 AGENTS.md 跨工具桥为准，无写死）。

## 落地面

- `skills/preflight/exit-ritual.md` —— **真相源**。§Cockpit update / Accumulator-drain discipline：Pending Review 加「老条目逼问」（A）；Key Context 重述为中转暂存 + 毕业(B2)/排空(B1) 双出口 + 家按类型表(C)。§Length check 的 Key Context 项随之调整（已毕业的不再算「膨胀滞留」）。§Key Context recovery slot 措辞补「中转、会毕业」。
- `skills/landing/SKILL.md` —— Step 8 引用上述（checklist 面，不重述真相）。
- `skills/preflight/protocol.md` —— 修 :36 Override authority 去 CLAUDE.md 写死。
- `skills/preflight/templates.md` —— 修 :21 / :39 去写死；cockpit Key Context Rules 注释补「毕业出口」。
- `skills/preflight/SKILL.md` —— 若 preflight 报告侧需提示「Key Context 有可毕业/可排空条目」，对应措辞（判断是否需要，避免噪音）。
- （可选 · 判断是否纳入）`skills/walkaround/SKILL.md` —— Audit：Key Context 条目 referent 已归档却仍滞留 → 非阻塞 INFO（现 Audit 14 查 stale/超长，补「死指针」一类）。避免 scope 膨胀，default 不做、由 plan 阶段定。

## 非目标（YAGNI）

- **不**给 Key Context 加结构化 `pin` 字段 / 脚本硬校验——毕业/排空是判断，留 AI 在 landing 判（脚本只算确定性事实；referent-death 检测借 landing 已有的「本会话归档集」，不新增脚本机制）。
- **不**自动删 Pending Review——A 只逼问，签收仍人来。
- **不**按年龄过期 Key Context——错触发，会误杀耐用原则。
- **不**碰 `## In Progress` AUTO / `## Next` / `Last updated` 机制。
- **不**新增 cockpit 硬字符总预算 / 自动截断（违「上下文不丢」红线）。
- 脚本多语言支持（py → +js，照顾未装 py/uv 的新手）是**独立议题**，另开 backlog，不在本 spec。

## 验证

- 用本 spec 把**当前** dogfood cockpit 过一遍：Key Context 5 条——耐用的毕业（de-scope→确认 docs 副本删、测试命令→rules）、referent 死的排空；Pending Review 5 条——逐条逼问签收/留/丢。看 cockpit 净收敛。
- `grep -rn "CLAUDE\.md" skills/` 确认改完后无残留写死（protocol/templates 三处）。
- `uv run pytest scripts/tests/`（纯措辞改无脚本测试；若 referent-death 检测落脚本辅助则补测试）。
- 归 3.0 alpha；`wc -m flightdeck/cockpit.md` 作 token 代理看净降。

## 开放参数（留实现/review 定）

- Pending Review「老」阈值：默认 **≥1 个 landing 跨越**就逼问（下个 landing 没签收即问）；是否放宽到 ≥N，review 定。
- B1 排空：默认 referent 死=高确定 → **自动 drop + landing 报告列出（可翻回）**，不预问；是否改「摊出来确认」，review 定。
- walkaround「死指针」Audit 是否纳入（落地面可选项）。

## 沿革

- 本 spec 源自一轮 brainstorm（cockpit accumulator 为何不收敛 → Key Context 该不该有手动清理 → 「耐用的为何不直接升上去」的洞察）。用户拍板方向：Key Context 中转化（耐用毕业 / 临时排空）+ Pending Review 选项 A（保留签收 + 逼问）+ 毕业目标家**不写死 CLAUDE.md**（多-agent）。
- 承接 `archive/specs/2026-06-16-cockpit-bloat-control.md`（v2 已 land）：v2 = 出场密度检查；本 spec = forcing function + Key Context 重新定性。两者互补、不重叠。
