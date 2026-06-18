---
name: sync
description: Use when explicitly syncing this deck's vendored shared-knowledge files (a checklist/doc carrying `synced_from`) against their master deck — pulls upstream-changed bodies, preserves the reserved project-specific section + routing frontmatter, and surfaces drift it can't auto-resolve. Triggered by `/flightdeck:sync`.
---

# Flightdeck Sync — vendored shared-knowledge refresh

母库（master deck）是共享知识的唯一真相源；本仪式把消费 deck 里 vendored 的副本按母库刷新。**谁新谁赢**（比 `last_updated`，无 hash）。AI 干合并；`flightdeck_index.py --sync-status` 算事实。

## 母库解析（master resolution）

1. 读消费 deck `rules.md` frontmatter 的 `shared_master`（一个 env 引用，如 `$FLIGHTDECK_SHARED_MASTER`）。
2. 展开 env 变量 → 母库 deck 根。
3. （Claude 便利回退）env 未设时，查用户全局 CLAUDE.md 的跨项目资产库根。
4. 仍解析不到 → 本机没有母库：每文件吐 `master-missing`、**优雅跳过**并报告；vendored 文件本身是自洽真文件，照常可用。

## 两个模式

### A. 再同步全部（裸跑 `/flightdeck:sync`）

1. 跑 `flightdeck_index.py <deck> --sync-status` → 每个 vendored 文件一行 `state<TAB>path<TAB>synced_from`。
2. 逐状态处理：
   - `upstream-changed` → 打开母库源 + 项目副本：**用母库正文替换共享正文；逐字保留项目的 `## 项目覆盖` 段 + 整个 frontmatter；把 `last_updated` 戳成母库的。** 绝不动 `when_to_read` / `applies_to`。
   - `in-sync` → 跳过。
   - `locally-ahead` → 跳过 + 报一句「项目这份比母库新，可能想回流母库」（MVP：只报，不自动回流）。
   - `dangling` → 报告（母库源已删），问用户：删本地副本 / 保留 / 改指。
   - `master-missing` → 报告一次、全跳（本机没母库）。
3. regen INDEX：`flightdeck_index.py <deck>`。
4. 出 banner。

### B. 首次下发（`/flightdeck:sync <母库相对路径>`）

1. 解析母库根；读 `<母库相对路径>` 处的母库文件。
2. 整文件拷贝（frontmatter + 正文）进消费 deck 的**同一相对路径**（母库 `checklists/commits.md` → deck `checklists/commits.md`）。
3. 往其 frontmatter 戳 `synced_from: <母库相对路径>`。
4. 按需本地化路由（项目可改 `when_to_read` / `applies_to`）；项目专属补充另起 `## 项目覆盖` 段。
5. regen INDEX。

## `## 项目覆盖` 约定

vendored 文件的项目专属补充写在一个保留标题段下（`## 项目覆盖`，或本 deck 语言的等价标题，如 `## Project-specific`）。sync **永不覆盖**该段下任何内容。该段**之上**（共享正文）归母库所有，`upstream-changed` 时被刷新。

## Don't do

- 不碰没有 `synced_from` 的文件（本地原创）。
- 不覆盖 frontmatter，也不覆盖 `## 项目覆盖` 段。
- 不自动把 `locally-ahead` 改动回流母库（MVP）。
- 母库缺席不硬失败 —— 优雅 no-op。

## Report

末尾统一 banner（先正文后 banner、一回合一个）：

```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · K locally-ahead · D dangling
[Master]  <已解析母库根>   (或 "master-missing — rules.md 的 shared_master（如 $FLIGHTDECK_SHARED_MASTER）未设/未解析，已跳过")
```
