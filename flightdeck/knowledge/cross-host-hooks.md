# 跨宿主 hook 能力对照 + flightdeck hook 技术方案

> 四家官方 hook 文档实读（2026-06-07）后的对照 + flightdeck 取用方案。
> 决策原则见本文「关键发现 3 + 取用方案」；落地见 spec `2026-06-07-hook-primary-refactor`。
> **事件名册随各家版本演进**——动 hook 前以各家 live 文档为准，本表是骨架不是契约。

## TL;DR（headline = 四家已大幅趋同）

四家**全部**具备：JSON hook 配置（`event → matcher → handler`）、入场注入（`SessionStart`/`sessionStart`）、**回合结尾事件**（Claude/Codex `Stop`、Cursor `stop`、Gemini `AfterAgent`——是「都有结束事件」非「同构 Stop」）、`PreToolUse` 级拦截、上下文注入、续命。Codex 与 Claude 的 `hooks.json` **结构**几乎同构（注：结构近 ≠ 生命周期/payload/返回协议近，详关键发现 4）。

这**否掉了旧论据的事实前提**（原 `why-no-hooks.md`，本轮删除）「跨工具 hook 没有统一标准、Codex 无富 hooks」——现已大体趋同。但**决策结论基本不变**：可移植的仍是**内容**（共享 `skills/` + `bootstrap`），不是 hook 脚本（matcher 语法/返回 schema/降级语义仍每家有别）；gating 类 hook 仍拒，但理由换成**内生**的（block 归账既漏又矛盾），不再靠"无标准"。

> **能力 ≠ 接入实证**（采纳 gpt）：本文是**能力/配置事实层**，证明四家"都有更强 hook 能力"——**不等于** flightdeck 在每家已跑通注入 + board-sync。把 hook 提为主路径、删降级叙事须先过**每家 live 实证**（见 spec `2026-06-07-hook-primary-refactor` 的 verify-then-strip 次序）。

## 四家能力对照

| 维度 | Claude Code | Codex | Cursor | Gemini CLI |
|---|---|---|---|---|
| 配置文件 | `~/.claude` 或 `.claude/settings.json`；插件 `hooks/hooks.json` | `~/.codex` 或 `<repo>/.codex/hooks.json`、`config.toml [hooks]`、`.codex-plugin` | `~/.cursor` 或 `<project>/.cursor/hooks.json` | `~/.gemini` 或 `.gemini/settings.json` |
| 结构 | `event→matcher→hooks[]` | 同 Claude（含 TOML 变体） | `hooks.{name}[]`（带 `version`/`failClosed`） | `event→matcher→hooks[]` |
| 入场 | `SessionStart`（startup\|clear\|compact\|resume） | `SessionStart`（同上） | `sessionStart` | `SessionStart` |
| 回合/会话结尾 | `Stop` / `SessionEnd` | `Stop`（回合结尾） | `stop` | `AfterAgent` / `SessionEnd` |
| 工具前拦截 | `PreToolUse` → `permissionDecision:"deny"` | `PreToolUse` → `permissionDecision:"deny"` | `beforeShellExecution`/`preToolUse` → `permission:"deny"` 或 exit 2 | `BeforeTool` → Block/Deny |
| 注入上下文 | `additionalContext`（SessionStart 等） | `additionalContext` | `additional_context`（+`env`） | `hookSpecificOutput.additionalContext`（同 Claude/Codex） |
| 续命 | `decision:"block"`+`reason`（Stop） | `decision:"block"`+`reason`（Stop） | `followup_message`（`loop_limit` 默认 5） | Block Turn |
| 改写入参 | — | `PreToolUse` `updatedInput` | — | — |
| 多 handler 类型 | command/http/mcp_tool/prompt/agent | command | command / prompt(LLM 判定) | command |
| 失败降级 | exit 非 2 → 放行；非阻塞错进 transcript | exit 类似 | exit≠0/≠2 → **fail-open**（`failClosed` 可反转） | 同步等待，无 bash 即不触发 |
| 执行模型 | 应用层 | 应用层 | stdio 双向 JSON | **同步跑在 agent loop 内**（阻塞） |

