---
status: active
when_to_read: 给 flightdeck 或任一 adapter 加任何 hook / 启动自动加载机制前
applies_to: [adapters, skills, hooks, startup]
last_updated: 2026-06-05
---

# Why flightdeck installs no hooks

flightdeck 在**任何宿主上都不装 hook**——没有启动钩子、没有 PreToolUse/PostToolUse 之类的拦截。
`adapters/claude/README.md` 写得很直白:"Nothing loads automatically — flightdeck installs
no startup hook. You run `/flightdeck:preflight` to begin a session." 这是有意的设计决策,不是缺功能。

## 决策

把"统一"放在**唯一可移植的层 = 共享 `skills/` 内容 + 手动 `/flightdeck:preflight` 入场**,
而不是放在各宿主的 hook 机制上。四家(Claude Code / Codex / Cursor / Gemini)的插件/扩展
manifest 都指向同一套 `skills/`(Gemini 经 `GEMINI.md` `@`-include),差异只在 manifest 格式。

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

- **不依赖 hook 的代价**:没有任何东西自动触发——入场必须显式 `/flightdeck:preflight`。这是
  接受的、且符合"显式入口"取向的取舍。
- **依赖 hook 的代价(被拒绝的那条路)**:等于给 4 家各写一套 hook、还要跟着各自版本演进
  (如 Cursor `sessionStart` 一度是 broken bug)——纯兼容包袱,违背本项目"果断删减、不留兼容
  死结"的取向。

> 唯一接近"跨工具统一"的约定是 `AGENTS.md`,但那是给**指令/上下文**用的(flightdeck `emit` 进
> 它),**不是 hooks**。没有"hooks 版的 AGENTS.md"。

## 由此推论

要给 flightdeck 加"每次会话自动跑某步""自动拦截某操作"之类能力前,先问:它能不能落在
**skill 内容 + 显式仪式**里,而不是某个宿主的 hook?默认答案是前者——否则就破坏了
tool-agnostic 这条底线。
