<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 分支全部 code-complete、未 push（rules 简化 / init 重做 / README+docs / 删 init 教程 / 删 cockpit hygiene footer / 机械层脚本 PoC：`scripts/flightdeck_index.py` INDEX-regen 已落地）。**未做 runtime dogfood**（本会话加载的是旧 2.3 skill），待 reload 后验证、发布、合并。

## Next session

1. 行为 dogfood（reload/重装插件后）：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、迁移改写、when-to-land、walkaround；②init 重做——干净目录首次建档全程。
2. 发布 3.0（[checklists/version-bump.md](flightdeck/checklists/version-bump.md)）+ 合并分支 → main。
3. 机械层脚本化 rollout（[sketches/scriptable-mechanical-layer.md](flightdeck/sketches/scriptable-mechanical-layer.md)）：INDEX-regen 接进 landing/walkaround/status 双轨 + rules `scripts:` 开关 + 版本 guard。
4. preflight 减重/纠错（[sketches/preflight-tri-review-triage.md](flightdeck/sketches/preflight-tri-review-triage.md)）：B1/B3 顺手，A1 拆 migration。
5. 仍开放：INDEX-row `—` 分隔符 ([incidents/index-row-summary-delimiter.md](flightdeck/incidents/index-row-summary-delimiter.md))；no-git HISTORY 格式。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
