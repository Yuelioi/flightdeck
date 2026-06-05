---
status: done
summary: 自治面收敛到底(真删 self-invoke/disabled_folders/run-scripts(转推断)/status:auto-land 开关，换好默认+推断+判断) + 智能 landing(智能归档替 auto-land) + commit 翻默认(本地自调/push 先问，override 保留) + 版本/布局判定脚本化(verdict 源自 MIGRATION frontmatter) + 版本职责单一归属(preflight 只读上报/landing 只读守卫/walkaround 唯一写) + preflight 删 Branch-0；并入 3.0
last_updated: 2026-06-04
---

# 命令简化 + 版本检查脚本化

## 背景 / 动机

3.0 把结构化 toggle 散文化（`flightdeck-3.0-rules-simplification` 分支）换来了表达力，代价是**配置可发现性差**：rules.md 的自治开关埋在一坨注释短语里，"某命令默认自不自调"得读 protocol 才知道。同时三件事纠缠不清：

1. **self-invoke 闸门**是配置噪声的主要来源，而 5 个命令里 4 个本就默认可自调，闸门价值低。
2. **版本处理脑裂**：preflight 静默 bump + 发被动提示，walkaround 才真正迁移——两个命令都碰版本。
3. **结构坏时 landing 直接崩**（`flightdeck_index.format_row` 对缺 `summary` 的文件 `KeyError`，或版本守卫中途退出），而不是干净地"先去迁移"。

本设计收紧每个命令的单一职责、把自治面收敛到"好默认 + 推断 + 判断"（删掉几乎所有开关）、把"是否该迁移"从 AI 读散文判断降为一次廉价脚本事实。**全部并入未发布的 3.0。**

## 设计

### ① 自治面收敛到底：删闸门/开关，换"好默认 + 推断 + 判断"

钝开关换成命令自身的智能，rules.md 几乎不用配。逐项：

- **删 self-invoke 闸门**（跨 5 skill）：删 `rules.md` 所有 `<ritual>: don't self-invoke` override + `protocol.md` 标准短语表对应行 + preflight/landing/walkaround/status/emit-agents-md 各自的 **"Gate — model-invocation check" 整节** + Rule resolution order 里的 self-invoke 解析。结果：**5 命令一律默认可自调（landing 也是）**。
- **`run scripts` → 环境推断**（不再是开关）：检测到 `uv`/`python` 可达即用脚本，否则手动兜底——与 git/emit 同列推断。dogfood 的 `run scripts with uv run` 也随之消失（自动 `uv`→`python`）。
- **删 `disabled_folders`**：frontmatter 去掉该键；walkaround/preflight 对**空/未用文件夹改宽容**（当非问题，顶多 INFO），只在内容**真放错地方**时问一次（低频审计问一次胜过常驻配置）。→ **frontmatter 收缩到只剩 `version`**。
- **commit → 翻默认（不是删开关）**：出厂默认 = landing 自写 message + **本地 commit 自调**（可 reset/amend、可逆、回收无难度、不外发）；**push 永远先问**（外发不可逆）。安全原则：可逆/非外发 = 自动，不可逆/外发 = 先问。**修订旧"默认啥都不 commit"。** 注意：commit **override 短语保留**（`commit: ask` / `don't auto-commit`），用户经 **CLAUDE.md > rules House Rule** 仍可改回（沿用既有 override 授权链）——与下面几项"真删无 override"不同。
- **`status: auto land` → 真删，改智能归档**（见下"智能 landing"，无 override）。
- **保留**的 override：`commit: ask` / `don't auto-commit`、`status: don't auto start`、git/emit 推断覆盖（`this deck doesn't use git` / `has AGENTS.md but don't auto-regen`）。
- 兼容：pre-3.0 的 `model_invocable` / `commit_mode` / `disabled_folders` 等键**读但忽略**——一条迁移说明。

#### 智能 landing（"作为 skill 本身能力的体现"，替掉开关）

- **归档与否靠判断**（替 `status: auto land`）：对每个 `done` 工件——整簇完成且**无 `active` 工件交叉引用它** → 归档进 `landed/`；仍被 active 引用、或同簇没全完 → **留原地（done-but-unlanded）**。把本仓库 INDEX 那条手写注释（scriptable 簇等 3.0 一起 land）内化成能力，不要开关。
- **commit**：本地自调、push 先问（同上）。
- **知识提取**：把会话学到的归类进 incidents/checklists——本就是判断，无开关。

#### scaffolds rules.md 模板重做（速查表版，收缩后）

