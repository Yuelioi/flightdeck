---
status: done
summary: 给 auto-land 补执行层——把唯一能在回合结尾安全自动化的 board-sync(cockpit ## 进行中 + INDEX 的 AUTO 区)从"靠 agent 自觉"转成脚本真执行(Stop hook 每回合结尾静默重生);判断性看板(## 下一步/Active focus/plan 指针)+知识分类+done 归档仍归 agent,靠 session-start 注入常驻强制令拉到很高的 best-effort,诚实不膨胀;why-no-hooks 核心前提对 gating hook 仍成立、对 session-start 注入失效,据此改写为采纳可移植注入+被动同步 hook、拒绝 gating hook
last_updated: 2026-06-07
related: specs/2026-06-06-end-of-turn-soft-landing.md
---

# auto-land 执行层：脚本静默焊死 board-sync + session-start 注入强提醒

> **Superseded by `specs/2026-06-07-hook-primary-refactor`**（done+archive）。本 spec 的有效产出（session-start 注入 + Stop board-sync）已 ship（commit `febdeea`/`08dac7c`）；hook-primary 把它泛化到四家并承继。保留作历史。

## 背景 / 要解决的问题

**症状（多项目实测）**：`soft-landing` / `checkpoint` **从不自动触发**。用户每次都得手动喊 `/flightdeck:landing`，体感"系统设计了自动落盘，但它从来不动"。这是 [[2026-06-06-end-of-turn-soft-landing]] live 复验的**负结果**。

**根因——没有执行者。** soft-landing/checkpoint、乃至 `done` 翻转后该自动跑的 full landing（exit-ritual 现有 signal 1：end-of-turn debounce），全靠 agent 在**每个回合结尾**主动回忆 signal 定义、正确分类、自己去跑。没有任何外部组件**执行**或**校验**。**指令 = 期望；期望 ≠ 执行**。技能链（brainstorming→…→finishing-a-development-branch）叠跑时，"回合结尾顺手落盘"这个最不显眼的约定第一个被牺牲。

**架构层面的必然。** `why-no-hooks.md` 诚实承认"没有任何东西自动触发——入场必须显式 `/flightdeck:preflight`"。这对**入场**成立；但 `exit-ritual.md` 把 soft-landing/checkpoint 写成**回合结尾自动触发**的机器，全自动驱动下回合结尾无人在场，于是入场**诚实**地要求手敲，出场**假装**会自动跑。这直接打在核心卖点（随时可关、preflight 干净接手、上下文不丢）上。

## 决策依据 —— superpowers 实证 + Claude hooks 实证 + 本仓库脚本实证

### superpowers 怎么做到近 100% 调用（读 `references/superpowers/`，2026-06-06）

`hooks/hooks.json`（Claude）/`hooks-cursor.json`（Cursor）跑 `hooks/session-start`，把 `using-superpowers/SKILL.md` 全文包成 `<EXTREMELY_IMPORTANT>` 注入每会话开场；无富 hook 的工具用指令文件兜（Gemini `GEMINI.md` `@`-include；Codex `AGENTS.md`）。README：*"Without [the bootstrap loaded at session start], the skills are dead weight — present on disk but never invoked"*。**结论 A**：连标杆也做不到纯靠约定让 agent 自觉读 skill——必须靠注入。**结论 B**：superpowers 的强制全在 **SessionStart = 入场**、**无任何 Stop hook**——它只解"入场/发现"，不解"回合结尾执行"，那是另一个问题。

### Claude hooks 能力（官方文档，`code.claude.com/docs/en/hooks`，2026-06）

- Stop hook 能 `{"decision":"block","reason":…}` 续命；`stop_hook_active` 字段存在。→ 这否掉了评审"Stop hook 无法阻止会话结束""字段不存在"的判断。
- **但**：本 spec **最终不使用 block**（见 ## 设计 Layer 2 的决策）——block 对归账既漏又矛盾，回合结尾能安全自动化的只有 board-sync。Stop hook 仅用于跑被动同步脚本（不门控、`exit 0`）。

### 本仓库脚本（已核实，非假设）

`flightdeck_index.py`（`scripts/`）已有接口：`<deck>` 重生全部 AUTO 区；`<deck> --check` = 报 INDEX AUTO 区 ↔ frontmatter 漂移、写零、stale 则 exit 1；`<deck> --archivable` = read-only 打印 archivable done 集。**本 spec 复用 `<deck>` regen，不新增脚本接口。**

## 核心切分 —— 哪部分能脚本执行，哪部分只能提醒（诚实底线）

| 动作 | 能否脚本确定性执行 | 谁来做 |
|---|---|---|
| **Board-sync**：cockpit `## 进行中` + 各 INDEX 的 `<!-- AUTO -->` 区 | ✅ 能（纯 frontmatter 派生、幂等） | **脚本**：Stop hook 每回合结尾静默重生 |
| **判断性看板**：`## 下一步` / `Active focus` / plan `## Progress current:` | ❌ 需判断 | **agent**（soft-land/checkpoint 时写） |
| **Knowledge-landing**：本回合写门知识的分类落盘 | ❌ 无文件信号 | **agent**（Layer 1 注入令 + Layer 3，best-effort） |
| **Full-landing 归账**：`done`-but-unlanded → archive+commit | 触发可检测，但有合法延迟情形（批量/等关联/用户说先别 land） | **agent**：下次 preflight 入口抓 + 常驻令催，**不在 Stop hook 强推** |

**本 spec 的诚实底线**：真·脚本执行的只有第一行（board-sync）。其余三行即使有 hook 也只能**强注入提醒**、拉到很高但非 100%。标题与目标据此不膨胀。

> **写门知识不是本 spec 的未定义概念**：判定标准是 `protocol.md § Write gate`（改变未来行为 / 影响决策 / 被反复引用；transient 副产物排除），exit-ritual 分类启发 (a)–(h) 已操作化。本 spec 沿用，不重新定义。

## 目标

1. **入场自动进入 preflight 接手模式**：进有 deck 的项目，开场注入 cockpit 锚点 + 强制"按 preflight 协议接手再动手"——不是 hook 替你执行 preflight skill，是让 agent 第 0 turn 就处于接手态、不需手敲。
2. **board-sync 真焊死**：cockpit `## 进行中` + INDEX AUTO 区永不漂移（脚本每回合结尾保证）——这正是 issue 里"checkpoint 最常被整个忘掉"那一档。
3. **判断/知识那半拉到很高且诚实**：靠常驻注入令 + 降负担，明确 best-effort、给可观测指标，不谎称"装上执行者"。
4. **保住可移植内容**：bootstrap 强制令单一真相源、全工具共享；触发胶水每工具一薄层。

## 非目标（YAGNI）

- **Stop hook 不 block、不归档、不刷判断性看板**——只跑静默 board-sync。归档（move+commit）副作用大、有合法延迟情形，blocking 又漏（放行即漏）又矛盾（等于自动触发 full landing），故不放进回合结尾 hook（评审 round-2 共识）。
- **不为 Knowledge-landing 设 hook 触发器**——无确定性信号；file-count 类启发式武断且 soft-land 不 commit 永不回落（round-1 三方命中，已弃）。
- **不给 Codex 造 gating**（只有非门控 `notify`）；**不引第三方依赖**；**不做并发锁**（单用户本地工具，YAGNI）。

## 设计 —— 三层，职责正交

```
Layer 1  session-start 注入（全工具·可移植基线）  → 入场接手 + 知识落盘强制令常驻
Layer 2  Stop hook（仅 Claude·被动同步）           → 每回合结尾静默重生 board AUTO 区（不 block）
Layer 3  skill 内容（全工具·无 hook 也生效）        → board AUTO 移出 agent 顾虑 + 改写 why-no-hooks
```

### Layer 1 —— session-start 注入

**机制**：照搬 superpowers 形状，每工具一薄层。Claude `hooks/hooks.json` 的 `SessionStart`（matcher `startup|clear|compact`）；Cursor `hooks-cursor.json` 的 `sessionStart`（superpowers 已 ship 此钩子为实证来源）；Gemini `GEMINI.md` `@`-include；Codex `AGENTS.md`。跨平台 wrapper **直接采用 superpowers 已验证的 `hooks/run-hook.cmd`**（near-verbatim：cmd/bash polyglot，处理 Windows Git-Bash 探测、无扩展名脚本、无 bash 时静默 `exit 0`——天然就是"hook 不可用即退回手动 preflight"的降级）。

**注入内容**：
- **静态强制令**（单一真相源 = `skills/_shared/bootstrap.md`，全工具共享一份）：`<EXTREMELY_IMPORTANT>` 短令——"本项目用 flightdeck。入场：按 `/flightdeck:preflight` 协议接手再动手。出场：回合结尾若产生写门知识，必须先 soft-land 再交还控制，不许答完就停。"
- **动态 cockpit 锚点**：脚本从 `flightdeck/cockpit.md` 抽 `Active focus` + `## 下一步` 注进去 —— 开场第 0 turn 见接手点。注入文案附一句"锚点可能滞后于上一回合，以 preflight 复核为准"（缓解陈旧锚点，见 ## 风险）。

**护栏（采纳评审）**：gate = "cwd 下 `flightdeck/` 目录存在"；`flightdeck/` 在但 `cockpit.md` 缺/损 → **仍注入静态令**（令其先 preflight/launch 重建），**只跳过动态锚点**；无 `flightdeck/` → 注入空、彻底闭嘴。

> **无竞态（澄清评审误解）**：soft-land 写的是 cockpit **文件**，preflight 与本注入**读文件、不读 git**（协议明文）。上一回合未 commit ≠ 内容过期。

### Layer 2 —— Stop hook（`hooks/stop`，被动同步、不门控）

```
1. cwd 无 flightdeck/ → exit 0
2. 跑 flightdeck_index.py <deck>  → 静默重生 ## 进行中 + INDEX 的 AUTO 区（幂等，写零差集时无变化）
3. exit 0（不 decision:block、不归档、不碰 ## 下一步/Active focus/plan 指针）
```

**为什么不 block**（round-2 评审共识）：block 唯一用途是"逼 agent 做事"，但唯一确定性可检测的归账欠账（`--archivable` 非空）若靠 block 续命，存在 ① **放行即漏**（第二次 `stop_hook_active=true` 必放行，工件照悬空——是"一次强制重试"非保证）；② 等于**自动触发 full landing**，与"full 手动/批量/等关联/用户说先别 land"冲突；③ 让 hook **承担业务语义判断**。故砍掉 block：done-but-unlanded 由**下次 preflight 入口**（现有）+ Layer 1 常驻令兜，不在回合结尾硬推。Stop hook 退化为纯被动同步，`stop_hook_active` 重入保护随之无需要。

### Layer 3 —— skill 内容

- **board AUTO 区移出 agent 的回合结尾顾虑**：脚本（Stop hook + index regen）已无条件保证 `## 进行中` / INDEX AUTO 区不漂，agent 回合结尾**不再需要操心这块的机械重生**。**但**（correctness，采纳 gpt）：checkpoint ≠ board-sync——checkpoint 还含刷 `## 下一步` + 推进 plan `current:`，**这俩需判断、仍归 agent**。所以 agent 回合结尾仍要：①（有 plan 推进时）刷判断性看板 ②"本回合有写门知识吗？有 → soft-land"。改写**不是**"agent 只剩二元问"——是把**机械 AUTO 区**从 agent 盘子里拿走、判断部分保留。
- **改写 `flightdeck/docs/why-no-hooks.md`**（措辞=核心前提部分失效、据此调整，**非**"正式推翻"）：其论据对 **gating/拦截类 hook**（跨工具无统一标准、纯兼容包袱）**仍成立**；对 **被动注入/同步类 hook** 被 superpowers 证伪（可做成每工具薄胶水+共享内容）。**抽象出新决策原则**（采纳 gpt）：*"被动注入/同步类 hook（无门控、胶水可移植）→ 接受；gating/拦截类 hook → 拒绝（或仅 Claude-only 增强且须 deterministic 触发）。"* 以后遇 Resume/Compact/PostToolUse 照此判，不再重吵。

## 可移植性 —— 诚实账（采纳评审）

可移植的是 **bootstrap 强制令内容**（单一真相源、全工具共享一份）。**触发胶水每工具一薄层**：Claude `SessionStart`+`Stop`、Cursor `sessionStart`、Gemini `@`-include、Codex `AGENTS.md`——约 5 个集成面，**用维护成本换可靠性，明确承认**，不粉饰成零成本。各工具效果分级（不夸"全工具同等受益"）：Claude = 入场注入 + board-sync 焊死（hook 实证）；Cursor = 入场注入（superpowers 实证 ship）；**Codex/Gemini = 仅指令文件注入，`AGENTS.md` 指令权重未实证、可能弱于系统消息 → 列入测试、不预设遵从率**。版本兼容：hook 机制随工具版本可能变；wrapper 无 bash 即静默 `exit 0`，失败降级 = 退回手动 preflight，不致命。

## 影响的文件（改动清单）

新增：`hooks/hooks.json`（`SessionStart` + `Stop`）、`hooks/hooks-cursor.json`（`sessionStart`）、`hooks/run-hook.cmd`（采用 superpowers 版）、`hooks/session-start`、`hooks/stop`、`skills/_shared/bootstrap.md`。

改动：各 manifest（`.claude-plugin`/`.codex-plugin`/`.cursor-plugin`/`gemini-extension.json`/`GEMINI.md`/`AGENTS.md`）指向 hooks / include bootstrap；`skills/preflight/exit-ritual.md`（board AUTO 移出 agent 顾虑、保留判断性看板与知识分类、删"自动发生"措辞）；`skills/preflight/protocol.md`、`skills/landing/SKILL.md`（同步）；`flightdeck/docs/why-no-hooks.md`（前提部分失效改写 + 新决策原则）；`flightdeck/docs/session-flow.md`（主干图纳入注入入场 + Stop board-sync）。

复用（不新增脚本接口）：`flightdeck_index.py <deck>`（静默 board-sync）。

测试（`tests/`）：① 有 `flightdeck/` 注入、无则静默、有目录缺/损 cockpit 仍注入静态令；② Stop hook 静默重生板面（含已 clean 时无变化）；③ 注入内容含 cockpit 锚点且 gate 正确；④ 无 bash 环境 wrapper 静默 `exit 0` 降级。

## 验收标准（采纳 gpt —— 把"焊死/很高"变可观测）

- **硬指标（board-sync）**：dogfood 连续 N 个工作回合后 `flightdeck_index.py flightdeck --check`（= INDEX AUTO ↔ frontmatter 一致性，写零）恒 `clean`、exit 0。
- **软指标（knowledge，承认非保证、非 pass/fail 闸）**：人工抽样产生写门知识的回合，观测 soft-land 触发率；判定靠人（写门知识定义见上，存在固有人工性，故是**观测指标非验收闸**）。漏判样例回流改 Layer 1 注入令措辞。
- N、抽样法、目标率取值 = plan 阶段定。

## 与 [[2026-06-06-end-of-turn-soft-landing]] 的关系

**接力，非取代。** soft-landing spec 定义 *what*（end-of-turn 落什么、三档语义、幂等）；本 spec 解决 *who executes it*（board-sync 脚本化 + 入场注入）。本 spec **修订**那篇一条非目标——原文"不做 harness 计时 hook、signal 3 是 AI 自调"，live 复验证明全自动下不可靠，故补执行层（但只补 board-sync 这一确定性半，知识半仍 AI 自调 + 注入催）。那篇**不标 superseded**（其 what 仍有效）；其落进 exit-ritual 的表述由本 spec Layer 3 一并改写，避免两套并存。

## 风险 / 取舍

- **知识/判断那半非保证**：明确接受。Stop hook 只焊 board-sync，其余靠常驻注入令 + 降负担，best-effort、有观测软指标，不过度承诺。
- **陈旧锚点**（采纳 gpt）：`## 下一步`/`Active focus` 由 agent 在 soft-land/checkpoint 写，若漏写则下个会话注入到陈旧值。鉴于锚点是开场最关键信息，缓解不止"一句话"：注入文案显式标"以 preflight 复核为准" + Layer 3 把判断性看板列为 agent 回合结尾必做项（非可选）。根治仍依赖 agent 落盘，记录在案。
- **Codex/Gemini 指令注入效果未实证**：见可移植性诚实账——列入测试、不预设遵从率、不夸"全工具同等"。
- **5 集成面维护成本 + 版本兼容**：已承认；wrapper 失败静默降级到手动 preflight。
- **每会话/每回合脚本开销**：注入抽两段 + 回合结尾一次幂等 regen，体量小；目录 gate 确保非 flightdeck 项目零开销。

## 评审纪要

外部 AI 评审两轮（原文存 `tmp/{claude,gpt,ds}.txt`，transient；用户提示"评审不了解项目现状，仅供参考"）。

**已查实并反驳**：
- DS 🔴"Stop hook 无法阻止会话结束" + "`stop_hook_active` 不存在"（round-1） → 官方 hooks 文档确证二者皆有。（本 spec 最终仍不用 block，但理由是设计取舍，非能力缺失。）
- "`--archivable` 未验证/可能不存在"（claude/ds round-2） → **已核实存在**（`flightdeck_index.py:365/542`，read-only）。
- "`--check` 行为未定义" → 已核实 = INDEX AUTO ↔ frontmatter 漂移检测、写零、stale exit 1，已写进验收。
- "写门知识未定义"（gpt/ds round-2） → reviewer 缺上下文：`protocol § Write gate` + exit-ritual (a)–(h) 已定义，本 spec 引用。
- claude#3 动态锚点"竞态" → 读文件不读 git，无竞态。
- Cursor `sessionStart` "未验证" → superpowers 实际 ship `hooks-cursor.json`，有实证来源（官方 Cursor 文档一致性留作实测）。

**采纳（改了设计）**：
- round-1：删 ≥5 file-count 启发式；改 `--archivable` 触发、修同步/检测顺序；诚实降调 + 拆动作；"自动进入 preflight 接手模式"；背景措辞；目录 gate + 缺 cockpit 兜底；可移植性诚实账；加验收；补风险；run-hook.cmd 规范。
- round-2：**砍掉 Stop hook 的 block**（放行即漏 + 自动触发 full-landing 矛盾 + 硬编码工作流 + hook 承担业务语义——ds🔴/gpt/ds🔵）→ Layer 2 缩成纯静默 board-sync；**board-sync ≠ checkpoint 的 correctness 修正**（gpt：判断性看板仍归 agent，不是"二元问"）；run-hook.cmd **采用 superpowers 已验证版**（claude#3/ds）；bootstrap.md 位置定 `skills/_shared/`；**抽象统一 hook 决策原则**写进 why-no-hooks（gpt）；Codex 效果分级 + 不夸全工具（ds📌）；陈旧锚点缓解加强（gpt）；版本兼容降级一句（ds📌）。

**push back / 留 plan**（用户拍板：锁定设计、剩余推进 plan）：并发锁 = YAGNI（单用户本地）；run-hook.cmd 逐字节、markdown 锚点解析规则、N/M/目标率取值 = plan/impl 级；"证明 done⇒必 land 工作流"被砍 block 后已无关。

**降调（用户拍板）**：why-no-hooks 从"正式推翻"降为"核心前提部分失效、据此调整"。
