# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-04 by 月离 (model-v4 Phase 4：迁移本仓库 deck 到新模型——sketch v1x→specs(idea)、3 个 pending spec→idea、删空 sketches/debriefs、cockpit 改 status-projection 结构（`## 进行中` AUTO 派生）)
**Active focus**: flightdeck 3.0 model-v4 实施中——folder 7→5 / 状态 6→4 / cockpit 为 active 集的派生视图；本仓库 deck 已迁到新模型，剩 Phase 5 验证收尾 + 发布。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-03-incident-recurrence-autocount-design.md](specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
- [2026-06-03-model-v4-folder-state-cockpit-design.md](specs/2026-06-03-model-v4-folder-state-cockpit-design.md) — flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
- [2026-06-03-scriptable-mechanical-layer-design.md](specs/2026-06-03-scriptable-mechanical-layer-design.md) — 机械层（INDEX 重生 / walkaround lint / AGENTS emit / 对账）脚本化降 token、模型只留判断；单语言 Python stdlib + markdown fallback 双轨 + rules scripts 开关 + 机械-判断分界 + 字母序；INDEX-regen PoC 已交付，余见 rollout plan
- [2026-06-03-model-v4-rollout.md](plans/2026-06-03-model-v4-rollout.md) — model-v4 分 6 phase 实施——数据模型真相源 → flightdeck_index 扩展(+测试) → 4 skill 行为 → scaffolds/emit/MIGRATION → dogfood 迁移本仓库 → 验证收尾；并入 3.0
- [2026-06-03-scriptable-mechanical-layer-rollout.md](plans/2026-06-03-scriptable-mechanical-layer-rollout.md) — 机械层脚本化 rollout —— INDEX-regen 接进 landing/walkaround/status 双轨 + rules scripts 开关 + 版本 guard + walkaround lint 子命令；分 3 phase，INDEX-regen PoC 已交付
<!-- /AUTO -->

## 下一步

- 发布前验证：reload（重载 plugin）后 dogfood 跑通 model-v4 行为（preflight 读新 cockpit / status idea→active 带动 `## 进行中` / landing 自动写两区）；重跑 `/flightdeck:emit-agents-md` 消除 AGENTS.md drift。
- 发布 3.0：version-bump + marketplace + tag + 合并分支 → main（见 [checklists/version-bump.md](checklists/version-bump.md)）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
