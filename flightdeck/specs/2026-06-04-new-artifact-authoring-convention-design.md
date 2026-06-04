---
status: active
summary: 撰写新 deck 工件每次交"推导税"（按-kind frontmatter / 命名 dateless-vs-dated / 记得 regen——位置实践中已可靠落对 flightdeck/specs/，不是痛点）。选定方向 B：新增 /flightdeck:new skill 包 flightdeck_new.py，确定性盖按-kind frontmatter + 命名 + 落目录 + regen，覆盖全部工件种类，shell-first 交接；SKILL=权威撰写契约文档面（含方向 A）。发现靠常驻指针（protocol 节 + emit-agents-md 模板行 + skill description）——目的是让 agent 用入口而非手搓，不防 docs/。并入 3.0
last_updated: 2026-06-04
---

# 撰写新 deck 工件的"推导税"——/flightdeck:new 入口（方向 B）

> 由真实会话（2026-06-04，preflight 瘦身设计）暴露并经用户校正框定。供 flightdeck 落地。

## 现象

每次让 agent 产出 deck 工件（spec/plan/incident/checklist/chart），它都得"现翻"——读 `templates.md`、翻现有 spec、翻 `commits.md`——才能拼出"放哪 + frontmatter 长啥样 + 命名怎么取 + 谁更新 INDEX/cockpit"。本该被遵守的约定，变成每次重新推导。

**校正（实践数据）**：产出**位置**实践中**已可靠落对** `flightdeck/specs/`——不是痛点。真正的代价是 agent 为了让它落对、且 frontmatter/命名/regen 都对，**每次交的"推导税"**：

- 按 kind 的 frontmatter 字段（workflow vs knowledge 各一套）；
- 命名规则（idea 用 dateless `<slug>.md`、active/done 加 `<date>-` 前缀；要不要 `-design` 后缀本会话就含糊过）；
- 写完**记得**跑 `flightdeck_index.py` 重生 INDEX/cockpit 投影。

位置是最容易的那部分；烦的是这套机械的 frontmatter/命名/regen 每次重推。

## 根因（结构性）

1. **flightdeck 只有"管理既有工件"的仪式**（`preflight` / `landing` / `walkaround` / `emit-agents-md`），**没有"创建新工件"的入口**。撰写动作发生在外部 skill（如 `brainstorming` / `writing-plans`）里。
2. **撰写 skill 不知道 flightdeck 的机械约定。** `brainstorming` 默认路径与自带 frontmatter 都不是 flightdeck 的；它只留一句"用户偏好可覆盖位置"。**位置每次被 agent 现翻纠正成功（所以落对）**，但 frontmatter/命名/regen 这套机械细节也只能靠同样的现翻拼出。
3. **约定分散**：位置在 `commits.md`、frontmatter 在 `templates.md`、INDEX/cockpit 归属在协议正文——没有一个"撰写 deck 工件该遵守的格式"的**单一权威源**，可在动笔时被指向。

## 设计：`/flightdeck:new` + `flightdeck_new.py`（方向 B）

把"放哪 + frontmatter + 命名 + regen"从**每次推导**变成**一次确定性盖章**。仿照刚落地的 `launch`（skill 包 `flightdeck_init.py`）。

### 组件

- **`scripts/flightdeck_new.py`**（快路径，Python stdlib，加入 init/index/lint/bump 脚本族）：
  `flightdeck_new.py <deck> <kind> --slug <s> --title "<T>" [--status idea|active|done] [--summary "..."] [--implements specs/x.md] [--when-to-read "..."] [--applies-to a,b,c] [--date <today>]`
  → folder=kind；按规则定文件名；盖**按-kind frontmatter**；写 `# <Title>` 骨架正文；**拒绝**目标已存在；**调 `flightdeck_index` 重生 INDEX/cockpit**；**打印创建的路径**。
- **`skills/new/SKILL.md`**（`/flightdeck:new`，仿 launch）：fast path 调脚本；**fallback = 权威"撰写契约"文档面**（folder=kind 表、按-kind frontmatter 表、命名规则、写完跑 index）——**这就是方向 A 的单一权威源**，无 runtime 时供 agent 手做，有 runtime 时脚本替它做。
- **发现/交接钩子**（见下）。

### 脚本钉死的"权威"（终结现翻 + 终结命名含糊）

- **命名规则（钉死一条）**：`[<date>-]<slug>.md`。`--slug` 显式给（kebab、ascii；Chinese 标题不适合做文件名，故 slug 与 title 分离）。`status≠idea` 加 `<date>-` 前缀，`idea` 不加（= model-v4 dateless 规则，现被脚本强制）。**不自动追加 `-design` 后缀**——要不要"design"由 slug 自带；本会话的含糊就此消除。
- **按-kind frontmatter**（源出 protocol canonical 字段表）：
  - workflow（spec/plan）：`status` / `summary` / `last_updated`（+可选 `implements` / `related`）。
  - knowledge（incident/checklist/chart）：`status` / `when_to_read` / `applies_to` / `last_updated`（+可选 `superseded_by`）。
