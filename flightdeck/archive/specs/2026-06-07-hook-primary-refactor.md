---
status: done
summary: 四家 hook 趋同后的大重构——给 Codex/Gemini 补真 hook、Cursor 补 stop（机制 A：每家一份小 config + 共享 session-start/stop/run-hook 脚本），四家吃满 SessionStart 注入 + Stop board-sync；删 why-no-hooks（理由已入 cross-host-hooks）；全 skill 文案以 hook 为主路径重写、删无-hook 双路径对冲与「仅 Claude 焊/Codex 退指令文件/未实证」措辞，保留知识分类归 agent + 一行环境降级地板；保行为紧致 protocol/templates/folder-semantics；收编 auto-land-executor + soft-landing + 2 rollout，取代部分标 superseded
last_updated: 2026-06-08
verify: 相位4 各家 live 实证（resync 后新会话）
supersedes: archive/specs/2026-06-06-auto-land-executor.md
---

# hook-primary 大重构：四家趋同后吃满真 hook + 全 skill 文案精简

## 背景 / 要解决的问题

`docs/cross-host-hooks.md`（2026-06-07 实读四家官方 hook 文档）确认：**Claude / Codex / Cursor / Gemini 四家已大幅趋同**——全部有 `SessionStart` 注入、`Stop`/回合结尾、`PreToolUse` 级拦截、JSON 配置（`event→matcher→handler`）、上下文注入。Codex 的 `hooks.json` 与 Claude **几乎同构**。

这推翻了 flightdeck 一系列基于「跨工具 hook 无统一标准、Codex 无富 hooks」旧前提的设计对冲：

1. **`docs/why-no-hooks.md` 的核心事实前提塌了**（Codex「无富 hooks/只 notify」是假的）。
2. **auto-land 执行层把 Codex/Gemini 限定为「仅指令文件注入、效果未实证」**——现在两家能跑真 hook，这层降级是多余的。
3. **当前 hook 接线只覆盖 Claude（`hooks.json` 全套）+ Cursor（`hooks-cursor.json` 仅 `sessionStart`，连 `stop` 都没接）**——Cursor 不得 board-sync，Codex/Gemini 完全没 hook 文件。
4. **全 skill 文案里散布大量「无 hook 宿主退指令文件 / 只有 Claude 焊死 / 效果未实证 / agent 得自己记着因为没人触发」的双路径对冲**——趋同后这些是纯 token 负担与认知噪音。

**一句话**：内容层（共享 skills + bootstrap）一直是对的，但**触发层与叙事层还停在「只有 Claude 真焊、其余兜底」的旧世界**。本 spec 把 hook 升为四家一致的**主路径**，并据此把全 skill 文案精简到「hook 为主、一行地板兜底」。

## 决策依据

- 事实底座 = `docs/cross-host-hooks.md`（四家能力对照 + 取用方案），本 spec 不重复论证，直接取用其结论。
- 沿用其**二分决策原则**：被动注入/同步类 hook（无门控、失败即静默降级）→ 采纳并四家拉满；gating/拦截类 hook（block 逼办事）→ **仍拒**，理由是**内生的**，与 hook 可用性无关，趋同不动摇它：**why 漏**＝二次 `stop_hook_active`/`loop_limit` 必放行 → 工件照悬空（一次强制重试非保证）；**why 矛盾**＝block 续命等于自动触发 full landing，与「手动/批量/等关联/用户说先别 land」冲突，且让 hook 承担业务语义。详 `cross-host-hooks.md` 关键发现 3 + auto-land spec round-2 纪要。

## 目标

1. **四家吃满被动 hook**：`SessionStart`/`sessionStart` 注入 bootstrap + cockpit 锚点；`Stop`/`stop` 静默 board-sync。Cursor 补 `stop`，Codex/Gemini 新增真 hook 接线。
2. **触发脚本单一真相源、四家共享**：`run-hook.cmd` + `session-start` + `stop` 一套脚本服务四家，每家只一份薄 config 指过去。
3. **全 skill 文案降到 hook-primary**：删无-hook 双路径对冲、「仅 Claude 焊 / Codex 退指令文件 / 效果未实证」措辞；叙事收敛成「hook 为主路径、四家一致」。删 `why-no-hooks.md`。
4. **保留诚实底线**：知识分类 + `## 下一步`/`Active focus` 判断仍归 agent（内生、hook 改不了）；**一行**环境降级地板（hook 没触发 → 手动 `/flightdeck:preflight`）保留，但不再写大段。
5. **保行为紧致非-hook 文档**：protocol/templates/folder-semantics 等只压字数、不动数据模型/status 语义/frontmatter 契约。
6. **收编在飞 spec**：本 spec 成为 hook 这条线唯一现行 spec，取代部分明标 superseded。

