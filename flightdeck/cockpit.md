# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-23 · 月离 · Stage: stage/land plan 2 done+归档（收窄为 walkaround Audit 13 翻转 + templates ## Staged 文档；landing/status 经判断证实 signal 耦合→交 plan 3）

Focus: stage/land 生命周期重构 → `specs/2026-06-22-stage-land-lifecycle.md`（plan 1·2 done+归档；plan 3 = 三层/signal 模型一处一次改完 待起）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-22-stage-land-lifecycle.md](specs/2026-06-22-stage-land-lifecycle.md) — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: st…
<!-- /AUTO -->

## Staged (awaiting land)

<!-- AUTO:staged -->

<!-- /AUTO -->

## Next

- **起 plan 3** — 三层/signal 模型一处一次改完：`landing` Modes 表/banner/commit 归属 + `status` Step 7（signal-1 auto-land）+ `exit-ritual`（signal 1/2/3 重设计 + 三层→stage/land + drain 下放）+ `protocol`（readiness 重设计）+ `preflight`（入口 readiness=staged 量）。**handoff 清单** → `archive/plans/2026-06-23-stage-land-prose-independent.md` 末 + spec Open Q3/Q5。
- （**parked**）本地缓存已同步当前构建（`build_stamp` `current`），多日 dogfood 中；跨项目 `--fanout` live 实证待做（需第二个消费 deck）→ `checklists/local-plugin-testing.md`。

## Key Context

- (none)

## Pending Review

- ⚠待复核 `docs/script-layer.md`：脚本层文档未补 `--register/list/prune-consumers` + `sync_status` 这批 flag；doc 仍 `status: stale`，下次补齐。
- [marker 自带化 英文散文]（已 commit `1348619` + 同步本地缓存）本会话翻 vendorable-master「自带 marker+stub」约定 + `marker-missing` 安全网,改了**发布面英文散文**:`skills/sync/SKILL.md`（boundary-marker 节 + mode-A 状态表 + mode-C re-stamp + 报告 banner）、`skills/walkaround/SKILL.md`（Audit 15 WARN 文案）、`skills/preflight/protocol.md` + `templates.md`（旧「母库无 marker」断言翻转）。canonical stub 措辞 = `## Project overrides` + 斜体注（用户已选 B）。**复核英文措辞是否合意**;设计真相 → `docs/shared-knowledge-sync.md`。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
