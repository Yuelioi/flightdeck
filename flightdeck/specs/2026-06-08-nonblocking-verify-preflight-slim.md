---
status: active
summary: 验证由阻塞门降为非阻塞标记——复用 stale 外加一个可编程锚点字段 verify:pending（随文件进 archive、preflight 扫描确定性重建待验证清单，不依赖手写 cockpit 行）；知识件 stale+verify、工作流 done+verify 照常归档清看板、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
last_updated: 2026-06-08
---

# 验证降为非阻塞标记（复用 stale + verify 锚点）+ preflight 瘦身

## 背景 / 要解决的问题

`skills/preflight/exit-ritual.md:246` 的 **needs-verify 门**规定：soft-landing 只能给「纯执行、无需验证」的任务自动翻 `done`；凡是 AI/脚本机械执行、误判不易察觉的（开 PR、部署、改 `protocol.md`/`rules.md`、改 frontmatter/脚本契约……）→ **AI 不许自断 `done`**。

后果（本会话亲历）：`specs/2026-06-07-hook-primary-refactor.md` + 其 rollout plan 卡在「相位4 各家 live 实证」——而 live 实证本会话根本做不了（hook 只在 resync 后新会话触发）。于是两件永远 `active`，堆在 cockpit `## 进行中` 下不来。这直接产生四个问题：

1. **看板堆积一堆「待验证」**（用户：完全没必要，应直接归档）。
2. **docs 加载**：其他项目反映 preflight 没加载 docs；docs 是关键摘要，应进上下文（注：3.0 源码 `skills/preflight/SKILL.md:27` 其实已读 `docs/INDEX.md`，详见 D）。
3. **智能 landing 卡死**：一旦「要验证」就不肯软着陆 → 当次产出无法干净落地 → **违背核心亮点「随时关对话、下次 preflight 干净接手、上下文不丢」**。
4. **preflight 输出太啰嗦**：整张 when_to_read/用途表刷屏，用户只想要「docs N条 / checklist N条」计数。

## 核心原则（为什么这么改）

**验证 = 非阻塞标记，不是落地门。** 安全性不靠「挡住落地」，靠「每次 preflight 把验证欠债浮出来」——**可见性 > 阻塞**，且可逆。

这条恰恰是 flightdeck 自己 3.0 的「**可逆=自动 / 外发=先问**」原则。needs-verify 门的理由（`exit-ritual.md:251`）写的就是「误判很便宜——`done` 只是一个 frontmatter 字段，用户能翻回来」；而归档进 `archive/` 同样可逆（`mv` 回来即可，文件没删）。既然「翻 done」可逆到可以自动，「归档」也可逆，那么「未验证就死锁在 active」反而自相矛盾。本 spec 消除这个矛盾。

**正面回应「改治理文案算不算放水」**（外部审核最尖锐的一条）：原门特意挡「改 `protocol.md` / `rules.md` / 脚本契约」这类，理由是「误判不易察觉」。本 spec 自己就属这类——但它的回应恰好堵死那个失效模式：`done + verify:pending` **不是静默通过**，而是**每次 preflight 都从文件扫描浮出**，直到验证清除字段。原门防的是「悄悄错了没人发现」；新设计让它「错了也会被反复看见 + 可逆复活」。**可见性替代阻塞，针对的是同一个风险，且不再让未验证的活死锁看板。**（此处只放宽「自断 done 的标记」，不放宽 AI 去执行外发动作本身——见「不做」。）

## 设计

### A. 验证降为非阻塞标记（复用 stale + `verify` 锚点）— 解 ①③

**改 needs-verify 门**（`exit-ritual.md:244–251`）：AI **可以**自断 `done`，但对 needs-verify 的活打上「未验证」标记，而不是拒绝落地。

**「未验证」复用现有 `stale`，外加一个可编程锚点字段 `verify: pending`——不新增状态、不迁移**：

- `stale` 的 status token 不变（知识三态仍 `active / stale / obsolete`），含义拓宽为 **待复核：疑似过期 _或_ 新产出未验证**；两来源由 **`verify: pending` 字段**区分。`verify` 是**字段不是状态**，与现有 `note:` / `resolved_by:` / `when_to_update:` 同级。
- **知识件（checklist / docs / incident）**：本会话新产出但没实证过 → 落 `status: stale` + `verify: pending`（区别于 `stale` 单独 = `when_to_update` 命中的「疑似过期」），留在原文件夹、仍进 catalog/可路由，渲染 `⚠未验证`。验证通过 → **删 `verify` 字段并翻回 `active`**。
- **工作流件（specs / plans）**：状态集**仍是 `idea / active / done`**（不破 model-v4 三态）。substantively 完成即可 `done` + `verify: pending`，照常按 `--archivable` 归档、**清空 `## 进行中`**。关键：**`verify: pending` 字段随文件一起进 `archive/`**，成为验证欠债的**文件级真相源**（不再依赖手写 cockpit 行）。验证通过 → **删 `verify` 字段**（状态已是 `done`，无需再翻）。

