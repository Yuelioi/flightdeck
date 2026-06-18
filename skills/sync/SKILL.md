---
name: sync
description: Use when explicitly syncing this deck's vendored shared-knowledge files (a checklist/doc carrying `synced_from`) against their master deck — pulls upstream-changed bodies, preserves the reserved project-specific section + routing frontmatter, surfaces drift it can't auto-resolve, and `push <path>` reverse-adds a local file up to the master (promote / backflow). Triggered by `/flightdeck:sync`.
---

# Flightdeck Sync — vendored shared-knowledge refresh

母库（master deck）是共享知识的唯一真相源；本仪式把消费 deck 里 vendored 的副本按母库刷新。**谁新谁赢**（比 `last_updated`，无 hash）。AI 干合并；`flightdeck_index.py --sync-status` 算事实。

## 母库解析（master resolution）

按序、先命中为准（前两步即脚本 `_resolve_master_root`）：
1. `rules.md` frontmatter `shared_master`（env 引用，如 `$FLIGHTDECK_SHARED_MASTER`）展开 → 若是存在目录则用。
2. 否则读 gitignored `<deck>/.shared-master` 指针文件（首行 = 路径，也 env 展开）——**项目里看得见、每台机器各填、不进 git**。
3. （Claude 便利回退）仍无 → 查用户全局 CLAUDE.md 的跨项目资产库根。
4. 全不中 → 本机没有母库：每文件吐 `master-missing`、**优雅跳过**并报告；vendored 文件本身自洽，照常可用。

## 模式（pull：A 全量 / B 首发；push：C 反向）

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

### C. 反向：推回母库（`/flightdeck:sync push <消费相对路径>`）

把消费 deck 的某文件推上母库（撤销早期「单向不回流」MVP 边界）。两种：

- **promote（本地原创、无 `synced_from`）**：项目内部写的、现在够通用 → 拷其**正文**到母库**同一相对路径**，母库 `last_updated` 取该文件的值；然后给本地文件**盖上 `synced_from`**（从此成 vendored 消费者）。母库已存在同名文件 → **停下问**（属冲突/回流，不是 promote）。
- **回流（已 vendored、`locally-ahead`）**：把该文件的**共享正文**推上母库源，母库 `last_updated` 戳成消费端的 → 两边 in-sync。
- **`## 项目覆盖` 段永不上推**（项目私有，不进母库）；只推共享正文。
- 收尾：regen **母库**与本 deck 的 INDEX。

## `## 项目覆盖` 约定

vendored 文件的项目专属补充写在一个保留标题段下（`## 项目覆盖`，或本 deck 语言的等价标题，如 `## Project-specific`）。sync **永不覆盖**该段下任何内容。该段**之上**（共享正文）归母库所有，`upstream-changed` 时被刷新。

## Don't do

- 不碰没有 `synced_from` 的文件（本地原创）。
- 不覆盖 frontmatter，也不覆盖 `## 项目覆盖` 段。
- `locally-ahead` 不**自动**回流——回流走显式 `/flightdeck:sync push`（防误推本地实验上母库）。
- promote / 回流都**只推共享正文，不上推 `## 项目覆盖` 段**（项目私有）。
- 母库缺席不硬失败 —— 优雅 no-op。

## Report

末尾统一 banner（先正文后 banner、一回合一个）：

```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · K locally-ahead · D dangling
[Master]  <已解析母库根>   (或 "master-missing — rules.md 的 shared_master（如 $FLIGHTDECK_SHARED_MASTER）未设/未解析，已跳过")
```
