---
status: done
---

# flightdeck 1.2 — INDEX + 显式 status 的轻量项目导航

**日期**：2026-06-01
**对外版本**：**1.2.0**（minor；不发 2.0）
**一句话定位**（采自 gpt 审核）：*flightdeck 1.2 = 一个以 INDEX 为核心、以显式 status 为元数据、以 cockpit 为焦点入口的轻量项目导航约定。*
**外部审核**：2.0 阶段两轮 + 1.2 阶段一轮（各 3 份 claude/ds/gpt），处置见 §13。

## 1. 动机（为什么是 1.2，不是 2.0）

1.1 的核心病：**文件夹位置同时编码了"类型"和"状态"**（specs/=设计+待办，flight-plans/=计划+进行中，landed/=完成）。

曾经设计过一版 2.0：引入 `kind/form/status/transition/work-item/task` 一整套正交状态机。但在落地与审核中发现它**过度抽象**，且与实际在用的 superpowers（brainstorming→spec 文档、writing-plans→plan 文档）二元产出脱节。于是撤回。

1.2 不是新模型，是把 1.1 **整理干净**：

> 相对 1.1 真正的改进 = **删减**（概念/文件夹）+ **文件必带 `status` 显式元数据** + **每目录 `INDEX.md` 派生索引**（外加"入口收敛"已带来的 rules.md / landed 泛化 / HISTORY / 移除 manifest+logbook+kneeboard）。

撤回 2.0 的 `form`/`work-item`/`task`/`transition`/`kind`-frontmatter，是本设计的明确决定（§12）。

## 2. 核心（只有三件事）

1. **文件夹 = 类型（kind），隐含**——`specs/` 里就是 spec，不写任何 `kind:` 字段。
2. **文件 frontmatter = 状态（status），显式且必填**——这是单文件真相。
3. **每个目录一个 `INDEX.md` = 该目录的派生索引**（文件 + status + 摘要），从各文件 frontmatter 汇总。读 INDEX 即知目录全貌与状态，**不必逐文件读 → 省 token**。

cockpit 退为纯焦点；状态可见性下放到 INDEX。

## 3. 数据模型

**类型（由目录表达，不写 frontmatter）**：
- 工作流：`sketches/`(念头) · `specs/`(设计) · `plans/`(实现计划)
- 知识：`incidents/` · `checklists/` · `charts/` · `debriefs/`

**frontmatter（压到最小，只留会变的 + 路由 + 关联）**：

```yaml
# spec / sketch
---
status: active
---

# plan
---
status: active
implements: specs/<x>.md      # 可选；单向引用，路径相对 flightdeck 根；无则 walkaround 提示「孤儿 plan」。spec 不需要反向字段
---

# knowledge (incident / checklist / chart / debrief)
---
status: active
when_to_read: <一行触发条件>
applies_to: [<tag>, ...]
last_updated: YYYY-MM-DD
# superseded 时：superseded_by: <path>
---
```

没有 `kind`、没有 `form`。spec↔plan 关联是 plan 上的单向 `implements`；反查某 spec 有哪些 plan，读 `plans/INDEX.md` 或扫 frontmatter，**不在 spec 上加 `implemented_by`**。

> `sketch` 实际只用 `active` / `scrapped`；templates 里 sketch 模板**单列**，避免照 spec 模板误填 `pending`。

## 4. status = 标签 + 推荐流转图（不是状态机）

**取值固定**：
- 工作流（sketch/spec/plan）：`pending / active / awaiting-review / blocked / done / scrapped`（sketch 实际只用 `active / scrapped`）
- 知识：`active / obsolete / superseded`

**推荐流转（文档规范，非强制）**：

```
pending → active → awaiting-review → done
active ↔ blocked
任意活跃态 → scrapped
（知识：active → obsolete | superseded）
```

