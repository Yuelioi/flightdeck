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

## 实现约定（评审采纳，钉死——同时是 SKILL 契约面的内容）

**kind → folder（单一常量表，脚本与文档共用，不各自隐含）**

| kind | folder |
|---|---|
| spec | `specs/` |
| plan | `plans/` |
| incident | `incidents/` |
| checklist | `checklists/` |
| chart | `charts/` |

**参数与校验（非法即报错退出，与 lint 哲学一致）**
- `--title` 必填（→ H1 + summary 起草）；`--slug` 必填、必须匹配 `^[a-z0-9-]+$`，非法（含中文/空格/大写/下划线）→ **报错** + 打印合法示例。**不**自动从 title 派生 slug（避免中英转换歧义）；SKILL fallback 给统一 slugify 规则（去非 ascii、空格→`-`、转小写、仅留 `a-z0-9-`）供无 runtime 手做时一致。
- 文件名日期 = `--date`（仅覆盖/补录历史用），缺省取**系统当天**；格式钉死 `YYYY-MM-DD`。
- `--implements` 仅 workflow（spec/plan）合法；knowledge kind 传入 → **报错**。
- knowledge（incident/checklist/chart）**必须**传 `--when-to-read` + `--applies-to`（required 路由字段，缺失 → **报错**；不自动填 "TBD" 占位）。
- 非法 `kind` → **报错**（不静默生成错文件）。
- 目标文件已存在 → **拒绝**（初期不做 `--force`；批量 `--no-regen` 同属未来、YAGNI 不做）；SKILL fallback 写明"已存在请先手动删/改名"。
- 默认 status：workflow=`idea`、knowledge=`active`（knowledge 天生是可消费知识 → 默认 active；SKILL 注明此差异的理由，免后人疑惑）。

**命名（SKILL 里也钉死、带负例）**：`[<date>-]<slug>.md`，`status≠idea` 加日期前缀。**不自动追加 `-design`**——`new-artifact.md` ✓；要带 "design" 须自己写进 slug，脚本绝不替你加。

**regen 与 stdout（消除 idea 建壳的误导）**：建壳后调 `flightdeck_index`，stdout 按 status 区分——active workflow → `INDEX + cockpit 进行中 已更新`；idea → `INDEX 已更新；cockpit 不变（status=idea）`；knowledge → `folder INDEX 已更新`。

**description（定稿，发现钩子用）**：`Create a new flightdeck deck artifact (spec / plan / incident / checklist / chart) with correct per-kind frontmatter, naming, and auto-regenerated INDEX/cockpit — use this instead of hand-writing the file. Triggered by /flightdeck:new.`

**landing 关系（SKILL 写明）**：`landing` 已内置 knowledge 约定；`new` 对 knowledge **可用但非必须路径**。二者走同一套 frontmatter 真相源；`new` 会填全部可选字段，`landing` 遵循自身字段集——兼容（缺的非必填字段不影响系统）。plan 期校验 `landing` 实际填的 knowledge 字段集。

## 验证

- `test_flightdeck_new.py`：建 spec（idea→dateless / active→dated）、建 plan（带 implements）、建 knowledge（带 when_to_read/applies_to）、拒绝已存在、regen 后 `flightdeck_index --check` clean。
- **错误路径测试**：非法 kind、空/纯空格/含中文 slug、缺 `--title`、knowledge 缺 `--when-to-read`/`--applies-to`、workflow 字段 `--implements` 传给 knowledge —— 一律**报错退出**而非生成文件。
- dogfood：`/flightdeck:new spec --slug demo --title "Demo" --status active` 在本仓库建壳 → 确认路径/frontmatter/cockpit 投影正确 → 删除 → **删除后 `flightdeck_index --check` 仍 clean**。
- `flightdeck_lint.py` / walkaround 对新建工件无 findings。

## 实现顺序（交给 writing-plans 细化）

1. `scripts/flightdeck_new.py` + `test_flightdeck_new.py`（机械层：命名/frontmatter/落目录/调 regen）。
2. `skills/new/SKILL.md`（fast path + 权威撰写契约 fallback + 交接说明）。
3. 发现钩子：protocol.md "Authoring" 节 + emit-agents-md 模板行 + 定稿 description。
4. 验证 + dogfood（先验证再更新对外文档，避免文档指向未稳接口）。
5. 文档：README.md / README.zh.md 命令表加 `/flightdeck:new`；`adapters/claude/README.md` + `adapters/gemini/README.md` 命令清单加 `new`。
6. 发布提醒：3.0 CHANGELOG 写新命令（version-bump step 3，本次不动 CHANGELOG）。

## 评审纪要

- **方向**：A/B/C 三选，用户**主推 B**（脚本入口，最治本——消除 frontmatter/命名/regen 推导）。A 作为 SKILL 的文档面保留；C 作为发现钩子保留。
- **种类范围**：用户选**全部工件种类**。
- **暴露形态**：用户选 **`/flightdeck:new` skill 包脚本**（仿 launch）。
- **痛点收窄（用户校正）**：位置实践中已可靠落对，**不是**痛点；真正的税是 frontmatter/命名/regen 推导。据此**砍掉**"防写 `docs/`"的 guard 框定，发现钩子改框为"用入口而非手搓"。
- **时序**：并入 3.0（未发布前所有新工作归 3.0，已记为常驻规则）。

### 第二轮（三份外部 review，approve + minor amendments）

采纳并钉进「实现约定」节：kind→folder 常量表 · 日期默认系统当天/格式 `YYYY-MM-DD` · `--slug` 必填+正则校验+SKILL 统一 slugify · `--title` 必填 · `--implements` 仅 workflow（误传报错）· knowledge 必填 when_to_read/applies_to（不 TBD）· 非法 kind 报错 · 已存在拒绝 · regen stdout 按 status 区分（消 idea 误导）· `-design` 负例 · knowledge=active 理由 · landing 与 new 的关系一句 · 定稿 description · 错误路径测试 + dogfood 删后 --check · 实现顺序验证前置于文档 · adapters 路径写明。

拒绝/不做：`--force`、`--no-regen`、`--auto-slug`（均 YAGNI，无当前用例，未来需要再加且不破兼容）；knowledge 字段默认 "TBD"（改为必填报错，更干净）。
