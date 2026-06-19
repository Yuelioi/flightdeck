---
status: active
when_to_read: 改 cockpit 字段结构/角色、Key Context 或 Pending Review 的生命周期、或 cockpit 相关 skill 散文之前
applies_to: [skills/preflight/exit-ritual.md, skills/preflight/templates.md, skills/preflight/protocol.md, skills/landing/SKILL.md, skills/walkaround/SKILL.md, scripts/flightdeck_index.py, scaffolds/full]
when_to_update: cockpit 字段集变化、Key Context/Pending Review 生命周期机制改动、In Progress 渲染规则改动、或 pointer-vs-record 原则调整时
last_updated: 2026-06-19
summary: cockpit 设计当前真相：纯恢复载荷原则（pointer-vs-record）、字段结构与角色（Updated/Focus/Pointers/Next/In Progress/Key Context/Pending Review/Hanging）、Key Context 中转暂存（drain/graduate）+ Pending Review aged-prompt 生命周期、home-by-kind（agent 中立）。
---

# Cockpit 设计：纯恢复载荷 + 字段角色 + accumulator 生命周期

> 当前真相（current truth）。由 `2026-06-19-cockpit-field-redesign` + `2026-06-19-cockpit-accumulator-convergence` 两 spec 毕业合并而来——同一北极星原则的两条轴。操作真相在各 skill；本 doc 是契约 + 设计依据。

## 北极星原则：cockpit = 纯恢复载荷

**cockpit 只物化「别处没有的判断」+ 一份廉价投影；记录住在各自的家，cockpit 只放链接。** 记录的家：历史 → `git log`、进度 → plan `## Progress`、目标/判据/方法 → spec body、耐用不变量 → `rules.md`、知识 → folder INDEX。

实证根据（三个真实 3.0 cockpit）：叙述字段（旧 `Last updated` 括号 / `Active focus` / `Next`）会漏入工作记录（changelog / 目标判据 / 进度日志），每仪式加载 = 主 token 黑洞；`In Progress` 反而干净（AUTO 投影，长仅因 summary 长）。

## 字段结构与角色（真相源 = `exit-ritual.md` §Cockpit update + `templates.md`）

字段顺序：`Updated · Focus · Pointers · ## Next · ## In Progress · ## Key Context · ## Pending Review · ## Hanging Tasks`。

- **`Updated`** — 纯戳 `Updated: <date> · <who> · Stage: <stage>`，**无 changelog**（历史归 git）。
- **`Focus`** — 一行线程标签 + 当前 spec/plan 链接，≤~100 字；**无目标/判据/方法**（归 spec body，不变量归 rules）。
- **`Pointers`** — 薄导航锚点（config/conventions/INDEX/archive），hand-maintained，非 AUTO；只放跳转、不放内容。
- **`## Next`** — 单个下一步 + plan 链接；**进度清单/依据/里程碑链接归 plan `## Progress`**。
- **`## In Progress`** — AUTO，`status:active` spec/plan 投影；渲染 **summary 截断头部（≤80 字 + …）**，全文留 spec。preflight 正常路径不读 specs/INDEX，靠这份廉价投影。
- **`## Key Context` / `## Pending Review` / `## Hanging Tasks`** — 见下生命周期。

**密度 + 角色越界检查（landing §Length check，门控 trim）**：80 行硬顶；逐字段越界（Updated 含 changelog · Focus 段落化 · Next 含进度）→ 把越界内容路由回家。walkaround **Audit 16** 非阻塞浮出字段结构/角色 conformance。

## Key Context = 中转暂存区（不是任何东西的永久住址）

承重字面量供下次会话恢复；**没有东西永驻**，两个出口（landing 时走）：

- **Drain（近确定性）**：条目 referent（指向的 spec/plan/incident）本会话 archived/graduated/done → 死指针 → 自动 drop（landing 报告列出，可 undo），活细节挪去 specs。
- **Graduate（判断，与 spec 毕业同质）**：耐用、不指向会死件的条目（standing 原则/约定/常驻事实）→ 毕业到 home-by-kind，从 cockpit 删。耐用原则不指向会死件 → 天然不被 drain 碰；graduate 防它原地腐烂。**无 pin、无原地保护、无按年龄过期**（年龄对 Key Context 是错触发，会误杀耐用原则）。

### home-by-kind（毕业目标，agent 中立）

| 耐用条目类型 | 毕业去 | 理由 |
|---|---|---|
| 行为红线 / 约定 | `rules.md` | 每仪式全文读，最响，agent 中立 |
| 设计依据 / 决策 | `docs/`（when_to_read 路由） | 碰到才浮出，不占常驻预算 |
| 常驻项目 meta | 项目的 agent 指令文件（`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`，按运行的 agent） | 每会话常驻，克制使用 |

**多 agent 红线**：绝不把「agent 指令文件」写死成 CLAUDE.md；override 权威序 = 项目 agent 文件 > deck `### Rules` > 默认。`rules.md` 与 agent 文件是常驻预算，多数耐用 Key Context 是「碰到才需要」的设计依据，归 `docs`。

## Pending Review = 签收队列 + aged-prompt

AI 自判 `done`、待人签收的工作 + 浮出的 stale `pending-review` 注记。非阻塞、主观（人签收，区别于客观 `verify:` 扫描）。drain on sign-off。**Aged-item forcing function**：跨 ≥1 个 landing 仍未签收的条目，landing 逐条逼问（sign off / keep / drop）——签收仍显式（绝不自动删），只防队列腐烂成杂物抽屉。

walkaround Audit 14 已覆盖 referent-died / 超长 Key Context（非阻塞 INFO），故无需新 audit。

## 落地面（操作真相）

- `skills/preflight/exit-ritual.md` §Cockpit update / Accumulator-drain / Length check — 字段角色 + 生命周期 + 越界检查真相源。
- `skills/preflight/templates.md` — cockpit 模板 + 字段 Rules + summary 上限。
- `skills/preflight/protocol.md` — pointer-vs-record 边界 + 字段语义。
- `skills/landing/SKILL.md` Step 8 — drain/graduate/aged-prompt 执行面。
- `scripts/flightdeck_index.py` — In Progress summary 截断渲染（`_truncate_inprogress_summary`，≤80）。
- `skills/walkaround/SKILL.md` Audit 16 — 字段结构 conformance。
- `scaffolds/full/flightdeck/cockpit.md` — 新 deck 出场即新结构。
