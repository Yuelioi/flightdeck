---
status: pending
summary: 删 minimal scaffold（留 scaffolds/full 目录名）；install 与 preflight 首次建档统一为 copy-the-scaffold（修注释丢失 + 消双流程）；加可跳过的演示式 onboarding 教程（样例 spec，结束清理）；init 加 git 检测提醒 + AGENTS.md opt-in 询问
last_updated: 2026-06-03
related: [specs/2026-06-03-rules-simplification-design.md]
---

# init 重做 + 单一 scaffold — 设计

## 背景与动机

flightdeck 有**两条初始化路径**，且对"minimal/full"处理不一致：
- CLI 安装器 `install --scaffold=minimal|full`（`minimal` = 3-file 契约；`full` = 全文件夹 + 3 文件）。
- `preflight` 首次建档：**内联现写**最小 3-file 契约，且"不预建其它文件夹"（按需创建）。

两条路 + 两个变体 → 每个 skill 都要判"文件夹缺失是 minimal 还是出错"。还有两个实问题：(a) `preflight` 内联现写导致 **`rules.md` 注释被删**（实测于 `tutorial/flightdeck`）；(b) 当前首次建档简陋，无 git 检测、无 AGENTS.md 询问、无上手引导。

## 目标 / 非目标

**目标**
- 删 `scaffolds/minimal/`，单一 scaffold（`scaffolds/full/`，目录名保留）。
- `install` 与 `preflight` 首次建档**统一为 copy 同一 scaffold**（消双流程 + 修注释丢失）。
- init 加：git 检测+提醒（offer `git init`）、AGENTS.md opt-in 询问、可跳过的演示式 onboarding 教程。
- 教程结束**清理样例**，deck 回到全空布局。

**非目标**
- **英文标准句修正不在本 spec** —— 那是对 3.0 实现的修正，折进 3.0 的 pending commit。
- 不新增 `rules.md` toggle（教程/AGENTS 询问是运行时 prompt，非配置）。
- 可重跑教程的独立命令：暂缓（YAGNI）。

## 1. scaffold 合并（item 1，B = 全盘统一）

- **删 `scaffolds/minimal/`**。`scaffolds/full/` 为唯一 scaffold（**目录名保留 `full`**，churn 最小）：全文件夹布局 + 各 `INDEX.md` + 带注释的**英文** `rules.md` + `cockpit.md` + `landed/HISTORY.md`。
- **「最小 3-file 契约」降为校验地板**（walkaround 仍在 `rules.md`/`cockpit.md`/`HISTORY.md` 缺失时 CRITICAL），但**不再是 scaffold 变体**。地板 ≠ init 创建物。
- **收益**：缺文件夹 = **真异常**（不再有"minimal vs 坏掉"歧义）→ preflight/walkaround 逻辑更简。这才是真正的"减法"（减代码路径）。

## 2. 统一 init = copy-the-scaffold

两条路都**逐字 copy `scaffolds/full/`**（注释保留）。`preflight` 首次建档在其上叠加：

1. **Branch-0**：无 `cockpit.md` → 首次建档。
2. **git 检测**：deck root 有无 `.git`。无 → 提醒（"无 git 也能用；staleness/history 落到 `landed/HISTORY.md`"）+ **offer `git init`? [y/N]**。有 → 标注。非阻塞。
3. 确认："Create a flightdeck deck here? (full layout + 3-file contract)"。
4. **Copy `scaffolds/full/`** → `flightdeck/`。
5. **Interview**（2 问）：Active focus + 首条 Next session → 替换 cockpit 占位符。
6. **AGENTS.md 询问**："Generate AGENTS.md cross-tool bridge? [Y/n]" → yes 跑 emitter（契合 3.0 emit 推断：opt-in 创建）。
7. **教程 offer**（可跳过）："Run a 2-min guided tour? (throwaway sample, auto-cleaned) [y/N]"。
8. STOP。

## 3. 教程 —— `skills/preflight/onboarding.md`（① 演示式）

新 companion 文件，`preflight` 引用：

- 创建 **`specs/hello-flightdeck.md`**（明标 throwaway）。
- **演示 + 旁白**每步，用户敲 enter/"next" 推进：
  `create→pending` → `start→active` → 改两笔 + `finish→awaiting-review` → `approve→done` → **`land`→ 归档 `landed/specs/`**。每步一行：动了哪个文件 / 哪条 INDEX 行。
- **清理**：删样例 + `landed/` 副本 + INDEX 行 + root 计数 → deck 回到全空布局。
- 演示式（非手把手）：目的是建心智模型；肌肉记忆留给用户做真 artifact 时。
- 可重跑命令：暂缓。

## 4. `--scaffold` 弃用路径

- **3.x**：保留 `--scaffold` 旗标但 **warn + ignore**（无论传 minimal/full 都 copy 全布局，打印一行弃用提示）。
- **4.0**：真删除旗标。
- （与 3.0 的"旧 key 3.x 兼容 / 4.0 删"节奏一致。）

## 5. 影响文件

- `scaffolds/minimal/` —— **删**。
- `scaffolds/full/rules.md` —— 英文化（与 3.0 英文标准句一致）。
- `install.sh` / `install.ps1` —— `--scaffold` warn+ignore；总是 copy 全布局。
- `skills/preflight/SKILL.md` —— 重写首次建档（git 检测 + copy scaffold + interview + AGENTS 询问 + 教程 offer）。
- `skills/preflight/onboarding.md` —— **新增**。
- `skills/preflight/folder-semantics.md` —— 简化 minimal-vs-full 一节为"单一 scaffold + 校验地板"。
- `README.md` / `README.zh.md` —— 安装/init 说明更新（去 minimal、加 git 检测/AGENTS/教程）。

## 6. 风险 / 开放问题

- **空 INDEX 文件清单（7 个）**：全布局新 deck 一上来带 7 个空 `INDEX.md`。已接受（换单一流程 + 更好教学）；walkaround 不应把"空 INDEX"报成问题。
- **copy 源定位**：`preflight` 运行时如何找到 `scaffolds/full/`（插件安装路径）？实施时确认相对/绝对路径解析（各 adapter 安装位不同）。
- **教程样例与真 artifact 混淆**：样例明标 throwaway + 结束清理；若用户中途中断教程，残留样例由下次 preflight/walkaround 作为 stray 提示。

## 实施分期（给 writing-plans 的提示）

- **P1**：删 `scaffolds/minimal/`；`scaffolds/full/rules.md` 英文化；`install.*` `--scaffold` warn+ignore；README 更新。
- **P2**：重写 `preflight` 首次建档为 copy-the-scaffold + git 检测 + AGENTS 询问；`folder-semantics` 简化。
- **P3**：新增 `onboarding.md` + 教程 offer 接入。
- **P4**：dogfood（reload 后）——在干净目录跑 `/flightdeck:preflight` 首次建档全程 + 教程 + 清理验证。
