<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0——持续把模型/功能**完善到位**（**不急发布、避免迁移债**）。最新落成 incident 错误库生命周期；active 只剩 `incident-recurrence`（待 dogfood 行为验证）+ 若干 idea。

## 进行中

- [2026-06-03-incident-recurrence-autocount-design.md](flightdeck/specs/2026-06-03-incident-recurrence-autocount-design.md) — incident 复发计数升级——recurrences 提为 frontmatter 字段(从 body 头)、上 INDEX 行 recur:N、landing 自动维护；次数派生"待晋升/已晋级"，不加 status 值、不自动晋级、不 gate INDEX（避开 2.0 状态机红线）。已实现+27 tests 绿，待 dogfood 行为验证

## 下一步

- 下会话 **reload 后 live 复验**本会话新功能：`/flightdeck:new` 建 incident 带 `## Signature`、`--match-signature` 建前查重、obsolete 退役出路由、landing gated 回归复活。
- `incident-recurrence`（唯一 active）补 dogfood 行为验证。
- 待办 idea 按需推进：status-spec-co-advance / structural-edit-guard / scrapped-artifact-disposition。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec/plan/incident/checklist/chart), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or place them under `docs/`.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
