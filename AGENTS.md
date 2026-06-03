<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 分支 code-complete、未 push；preflight skill 整改 + token-reduction 已完成、QA 通过（全仓 anchor 校验 / 脚本测试 24 passed / INDEX --check 全绿）。**未做 runtime dogfood**（本会话加载的是旧 2.3 skill），待 reload 后验证、发布、合并。

## Next session

1. 行为 dogfood（reload/重装插件后）—— 减重完成，进入测试：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、迁移改写、when-to-land、walkaround；②init 重做——干净目录首次建档全程。
2. 发布 3.0（[checklists/version-bump.md](flightdeck/checklists/version-bump.md)）+ 合并分支 → main。
3. 仍开放：INDEX-row `—` 分隔符 ([incidents/index-row-summary-delimiter.md](flightdeck/incidents/index-row-summary-delimiter.md))；no-git HISTORY 格式；walkaround 压缩（归 scriptable lint）。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
