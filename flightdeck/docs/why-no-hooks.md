---
status: active
when_to_read: 给 flightdeck 或任一 adapter 加任何 hook / 启动自动加载机制前
applies_to: [adapters, skills, hooks, startup]
last_updated: 2026-06-05
---

# Why flightdeck installs no hooks

flightdeck 历史上**不装任何 hook**——没有启动钩子、没有 PreToolUse/PostToolUse 之类的拦截,
入场全靠显式 `/flightdeck:preflight`。这条立场如今**部分修订**(见下一节):对 **gating/拦截类
hook** 仍然拒绝,对 **被动注入/同步类 hook** 已采纳一套(SessionStart 注入 + Stop 静默 board-sync,
见 `hooks/`)。下面的论据要分这两类读。

## 更新(2026-06-06):前提部分失效

原本"跨工具 hook 没有统一标准、装 hook = 纯兼容包袱"的论据,对 **gating/拦截类 hook**
(PreToolUse 拦操作、`decision:block` 续命)**仍然成立**——那条路继续拒绝。但对 **被动注入/同步类
hook**(无门控、只在 SessionStart 注入上下文 / 在 Stop 静默重生派生区)它**被证伪**了:superpowers
用 `hooks/run-hook.cmd` 跨平台 polyglot wrapper + 每工具一薄层胶水**证明可移植**(失败即静默降级到
手动入场)。flightdeck 据此采纳了被动 hook(spec `2026-06-06-auto-land-executor`):Claude 入场注入
bootstrap + cockpit 锚点、Stop 焊死机械 board AUTO 区;Cursor 入场注入;Codex/Gemini 仅指令文件注入
(`AGENTS.md` / `GEMINI.md` `@`-include),**效果未实证、列入测试、不预设遵从率**。所以本文立场从
"任何宿主都不装 hook"修订为下面的**决策原则**。

## 决策

把"统一"放在**可移植的内容层 = 共享 `skills/` + 单一真相源 bootstrap 强制令**,而不是各宿主的
gating hook 机制上。四家(Claude Code / Codex / Cursor / Gemini)的插件/扩展 manifest 都指向同一套
`skills/`(Gemini 经 `GEMINI.md` `@`-include),差异只在 manifest 格式。这层内容的**触发**:被动注入
类胶水每工具一薄层(Claude/Cursor 经 SessionStart 注入进入 preflight 接手态);无注入的宿主则以
显式 `/flightdeck:preflight` 为地板——内容不变,只是触发方式不同。

## 为什么:跨工具 hook 没有统一标准

同一个"工具调用前"的概念,各家的事件名、配置文件、执行模型互不通用,hook 脚本无法跨工具复用:

| Agent | 配置位置 | 模型 |
|---|---|---|
| Claude Code | `settings.json` | 应用层、~26 个生命周期事件(`PreToolUse`/`SessionStart`…),可编程拦截 |
| Cursor | `.cursor/hooks.json` | 自成一套(`beforeShellExecution`/`afterFileEdit`/`userPromptSubmitted`…) |
| Gemini CLI | `.gemini/settings.json` | `BeforeTool`/`AfterTool`(regex matcher),同步跑在 agent loop 内 |
| Codex | —(无富 hooks) | 内核层沙箱(Seatbelt/Landlock/seccomp)管安全,只有轻量 `notify` 回调 |

Codex 尤其是异类:它压根不走"可编程 hooks"路线。所以"给 flightdeck 加个 hook、四家都生效"
这个前提本身不成立。

## 取舍

- **被动注入/同步类 hook 的代价(已采纳)**:每工具一薄层胶水 + 跟版本演进的维护成本,明确
  承认、用它换可靠性(入场接手态 + 机械 board AUTO 不漂);失败即静默降级回手动 `/flightdeck:preflight`。
- **gating/拦截类 hook 的代价(被拒绝的那条路)**:等于给 4 家各写一套 hook、还要跟着各自版本演进
  (如 Cursor `sessionStart` 一度是 broken bug)——纯兼容包袱,违背本项目"果断删减、不留兼容
  死结"的取向。

> 唯一接近"跨工具统一"的约定是 `AGENTS.md`,但那是给**指令/上下文**用的(flightdeck `emit` 进
> 它),**不是 hooks**。没有"hooks 版的 AGENTS.md"。

## 决策原则(hook 取舍)

要给 flightdeck 加任何 hook 前,先按类型二分:

- **被动注入 / 同步类**(无门控、胶水可移植、失败即静默降级到手动)→ **接受**。例:SessionStart
  注入 bootstrap + cockpit 锚点;Stop 静默重生 board AUTO 区(`## 进行中` + 各 `INDEX.md`)。代价是
  每工具一薄层胶水 + 版本兼容跟进,明确承认。
- **gating / 拦截类**(PreToolUse/PostToolUse 拦操作、`decision:block` 续命、承担业务语义判断)
  → **拒绝**,或仅 **Claude-only 增强且须 deterministic 触发**。理由不变:跨工具无统一标准、纯
  兼容包袱;且 block 对本项目的归账既漏(放行即漏)又矛盾(等于自动触发 full landing)。

凡是能落在 **skill 内容 + 显式仪式 + 被动注入**里的能力,优先这条;以后遇 Resume/Compact/PostToolUse
之类照此判,不再逐个重吵。tool-agnostic 仍是底线——可移植的是**内容**,每工具的触发胶水各写一薄层。