## 非目标（YAGNI）

- **不引 gating/拦截**（不启用 `PreToolUse` deny、不启用 `Stop decision:block` 逼 landing）——内生理由不变，趋同不构成重启它的依据。
- **不为省 ~10 行把 Claude+Codex 耦进一份 config**（Approach B 否决）——两家随版本漂移即静默失效，违背「不留兼容死结」。
- **不做 config 生成器 / 构建步**（Approach C 否决）——4 个 ~10 行静态文件，YAGNI。
- **不趁机改数据模型 / status 语义 / 文件夹分类**——非-hook 文档只做保行为紧致。
- **不引第三方依赖、不做并发锁**（单用户本地工具，沿用 auto-land 结论）。

## 设计

### 机制层（Approach A —— 每家一份小 config + 共享脚本）

**共享可执行体（不变，仅扩展分支）**：`hooks/run-hook.cmd`（polyglot wrapper，无 bash 即静默 `exit 0`）、`hooks/session-start`、`hooks/stop`。

**每家一份薄 config（指向同一套脚本）**：

| 宿主 | config 文件 | SessionStart 注入 | Stop board-sync | 现状 → 目标 |
|---|---|---|---|---|
| Claude Code | `hooks/hooks.json` | ✅ 已有 | ✅ 已有 | 不变 |
| Cursor | `hooks/hooks-cursor.json` | ✅ 已有 | ❌ 缺 → **补 `stop`** | 补 stop |
| Codex | `.codex-plugin/plugin.json` 的 `hooks` 键（可引 `./hooks/hooks.json`，与 Claude 同构） | ✅ `SessionStart` 新增 | ✅ `Stop` 新增 | 全新 |
| Gemini CLI | `.gemini/settings.json` 的 `hooks` 块（event→matcher→hooks[]） | ✅ `SessionStart` 新增（注入字段见 ↓ 残留未知） | ✅ `AfterAgent` 新增 | 全新 |

**四家 hook 事实（2026-06-07 live 核实，替换原「以 live 文档为准」留白）**：

| 宿主 | 入场事件 | 注入字段（stdout JSON） | 回合结尾事件 | project-dir 信号 |
|---|---|---|---|---|
| Claude | `SessionStart` | `hookSpecificOutput.additionalContext` | `Stop` | stdin `cwd` |
| Codex | `SessionStart` | `hookSpecificOutput.additionalContext`（同 Claude） | `Stop` | stdin `cwd` |
| Cursor | `sessionStart` | `additional_context` | `stop` | stdin `workspace_roots[]` |
| Gemini | `SessionStart` | `hookSpecificOutput.additionalContext`（**同 Claude/Codex**） | `AfterAgent`（"once per turn after final response"） | stdin `cwd` + env `GEMINI_PROJECT_DIR` |

> **残留未知已消解**（2026-06-07 核 `geminicli.com/docs/hooks/reference/` + 镜像的 `google-gemini/gemini-cli` repo，并经 Google Developers Blog 佐证）：Gemini SessionStart 注入字段 = `hookSpecificOutput.additionalContext`，**与 Claude/Codex 字面同形**。即四家中 **3 家（Claude/Codex/Gemini）注入字段完全相同**，仅 Cursor 用 `additional_context`。`GEMINI.md` `@`-include 不再是"字段未知的兜底"，回归通用的"hook 未触发"降级地板（见 bootstrap 优先级）。
> **来源锚点诚实账**（采纳 gpt）：四家 hook 机制随版本演进、本表无 commit/version 锚——动 hook 前以各家 live 文档复核，本表是 2026-06-07 快照。

