<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 分支 code-complete、未 push；机械层脚本化(INDEX/init/release) + skill token-reduction 进行中（第一批已落：preflight SKILL 158→127 拆 setup.md、5 漂移修、去重）。**未做 runtime dogfood**（本会话加载的是旧 2.3 skill），待 reload 后验证、发布、合并。

## Next session

1. 行为 dogfood（reload/重装插件后）：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、迁移改写、when-to-land、walkaround；②init 重做——干净目录首次建档全程。
2. 发布 3.0（[checklists/version-bump.md](flightdeck/checklists/version-bump.md)）+ 合并分支 → main。
3. token-reduction 余下批次（[specs/2026-06-03-token-reduction-design.md](flightdeck/specs/2026-06-03-token-reduction-design.md)）：Tier 2 去重、templates、walkaround(待脚本 lint)、A1 拆 migration / A3 git heuristic。
4. preflight 纠错（[sketches/preflight-tri-review-triage.md](flightdeck/sketches/preflight-tri-review-triage.md)）：B1/B3 等（减重项已并入 token-reduction spec）。
5. 仍开放：INDEX-row `—` 分隔符 ([incidents/index-row-summary-delimiter.md](flightdeck/incidents/index-row-summary-delimiter.md))；no-git HISTORY 格式。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
