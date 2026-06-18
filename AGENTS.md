<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 alpha 打磨——`shared-knowledge-sync` 已 land（跨项目共享知识 vendoring：/flightdeck:sync + --sync-status + synced_from/shared_master），待端到端实证；`cockpit-bloat-control` 仍待复核/排期。

## In Progress

- [2026-06-16-cockpit-bloat-control.md](flightdeck/specs/2026-06-16-cockpit-bloat-control.md) — cockpit 膨胀治理：着陆归档时自动排空引用刚归档 artifact 的冗余散文（可逆，自动）；规范字段替换而非追加 + 逐字段密度检查（门控 trim）；walkaround 守卫野章节 + active 计数非阻塞提示。规范字段集本就精简，膨胀来自野章节与散文不排空。

## Next

- **复核 `shared-knowledge-sync`**（审 diff，或真 vendor 一份共享文件跑 `/flightdeck:sync` 做端到端实证）；之后回到 `cockpit-bloat-control` 复核/排期。

## Hanging Tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec / plan / incident / checklist / reference / doc), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or hand-derive their paths.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
