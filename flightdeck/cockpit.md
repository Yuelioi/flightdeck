# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-19 · 月离 · Stage: cockpit 重设计 3/3 完成 + skills 纯英文，发版门转绿

Focus: 今日三 spec 全完成（field-redesign / accumulator / i18n）→ 待整批 landing + 发版 v3.0.0-alpha.2

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-19-cockpit-accumulator-convergence.md](specs/2026-06-19-cockpit-accumulator-convergence.md) — cockpit 两个非-AUTO accumulator（Key Context / Pending Review）堆积陈年内容，现有 drain 纪律+密度门…
- [2026-06-19-cockpit-field-redesign.md](specs/2026-06-19-cockpit-field-redesign.md) — 三个真实 3.0 cockpit 实测：叙述字段（Last updated 括号 / Active focus / Next）漏入工作记录（changelog…
- [2026-06-19-skills-english-remediation.md](specs/2026-06-19-skills-english-remediation.md) — 实测 skills/ 有 184 处中文漂移（10 文件），违反 rules.md 发布面英文红线。已止血：CLAUDE.md 强化对比 + version-b…
- [2026-06-19-cockpit-accumulator-convergence-rollout.md](plans/2026-06-19-cockpit-accumulator-convergence-rollout.md) — 实现 accumulator-convergence：Key Context 重述为中转暂存（B1 referent 死即排空 / B2 耐用毕业上迁到 hom…
- [2026-06-19-cockpit-field-redesign-rollout.md](plans/2026-06-19-cockpit-field-redesign-rollout.md) — 实现 cockpit-field-redesign：新字段结构（Updated 纯戳 / Focus 一行 / Pointers 行 / Next 单步+进度移…
- [2026-06-19-skills-english-remediation-rollout.md](plans/2026-06-19-skills-english-remediation-rollout.md) — 翻译 10 个 skill 文件到纯英文：先拆结构坑（中文 heading→英文+全锚点同步改；## 评审纪要→## Review notes 改定义+全引用）…
<!-- /AUTO -->

## Next

- **整批 landing**：今日三 spec + 三 plan（均 graduate）flip done → 毕业进 docs/ → 归档；分支 `feat/cockpit-redesign` 并入 main（需用户批准）。
- **发版 `v3.0.0-alpha.2`**（英文发版门已绿）：README 过目 → `checklists/version-bump.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- (none) — 本会话 drain/graduate 完毕（家均已存在，零信息丢失）：de-scope 红线 + 测试/度量 → `rules.md`；de-scope 基线 → `docs/descope-baseline.md`；AI 化精简两支柱 → `protocol § Act-report-close loop` / `§ Rule resolution order`；shared-knowledge-sync → `docs/shared-knowledge-sync.md`。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
