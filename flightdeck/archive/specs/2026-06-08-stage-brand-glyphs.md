---
status: done
summary: 给 7 个 flightdeck 阶段各配一枚彩色 emoji 品牌图标（🛫preflight/🛬landing/🔍walkaround/✍️new/🔄status/🛠️launch/🌉emit-agents），加在各 skill 主报告/完成行；字形映射表落 skills/preflight/protocol.md 作文档级单一真相源；✈️ 留作整体 wordmark；scaffolds/模板/脚本/测试不动（横幅是模型 prose）
last_updated: 2026-06-10
---

# 每阶段品牌图标（彩色 emoji 套 + protocol.md 单一真相源）

## 背景 / 要解决的问题

flightdeck 的命名全是航空隐喻（cockpit / preflight / walkaround / landing），但**各阶段的用户可见输出没有视觉标识**——每个 ritual 跑完只有一行纯文字报告。用户希望每个阶段配一枚图标（"飞机起飞 = preflight 就绪、飞机着陆 = landing 已着陆"），让输出**更有品牌味**。

现状：只有 `launch` 的最终报告带一枚 `✈`（`skills/launch/SKILL.md:29`），是孤例、不成体系。目标是把它升级为**一套成体系、每命令一枚、风格一致**的品牌图标。

## 设计

### 1. 字形集（彩色 emoji，一命令一枚）

| 命令 | 图标 | codepoint | 语义 |
|---|---|---|---|
| launch | 🛠️ | U+1F6E0 FE0F | 造甲板 / 首次建机（**取代**现有的裸 `✈` = U+2708，无 FE0F） |
| preflight | 🛫 | U+1F6EB | 起飞前就绪 |
| walkaround | 🔍 | U+1F50D | 绕机巡检 / 审计 |
| new | ✍️ | U+270D FE0F | 新建工件 |
| status | 🔄 | U+1F504 | 状态流转 |
| landing | 🛬 | U+1F6EC | 着陆归档 |
| emit-agents-md | 🌉 | U+1F309 | 跨工具桥 |

设计取舍：飞行相位（launch/preflight/landing）用航空 emoji，工具类命令（walkaround/new/status/emit）用语义明确的功能 emoji——**功能可读性优先于强行航空化**。

**`✈️`（U+2708 + FE0F）保留作整体 wordmark**：README 标题 `# ✈️ flightdeck`（`README.md` / `README.zh.md`）已在用，是项目标志而非某命令的输出。launch 的旧字形其实是**裸 `✈`（U+2708，无 FE0F）**，与 wordmark 是不同码点序列；把它改 🛠️ 正是为了不让命令 glyph 和 wordmark 撞号。

### 2. 落点（各命令的主报告 / 完成行；**内容匹配串=权威锚点**，行号仅作定位提示）

只改**用户可见的主报告 / 完成行**，SKILL.md 的 H1 标题与正文示例不动。各命令"主报告行"的具体所指逐条列明（不是统一一种形态：有报告标题、有完成确认、有单句消息、有顶部横幅）：

| 命令 | 权威锚点（字面匹配串；行号仅提示，会漂移） | 改法 / 触点数 |
|---|---|---|
| preflight | `Preflight complete (read-only)`（散文收尾句 + Output format 块末行，约 :69 / :98） | 前缀 `🛫 `；2 处同串 |
| landing | Output format 块**顶部新增**横幅行 `🛬 已着陆`（该块当前无标题行——属**新增文本**）；soft-land 的 `「已保存」` marker（:21）→ `🛬 已保存` | 1 新增 + 1 加前缀；≤2 处 |
| walkaround | 报告标题 `=== /flightdeck:walkaround report ===`（findings 版 + clean 版各一，约 :190 / :210） | → `=== 🔍 /flightdeck:walkaround report ===`；`✅ Clean.` 不动；2 处同串 |
| status | 流转确认 print（`[判定: …; 无需验证; done]` / `[判定: …; 待验证: …; done + verify]`，约 :74 / :75；以及 active-flip 的确认 print） | 每条前缀 `🔄 `——这就是 status 的用户可见报告输出 |
| new | **新增**报告约定行 `✍️ 已建 <kind>: <path>`（new SKILL.md 当前仅 "It prints the created path"，**无报告横幅**） | 新增 1 行约定 |
| emit-agents-md | `AGENTS.md regenerated.`（:106，Output format 块首行） | → `🌉 AGENTS.md regenerated.` |
| launch | 裸 `✈ Deck created at`（U+2708，无 FE0F；:29 Final report 行） | `✈` → `🛠️` |

> 注 1（landing / new 的诚实标注）：landing 的 `🛬 已着陆` 与 new 的整行，都是**新增文本**而非"纯在现有行前加 emoji"——属轻微格式新增，已就此与用户对齐（new 顺带补上其当前缺失的输出指引）。
> 注 2（status 锚点）：`[判定: …; done]` 是 status 翻状态时打给用户看的**报告输出**（非 frontmatter 旁的审计注释），故是合法的"主报告行"。
> 注 3（new 的输出形态）：脚本 `flightdeck_new.py` 的 `created … at …` 是 Bash 工具结果（过程性 stdout，转瞬即逝）；给用户的**报告**由模型在脚本跑完后以**单行** `✍️ 已建 <kind>: <path>` 承载，不另复述脚本 stdout。用户看到的就是这一行带图标的确认（**非**"脚本一行 + 模型一行"并列）。

### 3. 单一真相源（**文档级**约定，防漂移靠人工同步）

