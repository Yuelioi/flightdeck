---
status: pending
implements: specs/2026-06-02-metadata-model-consolidation-design.md
---

# 元数据模型实现 plan —— 归一 + version + enrichment（三篇一栈）

> **For agentic workers:** REQUIRED SUB-SKILL: 用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务执行。步骤用 `- [ ]` 跟踪。

**Goal:** 一个 plan、一趟 pass 落地三篇叠放的 spec —— 先建元数据**单一权威源**，再把 `version` 与 workflow 富化字段并进去，最后回填存量并作为一次发布收口。

**实现的三篇 spec：**
- 上游：[metadata-model-consolidation](../specs/2026-06-02-metadata-model-consolidation-design.md)（本 plan 的 `implements`）
- [version-in-rules-migration-detection](../specs/2026-06-02-version-in-rules-migration-detection-design.md)
- [workflow-artifact-frontmatter-enrichment](../specs/2026-06-02-workflow-artifact-frontmatter-enrichment-design.md)

**Architecture:** 严格分层 —— Phase 0 先把"单一权威字段表"立在 `protocol.md`，其余文档改为指向它；Phase 1/2 只往这张表**填字段 + 接行为**，不再各处重述；Phase 3 dogfood 回填 + 发布。顺序是硬依赖：字段表不先立，后面两 phase 会重新制造漂移。

每个 task 改完即按其所属 spec 的设计核对，不重述设计理由（link, don't copy）。

---

## Phase 0 — 归一骨架（consolidation spec）

- [x] **0.1** `skills/preflight/protocol.md`：在 "Data model" 下新增 `## Frontmatter field reference (canonical)`，照搬 consolidation spec §2.2 的 13 行字段表（kind × 必填 × 谁读 × 谁写 × walkaround）。
- [x] **0.2** 同文件：写入两条裁决理由 —— §2.4 取代关系不对称（knowledge 留位→`superseded_by` 正向重定向；workflow 归档→`supersedes` 边 + grep）、§2.5 `last_updated` 强制级别不对称。
- [x] **0.3** `skills/preflight/templates.md`：各 frontmatter 模板块**去语义说明**，改注 "字段语义见 protocol.md § frontmatter reference"；**补 `skip_when`**（incidents/checklists，可选）到知识类模板。
- [x] **0.4** `skills/preflight/folder-semantics.md`：删除字段内联重述（line 144–251 一带），保留"文件夹用途"，字段一律指向权威表。
- [x] **0.5** `flightdeck/landed/specs/2026-05-30-bundles-and-routing-graph-design.md`：头部加一行废弃标注（bundles/`scope`/`non_goals` 未采纳，见 `protocol.md` "No bundle README"）。
- [x] **0.6** `skills/walkaround/SKILL.md`：Audit 列表加一句"校验项以 protocol.md 权威表为准"；此处不改具体 audit（留 Phase 1/2 随字段一起改），仅建立指向。

**Phase 0 验收**：`protocol.md` 是唯一定义字段语义处；templates/folder-semantics 不再自带字段语义；`skip_when` 三处一致；bundles spec 标废。

## Phase 1 — version → rules.md（version spec）

- [ ] **1.1** `skills/preflight/templates.md` rules.md 段 + `protocol.md`：rules.md 由"Optional file"改为**必选**；定义**三件套最小契约**（rules + cockpit + HISTORY）；rules 模板加 `version`。权威表对应行同步。
- [ ] **1.2** `MIGRATION.md`：加 frontmatter `current: <发布版本>` + `layout_need_update: []`；补一节"本次（version 搬家）存量迁移步骤"。
- [ ] **1.3** `skills/preflight/templates.md` cockpit 模板 + §Rules：**删 `**Layout**` 行**及其说明。
- [ ] **1.4** `skills/preflight/SKILL.md`：step 0 最小契约判定改为三件套；step 2 改读 rules.md `version` + MIGRATION.md 元数据，按 version spec §2.3 三分支判定；补"存量 deck 无 rules.md → 一次性提示补建（stamp version + 删 Layout 行）"。
- [ ] **1.5** `skills/walkaround/SKILL.md` Audit 10：从读 cockpit `Layout` 改为读 rules.md `version` + MIGRATION.md `current`/`layout_need_update`，按同一三分支判定。
- [ ] **1.6** `skills/landing/SKILL.md`（及共享 Land Routine）：归档前按需 bump `last_updated`（与 Phase 2 合流，先占位）。
- [ ] **1.7** `scaffolds/**`：full / minimal 补 `rules.md`（带 `version`）+ `landed/HISTORY.md`；删 cockpit `Layout` 行。
- [ ] **1.8** `flightdeck/checklists/version-bump.md`：加两条 —— 发布时 bump `MIGRATION.md` `current`；**破坏性布局变更**时追加 `layout_need_update`。顺手把该文件 `applies_to` 由主题词改为项目路径（house-rule nudge）。
- [ ] **1.9** `README.md` / `README.zh.md`：凡 `Layout` / 最小契约 / 迁移检测处改为新口径。

