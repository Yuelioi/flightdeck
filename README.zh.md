<div align="center">

# ✈️ flightdeck

**面向 AI 辅助工程会话的操作协议。**

[![Version: 3.0.0-alpha.5](https://img.shields.io/badge/version-3.0.0--alpha.5-orange?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-tested-success?style=flat-square)](adapters/claude/README.md)

🇨🇳 中文 · 🇬🇧 [English README](README.md)

</div>

---

> [!WARNING]
> **面向早期试用者的预发布版。** 这是 flightdeck 的 AI-native 重写版 —— 更少零件、无 schema、无脚本。格式与行为仍可能再变，先别在生产项目上依赖它。旧版创建的 deck **不会**自动迁移：请用 `/flightdeck:launch` 新建 deck，再把旧 `cockpit.md` 里仍有用的内容手工搬过来。反馈正是这个预发布版的意义 —— 欢迎提 [issue](https://github.com/Yuelioi/flightdeck/issues)。

> 你的 AI 助手在两次对话之间会失忆。**flightdeck** 是一套目录约定加一个 skill，给它跨会话的操作连续性 —— 让下一次会话知道你在做什么、为什么、下一步做什么。

## ✨ 亮点

- **默认零丢失 —— 恢复载荷自己落盘。** 任何做了真实工作的回合末尾，flightdeck 自动 **persist**：扫描这一回合的产出、把值得留的新知识写进 `knowledge/`，重写当前主题的 `index.md`，重写 `cockpit.md`，提交仓库。没有要记着跑的收尾命令。想关窗口随时关 —— 下一次 `/flightdeck:preflight` 从真实现场接手，而不是过期快照。
- **无 schema、无脚本、无项目级 INDEX。** 整套东西就是纯 markdown 加两条约定：**位置即状态**（项目里的文件夹 = 活的，移出 = 完成）和每个知识文件一行的**路由头**。没东西要迁移、没东西要保持同步、没东西会在模型升级时坏掉。

## TL;DR

```text
/plugin marketplace add Yuelioi/flightdeck
/plugin install flightdeck@flightdeck-marketplace
```

会话开始时运行 `/flightdeck:preflight` —— 会话入口接管。已有项目里它读 `flightdeck/briefing.md` 和 `flightdeck/cockpit.md`，扫描知识头部，列出可继续的工作，并等你选择后才读取该主题的 `index.md`。全新项目（没有 `cockpit.md`）里它指引你去 `/flightdeck:launch` 建好一个 deck。不会自动加载任何东西，你来调它。

## 它是什么

一个你的 AI 按约定读写的 `flightdeck/` 目录 —— 一层**温存层（warm tier）**住在你的仓库里、每回合提交，加一层放在全局普通目录、装「已完成或搁置」的**冷存层（cold tier）**：

```
your-project/
└── flightdeck/            # 温存层 —— git 跟踪，每回合提交
    ├── cockpit.md         # 项目索引（Focus / In flight / Next / Open questions）
    ├── briefing.md        # 稳定、人维护 —— ## Conventions（house rules）+ ## Subscriptions
    ├── work/              # 主题工作包：index.md + 可选 design/plan 文件
    └── knowledge/         # 路由到未来行为的知识，按域嵌套

~/.flightdeck/             # 冷存层 —— 全局普通目录，不是 git
├── knowledge/             # 真·跨项目知识（经 briefing 的 ## Subscriptions 订阅）
└── projects/<slug>/       # 单个项目的冷存：archive/<topic>/ + ideas/<topic>/
                           # <slug> = 项目绝对路径，分隔符 → -（防同名碰撞）
```

没有项目级 `INDEX.md`、没有 YAML frontmatter、没有 status 字段。**位置即状态**：`work/` 里的 topic package 是活的；把它移进 `~/.flightdeck/projects/<name>/archive/<topic>/` 就标记为完成。停放的 idea 住在 `ideas/<topic>/`，只是轻量 seed，不是 active recovery package。知识是常驻的 —— 在 = 有效，删了 = 死了。微妙状态（阻塞、等待、待评审）活在 cockpit 散文里，而不是某个文件夹或字段。

### cockpit.md —— 项目索引

每次会话首先读取。它故意保持小 —— 列出可继续的主题工作包，而不是承载主题笔记：

```markdown
# Cockpit — payment-service

Focus: stabilize the Stripe webhook handler — failing edge cases under knowledge/stripe/

## In flight

- work/webhook-idempotency/ — next: choose DB vs Redis key；主题 index 里有读取清单

## Next

Choose `work/webhook-idempotency/` to resume.

## Open questions

- Is the duplicate caused by Stripe retries or our own re-enqueue? (unverified)
```

没有 500 行的上下文倾倒。主题交接入口在 `work/<topic>/index.md`；长设计和计划文件只有被这个 index 指向时才读。可复用的未来行为在 `knowledge/`，通过扫描路由头发现，正文按需加载。

### work/&lt;topic&gt;/ —— 主题工作包

每个进行中的工作都是一个目录，只有一个稳定入口文件，其它都是按需支撑材料：

```text
work/<topic>/
  index.md      # 主题交接：状态、下一步、进度、读取指针
  design.md     # 可选：长设计 / spec
  plan.md       # 可选：当前计划
  plans/        # 可选：分阶段、备选或已废弃计划
```

preflight 在你选择主题前停在 `cockpit.md`。选择后只先读该主题的 `index.md`。`index.md` 说明现在要读什么、什么条件下才读、哪些进度已完成、下一步是什么。

### 路由头 —— 唯一的约定

每个知识文件以一个小头部开场，以 `---` 结束：

```markdown
# <title>          (坑用 # ⚠ <title> · 流程用 # <X> checklist)

SUMMARY: <一行 —— 这份文件装了什么>
READ WHEN: <什么时候路由到这里才对>

---

<自由散文正文>
```

路由只读头部（便宜）。标题字形编码了类型，所以没有 `kind` 字段、也没有「一类一文件夹」—— 知识改为按**域**嵌套，目录树本身就是索引。

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

你不用手动搭 deck —— 跑一次 `/flightdeck:launch`，它直接把骨架写出来。

## 用法

**会话开始** —— 运行 `/flightdeck:preflight`。它：

1. 加载协议、读 `flightdeck/cockpit.md`（外加 `briefing.md`）。
2. 扫路由头地图（便宜的一行头），再按需加载 body —— 按各头的 `READ WHEN:` 排序，约束性约定常驻前台、reactive trap 等症状出现才拉。
3. 瞥一眼 `git status` —— 仅在明显不对时给一行被动提示，绝不阻塞式追问。
4. 报告可继续项并询问要恢复哪个。你选择前，它不读主题文件，也不读知识正文。

全新项目（没有 `cockpit.md`）则 preflight 指引你去 `/flightdeck:launch`：做个快速检查后播种骨架（没 repo 时问一句 `git init` —— 零丢失保证需要 git）。

**会话结束** —— 没有要记的东西。一轮产出了真实增量时，flightdeck 自己 **persist**：扫描这一回合的产出、把过了写入门控的写进 `knowledge/`，重写当前主题的 `index.md`，把 `cockpit.md` 重写到当下，做一次本地 commit。纯对话、啥都没改的一轮不提交。下一次会话 —— 哪怕换个 AI 或换个人 —— 都能从这里精确接上。

### 命令

| 命令 | 用途 |
| --- | --- |
| `/flightdeck:preflight` | **会话入口接管** —— 加载协议，读 `briefing.md` 和 `cockpit.md`，扫描知识头部，列出可继续项，并等你选择后才读取主题 `index.md`。不会自动触发；不跑它就等于 flightdeck 没接管。 |
| `/flightdeck:launch` | **首次建 deck** —— 播种骨架（`cockpit.md` + `briefing.md` + `work/` + `knowledge/`）。没 repo 时问一句 `git init`。deck 已存在则拒绝。 |
| `/flightdeck:walkaround` | **完整性审计与修复** —— 一个按需的漂移巡检，针对新形态没有机制自纠的部分（cockpit 对不上现实、主题工作包形状不规范、孤儿 work、重复 trap、缺路由头、knowledge 根目录堆积）。机械问题直接修，可能丢语义的问题只提议。 |

**persist** 是第四个动词，但它不是命令 —— 它在任何执行回合末尾自动跑（扫描知识、重写 cockpit、commit）。`commit` 是**本地自动、push 才先问**（本地 commit 可逆；push 是受控关卡）。会话开始不加载任何东西，也没有后台进程。

### 路由 —— 什么触发什么

| 当下情形 | AI 去读 |
| --- | --- |
| 会话开始 /「我们刚在干嘛？」 | `briefing.md` + `cockpit.md` + 知识头部 |
| 已选择的一项进行中工作 | 先读 `work/<topic>/index.md`，再只读 `## Read now` 或命中的 `## Read if` |
|「迁移为啥挂了？」 | `knowledge/<域>/` 下的 `# ⚠` trap |
|「测试怎么跑？」 | `knowledge/<域>/` 下的 `# … checklist` |

## 配置

`flightdeck/briefing.md` 是按项目的控制面板 —— 单一、稳定、人维护、进场时读。无 frontmatter、无结构化字段；两段：

```markdown
## Conventions
deck 局部约定 + AI 按你自然话维护的行为规则，如 "发布面一律英文"、"commit 前先问我"。省略 = 默认。

## Subscriptions
每行一个 ~/.flightdeck 相对路径 —— 这个 deck 拉进的共享知识；空 = 不订阅
```

一切靠**推断或 skill 判断** —— git 由是否有 `.git` 目录推断，其余由协议决定。要改某个行为，**直接用自然话告诉 AI 一条持久偏好** ——「commit 前先问我」「别自动 start 工作」—— AI 会在 `## Conventions` 下追加一条自由文规则（注明来源 + 日期）并高于默认执行。没有要记的 magic-string 开关目录。

## 跨项目共享知识

有些流程和参考文档并不专属某个项目 —— 一份 commit message 清单、一份注释风格指南 —— 你希望在所有 deck 之间共用一份。flightdeck 用 `briefing.md` 里的 **`## Subscriptions`** 清单来处理：

- **Subscriptions** —— 每行一个 `~/.flightdeck` 相对路径。目录项订阅其整棵子树。进场时 preflight 把订阅的全局文件折进路由树，与本地 `knowledge/` 并列。
- **冷存层作共享库** —— 全局知识住在 `~/.flightdeck/knowledge/`。想放别处？把这个路径做成符号链接，Windows 上用目录联接（`mklink /J %USERPROFILE%\.flightdeck <target>`）。
- **全局知识也按域组织** —— 新共享知识放 `~/.flightdeck/knowledge/<domain>/...`。旧的根目录全局文件可继续作为订阅兼容路径，但不要继续扩大根目录堆积。
- **主题恢复依赖留在本地** —— 全局知识可以参与发现和判断，但 `work/<topic>/index.md` 不应直接指向 `~/.flightdeck/knowledge/...`。如果某个主题恢复时必须依赖一条共享知识，先把相关内容落到项目本地 `flightdeck/knowledge/<domain>/...`，再让主题 index 指向本地文件。
- **本地遮蔽全局** —— 项目若在同一相对路径有自己的文件，本地的整份胜出（替换，非合并）—— 确定、零维护。
- **下发（vendoring，可选）** —— 需要仓库自包含时，把订阅的全局文件快照进仓库当冻结副本、并撤掉订阅。默认是活订阅、不拷贝。

`## Subscriptions` 为空的 deck 从不碰全局库，可独立工作。

## 为什么需要它

多数「AI memory」方案的失败在于什么都存 —— 信号淹没在垃圾抽屉里。flightdeck 反着来：**严格写入门控**（只存会改变未来决策、或你会再查的东西）、**位置即状态**（topic package 在项目里就是活的，移进冷 archive 就是完成，停在 ideas 里就是未启动 seed）、一行**路由头**让知识无需全量倾倒就能被找到、以及每回合提交的**零丢失恢复载荷**（`cockpit.md` + `briefing.md` + 每个 active topic 的 `index.md` + `knowledge/`）。它是纯 markdown —— 能在 review 里 diff、在终端 grep，还能扛过模型升级或 AI 工具切换。

> ✨ 语义清晰高于主题统一 —— 航空隐喻只在能让意图更清晰处使用，绝不当成主题。

## 横向对比

flightdeck 与 [AGENTS.md](https://agents.md) 互补 —— 用 `AGENTS.md` 放静态规则，让 flightdeck 处理裸记忆工具没有的跨会话生命周期：

| | flightdeck | [AGENTS.md](https://agents.md) | Cline Memory Bank | OpenSpec | Cursor MDC | Letta Code |
| --- | --- | --- | --- | --- | --- | --- |
| 静态项目规则 | 用 AGENTS.md | ✅ 原生 | — | — | ✅ | — |
| 跨会话接续 | ✅ | — | ✅ | — | — | ✅ |
| 位置即状态生命周期（work ↔ 冷存） | ✅ | — | — | ✅ | — | — |
| 严格写入门控（防垃圾抽屉） | ✅ | — | — | — | — | — |
| 坑/教训追踪（根因） | ✅ | — | — | — | — | — |
| 懒路由（grep 头部，不全量倾倒） | ✅ | — | — | — | — | — |
| 单一显式入口（`/preflight`） | ✅ | — | — | — | — | — |
| 工具无关（markdown + 文件系统） | ✅ | ✅ | 部分 | ✅ | 仅 Cursor | — |

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

[AGENTS.md](https://agents.md) 是*静态*项目规则的跨工具标准 —— 每次会话加载、很少变。flightdeck 是它之上的*动态*层：跨会话接续、防垃圾抽屉的写入门控、坑追踪。两者可组合 —— 留着你的 `AGENTS.md`，再加一个 `flightdeck/` deck。如果你只需要一份静态规则清单，单用 AGENTS.md 就够了。

</details>

<details>
<summary><b>我有个旧的 <code>flightdeck/</code> —— 怎么升级？</b></summary>

这次重写**没有**自动迁移机制。要把旧 deck 升级到当前形态，跑 `/flightdeck:walkaround` —— 它会把 deck 修复成当前形状（并迁移旧结构：`INDEX.md`、frontmatter、kind-folder），保留你的内容。或用 `/flightdeck:launch` 新建，再把还想要的 `cockpit.md` 内容和知识文件手工搬过来（每份补一个路由头）。

</details>

## 文档

**协议参考**（canonical，AI 向）：进场加载的 micro-core 在 [skills/preflight/SKILL.md](skills/preflight/SKILL.md)；按需细节在 [concepts.md](skills/preflight/concepts.md)（定义）+ [operations.md](skills/preflight/operations.md)（操作）。历史见 [CHANGELOG.md](CHANGELOG.md)。

## 贡献

最高信号的贡献：一份 AI 偏离协议的 transcript（整套设计要防的就是这个失败模式），或某个 Codex / Cursor / Gemini manifest 的端到端验证日志（[模板](.github/PULL_REQUEST_TEMPLATE/manifest-verification.md)）。

## Roadmap

一个 "continuance" 基准（给 AI 一个半截项目的 deck、说"继续"、量化恢复质量）· 冷存合成/压缩 · 未测适配器的端到端验证 · MCP server。完整历史见 [CHANGELOG.md](CHANGELOG.md)。

## 致谢

- [AGENTS.md](https://agents.md) —— 纯 markdown 约定
- [superpowers](https://github.com/anthropic-experimental/superpowers) —— 协议 / skill 风格
- [Cline Memory Bank](https://docs.cline.bot) —— 启发写入门控的那个模式

## License

[MIT](LICENSE) © 月离 (Yuelioi)

---

<div align="center">

如果 flightdeck 帮你省下了一个上下文窗口，[给个 star](https://github.com/Yuelioi/flightdeck/stargazers)。

</div>