- **无转移表、无转移动词命令**（撤回 2.0 的 promote/start/review/... 那套）。
- **AI 对 status 的权限**：用户随时可手改，AI 不阻拦；AI 在 landing 时可**建议**下一个典型状态，经用户确认再改。
- **walkaround** 只审：值合法、必填、简单一致（`landed/` 里不应有非终态、`superseded` 须有 `superseded_by`、`plans/` 下无 `implements` 的文件给「孤儿 plan」INFO）；对偏离推荐流转的情况只给 **INFO/warning，不阻断**。

## 5. INDEX.md（核心机制）

**每个制品目录**（含 `sketches/`）都有一个 `INDEX.md` —— 该目录的派生索引：

```markdown
# specs/ — INDEX

<!-- AUTO:specs -->
- [2026-..-foo.md](2026-..-foo.md) — active — 一行摘要
- [2026-..-bar.md](2026-..-bar.md) — done — 一行摘要
<!-- /AUTO -->

<!-- 手工区（可选）：分组说明 / 多文件主题归类等，AI 不动 -->
```

- **最小列**：`文件名 | status | 一行摘要`；知识类额外带 `when_to_read` / `applies_to`。`implements` **不进** INDEX（保持轻量）。
- **`<!-- AUTO -->` 区机器维护**：AI 重生成此区（从文件 frontmatter 汇总），区外手工区不动。此约定写进 rules.md / skill，防止不同 session 重复追加而非重生成。
- **重生成范围**：landing 时**只重建本会话有文件变动的目录**（新增/修改/移动/land/status 变更）；其余目录 INDEX 不动。walkaround 做**全量** INDEX↔frontmatter 一致性校验。
- **根 `flightdeck/INDEX.md`**：子目录导览 + 全局状态摘要（纯派生）：

```markdown
# flightdeck — INDEX

<!-- AUTO:root -->
- specs/ — 3 (2 active, 1 done)
- plans/ — 2 (1 active, 1 blocked)
- incidents/ — 1 active
- checklists/ — 1 active
- charts/ — 2 imported
- debriefs/ — 1 active
- sketches/ — 4
<!-- /AUTO -->
```

cockpit = "我在干什么"，根 INDEX = "这个 flightdeck 有什么 + 整体状态"，语义不冲突。

- **`charts/` 的 INDEX.md** 可给一整个导入的外部项目文件夹当导览目录（解决"整目录参考"场景）。
- **`charts/` 在根 INDEX 的特殊处理**：导入的外部文件没有统一 frontmatter，**不做 status 计数**——根 INDEX 的 `charts/` 行只标文件/项目数 + "imported"（如 `charts/ — 2 projects imported`）。
- **根 INDEX 是可降级组件**：保留以提供全局概览；若未来发现大家多看目录级 INDEX、根 INDEX 少人用，可移除而不影响模型。

### 5.1 命令优先读 INDEX（省 token）

所有命令遵循"**先读 INDEX，按需才下钻读单文件**"：
- **preflight** 的路由目录**不再逐个读** `checklists/`/`incidents/` 的文件 frontmatter，改读它们的 `INDEX.md`（或根 INDEX）即可得到 `when_to_read`/`applies_to` + status；只有真要用某条时才读该文件全文。
- **walkaround** 先读各 INDEX 做状态/一致性扫描，仅下钻验证可疑项。
- **landing** 只重生成本会话有变动目录的 INDEX，其余 INDEX 只读。

这是 INDEX 机制的主要红利之一：把"逐文件读 frontmatter"换成"读一个目录 INDEX"，token 成本随目录数而非文件数增长。

## 6. cockpit = 纯焦点

`cockpit.md` 只含：`Last updated` + `Active focus` + `## Next session` + `## Hanging tasks`。**无 In flight**。
- `Hanging tasks` 是**手工维护**的轻量清单（阻塞清场的项），与 INDEX 的自动汇总彻底解耦。
- 看状态去读相应目录的 INDEX；看全局读根 INDEX。
- 80 行硬顶保留。

## 7. spec ↔ plan（对齐 superpowers）

