# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-19 · 月离 · Stage: cockpit 重设计执行中（field-redesign rollout）

Focus: cockpit 重设计三 spec 执行 → specs/2026-06-19-cockpit-field-redesign.md

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-19-cockpit-accumulator-convergence.md](specs/2026-06-19-cockpit-accumulator-convergence.md) — cockpit 两个非-AUTO accumulator（Key Context / Pending Review）堆积陈年内容，现有 drain 纪律+密度门…
- [2026-06-19-cockpit-field-redesign.md](specs/2026-06-19-cockpit-field-redesign.md) — 三个真实 3.0 cockpit 实测：叙述字段（Last updated 括号 / Active focus / Next）漏入工作记录（changelog…
- [2026-06-19-skills-english-remediation.md](specs/2026-06-19-skills-english-remediation.md) — 实测 skills/ 有 184 处中文漂移（10 文件），违反 rules.md 发布面英文红线。已止血：CLAUDE.md 强化对比 + version-b…
- [2026-06-19-cockpit-accumulator-convergence-rollout.md](plans/2026-06-19-cockpit-accumulator-convergence-rollout.md) — 实现 accumulator-convergence：Key Context 重述为中转暂存（B1 referent 死即排空 / B2 耐用毕业上迁到 hom…
- [2026-06-19-cockpit-field-redesign-rollout.md](plans/2026-06-19-cockpit-field-redesign-rollout.md) — 实现 cockpit-field-redesign：新字段结构（Updated 纯戳 / Focus 一行 / Pointers 行 / Next 单步+进度移…
<!-- /AUTO -->

## Next

- **接着执行 cockpit 重设计**：field-redesign rollout 收尾 → accumulator spec 写 plan + 执行 → i18n spec 翻译整顿 → `plans/2026-06-19-cockpit-field-redesign-rollout.md`
- （**parked**）发版 `v3.0.0-alpha.2`（README 待过目 → `checklists/version-bump.md`，注意英文发版门已挡，待 i18n 整顿后才转绿）；复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- (none) — 本会话 drain/graduate 完毕（家均已存在，零信息丢失）：de-scope 红线 + 测试/度量 → `rules.md`；de-scope 基线 → `docs/descope-baseline.md`；AI 化精简两支柱 → `protocol § Act-report-close loop` / `§ Rule resolution order`；shared-knowledge-sync → `docs/shared-knowledge-sync.md`。

## Pending Review

- [AI 化精简两 spec 实现] Spec 1 `act-report-close-loop` + Spec 2 `ai-authored-config` 均已 land（多个 per-task commit、160 测试绿、spec/plan 归档）。复核：审 diff 或跑 app（看 banner / `### Rules`）；**不满意就说「翻回」**撤最近着陆单元。已 commit，验证通过无需额外动作。
- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。
- [cockpit-bloat-control v2 实现] spec 重订（A 并入 accumulator-drain、C.1 因 Pending Review 转正作废，剔除）→ 只实现 B（landing 出场逐字段密度门控 trim）+ C.2（active>5 非阻塞提示），落 `exit-ritual.md`/`landing`/`preflight` SKILL；spec 已归档、169 测试绿。复核：审三处措辞 diff；**不满意说「翻回」**。
- ⚠待复核 `docs/descope-baseline.md`（触 stale）：改了 preflight/landing SKILL 散文（加密度检查 + active 计数），该 doc 对 preflight/landing 职责的枚举可能要补这两项——我读后判断仍成立（line 39 已钉「软上限=警戒线非截断」），人确认即可消 stale。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