> **Cursor 注入改用规则文件为主路径（架构决策，采纳用户 + claude-mem 实证）**：claude-mem 实测 Cursor `sessionStart` 注入不可靠（`references/claude-mem/cursor-hooks/CONTEXT-INJECTION.md`），改用 **`.cursor/rules/flightdeck-context.mdc`（frontmatter `alwaysApply: true`）**——Cursor 每次对话稳定加载 alwaysApply 规则。**原则：稳定加载 > 优雅加载。** 故 flightdeck 的 **Cursor 主注入路径 = hook 在 `sessionStart` + `stop` 写/刷新该规则文件**（内容 = bootstrap + cockpit 锚点），**独立成立、不依赖 sessionStart additionalContext**（后者至多 belt-and-suspenders）。该规则文件是 cockpit/bootstrap 的派生投影 → **gitignore**（不进 git，避免与单一真相源重复）。

**脚本泛化（4 家）**：
- **project-dir 解析（明确优先级，杜绝误判到上级目录）**：按宿主取**单一**信号——Claude/Codex = stdin `cwd`；Cursor = stdin `workspace_roots[0]`（多 root 取第一个）；Gemini = env `GEMINI_PROJECT_DIR`；**全部以 `$PWD` 为最后兜底**。解析得 `D` 后**只认 `D/flightdeck/` 是否存在**，存在才动、否则静默 `exit 0`——**绝不向上级目录回溯**（杜绝 gpt 指出的误判）。
- **`session-start` 的 `emit()`**：按上表四家分支输出对应字段（Claude/Codex 同形）；Gemini 分支在注入字段确认前 emit 留空、走 `GEMINI.md` 地板。
- **`stop` / `AfterAgent`**：project-dir 解析泛化后四家通用，逻辑不变（跑 `flightdeck_index.py <deck>` 静默重生 AUTO 区、`exit 0`、不门控）。
- **可观测性（采纳 gpt/ds——首次接 Codex/Gemini 的静默失败盲区）**：加 `FLIGHTDECK_HOOK_DEBUG=1` 一次性诊断开关——置位时 hook 把「解析到的 project-dir / gate 结果 / 是否跑了 regen / 降级原因」写 stderr（或 `flightdeck/.hooklog`）；默认全静默不变。让首次接入"hook 到底有没有触发"可证，不与正常降级混淆。

**各家 manifest** 指向 hooks / 加载 bootstrap：`.claude-plugin` / `.codex-plugin` / `.cursor-plugin` / `gemini-extension.json`（及 `GEMINI.md` / `AGENTS.md` 的 include）。

### 文案层

> **边界 — 写门/分类启发/body 质量段归 `write-gate-examples`（已落地），本轮不重写。** Phase 2 prose 重写按 section 标题锚点**跳过**：`protocol.md` 的 `## Write gate`、`exit-ritual.md` 的 `### 写工件 body 的质量` + `## Classification heuristics` 的 (a)–(h)。**Phase 2 不得移动/改名这三处标题**（只跳过、不重构）；真要动结构须在本 spec 内显式交接新锚点。下方点 3/4 改 exit-ritual/protocol 时只动 hook/注入叙事段，不碰这三处。

1. **删 `docs/why-no-hooks.md`**：gating 拒绝理由已入 `cross-host-hooks.md`「关键发现 3 + 取用方案」，删原文件无损。迁移清理（采纳 gpt/ds——给全 grep 模式，别遗漏变体）：
   - **指向该文件的引用**：grep `why-no-hooks`（覆盖 `[[why-no-hooks]]`、`why-no-hooks.md` 相对链接、纯文本提及）；命中处重定向到 `cross-host-hooks.md` 或就近删除。`docs/INDEX.md` 去行由 `flightdeck_index.py` regen 自动完成。
   - **已废措辞变体**：grep `无 ?hook|no-hook|仅 ?Claude|退指令文件|效果未实证|未实证`（中英混写/缩写）扫全 `skills/` + `docs/`，逐处判删（保留 `cross-host-hooks.md` 的史述）。
   - **外部引用**：检查 repo 根 `README`/`AGENTS.md`/`CHANGELOG` 是否提 `why-no-hooks`；git 历史里的旧链接**不追**（immutable，按本项目「不留历史流水账」取向）。
