# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-04 by 月离 (model-v4 6 phase + final review 通过；**scriptable 机械层 rollout 全完成**——交付 `flightdeck_lint.py`〔机械审计 Audit 1/4/5/7/8 → JSON〕、配线进 exit-ritual/walkaround、修 3 处 CHANGELOG dangling ref，deck lint 干净；65 tests 绿、index --check clean。剩发布前 reload 行为 dogfood + emit + 发布)
**Active focus**: flightdeck 3.0 收尾——model-v4 与 scriptable 机械层(lint) 均实施完成、本仓库 deck 已迁新模型且 lint 干净；剩发布前 reload 后行为 dogfood 验证（用户测试项：preflight/status/landing）+ AGENTS emit + 发布 → 合并 main。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-03-incident-recurrence-autocount-design.md](specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
- [2026-06-03-model-v4-folder-state-cockpit-design.md](specs/2026-06-03-model-v4-folder-state-cockpit-design.md) — flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
- [2026-06-04-preflight-slim-launch-split-design.md](specs/2026-06-04-preflight-slim-launch-split-design.md) — preflight 太重（兼管初始化/检查/接管）——拆出 `/flightdeck:launch` 接管首次创建 deck，preflight 瘦成纯接管（读 cockpit/INDEX → 报下一步 + 精简 catalog 预热 + 被动一行 git 提示），删掉与 walkaround 重复的检查（结构性迁移探测/catalog 状态体检/cockpit 漂移/阻塞式 reconcile）。并入 3.0
- [2026-06-03-model-v4-rollout.md](plans/2026-06-03-model-v4-rollout.md) — model-v4 分 6 phase 实施——数据模型真相源 → flightdeck_index 扩展(+测试) → 4 skill 行为 → scaffolds/emit/MIGRATION → dogfood 迁移本仓库 → 验证收尾；并入 3.0
- [2026-06-04-preflight-slim-launch-split.md](plans/2026-06-04-preflight-slim-launch-split.md) — 实现 preflight 瘦身 + 拆出 /flightdeck:launch——新建 launch skill（搬 setup.md）、重写 preflight（重定向 Branch-0 / 删重复检查 / 2 列 catalog / 被动 git 表 / 版本 bump 优先级）、删 setup.md、改两条 description、交叉引用 doc-sweep；验证靠现有 pytest + index --check + dogfood + walkaround。清单自动发现无需注册，CHANGELOG 留发布时写
<!-- /AUTO -->

## 下一步

- 发布前验证：reload（重载 plugin）后 dogfood 跑通 model-v4 行为（preflight 读新 cockpit / status idea→active 带动 `## 进行中` / landing 自动写两区）；重跑 `/flightdeck:emit-agents-md` 消除 AGENTS.md drift。
- 发布 3.0：version-bump + marketplace + tag + 合并分支 → main（见 [checklists/version-bump.md](checklists/version-bump.md)）。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
