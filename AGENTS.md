<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 分支 code-complete、未 push；preflight 整改 + 减重 + auto-count 已完成、QA 通过（anchor / 27 tests / INDEX 全绿）。**发布前剩 dogfood + scriptable lint + 几个开放项**（见下）。**未做 runtime dogfood**（本会话加载旧 2.3 skill），待 reload。

## Next session — 3.0 发布前清单

1. 重同步缓存 → 行为 dogfood（reload）← 发布前总闸：①3.0 软配置面（git/emit 推断、`### Autonomy overrides`、2.3→3.0 迁移、when-to-land、walkaround 不报假阳性）②init 重做（干净目录首次建档）③incident 复发 auto-count [spec](flightdeck/specs/2026-06-03-incident-recurrence-autocount-design.md)（landing 自动 [Case N]+recur:N、晋级 gate）。
2. scriptable 机械层 [plan](flightdeck/plans/2026-06-03-scriptable-mechanical-layer-rollout.md) / [spec](flightdeck/specs/2026-06-03-scriptable-mechanical-layer-design.md)：Phase 2 接 landing/walkaround/status；Phase 3 lint 子命令——status 合法性 / dangling-ref / stray / 结构块断言（=[structural-edit-guard](flightdeck/specs/2026-06-03-structural-edit-guard-design.md)）/ recur 校验 / untracked-spec（active|pending spec 未进 Next session 兜底）。walkaround 压缩待此。
3. 决策：recur≥3 已晋级在 INDEX 可见？（待晋级 vs 已晋级分不出，晋级记 body）定方案，归 [autocount spec](flightdeck/specs/2026-06-03-incident-recurrence-autocount-design.md)。
4. 小开放项：INDEX-row `—` 分隔符冲突 [incident](flightdeck/incidents/index-row-summary-delimiter.md)；no-git HISTORY 格式。
5. 发布 3.0（最后）[checklists/version-bump.md](flightdeck/checklists/version-bump.md)：version-bump + marketplace + tag + 合并分支 → main。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
