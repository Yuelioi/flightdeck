---
status: active
summary: flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
last_updated: 2026-06-03
related: [specs/2026-06-03-scriptable-mechanical-layer-design.md, landed/specs/2026-06-03-rules-simplification-design.md]
---

# flightdeck 模型 v4 — folder / 状态 / cockpit 简化（并入 3.0）

## 第一性原则：AI 全自动驱动

flightdeck 当前一大半设计假设的是**人机协作**：cockpit 是给人读的 ≤80 行 focus 层、状态是「AI 建议 / 人确认」的 label、`Next session` 与 `Hanging tasks` 手维护。

但真实用法是 **AI 全自动运作，人几乎不手动维护**。在这个前提下，现有模型的几条核心假设失效：

- "写了 spec 却没进 cockpit" 的**孤儿根因**不是缺一个检查，而是模型把"将 artifact 纳入 focus"这一步**默认交给人**，而人不做。
- "cockpit 是 focus 不是 status、由人手维护" 这条哲学的前提（人会维护 focus）不成立。
- "状态 AI 建议、人确认" 的确认环节对全自动场景是空转。

**本设计确立的第一性原则：AI 全自动驱动——创建 / 推进 artifact 的同一个动作里就把状态和 cockpit 一起维护好；人可以通过指挥 AI 来覆盖，但不必手动编辑文件。** 孤儿因此在结构上不可能出现。

> **根基句（评审 I）：cockpit 不再是人工维护的工作区（workspace），而是 active 状态的自动派生视图（status projection）。** folder 7→5 与状态 6→4 都是这条的自然推论——真正的核心是 cockpit 从「需同步维护的第二份事实」变成「单一事实源 active 的派生视图」。

> 取舍态度（维护者确认）：模型该删就果断删——现在不删，以后是包袱。

本设计是一次连贯的「模型 v4」重构，四个部分（folder / 状态 / cockpit / 删 debriefs）强耦合，作为**一个 spec**；**实施分 phase**，留给 writing-plans 阶段拆。**定位：并入 3.0**（3.0 推迟发布，作为 3.0「简化」主题的延续）。

## 1. 数据模型：folder 7→5，状态 6→4

### 1.1 folder：sketches 并入 specs、删 debriefs

| 现在 | 之后 |
| --- | --- |
| `sketches/` + `specs/` | **合并为 `specs/`**。"未启动的想法" 不再是独立文件夹，而是 specs 里 `status: idea` 的文件。原来的 "promote sketch→spec"（移文件 + 改状态 + 改关系边）退化成**只改一个状态字段** `idea → active`。 |
| `debriefs/` | **删除**（见 §3）。 |
| `plans/` `incidents/` `checklists/` `charts/` | 保留不动。 |

合并后的 artifact 文件夹：`specs/ plans/ incidents/ checklists/ charts/` + `landed/`。

- knowledge 三件套（`incidents/` `checklists/` `charts/`）整体不动，状态集不变。
- `charts/`（导入的外部材料）保留——它与 debriefs（外部评审 + disposition）语义不同，且不在本次删减范围。

### 1.2 workflow 状态：6→4

```
idea  →  active  →  done
   ↘ ─────────→  scrapped     （任意态决定不做了）
```

| 新状态 | 含义 | 吸收了旧的 |
| --- | --- | --- |
| `idea` | 未启动的想法 / 设计（待启动池） | 旧 `sketch` 的 active + 旧 spec/plan 的 `pending` |
| `active` | 正在做 | 旧 `active` + `awaiting-review` + `blocked` |
| `done` | 完成，归档进 `landed/` | `done` |
| `scrapped` | 否决 / 放弃，不归档；留作"考虑过、否决了"的备忘，防止 AI 反复重提同一被否方向 | `scrapped` |

砍除理由：
- **`pending` 并入 `idea`**——"还没启动的想法" 和 "设计写完待实现" 在全自动驱动下没必要分；AI 要做时直接 `idea → active`。
- **`awaiting-review` / `blocked` 并入 `active`**——review 由 AI 在 active 内完成；blocked 罕见，用 cockpit 一行备注表达，不值得占一个状态值。
- **knowledge 状态不变**：`active / obsolete / superseded`。