**判定行**（保持可审计）：
- needs-verify → `[判定: <理由>; 待验证: <怎么验>; done + verify:pending]`
- no-verify → `[判定: <理由>; 无需验证; done]`（不变）

> 一个字段、两种载体：知识件留在文件夹（`stale` + `verify`），工作流件归档（`done` + `verify`）——但**都靠同一个 `verify: pending` 字段被文件系统扫描重建**，健壮性一致（消除审核指出的「工作流欠债比知识脆」的不对称）。

### B. preflight 浮出「待验证」— 兑现「随时关不丢上下文」

**「待验证」清单是 `verify: pending` 的确定性扫描结果，不是手写文本。** preflight（及 landing/walkaround）扫 **active 树 + `archive/`** 中所有带 `verify: pending` 的工件 → 重建待验证清单（与现成「回归检测扫 `archive/incidents/`」同一套机械）。

- 渲染走 3c **既有**的「待复核」浮出口（`skills/landing/SKILL.md:39`：落在 `## 下一步` 行内或 `## 待复核` 小节），按 `verify` 字段区分显示 `⚠未验证: <file> — <怎么验>` vs 过期类 `⚠待复核: <file>`。**cockpit 行 = 派生显示，源在文件 frontmatter**——用户编辑/裁剪/regen cockpit 都不会丢欠债（下次扫描照样重建）。
- preflight 在 catalog 阶段顺带这次扫描；读到清单 → 下次进场即接手验证。
- **验证失败 → 复活**：扫描已确定性定位到文件（`archive/<folder>/<file>`）→ `mv` 回原文件夹、知识件翻 `active`、工作流件视情翻 `active`、保留/更新 `verify`。多项并存逐条独立处理。复活的触发者与批量细节由 plan 补全。

### C. preflight 输出瘦身 — 解 ④

**把「读」和「展示」拆开**（`skills/preflight/SKILL.md:25–31` 的 catalog warm-up + 输出格式）：
- **照旧读** folder INDEX 进上下文（路由 priming 不变，避免 AI 进场不知有啥）；
- **但用户可见输出只给计数**：`docs N · checklist N · incident N`，**不再回显整张 when_to_read / 用途 / applies_to 表**；
- when_to_read 在**任务命中触发时按需再读**（exit-ritual 本就这么规定，execution-time 读单文件）。AI 路由能力不依赖这次回显——INDEX 已在上下文里。
- preflight 输出保留：cockpit 对账行 + git/version 一行注（step 4，已是非阻塞）+ **「待验证」清单**（来自 B）+ next item。

### D. docs 加载/展示拆分 — 解 ②

- docs **保持载入上下文**（3.0 `SKILL.md:27` 已读 `docs/INDEX.md` 顶层，满足「关键摘要应加载」），但**展示归 C 只给计数**（`docs N条`），逐条用途 / 正文按需读。
- 「其他项目说没加载」需具体 repro 才能核查（本仓库看不到那个 deck）——**本 spec 范围外**；3.0 源码侧 docs 加载已就绪（`SKILL.md:27`）。

## 影响的文件（粗粒度；逐文件改动留给 plan）

- `skills/preflight/exit-ritual.md` — needs-verify 门重写（A）；`verify: pending` 锚点 + 扫描式待验证浮出（B）。
- `skills/preflight/protocol.md` — `done` 语义补「needs-verify 可自断为 done + verify:pending」；`stale` 含义拓宽 + `verify` 字段语义（待复核两来源）；落「验证非阻塞」原则。
- `skills/preflight/templates.md` — frontmatter 模板加可选字段 `verify: pending`（适用知识件 stale 与工作流 done）；`stale` 定义文案（过期 _或_ 未验证，由 `verify` 区分）。
- `skills/preflight/SKILL.md` — catalog 阶段加 `verify: pending` 扫描（active + archive）→ 待验证清单；输出瘦身（C）；docs 计数（D）。
- `skills/landing/SKILL.md` — 3a/3c 串起 `done + verify:pending` 与扫描式浮出；明确 soft-landing 不再被「要验证」挡住。
- `skills/status/SKILL.md` — `done` 翻转允许「+ verify:pending」分支与判定行。
- `scripts/flightdeck_index.py`（+ `scripts/tests/`） — **确认要改**（已坐实）：`:136` 当前对任何 `status: stale` 无条件加 `⚠`、**不分原因** → 改为按 `verify` 字段渲染 `⚠未验证` vs `⚠待复核`；并新增/扩展 `verify: pending` 跨 active+archive 的扫描（喂 B 的清单）；补对应测试。
- **首个适用对象** = cockpit 现存的 hook spec+plan：本 spec 落地后，它俩 `done + verify:pending` + 归档，`## 进行中` 清空，preflight 扫描浮出「⚠未验证: archive/…/hook-primary… — 相位4 各家 live 实证」。