2. **`skills/_shared/bootstrap.md`**：line 19-20「welded by a Stop hook on **Claude Code**」改为「welded by the turn-end hook on **every host that fires it**（Claude/Codex `Stop`、Cursor `stop`、Gemini `AfterAgent`）」；保留 entry-handoff + 知识分类 + soft-land 强制令（内生职责，不动）。

   > **bootstrap 链路优先级（采纳 gpt——杜绝双重注入）**：① **Claude/Codex/Gemini** = hook `SessionStart` 注入 `hookSpecificOutput.additionalContext`（主路径）；② **Cursor** = hook 写 `.cursor/rules/flightdeck-context.mdc`（`alwaysApply`）为主路径（sessionStart 不可靠，不作主依赖）；③ `GEMINI.md`/`AGENTS.md` `@`-include = **地板**，仅当 hook 不可用时承载；④ manifest **不再单独 include bootstrap 正文**。同一会话同一段 bootstrap 只注入一次。
   >
   > **「hook 不可用」判定（采纳 claude#3——给地板的切换条件）= 下列任一**：hook 配置/脚本文件缺失、wrapper 探测无 bash/python 而 `exit 0`、或 Phase 0 实证未观测到注入到达模型上下文。命中即该家走 `@`-include / 手动 `/flightdeck:preflight` 地板。
3. **`skills/preflight/exit-ritual.md`**：删「只有 Claude 焊 board / 其余靠 agent 自觉重生」的对冲；board AUTO 区四家都焊 → agent 回合结尾只剩判断性看板（`## 下一步`/plan `current:`）+「本回合有写门知识吗→ soft-land」。删「自动发生」与「未实证」类措辞。
4. **`skills/preflight/SKILL.md` / `protocol.md` / `landing/SKILL.md` / `status/SKILL.md`**：把入场/出场叙事统一到「hook 为主路径注入接手态 + Stop 焊 board-sync；hook 没触发 → 手动 `/flightdeck:preflight` 一行地板」。删散布的双路径展开。
5. **`docs/session-flow.md`**：主干图/叙事改为四家一致的 hook 入场 + Stop board-sync；删宿主分级与兜底分支的大段。
6. **保行为紧致**（只压字数、附「行为不变」自检；**有冗余则压、无可压则原样，不为改而改**——回应 claude#5：如 `spec-lifecycle.md`/`model-architecture.md` 本无 hook 措辞，若无可压即跳过，列入仅表示"在扫描范围内"非"必须改"）：`protocol.md` / `templates.md` / `folder-semantics.md` / `walkaround/SKILL.md` / `new/SKILL.md` / `emit-agents-md/SKILL.md` / `launch/SKILL.md` / `model-architecture.md` / `script-layer.md` / `spec-lifecycle.md`。

> **保行为硬约束**：第 6 类改动后，数据模型 / status 合法值 / frontmatter 必填项 / 文件夹分类 / INDEX 行格式**逐项不变**。验收闸是**两道**：① `flightdeck_index.py --check` + `flightdeck_lint.py` 全绿（**必要非充分**——只证 frontmatter/INDEX 完整，不证语义）；② **人工 diff 自检**——逐条确认删的是冗余措辞、改的不是规则（采纳 gpt/ds：脚本证明不了语义不变）。有疑则不动那一段。

### spec 收编映射

| 在飞工件 | 处置 |
|---|---|
| `specs/2026-06-06-auto-land-executor` | 「Codex/Gemini 仅指令文件 + why-no-hooks 改写」**被本 spec 取代** → 标 `superseded`（by 本 spec）；其已实施且仍有效的部分（Layer 1/2 机制、Stop 不 block）由本 spec 承继并扩到四家 |
| `specs/2026-06-06-end-of-turn-soft-landing` | *what*（soft-land 三档语义、幂等）仍有效、**不 superseded**、由该 spec 拥有。**本 spec 只改 exit-ritual 里 soft-land 的「触发叙事」**（hook/auto 部分——四家焊 board、入场注入），**不碰三档语义的表述**。划界：语义归 soft-landing spec、触发叙事归本 spec，杜绝两 spec 改同段（采纳 claude#4/gpt/ds） |
| `plans/2026-06-06-auto-land-executor-rollout` | 未做完部分并入本 spec 的新 rollout plan；**原 plan 标 `superseded`**（不留 active 并存）。已实施且仍有效的产出（`hooks/`、bootstrap、Claude/Cursor 接线）由新 rollout **承继为既有基线、不重做** |
| `plans/2026-06-06-soft-landing-rollout` | 同上：未做完并入、原 plan 标 `superseded` |