7 个 skill 各自加载、无法互相 import，字形只能硬编码进各自输出模板。为给**未来新增命令**留据可循：在 `skills/preflight/protocol.md` 增一节 `## Brand glyphs (per command)`（**统一术语为"命令"**，不用 "stage"——7 个里 new / emit 严格说是工具而非会话阶段），放第 1 节那张**四列**映射表（命令名 + emoji + codepoint + 语义；**codepoint 入表**，便于消解 FE0F 歧义）。

**效力边界（诚实声明）**：protocol.md 是**被动的文档真相源**，不是程序强制约束——并非全部 7 个 skill 都显式 `read()` 它（new / status / emit 的 SKILL.md 无此指令）。若日后有人改了某命令的字形却忘了同步 protocol.md，**当前方案无机制自动报警**；一致性靠人工同步。（可选未来增强：写一个 tests/ 检查，逐 skill grep 期望字形并与 protocol.md 表交叉核对——本 spec **不含**此项，避开 scripts/tests 改动。）

### 4. 范围边界（明确不动的东西）

- **scaffolds/ 不动**——图标在 skill 运行时输出，不进任何 deck 文件；避开 `incidents/scaffold-ships-verbatim` 雷。
- **templates.md 不动**——同理，不涉及 deck 文件模板。
- **scripts/ + scripts/tests/ 不动**——横幅是**模型生成的 prose**，非脚本 stdout（含 new 的 "created at" 那行实为 `flightdeck_new.py` stdout，故 new 用新增的**模型 prose** 行承载图标，不碰脚本）。
- **非运行时输出示例一律不改**：`✈️` wordmark（README 标题）、`archive/` 历史件（`archive/plans/2026-06-04-…` 的旧 ✈）、以及任何历史设计稿 / 截图 / README 示例块——本 spec 只改 7 个命令的**实时报告行** + protocol.md 表。
- **SKILL.md H1 标题 / 正文示例不动**——只**修改或新增**主报告 / 完成行。

## 验证（needs-verify：逐枚人眼复核，done 时随 `verify` 字段携带）

1. 7 个命令的运行时报告行，**每个触点**都含且**仅含该命令对应的那一枚**字形——注意部分命令有 **≤2 个触点**（preflight 散文 + 块、walkaround findings + clean、status done + active-flip、landing 顶部横幅 + soft-land marker），每个触点都须带、且只带该枚。scope 限定到运行时报告行；整份 SKILL.md 别处出现 `✅` 等其他 emoji 属正常，不算违规。
2. protocol.md 的 `## Brand glyphs (per command)` 表与各命令实际用字**三列全一致**（命令名 + emoji + codepoint 都对得上，非仅比 emoji 字形）。
3. `git grep` 复核 scaffolds/ / templates.md / scripts/（含 tests/）**零改动**；并人工扫一遍 tests/ 的**部分匹配 / 正则**断言，确认无依赖横幅 prose（预扫结论：命中仅测试方法名如 `test_*_reports_drift`，非 prose 断言——风险极低但实施时复核一次）。
4. **人工验收项（非自动、一次性）**：在目标终端（Claude Code）目视一次，确认各 emoji（尤其带 FE0F 变体选择符的 🛠️ / ✍️）渲染正常。终端渲染依赖字体 / OS / 模拟器，本 spec 不保证任意终端，仅在目标终端确认。

## 外部评审处置纪要（tmp/{ds,claude,gpt}.txt；技术过滤、非盲从）

**采纳并已折入本稿**：① 锚点改内容匹配优先、行号降为提示（ds#3 / gpt）；② "仅横幅行"措辞精确化、逐命令明列形态（gpt / claude#1）；③ 单一真相源软化为**文档级**被动约定、显式声明无自动防漂移（ds#5 / gpt）；④ 验收三处返工——emoji 渲染=人工一次性项、tests 风险扩查后软化"已确认"措辞、"仅含该枚"限定运行时报告行（ds#6 #7 / claude#3 / gpt）；⑤ `✈️` wordmark 显式保留（gpt#K 衍生）；⑥ status 主报告行=流转确认 print 已澄清（claude#1）。

**驳回 / 更正**：ds#2 **事实错**——`skills/landing/SKILL.md:21` 确有 `「已保存」marker`，ds 凭空写成 "Soft landing complete / 已软着陆"，锚点不悬空；claude#1 **前提误读**——"判定行是 frontmatter 旁审计注释"不成立，它是 status 打给用户的报告输出（其"澄清主报告行"诉求合理，已纳入采纳⑥）。

**范围决定**：评审一致指 new 加图标略超"纯加图标"（无现成横幅、需新增约定）。用户拍板**全 7 枚**——new 以"+1 约定行"诚实实现，理由：契合用户"每个命令都要品牌图标"的意图，且顺带补 new 当前缺失的输出指引。

**二轮（gpt / claude 更新，均判"无阻断级"）**：进一步采纳——① 术语统一为"命令 glyph"（protocol 节名 `## Brand glyphs (per command)`）；② launch 实际字形核实为**裸 `✈`（U+2708，无 FE0F）**、与 README wordmark `✈️`（+FE0F）区分；③ 验证项 1 改为按**触点**计（部分命令 ≤2 触点）、验证项 2 改为**三列一致**；④ new 输出形态明确为**单行模型 prose**（注 3）；⑤ 范围边界泛化为"非运行时输出示例一律不改"；⑥ protocol.md 表含 codepoint 列。

## 后续

转 writing-plans 出实施计划：按 7 命令 + 1 处 protocol.md = 8 个落点拆任务，每枚字形改完即可独立目视。
