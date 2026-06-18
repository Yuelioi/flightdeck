---
name: sync
description: Use when explicitly syncing this deck's vendored shared-knowledge files (a checklist/doc carrying `synced: true`) against their master deck — pulls upstream-changed bodies, preserves the reserved project-specific section + routing frontmatter, surfaces drift it can't auto-resolve, and `push <path>` reverse-adds a local file up to the master (promote / backflow). Triggered by `/flightdeck:sync`.
---

# Flightdeck Sync — vendored shared-knowledge refresh

母库（master deck）是共享知识的唯一真相源；本仪式把消费 deck 里 vendored 的副本按母库刷新。**谁新谁赢**（比 `last_updated`，无 hash）。AI 干合并；`flightdeck_index.py --sync-status` 算事实。

## 母库解析（master resolution）

固定约定：母库根 = `~/.flightdeck`（即脚本 `_resolve_master_root`，无入参）。是目录则用；否则 `master-missing`，每文件优雅跳过并报告（vendored 文件自洽，照常可用）。**逃生口**：母库想放别处，把 `~/.flightdeck` 做成指向它的符号链接；Windows 无管理员权限用目录联接 `mklink /J %USERPROFILE%\.flightdeck <target>`（`is_dir()` 两者都跟随）。

## 模式（pull：A 全量 / B 首发；push：C 反向）

### A. 再同步全部（裸跑 `/flightdeck:sync`）

1. 跑 `flightdeck_index.py <deck> --sync-status` → 每个 vendored 文件一行 `state<TAB>relpath`。
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
3. 往其 frontmatter 戳 `synced: true`，并**滤掉母库的 `consumers` 键**（母库专属，不进消费副本）。
4. 按需本地化路由（项目可改 `when_to_read` / `applies_to`）；项目专属补充另起 `## 项目覆盖` 段。
5. regen INDEX。
6. 注册消费者：对母库跑 `flightdeck_index.py <母库根> --register-consumer <本 deck 绝对路径> <母库相对路径>`（幂等；失败只警告，不回滚已落地的 vendor）。

### C. 反向：推回母库（`/flightdeck:sync push <消费相对路径>`）

把消费 deck 的某文件推上母库（撤销早期「单向不回流」MVP 边界）。两种：

- **promote（本地原创、无 `synced`）**：项目内部写的、现在够通用 → 拷其**正文**到母库**同一相对路径**，母库 `last_updated` 取该文件的值；然后给本地文件**盖上 `synced: true`**（从此成 vendored 消费者），同样对母库跑 `--register-consumer <本 deck> <相对路径>`。母库已存在同名文件 → **停下问**（属冲突/回流，不是 promote）。
- **回流（已 vendored、`locally-ahead`）**：把该文件的**共享正文**推上母库源，母库 `last_updated` 戳成消费端的 → 两边 in-sync。
- **`## 项目覆盖` 段永不上推**（项目私有，不进母库）；只推共享正文。
- 收尾：regen **母库**与本 deck 的 INDEX。

### D. 扇出：母库改动推全下游（`/flightdeck:sync --fanout`）

母库端一键把改动扇出到所有已注册消费 deck：
1. `flightdeck_index.py <母库根> --list-consumers` → 拿可达消费 deck 集合（空 → no-op，报「注册表为空」）。
2. **串行**遍历，对每个下游 deck 跑正常 pull（§A）：`--sync-status` 算该 deck `upstream-changed`，正文替换、逐字保 `## 项目覆盖`、frontmatter 不动。每个 deck 路径作显式入参，不切 cwd。
3. **失败隔离**：单 deck 失败（权限/锁/损坏/目录缺席）记一条、继续其余。
4. （可选）跑 `--prune-consumers` 清确认消失的 deck。

`--fanout` 是本 skill 的编排，**不是脚本 flag**；脚本只提供 register/list/prune 三个 primitive。

## `## 项目覆盖` 约定

vendored 文件的项目专属补充写在一个保留标题段下（`## 项目覆盖`，或本 deck 语言的等价标题，如 `## Project-specific`）。sync **永不覆盖**该段下任何内容。该段**之上**（共享正文）归母库所有，`upstream-changed` 时被刷新。

## Don't do

- 不碰没有 `synced: true` 的文件（本地原创）。
- 不覆盖 frontmatter，也不覆盖 `## 项目覆盖` 段。
- `locally-ahead` 不**自动**回流——回流走显式 `/flightdeck:sync push`（防误推本地实验上母库）。
- promote / 回流都**只推共享正文，不上推 `## 项目覆盖` 段**（项目私有）。
- 母库缺席不硬失败 —— 优雅 no-op。

## Report

末尾统一 banner（先正文后 banner、一回合一个）：

```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · K locally-ahead · D dangling
[Master]  <已解析母库根>   (或 "master-missing — ~/.flightdeck 不存在/非目录，已跳过")
```

（`--fanout` 模式额外逐 deck 一行 `<deck>: pulled N / in-sync / skipped / error <因>` + 总计。）
