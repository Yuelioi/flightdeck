# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-20 · 月离 · Stage: deck-format-conform done + graduate（`flightdeck_conform.py/.js` + `/flightdeck:conform` ship）；alpha.4 仍未 push / 未 tag

Focus: （无活跃 spec/plan）conform 已收尾；候选见 ## Next（含新发现的 flightdeck_new date-parity bug）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->

<!-- /AUTO -->

## Next

- 修 `flightdeck_new` 默认日期 parity：`.js` 用 UTC（`toISOString`）、`.py` 用 local（`date.today`），跨午夜窗 `test_parity_init_new` 红 → `incidents/new-default-date-local-vs-utc.md`（候选改 `.js` 用 local 组件）。
- （**parked**）跨项目本地验 alpha.4 → `checklists/local-plugin-testing.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Key Context

- alpha.4 已切但**未 push / 未 tag**（用户定）；conform 等新工作并入当前 alpha（未发布前不另起版本）。
- deck-format-conform 落地：设计真相源 `docs/deck-format-conform.md`；脚本 `scripts/flightdeck_conform.py/.js`（byte-parity，`ConformParity`）、skill `skills/conform/SKILL.md`、walkaround Audit 16 → 指向 `/flightdeck:conform`。`references/` 排除出 walk（IMPORTED_KIND）。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
