<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 收尾——model-v4 与 scriptable 机械层(lint) 均实施完成、本仓库 deck 已迁新模型且 lint 干净；剩发布前 reload 后行为 dogfood 验证（用户测试项：preflight/status/landing）+ AGENTS emit + 发布 → 合并 main。

## 进行中

- [2026-06-03-incident-recurrence-autocount-design.md](flightdeck/specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证
- [2026-06-03-model-v4-folder-state-cockpit-design.md](flightdeck/specs/2026-06-03-model-v4-folder-state-cockpit-design.md) — flightdeck 模型 v4——folder 7→5（sketches 并入 specs、删 debriefs）、workflow 状态 6→4（idea/active/done/scrapped）、cockpit 由 AI 全自动驱动（进行中区 AUTO 派生 + 下一步自动维护），并入 3.0
- [2026-06-03-model-v4-rollout.md](flightdeck/plans/2026-06-03-model-v4-rollout.md) — model-v4 分 6 phase 实施——数据模型真相源 → flightdeck_index 扩展(+测试) → 4 skill 行为 → scaffolds/emit/MIGRATION → dogfood 迁移本仓库 → 验证收尾；并入 3.0

## 下一步

- 发布前验证：reload（重载 plugin）后 dogfood 跑通 model-v4 行为（preflight 读新 cockpit / status idea→active 带动 `## 进行中` / landing 自动写两区）；重跑 `/flightdeck:emit-agents-md` 消除 AGENTS.md drift。
- 发布 3.0：version-bump + marketplace + tag + 合并分支 → main（见 [checklists/version-bump.md](flightdeck/checklists/version-bump.md)）。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
