---
status: done
summary: 验证由阻塞门降为非阻塞标记——复用 stale 外加可编程锚点字段 verify（有字段即欠验证、值=怎么验，随文件进 archive，preflight 扫 active+archive 确定性重建待验证清单，不依赖手写 cockpit 行）；知识件 stale+verify、工作流 done+verify 照常由 landing --archivable 完整归档、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
last_updated: 2026-06-10
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

**验证 = 非阻塞标记，不是落地门。** 安全性不靠「挡住落地」，靠「每次 preflight 把验证欠债浮出来」——**可见性 > 阻塞**，且可逆。（前提：preflight 是标准必经入口——这正是 flightdeck 的既有设计，「单一显式入口」。）

这条恰恰是 flightdeck 自己 3.0 的「**可逆=自动 / 外发=先问**」原则。needs-verify 门的理由（`exit-ritual.md:251`）写的就是「误判很便宜——`done` 只是一个 frontmatter 字段，用户能翻回来」；而归档进 `archive/` 同样可逆（`mv` 回来即可，文件没删）。既然「翻 done」可逆到可以自动，「归档」也可逆，那么「未验证就死锁在 active」反而自相矛盾。本 spec 消除这个矛盾。

**正面回应「改治理文案算不算放水」**（外部审核最尖锐的一条）：原门特意挡「改 `protocol.md` / `rules.md` / 脚本契约」这类，理由是「误判不易察觉」。本 spec 自己就属这类——但它的回应恰好堵死那个失效模式：`done + verify` **不是静默通过**，而是**每次 preflight 都从文件扫描浮出**，直到验证清除字段。原门防的是「悄悄错了没人发现」；新设计让它「错了也会被反复看见 + 可逆复活」。**可见性替代阻塞，针对的是同一个风险，且不再让未验证的活死锁看板。**（此处只放宽「自断 done 的标记」，不放宽 AI 去执行外发动作本身——见「不做」。）

## 设计

### A. 验证降为非阻塞标记（复用 stale + `verify` 锚点）— 解 ①③

**改 needs-verify 门**（`exit-ritual.md:244–251`）：AI **可以**自断 `done`，但对 needs-verify 的活打上「未验证」标记，而不是拒绝落地。

**「未验证」复用现有 `stale`，外加一个可编程锚点字段 `verify`——不新增主状态、不迁移**：

- **`verify` 字段语义**：**有该字段 = 欠验证**；**字段值 = 一行「怎么验」**（如 `verify: 相位4 各家 live 实证`），让欠债内容可被扫描器读到、cockpit 重建不丢说明；**无字段 = 已验证 / 无需验证**。`verify` 是 **status 的附加标记、不是独立状态机**（与 `note:` / `resolved_by:` / `when_to_update:` 同级），**须与 status 联读**——不是第四状态。
- `stale` 的 status token 不变（知识三态仍 `active / stale / obsolete`），含义拓宽为 **待复核：疑似过期 _或_ 新产出未验证**，两来源由 `verify` 字段区分（有 = 未验证，无 = `when_to_update` 命中的疑似过期）。
- **知识件（checklist / docs / incident）**：本会话新产出但没实证过 → `status: stale` + `verify: <怎么验>`，留在原文件夹、仍进 catalog/可路由，渲染 `⚠未验证`。
- **工作流件（specs / plans）**：状态集**仍是 `idea / active / done`**。substantively 完成即可 `done` + `verify: <怎么验>`，**`done` 本就不在 `## 进行中`（只投影 active）→ 看板即清空**；并照常由 **landing 的 `--archivable` 完整归档**（marker 随文件一起进 `archive/`，成为验证欠债的文件级真相源）。**完整归档的时机 = 调用 landing 时（end-of-turn `done`-flip 触发的 landing，或显式 `/flightdeck:landing`）或用户验证后**——不另设特例、最合流程；**恢复 = `mv` 回来，代价最小**（用户拍板）。

**验证完成/失败的处置**（per-kind，写进 `protocol.md`/`exit-ritual.md` 的明确 if-else，SKILL 先识别 artifact 类型再动作）：
- **验证通过**：删 `verify` 字段——知识件同时 `stale → active`；工作流件保持 `done`（随即满足 `--archivable`，归档）。
- **验证失败**：复活为 `active`（知识件/工作流件皆翻 `active`、`mv` 回原文件夹），**`verify` 字段保留**（重做 + 再验，验过才删）；无 `verify: failed` 取值——不给字段加状态机。多项并存逐条独立处理。