- brainstorming → 一个 `spec`（`specs/`）；writing-plans → 一或多个 `plan`（`plans/`，各带 `implements: specs/<x>.md`）。
- 多 plan 的进度看 `plans/INDEX.md` 的 status 列，一目了然。无需在 spec 里维护 plan 清单（INDEX 已提供）。

## 8. 目录布局 + 命名

```
flightdeck/
├── cockpit.md      rules.md      INDEX.md      （根入口三件）
├── sketches/      INDEX.md
├── specs/         INDEX.md
├── plans/         INDEX.md
├── incidents/     INDEX.md      （← incident-reports/ 改名）
├── checklists/    INDEX.md
├── charts/        INDEX.md      （可含外部项目树）
├── debriefs/      INDEX.md      （← safety-reviews/ 改名）
└── landed/        （镜像各目录 + HISTORY.md）
```

命名：`incident-reports/` → **`incidents/`**、`safety-reviews/` → **`debriefs/`**（去双词 + 飞行化：debrief = 任务后复盘）。其余 `specs/plans/sketches/checklists/charts/landed/` 及命令 `preflight/landing/walkaround`、入口 `cockpit` 保留（多为单词或本就是航空词）。

## 9. 多文件主题（撤回 bundle）

- 制品目录**不引入子文件夹层级**（避免"子文件夹里的文件算什么 kind"的递归问题）。
- 要拆多文件：放**同一目录**多个文件 + 在该目录 `INDEX.md` 的手工区分组说明。撤回 2.0 的 bundle（README 锚 + leaves + reading_order）整套。
- **唯一例外 `charts/`**：导入的外部项目本身带目录树是正常的，`charts/<project>/INDEX.md` 当导览即可。

## 10. README → INDEX

- flightdeck **约定内**一律用 `INDEX.md`，不再用 README（INDEX 语义 = 目录导航，更准；撤回 2.0 bundle README）。
- **仓库根的 `README.md`**（GitHub 项目介绍）是标准项目文件，**不受影响**。

## 11. 保留自"入口收敛"阶段

`cockpit.md` 单入口、`rules.md`（git/emit_agents_md/disabled_folders/disabled_gates + house rules）、`landed/` 泛化、`landed/HISTORY.md`（add-only,git:false 必需）、移除 `manifest.md`/`logbook.md`/`kneeboard/`。

## 12. 相对"刚实现的 2.0 分支"要撤/改什么

当前 `v2-entry-collapse-and-rules` 分支已实现 2.0（含仓库自迁移到 `work-items/`，未提交/未发布）。1.2 据此调整：

- **撤回**：`form` 轴、`work-item`/`work-items/`、`kind:` frontmatter、`kind: task`、`## Tasks` 概念、转移表 + 转移动词、bundle（README 锚/leaves/reading_order）。
- **改名**：`work-items/` → `specs/` + `plans/`；`incident-reports/` → `incidents/`；`safety-reviews/` → `debriefs/`；约定内 `README.md` → `INDEX.md`。
- **新增**：每目录 `INDEX.md`（含根）机制 + landing 重生成范围 + walkaround 一致性校验。
- **保留**：显式 `status`、cockpit 焦点、rules.md、landed/HISTORY。
- **版本**：`VERSION` + 5 manifest 从 `2.0.0` 改 `1.2.0`；CHANGELOG 重写为 `[1.2.0]`；MIGRATION 改 `1.1.x → 1.2`。
- **仓库自迁移**：当前已迁成 work-items/ 的本仓库 `flightdeck/` 要再调成 1.2 布局（work-items/ 拆回 specs/+plans/ 等 + 建各 INDEX）。

净效果：相对 2.0 是**大幅简化**（删多于加），相对 1.1 是"删减 + 显式 status + INDEX"。

## 13. 受影响组件（供 plan）