- **默认 status**：workflow 默认 `idea`（先泊位、不过早投影 cockpit；承接 brainstorming 时显式传 `--status active`）；knowledge 默认 `active`。
- **regen**：建壳后调 `flightdeck_index`（active workflow 即投影进 cockpit `## 进行中`；idea 不投影；knowledge 上 folder INDEX）——闭合"记得 regen"这一税。

### 交接工作流（shell-first）

外部 authoring skill **先建壳再填正文**：`/flightdeck:new spec --slug X --status active` → 得到路径 → 把正文写进该路径。比"写完再搬"干净，与 `flightdeck_init.py` 同模式，且 INDEX/cockpit 在建壳时已 regen。

### 发现/交接钩子（重新框定）+ 诚实局限

目的**不是**"把 brainstorming 从 `docs/` 拽回来"（实践中位置已对），而是**让 agent 伸手去调 `/flightdeck:new` 而不是手搓文件**。

- **protocol.md** 加一节 canonical "Authoring new artifacts"（权威参考，agent 按需读）。
- **emit-agents-md 模板**加一行，让生成的 **AGENTS.md**（常驻加载）承载："新 spec/plan/… → `/flightdeck:new`（确定性盖 frontmatter+命名+regen）"。
- `/flightdeck:new` 的 **description** 写得让 skill-routing 在"要建 spec/plan"时命中。

**诚实局限**：`flightdeck_new.py` 存在 ≠ 外部 skill 会调它——**我们改不了 superpowers 的 brainstorming/writing-plans**。所以"让外部 skill 交接"只能靠 flightdeck 侧的**常驻指针 + agent 的纪律**。正面信号：实践中位置每次都对，说明 agent 很会捡项目常驻约定——故这条 C 式指针靠谱。B 治本了**执行**（frontmatter/命名/regen 不再推导），发现仍是常驻注入。

### scriptable 层一致性

`flightdeck_new.py` 配 `scripts/tests/test_flightdeck_new.py`（仿 `test_flightdeck_init`，stdlib unittest）；SKILL 的 markdown fallback 是 source of truth（同 scriptable-mechanical-layer spec 哲学）；清单 `"skills": "./skills/"` 自动发现，无需注册（同 launch）。

### 范围

覆盖**全部工件种类**（spec/plan/incident/checklist/chart）——机制统一，每种的 frontmatter 脚本都知道。注：knowledge 工件主要由 `landing` 创建（已内置约定），故 new 入口对它们是"也可用"而非主战场；不改 landing 的现有创建逻辑（避免职责重叠，二者都走同一套 frontmatter 真相源即可）。**并入 3.0**（未发布）。

## 验证

- `test_flightdeck_new.py`：建 spec（idea→dateless / active→dated）、建 plan（带 implements）、建 knowledge（带 when_to_read/applies_to）、拒绝已存在、regen 后 `flightdeck_index --check` clean。
- dogfood：`/flightdeck:new spec --slug demo --status active` 在本仓库建壳 → 确认路径/frontmatter/cockpit 投影正确 → 删除。
- `flightdeck_lint.py` / walkaround 对新建工件无 findings。

## 实现顺序（交给 writing-plans 细化）

1. `scripts/flightdeck_new.py` + `test_flightdeck_new.py`（机械层：命名/frontmatter/落目录/调 regen）。
2. `skills/new/SKILL.md`（fast path + 权威撰写契约 fallback + 交接说明）。
3. 发现钩子：protocol.md "Authoring" 节 + emit-agents-md 模板行 + 校 description。
4. 文档：README/README.zh 命令表加 `/flightdeck:new`；adapters 命令清单加 `new`。
5. 验证 + dogfood；发布提醒：3.0 CHANGELOG 写新命令（version-bump step 3，本次不动 CHANGELOG）。

## 评审纪要

- **方向**：A/B/C 三选，用户**主推 B**（脚本入口，最治本——消除 frontmatter/命名/regen 推导）。A 作为 SKILL 的文档面保留；C 作为发现钩子保留。
- **种类范围**：用户选**全部工件种类**。
- **暴露形态**：用户选 **`/flightdeck:new` skill 包脚本**（仿 launch）。
- **痛点收窄（用户校正）**：位置实践中已可靠落对，**不是**痛点；真正的税是 frontmatter/命名/regen 推导。据此**砍掉**"防写 `docs/`"的 guard 框定，发现钩子改框为"用入口而非手搓"。
- **时序**：并入 3.0（未发布前所有新工作归 3.0，已记为常驻规则）。