**判定行**（保持可审计）：
- needs-verify → `[判定: <理由>; 待验证: <怎么验>; done + verify]`
- no-verify → `[判定: <理由>; 无需验证; done]`（不变）

> 一个字段、两种载体：知识件留在文件夹（`stale` + `verify`），工作流件归档（`done` + `verify`）——但**都靠同一个 `verify` 字段被文件系统扫描重建**，健壮性一致（消除审核指出的「工作流欠债比知识脆」的不对称）。

### B. preflight 浮出「待验证」— 兑现「随时关不丢上下文」

**「待验证」清单是 `verify` 字段的确定性扫描结果，不是手写文本。** preflight（及 landing/walkaround）扫 **active 树 + `archive/`** 中所有带 `verify` 的工件 → 重建待验证清单（与现成「回归检测扫 `archive/incidents/`」同一套机械）。**语义上等价于全量扫描；实现可加索引/缓存（如 `flightdeck_index` 提供），只要结果等价。**

- 渲染走 3c **既有**的「待复核」浮出口（`skills/landing/SKILL.md:39`：落在 `## 下一步` 行内或 `## 待复核` 小节），读 `verify` 值显示 `⚠未验证: <file> — <怎么验>`，区别于过期类 `⚠待复核: <file>`。**cockpit 行 = 派生显示，源在文件 frontmatter**——用户编辑/裁剪/regen cockpit 都不会丢欠债（下次扫描照样重建）。
- **归档件仍被扫出是有意为之**：`archive/` 里的 `done + verify` 每次 preflight 都浮出，正是「非阻塞 + 持续可见」在起作用——验证清字段后即退出清单，不是 archive 语义的 bug。
- **验证失败 → 复活**：扫描已确定性定位到文件（`archive/<folder>/<file>`）→ `mv` 回原文件夹 + 翻 `active` + 保留 `verify`。

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

- `skills/preflight/exit-ritual.md` — needs-verify 门重写（A）；`verify` 锚点 + 扫描式待验证浮出（B）；验证通过/失败 per-kind if-else。
- `skills/preflight/protocol.md` — `done` 语义补「needs-verify 可自断为 done + verify」；`stale` 含义拓宽 + `verify` 字段语义（附加标记、与 status 联读、值=怎么验）；落「验证非阻塞」原则。
- `skills/preflight/templates.md` — frontmatter 模板加可选字段 `verify: <一行怎么验>`（适用知识件 stale 与工作流 done）；`stale` 定义文案（过期 _或_ 未验证，由 `verify` 区分）。
- `skills/preflight/SKILL.md` — catalog 阶段加 `verify` 扫描（active + archive）→ 待验证清单；输出瘦身（C）；docs 计数（D）。
- `skills/landing/SKILL.md` — 3a/3c 串起 `done + verify` 与扫描式浮出；`--archivable` 照常归档 `done`（含带 `verify` 的）；明确 soft-landing 不再被「要验证」挡住。
- `skills/status/SKILL.md` — `done` 翻转允许「+ verify」分支与判定行。
- `scripts/flightdeck_index.py`（+ `scripts/tests/`） — **确认要改**（已坐实）：`:136` 当前对任何 `status: stale` 无条件加 `⚠`、**不分原因** → 改为读 `verify` 渲染 `⚠未验证` vs `⚠待复核`；**新增 `--verify-pending` 子命令**（列出 active+archive 全部带 `verify` 的文件路径，喂 B 的清单 + 验收）；补对应测试。
- **首个适用对象** = cockpit 现存的 hook spec+plan：本 spec 落地后，它俩 `done + verify` + 由 landing 归档，`## 进行中` 清空，preflight 扫描浮出「⚠未验证: archive/…/hook-primary… — 相位4 各家 live 实证」。

## 不做 / 边界（YAGNI）

