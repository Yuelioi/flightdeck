<div align="center">

# ✈️ flightdeck

**面向 AI 辅助工程会话的操作协议。**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)
[![AGENTS.md](https://img.shields.io/badge/emits-AGENTS.md-blueviolet?style=flat-square)](https://agents.md)

🇨🇳 中文 · 🇬🇧 [English README](README.md)

</div>

---

> 你的 AI 助手在两次对话之间会失忆。**flightdeck** 是一套目录约定加一个 skill，给它跨会话的操作连续性 —— 让下一次会话知道你在做什么、为什么、下一步做什么。

## TL;DR

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

会话开始时运行 `/flightdeck:preflight` —— 会话入口接管。已有项目里它读 `flightdeck/cockpit.md`、瞥一眼 `git status`、报告你上次停在哪。全新项目（没有 `cockpit.md`）里它指引你去 `/flightdeck:launch`，一步建好一个 deck —— 零提问。不会自动加载任何东西，你来调它。

## 它是什么

一个你的 AI 按约定读写的 `flightdeck/` 目录：

```
flightdeck/
├── cockpit.md          # 必读入口 —— Active focus / Next session / Hanging tasks
├── rules.md            # 项目配置 —— version + 自由散文 house rules
├── INDEX.md            # 跨所有文件夹的全局状态汇总
│
├── sketches/           # 早期想法、草稿
├── specs/              # 范围化的设计文档
├── plans/              # 分步实施计划
├── incidents/          # 教训记录（根因，不许"忘了"）
├── checklists/         # 可复用流程
├── references/         # 导入的外部材料（RFC、竞品代码）
├── debriefs/           # 外部 review 反馈（原文 + 处置）
├── docs/               # 自撰常驻技术资料
└── archive/            # 完成工作的归档
```

### cockpit.md —— 唯一必读文件

每次会话首先读取，硬上限 80 行：

```markdown
# Cockpit — payment-service

**Last updated**: 2026-05-28 by alice (shipped Stripe webhook refactor)
**Active focus**: stabilize Stripe webhook handler — failing edge cases in incidents/

## Next session

1. Reproduce the duplicate-event bug from incidents/stripe-idempotency.md (Case 3).
2. Decide: idempotency key in DB vs Redis.
3. Update plans/2026-05-26-stripe-hardening.md Phase 2 with the decision.

## Hanging tasks

- (none)
```

没有 500 行的上下文倾倒 —— 历史内容都在更深一层的文件夹里，按需从 `INDEX.md` 读取。

## 安装

### Claude Code &nbsp;<sub>✅ 已测试</sub>

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

更新：重跑 `/plugin install`。卸载：`/plugin uninstall flightdeck`。无 marketplace：`git clone` 后 `./install.sh`（Windows 用 `.\install.ps1`）。

### 其它 AI 工具 &nbsp;<sub>⚠️ manifest 已就位，未验证</sub>

<details>
<summary><b>Codex CLI / Cursor / Gemini CLI</b></summary>

- **Codex CLI** —— `/plugins` → 搜 "flightdeck" → 安装。见 [adapters/codex/](adapters/codex/README.md)。
- **Cursor** —— Agent 聊天里 `/add-plugin flightdeck`。见 [adapters/cursor/](adapters/cursor/README.md)。
- **Gemini CLI** —— `gemini extensions install https://github.com/Yuelioi/flightdeck`。见 [adapters/gemini/](adapters/gemini/README.md)。

</details>

你不用手动建 deck —— 跑一次 `/flightdeck:launch` 就帮你建好。

## 用法

**会话开始** —— 运行 `/flightdeck:preflight`。它：

1. 读 `flightdeck/cockpit.md`。
2. 瞥一眼 `git status`（分支 / 版本）—— 仅在明显不对时给一行被动提示，绝不阻塞式追问。
3. 报告下一项 —— 说 "go" 执行。

全新项目（没有 `cockpit.md`）则 preflight 指引你去 `/flightdeck:launch`：一步确定性复制脚手架 —— **零提问**（不问 git / 访谈 / `AGENTS.md`）。开始干活时再填 `cockpit.md` 的 `Active focus` / `## 下一步`；`git init` 和 `/flightdeck:emit-agents-md` 随时可选做。

**会话结束** —— 运行 `/flightdeck:landing`。它把新知识分类（bug → `incidents/`、流程 → `checklists/`、一次性 → 丢弃）、刷新 `cockpit.md`、提交。下一次会话 —— 哪怕换个 AI 或换个人 —— 都能从这里精确接上。

### 命令

| 命令 | 用途 |
| --- | --- |
| `/flightdeck:launch` | **首次建 deck** —— 复制脚手架、播种 `cockpit.md`（零提问）。deck 已存在则拒绝。 |
| `/flightdeck:preflight` | **会话入口接管** —— 读 `cockpit.md`、瞥一眼 git、报告下一项。无 deck → 指向 `/flightdeck:launch`。 |
| `/flightdeck:new` | 撰写 deck 工件（spec/plan/incident/checklist/chart）—— 盖 frontmatter + 命名、重生 INDEX/cockpit。代替手搓。 |
| `/flightdeck:landing` | 会话收尾 —— 分类新知识、更新 cockpit、提交。 |
| `/flightdeck:walkaround` | 完整性审计 —— 协议漂移检测。 |
| `/flightdeck:emit-agents-md` | 从 `cockpit.md` 重生 `AGENTS.md`。 |

工件 `status` **自动**推进（idea→active→done）。五个仪式（`preflight` / `landing` / `walkaround` / `emit-agents-md` / `status`）都可自调；`landing` 按判断决定归档（被 active 工件交叉引用的 `done` 工件留在原地）。`commit` 是**本地自动、push 才先问**（本地 commit 可逆；push 是受控关卡）。`/flightdeck:launch` 是显式的一次性命令（建 deck），不是会话仪式。会话开始不加载任何东西，也没有后台进程。

### 路由 —— 什么触发什么

| 当下情形 | AI 去读 |
| --- | --- |
| 会话开始 /「我们刚在干嘛？」 | `cockpit.md` |
|「迁移为啥挂了？」 | `incidents/` |
|「测试怎么跑？」 | `checklists/` |
|「来设计个 X」 | `specs/` |
|「拆成任务」 | `plans/` |
|「这是 review 反馈」 | `debriefs/`（带处置） |

## 配置

`flightdeck/rules.md` 是按项目的控制面板 —— 必需（承载 deck 的 `version`）：

```yaml
---
version: <release>       # 唯一的结构化字段
---

## House rules

### Project conventions
# deck 局部约定，如 "specs 用中文"、"不用 references/"

### Autonomy overrides
# 行为覆盖；省略 = 默认（本地 commit 自动、push 才先问；仪式都可自调）
```

`version` 是唯一的结构化字段。其余全靠**推断、默认或 skill 判断**：

- **git** —— 由是否有 `.git` 目录推断。
- **AGENTS.md** 重生 —— 由是否有 `AGENTS.md` 文件推断。
- **脚本** —— 由是否能跑到 `uv`/`python` 推断（否则走 markdown 兜底）。
- **仪式** —— 五个都可自调；**`status`** 自动推进 idea→active→done，但**从不归档**（归档是 `landing` 按交叉引用的判断）；**`commit`** 本地自动、**push 才先问**。

要改其中任何一条，在 `### Autonomy overrides` 里写一句标准句：

- `commit: ask`（每次本地 commit 前先问）· `don't auto-commit; leave changes for me / CI`
- `status: don't auto start` —— 不自动 flip idea→active
- `this deck doesn't use git` · `has AGENTS.md but don't auto-regen`

## 为什么需要它

多数"AI memory"方案的失败在于什么都存 —— 信号淹没在垃圾抽屉里。flightdeck 反着来：**严格写入门控**（只存会影响未来决策的）、**文件夹=类型 + status 生命周期**（工作推进、再归档到 `archive/`）、**INDEX 优先读**（大项目省 token）、以及会话收尾时分类新知识的**landing 仪式**。它是纯 markdown —— 能在 review 里 diff、在终端 grep，还能扛过模型升级或 AI 工具切换。

> ✨ 语义清晰高于主题统一 —— 航空隐喻只在能让意图更清晰处使用，绝不当成主题。

## 兼容性

| 工具 | 状态 | Manifest |
| --- | --- | --- |
| Claude Code | ✅ 已测试 | [`.claude-plugin/`](.claude-plugin/) |
| Codex CLI / App | ⚠️ 未测试 | [`.codex-plugin/`](.codex-plugin/) |
| Cursor | ⚠️ 未测试 | [`.cursor-plugin/`](.cursor-plugin/) |
| Gemini CLI | ⚠️ 未测试 | [`gemini-extension.json`](gemini-extension.json) |

[`skills/`](skills/) 下的内容是**工具无关的 markdown**；manifest 只是薄薄的发现指针。"未测试"指安装能用、但还没人端到端验证 AI 是否遵守协议 —— **欢迎带验证日志的 PR**。

## FAQ

<details>
<summary><b>这和直接用 AGENTS.md 区别在哪？</b></summary>

[AGENTS.md](https://agents.md) 是*静态*项目规则的跨工具标准。flightdeck 架在它之上 —— `/flightdeck:emit-agents-md` 从 `cockpit.md` 往 `AGENTS.md` 写一个 fenced block —— 并补上 AGENTS.md 没有的：跨会话接续、status 生命周期、防垃圾抽屉的写入门控、错题追踪。如果你只需要一份静态规则清单，单用 AGENTS.md 就够了。

</details>

<details>
<summary><b>我有个旧的 <code>flightdeck/</code> —— 怎么升级？</b></summary>

`/flightdeck:walkaround` 读 deck 的 `version`、并提示引导式迁移 —— 绝不静默，任何移动前都先征得你同意。`/flightdeck:preflight` 只在版本结构落后时提示并指向它（兼容但落后的版本由它静默 stamp）。见 [MIGRATION.md](MIGRATION.md)。

</details>

## 文档

**深入指南** —— 见 [`docs/`](docs/)：[生命周期与执行流程](docs/lifecycle.md) · [架构](docs/architecture.md) · [设计哲学](docs/philosophy.md) · [横向对比](docs/comparison.md)

**协议参考**（canonical，AI 向）：[protocol.md](skills/preflight/protocol.md) · [文件夹语义](skills/preflight/folder-semantics.md) · [模板](skills/preflight/templates.md) · [landing 仪式](skills/preflight/exit-ritual.md) · [MIGRATION.md](MIGRATION.md) · [CHANGELOG.md](CHANGELOG.md)

## 贡献

skill 改动遵循 **RED-GREEN-REFACTOR** —— 没有失败测试不许改（[TEST_PLAN.md](TEST_PLAN.md)）。最高信号的贡献：一份 AI 钻协议空子的 transcript，或某个 Codex / Cursor / Gemini manifest 的端到端验证日志（[模板](.github/PULL_REQUEST_TEMPLATE/manifest-verification.md)）。

## Roadmap

可选文件夹（`briefing/`、`blackbox/`、`crew-handover/`、`experiments/`）· "continuance" 基准（给 AI 一个半截项目的 deck、说"继续"、量化恢复质量）· 归档合成/压缩 · 未测适配器的端到端验证 · MCP server。完整历史见 [CHANGELOG.md](CHANGELOG.md)。

## 致谢

[AGENTS.md](https://agents.md) —— wire format · [OpenSpec](https://github.com/openspec/openspec) —— spec 演化标记 · [Cursor MDC](https://docs.cursor.com) —— 路径范围 frontmatter · [Letta Code](https://github.com/letta-ai/letta) —— 晋升门模式 · [superpowers](https://github.com/anthropic-experimental/superpowers) —— 协议风格 · [Cline Memory Bank](https://docs.cline.bot) —— 启发写入门控的那个模式。

## License

[MIT](LICENSE) © 月离 (Yuelioi)

---

<div align="center">

如果 flightdeck 帮你省下了一个上下文窗口，[给个 star](https://github.com/Yuelioi/flightdeck/stargazers)。

</div>
