# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-19 · 月离 · Stage: v3.0.0-alpha.4 已切（5 manifest + CHANGELOG，未 push / 未 tag）；launch-recorded-config 全 spec 相 1/2/3 done + land，spec graduate → docs/

Focus: deck-format-conform（strict formatter 设计）→ specs/2026-06-19-deck-format-conform.md

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-19-deck-format-conform.md](specs/2026-06-19-deck-format-conform.md) — A strict deck formatter that conforms every active file to its canonical schema/…
- [2026-06-19-deck-format-conform.md](plans/2026-06-19-deck-format-conform.md) — Implement the deck format conformer: new flightdeck_conform.py/.js (py/js byte-p…
<!-- /AUTO -->

## Next

- （**parked**）跨项目本地验 alpha.4 → `checklists/local-plugin-testing.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- **launch-recorded-config 已发版 `3.0.0-alpha.4`（本会话）**：spec graduate → `docs/launch-recorded-config.md`（设计现状真相源），相 1/2/3 plan 归档 `archive/plans/`。版本号（5 manifest）+ CHANGELOG 已落，`MIGRATION.md current` 仍 `3.0`（format baseline）；**未 push / 未 tag**（用户定）。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
