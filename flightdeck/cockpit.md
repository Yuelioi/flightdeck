# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-23 · 月离 · Stage: 「AI-native 重设」已定档（两轮锤定 + 外审回应 + 历史底稿收敛成单一可信源）— spec = 决策记录，剩 authoring/迁移执行；plan 3 仍 staged 待 land

Focus: AI-native 重设 brainstorm（少结构·多信任 AI）→ `specs/2026-06-23-ai-native-redesign.md`；stage/land plan 3 暂 parked（staged 待 land）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-22-stage-land-lifecycle.md](specs/2026-06-22-stage-land-lifecycle.md) — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: st…
- [2026-06-23-ai-native-redesign.md](specs/2026-06-23-ai-native-redesign.md) — 少结构·多信任 AI 重设:砍流程/迁移/冗余三痛,resume+persist 两动词,behave/know/now 三层软知识,引用订阅替 vendori…
<!-- /AUTO -->

## Staged (awaiting land)

<!-- AUTO:staged -->
### Done (awaiting land)
- [2026-06-23-stage-land-model-one-pass.md](plans/2026-06-23-stage-land-model-one-pass.md) — Rewrite the three-tier (checkpoint/soft-landing/full-landing) + signal 1/2/3 mod…
<!-- /AUTO -->

## Next

- **AI-native 重设 — 已定档** — 两轮锤定关掉所有设计开口 + 外审回应 + 头号风险入取舍 + §0–8 收敛成单一可信源。spec = 决策记录。**剩纯执行(非设计)**:① 深层 `behave/flightdeck.md` authoring + 微核心定稿(英文发布面);② 迁移脚本(形态已定,等新形态实体后写+跑);③ 产品化细节(缓)。下次起 `work/` 写协议正文即可。 → `specs/2026-06-23-ai-native-redesign.md`。
- （**parked**，focus 已切走）**review + land plan 3** — 通读 6 文件英文散文（`exit-ritual`/`protocol`/`landing`/`status`/`preflight`(SKILL+templates+folder-semantics)/`bootstrap`）确认 tone+自洽；满意后 `/flightdeck:landing` → 归档 plan 3 + graduate spec `2026-06-22-stage-land-lifecycle` → `docs/`。验证 = plan `verify:` 行；grep 旧术语已清零（仅留 2 处「not three tiers / no checkpoint ritual」negative mention）。**Downstream**（未做，plan 末「Downstream」节）：`docs/session-flow.md` 等 deck 内文档 + README/CHANGELOG 的 soft-landing 提及，land 时会被 stale-flag。
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