**可选 `note:` 字段（评审 E）**：active 吸收 `blocked` / `awaiting-review` 后会丢失"为什么没动"的诊断信息。**不**恢复 `blocked` 状态、不占状态值，改加一个**可选 `note:` frontmatter 字段**（如 `note: 等迁移设计定稿`）承载诊断 / 阻塞原因；cockpit `## 进行中` 与 walkaround 检测到该字段时在对应行标注 `[note: …]`，信息不丢。

### 1.3 命名约定

- `idea` 态文件**无日期前缀**（想法是 timeless 的，沿用旧 sketch 的 `<topic>.md`）。
- `idea → active` 翻转时**自动补 `YYYY-MM-DD-` 前缀**（与现有 spec 命名一致）。

### 1.4 状态决定 cockpit 可见性（与 §2 的接口）

| 状态 | 可见位置 |
| --- | --- |
| `idea` | 待启动池——只在 `specs/INDEX` 出现，**不进 cockpit**（它不是孤儿，是"还没轮到"） |
| `active` | **自动出现在 cockpit 的 `## 进行中`**；`idea→active` 翻转即"进 cockpit"的时刻 |
| `done` / `scrapped` | landing 自动移出 cockpit + 归档（scrapped 不归档，仅移出可见区） |

**scrapped 的归宿（评审 A）**：`scrapped` 文件**留在 `specs/` 原位**——不移 `landed/`、**不建 `graveyard/` 子文件夹**（后者违背"减文件夹"主旨，且 folder-semantics 禁止 `specs/` 子目录）。`flightdeck_index.py` 生成 `specs/INDEX` 时**跳过 `scrapped`**，使其不污染待启动池；需要时仅在单独 hand 区 `## 已否决` 列出。

**`specs/INDEX` 状态分组（评审 D）**：idea 文件无日期前缀，与 active/done 的 `YYYY-MM-DD-` 文件混排会乱。INDEX AUTO 区**按状态分组**：`待启动（idea）` 与 `进行中 / 已完成（active·done）` 两组；组内 active/done 按日期降序、idea 按字母序，`scrapped` 不出现。

## 2. cockpit 由 AI 全自动驱动

### 2.1 核心机制：状态翻转 = cockpit 维护触发点

cockpit 新增一个 `## 进行中` 的 **AUTO 区**（与 INDEX 的 `<!-- AUTO -->` 同机制，机器维护），内容 = 所有 `status: active` 的 spec/plan，自动派生：

- AI 决定做某想法 → `idea → active` → **同一动作里** regen 该 AUTO 区 → 自动出现在 cockpit。
- 完成 / 放弃 → `done` / `scrapped` → landing 自动移出 + 归档。

孤儿因此**结构上不可能**：active 必在 cockpit；idea 待在待启动池（`specs/INDEX`），本就不该进 cockpit。

### 2.2 cockpit 结构（之后）

```
Last updated: <自动>
Active focus: <AI 维护的一句话主线>

## 进行中          ← AUTO 区，从 status:active 的 spec/plan 派生（人不手写）
- [spec/plan 名] — 一句话

## 下一步          ← 全自动：AI 每次 landing 自动决定写入（接下来启动哪个 idea / 当前 active 的下一步）

## Hanging tasks   ← 阻塞项（保留）
```

把现在手写的 `Next session` 拆成两半：**进行中**（AUTO 派生）+ **下一步**（动作）。

**两区定义（评审 F）**：`Active focus` = 当前会话主线，粗粒度一句话；`## 下一步` = 下一个**具体可执行动作**（单步）。粒度不同，不重叠。

**`## 下一步` 生成协议（评审 B）**：AI 写入的"下一个动作"，内容可为 (i) 从 idea 池**启动**某想法，或 (ii) **推进**某 active 的续作。**触发点 = landing + `idea→active` 翻转 + 完成一个里程碑**；`preflight` 只读不重写（读到即用，过期由下次写入点纠正）。

### 2.3 全自动，人通过指挥 AI 干预

