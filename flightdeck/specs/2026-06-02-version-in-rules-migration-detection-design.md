---
status: done
summary: 版本号从 cockpit Layout 行搬进 rules.md（rules.md 转必选、三件套最小契约）；MIGRATION.md current + layout_need_update 驱动迁移检测
last_updated: 2026-06-03
supersedes: landed/specs/2026-06-01-layout-version-migration-detection-design.md
related: [specs/2026-06-02-metadata-model-consolidation-design.md, landed/specs/2026-06-02-soft-config-model-invocation-design.md]
---

# 版本号收进 rules.md + 三件套最小契约 + MIGRATION.md 驱动迁移检测

**日期**：2026-06-02
**来源**：dogfood 中作者自查 —— 插件已发 v2.1.0，但 cockpit 头部仍显示 `**Layout**: 1.2`，"为什么没更新成功？"的疑惑连作者本人都会产生，真实用户只会更懵。
**状态**：pending（设计定稿，待开 plan 实现）
**取代**：`landed/specs/2026-06-01-layout-version-migration-detection-design.md`（layout-version 计数器 + cockpit `Layout` 行的方案被本设计整体替换）
**修订**：`landed/specs/2026-06-02-soft-config-model-invocation-design.md` 的「rules.md 可选」口径（见下文 §4）

---

## 1. 问题

存在两个独立的版本号，且其中一个被裸露在操作仪表盘上：

| 版本号 | 含义 | 现在住哪 | 现值 |
| --- | --- | --- | --- |
| 插件 / 发布版本 | flightdeck **工具**本身（skills、manifest、CHANGELOG） | `.claude-plugin/plugin.json`、CHANGELOG 等 | v2.1.0 |
| Layout 版本 | 每个 deck 的**目录 / frontmatter schema** 版本 | 各 deck 的 `cockpit.md` 头部 `**Layout**` 行 | 1.2 |

两者**故意解耦**是对的（加法式发布不该强制迁移），但把"迁移 schema 版本"这个内部数字直接摆进 cockpit，制造了"我的 deck 是不是没更新"的错觉。问题不在解耦，在**呈现**：不该把一个永远落后于安装版本的数字单独裸露给用户。

## 2. 设计

### 2.1 版本号搬家：cockpit 不再挂 `Layout`，改由 rules.md 持有 `version`

- 删除 `cockpit.md` 头部的 `**Layout**: <ver>` 行。
- `rules.md` 新增 `version: <发布版本>` 字段，记录**本 deck 当前对齐到的发布版本**（如 `2.1`）。
- `rules.md` 是每个入场 skill 的第一读，版本判定不增加任何额外读取。

### 2.2 rules.md 升为必选：三件套最小契约

为保证 `version` 永远有家（裸 cockpit 的 deck 也能被迁移检测识别），最小契约从「仅 cockpit.md」升为三件套：

> **最小契约 = `rules.md`（配置）+ `cockpit.md`（看板）+ `landed/HISTORY.md`（历史）**

- first-time setup 在两问访谈（Active focus + 首个 next 项）之外，**非交互**地写入：默认值 + 当前 `version` 的 `rules.md`，以及只有表头的空 `HISTORY.md`。用户感知摩擦基本不变。
- 「裸 cockpit 几乎无迁移问题」成立（迁移风险随结构量增长），故无需为此情况保留 fallback —— 直接钉死契约更干净。

### 2.3 迁移策略改由 MIGRATION.md 元数据驱动

MIGRATION.md frontmatter 随插件发布，携带两个字段：

```yaml
---
current: 2.1            # 插件当前发布版本
layout_need_update: []  # 引入过布局迁移的版本白名单；1.2 起全是加法，故现为空
---
```

判定语义（preflight step 2 / walkaround Audit 10 加载时读这一小块元数据即可，token 几乎不花）：

```
deck.version (rules.md) vs current (MIGRATION.md):
  ==                                                   → 静默放行
  deck < current 且 ∃ v ∈ layout_need_update, deck < v ≤ current
                                                       → 提示迁移（指向 MIGRATION.md 对应段），用户确认前不动
  deck < current 且 不落后任何 layout_need_update 项    → 静默把 rules.md 的 version 顶到 current
```

