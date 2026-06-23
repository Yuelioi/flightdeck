# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-23 · 月离 · Stage: plan 3 执行完（stage/land 模型 6 面一次改完，6 commits）— done+verify，staged 待 land

Focus: stage/land 生命周期重构 → `specs/2026-06-22-stage-land-lifecycle.md`（plan 1·2·3 done；plan 3 staged 待 land → 一 land 即 graduate spec → docs/）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-22-stage-land-lifecycle.md](specs/2026-06-22-stage-land-lifecycle.md) — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: st…
<!-- /AUTO -->

## Staged (awaiting land)

<!-- AUTO:staged -->
### Done (awaiting land)
- [2026-06-23-stage-land-model-one-pass.md](plans/2026-06-23-stage-land-model-one-pass.md) — Rewrite the three-tier (checkpoint/soft-landing/full-landing) + signal 1/2/3 mod…
<!-- /AUTO -->

## Next

- **review + land plan 3** — 通读 6 文件英文散文（`exit-ritual`/`protocol`/`landing`/`status`/`preflight`(SKILL+templates+folder-semantics)/`bootstrap`）确认 tone+自洽；满意后 `/flightdeck:landing` → 归档 plan 3 + graduate spec `2026-06-22-stage-land-lifecycle` → `docs/`。验证 = plan `verify:` 行；grep 旧术语已清零（仅留 2 处「not three tiers / no checkpoint ritual」negative mention）。**Downstream**（未做，plan 末「Downstream」节）：`docs/session-flow.md` 等 deck 内文档 + README/CHANGELOG 的 soft-landing 提及，land 时会被 stale-flag。
- （**parked**）本地缓存已同步当前构建（`build_stamp` `current`），多日 dogfood 中；跨项目 `--fanout` live 实证待做（需第二个消费 deck）→ `checklists/local-plugin-testing.md`。

## Key Context

- (none)

## Pending Review

- ⚠待复核 **plan 3 stage/land 重写**（6 commits `89baf18`→`e85bd26`）：三层/signal 模型 → stage/land 两段，改了 6 个发布面英文散文（`exit-ritual` 模型源 + `protocol`/`landing`/`status`/`preflight`/`bootstrap` 引用）。**复核英文措辞 + 跨文件自洽**；满意即 land（graduate spec）。详 `plans/2026-06-23-stage-land-model-one-pass.md`。
- ⚠待复核 `docs/script-layer.md`：脚本层文档未补 `--register/list/prune-consumers` + `sync_status` 这批 flag；doc 仍 `status: stale`，下次补齐。
- [marker 自带化 英文散文]（已 commit `1348619` + 同步本地缓存）本会话翻 vendorable-master「自带 marker+stub」约定 + `marker-missing` 安全网,改了**发布面英文散文**:`skills/sync/SKILL.md`（boundary-marker 节 + mode-A 状态表 + mode-C re-stamp + 报告 banner）、`skills/walkaround/SKILL.md`（Audit 15 WARN 文案）、`skills/preflight/protocol.md` + `templates.md`（旧「母库无 marker」断言翻转）。canonical stub 措辞 = `## Project overrides` + 斜体注（用户已选 B）。**复核英文措辞是否合意**;设计真相 → `docs/shared-knowledge-sync.md`。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
