# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-19 · 月离 · Stage: 三 spec 已 landed（毕业 docs/cockpit-design + 归档）；待并 main + 发版 alpha.3

Focus: 发版 `v3.0.0-alpha.3`（当前已发 alpha.2；门已绿）→ checklists/version-bump.md

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## Next

- **并 main**：`feat/cockpit-redesign`（今日全部工作）合并入 main（合并本地可做；push 需用户显式批准）。
- **发版 `v3.0.0-alpha.3`**（门已绿）：走 `checklists/version-bump.md`——5 manifest bump `3.0.0-alpha.2`→`3.0.0-alpha.3`、CHANGELOG `[Unreleased]`→`[3.0.0-alpha.3]`（cockpit 重设计 + skills i18n）、annotated tag、push（需批准）。
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