现模板"几乎全是注释、靠取消注释配置"像死表单。重做成一段**紧凑速查注释**，用户在 heading 下**自己打一行**覆盖（不再 uncomment）。开关大批移除后，目标产物已很瘦：

```
---
version: 3.0
---

## House rules
<!-- 默认：本地 commit 自调(可 reset/amend) + push 先问 + landing 智能归档；脚本/ git / AGENTS 均自动推断。
     极少需要改；要改就在下方 heading 下打一行短语。可用短语：
       commit: ask | don't auto-commit
       status: don't auto start
       this deck doesn't use git | has AGENTS.md but don't auto-regen -->

### Project conventions

### Autonomy overrides
```

short-phrase 全集仍以 `protocol.md` 标准短语表为权威，模板只是速查。

### ② 版本/布局判定脚本化（机器事实）

新增脚本能力，给定 deck 返回 **verdict**，四态：

| verdict | 含义 |
|---|---|
| `current` | 版本号 = `current` 且无结构落后信号 |
| `compatible-behind` | 版本 < `current` 但 ≮ 任何 `layout_need_update` 项；仅需 bump |
| `structural-behind` | 版本 < 某 `layout_need_update` 项（或无 version），或命中结构信号；需迁移 |
| `malformed` | 结构损坏：缺必需 frontmatter 字段（如 workflow 缺 `summary`）等 |

- **判据**（全是机器可查事实）：
  - 版本号比对：deck `rules.md` `version` vs `MIGRATION.md` frontmatter 的 `current` + `layout_need_update`。
  - 结构信号：`sketches/`·`debriefs/` 文件夹是否仍在、有无 retired status 值（`pending`/`awaiting-review`/`blocked`）、`cockpit.md` 是否缺 `<!-- AUTO:inprogress -->` 区。
  - malformed：解析 frontmatter 时必需字段缺失。
- **数据源：复用 `MIGRATION.md` frontmatter**（`current` + `layout_need_update`），**不新建 json**。理由：版本号紧挨"每个迁移为什么"的散文段，单一真相源不两头漂；脚本已有 `parse_frontmatter()`，读它和 `json.load` 一样省事；对 AI 都是零 token（脚本读、AI 不读）。
- **fast-path / fallback**：沿用仓库现有"脚本快路 + 手动兜底"模式——`run scripts` 开 → 跑脚本拿 verdict；关 → AI 读 `MIGRATION.md` frontmatter（仅 YAML，非散文）+ 自查结构信号。不破 `run scripts` 的 opt-in 契约。
- 实现落点：扩展现有 `flightdeck_index.py`（`version_mismatch` 已在读 MIGRATION frontmatter，自然演进为 verdict 函数）或新增脚本/子命令；同时补掉 `format_row` 缺 `summary` 的 `KeyError` 脆弱点（malformed 应被判定为 verdict，而非崩）。

### ③ 版本职责单一归属（谁读、谁写分清）

| 命令 | 对 verdict 做什么 |
|---|---|
| **preflight** | 入口跑一次（每会话仅一次），**只读上报**一行——非 `current` → "deck 落后，run `/flightdeck:walkaround`"。**不 bump、不迁移** → preflight 仍 100% 只读。 |
| **landing** | regen 前**只读守卫**：`structural-behind`/`malformed` → 干净 STOP 指向 walkaround（替代现在中途 `KeyError` 崩）。不写版本。 |
| **walkaround** | **唯一写版本的命令**：`compatible-behind` 的 bump + `structural` 的迁移（所有判断动作都在这；已有 Audit 10 承接）。 |

**核心不变量**：preflight 只读上报 · landing 只读守卫 · **walkaround 是唯一写版本的人**。

> 关于 preflight 重新承担版本检查（与最初"版本全挪走"的设想相反）的理由：之前的顾虑是"AI 读散文做判断 + 静默 bump 这个写"。②把判断降为一次廉价脚本调用、③把 bump 移给 walkaround 后，preflight 只剩"读 verdict + 报一行"，仍是纯只读，且每会话只跑一次，是发现落后的最自然入口。

### ④ deck 存在检查瘦身

- 删掉 preflight Branch-0 那整段戒律（"读别的之前先 stop"、"别长回安装器"、迁移探测警告）。
- preflight 只留**一行优雅降级**：`cockpit.md` 不在 → "No deck — run `/flightdeck:launch`" → stop。这不是审计，纯粹"别崩"。
- "deck 健不健康/合不合法" 归 walkaround。

## 影响面（供 plan 分解）

