---
status: done
---

# 单入口塌缩：preflight 取代 workflow（删除自动加载）

**日期**：2026-06-02
**一句话定位**：删掉自动加载的 `workflow` skill 与整个 SessionStart hook，把协议知识并入 `preflight`；`/flightdeck:preflight` 成为唯一入口——无 cockpit 则初始化、有则照常只读对账。flightdeck 从「环境自动」转为「显式手动」，`flightdeck/` 目录布局（Layout 1.2）不变。

> 本 spec 已纳入两份外部审阅（`debriefs/claude.txt`、`debriefs/gpt.txt`）的处置结果，见各节标注。

## 1. 动机

### 1.1 双入口已产生「两个真相」——首要动机

`workflow`（每会话 hook 自动注入）与 `preflight`（显式 `/preflight`）在同一套入口逻辑（读 rules → 读 cockpit → git 四项对账 → 14 天 staleness）上**各维护一份副本**，且已经在**用户可观察的行为**上 drift：

- **空 Next session 的 fallback 不一致**：`workflow/SKILL.md` 搜 `specs/` + `plans/`（active/pending）再 `sketches/`；`preflight/SKILL.md` 只搜 `plans/`（+ done-未-land 提示去 land），**未提 `specs/`**。→ **同一状态、两套逻辑、两个结果。**
- **stale 交叉引用 bug**：`workflow/SKILL.md` 的 First-time setup 声称 bootstrap「typically because the user typed `/flightdeck:preflight`」，但实际 bootstrap 入口是 `/flightdeck:workflow`，且 `preflight` 根本无 bootstrap 逻辑。

这已不是维护成本问题，而是系统存在 **two sources of truth**。因此「删掉一个入口」优于「永远同步两个入口」。

> 补充（写入 MIGRATION，解释「为何删 > 合并」）：auto-load 在本会话已手动 `/preflight` 过时，仍会重复执行部分对账 = **double-run**，而非互补。

### 1.2 自动加载对实际用法零收益——次要动机

维护者长期使用中**从未主动打过 `/workflow`**，每次都显式 `/preflight`；auto-load 注入的「执行 item #1」从未被采用（preflight 的 report-and-stop 才是真实入口体验）。auto-load 的成本（每会话注入整个 SKILL、双份逻辑维护、迁移检测只落在 explicit 路径形成割裂）持续存在，对该用法收益为零。

### 1.3 结论

合并为单一显式入口，删除 auto-load，顺带消除 §1.1 的 drift 与 bug。

## 2. 设计决策

| 决策 | 取舍 |
|---|---|
| **唯一入口 = `/flightdeck:preflight`** | 无 cockpit → 初始化；有 → 只读对账 + catalog + 报告（现状不变） |
| **删除 `workflow` skill** | 协议知识并入 `preflight`（见 §3.2）；companion 迁至 `skills/preflight/` |
| **`/flightdeck:workflow` 彻底删除** | 调用即 unknown command；由 MIGRATION.md 指向 `/preflight`。不保留 shim（低采用期，clean 优先） |
| **删除整个 hook（无 breadcrumb）** | 新用户 onboarding 完全靠文档；日后如需 hint hook，重建成本低 |
| **其余 skill 保持独立、自足** | `landing` / `walkaround` / `emit-agents-md` 各自显式加载所需 companion，不依赖 preflight 已跑 |
| **Layout 不变（仍 1.2）** | 本次只改 skill 架构，不动 `flightdeck/` 目录结构；用户 deck 无需迁移 |
| **工具版本 → 2.0.0** | 破坏性（移除 skill + 自动加载）；与已废弃的 work-items 2.0 无关，CHANGELOG 措辞须区分 |

## 3. 机制

### 3.1 preflight 新增 branch-0：init-or-read（严格依赖链）

**硬规则：Layout 检测绝不能早于 deck 存在性判断**（Layout 行存在于 cockpit，而 cockpit 属于 deck）。存在性判断以 **`cockpit.md` 是否存在**为准（不是目录是否存在）——`cockpit.md` 才是 flightdeck 的最小契约，这样同时覆盖「目录都没有」与「目录在但半初始化（手动建了目录没跑 setup）」两种缺失。

判断链伪代码（plan 须照此实现）：

```
branch-0  (MUST run first)
read presence of flightdeck/cockpit.md:
  if NOT exists:                      # 含「无目录」与「半初始化」两种
      run First-time setup interview
      → write cockpit.md (with **Layout**: 1.2)
      → STOP   (下次 /preflight 走读路径)
  else:
      → layout 检测            (依赖 cockpit 存在)
      → 读 root INDEX + cockpit
      → git 对账
      → 加载 catalog
      → 报告 item #1
      → STOP
```

bootstrap 后立即结束（不自动续读）——与 preflight 既有的 report-and-stop 风格一致；自动续读会引入「刚写完又读 / 状态切换 / 分支复杂化」，收益不大。两份审阅均认可此选择。

### 3.2 协议知识的家：新增 `protocol.md`，SKILL 只留操作

为避免「workflow 300 行搬家成 preflight 400 行」，协议知识**不塞进 SKILL.md**，而是新建 `skills/preflight/protocol.md` 承载。目标结构：