- `## 进行中` 与 `## 下一步` **都由 AI 全自动维护**。
- 人想调整"下一步"等内容，**通过对话指挥 AI 改**，而不是手动编辑文件——所以无需为"人手编"保留半自动弹性。
- AUTO 区不应手改（改了下次 regen 覆盖）；`Active focus` / `Hanging tasks` 仍可被 AI 或人改写。

### 2.4 regen 责任 + 80 行约束

- `status`（翻状态时）和 `landing`（归档时）负责重生 `## 进行中`。
- 复用并扩展 `flightdeck_index.py`：除 INDEX 外，再生成 cockpit 进行中区——与 `scriptable-mechanical-layer` 一脉相承（机械层多接一个产物）。
- **80 行**保留为软上限：`## 进行中` 是 AUTO 且通常很短；active 堆积本身是失焦信号，walkaround 报 INFO，不阻塞。
- **改名同步（评审 H）**：`## 进行中` 每次从当前文件**重新派生**，故 `idea→active` 补日期前缀后，下次 regen 自动用新文件名 / 链接——无需手动同步；要求**改名与 regen 在同一动作内完成**，不留中间态。

## 3. 删 debriefs + 外部反馈流程

**取消 `debriefs/` 文件夹 + `reviewed` 字段。** 新流程：

- 外部评审反馈（其他 AI / 同事）= **transient 输入** → 项目根 `tmp/`（gitignored），AI 读它。
- 反馈的真正价值是 **disposition**（adopt / reject / defer 的决策）→ 直接落进**对应 spec** 的一节（如 `## 评审纪要`），随 spec 演进。
- raw feedback 用完即弃（`tmp/` 不入库）。

理由：debriefs 文件夹把"外部反馈"抬成一等公民，但它的价值是融进 spec 的决策，不是独立留存的原始文本。把 transient 的东西留在 transient 区。

`tmp/` 怎么用、何时清理是**用户自己的习惯，flightdeck 不规定**（不定义其结构 / 清理策略）——flightdeck 只约定"外部反馈的 disposition 落进对应 spec"，raw 输入在哪、留多久由用户决定。

## 4. 迁移（并入 3.0，非静默）

### 4.1 通用迁移（preflight 提议，绝不静默）

3.0 已在 `MIGRATION.md` 的 `layout_need_update` 中——本设计扩充 3.0 迁移内容：

1. `sketches/*` → `specs/`：`active → idea`，`scrapped` 保持。
2. `debriefs/`：未归档的把 disposition 并进对应 spec，raw 丢弃；已 `landed/debriefs/` 的保留；删空文件夹。
3. 状态重映射：`pending → idea`、`awaiting-review → active`、`blocked → active`（+ cockpit 一行备注）。
4. cockpit：插入 `## 进行中` AUTO 区并首次 regen；`Next session` 拆为 `## 进行中` + `## 下一步`。

### 4.2 本仓库（dogfood）迁移

- 旧 `specs/` 5 个：`incident-recurrence-autocount` / `scriptable-mechanical-layer`（active）留 `active`（进「进行中」）；`structural-edit-guard` / `preflight-silent-bump-nudge` / `status-spec-co-advance`（pending）→ `idea`（进待启动池）。本 model-v4 spec 自身为 `active`。
- sketch `v1x-deferred-ideas`（active）→ `specs/` 且 `status: idea`。
- `debriefs/` 已空（本会话归档完）→ 直接删文件夹；`landed/debriefs/` 历史保留。
- cockpit 重构成 §2.2 新结构。

## 5. skill / 文件影响盘点（实施分 phase）

| 文件 | 改动 |
| --- | --- |
| `skills/status` | 4 状态；翻 `active` 时自动 regen cockpit 进行中区 |
| `skills/landing` | 删 debrief 分类 (e) + disposition 阻塞门；状态映射；全自动写 `## 进行中` + `## 下一步` |
| `skills/preflight` | 读新 cockpit 结构；迁移检测含本次；fallback「待启动池」= idea specs |
| `skills/walkaround` | 删 debriefs 审计；状态合法值改 4 态；cockpit AUTO 区一致性检查 |
| `skills/preflight/protocol.md` · `folder-semantics.md` · `templates.md` | 大改：folder map、状态集、删 debriefs、cockpit 结构 |
| `scripts/flightdeck_index.py` | 扩展：多生成 cockpit `## 进行中` 区 |
| `scaffolds/full/` | 删 `sketches/` `debriefs/` 文件夹；cockpit 模板改新结构 |
| `skills/emit-agents-md` | cockpit 结构变更后 emit 逻辑跟进 |
| `MIGRATION.md` | 扩充 3.0 迁移段（§4.1） |