- **不**新增**主状态**（保 `idea/active/done`）。**唯一结构新增 = 可选字段 `verify`**（status 的附加标记、非独立状态机，与 `note:`/`resolved_by:` 同级）——为「文件级可重建、欠债不丢」付的最小代价，经审核采纳。
- **不**另造新的 cockpit 概念/section——验证欠债走 3c **既有**的「待复核」浮出（`## 下一步` 行内，或 3c 已允许的 `## 待复核` 小节），且只作**派生显示**，不发明新结构。
- **不**改 `stale` 的 status token、**不**触发 deck layout/结构迁移（仅拓宽含义 + 加一个可选字段；对存量 hook spec+plan 套用 = 普通状态操作，非批量迁移）。
- **不**给 `verify` 加审计字段（`verified_at` / 谁验证）：git log（删 `verify` 的那次 commit）即审计痕迹；历史日志是垃圾，不另存。
- **不**动「外发先问」：deploy / 开 PR / 发邮件 **该不该由 AI 去做**是另一层（不变）；本 spec 只放宽「做完后自断 done 的标记」，不放宽 AI 去执行外发动作本身。
- **不** eager-load docs 正文（仍按需）；**不**为「待验证」造老化/超期升级机器（离板 backlog ≠ 在板堆积；长了就是「去验证或删」的信号，沿用 idea 超 6 月删的同类处置）。

## 验收（可脚本验证，不靠「全新会话」手测）

- **看板清空**：hook spec+plan 标 `done + verify` 后，`## 进行中` 不再含这两件。
- **欠债 = 文件真相源（核心）**：`flightdeck_index.py --verify-pending` 列出 active+archive 全部带 `verify` 的文件路径；preflight「待验证」清单与该输出**逐行一致（忽略顺序）**。**手动删/改 cockpit 后重跑，清单仍一致**（证明源在文件、非 cockpit 文本；扫描语义为全量）。
- **退出队列闭环**：对某 `verify` 工件删字段后，`--verify-pending` 与下次 preflight 清单**不再含它**。
- **多项并存**：≥2 个带 `verify`（含跨 `specs/` 与 `archive/specs/`）时，清单逐条列全、互不吞并。
- **瘦身**：preflight 用户可见输出 = 计数 + 对账 + 待验证 + next item，无整张路由表刷屏。
- **知识件**：新写 checklist/doc 未实证 → `stale` + `verify`，渲染 `⚠未验证`（区别于 `when_to_update` 命中的 `⚠待复核`）；验证后删字段翻 `active`。

> **自指注脚**：本 spec 的实现本身就是「改了治理文案、需 resync 后新会话 live 实证」的典型 needs-verify 活——它会是自己这套「done + verify + 扫描浮出」设计的第一个用户。

## 评审纪要

两轮外部 AI 审核（`tmp/{ds,claude,gpt}.txt`，gitignored、advisory；审核方**不了解项目现状**，仅供参考）。R1 命中架构级缺陷（验证欠债无真相源）→ 引入 `verify` 锚点解决；R2 确认方向无误，余为完备性。

**采纳（已并入上文）**：`verify` 文件锚点（R1，三家命中，最关键）· `verify` 值=「怎么验」使欠债内容可重建（R2 claude3/gpt6）· 失败路径=复活 active、保留 verify（R2 claude2/ds1）· per-kind 删字段规则入 protocol（R2 ds1）· 验收改 `--verify-pending` 逐行一致 + 退出队列闭环（R2 claude4/ds3/gpt4）· stale 两义渲染区分（R1，坐实 `index.py:136`）· 「可见性替代阻塞」前提=preflight 必经（R2 gpt5）· 措辞「不新增主状态 / verify 是附加标记」（R2 gpt2/7）· archive 扫描语义补一句「等价全量、可缓存」（R2 gpt3）· 删 D 投机尾巴（R1 claude5）· 评审纪要精简（R2 claude1）。

**驳回（技术理由）**：拆两状态 / 弃 stale（verify 字段已分两义）· done(未验证) 非第四状态（字段非状态）· 瘦身降可发现性（误读，INDEX 仍读进上下文）· 阈值显示（用户已定计数）· 待验证老化机器（YAGNI）· 自指循环（非阻塞即设计目的，永挂=永久浮出非跳过）· 迁移矛盾（术语）· `verified_at`/审计字段（git log 即审计、历史日志是垃圾）· 新建 `.sh`（改用 `flightdeck_index.py` 子命令）。

**用户拍板（R2）**：不搞「留原地不归档」特例——`done + verify` 照常由 landing `--archivable` 完整归档（marker 随文件进 archive、待验证扫描含 archive），恢复 = `mv` 回来；最合流程、恢复代价最小。