## 不做 / 边界（YAGNI）

- **不**新增工作流状态（保 `idea/active/done`）。**唯一结构新增 = 可选字段 `verify: pending`**（标记字段、非状态，与 `note:`/`resolved_by:` 同级）——为「文件级可重建、欠债不丢」付的最小代价，经审核采纳。
- **不**另造新的 cockpit 概念/section——验证欠债走 3c **既有**的「待复核」浮出（`## 下一步` 行内，或 3c 已允许的 `## 待复核` 小节），且只作**派生显示**，不发明新结构。
- **不**改 `stale` 的 status token、**不**触发 deck layout/结构迁移（仅拓宽含义 + 加一个可选字段；对存量 hook spec+plan 套用 = 普通状态操作，非批量迁移）。
- **不**动「外发先问」：deploy / 开 PR / 发邮件 **该不该由 AI 去做**是另一层（不变）；本 spec 只放宽「做完后自断 done 的标记」，不放宽 AI 去执行外发动作本身。
- **不** eager-load docs 正文（仍按需）。
- **不**为「待验证」造老化/超期升级机器（YAGNI）：离板 backlog ≠ 在板堆积；清单长了就是「去验证或删」的信号，沿用 idea 超 6 月删的同类处置。

## 验收

- **看板清空**：hook spec+plan 不必等相位4，即可 `done + verify:pending` + 归档，`## 进行中` 不再含这两件。
- **欠债可重建（核心）**：在**全新会话**（无前序上下文）跑 preflight，「待验证」清单条数 **=** 当前 active+archive 里 `verify: pending` 工件数；**手动删/改 cockpit 后重跑，清单仍一致**（证明源在文件、非 cockpit 文本）。
- **多项并存**：≥2 个 `verify: pending`（含跨 `specs/` 与 `archive/specs/`）时，清单逐条列全、互不吞并。
- **瘦身**：preflight 用户可见输出 = 计数 + 对账 + 待验证 + next item，无整张路由表刷屏。
- **知识件**：新写 checklist/doc 未实证 → `stale` + `verify:pending`，渲染 `⚠未验证`（区别于 `when_to_update` 命中的 `⚠待复核`）；验证后删字段翻 `active`。

> **自指注脚**：本 spec 的实现本身就是「改了治理文案、需 resync 后新会话 live 实证」的典型 needs-verify 活——它会是自己这套「done + verify:pending + 扫描浮出」设计的第一个用户。

## 评审纪要

三份外部 AI 审核（`tmp/{ds,claude,gpt}.txt`，gitignored、transient；审核方**不了解项目现状**，仅供参考）的逐条处置：

**ADOPT（已并入上文）**
- **工作流欠债加 `verify: pending` 锚点字段**（ds#2/#8、claude#3、gpt#2/#4 三家独立命中）：原「纯 cockpit 行」是派生视图、可丢；改为文件级字段、扫描重建。**最有价值的一条。** → A/B、影响文件、验收。
- **`stale` 两义（过期 vs 未验证）在渲染层区分**（gpt#1、claude#1、ds#1）：由 `verify` 字段区分。坐实：`flightdeck_index.py:136` 当前对任何 stale 无条件加 `⚠`、不分原因。→ A、影响文件。
- **正面回应「改治理文案 done(未验证)」张力**（claude#2，最尖锐）：核心原则补「可见性替代阻塞」段。
- **收紧验收**（gpt#5、claude#4、ds#7）：改可观测判据 + 多项并存，不靠单案例。
- **删 D 段投机尾巴**（claude#5）。
- **`flightdeck_index`/lint 兼容审计提为「确认要改」**（gpt#8、ds#4）。

**REJECT（技术反驳——审核方缺项目上下文）**
- 拆两状态 / 弃用 stale（gpt#1、ds#1）：`verify` 字段已在不加状态前提下分清两义。
- done(未验证) 是隐藏第四状态（gpt#3）：`verify` 是字段非状态，工作流仍三态。
- 瘦身降低可发现性 / AI 冷启动没路由（gpt#11、ds#6）：误读——folder INDEX **仍读进上下文**，只是不回显。
- 阈值显示（gpt#11）：用户已定「N条就行」。
- 待验证老化 / 超期升级（gpt#7）：YAGNI，离板 backlog ≠ 在板堆积。
- 自指循环 → 验证被跳过（ds#8）：误框，非阻塞是设计目的；永不验证 = 永久挂起且永久浮出，不是跳过。
- 不做迁移 vs 首个适用对象矛盾（ds#5）：术语混淆，「不做迁移」指无 layout 迁移，套用存量 = 普通状态操作。

**DEFER 到 plan**
- 复活机制细节（谁触发/批量——gpt#6）：`verify` 锚点已让定位确定，余下由 plan 补。
- 「docs 没加载」实链路调查（gpt#12）：需具体 repro，范围外。