> 收编后 cockpit `## 进行中` 只剩本 spec（+ soft-landing spec 的 what）一条 hook 主线，消除两套并存。

## 纳入的恢复质量增量（借鉴外部记忆系统，用户拍板并入本轮）

来源 `docs/external-memory-borrowings.md`。本重构正在动入/出场（landing/exit-ritual）流程，故把两条**直接提升恢复成功率**的增量顺手并入（二者本质都是 landing artifact、非独立功能；一起改比回头改便宜）：

- **#2 cockpit `## 关键上下文` 槽（借 ReMe Compactor `## Critical Context`）**：cockpit 现有 focus + 下一步，但缺"承重字面量"——正改的路径、失败的测试名、错误串、关键函数名。新增一个 **agent 判断填写**的 `## 关键上下文` 区（语义同 `## 下一步`，soft-land/checkpoint 时刷新；**非脚本 AUTO 区**，因需判断）。恢复时这是"接手就能继续"的最后一公里。落点：cockpit 模板（`templates.md`）+ exit-ritual/soft-land 填写指引 + preflight 读取。
- **#4 失败/弯路捕获（借 ReMe `FailureExtractionOp`）**：landing 分类器加显式分支——本回合若**放弃某路径/撞墙**，写 `incident` 记**失败路径 + 为何失败**（不只记最终修复）。flightdeck `incidents/` 正为此，但写门话术偏"最终修复"、弱化负面知识。落点：exit-ritual/landing 分类启发加一条。

> **不并入本轮**：#1 写门负例（纯 prompt、低风险，单独推进）；#7 恢复回归测试（等恢复模型稳定再固化，避免绑死变动目标）——见 `external-memory-borrowings.md` 采纳决策。

## 实施次序 —— 先实证后精简（采纳 gpt/ds 核心修正）

评审最强一点：`cross-host-hooks.md` 证明的是**能力/配置正确**，**不是 flightdeck 在每家真跑通**（能挂 command ≠ 可靠注入 + 每回合 board-sync）。故本 spec 的次序**反过来——verify-then-strip，逐家**：

1. **Phase 0（每家·实证门）**：接线后在真实会话验证该家——① 入场注入是否真到达模型上下文；② 回合结尾 hook 是否每回合触发、board `--check` 恒 clean；③ 缺 deck/bash/python 静默降级。**专项风险核查（采纳 ds 的成熟度点）**：Cursor `stop` 成熟度（社区报告 CLI 近期才修、历史有不触发）+ `sessionStart` 注入是否真达 Agent Window；Gemini **同步阻塞**模型下 board-sync 实测耗时（用数据证"体量小"，非假设）。
2. **Phase 1（每家·条件精简）**：**只有通过 Phase 0 的宿主**，才删它那条降级叙事、把 hook 提为主路径。**未通过的宿主保留其 `@`-include / 手动 preflight 地板叙事**，记"待实证"，不强行精简。
3. **不依赖单家实证、可独立做**：删 `why-no-hooks.md`、保行为紧致——它们不声称"某家 hook 已跑通"。

> 这把"删降级叙事"从**无条件**改成**每家实证后**，直接补上评审指出的「事实层 → 策略层」推理缺口。最坏情形（某家始终过不了实证）= 那家停在地板叙事，不回退、不致命。**写 plan 时据此切相位**：接线 → Phase 0 实证 → Phase 1 条件精简，而非"接线即删叙事"。

## 影响的文件（改动清单）

**新增**：Codex hook config、Gemini `.gemini/settings.json` 片段（+ 对应 manifest 接线）。
**改动（机制）**：`hooks/hooks-cursor.json`（补 stop）、`hooks/session-start`（emit 补 Codex/Gemini + project-dir 泛化）、`hooks/stop`（project-dir 泛化）、各 manifest。
**改动（文案）**：`skills/_shared/bootstrap.md`、`skills/preflight/{SKILL,exit-ritual,protocol}.md`、`skills/{landing,status}/SKILL.md`、`docs/session-flow.md`。
**保行为紧致**：`skills/preflight/{templates,folder-semantics}.md`、`skills/{walkaround,new,emit-agents-md,launch}/SKILL.md`、`docs/{model-architecture,script-layer,spec-lifecycle}.md`。
**删除**：`docs/why-no-hooks.md`（+ INDEX 行 + 全仓引用）。
**复用**：`flightdeck_index.py <deck>`（静默 board-sync，**不新增其脚本接口**）；hook 脚本的 host-adapter 输出分支按 4 家扩展——这是 hook 适配面扩展，非新 index 接口（采纳 gpt 措辞精确化）。

