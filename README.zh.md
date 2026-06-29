<div align="center">

# flightdeck

**面向 AI 辅助工程会话的轻量操作协议。**

[![Version: 3.0.0-alpha.6](https://img.shields.io/badge/version-3.0.0--alpha.6-orange?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)
[![Codex](https://img.shields.io/badge/Codex-tested-success?style=flat-square)](adapters/codex/README.md)

中文 · [English README](README.md)

</div>

---

> [!WARNING]
> flightdeck 3.0 仍是 alpha。协议已经能用，并且本仓库正在 dogfood，但稳定版 3.0 前文件形态和措辞仍可能调整。安装新版本不会自动迁移旧 deck；可以运行 `/flightdeck:walkaround` 审计并修复旧形态，也可以用 `/flightdeck:launch` 重新开始。

AI 助手擅长单次会话，不擅长跨会话连续工作。flightdeck 给它一份小而明确的恢复载荷：当前在做什么、发生了什么变化、哪些知识以后还重要、下一步是什么。

## 你会得到什么

- **跨会话接续** — `/flightdeck:preflight` 读取项目 deck，列出可恢复的工作，并等你选择后才加载主题细节。
- **零丢失交接** — 工作推进后，flightdeck 更新当前主题索引、更新 `cockpit.md`、捕捉长期有用的知识，并做本地 commit。
- **严格写入门控** — 只记录会影响未来行为的决策、坑、流程和事实，不做垃圾抽屉式记忆。
- **纯 markdown** — deck 就是仓库里的文件和目录。能 diff、能 review、能 grep，也能跨 AI 工具继续使用。

## 安装

### Codex CLI / Codex App

Codex 通过 GitHub 插件链接安装已经验证。

1. 打开 `Plugins`。
2. 选择从 GitHub 添加插件。
3. 粘贴：

```text
https://github.com/Yuelioi/flightdeck
```

然后启用 `Flightdeck`，在项目里运行 `/flightdeck:launch`。

### Claude Code

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

更新时重新运行 `/plugin install`。卸载用 `/plugin uninstall flightdeck`。

### 其它工具

Cursor 和 Gemini 的 manifest 已包含在仓库里，但还没有完成端到端验证：

- Cursor: [`.cursor-plugin/`](.cursor-plugin/)
- Gemini CLI: [`gemini-extension.json`](gemini-extension.json)

欢迎提交验证日志。

## 第一次使用

在项目仓库中运行：

```text
/flightdeck:launch
```

它会创建：

```text
flightdeck/
  briefing.md      # 项目规则和共享知识订阅
  cockpit.md       # 小型项目索引：focus、active work、next step
  work/            # 活跃主题工作包
  knowledge/       # 长期项目知识，通过路由头触发
```

之后每次会话开始运行：

```text
/flightdeck:preflight
```

preflight 会读取 `briefing.md`、读取 `cockpit.md`、扫描知识头部、报告可恢复的工作，然后停下来等你选择。它不会把所有主题文件或所有知识正文一次性塞进上下文。

## 核心模型

flightdeck 有两层：

- **温层** — 仓库里的 `flightdeck/`。这是恢复载荷，应该被 commit。
- **冷层** — 仓库外的 `~/.flightdeck/`。完成的主题包和暂存想法可以放在那里。

核心规则是**位置即状态**：

- `flightdeck/work/<topic>/` 表示活跃工作。
- `~/.flightdeck/projects/<slug>/archive/<topic>/` 表示完成工作。
- `~/.flightdeck/projects/<slug>/ideas/<topic>/` 表示暂存想法，不是活跃工作。

每个活跃主题都有一个 `index.md`，说明当前事实、现在要读什么、什么条件下再读什么、发生了什么变化、下一步是什么。

知识文件使用一个很小的路由头：

```markdown
# <title>

SUMMARY: <一行摘要>
READ WHEN: <什么时候应该加载这份知识>

---
```

这样 preflight 可以把地图留在上下文里，同时只在触发条件出现时加载正文。

## 命令

| 命令 | 用途 |
| --- | --- |
| `/flightdeck:launch` | 创建新的 deck 骨架。已有 deck 时拒绝覆盖。 |
| `/flightdeck:preflight` | 进入会话：读取 deck，扫描路由头，列出可恢复工作，并等你选择。 |
| `/flightdeck:walkaround` | 审计并修复 deck 漂移：陈旧 cockpit、畸形主题包、缺路由头、旧 deck 形态等。 |

## 兼容性

| 工具 | 状态 | 说明 |
| --- | --- | --- |
| Claude Code | 已测试 | marketplace 安装已验证。 |
| Codex CLI / App | 已测试 | GitHub 插件链接安装已验证。 |
| Cursor | 仅 manifest | 尚未端到端验证行为。 |
| Gemini CLI | 仅 manifest | 尚未端到端验证行为。 |

## 文档

- 协议入口：[skills/preflight/SKILL.md](skills/preflight/SKILL.md)
- 概念说明：[skills/preflight/concepts.md](skills/preflight/concepts.md)
- 操作细节：[skills/preflight/operations.md](skills/preflight/operations.md)
- 版本历史：[CHANGELOG.md](CHANGELOG.md)

## 贡献

高信号贡献：

- 一份 AI 偏离协议的 transcript。
- Cursor 或 Gemini 的验证日志。
- 一个能让 deck 更容易冷启动恢复的小修复。

## License

[MIT](LICENSE) © 月离 (Yuelioi)
