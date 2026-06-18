<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 alpha 打磨——发版 `v3.0.0-alpha.2` 准备中（README shared-knowledge 节已加待过目 → 接 version-bump）；`shared-knowledge-sync` v2 待跨项目 `--fanout` live 实证。

## In Progress

None.

## Next

- **发版 `v3.0.0-alpha.2`**（用户拍板）：① `README.md` + `README.zh.md` 已加「shared-knowledge / 母库」节（`~/.flightdeck` + `synced` vendoring + `consumers`/`--fanout`，待用户过目，**未 commit**）。② 用户确认 README → 走 `checklists/version-bump.md` bump 到 `3.0.0-alpha.2`（含 README badge 第 7 行、各 manifest、CHANGELOG）。
- **复核 `shared-knowledge-sync` v2**（审分支 diff `feat/shared-knowledge-sync-v2`，未并 main；真 vendor 第二个项目跑 `/flightdeck:sync --fanout` 做跨项目 live 实证）。

## Hanging Tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec / plan / incident / checklist / reference / doc), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or hand-derive their paths.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