## 测试

- **机制 —— 最小覆盖矩阵**＝`{入场注入、回合末 board-sync、缺 deck 静默、缺 bash 静默、缺 python 静默}` × `{Claude, Codex, Cursor, Gemini}`，每格给命令 + 断言（不许选择性验证，采纳 gpt/ds）。专项：目录在但 cockpit 缺/损 → 仍注入静态令、只跳锚点；Stop/AfterAgent 已 clean 时重生无变化；**Cursor stop 新接线**与 sessionStart 共存不互扰；**Gemini 入场注入项**在字段锁定前测「降级到 `GEMINI.md` 地板」而非真 hook 注入。
- **保行为**：`flightdeck_index.py flightdeck --check` clean + `flightdeck_lint.py` clean（第 6 类文件改动的硬闸）；现有 149 测试不回归。
- **文案**：全仓 grep 无残留 `why-no-hooks` 引用、无「仅 Claude 焊 / 退指令文件 / 效果未实证」类已废措辞（除 `cross-host-hooks.md` 的史述）。

## 验收标准

- 四家各自 dogfood/冒烟：开场注入接手态、回合末 `--check` 恒 clean；缺 deck/缺 bash/缺 python 静默降级。
- **token 账（软指标、口径固定、采纳 gpt/ds）**：统计口径 = **skill 散文行数**（`skills/**/*.md` + `skills/_shared`，**不含**新增 hook config/manifest——机制文件本就增行，混入会污染口径）；基线 = 本 spec 落定时 **skills/ ≈ 2166 行（12 文件，2026-06-07）**。目标 = skill 散文净减且无信息丢失；**这是观测指标非 pass/fail 闸**（"无信息丢失"靠 diff 评审判，非脚本）。
- `why-no-hooks.md` 已删且无悬挂引用；`walkaround` 不报新孤儿/悬链。
- 收编后 cockpit `## 进行中` 无两套并存。
- 具体 N/抽样/目标行数 = plan 阶段定。

## 风险 / 取舍

- **Codex/Gemini 真 hook 效果首次实证**：从「指令文件未实证」升级为「真 hook」，但真 hook 在两家的**实际触发**仍需首次 live 复验；wrapper 失败静默降级到手动 preflight 为地板，不致命。
- **5+ 集成面维护成本**（四家 config + manifest）：明确承认，用维护成本换四家一致的可靠性；脚本单一真相源摊薄。
- **保行为紧致误伤数据模型**：以 `--check`/`lint` 全绿 + 逐项不变自检为闸；有疑则不动那一段。
- **环境降级地板被过度精简**：硬保留「hook 没触发 → 手动 preflight」一行，evidence = 仍有显式 `/flightdeck:preflight` skill 可独立跑通。

## 评审纪要

用户拍板（设计层）：机制 A、不启 gating、保留最小地板、全 skill 一起紧、删 why-no-hooks、收编在飞 spec。

外部 AI 评审一轮（claude/gpt/ds，原文 transient 存 `tmp/`；用户提示"不了解项目现状、仅供参考"）。