```
skills/preflight/
 ├─ SKILL.md            # invocation + checklist + branch-0 + routing summary + companion 索引
 ├─ protocol.md         # 原 workflow 协议知识：Core principle / Data model / Status / INDEX /
 │                      #   Folder map / Authority order / Lifecycle / Write gate /
 │                      #   Incident promotion gates / Common mistakes
 ├─ folder-semantics.md # 从 workflow/ 迁入
 ├─ templates.md        # 从 workflow/ 迁入
 └─ exit-ritual.md      # 从 workflow/ 迁入
```

**切分原则**：SKILL.md 只留「操作」（怎么跑这次入场）；「概念/协议」一律进 `protocol.md`。**量化上限：SKILL.md 正文 ≤ ~300 行**，超出即把更多概述移入 `protocol.md`，防止实现时「差不多还好」一路不下沉。

### 3.3 删除 hook 与 workflow 命令

- 删 `hooks/session-start`、`hooks/run-hook.cmd`、`hooks/hooks.json`（仅含一个 SessionStart hook）；hooks/ 清空后删目录。
- 三个 plugin manifest 移除 hook 注册与 `workflow` skill 注册；保留 `preflight` / `landing` / `walkaround` / `emit-agents-md`。`/flightdeck:workflow` 随 skill 删除而失效（unknown command）。

## 4. 受影响组件（供 plan）

- `skills/preflight/SKILL.md` — branch-0 init-or-read（§3.1）+ **统一 fallback**（合并 `specs/`+`plans/`+`sketches/`，修复 §1.1 分歧）+ routing summary + companion 索引；正文 ≤ ~300 行。
- `skills/preflight/protocol.md` — **新建**，承载原 workflow 协议知识（§3.2）。
- `skills/preflight/{exit-ritual,folder-semantics,templates}.md` — 从 `workflow/` 迁入。
- `skills/workflow/` — 删除整个目录。
- `skills/landing/SKILL.md`、`skills/walkaround/SKILL.md`、`skills/emit-agents-md/SKILL.md` — 所有 `../workflow/...` 链接 → `../preflight/...`；逐一确认自足。
- `hooks/` — 删除（session-start / run-hook.cmd / hooks.json）。
- `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.cursor-plugin/plugin.json` — 去 hook + 去 workflow skill 注册。
- `README.md` / `README.zh.md` — 重写 pitch（去「auto-loads / 自动加载」叙事）、Slash 命令表（删「✅ 自动加载」行 + workflow 行）、Getting started、架构 Mermaid 图（去 hook / auto-load 边）、对比表「Skill 自加载触发」行。
- `GEMINI.md`、`AGENTS.md`（若有 workflow / 自动加载提及）、`adapters/*/README.md` — 同步。
- `install.ps1` / `install.sh` — 若安装/连接 hook，移除该步。
- `MIGRATION.md` — 增「1.3 → 2.0」段，含**影响清单表**：

  | 项目 | 是否受影响 |
  |---|---|
  | deck 数据 / Layout / cockpit | 无 |
  | slash command（`/workflow` 失效） | 有 |
  | auto-load 行为（SessionStart 注入消失） | 有 |

  并明确一句：*依赖自动 SessionStart 加载的用户，2.0 起必须在会话开始显式运行 `/flightdeck:preflight`*（否则会觉得「升级后怎么没反应了」）。再补一句解释「为何删 > 合并」（§1.1 的 double-run）。
- `CHANGELOG.md` — `## [2.0.0]`，措辞明确「entry collapse」并与已废弃的 work-items 2.0 切割。
- `VERSION` — `2.0.0`。
- `TEST_PLAN.md` — 入口行为用例（单入口 init-or-read；无 hook）+ §6 的删除断言组。
- `scaffolds/**` — **全量** grep `skill: workflow` / `workflow` 文案（不止 `scaffolds/full/`），逐处改为 preflight。

## 5. 非目标

- 不改 `flightdeck/` 目录结构 / Layout 版本（仍 1.2）。
- 不改 landing / walkaround 的核心逻辑（只重指路径 + 确认自足）。
- 不保留任何 breadcrumb / hint hook，也不保留 workflow 命令 shim（日后按反馈再单独议）。

## 6. 风险与验证

- **手动-only 的可发现性**：新用户装完若不打 `/preflight` 则无任何动静。缓解：README 头部明确「唯一入口是 `/flightdeck:preflight`」；MIGRATION 影响表 + 显式提示；低采用期文档即 onboarding。已显式接受。
- **companion 路径迁移遗漏**（`../workflow/...` 残链）：**每改完一个 skill 文件即跑一次局部路径断言**，不留到最后统一验。收尾再跑全局：`rg -l "skills/workflow|\.\./workflow" skills/` 应无命中。
- **「概念删除」最易漏文档**：收尾跑一组删除断言——`rg -n "workflow|SessionStart|session-start|auto-load" .`，**仅允许命中** `CHANGELOG.md` / `MIGRATION.md` / `landed/`，其余命中即失败。

## 7. 待 plan 细化

- 统一后的空-Next-session fallback 精确措辞（`specs/` + `plans/` + `sketches/`，保留 done-未-land 提示去 land）。
- `protocol.md` 与 `SKILL.md` 的精确切分（哪些段进 protocol、SKILL 索引怎么写），并核对 SKILL ≤ ~300 行。
- CHANGELOG 2.0 措辞与「work-items 2.0 已废弃」的明确切割。