**Phase 1 验收**：新建 deck 写三件套 + `version`；preflight/walkaround 用 `version` 判迁移，旧 1.2 deck 触发"补建 rules.md"一次性迁移；cockpit 不再有 `Layout` 行。

## Phase 2 — workflow 富化（enrichment spec）

- [ ] **2.1** `skills/preflight/templates.md`：spec/sketch、plan frontmatter 加 `summary`（单行约束注释）+ `last_updated` + `supersedes`/`related`；per-folder INDEX 行格式说明改为"从 `summary` 派生"。权威表同步。
- [ ] **2.2** INDEX 生成逻辑（`landing` / `status` / `walkaround` 重生成 AUTO 区处）：读 frontmatter 时一并取 `summary` 生成行；`|` 转义兜底。
- [ ] **2.3** `skills/status/SKILL.md` + `skills/landing/SKILL.md`：`last_updated` 自动 bump 锚点（status 翻状态 / landing 归档实质修改时）；模型自调 status 时由 status 写 `last_updated`。
- [ ] **2.4** `skills/landing/SKILL.md`（Land Routine）：归档时扫描全仓 `supersedes`/`related`，把指向被归档文件的边改写为 `landed/` 前缀。
- [ ] **2.5** `skills/walkaround/SKILL.md`：可选 INFO 检查 —— 缺 `summary`/`last_updated`；`supersedes`/`related` 断边（目标在树及 landed 均不存在）。Audit 3 不扩 spec（`superseded_by` 仅 knowledge）。
- [ ] **2.6** 复核 Phase 2.2：`status`（v2.1 已落地）的 INDEX 单行写入**从一开始就读 `summary`**，确认无"先实现再回改"。

**Phase 2 验收**：spec/plan 带 `summary`/`last_updated`，INDEX 行由 `summary` 派生；landing 归档后关系边路径仍可导航；`last_updated` 由 skill 自动维护。

## Phase 3 — dogfood 回填 + 发布

- [ ] **3.1** 回填本 deck 存量 workflow 工件（三篇 pending spec、本 plan、`sketches/v1x-deferred-ideas.md`）：补 `summary` + `last_updated`；本 plan/spec 间补 `supersedes`/`related`（本 plan 三篇关系、consolidation↔version↔enrichment）。
- [ ] **3.2** 本 deck：`flightdeck/rules.md` 加 `version`；删 `flightdeck/cockpit.md` 的 `**Layout**: 1.2` 行；scaffolds 同步。
- [ ] **3.3** 跑 `/flightdeck:walkaround`，确认 clean（尤其新 audit 对齐、断边检查、version 检测）。
- [ ] **3.4** **发布**（按 `version-bump.md`）：本次含"rules.md 必选 + 删 Layout 行"= **布局影响变更** → 把本发布版本写进 `MIGRATION.md` `layout_need_update`（这是该机制的首个真实条目）；bump 5 个 manifest + CHANGELOG + `MIGRATION.md` `current`；写迁移指引。
- [ ] **3.5** AGENTS.md 重生成（`/flightdeck:emit-agents-md`）；cockpit Next session 收尾。

**Phase 3 验收**：本 deck 自身已是新模型（三件套 + version + 富化字段），walkaround clean，发布物一致，旧 deck 有明确迁移路径。

---

## 注意

- **顺序是硬依赖**：Phase 0 不先立权威表，Phase 1/2 会重新制造四处漂移。
- **自指迁移**（3.4）：本次改动本身就是 `layout_need_update` 机制要捕获的那类"布局影响变更" —— 旧 cockpit-only / 无 rules.md 的 deck 需补建。借此首条真实验证该机制。
- **验证场景**须覆盖 enrichment spec §2.3 注意块：active spec 被 active spec `supersedes` 时不自动翻旧 spec status。
