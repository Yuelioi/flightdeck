# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-23 · 月离 · Stage: marker 自带化 + `marker-missing` 安全网 landed（spec+plan 归档；脚本 py/js + 4 skill 散文 + 设计 doc 全翻；母库三文件 stamp、本仓副本 in-sync）

Focus: stage/land 生命周期重构 → `specs/2026-06-22-stage-land-lifecycle.md`（plan 1 执行中：`plans/2026-06-22-stage-land-staged-view-script.md`，Task 1 待跑）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-22-stage-land-lifecycle.md](specs/2026-06-22-stage-land-lifecycle.md) — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: st…
- [2026-06-22-stage-land-staged-view-script.md](plans/2026-06-22-stage-land-staged-view-script.md) — Script foundation for stage/land: named-marker multi-AUTO-region support + regen…
<!-- /AUTO -->

## Staged (awaiting land)

<!-- AUTO:staged -->

<!-- /AUTO -->

## Next

- 执行 **plan 1** → `plans/2026-06-22-stage-land-staged-view-script.md`：从 Task 1（AUTO 定位改命名 marker）起，4 个 TDD task。后续 plan 2（散文重写）/ plan 3（signal 体系 + walkaround 翻转）。
- （**parked**）本地缓存已同步当前构建（`build_stamp` `current`），多日 dogfood 中；跨项目 `--fanout` live 实证待做（需第二个消费 deck）→ `checklists/local-plugin-testing.md`。

## Key Context

- deck-format-conform 落地：设计真相源 `docs/deck-format-conform.md`；脚本 `scripts/flightdeck_conform.py/.js`（byte-parity，`ConformParity`）、skill `skills/conform/SKILL.md`、walkaround Audit 16 → 指向 `/flightdeck:conform`。`references/` 排除出 walk（IMPORTED_KIND）。

## Pending Review

- [shared-knowledge-sync **v2** 实现] 9 任务 land（169 测试绿、子代理两段评审 + opus 终审 ready；spec graduate→`docs/shared-knowledge-sync.md`、plan 归档）；母库已**物理移到** `~/.flightdeck`、本仓两 vendored 文件 `synced_from`→`synced` 迁移 + 补注册（`--list-consumers` 命中本仓、`in-sync`）。**跨项目 `--fanout` live 实证待做**（需第二个消费 deck）。审分支 diff `feat/shared-knowledge-sync-v2`；**不满意说「翻回」**。分支**未并入 main**（本仓只本地、不 push）。
- ⚠待复核 `docs/script-layer.md`：本会话 v2 又加 `--register/list/prune-consumers` + 改 `sync_status`（继上次 `--sync-status` 之后），脚本层文档仍未补；下次补齐这批 flag。
- [marker 自带化 英文散文]（已 commit `1348619` + 同步本地缓存）本会话翻 vendorable-master「自带 marker+stub」约定 + `marker-missing` 安全网,改了**发布面英文散文**:`skills/sync/SKILL.md`（boundary-marker 节 + mode-A 状态表 + mode-C re-stamp + 报告 banner）、`skills/walkaround/SKILL.md`（Audit 15 WARN 文案）、`skills/preflight/protocol.md` + `templates.md`（旧「母库无 marker」断言翻转）。canonical stub 措辞 = `## Project overrides` + 斜体注（用户已选 B）。**复核英文措辞是否合意**;设计真相 → `docs/shared-knowledge-sync.md`。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