## 6. 与现有 3.0 工作的关系

- 与已 landed 的 `rules-simplification` **正交**，同属 3.0「简化」主题。
- 与 active 的 [`scriptable-mechanical-layer`](2026-06-03-scriptable-mechanical-layer-design.md) **协同**：cockpit 进行中区 regen 直接接进机械层脚本（§2.4）。
- **`status-spec-co-advance`（本会话刚由 sketch 提升）部分被本重构吸收**：状态从 6 砍到 4、cockpit 自动驱动后，"plan 推进不带动 spec" 的**可见性/孤儿症状已消解**（active spec 永远在 `## 进行中`，不会被遗忘）。但"plan 翻 `done` 自动带动其 `implements:` 的 spec"这一**多工件状态联动 v4 未实现**（status 仍只动一个工件）。**复核结论（Phase 5）：保留为 `idea`**（待启动池），不 scrapped——剩余的状态联动增强仍是一个独立、可选的小设计。
- `structural-edit-guard` 仍独立有效（防多行 Edit 吞标题），不受本重构影响。

## 7. 开放问题（实施时定，不阻塞设计）

1. **（已由评审 D 定调）** `## 进行中` / `specs/INDEX` AUTO 行格式：复用 INDEX 行格式（`[file](file) — 一句话`），共享 `flightdeck_index.py` 实现。
2. **（DEFER — 评审 G）** idea 池随时间堆积可能"沉底变墓地"。v4 **不**在 cockpit 加 `Top ideas` 曝光区（与精简诉求冲突 + 需排序逻辑）；依赖 preflight fallback 扫 idea 池的既有曝光，留待 dogfood 观察是否需要轻量 Top-N。
3. **（DEFER — v5）** `## 下一步` 是否也改为**完全派生**（从 active 的最高优先 action 自动算出，而非 AI 写入）。v4 保留 AI 写入（符合"人指挥 AI 改"）；完全派生是 v5 话题。

## 8. 评审纪要（三方 AI 评审 disposition）

2026-06-03，Claude / DeepSeek / GPT 三方独立评审本 spec（raw 反馈经 `tmp/*.txt` 输入，按新流程读毕即弃）。一致结论：设计自洽、无硬伤，可进 writing-plans。disposition：

| 项 | 意见来源 | 处置 | 落点 |
|---|---|---|---|
| A scrapped 归宿 + INDEX 排除 | Claude🔴 / DS#1 | **采 DS、驳回 Claude `graveyard/`** | §1.4 |
| B `## 下一步` 生成协议 + 触发 | 三方 | adopt | §2.2 |
| C `tmp/` 生命周期 | DS#4 | **不采**——`tmp/` 是用户习惯，flightdeck 不规定其结构 / 清理 | §3 |
| D idea INDEX 分组排序 | DS#5 / ClaudeQ2 | adopt | §1.4 |
| E blocked 诊断 → `note:` 字段 | Claude / GPT | adopt（采通用 `note:`，不恢复 blocked） | §1.2 |
| F Active focus vs 下一步 定义 | Claude🟡4 | adopt | §2.2 |
| H AUTO 改名同步 | DS | adopt（澄清：重新派生，无需手动同步） | §2.4 |
| I cockpit = status projection 根基句 | GPT | adopt（升为原则根基） | 第一性原则 |
| G idea 池墓地 → Top ideas 曝光 | GPT#2 | **defer**（与精简冲突，记开放） | §7.2 |
| `## 下一步` 完全派生 | GPT | **defer → v5** | §7.3 |
| status-spec-co-advance 待复核吸收 | DS / GPT | 保持（§6 已是该措辞） | §6 |

> 绿灯共识（无需改动）：`pending→idea`、`awaiting-review→active`、debriefs 删除、idea 无日期前缀、80 行软上限——三方均确认正确。
