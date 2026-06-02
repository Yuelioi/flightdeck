---
status: pending
---

# 元数据模型归一：单一权威字段表 + 收编漂移字段 + 裁决不对称

**日期**：2026-06-02
**来源**：dogfood 调查 —— 准备给 frontmatter 加 5 个新字段前，发现同一套元数据模型被 `templates.md` / `folder-semantics.md` / `protocol.md` 各写一遍且已漂移（`skip_when` 实锤）。作者判断"元数据越来越重要"，应先归一再实现。
**状态**：pending（设计定稿，待开 plan 实现）
**关联**：本篇是 [version-in-rules](2026-06-02-version-in-rules-migration-detection-design.md) 与 [frontmatter-enrichment](2026-06-02-workflow-artifact-frontmatter-enrichment-design.md) 的**上游归一层** —— 两者的新字段并进本篇的权威表；三篇由**一个 plan** 同一 pass 实现。

---

## 1. 问题（调查结论）

1. **同一套 frontmatter 模型被 3 处各写一遍并已漂移**：`templates.md`（逐文件模板）/ `folder-semantics.md`（逐文件夹内联重述）/ `protocol.md`（数据模型 + hard-fail 规则），外加 `walkaround` 只校验子集。加 5 个新字段就要同步改 4 处。
2. **实锤漂移：`skip_when`**。已发布（CHANGELOG）、`protocol.md:94` + `folder-semantics.md:233` 有，**唯独 `templates.md` 没有**；且适用范围两处不一致（protocol 说 incidents+checklists+bundle-README，folder-semantics 只在 checklist 给）；walkaround 不认。
3. **`bundle` / `scope` / `non_goals` 已废弃**：bundles 设计（landed `2026-05-30-bundles-and-routing-graph-design.md`）未被采纳，`protocol.md:76` 明确 "No bundle README"。非活字段。
4. **两处故意的不对称未裁决**（见 §2.4 / §2.5）：取代关系（`supersedes` 边 vs `superseded_by` 状态）；`last_updated` 强制级别（knowledge 必填 vs workflow 推荐）。

## 2. 设计

### 2.1 单一真相源：权威字段表落在 `protocol.md`

- 在 `protocol.md` 的 "Data model" 下新增 **`## Frontmatter field reference（canonical）`** —— 全字段唯一定义处。
- `templates.md` 保留**可粘贴模板块**，但字段语义改为"见 protocol.md § frontmatter reference"，不再自带语义说明。
- `folder-semantics.md` **停止内联重述字段**，只讲"每个文件夹是干什么的"，字段一律指向权威表。
- `walkaround` 的校验项**对齐权威表**（每个 required 字段对应一条 audit；optional 字段最多 INFO）。

职责切分：protocol = 有哪些字段 + 语义；templates = 拿来即用；folder-semantics = 文件夹用途；walkaround = 按表校验。

### 2.2 权威字段表（落地目标）

| 字段 | 适用 kind | 必填? | 谁读 | 谁写 | walkaround |
| --- | --- | --- | --- | --- | --- |
| `status` | 全部 workflow + knowledge | **必填** | preflight/landing/status/walkaround | status/landing/用户 | Audit 1 |
| `summary` | workflow（sketches/specs/plans）| 推荐 | INDEX 生成 | status/landing/作者 | INFO（缺则提示） |
| `last_updated` | knowledge **必填**；workflow 推荐 | 判 staleness | status/landing **自动 bump** | knowledge: Audit 2；workflow: INFO |
| `implements` | plans | 可选 | 反查 plans/INDEX | 作者 | Audit 4（orphan INFO） |
| `supersedes` | workflow | 可选 | grep 派生反向 | 作者/status | 断边 INFO（可选） |
| `related` | workflow | 可选 | grep | 作者 | 断边 INFO（可选） |
| `when_to_read` | incidents/checklists/charts | **必填** | preflight 路由 | 作者 | Audit 2 |
| `applies_to` | incidents/checklists/charts | **必填** | preflight 路由 | 作者 | Audit 2 |
| `skip_when` | incidents/checklists | 可选 | 匹配期负路由 | 作者 | 不强制 |
| `superseded_by` | knowledge（当 status: superseded）| **条件必填** | 死文件→替代的正向重定向 | 作者 | Audit 3 |
| `reviewed` | debriefs | **必填** | 指向被审 spec | 作者 | debrief 检查 |
| `version` | `rules.md`（root）| **必填**（rules 升必选，见 version spec）| preflight/walkaround 迁移检测 | preflight setup/自动顶号 | Audit 10 |
| `git`/`emit_agents_md`/`disabled_folders`/`disabled_gates`/`model_invocable`/`status_auto` | `rules.md` | 可选（有默认）| 全部入场 skill | 用户 | — |