> 表内事件名为各家**核心子集**；Claude 另有大量细粒度事件（`PostToolUse`/`PreCompact`/`SubagentStop`/`WorktreeCreate`…），Gemini 另有 `Before/AfterModel`、`BeforeToolSelection`、`PreCompress`。设计时按需查 live 文档。

## 关键发现

1. **入场注入四家可达（能力层）。** `SessionStart`（Claude/Codex/Gemini，注入字段均 `hookSpecificOutput.additionalContext`）/`sessionStart`（Cursor，`additional_context`）都能注上下文——bootstrap 强制令 + cockpit 锚点**四家都能走真 hook**，不再只有 Claude/Cursor、Codex/Gemini 退指令文件。（是否**可靠到达** → 见上「能力 ≠ 接入实证」）
2. **回合结尾 board-sync 四家可挂（能力层）。** 四家都有回合结尾事件（`Stop`/`stop`/`AfterAgent`）可挂 command——`flightdeck_index.py <deck>` 重生 board AUTO 区可在四家做，不止 Claude。（是否**每回合可靠触发** → 见上「能力 ≠ 接入实证」）
3. **gating 仍该拒，但换理由。** 四家 `PreToolUse` 都能 deny、`Stop` 都能 `decision:block` 续命——能力齐了。但 flightdeck 拒 gating 的理由**与可移植性无关**：拿 block 逼 landing **既漏**（二次 `stop_hook_active`/`loop_limit` 必放行 → 工件照悬空）**又矛盾**（=自动触发 full landing，与"手动/批量/等关联/用户说先别 land"冲突）+ 让 hook 承担业务语义。这条内生理由四家通用。
4. **趋同 ≠ 可移植脚本。** 配置形状像，但 matcher 语法（exact vs 正则 vs `failClosed`）、返回 schema（`permissionDecision` vs `permission` vs Block Turn）、降级语义（Cursor fail-open、Gemini 同步阻塞）各家有别。**可移植的仍是 bootstrap 内容**，触发胶水每家一薄层——这层结论不变。
5. **Gemini 同步跑在 agent loop 内**——hook 脚本慢会**直接拖慢**每回合；board-sync 须快，**实测耗时列入接入验证**（不预判"够快"）。

## flightdeck 的取用方案

延用决策原则的**二分**（gating 拒、被动采纳），按新事实把覆盖面拉满：

- **被动注入 / 同步类（无门控、失败即静默降级到手动 preflight）→ 采纳，四家拉满。**
  - **入场注入**（bootstrap 强制令 + cockpit 锚点）：四家都走真 `SessionStart`/`sessionStart` hook 的 `additionalContext`。指令文件（`AGENTS.md`/`GEMINI.md @`-include）从"主路径"降为"hook 不可用时的兜底地板"。
  - **Stop board-sync**（`flightdeck_index.py <deck>` 重生 AUTO 区，`exit 0` 不门控）：四家都挂回合结尾事件。
  - 可移植的是 **`skills/_shared/bootstrap.md` 单一真相源**；每家一薄层触发胶水，`run-hook.cmd` 无 bash 即静默 `exit 0` → 退回手动 `/flightdeck:preflight`。（集成面计数与 perf 评估属设计层，见 spec）
- **gating / 拦截类（PreToolUse deny、Stop block 续命逼办事）→ 仍拒**（内生理由，见关键发现 3）；个别 Claude-only 增强须 deterministic 触发再议。
- **「无 hook 宿主不支持」→ 不适用。** 四家均已有 hook、无宿主可砍；且显式 `/flightdeck:preflight` 是零胶水、到处能跑的 graceful-degrade 地板，须保留。

### 落地

四家趋同的落地——给 Codex/Gemini 补真 hook、Cursor 补 stop、删 `why-no-hooks.md`、全 skill 文案精简——统一由 spec **`2026-06-07-hook-primary-refactor`** 承载（含 verify-then-strip 次序）。本 doc = 其**事实底座**，动 hook 前先读这张表。

## 来源

四家官方 hook 文档，2026-06-07 实读：
- Claude Code — `code.claude.com/docs/en/hooks`
- Codex — `developers.openai.com/codex/hooks`
- Cursor — `cursor.com/cn/docs/hooks`
- Gemini CLI — `geminicli.com/docs/hooks/`