- `scaffolds/full/flightdeck/rules.md` — 重做成速查表版（见 ①：frontmatter 仅剩 `version`；删大段散文/分隔线/分组；短语集大幅收缩；配置改为用户自打一行）。
- `skills/preflight/SKILL.md` — 删 Gate 节、删 Branch-0 戒律（留一行降级）、改 step 1（去静默 bump + 去版本比较，改为跑 verdict 只读上报）、对空/未用文件夹改宽容、去 `disabled_folders` 读取、`run scripts` 改推断。
- `skills/landing/SKILL.md` — 删 Gate 节、加 verdict 前置守卫、**智能归档**（替 `status: auto land`）、**commit 本地自调 / push 先问**、`run scripts` 改推断。
- `skills/walkaround/SKILL.md` — 删 Gate 节、消费 verdict 脚本、确立为唯一版本写者（bump + 迁移）、空/未用文件夹改宽容、去 `disabled_folders`。
- `skills/status/SKILL.md` — 删 Gate 节、去 `status: auto land` 分支（归档归 landing 智能判断）。
- `skills/emit-agents-md/SKILL.md` — 删 Gate 节。
- `skills/preflight/protocol.md` — Rule resolution order 去 self-invoke、`run scripts` 移到环境推断列；标准短语表**删** self-invoke / `status: auto land` / run scripts 行，**保留** commit override 行（但把默认从"ask"改为"auto local / push 先问"）；配置映射表去 `disabled_folders`、更新 version 读/写归属与 commit 新默认。
- `scripts/flightdeck_index.py`（或新脚本）+ `scripts/tests/` — verdict 函数 + 测试；补 `format_row` 缺 `summary` 健壮性。
- `MIGRATION.md` — frontmatter 不变（`current` + `layout_need_update` 仍是数据源）；散文更新 preflight 角色（静默 bump → 只读上报；walkaround 唯一写）；加一节迁移说明（self-invoke / `disabled_folders` / `commit_mode` / `status: auto land` / `run scripts` 全部移除或转推断；commit 安全默认变更）。
- `flightdeck/rules.md`（本 dogfood 仓库）— 删四行 manual-only + `disabled_folders` + `run scripts with uv run`，frontmatter 收到只剩 `version`。
- CHANGELOG — 发布时写（自治面收敛 / 智能 landing / commit 默认变更 / 版本检查脚本化 / preflight 行为变更）。

## 取舍记录

- **不换 JSON 管 INDEX**：INDEX 是行记录数据，JSON 每行重复 key 反而更费 token；且 INDEX 本就脚本生成、AI 不手改，写入痛点不在格式。
- **不换 JSON 管 rules**：会反转 3.0 散文化；自治 House Rule 的细微差别用散文表达更准。
- **不新建 `need_update_layout.json`**：见 ② 数据源理由（避免与 MIGRATION 散文两头漂）。
- **智能 landing 优于 `status: auto land` 开关**：归档"是否合适"是情境判断（交叉引用、簇是否完整），钝开关只会"done 即归档"，会误归档仍被引用的工件。skill 的判断力本身就是该有的能力。
- **commit 选"本地自调 / push 先问"而非"永远先问"**：本地 commit 可逆、回收无难度、非外发，自调不破 full-auto；push 外发不可逆，先问守住安全。比一刀切"永远先问"（卡无人值守）或"永远 auto"（外发失控）都稳。且 commit **保留 override**（与 self-invoke/disabled_folders 的"真删"不同）——它是唯一真有后果的动作，留给用户经 CLAUDE.md/rules 改回的余地。
- **删 `disabled_folders` 而非保留**：仅用过一次、连本仓库都是 `[]`，纯死配置；把默认行为改宽容（空文件夹=非问题）后根本不需要压制开关。

## 兼容 / 迁移

- pre-3.0 的 `model_invocable` / `commit_mode` / `disabled_folders` / `status_auto`（含 `auto land`）/ `run scripts` 等键：**读但忽略**（对应概念已删或转推断）。
- **commit 安全默认变更**：旧"开箱啥都不 commit" → 新"本地 commit 自调、push 先问"。这是面向全员的行为变更，须在 CHANGELOG + MIGRATION 显著标注。**override 仍在**：用户经 CLAUDE.md / rules House Rule（`commit: ask` / `don't auto-commit`）可改回原行为。
- 版本号语义不变；`flightdeck_index.py` 自身的 version guard 保留（脚本独立自保）。
- 本变更并入 3.0，发布前走交互 dogfood 验证。