- 现状校验：所有 1.2 / 2.0 / 2.1 的 deck，`layout_need_update` 为空 → **谁都不会被提示**（上一次真正的布局破坏是 1.1→1.2，早于本体系）。
- 将来若 3.0 改布局：往 `layout_need_update` 加 `3.0`，仅 `< 3.0` 的 deck 被提示，3.0 起的新 deck 不会误触发。

### 2.4 已决：`current` 住 MIGRATION.md，不读 plugin.json

一次元数据读同时拿到 `current` + `layout_need_update`，迁移策略单一权威源（MIGRATION.md 本就是"什么变了、什么要迁"的文档），skill 不必再硬编码 `last-breaking` 常量。

## 3. `layout_need_update` 白名单的对称代价 + 缓解

白名单（列"真正要迁的版本"）优于黑名单 `layout_skip`（列"可跳过的版本"）：破坏性改动稀少 → 列表短；默认不迁；忘记登记加法版本**不会**误报。

代价（须认下）：忘记登记一个**破坏性**版本 = deck 静默跑在不兼容布局上（漏报，比误报更阴）。缓解：发布破坏性改动时本就要写 MIGRATION.md，把"破坏性布局变更 → 追加到 `layout_need_update`"钉进 `checklists/version-bump.md` 发布清单即可堵住。

## 4. 存量 deck 迁移路径

本设计落地本身即一次迁移事件：

- **deck 有 cockpit 但无 rules.md**（1.2 / 2.0 老 deck）→ preflight 一次性提示"补建 `rules.md`?（stamp 到当前 version）"，非破坏性；确认后写入默认 rules.md + 当前 version，并删除 cockpit 的 `Layout` 行（或在迁移时静默移除）。
- 因 rules.md 由可选升为必选，`soft-config-model-invocation` spec 中「无 rules.md = 默认」的口径改为：**文件必选**；但*字段*省略仍走默认（变的是"文件在不在"，不是"字段缺不缺"）。

## 5. blast radius（实现时逐一处理）

- `skills/preflight/templates.md` —— rules.md 模板加 `version`；rules 规则段把"Optional file"改为"必选 + 三件套"；cockpit 模板删 `**Layout**` 行 + 改 §Rules 中 `Layout` 说明；MIGRATION.md 模板（若有）加 `current`/`layout_need_update`。
- `skills/preflight/SKILL.md` —— step 0 最小契约判定从「cockpit 存在」改为「三件套」；step 2 改读 rules.md `version` + MIGRATION.md 元数据，按 §2.3 判定；补存量迁移提示。
- `skills/preflight/protocol.md` —— 数据模型 / 最小契约 / 迁移检测描述同步。
- `skills/walkaround/SKILL.md` —— Audit 10 从读 cockpit `Layout` 改为读 rules.md `version` + MIGRATION.md；Audit 8 已知 root 入口已含 rules.md（确认）；Audit 5/契约相关项同步。
- `skills/landing`、`skills/status`、`skills/emit-agents-md` —— 凡引用 `Layout` 或最小契约处同步。
- `scaffolds/**` —— full / minimal 脚手架补 rules.md（带 version）+ HISTORY.md；删 cockpit `Layout` 行。
- `MIGRATION.md` —— 加 frontmatter（`current` + `layout_need_update`）；补一节描述本次（版本号搬家）的存量迁移步骤。
- `checklists/version-bump.md` —— 发布清单加两条：bump MIGRATION.md `current`；破坏性布局变更时追加 `layout_need_update`。
- `README.md` / `README.zh.md` —— 凡讲 `Layout` / 最小契约 / 迁移检测处同步。

## 6. 非目标

- 不改插件 semver 规则本身（仍按发布节奏走）。
- 不在本设计内改任何**实际**布局 schema —— 布局仍是 1.2，本设计只搬版本标记、改检测机制。
- 不引入自动迁移：所有迁移仍须用户确认（沿用"绝不静默迁移"）。