**采纳（改了 spec）**：
- **字段留白 → live 核实写实**（claude#1/#2、gpt#1/#2/#3、ds blanks）：四家事实表（Codex `Stop`+`.codex-plugin` `hooks`+`additionalContext`+stdin `cwd`；Cursor `stop`+`additional_context`+`workspace_roots`；Gemini `AfterAgent`+`GEMINI_PROJECT_DIR`）；**唯一残留** = Gemini 入场注入字段未公开 → 降级 `GEMINI.md` 地板，记账。
- **project-dir 优先级 + 不回溯上级**（gpt）：按宿主单一信号 + `$PWD` 兜底；只认 `D/flightdeck/`、不向上走。
- **soft-landing 职责划界**（claude#4/gpt/ds）：本 spec 只改触发叙事、不碰三档语义。
- **token KPI 口径固定 + 基线**（claude#3/gpt/ds）：skill 散文行数、基线 ≈2166、软指标非闸。
- **保行为双闸**（gpt/ds）：lint/check 必要非充分 + 人工 diff 自检。
- **可观测性**（gpt/ds）：`FLIGHTDECK_HOOK_DEBUG` 一次性诊断，破静默盲区。
- **bootstrap 三链路优先级**（gpt）：hook 主、include 地板、manifest 不重复注入。
- **superseded 状态钉死**（gpt/ds）：两 rollout 标 superseded 不留并存。
- **测试最小矩阵**（gpt/ds）：{5 场景}×{4 家} 给命令+断言。
- **迁移 grep 模式 + 废措辞变体 + 外部引用**（gpt/ds）。
- **gating 拒绝理由展开**（ds#2）；**emit 措辞精确化**（gpt：host-adapter 扩展非新接口）；**claude#5** spec-lifecycle 等无可压即跳过。

**反驳（评审缺上下文，未改）**：
- ds「run-hook.cmd 是 Windows 批处理、不能跨平台、无法判 bash」→ **错**：`: << 'CMDBLOCK'` polyglot（同时是合法 bash 与 cmd），采自 superpowers 已 ship+测试；扩展名缺省 + wrapper 正是为 Windows bash 探测而设（文件头自述）。ds「run-hook.cmd 必要性存疑」同此反驳。
- ds「Python 存在性未检查」→ **错**：`hooks/stop` 14-23 行已探 `python3/python` + `[ -f index_py ]`、缺即 `exit 0`。
- gpt「全仓 grep 无残留与史述冲突」→ 已在验收里碰出「除 cross-host-hooks.md 史述」。
- ds「149 测试来源未列」→ 在 `tests/`，auto-land spec 已记"149 通过"，非虚指。

外部 AI 评审第二轮（claude/gpt 转评 `cross-host-hooks.md`、ds 复评）：

**采纳（改了 spec/doc）**：
- **事实层→策略层推理缺口**（gpt 最强点 + ds「验证失败无 fallback」）→ 新增 **## 实施次序 verify-then-strip**：每家 Phase 0 实证门 + Phase 1 条件精简，未过的宿主停在地板叙事。
- **源真实性质疑**（claude#5/ds「geminicli.com 可疑/Codex 文档无法访问」）→ WebSearch 核实：geminicli.com **镜像官方 `google-gemini/gemini-cli` repo**、Google Developers Blog 佐证 → **残留未知消解**：Gemini 注入字段 = `hookSpecificOutput.additionalContext`（同 Claude/Codex，3/4 同形）。
- **「hook 不可用」降级判定**（claude#3）→ bootstrap 优先级补：文件缺失 / 无 bash·python / 实证未达三条任一。
- **来源版本锚点**（gpt/ds）→ 事实表加"无 commit 锚、2026-06-07 快照、动前复核"。
- **Cursor 成熟度 + Gemini 同步 perf**（ds）→ 并入 Phase 0 专项核查。

**反驳/澄清**：
- ds 重提 run-hook.cmd polyglot / python 未检查 / grep 模式 / token 基线 / 保行为闸 / soft-landing 冲突 / Codex 多配置歧义 → **均为对上一版的复述**，现行 spec 已逐条处置（polyglot 与 python 检查见 round-1 反驳；Codex 配置已定 `.codex-plugin` `hooks` 引 `./hooks/hooks.json`；其余见 round-1 采纳）。
- claude#1/#4 + ds 自指矛盾（`[[why-no-hooks]]` 悬链 / 回流清单说"订正"但 spec 说"删"）→ **属 `cross-host-hooks.md` 自身待清理**，本轮一并清（去 `[[why-no-hooks]]`、回流清单改指本 spec、TL;DR 软化"同构 Stop"、移走 4-5 集成面/perf 设计估算）。
- ds「Cursor Windows extensionless 弹窗」→ 由 `run-hook.cmd` wrapper 兜（宿主调的是 `.cmd`，非直接调无扩展名脚本）；列入 Phase 0 的 Windows-Cursor 冒烟。