> `cockpit.md` 头部的 `Last updated`/`Active focus`/`Next session`/`Hanging tasks` 是看板字段（非 YAML frontmatter）；`Layout` 行由 version spec 删除。

### 2.3 `skip_when` 收编 + 废字段判死

- `skip_when` 进权威表（incidents/checklists，可选，负路由），同步补进 `templates.md`；统一适用范围（不含已死的 bundle-README）。
- `bundle` / `scope` / `non_goals` 判死：在 landed `2026-05-30-bundles-and-routing-graph-design.md` 头部标注**已废弃/未采纳**（类比 2.0 abandoned），避免后人误读为活设计。

### 2.4 裁决：取代关系的不对称 —— **保留分裂，并文档化理由**

| | knowledge | workflow |
| --- | --- | --- |
| 机制 | `status: superseded` + `superseded_by`（正向指针，必填） | `supersedes` 边（挂新工件，反向靠 grep） |
| 为何不同 | 知识文件**留在原地不归档** → 读者会撞上"死但在位"的文件，**必须有正向重定向**到替代 | 旧 workflow 工件是 `done` 并**归档进 landed**（历史），读者极少冷撞；"谁取代我"是低频反查 → grep 足够 |

结论：两套机制各自正确，不强行统一；权威表 + protocol 明确写出这条"知识留位、workflow 归档"的根因。

### 2.5 裁决：`last_updated` 强制级别不对称 —— **保留，文档化**

- knowledge **必填**：路由依赖 staleness 判断（陈旧 advice 危险）。
- workflow **推荐 + 自动 bump**：靠 INDEX/cockpit 发现而非 grep 路由，staleness 次要；自动 bump 防腐化。

### 2.6 `summary` 仅 workflow

knowledge 的 INDEX 行已展示 `when_to_read`/`applies_to`（其"摘要等价物"），且知识文件多不归档、无"摘要落地即丢"问题 → `summary` 只加 workflow。权威表写明此切分。

## 3. 与两篇 pending spec 的关系

- 本篇定**表的结构与归一原则**；version / enrichment 两篇定**各自新字段的语义与行为**。
- 实现合并为**一个 plan**，顺序：先按本篇建权威表骨架 + 收编 skip_when + 判死废字段 + 写两条裁决 → 再把 version（`version`）、enrichment（`summary`/`last_updated`/`supersedes`/`related`）的字段填进表 → 最后回填存量工件 + 对齐 walkaround。
- 三篇 spec 各自 `implements` 由 plan 侧的 `implements:` 承接（一个 plan 可在正文声明覆盖三篇；或主 plan implements 本篇、正文引用另两篇）。

## 4. blast radius

- `skills/preflight/protocol.md` —— 新增权威字段表；写入 §2.4/§2.5 两条裁决理由。
- `skills/preflight/templates.md` —— 模板块去语义、指向权威表；补 `skip_when`。
- `skills/preflight/folder-semantics.md` —— 删字段内联重述，指向权威表。
- `skills/walkaround/SKILL.md` —— 校验项逐条对齐权威表（required→audit、optional→最多 INFO）。
- `flightdeck/landed/specs/2026-05-30-bundles-and-routing-graph-design.md` —— 头部标注废弃。
- `scaffolds/**`、`README*` —— 凡重述字段处改为指向权威表。

## 5. 非目标

- 不改字段的运行语义（那是另两篇 spec 的事）；本篇只做"归一 + 收编 + 裁决 + 单一真相源"。
- 不强行统一 knowledge/workflow 的取代关系（§2.4 已裁决保留分裂）。
- 不复活 bundles / `scope` / `non_goals`。