- `skills/workflow/SKILL.md`：数据模型（目录=kind / frontmatter=status）、status 流转图、INDEX 机制、cockpit 焦点、authority order；删 form/work-item/转移表。
- `skills/workflow/folder-semantics.md`：specs/+plans/ + incidents/debriefs 命名、每目录 INDEX、无子文件夹 bundle、charts 外部项目、README→INDEX。
- `skills/workflow/templates.md`：最小 frontmatter（spec/plan/sketch/knowledge）、INDEX.md 模板（目录级 + 根）、status 流转图；删 work-item/task/## Tasks/转移表模板。
- `skills/workflow/exit-ritual.md`：landing 重生成受影响目录 INDEX、AI 建议 status、手工 hanging tasks。
- `skills/preflight/SKILL.md`：reconcile 读根 INDEX + cockpit；1.1.x→1.2 迁移检测；读目录 INDEX 而非逐文件。
- `skills/landing/SKILL.md`：INDEX 重生成范围、status 建议、land 归档。
- `skills/walkaround/SKILL.md`：审 status 合法/必填/一致 + INDEX↔frontmatter 一致 + 流转偏离 warning；删 2.0 状态机审计。
- `skills/emit-agents-md/SKILL.md`：从 cockpit 渲染（focus/next/hanging）；去 In flight。
- `scaffolds/`：1.2 目录布局 + 各 INDEX.md 占位 + 最小 frontmatter 模板。
- 发布：VERSION + 5 manifest = 1.2.0；CHANGELOG [1.2.0]；MIGRATION 1.1.x→1.2 + 对照表；README EN/ZH；AGENTS 重生成；TEST_PLAN。

## 14. 审核处置（disposition）

**2.0 阶段（历史，已被本设计撤回大部分）**：两轮审核接受了 form×status 正交、转移表等——这些在 1.2 被有意撤回（过度抽象）。原文见 `landed/safety-reviews/`。

**1.2 阶段（本设计，tmp/ 三审）**：三家一致判定骨架可定稿、无结构性缺陷。全部采纳为澄清（已落入 §1–§12）：
- frontmatter 最小 + implements 单向（ds）；status 标签+流转图+AI 权限（ds/gpt——gpt 坚持保留流转图作规范，已采纳）；INDEX 最小列 + AUTO 区 + 重生成范围（claude/ds）；sketches/ 也有 INDEX（ds）；cockpit hanging 手工维护（ds）；多文件主题不引入子文件夹（ds）；README 全废为 INDEX（gpt，限约定内）；implements 路径相对 flightdeck 根（ds）。
- **一处真分歧 → 用户裁决**：根 `flightdeck/INDEX.md` —— claude/ds 主张不加、gpt 主张加；**用户定：加**（全局状态一目了然 + 每目录都有 INDEX 的一致性）。

**1.2 第三轮（针对 spec 全文，tmp/ 三审）**：三家一致可进 plan、无结构性缺陷（gpt：1.2 最大成功是删掉 form/work-item/task/bundle/transition 整层抽象，用 INDEX 补可见性）。采纳：
- **命令优先读 INDEX**（用户提出 + INDEX 红利）→ §5.1。
- `charts/` 在根 INDEX 不计 status、只标项目数（claude）→ §5。
- sketch 模板单列（claude）→ §3。
- 根 INDEX 标可降级组件（gpt）→ §5。
- 迁移混合 work-item 需人工确认（claude）→ §15。
- 一处决策 **plan 是否强制 implements → 用户定：可选 + walkaround 提示孤儿**（§3/§4）。

无未决项。

## 15. 待 plan 细化

- INDEX.md `<!-- AUTO -->` 标记的精确语法 + 根 INDEX 的状态计数格式。
- 1.1.x→1.2 迁移脚本细节（specs/ 不动、flight-plans/→plans/、incident-reports/→incidents/、safety-reviews/→debriefs/、各目录建 INDEX、文件补 status）。
- 本仓库从"2.0 work-items/ 中间态"回退到 1.2 布局的具体步骤。**若某 work-item 文件既含 design 又含 plan 内容,拆回 specs/+plans/ 需人工判断**(plan 里标为人工确认步骤,不全自动)。
- 是否压扁分支历史后作为 1.2.0 发布。
