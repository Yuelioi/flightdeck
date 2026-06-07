---
status: active
when_to_read: 想把一个 spec/plan 标记为被取代/收编、或给 workflow 工件设 active/done 以外的状态前
applies_to: [specs, plans, status, superseded, workflow, lifecycle, flightdeck_lint.py, supersedes, archive]
last_updated: 2026-06-07
resolved_by:
---

# workflow 工件无 superseded 状态——收编走 done+archive+supersedes 边

## Signature
- symptom: `flightdeck_lint.py: <name> has illegal status `superseded` (legal: ['active', 'done', 'idea'])`
- error_type: —
- where: scripts/flightdeck_lint.py —— Audit 1 status legality（`WORKFLOW_STATUSES = {idea, active, done}`）
- trigger: 给 specs/ 或 plans/ 工件的 frontmatter 写 `status: superseded`（想表达"被新工件取代/收编"）

## 症状/复现

hook-primary-refactor rollout 的 Phase 3「收编」步骤写：把 `specs/2026-06-06-auto-land-executor` + 两个旧 rollout plan 标 `status: superseded`。但 `superseded` 是 **knowledge**（incidents/checklists/docs/references）的状态值之一（`active/obsolete/superseded`）；**workflow（specs/plans）合法状态只有 `idea/active/done`**（`flightdeck_lint.py:42` `WORKFLOW_STATUSES`）。给 workflow 设 superseded → lint Audit 1 判 illegal status。

## 根因

数据模型对两类工件用**不同状态轴**：workflow 走生命周期 `idea→active→done→archive`，knowledge 走 `active→obsolete|superseded`（原地不归档，故需 `superseded_by` 前向边重定向）。"被取代"在两轴的表达**不对称**：knowledge 用 `status: superseded` + `superseded_by`（前向，因 reader 会冷撞到原地死文件）；workflow 用 **`done` + 归档 + 新工件的 `supersedes` 反向边**（旧的进 archive/、reader 很少冷撞，故反向边即可、"谁取代我"靠 grep）。见 protocol § Supersession（edge vs status pointer）。plan 把 knowledge 的 superseded 误套到 workflow。

## 修法

workflow 工件的"收编/被取代"= **翻 `done` + Land Routine 归档 + 由取代它的新工件 carry `supersedes:` 反向边**，不写 `status: superseded`。本例：三个旧工件的有效产出已 ship（auto-land 执行层 commit febdeea、soft-landing commit 14c5a92），翻 `done` 属实；新 `hook-primary-refactor` spec/rollout carry `supersedes` 指向它们；`--archivable` 会把无 active 入边（`implements`/`superseded_by`）的 done 集算出，cluster 归档。`supersedes` 是反向边、不进 archivable 阻塞集，不挡归档。

教训：凡给工件设非 active/done 的状态前，先认清它是 workflow 还是 knowledge——两轴状态值不通用。plan 写"标 superseded"这类跨模型动作时，落地前对 `flightdeck_lint.py` 的 `*_STATUSES` 核一遍。

## 更新（2026-06-07，graduate + 知识保鲜 spec）

本条原文（症状/根因）写于 knowledge 状态轴还是 `active/obsolete/superseded` 时。现已变更：**knowledge status 轴收成 `{active, stale, obsolete}`——`superseded` 状态值已在两轴全局退役**（`flightdeck_lint.py:43` `KNOWLEDGE_STATUSES = {active, stale, obsolete}`）。

因此"被取代"现在**两轴写法统一**：旧件翻终态（workflow `done` / knowledge `obsolete`）→ 仪式排进 `archive/`，新件 carry `supersedes:` 溯源边（纯溯源、**不进** `--archivable` 钉扣集；钉扣边只剩 `implements:`，`superseded_by` 字段亦退役）。原"knowledge 用原地 `superseded` + 前向 `superseded_by`、workflow 用 done+archive+反向 supersedes"的**不对称已消除**。

本条核心教训仍成立（workflow vs knowledge 两轴状态值不通用），但现在**两轴都没有 `superseded` 状态值**——给任一类工件写 `status: superseded` 都非法。

## Cases
- 2026-06-07 首次——hook-primary rollout Phase 3 落地前发现，未真写非法状态（核模型时拦下）。修法=改用 done+archive+supersedes；待用户确认收编映射后执行。
- 2026-06-07 更新——graduate+知识保鲜 spec 把 knowledge 状态轴改成 `{active, stale, obsolete}`，`superseded` 状态值两轴全局退役、`superseded_by` 退役；"被取代"两轴写法统一为终态+archive+`supersedes` 溯源边。见上 § 更新。
