<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

（无活跃 spec/plan）deck-format-conform 已收尾（`flightdeck_conform.py/.js` + `/flightdeck:conform` ship）；候选见 Next（含新发现的 flightdeck_new date-parity bug）

## In Progress

None.

## Next

- 修 `flightdeck_new` 默认日期 parity：`.js` 用 UTC（`toISOString`）、`.py` 用 local（`date.today`），跨午夜窗 `test_parity_init_new` 红 → `incidents/new-default-date-local-vs-utc.md`。
- （**parked**）跨项目本地验 alpha.4 → `checklists/local-plugin-testing.md`。
- （**parked**）复核 `shared-knowledge-sync` v2（`feat/shared-knowledge-sync-v2`，未并 main）。

## Hanging Tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec / plan / incident / checklist / reference / doc), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or hand-derive their paths.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
