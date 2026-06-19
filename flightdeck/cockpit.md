# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-20 · 月离 · Stage: conform ship + flightdeck_new date-parity 修复（错题已退役）；commits/comments.md 退役 portable（本仓+母库，deck conform-clean）；alpha.4 仍未 push / 未 tag

Focus: （无活跃 spec/plan）候选见 ## Next

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-20-sync-mechanical-pull.md](specs/2026-06-20-sync-mechanical-pull.md) — 把带时间戳的 AI-merge sync 降级为纯机械模型：母库是 shared 内容唯一写者、consumer 不改 shared，<!-- flightde…
<!-- /AUTO -->

## Next

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
